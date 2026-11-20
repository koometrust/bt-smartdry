# 01: Avoided-Post-Harvest-Loss Schema, Backend Engine, and Analytics Rollup

**What to build:** When an Operator marks a Batch as completed, the backend automatically calculates the physical crop preserved in kilograms and indicative financial value in KES based on crop-specific baseline loss rates and Quality Grade pricing multipliers, persisting the results on the Batch record and exposing aggregated metrics for Administrator Analytics.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Database schema migration adds `avoided_loss_kg` (Float, nullable) and `avoided_loss_kes` (Float, nullable) to `batches` table.
- [ ] `loss_service.py` implements the physical and economic loss formulation using crop baselines (Moringa 35% vs 5%, KES 300/kg; Prunus 30% vs 4%, KES 450/kg; Hibiscus 40% vs 6%, KES 250/kg).
- [ ] Quality Grade pricing multipliers (Export = 1.0, Standard = 0.9, Downgraded = 0.5) are applied to the calculated KES value.
- [ ] Completing a batch via `PATCH /api/v1/batches/{id}/complete` invokes the loss service, commits the calculated values to the database, and returns them in `BatchResponse`.
- [ ] Analytics endpoint (`GET /api/v1/analytics/overview`) returns network-wide aggregated `total_avoided_loss_kg`, `total_avoided_loss_kes`, and crop/hub breakdowns.
- [ ] Unit and integration tests verify calculation accuracy, grade penalties, edge conditions, and database persistence.

