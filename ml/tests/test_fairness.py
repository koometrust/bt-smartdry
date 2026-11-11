import pytest
import pandas as pd
import numpy as np

from ml.training.fairness import evaluate_fairness
from ml.training.train_regressor import create_regressor_pipeline
from ml.training.train_classifier import create_classifier_pipeline
from ml.training.dataset import FEATURE_COLUMNS, REGRESSION_TARGET, CLASSIFICATION_TARGET


def test_fairness_audit_structure():
    # Build a small deterministic test dataset across all crops and hubs
    rows = []
    crops = ["moringa", "prunus", "hibiscus"]
    hubs = ["meru", "tharaka_nithi", "eldoret"]

    for crop in crops:
        for hub in hubs:
            for i in range(15):
                rows.append({
                    "batch_id": f"b_{crop}_{hub}_{i}",
                    "temperature": 42.0 + (i % 5),
                    "humidity": 35.0 - (i % 4),
                    "vpd": 2.2,
                    "current_moisture": 18.0 - (i % 6),
                    "batch_weight": 50.0,
                    "elapsed_hours": float(i * 0.5),
                    "ambient_temperature": 26.0,
                    "ambient_humidity": 55.0,
                    "crop_type": crop,
                    "hub_location": hub,
                    "remaining_hours": max(0.0, 5.0 - (i * 0.3)),
                    "quality_grade": "export" if i % 2 == 0 else "standard",
                })
    df_test = pd.DataFrame(rows)

    # Fit small pipeline for test evaluation
    reg = create_regressor_pipeline(random_state=42)
    reg.fit(df_test[FEATURE_COLUMNS], df_test[REGRESSION_TARGET])

    cls_pipe = create_classifier_pipeline(model_type="gradient_boosting", random_state=42)
    cls_pipe.fit(df_test[FEATURE_COLUMNS], df_test[CLASSIFICATION_TARGET])

    audit = evaluate_fairness(reg, cls_pipe, df_test, r2_disparity_threshold=0.15)

    assert "overall_metrics" in audit
    assert "crop_subgroups" in audit
    assert "hub_subgroups" in audit
    assert set(audit["crop_subgroups"].keys()) == {"moringa", "prunus", "hibiscus"}
    assert set(audit["hub_subgroups"].keys()) == {"meru", "tharaka_nithi", "eldoret"}

