#!/usr/bin/env python3
"""
BT-SmartDry On-Demand Telemetry Burst Trigger CLI.
Used during live demonstrations or scripted tests to run a bounded number of ticks
without consuming continuous cloud compute quotas.
"""
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from simulator.main import run_simulator
except ImportError:
    from main import run_simulator


def main():
    parser = argparse.ArgumentParser(description="Run on-demand BT-SmartDry telemetry burst")
    parser.add_argument("--burst", type=int, default=5, help="Number of ticks to emit (default: 5)")
    parser.add_argument("--interval", type=float, default=2.0, help="Interval between ticks in seconds (default: 2.0)")
    args = parser.parse_args()

    print(f"[BT-SmartDry] Launching on-demand simulation burst: {args.burst} ticks @ {args.interval}s interval")
    run_simulator(burst=args.burst, interval=args.interval)


if __name__ == "__main__":
    main()

