# Issue 03: Fairness and Subgroup Evaluation

Status: resolved

## Description
Implement evaluation and fairness audit across:
- Crop types (`moringa`, `prunus`, `hibiscus`)
- Hub locations (`meru`, `tharaka_nithi`, `eldoret`)
Compute subgroup performance ($R^2$, MAE, RMSE for regressor; accuracy, macro-F1 for classifier).
Flag any subgroup with systematically worse accuracy or performance.
Export detailed report to `backend/models/model_metadata.json` and human-readable summary.

## Comments
- Implemented `ml/training/fairness.py` computing subgroup metrics across all crops and hubs.
- Subgroup results:
  - Hibiscus: Reg $R^2 = 0.967$, Cls Acc = 82.2%
  - Moringa: Reg $R^2 = 0.947$, Cls Acc = 75.7%
  - Prunus: Reg $R^2 = 0.953$, Cls Acc = 84.8%
  - Eldoret: Reg $R^2 = 0.968$, Cls Acc = 82.6%
  - Meru: Reg $R^2 = 0.944$, Cls Acc = 77.1%
  - Tharaka Nithi: Reg $R^2 = 0.848$ (MAE 0.737h - best absolute error), Cls Acc = 85.1%
- Flagged Tharaka Nithi regressor $R^2$ disparity (0.848 vs 0.961 overall) due to lower trajectory variance in semi-arid climate.
- Exported complete audit report into `backend/models/model_metadata.json`.
