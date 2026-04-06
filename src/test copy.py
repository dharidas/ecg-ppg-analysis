import os
import requests
import pandas as pd
import io

# Configuration
# Changed from /content/ to /files/ for direct raw access
BASE_URL = "https://physionet.org/files/vitaldb-arrhythmia/1.0.0/Annotation_Files/"
SAVE_DIR = "data/vitaldb/raw/annotations"

os.makedirs(SAVE_DIR, exist_ok=True)

def download_raw_annotation(case_id):
    filename = f"Annotation_file_{case_id}.csv"
    save_path = os.path.join(SAVE_DIR, filename)
    
    # Using the /files/ path usually provides the raw file directly
    url = f"{BASE_URL}{filename}"
    
    # Some PhysioNet files require the ?download=1 flag even on the files server
    params = {'download': '1'}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    print(f"Downloading Case {case_id} from {url}...")
    try:
        # Use params=params to ensure the download flag is attached correctly
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        
        content = response.text

        # 1. Check if we got HTML (the 'Preview' page)
        if "<!DOCTYPE html>" in content or "<html>" in content:
            print(f"  [!] Failed: Still receiving HTML for {case_id}. Server is redirecting to preview.")
            return False

        # 2. Check if the content is empty
        if not content.strip():
            print(f"  [!] Failed: File is empty for {case_id}.")
            return False

        # 3. Verify and Save
        df = pd.read_csv(io.StringIO(content))
        df.to_csv(save_path, index=False)
        print(f"  [✓] Success: Saved {len(df)} rows to {save_path}")
        return True

    except Exception as e:
        print(f"  [!] Error: {e}")
        return False

if __name__ == "__main__":
    # Test with Case 3125
    download_raw_annotation(3125)