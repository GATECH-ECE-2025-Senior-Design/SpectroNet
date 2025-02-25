import os
import numpy as np

# --- Function to Add Noise (with fixed noise_std) ---
def add_noise_to_spectrogram(file_path):
    """
    Loads a spectrogram from a .npy file, adds Gaussian noise with a fixed
    standard deviation, and returns the noisy spectrogram.
    """
    noise_std = 12  # Adjust as needed
    spectrogram = np.load(file_path)
    noise = np.random.normal(loc=0.0, scale=noise_std, size=spectrogram.shape)
    noisy_spectrogram = spectrogram + noise
    return noisy_spectrogram

# 1. List the base (original) .npy files (skip those already ending in _noisy.npy)
files_to_process = [
    f for f in os.listdir(spectrogram_folder)
    if f.endswith(".npy") and not f.endswith("_noisy.npy")
]

# 2. For each original file:
#    a) load + add noise
#    b) save as "<original>_noisy.npy"
#    c) delete the old file
for file in files_to_process:
    file_path = os.path.join(spectrogram_folder, file)
    
    # a) Load + add noise
    noisy_spec = add_noise_to_spectrogram(file_path)
    
    # b) Create the noisy filename and save
    noisy_file_path = file_path.replace(".npy", "_noisy.npy")
    np.save(noisy_file_path, noisy_spec)
    
    # c) Remove the old original file
    os.remove(file_path)
    
    print(f"Created {noisy_file_path} and removed original {file_path}")

print("All original files have been converted to noisy files and deleted.")