# 01: Multi-Batch IoT Telemetry Simulator

**What to build:**
A robust, standalone Python simulator service (`simulator/`) that streams realistic drying telemetry to the FastAPI backend. It simulates multiple concurrent batches across the 3 hubs (Meru, Tharaka Nithi, Eldoret) using the physics-based thin-layer drying model and weather cycle. Configurable interval down to 1 second for rapid demonstrations, with automatic batch auto-discovery or creation.

**Blocked by:** None (can start immediately)

**Status:** resolved

## Acceptance Criteria
- [x] Implement `simulator/main.py` and supporting modules using `httpx` and `pydantic`.
- [x] Connects to backend API, authenticates using seed operator credentials, and checks for active batches across hubs.
- [x] If no active batches exist, provisions realistic demo batches (e.g., Moringa in Meru, Prunus in Eldoret, Hibiscus in Tharaka Nithi) within the 200 kg capacity limit.
- [x] Generates coherent sensor readings (dryer temp, dryer humidity, ambient temp, ambient humidity, VPD, moisture) at intervals defined by `SIMULATOR_INTERVAL_SECONDS` (default: 5s, customizable).
- [x] Posts readings to `/api/v1/readings/`, triggering the backend ML inference and alert dispatching logic.
- [x] Handles batch completion when target moisture is reached and gracefully handles server connection errors.
- [x] Includes test coverage (`simulator/test_simulator.py`) for simulator physics, telemetry serialization, and mock API streaming.

## Comments
- Implemented `simulator/physics.py` with Tetens formula, saturation vapor pressure, psychrometric VPD, hub-specific diurnal curves, greenhouse thermal amplification, and thin-layer exponential moisture kinetics.
- Implemented `simulator/main.py` with multi-hub multi-batch concurrency, auto-discovery of hubs, auto-creation of demo batches up to 200kg limit, virtual kinetics advancement, and clean shutdown handling.
- Implemented `simulator/test_simulator.py` with 6 unit tests covering physics bounds, monotonic moisture decay, and mock API streaming; 100% tests pass.
