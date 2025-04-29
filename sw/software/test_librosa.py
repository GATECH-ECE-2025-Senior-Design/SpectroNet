import librosa
import multiprocessing

file_path = "/Users/padmamithra/Downloads/SpectroNet/sw/datasets/digits_train/7_43_3.wav"

try:
    y, sr = librosa.load(file_path, sr=16000)
    print(f"Successfully loaded: {file_path} (Length: {len(y)} samples, Sample Rate: {sr})")
except Exception as e:
    print(f"Error loading file: {e}")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
