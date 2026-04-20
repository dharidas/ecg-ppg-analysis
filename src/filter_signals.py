import os
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
import glob

# Configuration
PROCESSED_DIR = "data/vitaldb/processed"
FILTERED_DIR = "data/vitaldb/filtered"
SAMPLING_RATE = 500  # As defined in extraction script

# Filter configurations
ECG_LOWCUT = 0.5
ECG_HIGHCUT = 40.0  # 40 Hz gracefully eliminates 50/60Hz powerline noise without notch filter
FILTER_ORDER = 4

PPG_LOWCUT = 0.5
PPG_HIGHCUT = 8.0   # Heart rarely beats faster than 3-4 times/sec; restricts high-freq noise

def butter_bandpass(lowcut, highcut, fs, order=4):
    """Design a bandpass butterworth filter."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_bandpass_filter(data, lowcut, highcut, fs, order=4):
    """Apply the bandpass butterworth filter using filtfilt for zero-phase distortion."""
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def process_files():
    """Iterate through processed files and apply filters."""
    os.makedirs(FILTERED_DIR, exist_ok=True)
    
    # Find all processed csv.gz files
    search_path = os.path.join(PROCESSED_DIR, "*_processed.csv.gz")
    processed_files = glob.glob(search_path)
    
    if not processed_files:
        print(f"No processed files found in {PROCESSED_DIR}.")
        return

    for file_path in processed_files:
        filename = os.path.basename(file_path)
        print(f"Filtering {filename}...")
        
        try:
            # Load data
            df = pd.read_csv(file_path, compression='gzip')
            
            # Ensure the required columns exist
            if 'ecg_v' not in df.columns or 'ppg_v' not in df.columns:
                print(f"  [!] Skipping {filename}: Missing 'ecg_v' or 'ppg_v' columns.")
                continue

            # Filtering requires processing each segment individually 
            # to avoid artifacts at segment boundaries, but here we can group by segment_id if it exists
            # Let's check if 'segment_id' exists which was created in extract_signals
            if 'segment_id' in df.columns:
                # Group by segment to avoid filtering across discontinuous boundaries
                filtered_ecg = []
                filtered_ppg = []
                
                for _, group in df.groupby('segment_id', sort=False):
                    ecg_segment = group['ecg_v'].values
                    ppg_segment = group['ppg_v'].values
                    
                    # Apply filters
                    filtered_ecg_seg = apply_bandpass_filter(ecg_segment, ECG_LOWCUT, ECG_HIGHCUT, SAMPLING_RATE, FILTER_ORDER)
                    filtered_ppg_seg = apply_bandpass_filter(ppg_segment, PPG_LOWCUT, PPG_HIGHCUT, SAMPLING_RATE, FILTER_ORDER)
                    
                    filtered_ecg.extend(filtered_ecg_seg)
                    filtered_ppg.extend(filtered_ppg_seg)
                
                df['ecg_v_filtered'] = filtered_ecg
                df['ppg_v_filtered'] = filtered_ppg
                
            else:
                # Fallback to entire array if segment_id is missing
                df['ecg_v_filtered'] = apply_bandpass_filter(df['ecg_v'].values, ECG_LOWCUT, ECG_HIGHCUT, SAMPLING_RATE, FILTER_ORDER)
                df['ppg_v_filtered'] = apply_bandpass_filter(df['ppg_v'].values, PPG_LOWCUT, PPG_HIGHCUT, SAMPLING_RATE, FILTER_ORDER)

            # Drop old un-filtered columns optionally and rename or just append
            # Here we just replace them to keep file size comparable and same format or keep both
            # Let's replace the raw with filtered
            df['ecg_v'] = df['ecg_v_filtered']
            df['ppg_v'] = df['ppg_v_filtered']
            df.drop(columns=['ecg_v_filtered', 'ppg_v_filtered'], inplace=True)
            
            output_filename = filename.replace('_processed.csv.gz', '_filtered.csv.gz')
            output_path = os.path.join(FILTERED_DIR, output_filename)
            
            # Save the processed data
            df.to_csv(output_path, index=False, compression='gzip')
            print(f"  [✓] Success: Filtered data saved to {output_path}")
            
        except Exception as e:
            print(f"  [!] Error processing {filename}: {e}")

if __name__ == "__main__":
    process_files()
