# 04: Frontend Avoided-Loss UI & Analytics Integration (shadcn UI)

**What to build:** User-facing presentation of avoided harvest loss in the React dashboard using shadcn UI components, displaying physical kilograms and economic value saved on completed batch cards, historical logs, and aggregated network analytics, with full bilingual English and Kiswahili support and an explicit indicative disclaimer.

**Blocked by:** 01: Avoided-Post-Harvest-Loss Schema, Backend Engine, and Analytics Rollup

**Status:** resolved

- [x] `BatchDetailPage.tsx` displays an "Avoided Harvest Loss" card for completed batches showing kilograms saved, KES value preserved, and the required indicative disclaimer.
- [x] `BatchHistoryPage.tsx` includes table columns / badges displaying avoided loss kilograms and KES value for each completed batch.
- [x] `AnalyticsPage.tsx` renders summary metric cards for total avoided loss (kg) and total value (KES) alongside crop-specific preservation breakdowns.
- [x] All UI components adhere to shadcn UI styling patterns (Card, Badge, Table, Tooltip).
- [x] All new labels, units, and disclaimers are translated in both `locales/en.json` and `locales/sw.json`.
- [x] Frontend tests verify rendering of loss metrics, empty states for active batches, and language switching.

## Answer

Implemented in `frontend/src/pages/BatchDetailPage.tsx`, `frontend/src/pages/BatchHistoryPage.tsx`, `frontend/src/pages/AnalyticsPage.tsx`, `frontend/src/types/index.ts`, `frontend/src/api/client.ts`, and translation files `en.json` / `sw.json`.
- Batch Detail presents the Avoided Harvest Loss card upon completion with kilograms saved, KES value, and the indicative disclaimer: *"Indicative post-harvest metric; non-certified carbon or agronomic claim"*.
- Batch History table features an Avoided Loss column showing kg and KES preserved.
- Analytics page aggregates network-wide preserved biomass and economic value.
- Full bilingual coverage verified across 16 Vitest tests, including `avoidedLoss.test.ts`.
