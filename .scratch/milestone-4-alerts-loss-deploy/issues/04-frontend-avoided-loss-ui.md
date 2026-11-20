# 04: Frontend Avoided-Loss UI & Analytics Integration (shadcn UI)

**What to build:** User-facing presentation of avoided harvest loss in the React dashboard using shadcn UI components, displaying physical kilograms and economic value saved on completed batch cards, historical logs, and aggregated network analytics, with full bilingual English and Kiswahili support and an explicit indicative disclaimer.

**Blocked by:** 01: Avoided-Post-Harvest-Loss Schema, Backend Engine, and Analytics Rollup

**Status:** ready-for-agent

- [ ] `BatchDetailPage.tsx` displays an "Avoided Harvest Loss" card for completed batches showing kilograms saved, KES value preserved, and the required indicative disclaimer.
- [ ] `BatchHistoryPage.tsx` includes table columns / badges displaying avoided loss kilograms and KES value for each completed batch.
- [ ] `AnalyticsPage.tsx` renders summary metric cards for total avoided loss (kg) and total value (KES) alongside crop-specific preservation breakdowns.
- [ ] All UI components adhere to shadcn UI styling patterns (Card, Badge, Table, Tooltip).
- [ ] All new labels, units, and disclaimers are translated in both `locales/en.json` and `locales/sw.json`.
- [ ] Frontend tests verify rendering of loss metrics, empty states for active batches, and language switching.

