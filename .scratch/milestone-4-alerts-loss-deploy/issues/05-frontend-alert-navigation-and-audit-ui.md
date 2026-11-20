# 05: Frontend Alert Navigation, Bell Badge, and Audit Log UI (shadcn UI)

**What to build:** An integrated alert monitoring interface in the dashboard featuring a top-level `/alerts` audit page with filterable table and a header notification bell icon displaying an unread badge that opens a slide-out alert drawer, built with shadcn UI primitives and refreshed via 30-second React Query polling.

**Blocked by:** 02: Multi-Tier Alert Service Hardening & Scoped Alerts API

**Status:** resolved

- [x] Header notification bell in `Navbar.tsx` displays live unread alert badge count polled every 30 seconds.
- [x] Clicking the notification bell opens a shadcn UI slide-out drawer (`Sheet`) listing recent alerts with trigger type badges and relative timestamps.
- [x] Dedicated `/alerts` route and navigation link added for Operators and Administrators.
- [x] Alerts audit page displays a filterable data table using shadcn UI components (Table, Badge, Select, Button) with filtering by Hub and Alert Type (`Near Completion`, `Completion`, `Anomaly`).
- [x] Operators can acknowledge/mark alerts as read from both the drawer and the audit table.
- [x] Complete bilingual translation in `locales/en.json` and `locales/sw.json`.
- [x] Frontend tests verify bell badge display, drawer open/close interaction, table filtering, and role-based route access.

## Answer

Implemented in `frontend/src/components/ui/sheet.tsx`, `frontend/src/components/AlertsDrawer.tsx`, `frontend/src/pages/AlertsPage.tsx`, `frontend/src/components/Navbar.tsx`, `frontend/src/App.tsx`, and bilingual translations in `en.json` / `sw.json`.
- `Navbar.tsx` integrates the live unread alert badge and opens the `AlertsDrawer` slide-out sheet.
- `/alerts` route provides the audit log table filterable by Hub, Alert Type, and Read Status.
- Operators and Administrators can acknowledge alerts as read from both the drawer and the table.
- Verified with 18 Vitest tests, including `alertsUI.test.ts` and `authGuard.test.ts`.
