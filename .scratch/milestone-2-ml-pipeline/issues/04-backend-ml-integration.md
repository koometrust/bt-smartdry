# Issue 04: Backend ML Inference Integration

Status: resolved

## Description
Integrate trained models into backend:
- Create `backend/app/services/ml_service.py` to load artifacts on startup.
- Hook into `lifespan` in `backend/app/main.py`.
- Update `backend/app/services/reading_service.py` to call ML inference with fallbacks.
- Ensure prediction latency is low (< 20ms) and non-blocking.

## Comments
- Implemented `backend/app/services/ml_service.py` loading `remaining_time_regressor.joblib`, `quality_grade_classifier.joblib`, and `model_metadata.json` on startup.
- Hooked into `lifespan` in `backend/app/main.py` and exposed ML loading status in `/health`.
- Updated `backend/app/services/reading_service.py` to extract all 10 features (dryer temp, dryer RH, dryer VPD, current moisture, weight, elapsed hours, ambient temp, ambient RH, crop type, hub location) and perform real-time ML inference.
- Handled timezone-aware datetime calculations and graceful heuristic fallback.
