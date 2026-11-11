import pytest
import math
import numpy as np

from ml.synthetic.physics import (
    calculate_saturation_vapor_pressure,
    calculate_vpd,
    simulate_ambient_conditions,
    simulate_dryer_conditions,
    compute_drying_rate,
    HUB_CLIMATES,
    CROP_PARAMETERS,
)


def test_saturation_vapor_pressure():
    # At 0°C, VP_sat ~ 0.611 kPa
    vp_0 = calculate_saturation_vapor_pressure(0.0)
    assert math.isclose(vp_0, 0.61078, rel_tol=1e-3)

    # At 25°C, VP_sat ~ 3.17 kPa
    vp_25 = calculate_saturation_vapor_pressure(25.0)
    assert 3.10 <= vp_25 <= 3.25

    # At 50°C, VP_sat ~ 12.3 kPa
    vp_50 = calculate_saturation_vapor_pressure(50.0)
    assert 12.0 <= vp_50 <= 12.6


def test_vpd_calculation():
    # At 100% RH, VPD must be 0
    vpd_100 = calculate_vpd(30.0, 100.0)
    assert vpd_100 == 0.0

    # At 50% RH at 30°C, VPD should be half of VP_sat(30°C) ~ 4.24 / 2 = 2.12 kPa
    vpd_50 = calculate_vpd(30.0, 50.0)
    assert 2.0 <= vpd_50 <= 2.25

    # VPD cannot be negative even if RH > 100%
    vpd_over = calculate_vpd(25.0, 105.0)
    assert vpd_over == 0.0


def test_ambient_weather_diurnal_cycle():
    rng = np.random.default_rng(123)
    for hub in ["meru", "tharaka_nithi", "eldoret"]:
        # Night / early morning (05:00) should be cooler and higher humidity
        temp_night, rh_night = simulate_ambient_conditions(hub, 5.0, rng)
        # Mid-afternoon (14:00) should be warmer and lower humidity
        temp_day, rh_day = simulate_ambient_conditions(hub, 14.0, rng)

        assert temp_day > temp_night
        assert rh_day < rh_night
        assert 10.0 <= temp_night <= 45.0
        assert 15.0 <= rh_day <= 95.0


def test_dryer_greenhouse_heating():
    rng = np.random.default_rng(42)
    # At noon (12:00), solar greenhouse should raise dryer temperature above ambient
    amb_temp = 25.0
    amb_rh = 50.0
    dryer_temp, dryer_rh, dryer_vpd = simulate_dryer_conditions(
        hub="meru",
        amb_temp=amb_temp,
        amb_rh=amb_rh,
        hour_of_day=12.0,
        current_moisture=40.0,
        rng=rng,
    )
    assert dryer_temp > amb_temp
    assert dryer_vpd > 0.5


def test_drying_rate_sensitivity():
    # Higher temperature must increase drying rate
    k_cool = compute_drying_rate("moringa", dryer_temp=30.0, dryer_vpd=2.0, batch_weight_kg=50.0)
    k_hot = compute_drying_rate("moringa", dryer_temp=50.0, dryer_vpd=2.0, batch_weight_kg=50.0)
    assert k_hot > k_cool

    # Higher VPD must increase drying rate
    k_low_vpd = compute_drying_rate("moringa", dryer_temp=40.0, dryer_vpd=0.5, batch_weight_kg=50.0)
    k_high_vpd = compute_drying_rate("moringa", dryer_temp=40.0, dryer_vpd=3.0, batch_weight_kg=50.0)
    assert k_high_vpd > k_low_vpd

    # Higher batch weight (thicker bed) must slightly reduce drying rate
    k_light = compute_drying_rate("moringa", dryer_temp=40.0, dryer_vpd=2.0, batch_weight_kg=20.0)
    k_heavy = compute_drying_rate("moringa", dryer_temp=40.0, dryer_vpd=2.0, batch_weight_kg=120.0)
    assert k_light > k_heavy

