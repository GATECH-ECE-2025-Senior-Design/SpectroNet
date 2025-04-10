import os
import numpy as np
import tensorflow as tf
import librosa

# Set up model & functions (from your provided code)
SR = 8000
N_MELS = 96
HOP_LENGTH = 64
SAMPLES_PER_DFT = 384
TARGET_SHAPE = (96, 96)

def load_audio(file_path, sr=SR):
    audio, _ = librosa.load(file_path, sr=sr)
    return audio

def compute_mel_spectrogram(audio, sr=SR, n_mels=N_MELS, hop_length=HOP_LENGTH, n_fft=SAMPLES_PER_DFT):
    mel_spec = librosa.feature.melspectrogram(
        y=audio,
        sr=sr,
        n_mels=n_mels,
        hop_length=hop_length,
        n_fft=n_fft
    )
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    return mel_spec_db

def preprocess_spectrogram(spectrogram, target_shape=TARGET_SHAPE):
    spectrogram_3d = spectrogram[..., np.newaxis]
    spectrogram_resized = tf.image.resize(spectrogram_3d, target_shape)
    # spectrogram_norm = (spectrogram_resized + 80.0) / 80.0
    return spectrogram_resized.numpy()

# Define input and output directories
wav_dir = "WAVs"  # directory containing your .wav files
output_dir = "spectrograms"  # directory where .npy files will be saved

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each WAV file in the directory
for filename in os.listdir(wav_dir):
    if filename.lower().endswith(".wav"):
        wav_path = os.path.join(wav_dir, filename)
        print(f"Processing {wav_path}...")
        
        # Load audio file
        audio = load_audio(wav_path)
        
        # Compute mel spectrogram
        mel_spec_db = compute_mel_spectrogram(audio)
        
        # Preprocess spectrogram (resize and normalize)
        processed_spec = preprocess_spectrogram(mel_spec_db)
        if processed_spec.shape == (96, 96, 1):
            processed_spec = np.squeeze(processed_spec, axis=-1)
        # Save the processed spectrogram as a .npy file
        base_name = os.path.splitext(filename)[0]
        npy_filename = os.path.join(output_dir, base_name + ".npy")
        np.save(npy_filename, processed_spec)
        
        print(f"Saved spectrogram to {npy_filename}")
