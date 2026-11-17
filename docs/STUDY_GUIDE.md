# BT-SmartDry: Project Defense & Technical Study Guide

This document is the comprehensive reference guide for presenting and defending the **BT-SmartDry** capstone project to academic supervisors and technical evaluators. It covers architectural decisions, machine learning mechanics, codebase navigation, live modification procedures, and defense questions.

---

## 1. Executive Summary & Project Overview

**BT-SmartDry** is an IoT monitoring, machine learning prediction, and bilingual advisory system designed for **Botanic Treasures'** commercial solar crop dryers.

- **Beneficiary:** Women-led agricultural processing hubs in Kenya.
- **3 Regional Hubs:**
  1. **Meru Hub** (Highland agroforestry zone, primary crop: *Moringa Oleifera*).
  2. **Tharaka Nithi Hub** (Warm semi-arid solar basin, primary crop: *Hibiscus Sabdariffa*).
  3. **Eldoret Hub** (High-altitude Western highlands, primary crop: *Prunus Africana*).
- **Core Dual ML Objectives:**
  1. **Remaining Drying Time Prediction:** Continuous non-linear regression predicting hours until target moisture is reached ($R^2 \ge 0.85$ target; **$0.961$ achieved**).
  2. **Final Quality Grade Classification:** Multi-class classification predicting commercial grade—*Export*, *Standard*, or *Downgraded* ($\ge 80\%$ accuracy target; **$81.34\%$ achieved**).
- **Embedded Bilingual Advisory:** Plain-language actionable recommendations in **English** and **Kiswahili** delivered via web dashboard and SMS alerts (via Africa's Talking), strictly avoiding black-box LLM hallucinations ([ADR-0001](adr/0001-templated-advisories-over-llm.md)).

---

## 2. Codebase Map & Key Seams

When presenting to your supervisor, use this table to navigate the repository with confidence:

| Concept / Capability | File Path | Key Functions / Highlights |
|---|---|---|
| **Feature Definitions** | `ml/training/dataset.py` | `NUMERIC_FEATURES`, `CATEGORICAL_FEATURES` (10 total features) |
| **Leak-Free Splitting** | `ml/training/dataset.py` | `split_by_batch(df, test_size=0.2)` (split by `batch_id`) |
| **Drying Time Regressor** | `ml/training/train_regressor.py` | `create_regressor_pipeline`, `train_regressor` (XGBoost Regressor) |
| **Grade Classifier Tournament**| `ml/training/train_classifier.py`| `evaluate_classifier_candidates` (5-fold CV Random Forest vs HistGradientBoosting) |
| **Pipeline Runner & Serialization**| `ml/training/pipeline.py` | Orchestrates training, benchmark assertion, fairness audit, serialization |
| **Model Metadata & Audit** | `backend/models/model_metadata.json` | Recorded metrics, artifact sizes (< 3 MB total), CV results, fairness gap |
| **Embedded Backend Inference** | `backend/app/services/ml_service.py` | `MLService` singleton loaded at FastAPI startup (`lifespan`) |
| **Reading Ingestion & Advisory**| `backend/app/services/reading_service.py` | Computes elapsed time, runs inference, dispatches bilingual advisory |
| **IoT Telemetry Simulator** | `simulator/main.py` | Multi-batch, multi-hub real-time streaming process |
| **Simulator Physics Engine** | `simulator/physics.py` & `ml/synthetic/physics.py` | Tetens vapor pressure, psychrometric VPD, thin-layer decay kinetics |
| **React Dashboard & UI** | `frontend/src/` | 6 routes, React Query 30s polling, shadcn/ui components, bilingual i18n |

---

## 3. Machine Learning Deep Dive

### A. The 10 Features & Physical Justification
The model takes a snapshot vector of 10 features per sensor reading:
1. `temperature` (°C, dryer internal): Heat drives evaporation.
2. `humidity` (%, dryer internal): Ambient moisture capacity inside collector.
3. `vpd` (kPa, Vapor Pressure Deficit): True thermodynamic drying force calculated via Tetens formula:
   $$\text{VP}_{\text{sat}} = 0.61078 \times \exp\left(\frac{17.27 \times T}{T + 237.3}\right)$$
   $$\text{VPD} = \text{VP}_{\text{sat}} \times \left(1 - \frac{\text{RH}}{100}\right)$$
4. `current_moisture` (%): Current crop moisture content.
5. `batch_weight` (kg): Loaded harvest mass (influences bed resistance and air flow).
6. `elapsed_hours` (hours): Duration since drying commenced.
7. `ambient_temperature` (°C): Exterior atmospheric temperature.
8. `ambient_humidity` (%): Exterior relative humidity.
9. `crop_type` (Categorical: `moringa`, `hibiscus`, `prunus`): Distinct cellular moisture binding and tissue geometry.
10. `hub_location` (Categorical: `meru`, `tharaka_nithi`, `eldoret`): Altitude and microclimatic diurnal variations.

### B. Train / Test Split Methodology
In `ml/training/dataset.py`:
- **Split Unit:** Partitioned strictly on `batch_id`, **not row-by-row**.
- **Data Leakage Prevention:** Each batch contains 50–150 chronological readings. If split row-wise randomly, reading $t$ would be in training while $t+5\text{ min}$ would be in test, resulting in synthetic overfitting where the model memorizes individual batch curves rather than learning general drying thermodynamics.
- **Why 80% Train / 20% Test?**
  - Our dataset has **2,000 batches** (223,867 reading snapshots).
  - 80% training = **1,600 batches** (~176,500 snapshots) providing ample density across the 3 crops and 3 weather cycles.
  - 20% test = **400 batches** (**47,354 snapshots**) held out. 47,354 samples provide high statistical power (standard error $< 0.003$), allowing confident verification of $R^2$ and accuracy across sub-groups.
  - A 70/30 or 75/25 split would withhold 100–200 batches from training without yielding any additional statistical power on validation.

### C. Live Code Modification Procedure
If the supervisor asks you to change the train/test ratio (e.g. to 75/25 or 70/30):
1. Open `ml/training/dataset.py` at line 75:
   ```python
   def split_by_batch(
       df: pd.DataFrame,
       test_size: float = 0.25,  # Change 0.2 to 0.25 (75/25) or 0.30 (70/30)
       random_state: int = 42
   ) -> Tuple[pd.DataFrame, pd.DataFrame]:
   ```
2. Retrain and regenerate artifacts in terminal:
   ```bash
   source .venv/bin/activate
   python -m ml.training.pipeline
   ```
3. Inspect the updated metrics generated in `backend/models/model_metadata.json`.

### D. Model Tournament & Benchmark Results
- **Drying-Time Regressor:** XGBoost Regressor (`n_estimators=250, max_depth=6, learning_rate=0.1`).
  - Target: $R^2 \ge 0.85$
  - **Achieved: $R^2 = 0.961$**, Mean Absolute Error = **$1.13$ hours**.
- **Quality-Grade Classifier:** 5-Fold Cross-Validation Tournament between `HistGradientBoostingClassifier` and `RandomForestClassifier`:
  - `HistGradientBoostingClassifier`: Mean CV Accuracy = $67.60\%$.
  - `RandomForestClassifier`: Mean CV Accuracy = **$78.06\%$**.
  - **Selected Winner:** Random Forest (`class_weight="balanced"` to mitigate imbalanced downgraded/export classes).
  - Target: Accuracy $\ge 80.0\%$
  - **Achieved: $81.34\%$ Accuracy**, Macro F1 = **$0.797$**.
- **Artifact Constraints:**
  - `remaining_time_regressor.joblib`: **0.37 MB**
  - `quality_grade_classifier.joblib`: **2.50 MB**
  - Both strictly respect the **$< 5.0$ MB** lightweight deployment limit.

---

## 4. Architectural Decisions (ADRs)

1. **[ADR-0001: Templated Advisories Over LLM](adr/0001-templated-advisories-over-llm.md)**
   - *Decision:* Generate advisories using localized template strings (`locales/en.json`, `locales/sw.json`) populated with variables, rather than a generative LLM.
   - *Rationale:* Zero hallucination risk for agronomic advice, sub-millisecond response latency, zero cloud inference cost, and guaranteed Kiswahili grammatical parity.
2. **[ADR-0002: Multi-Batch Per Dryer with 200 kg Limit](adr/0002-multi-batch-per-dryer.md)**
   - *Decision:* One physical solar dryer per hub, but allowing multiple concurrent batches of different crops sharing the collector, strictly bounded by a 200 kg capacity meter.
   - *Rationale:* Reflects actual cooperative operations where farmers bring varying harvest sizes (e.g., 30 kg Moringa + 40 kg Hibiscus).

---

## 5. Defense Q&A: Anticipated Supervisor Inquiries

### Q: "Why synthetic data instead of physical IoT sensors?"
> **Answer:** "A single physical drying cycle for Prunus or Moringa takes 2 to 3 full days. Collecting 2,000 batches of empirical data across 3 regions in Kenya would require over 12 years of continuous logging. Therefore, synthetic data generation based on published thin-layer exponential drying kinetics and diurnal solar thermodynamics was used to build and validate the end-to-end architecture before deployment."

### Q: "How does the backend prevent over-drying?"
> **Answer:** "Over-drying causes substantial commercial loss (loss of bioactive volatile oils in Moringa and bark degradation in Prunus). In `ml/synthetic/physics.py` and `backend/app/services/reading_service.py`, moisture dropping more than 2.5% below target automatically downgrades the batch grade to `downgraded` and triggers an urgent near-completion SMS alert."

### Q: "Why embed ML models inside FastAPI instead of deploying a separate microservice (like TorchServe or Triton)?"
> **Answer:** "Our models are lightweight ($< 3$ MB combined) and CPU inference takes less than 5 milliseconds. Creating a separate ML microservice would add unnecessary network serialization overhead, double our container memory footprint on Render's free tier, and introduce an additional point of failure."

### Q: "How does the frontend handle real-time telemetry without WebSockets?"
> **Answer:** "As documented in `docs/context.md`, solar drying kinetics evolve over hours, not milliseconds. React Query polling every 30 seconds (`refetchInterval: 30000`) avoids persistent WebSocket connection drops in rural Kenyan hubs with unstable 3G/Edge connections while providing fresh data."
