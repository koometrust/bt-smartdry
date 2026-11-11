"""
CLI script to generate and export synthetic batch and sensor reading data.
"""

import os
import argparse
import time
from pathlib import Path
import pandas as pd

from ml.synthetic.generator import generate_synthetic_dataset


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic dataset for BT-SmartDry")
    parser.add_argument("--batches", type=int, default=2000, help="Number of batches to generate (default: 2000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--outdir", type=str, default="ml/data", help="Output directory for generated datasets")
    args = parser.parse_args()

    out_path = Path(args.outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    print(f"Generating synthetic dataset: {args.batches} batches (seed={args.seed})...")
    start_t = time.time()
    df_batches, df_snapshots = generate_synthetic_dataset(num_batches=args.batches, random_seed=args.seed)
    gen_time = time.time() - start_t
    print(f"Generated {len(df_batches)} batches and {len(df_snapshots)} reading snapshots in {gen_time:.2f}s.")

    # Save batches
    batches_file = out_path / "batches.csv"
    df_batches.to_csv(batches_file, index=False)
    print(f"Saved batches to {batches_file}")

    # Save snapshots
    snapshots_csv = out_path / "training_snapshots.csv.gz"
    df_snapshots.to_csv(snapshots_csv, index=False, compression="gzip")
    print(f"Saved snapshots to {snapshots_csv} ({snapshots_csv.stat().st_size / (1024*1024):.2f} MB)")

    # Print summary statistics
    print("\n--- Batch Quality Grade Distribution ---")
    print(df_batches["quality_grade"].value_counts(normalize=True).round(3) * 100)

    print("\n--- Batches Per Hub ---")
    print(df_batches["hub_location"].value_counts())

    print("\n--- Batches Per Crop ---")
    print(df_batches["crop_type"].value_counts())

    print("\n--- Snapshot Duration and Readings Summary ---")
    print(df_batches[["total_readings", "duration_hours", "initial_moisture_pct", "final_moisture_pct"]].describe().round(2))


if __name__ == "__main__":
    main()

