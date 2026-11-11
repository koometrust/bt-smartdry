# 03: Active Batches & Batch Detail Pages

**What to build:**
Implement the primary operator views: Active Batches (`/`) with 30-second React Query polling, hub filtering (for Admin), new batch creation modal respecting the 200kg capacity limit per dryer; and the Batch Detail page (`/batches/:id`) displaying live sensor telemetry charts, ML prediction cards (remaining hours, predicted quality grade), bilingual advisory messages, and batch completion action.

**Blocked by:** 02

**Status:** resolved

## Acceptance Criteria
- [x] Active Batches page (`/`):
  - [x] Fetches batches using TanStack Query with `refetchInterval: 30000` (30s polling).
  - [x] Operators see batches for their hub; Admins see all hubs with hub filter tabs.
  - [x] Cards display crop name, initial weight, current moisture %, predicted remaining hours, predicted grade badge, and progress bar towards target moisture.
  - [x] "New Batch" modal with validation: crop type selection, weight input with real-time remaining capacity check against 200 kg limit, and optional target moisture.
- [x] Batch Detail page (`/batches/:id`):
  - [x] Real-time polling of batch metadata and recent readings.
  - [x] Interactive sensor trend chart showing moisture decline, temperature, and humidity over elapsed time.
  - [x] Prediction summary card: remaining time countdown, predicted grade badge (Export, Standard, Downgraded).
  - [x] Bilingual advisory banner: display localized action instructions in the active UI language.
  - [x] "Complete Batch" action button prompting operator confirmation and marking batch status as completed.

## Comments
- Implemented `ActiveBatchesPage.tsx` with TanStack Query 30-second refetch interval, hub filtering, and capacity meters.
- Implemented `CreateBatchModal.tsx` enforcing the 200 kg capacity limit per dryer with real-time capacity calculations.
- Implemented `BatchDetailPage.tsx` featuring `SensorChart.tsx`, `AdvisoryCard.tsx`, `PredictionBadge.tsx`, and batch completion controls.
- Tested and verified with production build passing cleanly.
