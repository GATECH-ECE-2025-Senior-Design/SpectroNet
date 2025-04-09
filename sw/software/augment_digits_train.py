import os
import numpy as np
import soundfile as sf
import re
import librosa
import threading
from scipy import signal
import argparse

# Number of new files per augmentation type
N_NEW_FILES_PER_AUG_TYPE = 2

# Hard-coded file paths (do not change)
BASE_DIR = os.path.abspath("sw")  # Root directory
parser = argparse.ArgumentParser(description="Augment .wav files with noise.")
parser.add_argument('--input_dir', type=str, required=True, help="Directory containing .wav files to augment.")
args = parser.parse_args()
# DATASET_DIR = "/Users/padmamithra/Downloads/SpectroNet/sw/datasets/digits_train"
DATASET_DIR = args.input_dir  # Use the passed directory
NOISE_DIR = "/Users/padmamithra/Downloads/SpectroNet/sw/software/noise_augment/PCAFETER"

# Define datasets_folder (added so it’s available if needed later)
datasets_folder = os.path.join(BASE_DIR, "..", "datasets")

# Regex for file names (Matches files named like X_YY_N.wav)
filename_pattern = re.compile(r"^(\d)_(\d{2})_(\d+)\.wav$")

###############################
# Augmentation Functions
###############################

def add_background_noise(audio, noise, snr_db_range=(0, 30)):
    """Add random background noise at a random SNR within snr_db_range."""
    snr_db = np.random.uniform(*snr_db_range)
    if len(noise) > len(audio):
        start_idx = np.random.randint(0, len(noise) - len(audio))
        noise_segment = noise[start_idx:start_idx+len(audio)]
    else:
        noise_segment = np.tile(noise, int(np.ceil(len(audio)/len(noise))))[:len(audio)]
    
    audio_rms = np.sqrt(np.mean(audio**2)) + 1e-8
    noise_rms = np.sqrt(np.mean(noise_segment**2)) + 1e-8
    desired_noise_rms = audio_rms / (10**(snr_db/20))
    scaling_factor = desired_noise_rms / noise_rms
    noise_scaled = noise_segment * scaling_factor
    return audio + noise_scaled

def add_reverb(audio, rir, normalize=True):
    """Convolve audio with a Room Impulse Response (RIR) to add reverb."""
    rev_audio = signal.convolve(audio, rir, mode='full')
    if normalize:
        orig_rms = np.sqrt(np.mean(audio**2)) + 1e-8
        rev_rms = np.sqrt(np.mean(rev_audio**2)) + 1e-8
        rev_audio *= (orig_rms / rev_rms)
    return rev_audio

def pitch_shift(audio, sr, semitone_range=(-2, 2)):
    """Random pitch shift within semitone_range (e.g., ±2 semitones)."""
    semitones = np.random.uniform(*semitone_range)
    return librosa.effects.pitch_shift(audio, sr=sr, n_steps=semitones)

def time_stretch(audio, stretch_range=(0.9, 1.1)):
    """Random time stretch within stretch_range (e.g., 0.9–1.1)."""
    rate = np.random.uniform(*stretch_range)
    return librosa.effects.time_stretch(audio, rate=rate)

def time_shift(audio, max_shift=0.1):
    """Circular shift audio up to ± max_shift fraction of its length."""
    length = len(audio)
    shift_amt = int(np.random.uniform(-max_shift, max_shift) * length)
    return np.roll(audio, shift_amt)

def random_filter(audio, sr, filter_types=('low', 'high', 'band'),
                  freq_range=(300, 3000), order=4):
    """Apply a random Butterworth filter (low, high, or band) with random cutoff(s)."""
    ftype = np.random.choice(filter_types)
    low_freq = np.random.uniform(*freq_range)
    high_freq = np.random.uniform(*freq_range)
    if low_freq > high_freq:
        low_freq, high_freq = high_freq, low_freq
    nyquist = sr / 2.0
    low_norm = low_freq / nyquist
    high_norm = high_freq / nyquist
    if ftype == 'low':
        b, a = signal.butter(order, low_norm, btype='low')
    elif ftype == 'high':
        b, a = signal.butter(order, high_norm, btype='high')
    else:
        b, a = signal.butter(order, [low_norm, high_norm], btype='band')
    return signal.lfilter(b, a, audio)

def random_gain(audio, gain_range=(0.5, 2.0)):
    """Randomly scale audio amplitude by factor in gain_range."""
    gain = np.random.uniform(*gain_range)
    return audio * gain

def random_clipping(audio, clip_prob=0.2, clip_threshold_range=(0.2, 0.9)):
    """With probability clip_prob, clip the waveform to ± threshold in clip_threshold_range."""
    if np.random.rand() < clip_prob:
        threshold = np.random.uniform(*clip_threshold_range)
        audio = np.clip(audio, -threshold, threshold)
    return audio

def augment_pipeline(audio, sr, noise=None, rir=None,
                     p_noise=0.5, p_reverb=0.3, p_pitch_stretch=0.5,
                     p_filter=0.3, p_clip=0.2):
    """
    Applies a sequence of augmentations (randomly) to an audio signal.
    """
    # Random gain always
    audio = random_gain(audio, (0.7, 1.3))
    
    # Noise addition
    if noise is not None and np.random.rand() < p_noise:
        audio = add_background_noise(audio, noise, snr_db_range=(0, 20))
        
    # Reverb
    if rir is not None and np.random.rand() < p_reverb:
        audio = add_reverb(audio, rir, normalize=True)
    
    # Pitch or Time Stretch (50% chance each)
    if np.random.rand() < p_pitch_stretch:
        if np.random.rand() < 0.5:
            audio = pitch_shift(audio, sr, semitone_range=(-2, 2))
        else:
            audio = time_stretch(audio, stretch_range=(0.9, 1.1))
    
    # Time shift (always a small shift)
    audio = time_shift(audio, max_shift=0.1)
    
    # Random filter
    if np.random.rand() < p_filter:
        audio = random_filter(audio, sr, filter_types=('low', 'high', 'band'),
                              freq_range=(300, 3000), order=4)
    
    # Random clipping
    audio = random_clipping(audio, clip_prob=p_clip, clip_threshold_range=(0.2, 0.9))
    
    return audio

#############################################################
# Thread worker function: processes all files in one folder
#############################################################
def augment_wavs_in_folder(folder_path, noise_data):  # rir_data can be added if available
    """
    1) Find all .wav files in this folder.
    2) Track highest index for each (label, speaker).
    3) For each file, generate new augmented files.
    """
    # 1) Gather all .wav files in this folder
    wav_paths = []
    for fn in os.listdir(folder_path):
        if fn.endswith(".wav"):
            full_path = os.path.join(folder_path, fn)
            wav_paths.append(full_path)

    # 2) Build dictionary of highest index for each (label, speaker)
    highest_index_dict = {}
    for path in wav_paths:
        filename = os.path.basename(path)
        match = filename_pattern.match(filename)
        if match:
            label_str, speaker_str, n_str = match.groups()
            label = int(label_str)
            speaker = int(speaker_str)
            index_n = int(n_str)
            key = (label, speaker)
            highest_index_dict[key] = max(index_n, highest_index_dict.get(key, -1))

    # 3) For each .wav file, generate new augmented files
    for path in wav_paths:
        filename = os.path.basename(path)
        match = filename_pattern.match(filename)
        if not match:
            print(f"Skipping file with unexpected name: {filename}")
            continue

        label_str, speaker_str, n_str = match.groups()
        label = int(label_str)
        speaker = int(speaker_str)
        index_n = int(n_str)

        key = (label, speaker)
        current_max = highest_index_dict[key]
        new_file_index = current_max + 1

        # Load the WAV
        audio, sr = librosa.load(path, sr=16000)

        # Generate N_NEW_FILES_PER_AUG_TYPE augmented files
        for _ in range(N_NEW_FILES_PER_AUG_TYPE):
            aug_audio = augment_pipeline(
                audio, sr=16000,
                noise=noise_data,
                # rir can be added here if available
                p_noise=0.5,
                p_reverb=0.3,
                p_pitch_stretch=0.5,
                p_filter=0.3,
                p_clip=0.2
            )
            out_name = f"{label}_{speaker_str}_{new_file_index}.wav"
            out_path = os.path.join(folder_path, out_name)
            sf.write(out_path, aug_audio, sr)
            new_file_index += 1

        highest_index_dict[key] = new_file_index - 1

    print(f"[THREAD] Done augmenting folder: {folder_path}")

def downmix_channels_to_mono(directory):
    """
    Reads WAV files named chXX.wav (XX from 01 to 16), downmixes them to mono.
    """
    num_channels = 16
    all_audio = []
    for i in range(1, num_channels + 1):
        filename = f"{directory}/ch{i:02d}.wav"
        y, sr = librosa.load(filename, sr=None)
        all_audio.append(y)
    all_audio = np.vstack(all_audio)
    mono_audio = np.mean(all_audio, axis=0)
    return mono_audio

############################################
# Main: Launch a thread per subfolder
############################################
if __name__ == "__main__":
    # Load noise audio data as a NumPy array using the downmix function
    noise_data = downmix_channels_to_mono(NOISE_DIR)

    threads = []
    for subfolder_name in os.listdir(DATASET_DIR):
        subfolder_path = os.path.join(DATASET_DIR, subfolder_name)
        if os.path.isdir(subfolder_path):
            t = threading.Thread(target=augment_wavs_in_folder, args=(subfolder_path, noise_data))
            t.start()
            threads.append(t)
    for t in threads:
        t.join()
    print("All threads finished. Augmentation complete.")