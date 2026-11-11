"""
XGBoost Regressor training module for remaining drying hours.
Evaluates 5-fold cross-validation and held-out test performance.
Target benchmark: R² >= 0.85.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error
from xgboost import XGBRegressor

from ml.training.dataset import (
    FEATURE_COLUMNS,
    REGRESSION_TARGET,
    build_preprocessor,
)


def create_regressor_pipeline(random_state: int = 42) -> Pipeline:
    """
    Construct end-to-end scikit-learn Pipeline with ColumnTransformer preprocessor
    and XGBoost Regressor estimator.
    """
    preprocessor = build_preprocessor()
    estimator = XGBRegressor(
        n_estimators=250,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=3,
        n_jobs=-1,
        random_state=random_state,
        tree_method="hist",
    )
    return Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", estimator),
    ])


def evaluate_regressor_cv(
    df_train: pd.DataFrame,
    n_splits: int = 5,
    random_state: int = 42,
    cv_batch_limit: int = 400,
) -> Dict[str, Any]:
    """
    Perform 5-fold cross-validation on train batches for remaining hours regression.
    Uses up to cv_batch_limit batches for fast, high-confidence CV estimation.
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
    
    fold_r2 = []
    fold_mae = []
    fold_rmse = []
    
    for fold, (train_b_idx, val_b_idx) in enumerate(kf.split(unique_batches), 1):
        train_batches = set(unique_batches[train_b_idx])
        val_batches = set(unique_batches[val_b_idx])
        
        train_fold = df_cv[df_cv["batch_id"].isin(train_batches)]
        val_fold = df_cv[df_cv["batch_id"].isin(val_batches)]
        
        X_tr = train_fold[FEATURE_COLUMNS]
        y_tr = train_fold[REGRESSION_TARGET]
        X_val = val_fold[FEATURE_COLUMNS]
        y_val = val_fold[REGRESSION_TARGET]
        
        pipeline = create_regressor_pipeline(random_state=random_state + fold)
        pipeline.fit(X_tr, y_tr)
        
        preds = pipeline.predict(X_val)
        preds = np.clip(preds, a_min=0.0, a_max=None)
        
        r2 = r2_score(y_val, preds)
        mae = mean_absolute_error(y_val, preds)
        rmse = root_mean_squared_error(y_val, preds)
        
        fold_r2.append(r2)
        fold_mae.append(mae)
        fold_rmse.append(rmse)
        
    return {
        "n_folds": n_splits,
        "cv_r2_mean": float(np.mean(fold_r2)),
        "cv_r2_std": float(np.std(fold_r2)),
        "cv_mae_mean": float(np.mean(fold_mae)),
        "cv_rmse_mean": float(np.mean(fold_rmse)),
        "fold_r2": [float(x) for x in fold_r2],
    }


def train_regressor(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    random_state: int = 42,
) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Train final XGBoost regression pipeline on full train set and evaluate on test set.
    """
    X_train = df_train[FEATURE_COLUMNS]
    y_train = df_train[REGRESSION_TARGET]
    
    X_test = df_test[FEATURE_COLUMNS]
    y_test = df_test[REGRESSION_TARGET]
    
    pipeline = create_regressor_pipeline(random_state=random_state)
    pipeline.fit(X_train, y_train)
    
    preds_test = pipeline.predict(X_test)
    preds_test = np.clip(preds_test, a_min=0.0, a_max=None)
    
    test_r2 = float(r2_score(y_test, preds_test))
    test_mae = float(mean_absolute_error(y_test, preds_test))
    test_rmse = float(root_mean_squared_error(y_test, preds_test))
    
    metrics = {
        "test_r2": test_r2,
        "test_mae_hours": test_mae,
        "test_rmse_hours": test_rmse,
        "benchmark_passed": bool(test_r2 >= 0.85),
    }
    
    return pipeline, metrics
