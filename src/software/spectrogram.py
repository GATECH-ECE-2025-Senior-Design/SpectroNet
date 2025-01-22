import numpy as np
import matplotlib.pyplot as plt
import os
import librosa
from scipy.io import wavfile
from scipy.signal import spectrogram
from scipy.signal import resample_poly

def read_wav(file_path, target_sample_rate=8000, target_dtype=np.int16):
  """
  Reads .wav file specified by path, decimates to specified sample rate and quantizes to specified precision.
  Returns the audio as an array.

  Parameters:
  - file_path: The path to the .wav file.
  - target_sample_rate: The targeted sample_rate.
  - target_dtype: The targeted data type.

  Returns:
  - audio_data (np.ndarray): The audio data as an array of the target data type.
  """

  sample_rate, audio_data = wavfile.read(file_path)

  # resample to target sample rate if sample rates are different
  if target_sample_rate != sample_rate:
      audio_data = resample_poly(audio_data, target_sample_rate, sample_rate)

  # convert to target quantization
  if target_dtype != audio_data.dtype:
    audio_data = audio_data.astype(target_dtype)

  return audio_data

# just calls scipy spectrogram for now
def spectrogram_choice(sample_rate, audio_data, spec_type="simple", dft_bins=128, hop_length=32):
  if spec_type == "simple":
    overlap_length = dft_bins - hop_length
    frequency, time, power = spectrogram(audio_data, fs=sample_rate, nperseg=dft_bins, noverlap=overlap_length)
    return frequency, time, power
  elif spec_type == "cqt":
    power = np.abs(librosa.cqt(audio_data, sr=sample_rate, n_bins=128, bins_per_octave=20, hop_length=hop_length))
    # let's just call the bins "frequency"
    frequency = np.linspace(0, power.shape[0], power.shape[0])
    # and pre-calculate time
    time = np.linspace(0, len(audio_data), power.shape[1])
    return frequency, time, power
  else:
    print("Error: Invalid value for spectrogram_choice argument \'type\'!")
    exit()

########
# TEST #
########

sample_rate = 8000
current_dir = os.path.dirname(os.path.abspath(__file__))

audio_data = read_wav(os.path.join(current_dir, "..", "datasets", "digits", "01", "0_01_0.wav"), target_sample_rate=sample_rate, target_dtype=np.float32)
# plt.figure(figsize=(10, 4))
# plt.plot(audio_data)
# plt.title(f"Audio Waveform - {sample_rate} Hz")
# plt.xlabel('Sample Index')
# plt.ylabel('Amplitude')
# plt.grid(True)
# plt.show()

frequency, time, power = spectrogram_choice(sample_rate, audio_data, spec_type="cqt", dft_bins=128, hop_length=48)
plt.pcolormesh(time, frequency, 10 * np.log10(power), shading='auto')
plt.title('Spectrogram')
plt.xlabel('Time [s]')
plt.ylabel('Frequency [Hz]')
plt.colorbar(label='Power [dB]')
plt.show()
