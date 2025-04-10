#!/usr/bin/env python3
import kagglehub
import os
import shutil
import argparse
import glob
import random
import librosa
import numpy as np
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# ------------------------------------------------------------------------------
# Parse command line arguments
# ------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Download and preprocess Audio MNIST.")
parser.add_argument('--login', action='store_true', default=False, help="Set to True to log in.")
args = parser.parse_args()

# ------------------------------------------------------------------------------
# Global helper functions (module-level, so they can be pickled for multiprocessing)
# ------------------------------------------------------------------------------

def copy_wav_to_subfolder(src_file, dest_root):
    """
    Copy a single .wav file into a speaker subfolder in the given destination root.
    """
    filename = os.path.basename(src_file)
    try:
        _, speaker_str, _ = filename.split("_")
    except ValueError:
        # If filename does not match the expected format, skip it.
        print(f"Skipping file with unexpected name format: {filename}")
        return
    speaker_num = int(speaker_str)
    speaker_folder_name = f"{speaker_num:02d}"
    speaker_subfolder = os.path.join(dest_root, speaker_folder_name)
    os.makedirs(speaker_subfolder, exist_ok=True)
    dest_path = os.path.join(speaker_subfolder, filename)
    shutil.copy2(src_file, dest_path)

def chunked_interleaving(file_list, label_list, chunk_size=10):
    groups = defaultdict(list)
    for fpath, lbl in zip(file_list, label_list):
        groups[lbl].append(fpath)
    for lbl in groups:
        random.shuffle(groups[lbl])
    sub_chunks = []
    for lbl, fpaths in groups.items():
        for start in range(0, len(fpaths), chunk_size):
            chunk = fpaths[start:start + chunk_size]
            sub_chunks.append((lbl, chunk))
    random.shuffle(sub_chunks)
    new_file_list = []
    new_label_list = []
    for lbl, chunk in sub_chunks:
        for fpath in chunk:
            new_file_list.append(fpath)
            new_label_list.append(lbl)
    return new_file_list, new_label_list

def compute_mel_spectrogram(file_path):
    """
    Load the audio file and compute its mel spectrogram.
    Returns the mean value of the mel spectrogram as a summary statistic.
    In case of error, prints an error message and returns np.nan.
    """
    try:
        y, sr = librosa.load(file_path, sr=8000)
        mel = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=384, hop_length=64, n_mels=96, power=2.0)
        return mel.mean()
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return np.nan

def batched_process(file_list, batch_size, max_workers=30):
    """
    Process the list of files in batches using a ProcessPoolExecutor.
    Returns a combined list of results.
    """
    results = []
    num_files = len(file_list)
    num_batches = (num_files + batch_size - 1) // batch_size
    for i in range(0, num_files, batch_size):
        batch = file_list[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1} of {num_batches} ({len(batch)} files)...")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            batch_results = list(executor.map(compute_mel_spectrogram, batch))
        results.extend(batch_results)
    return results

# ------------------------------------------------------------------------------
# Main function encapsulating the sequential pipeline and parallel sections.
# ------------------------------------------------------------------------------
def main():
    # ------------------------------------------------------------------------------
    # Login to KaggleHub if requested
    # ------------------------------------------------------------------------------
    if args.login:
        kagglehub.login()

    # ------------------------------------------------------------------------------
    # Download datasets
    # ------------------------------------------------------------------------------
    audio_mnist_path = kagglehub.dataset_download("sripaadsrinivasan/audio-mnist")
    audio_noise_path = kagglehub.dataset_download("minsithu/audio-noise-dataset")

    print(f"✅ Audio MNIST dataset downloaded to: {audio_mnist_path}")
    print(f"✅ Background Noise dataset downloaded to: {audio_noise_path}")

    # ------------------------------------------------------------------------------
    # Define dataset storage paths
    # ------------------------------------------------------------------------------
    current_directory = os.path.dirname(os.path.realpath(__file__))
    datasets_folder = os.path.join(current_directory, "..", "datasets")
    os.makedirs(datasets_folder, exist_ok=True)

    # Create the following folders:
    train_path = os.path.join(datasets_folder, "digits_train")
    test_path  = os.path.join(datasets_folder, "digits_test")

    # Remove old folders, then recreate them
    for path in [train_path, test_path]:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

    # ------------------------------------------------------------------------------
    # Get all .wav files from the Audio MNIST dataset
    # ------------------------------------------------------------------------------
    audio_mnist_data_path = os.path.join(audio_mnist_path, "data")
    all_wav_files = glob.glob(os.path.join(audio_mnist_data_path, "**/*.wav"), recursive=True)

    # ------------------------------------------------------------------------------
    # Group files by (digit, speaker)
    # ------------------------------------------------------------------------------
    digit_speaker_map = defaultdict(list)
    for file in all_wav_files:
        filename = os.path.basename(file)
        try:
            digit_str, speaker_str, _ = filename.split("_")
            digit = int(digit_str)
            speaker = int(speaker_str)
            digit_speaker_map[(digit, speaker)].append(file)
        except ValueError:
            print(f"Skipping file with unexpected name format: {filename}")

    # ------------------------------------------------------------------------------
    # Split data into train and test sets (70% train, 30% test per group)
    # ------------------------------------------------------------------------------
    train_files = []
    test_files = []
    for (digit, speaker), files in digit_speaker_map.items():
        random.shuffle(files)
        num_files = len(files)
        train_count = int(0.70 * num_files)
        train_files.extend(files[:train_count])
        test_files.extend(files[train_count:])

    random.shuffle(test_files)
    train_labels = [int(os.path.basename(f).split("_")[0]) for f in train_files]

    # Apply chunked interleaving to the training set
    train_files, train_labels = chunked_interleaving(train_files, train_labels, chunk_size=10)

    # ------------------------------------------------------------------------------
    # Parallel copying of files using multithreading
    # ------------------------------------------------------------------------------
    def parallel_copy(file_list, dest_folder):
        with ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(lambda f: copy_wav_to_subfolder(f, dest_folder), file_list)

    print("📂 Copying training files in parallel...")
    parallel_copy(train_files, train_path)
    print("📂 Copying test files in parallel...")
    parallel_copy(test_files, test_path)

    # ------------------------------------------------------------------------------
    # Parallel CPU-bound signal processing with batched multiprocessing.
    # ------------------------------------------------------------------------------
    batch_size = 100  # Adjust batch size as needed
    print("⚙️ Processing training files in batches to compute mel spectrogram mean values...")
    mel_means = batched_process(train_files, batch_size=batch_size, max_workers=30)
    print(f"✅ Processed {len(mel_means)} training files. Sample mel spectrogram mean values (first 10):")
    print(mel_means[:10])

    # ------------------------------------------------------------------------------
    # Print dataset statistics
    # ------------------------------------------------------------------------------
    print(f"✅ Training dataset contains {len(train_files)} files.")
    print(f"✅ Test dataset contains {len(test_files)} files.")

    # ------------------------------------------------------------------------------
    # Copy Background Noise into datasets
    # ------------------------------------------------------------------------------
    noise_dir = os.path.join(datasets_folder, "noise")
    if not os.path.exists(noise_dir):
        os.makedirs(noise_dir)
        shutil.copytree(audio_noise_path, noise_dir, dirs_exist_ok=True)
        print(f"✅ Background Noise moved to '{datasets_folder}'.")
    else:
        print("✅ Noise dataset already exists in 'datasets'!")

if __name__ == "__main__":
    main()
