import numpy as np
import time
import re
from pycoral.utils.edgetpu import make_interpreter

# Path to your Edge TPU compiled model
MODEL_PATH = "quantized_spectrogram_model_edgetpu.tflite"

# Load the Edge TPU interpreter
interpreter = make_interpreter(MODEL_PATH)
interpreter.allocate_tensors()

# Function to extract label from filename (first number in "X_Y_Z.npy")
def extract_label(filename):
    match = re.match(r'(\d+)_\d+_\d+\.npy', filename)
    if match:
        return int(match.group(1))  # Extract the first number (X) as label
    return None  # Return None if filename format is incorrect

# Function to preprocess the input .npy file with normalization
def preprocess_npy(npy_path):
    data = np.load(npy_path)  # Load the numpy array
    print(f"Original data shape: {data.shape}, dtype: {data.dtype}")

    # Ensure the array is in (96, 96) format
    if data.shape != (96, 96):
        raise ValueError(f"Expected shape (96, 96), but got {data.shape}")

    # Apply normalization: X = (X + 80) / 80
    data = (data + 80) / 80  # Normalize to [0,1]

    # Scale to [0,255] for Edge TPU
    data = data * 255  
    data = np.clip(data, 0, 255).astype(np.uint8)  # Ensure uint8 format

    # Expand dimensions if the model expects (96,96,1)
    if len(interpreter.get_input_details()[0]['shape']) == 4:
        data = np.expand_dims(data, axis=-1)  # Shape becomes (96,96,1)

    print(f"Processed data shape: {data.shape}, dtype: {data.dtype}")
    return data

# Run inference
def run_inference(npy_path):
    label = extract_label(npy_path)  # Get ground truth label
    data = preprocess_npy(npy_path)

    # Get model input tensor details
    input_details = interpreter.get_input_details()[0]
    input_tensor_index = input_details['index']

    # Ensure the input shape matches model expectations
    if data.shape != tuple(input_details['shape'][1:]):
        raise ValueError(f"Expected input shape {input_details['shape'][1:]}, but got {data.shape}")

    # Set input tensor
    interpreter.tensor(input_tensor_index)()[0] = data

    # Run inference
    start_time = time.time()
    interpreter.invoke()
    end_time = time.time()

    # Retrieve output
    output_details = interpreter.get_output_details()[0]
    output_data = interpreter.get_tensor(output_details['index'])

    # Get the predicted label (assuming output is classification probabilities)
    predicted_label = np.argmax(output_data)  # Get index of max probability

    # Print results
    inference_time = (end_time - start_time) * 1000  # Convert to milliseconds
    print(f"\nFile: {npy_path}")
    print(f"Inference Time: {inference_time:.2f} ms")
    print(f"Expected Label: {label}")
    print(f"Predicted Label: {predicted_label}")
    print(f"Raw Model Output: {output_data}")

# Example usage
if __name__ == "__main__":
    NPY_PATH = "9_13_42.npy"  # Replace with your actual .npy file
    run_inference(NPY_PATH)