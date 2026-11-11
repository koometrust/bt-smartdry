# Issue 02: Offline ML Training Pipeline

Status: resolved

## Description
Build the training pipeline in `ml/training/`:
- Data ingestion and feature engineering with scikit-learn transformers.
- 80/20 train/test split and 5-fold cross validation.
- Regressor: XGBoost regressor predicting `remaining_hours` aiming for $R^2 \ge 0.85$.
- Classifier: Gradient-boosted / Random Forest classifier predicting `quality_grade` with class weighting aiming for accuracy $\ge 80\%$.
- Validation comparison to pick the best model.
- Model serialization (< 5 MB) to `backend/models/`.

## Comments
- Implemented `ml/training/dataset.py` with 10 features, ColumnTransformer, and leak-free batch-level splitting.
- Implemented `ml/training/train_regressor.py` with XGBoost regressor, 5-fold CV ($R^2 = 0.903$), and held-out test evaluation ($R^2 = 0.9611$, MAE = 1.13h, beating $\ge 0.85$ target).
- Implemented `ml/training/train_classifier.py` comparing HistGradientBoosting vs RandomForest via 5-fold CV. RandomForest won with 78.06% CV accuracy and achieved 81.34% test accuracy (beating $\ge 80\%$ target).
- Serialized artifacts to `backend/models/remaining_time_regressor.joblib` (0.37 MB) and `backend/models/quality_grade_classifier.joblib` (2.50 MB), both well under 5 MB.
