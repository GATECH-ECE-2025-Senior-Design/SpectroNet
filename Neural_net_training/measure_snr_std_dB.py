import numpy as np
import os

noise_std = 12  # Fixed noise level; adjust as needed 

def measure_snr_db(spectrogram, noise_std):
    """
    Computes an approximate SNR (in dB) for a given spectrogram by comparing the 
    mean signal power to the theoretical noise power.
    """
    # Calculate the average power of the spectrogram (signal power)
    signal_power = np.mean(spectrogram**2)
    # Theoretical noise power is noise_std squared (for Gaussian noise)
    noise_power = noise_std**2
    # Compute SNR in dB
    snr_db = 10 * np.log10(signal_power / noise_power)
    return snr_db

# Option 1: Run across all noisy spectrogram files
noisy_files = [f for f in os.listdir(spectrogram_folder) if f.endswith("_noisy.npy")]
snr_values = []

for file in noisy_files:
    file_path = os.path.join(spectrogram_folder, file)
    spec = np.load(file_path)
    snr = measure_snr_db(spec, noise_std)
    snr_values.append(snr)

print(f"Processed {len(noisy_files)} files.")
print("SNR statistics (in dB):")
print("Mean SNR:", np.mean(snr_values))
print("Min SNR:", np.min(snr_values))
print("Max SNR:", np.max(snr_values))

# Option 2: If you only want to check a sample of files
import random
sample_files = random.sample(noisy_files, min(10, len(noisy_files)))
for file in sample_files:
    file_path = os.path.join(spectrogram_folder, file)
    spec = np.load(file_path)
    snr = measure_snr_db(spec, noise_std)
    print(f"{file} SNR: {snr:.2f} dB")