#!/usr/bin/env python3
"""
Build script to convert hERG cardiotoxicity data to Parquet format.
Contains hERG channel blocker/non-blocker classifications with SMILES.
Sources: CardioTox, hERG-QSAR (ChEMBL-derived)
"""

import os
from pathlib import Path
import pandas as pd

def make_unique_columns(df):
    """Make column names unique by appending suffix for duplicates."""
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [
            f"{dup}_{i}" if i != 0 else dup
            for i in range(sum(cols == dup))
        ]
    df.columns = cols
    return df

def main():
    download_path = Path("download")
    brick_path = Path("brick")
    brick_path.mkdir(exist_ok=True)

    all_data = []

    # Process hERG-QSAR datasets
    for csv_name in ["Training_Set.csv", "Validation_Set.csv", "External_set.csv"]:
        csv_file = download_path / csv_name
        if csv_file.exists():
            print(f"Processing {csv_file}...")
            try:
                df = pd.read_csv(csv_file, low_memory=False)
                df.columns = [str(c).strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
                df['source'] = 'hERG-QSAR'
                df['dataset'] = csv_name.replace('.csv', '')
                all_data.append(df)
                print(f"  - Loaded {len(df)} records")
            except Exception as e:
                print(f"  - Error: {e}")

    # Process CardioTox datasets
    cardiotox_files = list(download_path.rglob("*.csv"))
    for csv_file in cardiotox_files:
        if csv_file.name not in ["Training_Set.csv", "Validation_Set.csv", "External_set.csv"]:
            print(f"Processing {csv_file}...")
            try:
                df = pd.read_csv(csv_file, low_memory=False)
                df.columns = [str(c).strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
                df['source'] = 'CardioTox'
                df['dataset'] = csv_file.stem
                all_data.append(df)
                print(f"  - Loaded {len(df)} records")
            except Exception as e:
                print(f"  - Error: {e}")

    # Combine all datasets
    if all_data:
        # Save individual datasets
        for i, df in enumerate(all_data):
            source = df['source'].iloc[0] if 'source' in df.columns else f'dataset_{i}'
            dataset = df['dataset'].iloc[0] if 'dataset' in df.columns else f'part_{i}'
            output_name = f"{source.lower().replace(' ', '_')}_{dataset.lower()}"
            output_file = brick_path / f"{output_name}.parquet"
            # Make column names unique before saving
            df = make_unique_columns(df)
            df.to_parquet(output_file, index=False)
            print(f"  - Saved {len(df)} records to {output_file}")

        # Create combined dataset (only use key columns to avoid schema conflicts)
        key_cols = ['smiles', 'activity', 'source', 'dataset']
        combined_data = []
        for df in all_data:
            df_cols = [c for c in key_cols if c in df.columns]
            if 'smiles' in df.columns:
                combined_data.append(df[df_cols].copy())

        if combined_data:
            combined = pd.concat(combined_data, ignore_index=True)
            combined_file = brick_path / "herg_combined.parquet"
            combined.to_parquet(combined_file, index=False)
            print(f"\nCombined dataset: {len(combined)} total records")

    # Print summary
    print("\nOutput files:")
    for f in brick_path.glob("*.parquet"):
        df = pd.read_parquet(f)
        print(f"  - {f.name}: {len(df)} rows, {len(df.columns)} columns")

if __name__ == "__main__":
    main()
