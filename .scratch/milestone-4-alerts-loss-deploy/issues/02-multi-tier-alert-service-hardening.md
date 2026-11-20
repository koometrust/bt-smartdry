# 02: Multi-Tier Alert Service Hardening & Scoped Alerts API

**What to build:** An authenticated, role-scoped Alerts API allowing Operators to view alerts for their Hub and Administrators to audit alerts system-wide, supported by a 3-tier dispatch configuration (`SMS_PROVIDER_MODE=mock|sandbox|live`) that ensures zero-cost automated testing, sandbox verification, and reliable live cellular SMS delivery via Africa's Talking.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] `SMS_PROVIDER_MODE` added to backend settings with values `mock`, `sandbox`, and `live` (defaulting to `mock` in testing/dev).
- [x] `alert_service.py` cleanly handles dispatch according to the configured mode: recording mock alerts without network calls, routing through sandbox, or calling live Africa's Talking credentials.
- [x] `GET /api/v1/alerts/` lists alerts with pagination and filters (`hub_id`, `alert_type`), strictly scoping Operators to their hub's batches and allowing Administrators full visibility.
- [x] `GET /api/v1/alerts/unread-count` returns the count of recent unread alerts for the authenticated user's scope.
- [x] `POST /api/v1/alerts/{id}/read` marks an alert as read/acknowledged.
- [x] Recipient phone numbers are sourced strictly from authenticated Operator accounts in compliance with the Data Protection Act 2019.
- [x] Automated tests verify role-based scoping, query filtering, and failure fallback handling across dispatch modes.

## Answer

Implemented in `backend/app/core/config.py`, `backend/app/models/alert.py`, `backend/app/schemas/alert.py`, `backend/app/services/alert_service.py`, `backend/app/api/v1/endpoints/alerts.py`, and Alembic migration `0003_add_is_read_to_alerts.py`.
- `SMS_PROVIDER_MODE` supports `mock`, `sandbox`, and `live` modes.
- Sourcing recipient phone numbers strictly from authenticated user accounts maintains compliance with Kenya's Data Protection Act 2019.
- Scoped alerts API supports filtering by hub and alert type, unread alert counts, and marking alerts as read.
- Verified with unit and integration tests in `backend/tests/test_alerts_api.py`.
