"""
Embedded Machine Learning Inference Service for BT-SmartDry.
Loads pre-trained XGBoost Regressor (remaining hours) and
Classifier (quality grade) at backend startup and provides low-latency predictions.
Includes graceful fallback if models are not yet trained or missing.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import joblib

from app.schemas.batch import QualityGrade

logger = logging.getLogger("btsmartdry.ml_service")

EXPECTED_FEATURES = [
    "temperature",
    "humidity",
    "vpd",
    "current_moisture",
    "batch_weight",
    "elapsed_hours",
    "ambient_temperature",
    "ambient_humidity",
    "crop_type",
    "hub_location",
]


def normalize_hub_location(loc: str) -> str:
    """Normalize hub name or location string to canonical hub key."""
    s = str(loc).lower()
    if "tharaka" in s:
        return "tharaka_nithi"
    elif "eldoret" in s:
        return "eldoret"
    elif "meru" in s:
        return "meru"
    return "meru"


class MLService:
    def __init__(self, models_dir: Optional[Path] = None):
        if models_dir is None:
            models_dir = Path(__file__).resolve().parent.parent.parent / "models"
        self.models_dir = Path(models_dir)
        self.regressor = None
        self.classifier = None
        self.metadata: Optional[Dict[str, Any]] = None
        self._is_loaded = False

    def load_models(self) -> bool:
        """
        Load regressor, classifier, and metadata from models_dir.
        Returns True if both models are successfully loaded, False otherwise.
        """
        reg_path = self.models_dir / "remaining_time_regressor.joblib"
        cls_path = self.models_dir / "quality_grade_classifier.joblib"
        meta_path = self.models_dir / "model_metadata.json"

        if not reg_path.exists() or not cls_path.exists():
            logger.warning(
                f"Model artifacts not found in {self.models_dir}. "
                "Running in fallback heuristic mode."
            )
            self._is_loaded = False
            return False

        try:
            self.regressor = joblib.load(reg_path)
            self.classifier = joblib.load(cls_path)
            if meta_path.exists():
                with open(meta_path, "r") as f:
                    self.metadata = json.load(f)
            self._is_loaded = True
            logger.info(f"Successfully loaded ML models from {self.models_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to load ML models from {self.models_dir}: {e}", exc_info=True)
            self._is_loaded = False
            return False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def predict(
        self,
        features: Dict[str, Any],
        fallback_target_moisture: float = 10.0
    ) -> Tuple[float, QualityGrade]:
        """
        Predict remaining drying hours and quality grade for a reading snapshot.
        If models are not loaded, falls back gracefully to domain heuristic rules.
        """
        current_m = float(features["current_moisture"])
        target_m = fallback_target_moisture

        if self._is_loaded and self.regressor is not None and self.classifier is not None:
            try:
                hub_loc = normalize_hub_location(str(features.get("hub_location", "meru")))
                crop_t = str(features.get("crop_type", "moringa")).lower()

                input_data = {
                    "temperature": [float(features["temperature"])],
                    "humidity": [float(features["humidity"])],
                    "vpd": [float(features["vpd"])],
                    "current_moisture": [current_m],
                    "batch_weight": [float(features.get("batch_weight", 50.0))],
                    "elapsed_hours": [float(features.get("elapsed_hours", 0.0))],
                    "ambient_temperature": [float(features.get("ambient_temperature", features["temperature"] - 10.0))],
                    "ambient_humidity": [float(features.get("ambient_humidity", features["humidity"] + 15.0))],
                    "crop_type": [crop_t],
                    "hub_location": [hub_loc],
                }
                df_input = pd.DataFrame(input_data)

                # 1. Regression: remaining hours
                if current_m <= target_m:
                    pred_hours = 0.0
                else:
                    raw_pred = float(self.regressor.predict(df_input)[0])
                    # Physical sanity bounds: moisture above target requires positive time
                    min_phys = max(0.2, (current_m - target_m) * 0.15)
                    pred_hours = max(min_phys, round(raw_pred, 2))

                # 2. Classification: quality grade
                pred_grade_str = str(self.classifier.predict(df_input)[0]).lower()
                try:
                    pred_grade = QualityGrade(pred_grade_str)
                except ValueError:
                    pred_grade = QualityGrade.STANDARD

                return pred_hours, pred_grade
            except Exception as e:
                logger.error(f"ML inference error: {e}. Falling back to heuristic.", exc_info=True)

        # Fallback physics / domain heuristic
        remaining_hours = max(0.0, (current_m - target_m) * 1.5)
        
        # Over-drying penalty per ADR-0002
        if current_m < (target_m - 2.5):
            grade = QualityGrade.DOWNGRADED
        elif current_m <= (target_m + 1.0):
            grade = QualityGrade.EXPORT
        else:
            grade = QualityGrade.STANDARD

        return round(remaining_hours, 2), grade


# Singleton instance
_ml_service: Optional[MLService] = None


def get_ml_service() -> MLService:
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service
