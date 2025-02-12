import numpy as np
import matplotlib.pyplot as plt
import os
import librosa
from scipy.io import wavfile
from scipy.signal import spectrogram
from scipy.signal import resample_poly
import warnings

# block out librosa warning for CQT
warnings.filterwarnings("ignore", category=UserWarning, module="librosa")

def read_wav(file_path, target_sample_rate=8000, target_dtype=np.int16, time_min=0.5):
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

  samples_min = round(time_min * target_sample_rate) # minimum number of samples given minimum time
  if len(audio_data) < samples_min:
    zero_pad = np.zeros(samples_min - len(audio_data)) # create min number of extra samples
    audio_data = np.concatenate((zero_pad, audio_data)) # zero pad before the audio sample

  # convert to target quantization
  if target_dtype != audio_data.dtype:
    audio_data = audio_data.astype(target_dtype)

  return audio_data

def spectrogram_choice(audio_data, sample_rate=8000, spec_type="simple", num_bins=128, \
                       hop_length=32, target_dtype=np.int16):
  """
  Generates a square aspect-ratio spectrogram of the input waveform as defined by the function parameters.

  Parameters:
  - audio_data: The audio data as an array.
  - sample_rate: The sample rate of the audio data.
  - spec_type: The "type" of spectrogram to be generated. {"simple", "cqt", "mel"}.
  - bins: The resolution of the output image. 
    For DFTs, a non power-of-two number of bins will result in a larger DFT, 
    with uppermost bins being truncated. Thus, Nyquist frequency would not be represented in the spectrogram.
  - hop_length: The number of samples that each DFT/CQT/etc. jumps by.

  Returns:
  - bins: A 1-D array representing the frequency of each bin.
  - time: A 1-D array representing the time for each DFT/CQT.
  - power: A 2-D array representing the power for each bin at each time.
  
  TODO: parameterize min-max bin frequencies for cqt & mel spectrograms.
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
    bins, time, power = spectrogram(audio_data, fs=sample_rate, nperseg=samples_per_dft, \
                                    noverlap=overlap_length)
    # delete lowest (0 Hz) bin, delete higher bins for non power-of-two number of bins
    bins = bins[1:1+num_bins]
    power = power[1:1+num_bins]
  elif spec_type == "cqt":
    # male voices go down to 100 Hz, so giving some slack
    fmin = 80
    bins_per_octave = 20
    # librosa only accepts floats, so recast
    audio_data = audio_data.astype(np.float32)
    power = np.abs(librosa.cqt(audio_data, sr=sample_rate, n_bins=num_bins, \
                               bins_per_octave=bins_per_octave, hop_length=hop_length, fmin=fmin))
    # calculate frequency bins
    octave_ratio = 2 ** (1 / bins_per_octave)
    bins = [fmin * (octave_ratio ** i) for i in range(num_bins)]
    # calculate time indices (linear)
    time = np.linspace(0, len(audio_data), power.shape[1])
  elif spec_type == "mel":
    fmin = 40
    fmax = 3000
    n_mels = num_bins
    hop_length = hop_length
    n_fft = 1024 # samples per fft -> output bins = n_fft/2 + 1
    # librosa only accepts floats, so recast
    audio_data = audio_data.astype(np.float32)
    power = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate, n_mels=n_mels, \
                                           fmin=fmin, fmax=fmax, hop_length=hop_length, n_fft=n_fft)
    # bin indices (linear)
    bins = np.linspace(0, power.shape[0], power.shape[0])
    # calculate time indices (linear)
    time = np.linspace(0, len(audio_data), power.shape[1])
    # print(power.shape)
  else:
    print("Error: Invalid value for spectrogram_choice argument \'spec_type\'!")
    exit()
  
  # (re)cast to desired type
  if target_dtype != power.dtype:
    power = power.astype(target_dtype)

  return bins, time, power

########
# TEST #
########

# spec_type = "mel"
# sample_rate = 8000
# dtype = np.int32
# current_dir = os.path.dirname(os.path.abspath(__file__))
# audio_data = read_wav(os.path.join(current_dir, "..", "datasets", "digits", "01", "0_01_0.wav"), \
#                       target_sample_rate=sample_rate, target_dtype=dtype)

# plt.figure(figsize=(10, 4))
# plt.plot(audio_data)
# plt.title(f"Audio Waveform - {sample_rate} Hz")
# plt.xlabel('Sample Index')
# plt.ylabel('Amplitude')
# plt.grid(True)
# plt.show()

# bins, time, power = spectrogram_choice(audio_data, sample_rate=sample_rate, spec_type=spec_type, \
#                                        num_bins=100, hop_length=32, target_dtype=dtype)
# print(len(time))
# if (spec_type == 'mel'):
#   plt.pcolormesh(time, bins, (power), shading='auto')
# else:
#   power_dB = librosa.power_to_db(power, ref=np.max)

# plt.pcolormesh(time, bins, power_dB, shading='auto')
# plt.title(f'Spectrogram: {spec_type}')
# plt.xlabel('Time [s]')
# plt.ylabel('Bin Label')
# plt.colorbar(label='Power [dB]')
# plt.show()

