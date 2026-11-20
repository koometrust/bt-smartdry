# 02: Multi-Tier Alert Service Hardening & Scoped Alerts API

**What to build:** An authenticated, role-scoped Alerts API allowing Operators to view alerts for their Hub and Administrators to audit alerts system-wide, supported by a 3-tier dispatch configuration (`SMS_PROVIDER_MODE=mock|sandbox|live`) that ensures zero-cost automated testing, sandbox verification, and reliable live cellular SMS delivery via Africa's Talking.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `SMS_PROVIDER_MODE` added to backend settings with values `mock`, `sandbox`, and `live` (defaulting to `mock` in testing/dev).
- [ ] `alert_service.py` cleanly handles dispatch according to the configured mode: recording mock alerts without network calls, routing through sandbox, or calling live Africa's Talking credentials.
- [ ] `GET /api/v1/alerts/` lists alerts with pagination and filters (`hub_id`, `alert_type`), strictly scoping Operators to their hub's batches and allowing Administrators full visibility.
- [ ] `GET /api/v1/alerts/unread-count` returns the count of recent unread alerts for the authenticated user's scope.
- [ ] `POST /api/v1/alerts/{id}/read` marks an alert as read/acknowledged.
- [ ] Recipient phone numbers are sourced strictly from authenticated Operator accounts in compliance with the Data Protection Act 2019.
- [ ] Automated tests verify role-based scoping, query filtering, and failure fallback handling across dispatch modes.

