# 04: Batch History, Hub Overview & Analytics Pages

**What to build:**
Implement the secondary and administrative views: Batch History (`/history`) showing completed drying cycles with their final quality grades; Hub Overview (`/hubs`) providing administrators with real-time capacity monitoring cards (out of 200 kg) across Meru, Tharaka Nithi, and Eldoret; and Analytics (`/analytics`) providing throughput metrics, crop distribution, and quality grade breakdown charts.

**Blocked by:** 02, 03

**Status:** resolved

## Acceptance Criteria
- [x] Batch History page (`/history`):
  - [x] Displays table/list of completed batches with filters by crop type, hub location, and quality grade.
  - [x] Columns: Batch ID, Crop, Weight, Start/End times, Final Moisture, and Final Quality Grade badge.
  - [x] Search and filter support.
- [x] Hub Overview page (`/hubs`, Admin only):
  - [x] 3 summary cards for Meru, Tharaka Nithi, and Eldoret.
  - [x] Visual capacity meter displaying currently loaded weight vs 200 kg capacity limit (ADR-0002).
  - [x] Count of active batches and dryer status indicators.
- [x] Analytics page (`/analytics`, Admin only):
  - [x] Key performance indicators: Total batches dried, total kilograms processed, export quality percentage.
  - [x] Quality grade distribution chart (Export vs Standard vs Downgraded).
  - [x] Crop throughput breakdown (Moringa, Prunus, Hibiscus).

## Comments
- Implemented `BatchHistoryPage.tsx` with filtering by crop type and quality grade.
- Implemented `HubOverviewPage.tsx` with regional solar dryer cards and ADR-0002 200 kg capacity meters.
- Implemented `AnalyticsPage.tsx` with KPI summary cards, quality grade ratio bars, and crop volume distributions.
- Built and validated with `npm run build` and `npm run test`.
