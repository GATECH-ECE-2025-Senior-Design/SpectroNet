import numpy as np
import time
import re
import os
from pycoral.utils.edgetpu import make_interpreter
import tflite_runtime.interpreter as tflite
import tensorflow as tf
# Paths to models
EDGE_TPU_MODEL = "quantized2_mel_spectrogram_model_edgetpu.tflite"
CPU_MODEL = "quantized2_mel_spectrogram_model.tflite"  # Ensure you have the CPU model

# Load TPU & CPU interpreters **once**
tpu_interpreter = make_interpreter(EDGE_TPU_MODEL)
tpu_interpreter.allocate_tensors()

cpu_interpreter = tf.lite.Interpreter(model_path=CPU_MODEL)
cpu_interpreter.allocate_tensors()

input_details = cpu_interpreter.get_input_details()
output_details = cpu_interpreter.get_output_details()

print("CPU Model Input Shape:", input_details[0]['shape'])
print("CPU Model Output Shape:", output_details[0]['shape'])
print("CPU Model Input Type:", input_details[0]['dtype'])

# Mapping words to numbers (handling title case)
word_to_number = {
    "Zero": 0, "One": 1, "Two": 2, "Three": 3, "Four": 4,
    "Five": 5, "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9
}

# Function to extract label from filename
def extract_label(filename):
    match = re.match(r'([A-Za-z]+)\.npy$', filename)  # Match word before ".npy"
    if match:
        word = match.group(1)  # Keep original capitalization (Title Case)
        return word_to_number.get(word, None)  # Return number or None if not found
    return None  # Return None if the filename doesn't match

# Function to preprocess input .npy file
def preprocess_npy(npy_path):
    data = np.load(npy_path)  # Load the numpy array

    # Ensure correct shape
    if data.shape != (96, 96):
        raise ValueError(f"Expected shape (96, 96), but got {data.shape}")

    # Normalize using (X + 80) / 80
    data = (data + 80) / 80  

    # Scale to [0,255] for uint8
    data = data * 255  
    data = np.clip(data, 0, 255).astype(np.uint8)

    # Expand dimensions if necessary
    if len(tpu_interpreter.get_input_details()[0]['shape']) == 4:
        data = np.expand_dims(data, axis=-1)  # Shape becomes (96,96,1)

    return data

# Run inference
def run_inference(interpreter, data):
    # Get input details
    input_details = interpreter.get_input_details()[0]
    input_tensor_index = input_details['index']

    # Ensure the shape matches the model
    if data.shape != tuple(input_details['shape'][1:]):
        raise ValueError(f"Expected input shape {input_details['shape'][1:]}, but got {data.shape}")

    # Set input tensor
    interpreter.tensor(input_tensor_index)()[0] = data

    # Run inference and time it
    start_time = time.perf_counter()  # More precise timing
    interpreter.invoke()
    end_time = time.perf_counter()

    # Retrieve output
    output_details = interpreter.get_output_details()[0]
    output_data = interpreter.get_tensor(output_details['index'])

    # Get predicted label (assuming classification)
    predicted_label = np.argmax(output_data)
    inference_time = (end_time - start_time) * 1_000_000  # Convert to microseconds (µs)

    return predicted_label, inference_time, output_data

# Batch process multiple `.npy` files
def batch_compare_inference(directory):
    npy_files = sorted([f for f in os.listdir(directory) if f.endswith(".npy")])
    
    if not npy_files:
        print("No .npy files found in the directory.")
        return

    # Lists to store times (excluding first inference)
    tpu_times = []
    cpu_times = []

    print("\n================== BATCH INFERENCE RESULTS ==================")

    for i, npy_file in enumerate(npy_files):
        npy_path = os.path.join(directory, npy_file)
        label = extract_label(npy_file)  # Ground truth label
        data = preprocess_npy(npy_path)

        # Run on TPU
        predicted_tpu, time_tpu, output_tpu = run_inference(tpu_interpreter, data)
        if i > 0:  # Skip first run for fair average
            tpu_times.append(time_tpu)

        # Run on CPU
        predicted_cpu, time_cpu, output_cpu = run_inference(cpu_interpreter, data)
        cpu_times.append(time_cpu)

        # Print comparison
        print(f"\nFile: {npy_file}")
        print(f"Expected Label: {label}")
        print(f"Edge TPU Predicted: {predicted_tpu}, Time: {time_tpu:.2f} µs")
        print(f"CPU Predicted:      {predicted_cpu}, Time: {time_cpu:.2f} µs")

    # Calculate average inference time (excluding first TPU run)
    avg_tpu_time = sum(tpu_times) / len(tpu_times) if len(tpu_times) > 0 else 0
    avg_cpu_time = sum(cpu_times) / len(cpu_times) if len(cpu_times) > 0 else 0

    print("\n================== PERFORMANCE SUMMARY ==================")
    print(f"Total Files Processed: {len(npy_files)}")
    print(f"Average Edge TPU Time (Excluding 1st run): {avg_tpu_time:.2f} µs")
    print(f"Average CPU Time: {avg_cpu_time:.2f} µs")
    print("=========================================================")

# Example usage
if __name__ == "__main__":
    DIRECTORY = "Spectrograms/"  # Change this to your directory containing .npy files
    batch_compare_inference(DIRECTORY)
