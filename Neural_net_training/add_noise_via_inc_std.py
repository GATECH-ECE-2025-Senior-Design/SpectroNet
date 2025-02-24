# --- Function to Add Noise (with fixed noise_std) ---
def add_noise_to_spectrogram(file_path):
    """
    Loads a spectrogram from a .npy file, adds Gaussian noise with a fixed
    standard deviation, and returns the noisy spectrogram.
    """
    noise_std = 12  # Fixed noise level; adjust as needed 
    # -> approximately 0.1 std means roughly around 15 dB
    # speech can drop to around 15 dB on the battlefield
    spectrogram = np.load(file_path)
    noise = np.random.normal(loc=0.0, scale=noise_std, size=spectrogram.shape)
    noisy_spectrogram = spectrogram + noise
    return noisy_spectrogram

# --- Apply Noise to All Files and Save Them ---
all_noisy_files = {}
for file in files:
    file_path = os.path.join(spectrogram_folder, file)
    noisy_spec = add_noise_to_spectrogram(file_path)
    noisy_file_path = file_path.replace(".npy", "_noisy.npy")
    np.save(noisy_file_path, noisy_spec)
    all_noisy_files[file] = noisy_file_path

print("Noisy files created for all files:")
for orig, noisy in all_noisy_files.items():
    print(f"{orig} -> {noisy}")

# Later, when loading data, I load the noisy files and then apply normalization:
# For example:
# normalized = (noisy_spectrogram + 80) / 80