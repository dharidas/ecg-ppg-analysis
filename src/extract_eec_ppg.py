import os
import pandas as pd
import vitaldb
import numpy as np

# Configuration
RAW_DIR = "data/vitaldb/raw"
WAVEFORM_DIR = os.path.join(RAW_DIR, "waveforms")
ANNOTATION_DIR = os.path.join(RAW_DIR, "annotations")
PROCESSED_DIR = "data/vitaldb/processed"

SAMPLING_RATE = 500  # VitalDB high-res waveforms are typically 500Hz
SEGMENT_LEN_SEC = 30
SAMPLES_PER_SEGMENT = SAMPLING_RATE * SEGMENT_LEN_SEC

# Ensure output directory exists
os.makedirs(PROCESSED_DIR, exist_ok=True)

def extract_signals():
    # Find all downloaded waveform files
    vital_files = [f for f in os.listdir(WAVEFORM_DIR) if f.endswith('.vital')]
    
    if not vital_files:
        print("No .vital files found in raw/waveforms. Please run the download script first.")
        return

    for vf_name in vital_files:
        case_id = vf_name.replace('.vital', '')
        print(f"\nProcessing Case {case_id}...")
        
        # 1. Check for matching annotation
        ann_path = os.path.join(ANNOTATION_DIR, f"Annotation_file_{case_id}.csv")
        if not os.path.exists(ann_path):
            print(f"  [!] Skipping: Annotation file for {case_id} not found.")
            continue
        
        # 2. Load Waveforms from the local .vital file
        try:
            vf = vitaldb.VitalFile(os.path.join(WAVEFORM_DIR, vf_name))
            # Tracks we want: ECG (Lead II) and Pleth (PPG)
            # interval=0.002 corresponds to 500Hz
            vals = vf.to_numpy(['SNUADC/ECG_II', 'SNUADC/PLETH'], interval=1/SAMPLING_RATE)
            
            if vals is None or np.isnan(vals).all():
                print(f"  [!] Skipping: No valid waveform data in {vf_name}.")
                continue
        except Exception as e:
            print(f"  [!] Error reading .vital file: {e}")
            continue

        # 3. Load Annotation to get metadata
        ann_df = pd.read_csv(ann_path)
        # Assuming patient_id is in the annotation; otherwise use case_id
        # patient_id = ann_df['patient_id'].iloc[0] if 'patient_id' in ann_df.columns else f"P{case_id}"

        # 4. Slice into 30-second segments
        total_samples = len(vals)
        num_segments = int(total_samples // SAMPLES_PER_SEGMENT)
        
        case_segments = []

        for i in range(num_segments):
            start_idx = i * SAMPLES_PER_SEGMENT
            end_idx = (i + 1) * SAMPLES_PER_SEGMENT
            
            segment_data = vals[start_idx:end_idx]

            # Quality Check: Skip segments that are entirely NaN or "flatlined"
            if np.isnan(segment_data).any() or np.std(segment_data[:, 1]) < 0.001:
                continue

            # Create long-form DataFrame for this segment
            seg_df = pd.DataFrame({
                'case_id': case_id,
                # 'patient_id': patient_id,
                'segment_id': f"{case_id}_{i}",
                'timestamp_idx': np.arange(SAMPLES_PER_SEGMENT),
                'ecg_v': segment_data[:, 0],
                'ppg_v': segment_data[:, 1]
            })
            case_segments.append(seg_df)

        # 5. Save the processed data for this case
        if case_segments:
            final_case_df = pd.concat(case_segments, ignore_index=True)
            output_filename = f"case_{case_id}_processed.csv.gz"
            output_path = os.path.join(PROCESSED_DIR, output_filename)
            
            # Gzip compression is highly recommended for long-form CSVs
            final_case_df.to_csv(output_path, index=False, compression='gzip')
            print(f"  [✓] Success: Extracted {len(case_segments)} segments to {output_path}")
        else:
            print(f"  [!] No valid segments extracted for Case {case_id}.")

if __name__ == "__main__":
    extract_signals()