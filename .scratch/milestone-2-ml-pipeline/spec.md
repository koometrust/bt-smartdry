# Milestone 2 Spec: Synthetic Dataset Generation & Offline ML Training Pipeline

## Overview
Milestone 2 implements the data generation and offline machine learning pipeline for BT-SmartDry:
1. Synthetic dataset generation simulating ~2,000 batches with 5-minute interval sensor readings across 3 hubs and 3 crops with realistic thermodynamics and drying physics.
2. Offline ML training pipeline with 80/20 train/test split, 5-fold cross-validation, class balancing, model selection, and fairness evaluation.
3. Target benchmarks:
   - Drying-time regressor (XGBoost): $R^2 \ge 0.85$ on held-out test set.
   - Quality-grade classifier (Gradient Boosting / Random Forest): accuracy $\ge 80\%$ on held-out test set.
4. Model serialization (< 5 MB per artifact) into `backend/models/`.
5. Backend ML inference engine loaded during FastAPI startup and embedded into `reading_service.py`.

## Data Model & Features
- **10 Features:**
  - `temperature` (°C, dryer interior)
  - `humidity` (%, dryer interior)
  - `vpd` (kPa, dryer interior vapour pressure deficit)
  - `current_moisture` (%)
  - `batch_weight` (kg)
  - `crop_type` ("moringa", "prunus", "hibiscus")
  - `hub_location` ("meru", "tharaka_nithi", "eldoret")
  - `elapsed_hours` (hours since batch start)
  - `ambient_temperature` (°C, exterior)
  - `ambient_humidity` (%, exterior)
- **Targets:**
  - `remaining_hours`: Non-negative float
  - `quality_grade`: Categorical string ("export", "standard", "downgraded")

