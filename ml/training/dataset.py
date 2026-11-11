"""
Dataset preparation, feature specifications, and train/test splitting for BT-SmartDry.
"""

from typing import List, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# The 10 canonical features specified in docs/context.md
NUMERIC_FEATURES: List[str] = [
    "temperature",
    "humidity",
    "vpd",
    "current_moisture",
    "batch_weight",
    "elapsed_hours",
    "ambient_temperature",
    "ambient_humidity",
]

CATEGORICAL_FEATURES: List[str] = [
    "crop_type",
    "hub_location",
]

FEATURE_COLUMNS: List[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES

REGRESSION_TARGET: str = "remaining_hours"
CLASSIFICATION_TARGET: str = "quality_grade"


def build_preprocessor() -> ColumnTransformer:
    """
    Build scikit-learn ColumnTransformer for standard feature encoding.
    Passes scaled numeric features and one-hot encoded categorical features.
    """
    return ColumnTransformer(
        transformers=[
            (
                "num",
                StandardScaler(),
                NUMERIC_FEATURES,
            ),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
    )


def load_dataset(dataset_path: str = "ml/data/training_snapshots.csv.gz") -> pd.DataFrame:
    """Load training snapshot dataset from disk."""
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot dataset not found at {path}. Run synthetic generator first.")
    
    df = pd.read_csv(path)
    
    # Ensure expected columns are present
    missing = [c for c in FEATURE_COLUMNS + [REGRESSION_TARGET, CLASSIFICATION_TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
        
    return df


def split_by_batch(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split snapshot dataset by batch_id into 80% train and 20% test.
    This guarantees zero data leakage between train and test batches.
    """
    unique_batches = df["batch_id"].unique()
    rng = np.random.default_rng(random_state)
    shuffled_batches = rng.permutation(unique_batches)
    
    split_idx = int(len(shuffled_batches) * (1.0 - test_size))
    train_batches = set(shuffled_batches[:split_idx])
    test_batches = set(shuffled_batches[split_idx:])
    
    df_train = df[df["batch_id"].isin(train_batches)].copy().reset_index(drop=True)
    df_test = df[df["batch_id"].isin(test_batches)].copy().reset_index(drop=True)
    
    return df_train, df_test

