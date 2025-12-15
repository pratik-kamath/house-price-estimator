
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
INPUT_FILE = os.path.join(DATA_DIR, 'sales_history.parquet')
OUTPUT_FILE = os.path.join(DATA_DIR, 'training_data.parquet')

def main():
    print(f"Loading data from {INPUT_FILE}...")
    if not os.path.exists(INPUT_FILE):
        print("Input file not found. Please run process_data.py first.")
        return

    df = pd.read_parquet(INPUT_FILE)
    original_len = len(df)
    print(f"Original Records: {original_len:,}")

    # 1. Filter Years (2018 - 2024)
    print("Filtering Years (2018-2024)...")
    df = df[(df['Year'] >= 2018) & (df['Year'] <= 2024)]
    print(f" -> Remaining: {len(df):,} ({len(df)/original_len:.1%})")

    # 2. Filter Property Types
    # Check exact strings: likely 'RESIDENCE', 'STRATA UNIT'
    # Let's verify what's in the data or just use str.contains
    print("Filtering Property Types (Residence / Strata Unit)...")
    valid_types = ['RESIDENCE', 'STRATA UNIT']
    df = df[df['PropertyType'].isin(valid_types)]
    print(f" -> Remaining: {len(df):,} ({len(df)/original_len:.1%})")

    # 3. Filter Price Outliers ($200k - $10M)
    print("Filtering Price Outliers ($200k - $10M)...")
    df = df[(df['PurchasePrice'] >= 200000) & (df['PurchasePrice'] <= 10000000)]
    print(f" -> Remaining: {len(df):,} ({len(df)/original_len:.1%})")
    
    # 4. Drop Duplicates (if any)
    df = df.drop_duplicates(subset=['PropertyID', 'ContractDate', 'PurchasePrice'])
    print(f"Final Count after dedup: {len(df):,}")

    # Save
    print(f"Saving to {OUTPUT_FILE}...")
    df.to_parquet(OUTPUT_FILE, index=False)
    print("Clean data saved.")

if __name__ == "__main__":
    main()
