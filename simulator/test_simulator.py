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
from simulator.main import TelemetrySimulator


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

