import kagglehub
import os
import shutil
import argparse
import glob
import random
import librosa
import numpy as np
from collections import defaultdict

# ------------------------------------------------------------------------------
# Parse command line arguments
# ------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Download and preprocess Audio MNIST.")
parser.add_argument('--login', action='store_true', default=False, help="Set to True to log in.")
args = parser.parse_args()

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

# We will create the following folders:
train_path = os.path.join(datasets_folder, "digits_train")
test_path  = os.path.join(datasets_folder, "digits_test")

# Remove any old folders and then create new ones
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
    digit_str, speaker_str, _ = filename.split("_")
    digit = int(digit_str)
    speaker = int(speaker_str)
    digit_speaker_map[(digit, speaker)].append(file)

# ------------------------------------------------------------------------------
# Helper function: copy a .wav file into a speaker subfolder.
# ------------------------------------------------------------------------------
def copy_wav_to_subfolder(src_file, dest_root):
    filename = os.path.basename(src_file)
    _, speaker_str, _ = filename.split("_")
    speaker_num = int(speaker_str)
    speaker_folder_name = f"{speaker_num:02d}"
    speaker_subfolder = os.path.join(dest_root, speaker_folder_name)
    os.makedirs(speaker_subfolder, exist_ok=True)
    dest_path = os.path.join(speaker_subfolder, filename)
    shutil.copy2(src_file, dest_path)

# ------------------------------------------------------------------------------
# Split data into train and test sets (70% train, 30% test per (digit, speaker) group)
# ------------------------------------------------------------------------------
train_files = []
test_files = []

for (digit, speaker), files in digit_speaker_map.items():
    random.shuffle(files)
    num_files = len(files)
    train_count = int(0.70 * num_files)
    train_files.extend(files[:train_count])
    test_files.extend(files[train_count:])

# Shuffle test set for global randomness
random.shuffle(test_files)

# For training, extract labels (the label is the digit)
train_labels = [int(os.path.basename(f).split("_")[0]) for f in train_files]

# Optionally, apply chunked interleaving to training set
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

train_files, train_labels = chunked_interleaving(train_files, train_labels, chunk_size=10)

# ------------------------------------------------------------------------------
# Copy files into the respective folders, using subfolders for speaker IDs.
# ------------------------------------------------------------------------------
for file in train_files:
    copy_wav_to_subfolder(file, train_path)
for file in test_files:
    copy_wav_to_subfolder(file, test_path)

# ------------------------------------------------------------------------------
# Print dataset statistics
# ------------------------------------------------------------------------------
print(f"✅ Training dataset contains {len(train_files)} files.")
print(f"✅ Test dataset contains {len(test_files)} files.")

# ------------------------------------------------------------------------------
# Copy Background Noise into `datasets`
# ------------------------------------------------------------------------------
noise_path = os.path.join(datasets_folder, "noise")
if not os.path.exists(noise_path):
    os.makedirs(noise_path)
    shutil.copytree(audio_noise_path, noise_path, dirs_exist_ok=True)
    print(f"✅ Background Noise moved to '{datasets_folder}'.")
else:
    print("✅ Noise dataset already exists in 'datasets'!")