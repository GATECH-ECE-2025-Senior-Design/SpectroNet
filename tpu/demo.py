import os
import numpy as np
import time
import re
import logging
import librosa
import tensorflow as tf
from pycoral.utils.edgetpu import make_interpreter

# === Logging Configuration ===
log_file = "inference_log.txt"
log_format = "%(asctime)s - %(levelname)s - %(message)s"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler(log_file, mode="w")
file_handler.setFormatter(logging.Formatter(log_format))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# === Constants for Spectrogram Processing ===
SR = 8000
N_MELS = 96
HOP_LENGTH = 64
SAMPLES_PER_DFT = 384
TARGET_SHAPE = (96, 96)

# === Paths ===
WAV_DIR = "WAVs/"  # Directory containing .wav files
SPECTROGRAM_DIR = "Spectrograms/"  # Directory for storing .npy files
EDGE_TPU_MODEL = "quantized2_mel_spectrogram_model_edgetpu.tflite"

# === Ensure Directories Exist ===
if not os.path.exists(SPECTROGRAM_DIR):
    os.makedirs(SPECTROGRAM_DIR)

# === Load TPU Model ===
tpu_interpreter = make_interpreter(EDGE_TPU_MODEL)
tpu_interpreter.allocate_tensors()

# === Function to Convert WAV to Spectrogram ===
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
    return spectrogram_resized.numpy()

# === Function to Extract Label from Filename ===
def extract_label(filename):
    logger.info(f"Extracting label from filename: {filename}")  # Debugging step
    
    # Remove file extension if present
    base_name = os.path.splitext(filename)[0]  # Removes ".npy" or ".wav"

    # Convert to lowercase to match dictionary
    word = base_name.lower()

    # Mapping words to numbers
    word_to_number = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9
    }

    extracted_label = word_to_number.get(word, None)
    
    return extracted_label

# === Function to Preprocess .npy File for Inference ===
def preprocess_npy(npy_path):
    data = np.load(npy_path)

    if data.shape != (96, 96):
        raise ValueError(f"Expected shape (96, 96), but got {data.shape}")

    # Normalize using (X + 80) / 80
    data = (data + 80) / 80  

    # Scale to [0,255] for uint8
    data = data * 255  
    data = np.clip(data, 0, 255).astype(np.uint8)

    if len(tpu_interpreter.get_input_details()[0]['shape']) == 4:
        data = np.expand_dims(data, axis=-1)  # Shape becomes (96,96,1)

    return data

# === Function to Run Inference on TPU ===
def run_inference(interpreter, data):
    input_details = interpreter.get_input_details()[0]
    input_tensor_index = input_details['index']

    if data.shape != tuple(input_details['shape'][1:]):
        raise ValueError(f"Expected input shape {input_details['shape'][1:]}, but got {data.shape}")

    interpreter.tensor(input_tensor_index)()[0] = data

    start_time = time.perf_counter()
    interpreter.invoke()
    end_time = time.perf_counter()

    output_details = interpreter.get_output_details()[0]
    output_data = interpreter.get_tensor(output_details['index'])

    predicted_label = np.argmax(output_data)
    inference_time = (end_time - start_time) * 1_000_000  # Convert to µs

    return predicted_label, inference_time, output_data

# === Function to Process WAV Files and Run Inference (Only TPU) ===
def process_wavs_and_run_inference():
    wav_files = sorted([f for f in os.listdir(WAV_DIR) if f.lower().endswith(".wav")])

    if not wav_files:
        logger.info("No .wav files found in the directory.")
        return

    tpu_times = []

    logger.info("\n================== AUDIO INFERENCE RESULTS ==================")

    for i, wav_file in enumerate(wav_files):
        wav_path = os.path.join(WAV_DIR, wav_file)
        base_name = os.path.splitext(wav_file)[0]
        npy_path = os.path.join(SPECTROGRAM_DIR, base_name + ".npy")

        logger.info(f"\nProcessing {wav_file}...")

        # Convert WAV to Spectrogram
        audio = load_audio(wav_path)
        mel_spec_db = compute_mel_spectrogram(audio)
        processed_spec = preprocess_spectrogram(mel_spec_db)
        if processed_spec.shape == (96, 96, 1):
            processed_spec = np.squeeze(processed_spec, axis=-1)
        np.save(npy_path, processed_spec)

        logger.info(f"Saved spectrogram to {npy_path}")

        # Extract label from filename
        label = extract_label(base_name)

        # Preprocess .npy file for inference
        data = preprocess_npy(npy_path)

        # Run inference on TPU
        predicted_tpu, time_tpu, _ = run_inference(tpu_interpreter, data)
        if i > 0:
            tpu_times.append(time_tpu)

        # Log results
        logger.info(f"Expected Label: {label}")
        logger.info(f"Edge TPU Predicted: {predicted_tpu}, Time: {time_tpu:.2f} µs")

    # Compute average inference times
    avg_tpu_time = sum(tpu_times) / len(tpu_times) if len(tpu_times) > 0 else 0

    logger.info("\n================== PERFORMANCE SUMMARY ==================")
    logger.info(f"Total Files Processed: {len(wav_files)}")
    logger.info(f"Average Edge TPU Time (Excluding 1st run): {avg_tpu_time:.2f} µs")
    logger.info("=========================================================")

# === Main Execution ===
if __name__ == "__main__":
    process_wavs_and_run_inference()
