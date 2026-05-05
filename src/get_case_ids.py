import os
import re
import requests
import pandas as pd

URL = "https://physionet.org/files/vitaldb-arrhythmia/1.0.0/Annotation_Files/"
OUTPUT_DIR = "data/vitaldb"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "case_ids.csv")

def get_case_ids():
    print(f"Fetching case IDs from {URL}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    
    # Find all occurrences of Annotation_file_<id>.csv
    # The file name format is Annotation_file_1001.csv
    matches = re.findall(r'Annotation_file_(\d+)\.csv', response.text)
    
    # Remove duplicates and sort
    case_ids = sorted(list(set(int(m) for m in matches)))
    
    print(f"Found {len(case_ids)} unique case IDs.")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    df = pd.DataFrame({'case_id': case_ids})
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved case IDs to {OUTPUT_FILE}")

if __name__ == "__main__":
    get_case_ids()
