import csv
import sys
import os
import statistics
from collections import Counter
from datetime import datetime

def load_sales_data(filepath):
    sales_data = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if not row: continue
                
                # Filter for 'B' records (Sales Data)
                if row[0] == 'B':
                    # Extract logic
                    # 0: RecordType
                    # ...
                    # 7: HouseNumber
                    # 8: StreetName
                    # 9: Suburb
                    # 10: Postcode
                    # 11: Area
                    # 13: ContractDate (YYYYMMDD)
                    # 15: PurchasePrice
                    # 18: Prop Type
                    
                    try:
                        record = {
                            'DistrictCode': row[1] if len(row) > 1 else '',
                            'Address': f"{row[7] if len(row) > 7 else ''} {row[8] if len(row) > 8 else ''}".strip(),
                            'Suburb': row[9] if len(row) > 9 else '',
                            'Postcode': row[10] if len(row) > 10 else '',
                            'Area': float(row[11]) if len(row) > 11 and row[11].replace('.','',1).isdigit() else 0.0,
                            'ContractDate': row[13] if len(row) > 13 else '',
                            'Price': int(row[15]) if len(row) > 15 and row[15].isdigit() else 0,
                            'Type': row[18] if len(row) > 18 else ''
                        }
                        sales_data.append(record)
                    except (ValueError, IndexError):
                        continue
                        
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

    return sales_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_sales_data.py <path_to_dat_file>")
        default_path = "data/2024/20240101/001_SALES_DATA_NNME_01012024.DAT"
        if os.path.exists(default_path):
            print(f"Using default path: {default_path}")
            filepath = default_path
        else:
            sys.exit(1)
    else:
        filepath = sys.argv[1]

    data = load_sales_data(filepath)
    
    if data:
        print(f"\n--- Loaded {len(data)} Sales Records ---")
        
        # Prices
        prices = [d['Price'] for d in data if d['Price'] > 0]
        if prices:
            print(f"\nPrice Statistics:")
            print(f"  Count: {len(prices)}")
            print(f"  Min:   ${min(prices):,}")
            print(f"  Max:   ${max(prices):,}")
            print(f"  Avg:   ${statistics.mean(prices):,.2f}")
            print(f"  Median:${statistics.median(prices):,.2f}")
        
        # Types
        types = [d['Type'] for d in data]
        print(f"\nProperty Type Counts:")
        for type_, count in Counter(types).most_common():
            print(f"  {type_}: {count}")

        # Suburbs
        suburbs = [d['Suburb'] for d in data]
        print(f"\nTop 5 Suburbs:")
        for sub, count in Counter(suburbs).most_common(5):
            print(f"  {sub}: {count}")
            
        print("\n--- Sample Record ---")
        print(data[0])
