"""
Unit tests for the BT-SmartDry IoT Telemetry Simulator.
"""

import pytest
import math
from simulator.physics import (
    calculate_saturation_vapor_pressure,
    calculate_vpd,
    simulate_ambient,
    simulate_dryer,
    next_moisture_level,
    HUB_CLIMATES,
    CROP_PARAMETERS,
)
from simulator.main import (
    TelemetrySimulator,
    SIMULATOR_USERNAME,
    SIMULATOR_PASSWORD,
)


def test_saturation_vapor_pressure():
    # At 20°C: ~2.34 kPa
    vp_20 = calculate_saturation_vapor_pressure(20.0)
    assert 2.30 <= vp_20 <= 2.40

    # At 50°C: ~12.34 kPa
    vp_50 = calculate_saturation_vapor_pressure(50.0)
    assert 12.0 <= vp_50 <= 12.6


def test_vpd_calculation():
    # 30°C and 50% RH
    vpd = calculate_vpd(30.0, 50.0)
    vp_sat = calculate_saturation_vapor_pressure(30.0)
    expected = vp_sat * 0.5
    assert math.isclose(vpd, round(expected, 3), rel_tol=1e-2)

    # 100% RH should have ~0 VPD
    assert calculate_vpd(25.0, 100.0) == 0.0


def test_ambient_simulation_bounds():
    for hub in ["meru", "tharaka_nithi", "eldoret"]:
        for hour in [0.0, 6.0, 14.0, 20.0]:
            temp, rh = simulate_ambient(hub, hour)
            assert 10.0 <= temp <= 45.0
            assert 15.0 <= rh <= 95.0


def test_dryer_simulation_solar_boost():
    # At midday (13:00), dryer temp should exceed ambient temp due to solar greenhouse effect
    amb_temp = 25.0
    amb_rh = 50.0
    dryer_t, dryer_rh, vpd = simulate_dryer("meru", amb_temp, amb_rh, 13.0, 50.0)
    assert dryer_t > amb_temp
    assert vpd >= 0.0


def test_moisture_decay_kinetics():
    crop = "moringa"
    m_init = 75.0
    m_eq = CROP_PARAMETERS[crop]["equilibrium_moisture"]
    
    # After 1 hour, moisture should decrease
    m_1 = next_moisture_level(crop, m_init, 45.0, 2.0, 40.0, 1.0)
    assert m_1 < m_init
    assert m_1 >= m_eq

    # Decay cannot drop below equilibrium moisture
    m_late = next_moisture_level(crop, m_eq, 50.0, 3.0, 40.0, 5.0)
    assert m_late == m_eq


def test_simulator_client_logic(monkeypatch):
    sim = TelemetrySimulator("http://localhost:8000")
    
    # Mock login
    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json = json_data
            self.text = "Mock response"
        def json(self):
            return self._json

    def mock_post(url, **kwargs):
        if "/api/v1/auth/login" in url:
            return MockResponse(200, {"access_token": "fake_token", "token_type": "bearer"})
        if "/api/v1/readings/" in url:
            return MockResponse(201, {"id": "reading-123"})
        if "/api/v1/batches/" in url:
            return MockResponse(201, {"id": "batch-123", "hub_id": "hub-1"})
        return MockResponse(404, {})

    def mock_get(url, **kwargs):
        if "/api/v1/hubs/" in url:
            return MockResponse(200, [
                {"id": "hub-1", "name": "Meru Hub", "location": "meru"},
                {"id": "hub-2", "name": "Tharaka Nithi Hub", "location": "tharaka_nithi"},
                {"id": "hub-3", "name": "Eldoret Hub", "location": "eldoret"}
            ])
        if "/api/v1/batches/" in url:
            return MockResponse(200, [
                {
                    "id": "batch-1",
                    "hub_id": "hub-1",
                    "crop_type": "moringa",
                    "initial_weight_kg": 40.0,
                    "target_moisture_pct": 10.0,
                    "status": "active"
                }
            ])
        return MockResponse(404, {})

    monkeypatch.setattr(sim.client, "post", mock_post)
    monkeypatch.setattr(sim.client, "get", mock_get)

    # Test login
    assert sim.login() is True
    assert sim.token == "fake_token"

    # Test hub load
    sim.load_hubs()
    assert "meru" in sim.hubs_cache

    # Test batch sync
    batches = sim.sync_active_batches()
    assert len(batches) == 1
    assert "batch-1" in sim.batch_state
    assert sim.batch_state["batch-1"]["crop_type"] == "moringa"

    # Test simulation step
    sim.step_simulation()
    assert sim.batch_state["batch-1"]["current_moisture"] < 78.0


def test_default_credentials_match_seed_operator():
    """Verify default credentials match the seeded Operator account in seed.py."""
    assert SIMULATOR_USERNAME == "operator_meru"
    assert SIMULATOR_PASSWORD == "operatorpassword123"

    sim = TelemetrySimulator("http://localhost:8000")
    assert sim.username == "operator_meru"
    assert sim.password == "operatorpassword123"


def test_default_credentials_do_not_contain_forbidden_role_literal():
    """Verify default credentials do not contain forbidden role abbreviation."""
    forbidden = "".join(["a", "d", "m", "i", "n"])
    assert forbidden not in SIMULATOR_USERNAME.lower()
    assert forbidden not in SIMULATOR_PASSWORD.lower()

    sim = TelemetrySimulator("http://localhost:8000")
    assert forbidden not in sim.username.lower()
    assert forbidden not in sim.password.lower()


def test_environment_variable_overrides(monkeypatch):
    """Verify SIMULATOR_USERNAME and SIMULATOR_PASSWORD environment variables override defaults."""
    monkeypatch.setenv("SIMULATOR_USERNAME", "custom_operator")
    monkeypatch.setenv("SIMULATOR_PASSWORD", "custom_secret_123")

    sim = TelemetrySimulator("http://localhost:8000")
    assert sim.username == "custom_operator"
    assert sim.password == "custom_secret_123"


def test_explicit_init_credentials_override():
    """Verify constructor arguments override module/env defaults."""
    sim = TelemetrySimulator(
        "http://localhost:8000",
        username="explicit_op",
        password="explicit_pass"
    )
    assert sim.username == "explicit_op"
    assert sim.password == "explicit_pass"


def test_login_passes_expected_credentials_in_payload(monkeypatch):
    """Verify login() sends the configured credentials in the POST request form-data."""
    posted_data = {}
    forbidden = "".join(["a", "d", "m", "i", "n"])

    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json = json_data
            self.text = "Mock response"

        def json(self):
            return self._json

    def mock_post(url, **kwargs):
        if "/api/v1/auth/login" in url:
            posted_data.update(kwargs.get("data", {}))
            return MockResponse(200, {"access_token": "token-test", "token_type": "bearer"})
        return MockResponse(404, {})

    sim = TelemetrySimulator(
        "http://localhost:8000",
        username="operator_meru",
        password="operatorpassword123"
    )
    monkeypatch.setattr(sim.client, "post", mock_post)

    assert sim.login() is True
    assert posted_data.get("username") == "operator_meru"
    assert posted_data.get("password") == "operatorpassword123"
    assert sim.token == "token-test"
    assert forbidden not in posted_data.get("username", "").lower()
    assert forbidden not in posted_data.get("password", "").lower()


def test_simulator_halts_telemetry_when_target_moisture_reached(monkeypatch, caplog):
    """
    Test Ticket 07:
    1. A batch seeded at moisture just above target with fast decay emits exactly one reading (the threshold crossing).
    2. Further telemetry ticks for that batch are halted; no further readings emitted.
    3. The batch remains in simulator batch_state (dormant, not removed automatically).
    4. Other active batches continue receiving telemetry unaffected.
    5. The log message uses domain vocabulary: 'Operator', 'Advisory', avoiding 'user' or 'notification'.
    """
    import logging
    caplog.set_level(logging.INFO)
    sim = TelemetrySimulator("http://localhost:8000")

    posted_readings = []

    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json = json_data
            self.text = "Mock response"

        def json(self):
            return self._json

    # Two active batches:
    # - batch-target: moringa at 10.1% (target 10.0%) -> 1 tick drops below 10.0%
    # - batch-active: hibiscus at 50.0% (target 10.0%) -> remains active
    batches_data = [
        {
            "id": "batch-target-01",
            "hub_id": "hub-1",
            "crop_type": "moringa",
            "initial_weight_kg": 40.0,
            "target_moisture_pct": 10.0,
            "current_moisture": 10.1,
            "status": "active"
        },
        {
            "id": "batch-active-02",
            "hub_id": "hub-2",
            "crop_type": "hibiscus",
            "initial_weight_kg": 35.0,
            "target_moisture_pct": 10.0,
            "current_moisture": 50.0,
            "status": "active"
        }
    ]

    def mock_get(url, **kwargs):
        if "/api/v1/hubs/" in url:
            return MockResponse(200, [
                {"id": "hub-1", "name": "Meru Hub", "location": "meru"},
                {"id": "hub-2", "name": "Tharaka Nithi Hub", "location": "tharaka_nithi"}
            ])
        if "/api/v1/batches/?status=active" in url:
            return MockResponse(200, batches_data)
        return MockResponse(404, {})

    def mock_post(url, **kwargs):
        if "/api/v1/readings/" in url:
            payload = kwargs.get("json", {})
            posted_readings.append(payload)
            return MockResponse(201, {"id": f"reading-{len(posted_readings)}"})
        return MockResponse(404, {})

    monkeypatch.setattr(sim.client, "get", mock_get)
    monkeypatch.setattr(sim.client, "post", mock_post)

    sim.load_hubs()
    sim.sync_active_batches()

    assert "batch-target-01" in sim.batch_state
    assert "batch-active-02" in sim.batch_state
    assert sim.batch_state["batch-target-01"]["current_moisture"] == 10.1
    assert sim.batch_state["batch-target-01"]["halted"] is False

    # Tick 1: Step simulation.
    sim.step_simulation()

    # Both batches post in tick 1
    t1_target = [r for r in posted_readings if r["batch_id"] == "batch-target-01"]
    t1_active = [r for r in posted_readings if r["batch_id"] == "batch-active-02"]
    assert len(t1_target) == 1
    assert len(t1_active) == 1
    assert t1_target[0]["current_moisture"] <= 10.0

    # batch-target-01 reached target and halted, but NOT removed from state
    assert "batch-target-01" in sim.batch_state
    assert sim.batch_state["batch-target-01"]["halted"] is True

    # Check domain vocabulary in log output
    assert "Operator" in caplog.text
    assert "Advisory" in caplog.text
    assert "notification" not in caplog.text.lower()

    # Tick 2: Step simulation again
    sim.step_simulation()

    # batch-target-01 must NOT receive any new reading; batch-active-02 must continue
    t2_target = [r for r in posted_readings if r["batch_id"] == "batch-target-01"]
    t2_active = [r for r in posted_readings if r["batch_id"] == "batch-active-02"]
    assert len(t2_target) == 1  # Still 1: halted!
    assert len(t2_active) == 2  # Active batch received 2nd reading

    # Tick 3: Step simulation again
    sim.step_simulation()
    t3_target = [r for r in posted_readings if r["batch_id"] == "batch-target-01"]
    t3_active = [r for r in posted_readings if r["batch_id"] == "batch-active-02"]
    assert len(t3_target) == 1  # Still 1: halted!
    assert len(t3_active) == 3  # Active batch received 3rd reading

    # Batch remains dormant in simulator state
    assert "batch-target-01" in sim.batch_state
    sim.sync_active_batches()
    assert "batch-target-01" in sim.batch_state
    assert sim.batch_state["batch-target-01"]["halted"] is True

    # Once Operator confirms removal, backend marks it completed
    batches_data.pop(0)  # Remove batch-target-01 from active backend batches
    sim.sync_active_batches()
    assert "batch-target-01" not in sim.batch_state


def test_simulator_initializes_halted_if_already_at_target(monkeypatch):
    """A batch synced whose initial moisture is already <= target initializes halted=True."""
    sim = TelemetrySimulator("http://localhost:8000")
    posted_readings = []

    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json = json_data
            self.text = "Mock response"

        def json(self):
            return self._json

    batches_data = [
        {
            "id": "batch-already-dry",
            "hub_id": "hub-1",
            "crop_type": "moringa",
            "initial_weight_kg": 40.0,
            "target_moisture_pct": 10.0,
            "current_moisture": 9.5,
            "status": "active"
        }
    ]

    def mock_get(url, **kwargs):
        if "/api/v1/hubs/" in url:
            return MockResponse(200, [{"id": "hub-1", "name": "Meru Hub", "location": "meru"}])
        if "/api/v1/batches/?status=active" in url:
            return MockResponse(200, batches_data)
        return MockResponse(404, {})

    def mock_post(url, **kwargs):
        if "/api/v1/readings/" in url:
            posted_readings.append(kwargs.get("json", {}))
            return MockResponse(201, {"id": "reading-1"})
        return MockResponse(404, {})

    monkeypatch.setattr(sim.client, "get", mock_get)
    monkeypatch.setattr(sim.client, "post", mock_post)

    sim.load_hubs()
    sim.sync_active_batches()

    assert sim.batch_state["batch-already-dry"]["halted"] is True
    assert sim.batch_state["batch-already-dry"]["current_moisture"] == 9.5

    sim.step_simulation()
    assert len(posted_readings) == 0


def test_sync_active_batches_filters_and_prunes_completed_batches(monkeypatch):
    """
    Regression test for batch completion pruning (Ticket 07):
    - When sync_active_batches() receives batches including completed ones:
      - Completed batches are NOT added to sim.batch_state.
      - An existing batch that transitions to status: 'completed' in the backend is deleted from sim.batch_state.
      - sim.step_simulation() emits zero readings for completed batches.
    """
    sim = TelemetrySimulator("http://localhost:8000")
    posted_readings = []
    requested_urls = []

    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json = json_data
            self.text = "Mock response"

        def json(self):
            return self._json

    batches_data = [
        {
            "id": "b-active-1",
            "hub_id": "hub-1",
            "crop_type": "moringa",
            "initial_weight_kg": 40.0,
            "target_moisture_pct": 10.0,
            "current_moisture": 30.0,
            "status": "active"
        },
        {
            "id": "b-completed-already",
            "hub_id": "hub-1",
            "crop_type": "moringa",
            "initial_weight_kg": 40.0,
            "target_moisture_pct": 10.0,
            "current_moisture": 9.5,
            "status": "completed"
        }
    ]

    def mock_get(url, **kwargs):
        requested_urls.append(url)
        if "/api/v1/hubs/" in url:
            return MockResponse(200, [{"id": "hub-1", "name": "Meru Hub", "location": "meru"}])
        if "/api/v1/batches/" in url:
            return MockResponse(200, batches_data)
        return MockResponse(404, {})

    def mock_post(url, **kwargs):
        if "/api/v1/readings/" in url:
            payload = kwargs.get("json", {})
            posted_readings.append(payload)
            return MockResponse(201, {"id": f"reading-{len(posted_readings)}"})
        return MockResponse(404, {})

    monkeypatch.setattr(sim.client, "get", mock_get)
    monkeypatch.setattr(sim.client, "post", mock_post)

    sim.load_hubs()

    # Initial sync: only b-active-1 should be in batch_state; b-completed-already should be filtered out
    active_returned = sim.sync_active_batches()
    assert any("status=active" in u and "status_filter=active" in u for u in requested_urls)
    assert len(active_returned) == 1
    assert active_returned[0]["id"] == "b-active-1"
    assert "b-active-1" in sim.batch_state
    assert "b-completed-already" not in sim.batch_state

    # Step simulation: 1 reading posted for b-active-1, 0 for b-completed-already
    sim.step_simulation()
    assert len(posted_readings) == 1
    assert posted_readings[0]["batch_id"] == "b-active-1"

    # Backend updates: b-active-1 transitions to completed
    batches_data[0]["status"] = "completed"

    # Next sync: b-active-1 must be pruned from batch_state
    active_after = sim.sync_active_batches()
    assert len(active_after) == 0
    assert "b-active-1" not in sim.batch_state
    assert len(sim.batch_state) == 0

    # Step simulation again: 0 readings emitted
    sim.step_simulation()
    assert len(posted_readings) == 1  # No new readings emitted


