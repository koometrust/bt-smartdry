"""
Thermodynamic and thin-layer drying physics for the BT-SmartDry IoT Simulator.
Pure Python implementation matching project domain definitions and kinetics.
"""

import math
import random
from typing import Tuple, Dict

# Hub climate parameters
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
        "initial_moisture": 78.0,
        "target_moisture": 10.0,
        "equilibrium_moisture": 6.5,
        "base_drying_rate": 0.22,
        "optimal_min": 9.0,
        "optimal_max": 11.0,
    },
    "hibiscus": {
        "initial_moisture": 82.0,
        "target_moisture": 10.0,
        "equilibrium_moisture": 6.0,
        "base_drying_rate": 0.17,
        "optimal_min": 9.0,
        "optimal_max": 11.0,
    },
    "prunus": {
        "initial_moisture": 70.0,
        "target_moisture": 12.0,
        "equilibrium_moisture": 7.0,
        "base_drying_rate": 0.12,
        "optimal_min": 11.0,
        "optimal_max": 13.0,
    },
}


def calculate_saturation_vapor_pressure(temp_c: float) -> float:
    """Calculate saturation vapor pressure in kPa via Tetens formula."""
    return 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))


def calculate_vpd(temp_c: float, rh_pct: float) -> float:
    """Calculate Vapor Pressure Deficit (VPD) in kPa."""
    vp_sat = calculate_saturation_vapor_pressure(temp_c)
    rh_frac = max(0.0, min(100.0, rh_pct)) / 100.0
    return max(0.0, round(vp_sat * (1.0 - rh_frac), 3))


def simulate_ambient(hub: str, hour_of_day: float) -> Tuple[float, float]:
    """Simulate ambient diurnal temperature and relative humidity for hub."""
    climate = HUB_CLIMATES.get(hub.lower(), HUB_CLIMATES["meru"])
    rad = (hour_of_day - 8.0) * math.pi / 12.0
    diurnal = math.sin(rad)
    
    noise_t = random.gauss(0.0, 0.4)
    amb_temp = climate["base_temp"] + (climate["temp_amp"] * diurnal) + noise_t
    amb_temp = max(10.0, min(45.0, round(amb_temp, 2)))
    
    noise_rh = random.gauss(0.0, 1.2)
    amb_rh = climate["base_rh"] - (climate["rh_amp"] * diurnal) + noise_rh
    amb_rh = max(15.0, min(95.0, round(amb_rh, 2)))
    
    return amb_temp, amb_rh


def simulate_dryer(
    hub: str,
    amb_temp: float,
    amb_rh: float,
    hour_of_day: float,
    current_moisture: float
) -> Tuple[float, float, float]:
    """Simulate solar collector greenhouse heating and internal humidity."""
    climate = HUB_CLIMATES.get(hub.lower(), HUB_CLIMATES["meru"])
    solar_boost = 0.0
    if 7.0 <= hour_of_day <= 18.0:
        sun_angle = (hour_of_day - 7.0) * math.pi / 11.0
        max_delta_t = 16.0 * climate["solar_factor"] + random.uniform(-1.5, 2.0)
        solar_boost = max_delta_t * math.sin(sun_angle)
        
    dryer_temp = amb_temp + solar_boost + random.gauss(0.0, 0.4)
    dryer_temp = max(15.0, min(65.0, round(dryer_temp, 2)))
    
    vp_amb = calculate_saturation_vapor_pressure(amb_temp) * (amb_rh / 100.0)
    vp_sat_dryer = calculate_saturation_vapor_pressure(dryer_temp)
    
    evap_vp = 0.08 * (current_moisture / 100.0) * (solar_boost / 15.0 if solar_boost > 0 else 0.05)
    dryer_vp = min(vp_sat_dryer * 0.95, vp_amb + evap_vp)
    
    dryer_rh = (dryer_vp / vp_sat_dryer) * 100.0 + random.gauss(0.0, 0.8)
    dryer_rh = max(10.0, min(92.0, round(dryer_rh, 2)))
    
    dryer_vpd = calculate_vpd(dryer_temp, dryer_rh)
    return dryer_temp, dryer_rh, dryer_vpd


def next_moisture_level(
    crop_type: str,
    current_moisture: float,
    dryer_temp: float,
    dryer_vpd: float,
    batch_weight_kg: float,
    dt_hours: float
) -> float:
    """
    Step moisture forward over dt_hours using thin-layer exponential kinetics:
    dM/dt = -k * (M - M_eq)
    """
    params = CROP_PARAMETERS.get(crop_type.lower(), CROP_PARAMETERS["moringa"])
    m_eq = params["equilibrium_moisture"]
    if current_moisture <= m_eq:
        return m_eq
        
    base_k = params["base_drying_rate"]
    temp_factor = math.exp(0.035 * (dryer_temp - 38.0))
    vpd_factor = 0.8 + 0.25 * min(dryer_vpd, 4.0)
    weight_factor = (50.0 / max(10.0, batch_weight_kg)) ** 0.18
    k = max(0.02, min(0.65, base_k * temp_factor * vpd_factor * weight_factor))
    
    # Exponential decay step
    decay = math.exp(-k * dt_hours)
    next_m = m_eq + (current_moisture - m_eq) * decay
    return max(m_eq, round(next_m, 2))

