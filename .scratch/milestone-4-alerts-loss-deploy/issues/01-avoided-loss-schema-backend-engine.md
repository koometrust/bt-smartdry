# 01: Avoided-Post-Harvest-Loss Schema, Backend Engine, and Analytics Rollup

**What to build:** When an Operator marks a Batch as completed, the backend automatically calculates the physical crop preserved in kilograms and indicative financial value in KES based on crop-specific baseline loss rates and Quality Grade pricing multipliers, persisting the results on the Batch record and exposing aggregated metrics for Administrator Analytics.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] Database schema migration adds `avoided_loss_kg` (Float, nullable) and `avoided_loss_kes` (Float, nullable) to `batches` table.
- [x] `loss_service.py` implements the physical and economic loss formulation using crop baselines (Moringa 35% vs 5%, KES 300/kg; Prunus 30% vs 4%, KES 450/kg; Hibiscus 40% vs 6%, KES 250/kg).
- [x] Quality Grade pricing multipliers (Export = 1.0, Standard = 0.9, Downgraded = 0.5) are applied to the calculated KES value.
- [x] Completing a batch via `PATCH /api/v1/batches/{id}/complete` invokes the loss service, commits the calculated values to the database, and returns them in `BatchResponse`.
- [x] Analytics endpoint (`GET /api/v1/analytics/overview`) returns network-wide aggregated `total_avoided_loss_kg`, `total_avoided_loss_kes`, and crop/hub breakdowns.
- [x] Unit and integration tests verify calculation accuracy, grade penalties, edge conditions, and database persistence.

## Answer

Implemented in `backend/app/services/loss_service.py`, `backend/app/models/batch.py`, `backend/app/schemas/batch.py`, `backend/app/services/batch_service.py`, `backend/app/api/v1/endpoints/analytics.py`, and Alembic migration `0002_add_avoided_loss_to_batches.py`.
- Formulations:
  - $\text{kg\_saved} = \text{initial\_weight\_kg} \times (\text{baseline\_loss\_rate} - \text{smartdry\_loss\_rate})$
  - $\text{kes\_saved} = \text{kg\_saved} \times \text{market\_price\_per\_kg} \times \text{grade\_multiplier}$
- Batch completion via POST or PATCH persists `avoided_loss_kg` and `avoided_loss_kes`.
- Analytics endpoint `GET /api/v1/analytics/overview` provides network-wide and hub/crop aggregations.
- 8 tests passing in `test_loss_service.py` and `test_batch_completion_loss.py`.
