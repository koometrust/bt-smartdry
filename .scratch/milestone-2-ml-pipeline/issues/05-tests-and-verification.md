# Issue 05: Unit, Integration Tests & Benchmarking

Status: resolved

## Description
Write comprehensive test suite for:
- Synthetic data generation (physics sanity, distributions, schema).
- ML pipeline training, evaluation, and fairness metrics.
- Backend ML service startup, inference execution, and reading handling.
- Verify $R^2 \ge 0.85$ and accuracy $\ge 80\%$ benchmark requirements.

## Comments
- Implemented `ml/tests/test_physics.py` testing Tetens equation, saturation vapor pressure, psychrometric VPD calculations, diurnal weather cycles, and drying rate kinetics.
- Implemented `ml/tests/test_synthetic_generator.py` testing trajectory physics, 50-150 readings boundary, monotonic moisture decay, and schema features.
- Implemented `ml/tests/test_training_pipeline.py` testing leak-free batch splitting, ColumnTransformer preprocessors, benchmark requirements ($R^2 \ge 0.85$, accuracy $\ge 80\%$), and model artifact sizes (< 5 MB).
- Implemented `ml/tests/test_fairness.py` verifying subgroup evaluations across crops and hubs.
- Implemented `backend/tests/test_ml_service.py` verifying ML service model artifact loading, inference latency, fallback mode, and reading API integration with live predictions.
- All 21 tests pass with zero warnings or errors.
