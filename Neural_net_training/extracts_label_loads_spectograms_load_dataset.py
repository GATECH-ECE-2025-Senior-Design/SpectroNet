import numpy as np
import tensorflow as tf
import os
import re

# Declare constants
IMAGE_HEIGHT = 96
IMAGE_WIDTH = 96
BATCH_SIZE = 32
N_CHANNELS = 1  # Grayscale spectrograms
N_CLASSES = 10

# Extract only the first number (X) from filename
def extract_label(filename):
    match = re.match(r'(\d+)_(\d+)_(\d+)\.npy', filename)  # Match full filename pattern
    if match:
        first_num = int(match.group(1))  # Take only the first number (X)
        speaker = int(match.group(2))
        return first_num, speaker
    return None, None  # Return None for invalid cases


# Function to load spectrograms
def load_spectrograms(folder):
    spectrograms, labels, speakers = [], [], []

    for file in os.listdir(folder):
        if file.endswith(".npy"):
            filepath = os.path.join(folder, file)
            label, speaker = extract_label(file)

            if label is None or not (0 <= label < N_CLASSES):
                continue

            spectrogram = np.load(filepath)
            spectrogram = np.expand_dims(spectrogram, axis=-1)  # Add channel dim
            spectrograms.append(spectrogram)
            labels.append(label)
            speakers.append(speaker)

    return np.array(spectrograms, dtype=np.float32), np.array(labels, dtype=np.int32), np.array(speakers, dtype=np.int32)

# 
X, y, speaker_ids = load_spectrograms(spectrogram_folder)

# One-hot encode labels
# y = tf.keras.utils.to_categorical(y, num_classes=N_CLASSES)

# Normalize spectrograms from [-80, 0] to [0,1]
X = (X + 80) / 80
print(f"Normalized spectrograms: Min {np.min(X)}, Max {np.max(X)}")
print("Unique speakers:", np.unique(speaker_ids))