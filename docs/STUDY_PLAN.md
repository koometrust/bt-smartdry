# BT-SmartDry: Quick Defense Study Plan & Cheat Sheet

> **Time to review:** 5–10 minutes before meeting your supervisor.  
> **Full deep dive:** [`docs/STUDY_GUIDE.md`](file:///home/jude/Develop/DKUT/bt-smartdry/docs/STUDY_GUIDE.md)

---

## 1. 30-Second Elevator Pitch
> *"BT-SmartDry is an IoT telemetry, dual-model machine learning, and bilingual advisory system engineered for commercial solar crop dryers operated by women-led agricultural hubs in Kenya (Meru, Tharaka Nithi, and Eldoret). It predicts remaining drying time using an XGBoost regressor ($R^2 = 0.961$) and predicts post-harvest quality grade using a Random Forest classifier ($81.34\%$ accuracy), serving real-time agronomic guidance in English and Kiswahili without generative LLM hallucinations."*

---

## 2. The 5 Top Supervisor Questions (Instant Answers)

### Q1: "In which file did you do the machine learning?"
* **Features & Data Splitting:** [`ml/training/dataset.py`](file:///home/jude/Develop/DKUT/bt-smartdry/ml/training/dataset.py)
* **Drying-Time Regressor:** [`ml/training/train_regressor.py`](file:///home/jude/Develop/DKUT/bt-smartdry/ml/training/train_regressor.py) (XGBoost Regressor)
* **Quality-Grade Classifier:** [`ml/training/train_classifier.py`](file:///home/jude/Develop/DKUT/bt-smartdry/ml/training/train_classifier.py) (Random Forest Classifier)
* **Full Pipeline & Serialization:** [`ml/training/pipeline.py`](file:///home/jude/Develop/DKUT/bt-smartdry/ml/training/pipeline.py)
* **Live FastAPI Inference:** [`backend/app/services/ml_service.py`](file:///home/jude/Develop/DKUT/bt-smartdry/backend/app/services/ml_service.py) (Loaded once at startup)

---

### Q2: "How did you split the data, and why split by batch instead of random rows?"
* **Function:** `split_by_batch(df, test_size=0.2)` in [`ml/training/dataset.py`](file:///home/jude/Develop/DKUT/bt-smartdry/ml/training/dataset.py).
* **Why Batch-level?** A crop drying cycle logs readings every 5 minutes (50–150 rows per batch). A naive random split would place reading $t$ in train and $t+5\text{ min}$ in test—causing **temporal data leakage**. The model would just memorize individual curves. Splitting by unique `batch_id` tests true generalization to completely unseen drying batches.
* **Why 80/20 and not 75/25 or 70/30?**
  * We have 2,000 batches (223,867 readings).
  * 80% train = **1,600 batches** (robust coverage across 3 crops, 3 hubs, and seasonal weather).
  * 20% test = **400 batches (47,354 reading snapshots)**. 47,354 test observations provide massive statistical power (standard error $< 0.003$). A 75/25 or 70/30 split needlessly takes away training data without any statistical benefit on the test set.

---

### Q3: "What if I ask you to change the split to 75/25 or 70/30 right now?"
**Steps to demonstrate live:**
1. Open [`ml/training/dataset.py`](file:///home/jude/Develop/DKUT/bt-smartdry/ml/training/dataset.py#L74-L79):
   ```python
   def split_by_batch(
       df: pd.DataFrame,
       test_size: float = 0.25,  # change 0.2 to 0.25 (75/25) or 0.30 (70/30)
       random_state: int = 42
   ) -> Tuple[pd.DataFrame, pd.DataFrame]:
   ```
2. Run pipeline in terminal:
   ```bash
   python -m ml.training.pipeline
   ```
3. Show the newly generated evaluation metrics and timestamps in [`backend/models/model_metadata.json`](file:///home/jude/Develop/DKUT/bt-smartdry/backend/models/model_metadata.json).

---

### Q4: "What are your features, and what is VPD?"
* **10 Features:**
  - 8 Numeric: `temperature`, `humidity`, `vpd`, `current_moisture`, `batch_weight`, `elapsed_hours`, `ambient_temperature`, `ambient_humidity`.
  - 2 Categorical: `crop_type` (`moringa`, `hibiscus`, `prunus`), `hub_location` (`meru`, `tharaka_nithi`, `eldoret`).
* **Why VPD (Vapor Pressure Deficit)?** Relative humidity alone is misleading because warm air holds more moisture than cold air. VPD calculates the actual drying force (the difference between saturation vapor pressure and actual vapor pressure via the Tetens formula). It is the single most physically accurate indicator of crop evaporation rate.

---

### Q5: "What models did you choose and what are the results?"
* **Drying Time (Regression):** **XGBoost Regressor**
  - Result: **$R^2 = 0.961$** (spec target $\ge 0.85$), MAE = **$1.13$ hours**.
* **Quality Grade (Classification):** **Random Forest** (won 5-fold CV tournament against HistGradientBoosting: $78.06\%$ vs $67.60\%$)
  - Result: **$81.34\%$ Accuracy** (spec target $\ge 80.0\%$), Macro F1 = **$0.797$**.
  - Uses `class_weight="balanced"` to protect minority quality classes.
* **Lightweight:** Combined serialized artifact size is **$< 2.9$ MB** (well under the 5 MB ceiling).

---

## 3. Core Architectural Decisions (ADRs)

| Decision | What we decided | Why we decided it |
|---|---|---|
| **[ADR-0001](adr/0001-templated-advisories-over-llm.md)** | Templated bilingual strings (`en.json`, `sw.json`) instead of LLMs | Zero agronomic hallucination risk, sub-millisecond execution, zero API costs, verified grammatical Swahili. |
| **[ADR-0002](adr/0002-multi-batch-per-dryer.md)** | Multi-batch support up to 200 kg per dryer | Real solar collectors hold multiple farmers' harvests simultaneously (e.g. 50 kg Moringa + 80 kg Hibiscus). |
| **No WebSockets** | React Query with 30s background polling | Crop drying evolves over hours; persistent WebSockets disconnect frequently on rural Kenyan 2G/3G networks. |

---

## 4. Quick Live Demo Commands

If your supervisor asks to see the running system:

```bash
# 1. Backend (Terminal 1)
source .venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000

# 2. Frontend (Terminal 2)
cd frontend
npm run dev
# Open http://localhost:5173

# 3. Telemetry Simulator (Terminal 3)
source .venv/bin/activate
python -m simulator.main --speed 60.0
```

* **Demo Accounts:**
  - Manager: `manager@meru.bt.co.ke` / `SmartDry#2024`
  - Operator: `operator@meru.bt.co.ke` / `SmartDry#2024`
