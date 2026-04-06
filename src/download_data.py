import os
import requests
import pandas as pd
import vitaldb
import io
import time

# Configuration
BASE_RAW_DIR = "data/vitaldb/raw"
WAVEFORM_DIR = os.path.join(BASE_RAW_DIR, "waveforms")
ANNOTATION_DIR = os.path.join(BASE_RAW_DIR, "annotations")

# URL for direct raw file access (bypasses the HTML preview/content wrapper)
PHYSIONET_FILES_URL = "https://physionet.org/files/vitaldb-arrhythmia/1.0.0/Annotation_Files/"

# Ensure directory structure exists
os.makedirs(WAVEFORM_DIR, exist_ok=True)
os.makedirs(ANNOTATION_DIR, exist_ok=True)

def download_vitaldb_and_annotations(case_ids):
    # Headers to mimic a browser to ensure PhysioNet serves the raw file
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for case_id in case_ids:
        print(f"\n--- Processing Case {case_id} ---")
        
        # 1. Download Waveform (.vital) from VitalDB API
        vital_path = os.path.join(WAVEFORM_DIR, f"{case_id}.vital")
        if not os.path.exists(vital_path):
            try:
                # We request ECG (II) and PPG (PLETH)
                vf = vitaldb.VitalFile(case_id, ['SNUADC/ECG_II', 'SNUADC/PLETH'])
                vf.to_vital(vital_path)
                print(f"  [✓] Waveform saved to {vital_path}")
            except Exception as e:
                print(f"  [!] VitalDB Error for {case_id}: {e}")
                # We continue to annotation even if waveform fails, or use 'continue' to skip
        else:
            print(f"  [-] Waveform {case_id}.vital already exists.")

        # 2. Download Raw Annotation (.csv) from PhysioNet Files Server
        ann_filename = f"Annotation_file_{case_id}.csv"
        ann_path = os.path.join(ANNOTATION_DIR, ann_filename)
        
        if not os.path.exists(ann_path):
            # Using /files/ and ?download=1 to get the Plain Text output directly
            download_url = f"{PHYSIONET_FILES_URL}{ann_filename}?download=1"
            
            try:
                response = requests.get(download_url, headers=headers, timeout=20)
                response.raise_for_status()
                
                content = response.text

                # Verification: Ensure we didn't get an HTML wrapper
                if "<!DOCTYPE html>" in content or "<html>" in content:
                    print(f"  [!] Error: Received HTML instead of raw text for {case_id}. Check URL.")
                    continue
                
                # Verify content is a valid CSV by loading it into a DataFrame
                df = pd.read_csv(io.StringIO(content))
                
                # Save as clean CSV
                df.to_csv(ann_path, index=False)
                print(f"  [✓] Annotation saved: {len(df)} rows recovered.")
                
                # Slight pause to be polite to PhysioNet servers
                time.sleep(0.5)

            except Exception as e:
                print(f"  [!] PhysioNet Error for {case_id}: {e}")
        else:
            print(f"  [-] Annotation {ann_filename} already exists.")

if __name__ == "__main__":
    # Add your target case IDs here
    # Example: 337, 2891, 3125
    target_cases = [3129, 3125, 3134, 2891, 3125] 
    download_vitaldb_and_annotations(target_cases)