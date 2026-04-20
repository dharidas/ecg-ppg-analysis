# ECG and PPG Analysis for Arrhythmia Detection

## Project Overview
This project aims to analyze Electrocardiogram (ECG) and Photoplethysmogram (PPG) data to detect arrhythmias using quantum-hybrid models. 

So far, the project focuses on the initial data engineering and signal processing pipeline, preparing high-resolution clinical data for downstream machine learning tasks. The pipeline involves downloading, segmenting, and applying digital filters to the physiological signals.

## Current Pipeline

The current data processing pipeline consists of three main stages, implemented as Python scripts in the `src/` directory.

### 1. Data Downloading (`src/download_data.py`)
This script automates the retrieval of patient data from the [VitalDB](https://vitaldb.net/) and PhysioNet databases.
- Retrieves high-resolution waveform data (`.vital` format) directly using the VitalDB API. Specifically, it requests the **ECG Lead II** and **PLETH (PPG)** tracks.
- Fetches the corresponding annotation files (`.csv`) containing patient metadata and clinical events from the PhysioNet open data server.
- The raw files are saved into the `data/vitaldb/raw/` directory (categorized into `waveforms` and `annotations`).

### 2. Signal Extraction and Segmentation (`src/extract_eec_ppg.py`)
This step processes the raw `.vital` waveform files into standardized segments useful for chunk-based machine learning approaches.
- Extracts waveform data at a sampling rate of **500Hz**.
- Divides the continuous track recordings into **30-second segments** (15,000 samples per segment).
- Applies a basic quality check: discards any segments that contain missing values (`NaN`) or appear to represent a "flatline" (standard deviation near zero).
- Exports the valid segments as compressed long-form tabular data (`.csv.gz`) into the `data/vitaldb/processed/` directory.

### 3. Signal Filtering (`src/filter_signals.py`)
Physiological signals are susceptible to various kinds of noise (e.g., baseline wander, powerline interference, motion artifacts). This script applies targeted digital filters to isolate the relevant signal frequency bands.
- Uses a **4th-order Butterworth bandpass filter**, applied bidirectionally (using `scipy.signal.filtfilt`) to prevent phase shift/distortion.
- **ECG Filtering:** Applied with a bandpass of **0.5 Hz to 40.0 Hz**. This configuration preserves the QRS complexes while effectively eliminating low-frequency baseline drift and high-frequency powerline noise (50/60Hz).
- **PPG Filtering:** Applied with a bandpass of **0.5 Hz to 8.0 Hz**. Because the heart beats relatively slowly (rarely faster than 3-4 beats per second), this tighter filter isolates the blood flow wave and aggressively cuts out higher-frequency artifacts.
- The filtered datasets overwrite the raw signal columns and are exported to the `data/vitaldb/filtered/` directory.

## Directory Structure
- `src/` - Contains the Python source code for data downloading and processing.
- `data/vitaldb/` - Storage location for local data processing.
  - `raw/` - Raw `.vital` and `.csv` annotations.
  - `processed/` - Sliced 30-second segments prior to filtering.
  - `filtered/` - Clean, filtered signals ready for model training.
- `docs/` - Project documentation.
