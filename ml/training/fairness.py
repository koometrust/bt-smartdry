"""
Fairness and subgroup audit module for BT-SmartDry ML models.
Evaluates regression (remaining hours) and classification (quality grade) metrics
across crop types and hub locations, flagging systematic disparities.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error, accuracy_score, f1_score

from ml.training.dataset import (
    FEATURE_COLUMNS,
    REGRESSION_TARGET,
    CLASSIFICATION_TARGET,
)


def evaluate_fairness(
    regressor_pipeline: Pipeline,
    classifier_pipeline: Pipeline,
    df_test: pd.DataFrame,
    r2_disparity_threshold: float = 0.08,
    acc_disparity_threshold: float = 0.08,
) -> Dict[str, Any]:
    """
    Perform comprehensive fairness audit across crops and hubs.
    Returns structured results including overall metrics, subgroup metrics,
    and flagged disparities.
    """
    X_test = df_test[FEATURE_COLUMNS]
    y_reg_test = df_test[REGRESSION_TARGET].values
    y_cls_test = df_test[CLASSIFICATION_TARGET].values
    
    # Global predictions
    reg_preds = np.clip(regressor_pipeline.predict(X_test), 0.0, None)
    cls_preds = classifier_pipeline.predict(X_test)
    
    overall_r2 = float(r2_score(y_reg_test, reg_preds))
    overall_mae = float(mean_absolute_error(y_reg_test, reg_preds))
    overall_acc = float(accuracy_score(y_cls_test, cls_preds))
    overall_f1 = float(f1_score(y_cls_test, cls_preds, average="macro"))
    
    crops = sorted(df_test["crop_type"].unique().tolist())
    hubs = sorted(df_test["hub_location"].unique().tolist())
    
    crop_audit: Dict[str, Any] = {}
    hub_audit: Dict[str, Any] = {}
    flagged_disparities: List[Dict[str, Any]] = []
    
    # 1. Audit across crops
    for crop in crops:
        mask = (df_test["crop_type"] == crop).values
        sub_y_reg = y_reg_test[mask]
        sub_reg_preds = reg_preds[mask]
        sub_y_cls = y_cls_test[mask]
        sub_cls_preds = cls_preds[mask]
        
        sub_r2 = float(r2_score(sub_y_reg, sub_reg_preds))
        sub_mae = float(mean_absolute_error(sub_y_reg, sub_reg_preds))
        sub_rmse = float(root_mean_squared_error(sub_y_reg, sub_reg_preds))
        sub_acc = float(accuracy_score(sub_y_cls, sub_cls_preds))
        sub_f1 = float(f1_score(sub_y_cls, sub_cls_preds, average="macro"))
        
        crop_audit[crop] = {
            "n_samples": int(np.sum(mask)),
            "regressor_r2": sub_r2,
            "regressor_mae_hours": sub_mae,
            "regressor_rmse_hours": sub_rmse,
            "classifier_accuracy": sub_acc,
            "classifier_macro_f1": sub_f1,
        }
        
        if (overall_r2 - sub_r2) > r2_disparity_threshold:
            flagged_disparities.append({
                "subgroup": f"crop_type:{crop}",
                "model": "regressor",
                "metric": "r2",
                "subgroup_value": sub_r2,
                "overall_value": overall_r2,
                "gap": round(overall_r2 - sub_r2, 4),
            })
            
        if (overall_acc - sub_acc) > acc_disparity_threshold:
            flagged_disparities.append({
                "subgroup": f"crop_type:{crop}",
                "model": "classifier",
                "metric": "accuracy",
                "subgroup_value": sub_acc,
                "overall_value": overall_acc,
                "gap": round(overall_acc - sub_acc, 4),
            })
            
    # 2. Audit across hubs
    for hub in hubs:
        mask = (df_test["hub_location"] == hub).values
        sub_y_reg = y_reg_test[mask]
        sub_reg_preds = reg_preds[mask]
        sub_y_cls = y_cls_test[mask]
        sub_cls_preds = cls_preds[mask]
        
        sub_r2 = float(r2_score(sub_y_reg, sub_reg_preds))
        sub_mae = float(mean_absolute_error(sub_y_reg, sub_reg_preds))
        sub_rmse = float(root_mean_squared_error(sub_y_reg, sub_reg_preds))
        sub_acc = float(accuracy_score(sub_y_cls, sub_cls_preds))
        sub_f1 = float(f1_score(sub_y_cls, sub_cls_preds, average="macro"))
        
        hub_audit[hub] = {
            "n_samples": int(np.sum(mask)),
            "regressor_r2": sub_r2,
            "regressor_mae_hours": sub_mae,
            "regressor_rmse_hours": sub_rmse,
            "classifier_accuracy": sub_acc,
            "classifier_macro_f1": sub_f1,
        }
        
        if (overall_r2 - sub_r2) > r2_disparity_threshold:
            flagged_disparities.append({
                "subgroup": f"hub_location:{hub}",
                "model": "regressor",
                "metric": "r2",
                "subgroup_value": sub_r2,
                "overall_value": overall_r2,
                "gap": round(overall_r2 - sub_r2, 4),
            })
            
        if (overall_acc - sub_acc) > acc_disparity_threshold:
            flagged_disparities.append({
                "subgroup": f"hub_location:{hub}",
                "model": "classifier",
                "metric": "accuracy",
                "subgroup_value": sub_acc,
                "overall_value": overall_acc,
                "gap": round(overall_acc - sub_acc, 4),
            })
            
    return {
        "overall_metrics": {
            "regressor_r2": overall_r2,
            "regressor_mae_hours": overall_mae,
            "classifier_accuracy": overall_acc,
            "classifier_macro_f1": overall_f1,
        },
        "crop_subgroups": crop_audit,
        "hub_subgroups": hub_audit,
        "flagged_disparities": flagged_disparities,
        "fairness_passed": len(flagged_disparities) == 0,
    }

