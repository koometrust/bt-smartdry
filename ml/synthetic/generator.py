"""
Synthetic dataset generator for BT-SmartDry.
Generates realistic batch trajectories and 5-minute sensor reading sequences
using solar greenhouse thermodynamic and thin-layer crop drying models.
"""

import math
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd

from ml.synthetic.physics import (
    HUB_CLIMATES,
    CROP_PARAMETERS,
    simulate_ambient_conditions,
    simulate_dryer_conditions,
    compute_drying_rate,
)

CROPS = ["moringa", "prunus", "hibiscus"]
HUBS = ["meru", "tharaka_nithi", "eldoret"]

# Max safe dryer temperatures aligned with reading_service.py anomaly threshold (60°C)
CROP_MAX_SAFE_TEMP = {
    "moringa": 61.0,
    "hibiscus": 60.0,
    "prunus": 64.0,
}


def generate_batch_trajectory(
    batch_idx: int,
    crop_type: str,
    hub_location: str,
    batch_weight_kg: float,
    start_dt: datetime,
    target_moisture_pct: float,
    rng: np.random.Generator,
    quality_profile: str = "export",  # "export", "standard", "downgraded"
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Simulate one batch trajectory with 5-minute interval readings (50 to 150 readings).
    The physical conditions and drying speed reflect the quality profile.
    """
    crop_info = CROP_PARAMETERS[crop_type]
    batch_id = str(uuid.uuid4())
    safe_max_temp = CROP_MAX_SAFE_TEMP[crop_type]
    
    # Initial moisture
    m_init = float(rng.normal(crop_info["initial_moisture_mean"], crop_info["initial_moisture_std"]))
    m_init = max(60.0, min(88.0, round(m_init, 2)))
    m_eq = crop_info["equilibrium_moisture"]
    step_hours = 5.0 / 60.0  # 5 minutes
    
    # Trajectory atmospheric biases according to quality profile
    # Export: ideal drying weather (moderate warm temp, good VPD 1.8-3.5 kPa, excellent airflow)
    # Standard: borderline weather (cooler or muggier, VPD 0.9-1.8 kPa, slightly slower drying)
    # Downgraded: severe weather (heatwave overheating, or high humidity stalling drying, or severe over-dry)
    if quality_profile == "export":
        temp_bias = float(rng.uniform(-0.5, 2.0))
        rh_bias = float(rng.uniform(-6.0, 2.0))
        stop_offset = float(rng.uniform(-0.6, 0.6))
        anomaly_mode = None
    elif quality_profile == "standard":
        temp_bias = float(rng.uniform(-3.5, 0.0))
        rh_bias = float(rng.uniform(6.0, 16.0))
        stop_offset = float(rng.choice([-1.5, 1.5]) + rng.uniform(-0.4, 0.4))
        anomaly_mode = None
    else:  # downgraded
        sub_type = str(rng.choice(["overheating", "humid_stalled", "over_dried"]))
        if sub_type == "overheating":
            temp_bias = float(rng.uniform(7.0, 12.0))
            rh_bias = float(rng.uniform(-14.0, -6.0))
            stop_offset = float(rng.uniform(-1.0, 1.0))
            anomaly_mode = "overheating"
        elif sub_type == "humid_stalled":
            temp_bias = float(rng.uniform(-6.0, -3.0))
            rh_bias = float(rng.uniform(18.0, 28.0))
            stop_offset = float(rng.uniform(2.8, 6.0))
            anomaly_mode = "stalled"
        else:  # over_dried
            temp_bias = float(rng.uniform(1.0, 4.0))
            rh_bias = float(rng.uniform(-8.0, 0.0))
            stop_offset = float(rng.uniform(-4.5, -2.8))
            anomaly_mode = "over_dried"

    stop_moisture = max(m_eq + 0.5, target_moisture_pct + stop_offset)
    
    current_m = m_init
    current_dt = start_dt
    step_records = []
    max_steps = 150
    t_target = None
    max_temp_encountered = 0.0

    for step in range(max_steps):
        elapsed_hours = round(step * step_hours, 4)
        hour_of_day = (current_dt.hour + current_dt.minute / 60.0) % 24.0
        
        # 1. Ambient weather
        amb_temp, amb_rh = simulate_ambient_conditions(hub_location, hour_of_day, rng)
        amb_temp = max(10.0, min(45.0, round(amb_temp + temp_bias * 0.3, 2)))
        amb_rh = max(15.0, min(95.0, round(amb_rh + rh_bias * 0.4, 2)))
        
        # 2. Dryer internal conditions
        dryer_temp, dryer_rh, dryer_vpd = simulate_dryer_conditions(
            hub_location, amb_temp, amb_rh, hour_of_day, current_m, rng
        )
        dryer_temp = max(15.0, min(68.0, round(dryer_temp + temp_bias, 2)))
        dryer_rh = max(8.0, min(96.0, round(dryer_rh + rh_bias, 2)))
        dryer_vpd = max(0.1, round(dryer_vpd * (1.0 + temp_bias * 0.04), 3))
        
        if dryer_temp > max_temp_encountered:
            max_temp_encountered = dryer_temp
            
        # Track when target moisture is physically achieved
        if current_m <= target_moisture_pct and t_target is None:
            t_target = elapsed_hours
            
        step_records.append({
            "batch_id": batch_id,
            "timestamp": current_dt.isoformat(),
            "elapsed_hours": elapsed_hours,
            "temperature": dryer_temp,
            "humidity": dryer_rh,
            "vpd": dryer_vpd,
            "current_moisture": round(current_m, 2),
            "ambient_temperature": amb_temp,
            "ambient_humidity": amb_rh,
            "step_index": step,
        })
        
        # 3. Moisture decay step
        k = compute_drying_rate(crop_type, dryer_temp, dryer_vpd, batch_weight_kg)
        if anomaly_mode == "stalled":
            k *= 0.65  # High humidity severely suppresses evaporation
            
        decay = math.exp(-k * step_hours)
        next_m = m_eq + (current_m - m_eq) * decay + float(rng.normal(0.0, 0.015))
        next_m = min(current_m, max(m_eq + 0.2, next_m))
        current_m = next_m
        current_dt += timedelta(minutes=5)
        
        # Batch stop condition: minimum 50 readings (per context.md ~50-150 readings)
        if step >= 50 and current_m <= stop_moisture:
            break

    # If target wasn't reached, project based on last k
    if t_target is None:
        last_m = step_records[-1]["current_moisture"]
        if last_m > target_moisture_pct:
            needed_hours = math.log((last_m - m_eq) / max(0.1, (target_moisture_pct - m_eq))) / max(0.05, k)
            t_target = round(step_records[-1]["elapsed_hours"] + needed_hours, 3)
        else:
            t_target = step_records[-1]["elapsed_hours"]

    total_readings = len(step_records)
    final_moisture = step_records[-1]["current_moisture"]
    total_duration_hours = round(total_readings * step_hours, 3)
    moisture_diff = final_moisture - target_moisture_pct
    
    crop_optimal_duration = {
        "moringa": 9.5,
        "hibiscus": 10.5,
        "prunus": 12.0,
    }
    opt_dur = crop_optimal_duration[crop_type]

    # Exact rules evaluation from context.md:
    # "final moisture in optimal range + drying time within bounds -> Export;
    #  borderline -> Standard; outside (too wet or too dry) -> Downgraded. Over-drying penalised."
    if max_temp_encountered >= safe_max_temp:
        actual_grade = "downgraded"  # Overheating / nutrient scorch
    elif -1.0 <= moisture_diff <= 1.0 and total_duration_hours <= opt_dur:
        actual_grade = "export"
    elif -2.5 <= moisture_diff <= 2.5 and total_duration_hours <= (opt_dur + 1.5):
        actual_grade = "standard"
    else:
        actual_grade = "downgraded"  # Over-dried, under-dried, or delayed

    batch_record = {
        "batch_id": batch_id,
        "batch_idx": batch_idx,
        "crop_type": crop_type,
        "hub_location": hub_location,
        "batch_weight_kg": round(batch_weight_kg, 1),
        "target_moisture_pct": target_moisture_pct,
        "initial_moisture_pct": m_init,
        "final_moisture_pct": final_moisture,
        "total_readings": total_readings,
        "duration_hours": total_duration_hours,
        "time_to_target_hours": round(t_target, 3),
        "quality_grade": actual_grade,
        "max_temperature": round(max_temp_encountered, 2),
        "start_time": start_dt.isoformat(),
        "end_time": (start_dt + timedelta(hours=total_duration_hours)).isoformat(),
    }
    
    # Backfill remaining_hours and quality_grade onto each reading snapshot
    for r in step_records:
        r["batch_weight"] = batch_record["batch_weight_kg"]
        r["crop_type"] = crop_type
        r["hub_location"] = hub_location
        r["target_moisture"] = target_moisture_pct
        r["remaining_hours"] = max(0.0, round(t_target - r["elapsed_hours"], 3))
        r["quality_grade"] = actual_grade

    return batch_record, step_records


def generate_synthetic_dataset(
    num_batches: int = 2000,
    random_seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic batches and snapshot readings across 3 hubs and 3 crops.
    Returns: (df_batches, df_snapshots)
    """
    rng = np.random.default_rng(random_seed)
    
    batches_data = []
    snapshots_data = []
    base_date = datetime(2026, 6, 1, 7, 30, tzinfo=timezone.utc)
    
    # Target distribution across quality profiles:
    # Export: ~45%, Standard: ~30%, Downgraded: ~25%
    profiles = ["export", "standard", "downgraded"]
    profile_probs = [0.45, 0.30, 0.25]
    
    for i in range(num_batches):
        crop = str(rng.choice(CROPS))
        hub = str(rng.choice(HUBS))
        weight = float(rng.uniform(15.0, 150.0))
        target_m = CROP_PARAMETERS[crop]["target_moisture"]
        
        day_offset = int(rng.integers(0, 90))
        hour_offset = float(rng.uniform(0.0, 2.5))
        batch_start = base_date + timedelta(days=day_offset, hours=hour_offset)
        
        prof = str(rng.choice(profiles, p=profile_probs))
        
        batch_rec, readings = generate_batch_trajectory(
            batch_idx=i,
            crop_type=crop,
            hub_location=hub,
            batch_weight_kg=weight,
            start_dt=batch_start,
            target_moisture_pct=target_m,
            rng=rng,
            quality_profile=prof,
        )
        
        batches_data.append(batch_rec)
        snapshots_data.extend(readings)
        
    df_batches = pd.DataFrame(batches_data)
    df_snapshots = pd.DataFrame(snapshots_data)
    
    return df_batches, df_snapshots
