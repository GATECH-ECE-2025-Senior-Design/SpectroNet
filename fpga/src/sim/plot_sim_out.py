import struct
import numpy as np
import matplotlib.pyplot as plt
import librosa

def hex_to_float(hex_str: str) -> np.float32:
    return struct.unpack('!f', bytes.fromhex(hex_str))[0]

def load_complex_numbers_from_txt(file_path: str) -> np.ndarray:
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f]

    if len(lines) % 2 != 0:
        raise ValueError("File must contain an even number of lines (real/imag pairs)")
    
    complex_numbers = [complex(hex_to_float(lines[i]), hex_to_float(lines[i+1])) 
                       for i in range(0, len(lines), 2)]
    
    complex_array = np.array(complex_numbers, dtype=np.complex64)
    
    if len(complex_array) % 512 != 0:
        raise ValueError("Total number of complex numbers must be a multiple of 384")
    
    return np.transpose(complex_array.reshape(-1,512)) # 512 output bins (we only need 192 though)

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
    complex_array = load_complex_numbers_from_txt(file_path)
    plot_heatmap(complex_array)
