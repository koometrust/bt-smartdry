# 05: End-to-End Verification, Production Build & CI

**What to build:**
Comprehensive unit, component, and integration verification for the telemetry simulator and React frontend dashboard. Ensure production build (`npm run build`) runs cleanly, Vitest/pytest tests pass, Dockerfile and Docker Compose configurations work seamlessly, and CI workflow incorporates frontend and simulator testing.

**Blocked by:** 01, 04

**Status:** resolved

## Acceptance Criteria
- [x] Frontend unit & component tests verifying authentication guards, i18n translation rendering, capacity calculator, and batch cards.
- [x] Simulator automated tests verifying physics calculation, telemetry payload validation, error recovery, and batch creation.
- [x] Verify `npm run build` succeeds without type errors or bundler warnings.
- [x] Verify Dockerfile in `frontend/` (multi-stage build with nginx) and `simulator/` builds properly.
- [x] Update `docker-compose.yml` and GitHub Actions CI workflow (`.github/workflows/ci.yml`) to validate frontend build, simulator tests, and backend tests.
- [x] Verify end-to-end flow: start backend, run simulator streaming readings, verify batch updates with ML predictions, and render in frontend.

## Comments
- Validated all 27 Python tests across backend, ML, and simulator services (`pytest ml/tests/ backend/tests/ simulator/test_simulator.py`).
- Validated all 5 frontend Vitest tests (`npm run test`) for i18n key consistency and capacity rules.
- Validated production build (`npm run build`) creating optimized distribution bundles.
- Configured CI workflow in `.github/workflows/ci.yml` covering Python tests, frontend tests, and production build.
- Updated `docker-compose.yml` port mappings for frontend nginx container.
