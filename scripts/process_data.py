
import os
import glob
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'sales_history.parquet')

def parse_dat_file(filepath):
    """
    Parses a single .DAT file and returns a list of dictionaries.
    """
    records = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                parts = line.split(';')
                if not parts or parts[0] != 'B':
                    continue
                
                # Extract fields based on known structure
                # 0: RecordType
                # 7: HouseNumber
                # 8: StreetName
                # 9: Suburb
                # 10: Postcode
                # 11: Area
                # 12: AreaUnit
                # 13: ContractDate (YYYYMMDD)
                # 15: PurchasePrice
                # 16: Zoning
                # 18: PropertyType

                try:
                    # Basic Validation
                    if len(parts) < 19:
                        continue
                        
                    contract_date_str = parts[13]
                    price_str = parts[15]
                    
                    if not contract_date_str or not price_str:
                        continue

                    record = {
                        'DistrictCode': parts[1],
                        'PropertyID': parts[2],
                        'ValuationNum': parts[3],
                        # Address Construction
                        'HouseNumber': parts[7].strip(),
                        'StreetName': parts[8].strip(),
                        'Suburb': parts[9].strip().upper(), # Normalize Suburb
                        'Postcode': parts[10].strip(),
                        'Area': parts[11].strip(),
                        'AreaUnit': parts[12].strip(),
                        'ContractDate': contract_date_str,
                        'PurchasePrice': price_str,
                        'Zoning': parts[16].strip(),
                        'PropertyType': parts[18].strip().upper(), # Normalize Type
                        # Source tracking
                        'SourceFile': os.path.basename(filepath)
                    }
                    records.append(record)
                except Exception:
                    continue
    except Exception as e:
        # print(f"Error reading {filepath}: {e}")
        pass
        
    return records

def process_chunk(files):
    """
    Process a list of files and return a DataFrame.
    """
    chunk_records = []
    for f in files:
        chunk_records.extend(parse_dat_file(f))
    return chunk_records

def main():
    print(f"Scanning for .DAT files in {DATA_DIR}...")
    all_files = glob.glob(os.path.join(DATA_DIR, '*.DAT'))
    total_files = len(all_files)
    print(f"Found {total_files} files.")
    
    if total_files == 0:
        print("No DAT files found. Exiting.")
        return

    # Split work for parallel processing
    # Adjust max_workers based on system, usually cpu_count is good
    # We chunk the files so we don't spawn too many tasks
    num_workers = os.cpu_count() or 4
    chunk_size = max(1, total_files // (num_workers * 4))
    
    file_chunks = [all_files[i:i + chunk_size] for i in range(0, total_files, chunk_size)]
    
    print(f"Processing in parellel with {num_workers} workers...")
    
    all_records = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(process_chunk, file_chunks), total=len(file_chunks)))
        
    for res in results:
        all_records.extend(res)
        
    print(f"Total raw records extracted: {len(all_records)}")
    
    if not all_records:
        print("No records extracted.")
        return

    print("Creating DataFrame...")
    df = pd.DataFrame(all_records)
    
    print("Preprocessing data...")
    # 1. Convert Types
    df['PurchasePrice'] = pd.to_numeric(df['PurchasePrice'], errors='coerce')
    df['Area'] = pd.to_numeric(df['Area'], errors='coerce')
    df['ContractDate'] = pd.to_datetime(df['ContractDate'], format='%Y%m%d', errors='coerce')
    
    # 2. Filter Valid Sales
    df = df.dropna(subset=['PurchasePrice', 'ContractDate'])
    df = df[df['PurchasePrice'] > 1000] # Remove placeholders like $1 sales
    
    # 3. Time Features
    df['Year'] = df['ContractDate'].dt.year
    df['Month'] = df['ContractDate'].dt.month
    df['Quarter'] = df['ContractDate'].dt.quarter
    
    # 4. Address Combine
    df['FullAddress'] = df['HouseNumber'] + ' ' + df['StreetName'] + ', ' + df['Suburb'] + ' ' + df['Postcode']
    df['FullAddress'] = df['FullAddress'].str.replace(r'\s+', ' ', regex=True).str.strip()

    print(f"Final dataset shape: {df.shape}")
    print(f"Saving to {OUTPUT_FILE}...")
    
    # Save to Parquet (requires pyarrow or fastparquet, usually installed with pandas in many envs, 
    # checking requirements.txt pyarrow is listed)
    df.to_parquet(OUTPUT_FILE, index=False)
    print("Done!")

if __name__ == "__main__":
    main()
