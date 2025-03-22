import struct
import numpy as np
import matplotlib.pyplot as plt
import librosa

def hex_to_float(hex_str: str) -> np.float32:
    return struct.unpack('!f', bytes.fromhex(hex_str))[0]

def load_from_txt(file_path: str) -> np.ndarray:
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f]

    # if len(lines) % 2 != 0:
    #     raise ValueError("File must contain an even number of lines (real/imag pairs)")
    
    values_1D = [(hex_to_float(line)) for line in lines]
    
    if len(values_1D) % 256 != 0:
        raise ValueError("Total number of values must be a multiple of 256.")
    
    return np.transpose(np.asarray(values_1D).reshape(-1,256)) # 256 output bins

def plot_heatmap(complex_array: np.ndarray):
    magnitude = np.abs(complex_array)  # Compute magnitude of complex numbers
    magnitude_dB = librosa.power_to_db(magnitude, ref=np.max)

    plt.figure(figsize=(10, 6))
    plt.imshow(magnitude_dB, aspect='auto', interpolation='nearest', origin='lower')
    plt.ylim(bottom=1, top=192) # cut out DC bin, cut out bins above half-nyquist
    plt.colorbar(label='Log Magnitude')
    plt.xlabel("Index in Row")
    plt.ylabel("Row Number")
    plt.title("Log-Scaled Heatmap of Complex Number Magnitudes")
    plt.show()

if __name__ == "__main__":
    file_path = "sim_out.txt"
    complex_array = load_from_txt(file_path)
    plot_heatmap(complex_array)
