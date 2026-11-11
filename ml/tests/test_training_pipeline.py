import pytest
from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np

from ml.training.dataset import split_by_batch, build_preprocessor, FEATURE_COLUMNS
from ml.training.train_regressor import create_regressor_pipeline, train_regressor
from ml.training.train_classifier import create_classifier_pipeline, train_classifier


def test_leak_free_split():
    # Synthetic mock snapshots
    data = []
    for b_id in [f"batch_{i}" for i in range(20)]:
        for step in range(10):
            data.append({
                "batch_id": b_id,
                "temperature": 40.0,
                "humidity": 30.0,
                "vpd": 2.0,
                "current_moisture": 15.0,
                "batch_weight": 50.0,
                "elapsed_hours": step * 0.1,
                "ambient_temperature": 25.0,
                "ambient_humidity": 50.0,
                "crop_type": "moringa",
                "hub_location": "meru",
                "remaining_hours": 2.0,
                "quality_grade": "export",
            })
    df = pd.DataFrame(data)
    df_train, df_test = split_by_batch(df, test_size=0.25, random_state=42)

    train_batches = set(df_train["batch_id"].unique())
    test_batches = set(df_test["batch_id"].unique())

    # Zero leakage: disjoint batch sets
    assert len(train_batches.intersection(test_batches)) == 0
    assert len(train_batches) == 15
    assert len(test_batches) == 5


def test_model_artifact_benchmarks_and_size():
    meta_path = Path("backend/models/model_metadata.json")
    reg_path = Path("backend/models/remaining_time_regressor.joblib")
    cls_path = Path("backend/models/quality_grade_classifier.joblib")

    assert meta_path.exists(), "Model metadata not found. Run training pipeline first."
    assert reg_path.exists(), "Regressor artifact not found."
    assert cls_path.exists(), "Classifier artifact not found."

    # Size constraints < 5 MB
    reg_size_mb = reg_path.stat().st_size / (1024 * 1024)
    cls_size_mb = cls_path.stat().st_size / (1024 * 1024)
    assert reg_size_mb < 5.0, f"Regressor exceeds 5 MB: {reg_size_mb:.2f} MB"
    assert cls_size_mb < 5.0, f"Classifier exceeds 5 MB: {cls_size_mb:.2f} MB"

    with open(meta_path, "r") as f:
        meta = json.load(f)

    # Benchmark metrics
    benchmarks = meta["benchmarks"]
    assert benchmarks["r2_passed"] is True, f"R² target 0.85 failed: {benchmarks['r2_achieved']}"
    assert benchmarks["accuracy_passed"] is True, f"Accuracy target 0.80 failed: {benchmarks['accuracy_achieved']}"
    assert benchmarks["r2_achieved"] >= 0.85
    assert benchmarks["accuracy_achieved"] >= 0.80

