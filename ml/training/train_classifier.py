"""
Quality grade classifier training module.
Compares Gradient-Boosted Classifier vs Random Forest Classifier via 5-fold CV,
selects the winning architecture on validation, handles class balance,
and evaluates performance against the >= 80% accuracy target.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier

from ml.training.dataset import (
    FEATURE_COLUMNS,
    CLASSIFICATION_TARGET,
    build_preprocessor,
)


def create_classifier_pipeline(model_type: str = "gradient_boosting", random_state: int = 42) -> Pipeline:
    """
    Construct pipeline with preprocessor and chosen classifier.
    Handles class balance via balanced class weighting.
    Enforces compact tree depth so artifact stays strictly < 5 MB.
    """
    preprocessor = build_preprocessor()
    
    if model_type == "random_forest":
        estimator = RandomForestClassifier(
            n_estimators=60,
            max_depth=10,
            min_samples_split=6,
            class_weight="balanced",
            n_jobs=-1,
            random_state=random_state,
        )
    else:  # gradient_boosting
        estimator = HistGradientBoostingClassifier(
            max_iter=150,
            max_depth=7,
            learning_rate=0.1,
            class_weight="balanced",
            random_state=random_state,
        )
        
    return Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", estimator),
    ])


def evaluate_classifier_candidates(
    df_train: pd.DataFrame,
    n_splits: int = 5,
    random_state: int = 42,
    cv_batch_limit: int = 300,
) -> Tuple[str, Dict[str, Any]]:
    """
    Run 5-fold cross-validation on train batches for both candidate architectures:
    - Gradient-Boosted Classifier
    - Random Forest Classifier
    Uses up to cv_batch_limit batches for fast, high-confidence CV estimation.
    Returns the winning model type and comparison metrics.
    """
    unique_batches = df_train["batch_id"].unique()
    if len(unique_batches) > cv_batch_limit:
        rng = np.random.default_rng(random_state)
        sampled_batches = set(rng.choice(unique_batches, size=cv_batch_limit, replace=False))
        df_cv = df_train[df_train["batch_id"].isin(sampled_batches)].copy()
        unique_batches = df_cv["batch_id"].unique()
    else:
        df_cv = df_train

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    candidates = ["gradient_boosting", "random_forest"]
    results = {}
    
    for model_type in candidates:
        fold_acc = []
        fold_f1 = []
        
        for fold, (train_b_idx, val_b_idx) in enumerate(kf.split(unique_batches), 1):
            train_batches = set(unique_batches[train_b_idx])
            val_batches = set(unique_batches[val_b_idx])
            
            train_fold = df_cv[df_cv["batch_id"].isin(train_batches)]
            val_fold = df_cv[df_cv["batch_id"].isin(val_batches)]
            
            X_tr = train_fold[FEATURE_COLUMNS]
            y_tr = train_fold[CLASSIFICATION_TARGET]
            X_val = val_fold[FEATURE_COLUMNS]
            y_val = val_fold[CLASSIFICATION_TARGET]
            
            pipeline = create_classifier_pipeline(model_type=model_type, random_state=random_state + fold)
            pipeline.fit(X_tr, y_tr)
            
            preds = pipeline.predict(X_val)
            acc = accuracy_score(y_val, preds)
            f1 = f1_score(y_val, preds, average="macro")
            
            fold_acc.append(acc)
            fold_f1.append(f1)
            
        results[model_type] = {
            "cv_accuracy_mean": float(np.mean(fold_acc)),
            "cv_accuracy_std": float(np.std(fold_acc)),
            "cv_macro_f1_mean": float(np.mean(fold_f1)),
            "fold_accuracies": [float(x) for x in fold_acc],
        }
        
    # Select winning model based on validation accuracy
    winner = max(candidates, key=lambda m: results[m]["cv_accuracy_mean"])
    
    return winner, {
        "candidate_results": results,
        "selected_winner": winner,
    }


def train_classifier(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    model_type: str = "gradient_boosting",
    random_state: int = 42,
) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Train final classifier pipeline on full train set and evaluate on test set.
    """
    X_train = df_train[FEATURE_COLUMNS]
    y_train = df_train[CLASSIFICATION_TARGET]
    
    X_test = df_test[FEATURE_COLUMNS]
    y_test = df_test[CLASSIFICATION_TARGET]
    
    pipeline = create_classifier_pipeline(model_type=model_type, random_state=random_state)
    pipeline.fit(X_train, y_train)
    
    preds_test = pipeline.predict(X_test)
    
    test_accuracy = float(accuracy_score(y_test, preds_test))
    test_macro_f1 = float(f1_score(y_test, preds_test, average="macro"))
    test_weighted_f1 = float(f1_score(y_test, preds_test, average="weighted"))
    report = classification_report(y_test, preds_test, output_dict=True)
    
    metrics = {
        "model_type": model_type,
        "test_accuracy": test_accuracy,
        "test_macro_f1": test_macro_f1,
        "test_weighted_f1": test_weighted_f1,
        "benchmark_passed": bool(test_accuracy >= 0.80),
        "classification_report": report,
    }
    
    return pipeline, metrics
