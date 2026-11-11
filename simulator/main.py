"""
BT-SmartDry IoT Telemetry Simulator.
Continuously publishes realistic sensor telemetry for multi-hub concurrent batches.
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import httpx

from physics import (
    simulate_ambient,
    simulate_dryer,
    next_moisture_level,
    CROP_PARAMETERS
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("simulator")

BACKEND_URL = os.getenv("SIMULATOR_BACKEND_URL", "http://localhost:8000")
INTERVAL_SECONDS = float(os.getenv("SIMULATOR_INTERVAL_SECONDS", "5.0"))
# Virtual speedup: each tick represents dt_hours of drying physics (default 0.5 hours per tick)
VIRTUAL_HOURS_PER_TICK = float(os.getenv("SIMULATOR_VIRTUAL_HOURS_PER_TICK", "0.35"))

DEMO_PROFILES = [
    {
        "hub_name": "Meru Hub",
        "crop_type": "moringa",
        "weight_kg": 45.0,
        "target_moisture": 10.0
    },
    {
        "hub_name": "Tharaka Nithi Hub",
        "crop_type": "hibiscus",
        "weight_kg": 35.0,
        "target_moisture": 10.0
    },
    {
        "hub_name": "Eldoret Hub",
        "crop_type": "prunus",
        "weight_kg": 60.0,
        "target_moisture": 12.0
    }
]

running = True


def handle_shutdown(signum, frame):
    global running
    logger.info("Shutdown signal received. Exiting simulator loop...")
    running = False


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


class TelemetrySimulator:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url.rstrip("/")
        self.client = httpx.Client(base_url=self.backend_url, timeout=10.0)
        self.token: Optional[str] = None
        self.hubs_cache: Dict[str, dict] = {}
        # batch_id -> {current_moisture, elapsed_hours, crop_type, hub_location, weight_kg, target_moisture}
        self.batch_state: Dict[str, dict] = {}

    def login(self) -> bool:
        """Authenticate using default admin credentials to manage multi-hub batches."""
        try:
            res = self.client.post(
                "/api/v1/auth/login",
                data={"username": "admin", "password": "adminpassword123"}
            )
            if res.status_code == 200:
                self.token = res.json()["access_token"]
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                logger.info("Simulator authenticated successfully as admin.")
                return True
            else:
                logger.error(f"Authentication failed: {res.status_code} - {res.text}")
                return False
        except Exception as e:
            logger.warning(f"Could not connect to backend at {self.backend_url}: {e}")
            return False

    def load_hubs(self) -> None:
        """Fetch and cache available hubs."""
        try:
            res = self.client.get("/api/v1/hubs/")
            if res.status_code == 200:
                hubs = res.json()
                for h in hubs:
                    self.hubs_cache[h["name"].lower()] = h
                    self.hubs_cache[h["location"].lower()] = h
                    self.hubs_cache[str(h["id"])] = h
                logger.info(f"Loaded {len(hubs)} hubs into cache.")
        except Exception as e:
            logger.warning(f"Failed to fetch hubs: {e}")

    def sync_active_batches(self) -> List[dict]:
        """Fetch all currently active batches from backend."""
        try:
            res = self.client.get("/api/v1/batches/?status=active")
            if res.status_code == 200:
                batches = res.json()
                # Update local tracking
                active_ids = set()
                for b in batches:
                    b_id = str(b["id"])
                    active_ids.add(b_id)
                    if b_id not in self.batch_state:
                        hub_info = self.hubs_cache.get(str(b["hub_id"]), {})
                        hub_loc = hub_info.get("location", "meru").lower()
                        crop = b["crop_type"].lower()
                        # Initial moisture default from kinetics if none yet recorded
                        init_m = CROP_PARAMETERS.get(crop, {}).get("initial_moisture", 75.0)
                        self.batch_state[b_id] = {
                            "crop_type": crop,
                            "hub_location": hub_loc,
                            "weight_kg": float(b["initial_weight_kg"]),
                            "target_moisture": float(b["target_moisture_pct"]),
                            "current_moisture": init_m,
                            "elapsed_hours": 0.0
                        }
                # Remove inactive from local state
                for b_id in list(self.batch_state.keys()):
                    if b_id not in active_ids:
                        del self.batch_state[b_id]
                return batches
            return []
        except Exception as e:
            logger.warning(f"Failed to sync batches: {e}")
            return []

    def ensure_demo_batches(self) -> None:
        """Ensure at least one batch per hub is actively drying."""
        active_batches = self.sync_active_batches()
        if len(active_batches) >= 3:
            return

        logger.info(f"Only {len(active_batches)} active batches found. Provisioning demo batches...")
        for profile in DEMO_PROFILES:
            hub = self.hubs_cache.get(profile["hub_name"].lower())
            if not hub:
                continue

            # Check if this hub already has an active batch
            hub_id = hub["id"]
            has_batch = any(b["hub_id"] == hub_id for b in active_batches)
            if not has_batch:
                payload = {
                    "hub_id": hub_id,
                    "crop_type": profile["crop_type"],
                    "initial_weight_kg": profile["weight_kg"],
                    "target_moisture_pct": profile["target_moisture"]
                }
                try:
                    res = self.client.post("/api/v1/batches/", json=payload)
                    if res.status_code == 201:
                        new_batch = res.json()
                        logger.info(
                            f"Created demo batch {new_batch['id']} for {profile['crop_type']} at {hub['name']}."
                        )
                except Exception as e:
                    logger.warning(f"Failed to create demo batch: {e}")

        # Refresh local state
        self.sync_active_batches()

    def step_simulation(self) -> None:
        """Advance physics and publish readings for all active batches."""
        now_dt = datetime.now(timezone.utc)
        current_hour_of_day = (now_dt.hour + now_dt.minute / 60.0) % 24.0

        for batch_id, state in list(self.batch_state.items()):
            hub_loc = state["hub_location"]
            crop = state["crop_type"]
            weight = state["weight_kg"]
            target_m = state["target_moisture"]
            curr_m = state["current_moisture"]

            # 1. Physics simulation step
            amb_temp, amb_rh = simulate_ambient(hub_loc, current_hour_of_day)
            dryer_temp, dryer_rh, dryer_vpd = simulate_dryer(
                hub_loc, amb_temp, amb_rh, current_hour_of_day, curr_m
            )
            
            # Step moisture forward
            new_m = next_moisture_level(
                crop, curr_m, dryer_temp, dryer_vpd, weight, VIRTUAL_HOURS_PER_TICK
            )
            state["current_moisture"] = new_m
            state["elapsed_hours"] += VIRTUAL_HOURS_PER_TICK

            # 2. Publish Reading to Backend API
            reading_payload = {
                "batch_id": batch_id,
                "temperature": dryer_temp,
                "humidity": dryer_rh,
                "vpd": dryer_vpd,
                "current_moisture": new_m,
                "ambient_temperature": amb_temp,
                "ambient_humidity": amb_rh,
                "timestamp": now_dt.isoformat()
            }

            try:
                r_res = self.client.post("/api/v1/readings/", json=reading_payload)
                if r_res.status_code == 201:
                    logger.info(
                        f"Reading posted -> Batch {batch_id[:8]} ({crop}@{hub_loc}): "
                        f"Moisture={new_m}% | Temp={dryer_temp}°C | RH={dryer_rh}% | VPD={dryer_vpd}kPa"
                    )
                else:
                    logger.warning(f"Failed reading post: {r_res.status_code} - {r_res.text}")
            except Exception as e:
                logger.error(f"Error posting reading for batch {batch_id}: {e}")

            # 3. If moisture target reached (or over-dried), complete batch
            if new_m <= target_m:
                logger.info(f"Batch {batch_id[:8]} reached target moisture {target_m}% (actual: {new_m}%). Completing batch...")
                try:
                    self.client.patch(f"/api/v1/batches/{batch_id}", json={"status": "completed"})
                    del self.batch_state[batch_id]
                except Exception as e:
                    logger.warning(f"Failed to complete batch {batch_id}: {e}")


def run_simulator():
    logger.info(f"Starting BT-SmartDry Telemetry Simulator (Target: {BACKEND_URL}, Interval: {INTERVAL_SECONDS}s)")
    sim = TelemetrySimulator(BACKEND_URL)

    # Initial connection loop
    while running and not sim.token:
        if sim.login():
            sim.load_hubs()
            sim.ensure_demo_batches()
            break
        logger.info("Waiting 3s to retry backend connection...")
        time.sleep(3.0)

    # Main telemetry streaming loop
    tick_counter = 0
    while running:
        try:
            # Periodically re-sync batches every 10 ticks
            if tick_counter % 10 == 0:
                sim.ensure_demo_batches()

            sim.step_simulation()
            tick_counter += 1
        except Exception as e:
            logger.error(f"Unexpected error in simulator cycle: {e}")

        time.sleep(INTERVAL_SECONDS)

    sim.client.close()
    logger.info("Simulator terminated cleanly.")


if __name__ == "__main__":
    run_simulator()

