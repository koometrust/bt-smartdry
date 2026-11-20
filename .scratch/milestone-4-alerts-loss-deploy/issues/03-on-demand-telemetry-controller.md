# 03: On-Demand Cloud Telemetry Controller API & CLI Runner

**What to build:** An on-demand telemetry controller accessible via authenticated REST API endpoints and a CLI runner that starts and stops streaming sensor readings across hubs, enabling live interactive demonstrations without running a continuous 24/7 background daemon that exhausts free-tier cloud compute quotas.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `POST /api/v1/simulator/start` initiates background telemetry generation for active batches with configurable tick interval.
- [ ] `POST /api/v1/simulator/stop` gracefully halts the running telemetry simulation process.
- [ ] `GET /api/v1/simulator/status` returns the operational status (running / idle), active simulated batch count, and timestamp of the last reading emitted.
- [ ] Authentication guards ensure only authorized users (Operators and Administrators) can invoke simulator controls.
- [ ] Standalone CLI script (`simulator/run_ondemand.py` or `python -m simulator.main --burst`) allows manual or scripted demonstration triggering.
- [ ] Integration tests verify start, status reporting, concurrent batch telemetry emission, and clean termination.

