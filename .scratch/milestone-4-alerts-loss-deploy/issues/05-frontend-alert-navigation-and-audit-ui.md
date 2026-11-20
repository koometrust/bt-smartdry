# 05: Frontend Alert Navigation, Bell Badge, and Audit Log UI (shadcn UI)

**What to build:** An integrated alert monitoring interface in the dashboard featuring a top-level `/alerts` audit page with filterable table and a header notification bell icon displaying an unread badge that opens a slide-out alert drawer, built with shadcn UI primitives and refreshed via 30-second React Query polling.

**Blocked by:** 02: Multi-Tier Alert Service Hardening & Scoped Alerts API

**Status:** ready-for-agent

- [ ] Header notification bell in `Navbar.tsx` displays live unread alert badge count polled every 30 seconds.
- [ ] Clicking the notification bell opens a shadcn UI slide-out drawer (`Sheet`) listing recent alerts with trigger type badges and relative timestamps.
- [ ] Dedicated `/alerts` route and navigation link added for Operators and Administrators.
- [ ] Alerts audit page displays a filterable data table using shadcn UI components (Table, Badge, Select, Button) with filtering by Hub and Alert Type (`Near Completion`, `Completion`, `Anomaly`).
- [ ] Operators can acknowledge/mark alerts as read from both the drawer and the audit table.
- [ ] Complete bilingual translation in `locales/en.json` and `locales/sw.json`.
- [ ] Frontend tests verify bell badge display, drawer open/close interaction, table filtering, and role-based route access.

