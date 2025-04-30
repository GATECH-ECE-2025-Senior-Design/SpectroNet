import struct
import numpy as np
import matplotlib.pyplot as plt
import librosa

def hex_to_float(hex_str: str) -> np.float32:
    return struct.unpack('!f', bytes.fromhex(hex_str))[0]

def load_from_txt(file_path: str, height: int) -> np.ndarray:
    # hex string float
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f]
    # convert to float
    values_1D = [(hex_to_float(line)) for line in lines]
    # check that output is a multiple of height (else there is a hardware problem)
    if len(values_1D) % height != 0:
        raise ValueError(f"Total number of values must be a multiple of {height}.")
    # 2d array that is [height] tall
    # transpose is used because the first [height] samples represent a vertical set of pixels
    return np.transpose(np.asarray(values_1D).reshape(-1, height))

def plot_heatmap(power: np.ndarray):
    power_dB = librosa.power_to_db(power, ref=np.max)

    plt.figure(figsize=(10, 6))
    plt.imshow(power_dB, aspect='auto', interpolation='nearest', origin='lower')
    plt.colorbar(label='Log Power')
    plt.xlabel("FFT Index")
    plt.ylabel("FFT Bin")
    plt.title("Wiwiwi")
    plt.show()

if __name__ == "__main__":
    # spectrogram -- log(stft^2)
    file_spec = "spec_out.txt"
    spec = load_from_txt(file_spec, 256)
    plot_heatmap(spec)
    # mel spectrogram -- log spaced spectrogram
    file_mel = "mel_out.txt"
    mel = load_from_txt(file_mel, 96)
    plot_heatmap(mel)