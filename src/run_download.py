import argparse
import pandas as pd
from download_data import download_vitaldb_and_annotations

def main():
    parser = argparse.ArgumentParser(description="Download vitaldb data for a range of case IDs from a CSV.")
    parser.add_argument("csv_name", help="Path to the CSV file containing case IDs")
    parser.add_argument("start_line", type=int, help="Start index (0-indexed, corresponding to the first case ID to download)")
    parser.add_argument("end_line", type=int, help="End index (exclusive, corresponding to the stop index)")
    
    args = parser.parse_args()
    
    print(f"Reading {args.csv_name}...")
    try:
        df = pd.read_csv(args.csv_name)
    except FileNotFoundError:
        print(f"Error: File not found: {args.csv_name}")
        return
    
    if 'case_id' not in df.columns:
        print("Error: CSV must contain a 'case_id' column.")
        return
        
    total_cases = len(df)
    
    start_idx = max(0, args.start_line)
    end_idx = min(total_cases, args.end_line)
    
    if start_idx >= end_idx:
        print(f"Error: Invalid range. start_line ({start_idx}) must be less than end_line ({end_idx}).")
        return
        
    target_cases = df['case_id'].iloc[start_idx:end_idx].tolist()
    
    print(f"Targeting {len(target_cases)} cases (indices {start_idx} to {end_idx-1}).")
    download_vitaldb_and_annotations(target_cases)

if __name__ == "__main__":
    main()
