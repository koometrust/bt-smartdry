"""
Psychrometric and thermodynamic physics functions for solar crop drying.
Includes saturation vapor pressure, vapor pressure deficit (VPD),
hub-specific ambient weather generation, and thin-layer moisture decay.
"""

import math
from typing import Tuple, Dict
import numpy as np


# Hub climate parameters: (baseline_temp, temp_amplitude, baseline_rh, rh_amplitude)
HUB_CLIMATES: Dict[str, Dict[str, float]] = {
    "meru": {
        "base_temp": 21.0,
        "temp_amp": 6.0,
        "base_rh": 66.0,
        "rh_amp": 18.0,
        "solar_factor": 1.05,
    },
    "tharaka_nithi": {
        "base_temp": 27.0,
        "temp_amp": 7.5,
        "base_rh": 48.0,
        "rh_amp": 16.0,
        "solar_factor": 1.15,
    },
    "eldoret": {
        "base_temp": 18.5,
        "temp_amp": 6.5,
        "base_rh": 62.0,
        "rh_amp": 20.0,
        "solar_factor": 1.0,
    },
}

# Crop drying kinetics parameters
CROP_PARAMETERS: Dict[str, Dict[str, float]] = {
    "moringa": {
        "initial_moisture_mean": 78.0,
        "initial_moisture_std": 3.0,
        "target_moisture": 10.0,
        "equilibrium_moisture": 6.5,
        "base_drying_rate": 0.22,  # Leaves dry relatively fast
        "optimal_min": 9.0,
        "optimal_max": 11.0,
    },
    "hibiscus": {
        "initial_moisture_mean": 82.0,
        "initial_moisture_std": 3.5,
        "target_moisture": 10.0,
        "equilibrium_moisture": 6.0,
        "base_drying_rate": 0.17,  # Calyces have fleshy tissue
        "optimal_min": 9.0,
        "optimal_max": 11.0,
    },
    "prunus": {
        "initial_moisture_mean": 70.0,
        "initial_moisture_std": 4.0,
        "target_moisture": 12.0,
        "equilibrium_moisture": 7.0,
        "base_drying_rate": 0.12,  # Dense woody bark/foliage
        "optimal_min": 11.0,
        "optimal_max": 13.0,
    },
}


def calculate_saturation_vapor_pressure(temp_c: float) -> float:
    """
    Calculate saturation vapor pressure (VP_sat) in kPa using Tetens equation.
    Formula: 0.61078 * exp((17.27 * T) / (T + 237.3))
    """
    return 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))


def calculate_vpd(temp_c: float, relative_humidity_pct: float) -> float:
    """
    Calculate Vapor Pressure Deficit (VPD) in kPa.
    VPD = VP_sat * (1 - RH / 100)
    """
    vp_sat = calculate_saturation_vapor_pressure(temp_c)
    rh_frac = max(0.0, min(100.0, relative_humidity_pct)) / 100.0
    vpd = vp_sat * (1.0 - rh_frac)
    return max(0.0, round(vpd, 3))


def simulate_ambient_conditions(
    hub: str,
    hour_of_day: float,
    rng: np.random.Generator
) -> Tuple[float, float]:
    """
    Simulate diurnal ambient temperature (°C) and relative humidity (%) for a given hub.
    Peak temperature around 14:00, minimum around 05:00.
    """
    climate = HUB_CLIMATES.get(hub.lower(), HUB_CLIMATES["meru"])
    
    # Phase shift: peak at 14:00 (14 - 8 = 6 -> cos phase or sin phase)
    # sin((hour - 8) * pi / 12) reaches max at hour 14
    rad = (hour_of_day - 8.0) * math.pi / 12.0
    diurnal_factor = math.sin(rad)
    
    # Temperature: base + amp * diurnal_factor + small noise
    temp_noise = float(rng.normal(0.0, 0.6))
    amb_temp = climate["base_temp"] + (climate["temp_amp"] * diurnal_factor) + temp_noise
    amb_temp = max(10.0, min(45.0, round(amb_temp, 2)))
    
    # Relative humidity: inverse diurnal cycle
    rh_noise = float(rng.normal(0.0, 1.5))
    amb_rh = climate["base_rh"] - (climate["rh_amp"] * diurnal_factor) + rh_noise
    amb_rh = max(15.0, min(95.0, round(amb_rh, 2)))
    
    return amb_temp, amb_rh


def simulate_dryer_conditions(
    hub: str,
    amb_temp: float,
    amb_rh: float,
    hour_of_day: float,
    current_moisture: float,
    rng: np.random.Generator
) -> Tuple[float, float, float]:
    """
    Simulate greenhouse solar heating effect inside the dryer.
    Returns: (dryer_temp, dryer_humidity, dryer_vpd)
    """
    climate = HUB_CLIMATES.get(hub.lower(), HUB_CLIMATES["meru"])
    solar_boost = 0.0
    
    # Solar collector active between 07:00 and 18:00
    if 7.0 <= hour_of_day <= 18.0:
        sun_angle = (hour_of_day - 7.0) * math.pi / 11.0
        max_delta_t = 16.0 * climate["solar_factor"] + float(rng.uniform(-2.0, 3.0))
        solar_boost = max_delta_t * math.sin(sun_angle)
    
    dryer_temp = amb_temp + solar_boost + float(rng.normal(0.0, 0.5))
    dryer_temp = max(15.0, min(65.0, round(dryer_temp, 2)))
    
    # Evaporating moisture and temperature rise determine internal RH
    vp_amb = calculate_saturation_vapor_pressure(amb_temp) * (amb_rh / 100.0)
    vp_sat_dryer = calculate_saturation_vapor_pressure(dryer_temp)
    
    # Crop evaporation adds partial vapor pressure
    evap_vp = 0.08 * (current_moisture / 100.0) * (solar_boost / 15.0 if solar_boost > 0 else 0.05)
    dryer_vp = min(vp_sat_dryer * 0.95, vp_amb + evap_vp)
    
    dryer_rh = (dryer_vp / vp_sat_dryer) * 100.0 + float(rng.normal(0.0, 1.0))
    dryer_rh = max(10.0, min(92.0, round(dryer_rh, 2)))
    
    dryer_vpd = calculate_vpd(dryer_temp, dryer_rh)
    
    return dryer_temp, dryer_rh, dryer_vpd


def compute_drying_rate(
    crop_type: str,
    dryer_temp: float,
    dryer_vpd: float,
    batch_weight_kg: float
) -> float:
    """
    Compute instantaneous drying rate constant k (hr^-1) based on
    crop kinetics, temperature, VPD, and bed depth (weight).
    """
    crop_params = CROP_PARAMETERS.get(crop_type.lower(), CROP_PARAMETERS["moringa"])
    base_k = crop_params["base_drying_rate"]
    
    # Arrhenius temperature factor centered at 38°C
    temp_factor = math.exp(0.035 * (dryer_temp - 38.0))
    
    # VPD driving force factor
    vpd_factor = 0.8 + 0.25 * min(dryer_vpd, 4.0)
    
    # Batch weight impedance (nominal 50kg, higher weight = slightly slower drying)
    weight_factor = (50.0 / max(10.0, batch_weight_kg)) ** 0.18
    
    k = base_k * temp_factor * vpd_factor * weight_factor
    return max(0.02, min(0.65, k))

