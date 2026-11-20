# 03: On-Demand Cloud Telemetry Controller API & CLI Runner

**What to build:** An on-demand telemetry controller accessible via authenticated REST API endpoints and a CLI runner that starts and stops streaming sensor readings across hubs, enabling live interactive demonstrations without running a continuous 24/7 background daemon that exhausts free-tier cloud compute quotas.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] `POST /api/v1/simulator/start` initiates background telemetry generation for active batches with configurable tick interval.
- [x] `POST /api/v1/simulator/stop` gracefully halts the running telemetry simulation process.
- [x] `GET /api/v1/simulator/status` returns the operational status (running / idle), active simulated batch count, and timestamp of the last reading emitted.
- [x] Authentication guards ensure only authorized users (Operators and Administrators) can invoke simulator controls.
- [x] Standalone CLI script (`simulator/run_ondemand.py` or `python -m simulator.main --burst`) allows manual or scripted demonstration triggering.
- [x] Integration tests verify start, status reporting, concurrent batch telemetry emission, and clean termination.

## Answer

Implemented in `backend/app/services/simulator_service.py`, `backend/app/services/physics.py`, `backend/app/api/v1/endpoints/simulator.py`, `backend/app/api/v1/router.py`, `simulator/main.py` (`--burst` and `--interval` support), and CLI runner `simulator/run_ondemand.py`.
- Endpoints `POST /api/v1/simulator/start`, `POST /api/v1/simulator/stop`, and `GET /api/v1/simulator/status` require JWT authentication.
- CLI script `simulator/run_ondemand.py --burst N --interval S` enables bounded on-demand telemetry bursts for presentations and tests without consuming continuous compute quotas.
- Verified by integration tests in `backend/tests/test_simulator_api.py`.
