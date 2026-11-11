# Issue 01: Synthetic Dataset Generator

Status: resolved

## Description
Build the synthetic dataset generator in `ml/synthetic/` generating ~2,000 batches with 50-150 readings each at 5-minute intervals.
Simulate realistic solar dryer physics:
- Diurnal ambient weather cycle per hub (Meru, Tharaka Nithi, Eldoret).
- Greenhouse temperature rise and relative humidity depression inside dryer.
- Psychrometric VPD computation.
- Thin-layer exponential decay moisture curve modulated by crop type, batch weight, temperature, and VPD.
- Batch quality grade rule evaluation (Export, Standard, Downgraded) with over-drying penalties.
- Export both full reading series and snapshot tabular dataset for ML training.

## Comments
- Implemented `ml/synthetic/physics.py` with Tetens equation for saturation vapor pressure, VPD calculation, diurnal weather cycles for Meru/Tharaka Nithi/Eldoret, greenhouse solar temperature boost, and thin-layer crop drying kinetics.
- Implemented `ml/synthetic/generator.py` and `ml/synthetic/export.py`.
- Generated 2,000 batches and 223,867 reading snapshots to `ml/data/batches.csv` and `ml/data/training_snapshots.csv.gz`.
- Verified balanced distributions across hubs (678 Eldoret, 666 Meru, 656 Tharaka Nithi) and crops (676 Moringa, 675 Hibiscus, 649 Prunus).
