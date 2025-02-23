import os
import numpy as np
import random

spectrogram_folder = "/content/spectrogram_data/images"

# List all .npy files
npy_files = [f for f in os.listdir(spectrogram_folder) if f.endswith('.npy')]

# Track any corrupted or problematic files
corrupt_files = []
zero_files = []
shape_set = set()  # To track different shapes

# Check each file
for file in npy_files:
    file_path = os.path.join(spectrogram_folder, file)

    try:
        # Load the .npy file
        spectrogram = np.load(file_path)

        # Track the shape
        shape_set.add(spectrogram.shape)

        # Check for all-zero spectrograms
        if np.all(spectrogram == 0):
            zero_files.append(file)

    except Exception as e:
        print(f"Corrupt file detected: {file} ({e})")
        corrupt_files.append(file)

# Print results
print(f"Checked {len(npy_files)} files.")
print(f"Unique spectrogram shapes found: {shape_set}")
print(f"{len(corrupt_files)} corrupt files: {corrupt_files}")
print(f"{len(zero_files)} all-zero files: {zero_files}")

# Pick a few files for debugging
debug_files = random.sample(npy_files, 5)

for file in debug_files:
    file_path = os.path.join(spectrogram_folder, file)
    spectrogram = np.load(file_path)

    print(f"{file} | Shape: {spectrogram.shape} | Min: {np.min(spectrogram)} | Max: {np.max(spectrogram)} | Mean: {np.mean(spectrogram)}")

# Select a sample spectrogram
file_path = os.path.join(spectrogram_folder, npy_files[0])  # Pick first file
spectrogram = np.load(file_path)

# Check for NaN, Inf, or extreme values
print(f"Contains NaN? {np.isnan(spectrogram).any()}")
print(f"Contains Inf? {np.isinf(spectrogram).any()}")