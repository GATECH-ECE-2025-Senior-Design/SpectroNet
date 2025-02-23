import numpy as np
import tensorflow as tf
import os
import random

# Define spectrogram folder path
spectrogram_folder = "/content/spectrogram_data/images"

# Get a list of all spectrogram `.npy` files
spectrogram_files = [os.path.join(spectrogram_folder, f) for f in os.listdir(spectrogram_folder) if f.endswith(".npy")]

# Select 5 random spectrograms
random_samples = random.sample(spectrogram_files, 5)

# ✅ Load and preprocess spectrograms
spectrograms = []
for file in random_samples:
    spectrogram = np.load(file)  # Load file
    spectrogram = (spectrogram + 80) / 80  # Normalize (same as training)
    spectrogram = np.expand_dims(spectrogram, axis=(0, -1))  # Add batch & channel dims
    spectrograms.append(spectrogram)

# Convert list to TensorFlow tensor (stack along batch dimension)
spectrograms = np.vstack(spectrograms).astype(np.float32)  # Shape: (5, 96, 96, 1)

# Get model logits
logits = model(spectrograms, training=False)  # Raw output before softmax

# Convert logits to softmax probabilities
softmax_probs = tf.nn.softmax(logits).numpy()

# Get predicted class
predicted_classes = np.argmax(softmax_probs, axis=1)

# Print results
for i, file in enumerate(random_samples):
    print(f"Sample {i+1} - File: {os.path.basename(file)}")
    print(f"Predicted Class: {predicted_classes[i]}")
    print(f"Softmax Probabilities: {softmax_probs[i]}\n")
