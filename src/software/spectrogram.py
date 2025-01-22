import numpy as np
import matplotlib.pyplot as plt
import os
import librosa
import math
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
    The audio data as an array of the target data type.

  TODO: Maybe add parameter for normalization? (multiply data by fixed amount before quantizing)
  """

  sample_rate, audio_data = wavfile.read(file_path)

  # resample to target sample rate if sample rates are different
  if target_sample_rate != sample_rate:
      audio_data = resample_poly(audio_data, target_sample_rate, sample_rate)

  # convert to target quantization
  if target_dtype != audio_data.dtype:
    audio_data = audio_data.astype(target_dtype)

  return audio_data

def spectrogram_choice(audio_data, sample_rate=8000, spec_type="simple", num_bins=128, hop_length=32):
  """
  Generates a square aspect-ratio spectrogram of the input waveform as defined by the function parameters.

  Parameters:
  - audio_data: The audio data as an array.
  - sample_rate: The sample rate of the audio data.
  - spec_type: The "type" of spectrogram to be generated. {"simple", "cqt"}.
  - bins: The resolution of the output image. 
    For DFTs, a non power-of-two number of bins will result in a larger DFT, 
    with uppermost bins being truncated. Thus, Nyquist frequency would not be represented in the spectrogram.
  - hop_length: The number of samples that each DFT/CQT/etc. jumps by.

  Returns:
  - bins: A 1-D array representing the frequency of each bin.
  - time: A 1-D array representing the time for each DFT/CQT.
  - power: A 2-D array representing the power for each bin at each time.
  """

  bins = None 
  time = None
  power = None
  if spec_type == "simple":
    dft_bins = num_bins
    # compensate for non power-of-two number of bins
    if (num_bins & (num_bins - 1)) != 0:
      dft_bins = 2 ** (num_bins.bit_length())
    samples_per_dft = dft_bins * 2
    overlap_length = samples_per_dft - hop_length
    bins, time, power = spectrogram(audio_data, fs=sample_rate, nperseg=samples_per_dft, noverlap=overlap_length)
    # delete lowest (0 Hz) bin, delete higher bins for non power-of-two number of bins
    bins = bins[1:1+num_bins]
    power = power[1:1+num_bins]
  elif spec_type == "cqt":
    # male voices go down to 100 Hz, so giving some slack
    fmin = 80
    power = np.abs(librosa.cqt(audio_data, sr=sample_rate, n_bins=num_bins, bins_per_octave=20, hop_length=hop_length, fmin=fmin))
    bins = np.linspace(0, power.shape[0], power.shape[0])
    # calculate time indices (linear)
    time = np.linspace(0, len(audio_data), power.shape[1])
  else:
    print("Error: Invalid value for spectrogram_choice argument \'spec_type\'!")
    exit()

  return bins, time, power

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

spec_type = "cqt"
bins, time, power = spectrogram_choice(audio_data, sample_rate=sample_rate, spec_type=spec_type, num_bins=100, hop_length=32)
plt.pcolormesh(time, bins, 10 * np.log10(power), shading='auto')
plt.title(f'Spectrogram: {spec_type}')
plt.xlabel('Time [s]')
plt.ylabel('Bin Label')
plt.colorbar(label='Power [dB]')
plt.show()
