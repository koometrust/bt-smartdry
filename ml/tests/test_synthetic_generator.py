import pytest
import numpy as np
import pandas as pd

from ml.synthetic.generator import generate_batch_trajectory, generate_synthetic_dataset
from ml.training.dataset import FEATURE_COLUMNS, REGRESSION_TARGET, CLASSIFICATION_TARGET


def test_batch_trajectory_physics_and_schema():
    rng = np.random.default_rng(42)
    start_dt = pd.Timestamp("2026-06-01 08:00:00+00:00").to_pydatetime()
    batch_rec, readings = generate_batch_trajectory(
        batch_idx=1,
        crop_type="moringa",
        hub_location="meru",
        batch_weight_kg=50.0,
        start_dt=start_dt,
        target_moisture_pct=10.0,
        rng=rng,
        quality_profile="export",
    )

    # 1. Spec check: 50 to 150 readings per batch
    assert 50 <= len(readings) <= 150
    assert batch_rec["total_readings"] == len(readings)

    # 2. Moisture must generally decay monotonically
    moisture_series = [r["current_moisture"] for r in readings]
    assert moisture_series[0] > moisture_series[-1]
    assert moisture_series[-1] < 20.0

    # 3. Snapshot features must contain all 10 canonical features
    first_snapshot = readings[0]
    for feat in FEATURE_COLUMNS:
        assert feat in first_snapshot, f"Missing feature: {feat}"
    assert REGRESSION_TARGET in first_snapshot
    assert CLASSIFICATION_TARGET in first_snapshot

    # 4. Remaining hours non-negative and decreasing
    assert first_snapshot["remaining_hours"] >= readings[-1]["remaining_hours"]
    assert readings[-1]["remaining_hours"] >= 0.0


def test_generate_synthetic_dataset_distributions():
    df_batches, df_snapshots = generate_synthetic_dataset(num_batches=30, random_seed=99)

    assert len(df_batches) == 30
    assert len(df_snapshots) >= 30 * 50

    # Verify all crops and hubs represented
    assert set(df_batches["crop_type"].unique()) == {"moringa", "prunus", "hibiscus"}
    assert set(df_batches["hub_location"].unique()) == {"meru", "tharaka_nithi", "eldoret"}

    # Verify quality grades present
    grades = set(df_batches["quality_grade"].unique())
    assert "export" in grades
    assert "downgraded" in grades

