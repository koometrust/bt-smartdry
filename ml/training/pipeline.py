"""
Master ML Training Pipeline for BT-SmartDry.
Orchestrates:
1. Snapshot data loading and train/test splitting (80/20 by batch).
2. XGBoost regressor 5-fold CV and final model training (target R² >= 0.85).
3. Classifier candidate CV selection (Gradient Boosting vs Random Forest), training (target Acc >= 80%).
4. Fairness and subgroup auditing across crops and hubs.
5. Model artifact export (< 5 MB per model) and metadata generation in backend/models/.
"""

import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
import joblib
import pandas as pd

from ml.training.dataset import (
    load_dataset,
    split_by_batch,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)
from ml.training.train_regressor import (
    evaluate_regressor_cv,
    train_regressor,
)
from ml.training.train_classifier import (
    evaluate_classifier_candidates,
    train_classifier,
)
from ml.training.fairness import evaluate_fairness


def run_pipeline(
    dataset_path: str = "ml/data/training_snapshots.csv.gz",
    output_dir: str = "backend/models",
    random_seed: int = 42,
    sample_fraction: float = 1.0,
) -> dict:
    start_time = time.time()
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("BT-SmartDry: Starting Offline ML Training Pipeline")
    print("=" * 60)

    # 1. Load data
    print(f"Loading dataset from: {dataset_path} ...")
    df = load_dataset(dataset_path)
    if sample_fraction < 1.0:
        unique_batches = df["batch_id"].unique()
        sampled_batches = set(pd.Series(unique_batches).sample(frac=sample_fraction, random_state=random_seed))
        df = df[df["batch_id"].isin(sampled_batches)].copy().reset_index(drop=True)
        print(f"Subsampled to {len(sampled_batches)} batches ({len(df)} snapshots).")
    else:
        print(f"Loaded {df['batch_id'].nunique()} batches ({len(df)} snapshots).")

    # 2. Split train/test (80/20 by batch)
    df_train, df_test = split_by_batch(df, test_size=0.2, random_state=random_seed)
    print(f"Train set: {df_train['batch_id'].nunique()} batches, {len(df_train)} snapshots.")
    print(f"Test set:  {df_test['batch_id'].nunique()} batches, {len(df_test)} snapshots.")

    # 3. Train Regressor (XGBoost)
    print("\n[Step 1/4] Evaluating & Training Remaining Time Regressor...")
    cv_reg_metrics = evaluate_regressor_cv(df_train, n_splits=5, random_state=random_seed)
    print(f"  5-Fold CV R²:   {cv_reg_metrics['cv_r2_mean']:.4f} +/- {cv_reg_metrics['cv_r2_std']:.4f}")
    print(f"  5-Fold CV MAE:  {cv_reg_metrics['cv_mae_mean']:.4f} hours")

    reg_pipeline, test_reg_metrics = train_regressor(df_train, df_test, random_state=random_seed)
    print(f"  Held-Out Test R²:  {test_reg_metrics['test_r2']:.4f} (Target: >= 0.85 -> {'PASS' if test_reg_metrics['benchmark_passed'] else 'FAIL'})")
    print(f"  Held-Out Test MAE: {test_reg_metrics['test_mae_hours']:.4f} hours")

    # 4. Train Classifier (Model Selection + Training)
    print("\n[Step 2/4] Evaluating Classifier Candidates (Gradient Boosting vs Random Forest)...")
    winner_name, candidate_metrics = evaluate_classifier_candidates(df_train, n_splits=5, random_state=random_seed)
    for model_name, metrics in candidate_metrics["candidate_results"].items():
        print(f"  {model_name}: CV Accuracy = {metrics['cv_accuracy_mean']:.4f} +/- {metrics['cv_accuracy_std']:.4f}, Macro-F1 = {metrics['cv_macro_f1_mean']:.4f}")
    print(f"  Selected winning architecture: {winner_name}")

    cls_pipeline, test_cls_metrics = train_classifier(df_train, df_test, model_type=winner_name, random_state=random_seed)
    print(f"  Held-Out Test Accuracy: {test_cls_metrics['test_accuracy'] * 100:.2f}% (Target: >= 80% -> {'PASS' if test_cls_metrics['benchmark_passed'] else 'FAIL'})")
    print(f"  Held-Out Test Macro-F1: {test_cls_metrics['test_macro_f1']:.4f}")

    # 5. Fairness & Subgroup Evaluation
    print("\n[Step 3/4] Performing Subgroup Fairness Audit across Crops and Hubs...")
    fairness_report = evaluate_fairness(reg_pipeline, cls_pipeline, df_test)
    print("  Subgroup Performance by Crop:")
    for crop, stats in fairness_report["crop_subgroups"].items():
        print(f"    - {crop.capitalize():10}: Reg R²={stats['regressor_r2']:.4f}, MAE={stats['regressor_mae_hours']:.3f}h | Cls Acc={stats['classifier_accuracy']*100:.1f}%, F1={stats['classifier_macro_f1']:.3f}")

    print("  Subgroup Performance by Hub:")
    for hub, stats in fairness_report["hub_subgroups"].items():
        print(f"    - {hub.capitalize():14}: Reg R²={stats['regressor_r2']:.4f}, MAE={stats['regressor_mae_hours']:.3f}h | Cls Acc={stats['classifier_accuracy']*100:.1f}%, F1={stats['classifier_macro_f1']:.3f}")

    if fairness_report["flagged_disparities"]:
        print("  WARNING: Flagged subgroup disparities:")
        for flag in fairness_report["flagged_disparities"]:
            print(f"    ! {flag}")
    else:
        print("  Fairness audit PASSED: No systematic subgroup disparities detected.")

    # 6. Export Model Artifacts
    print("\n[Step 4/4] Serializing Model Artifacts to backend/models/ ...")
    reg_file = out_path / "remaining_time_regressor.joblib"
    cls_file = out_path / "quality_grade_classifier.joblib"
    metadata_file = out_path / "model_metadata.json"

    joblib.dump(reg_pipeline, reg_file, compress=3)
    reg_size_mb = reg_file.stat().st_size / (1024 * 1024)
    print(f"  Saved Regressor to:  {reg_file} ({reg_size_mb:.2f} MB - {'PASS < 5MB' if reg_size_mb < 5.0 else 'FAIL'})")

    joblib.dump(cls_pipeline, cls_file, compress=3)
    cls_size_mb = cls_file.stat().st_size / (1024 * 1024)
    print(f"  Saved Classifier to: {cls_file} ({cls_size_mb:.2f} MB - {'PASS < 5MB' if cls_size_mb < 5.0 else 'FAIL'})")

    metadata = {
        "pipeline_version": "1.0.0",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "random_seed": random_seed,
        "features": {
            "all_features": FEATURE_COLUMNS,
            "numeric_features": NUMERIC_FEATURES,
            "categorical_features": CATEGORICAL_FEATURES,
        },
        "regressor": {
            "model_family": "xgboost.XGBRegressor",
            "cv_metrics": cv_reg_metrics,
            "test_metrics": test_reg_metrics,
            "artifact_file": "remaining_time_regressor.joblib",
            "artifact_size_mb": round(reg_size_mb, 3),
        },
        "classifier": {
            "model_family": winner_name,
            "candidate_cv_selection": candidate_metrics,
            "test_metrics": test_cls_metrics,
            "artifact_file": "quality_grade_classifier.joblib",
            "artifact_size_mb": round(cls_size_mb, 3),
        },
        "fairness_audit": fairness_report,
        "benchmarks": {
            "r2_target": 0.85,
            "r2_achieved": test_reg_metrics["test_r2"],
            "r2_passed": test_reg_metrics["benchmark_passed"],
            "accuracy_target": 0.80,
            "accuracy_achieved": test_cls_metrics["test_accuracy"],
            "accuracy_passed": test_cls_metrics["benchmark_passed"],
            "artifact_size_under_5mb": bool(reg_size_mb < 5.0 and cls_size_mb < 5.0),
        },
    }

    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved Metadata to:   {metadata_file}")

    elapsed = time.time() - start_time
    print("=" * 60)
    print(f"Pipeline completed successfully in {elapsed:.2f} seconds.")
    print("=" * 60)

    return metadata


def main():
    parser = argparse.ArgumentParser(description="Run BT-SmartDry offline ML training pipeline")
    parser.add_argument("--dataset", type=str, default="ml/data/training_snapshots.csv.gz", help="Path to snapshot dataset")
    parser.add_argument("--outdir", type=str, default="backend/models", help="Output directory for model artifacts")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--subsample", type=float, default=1.0, help="Fraction of batches to subsample (default 1.0 = all)")
    args = parser.parse_args()

    run_pipeline(
        dataset_path=args.dataset,
        output_dir=args.outdir,
        random_seed=args.seed,
        sample_fraction=args.subsample,
    )


if __name__ == "__main__":
    main()

