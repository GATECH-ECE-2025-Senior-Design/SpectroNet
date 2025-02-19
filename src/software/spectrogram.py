from scipy.io import wavfile
from scipy.signal import spectrogram
from scipy.signal import resample_poly
import numpy as np
import librosa
import warnings
import math

# block out librosa warning for CQT
warnings.filterwarnings("ignore", category=UserWarning, module="librosa")

def read_wav(file_path, target_sample_rate=8000, target_dtype=np.int16, time_min=0.8, normalize=1023):
  """
  Reads .wav file specified by path, decimates to specified sample rate and quantizes to specified precision.
  Returns the audio as an array.

  Parameters:
  - file_path: The path to the .wav file.
  - target_sample_rate: The targeted sample_rate.
  - target_dtype: The targeted data type.
  - time_min: The minimum expected time for the audio file.
              If the audio file does not meet this requirement, zero-padding is added before the data.
  - normalize: The amplitude in which the audio file is normalized to.
               This means the maximum amplitude of the returned audio data is equal to the 'normalize' value

  Returns:
    The audio data as an array of the target data type.
  """

  sample_rate, audio_data = wavfile.read(file_path)

  # resample to target sample rate if sample rates are different
  if target_sample_rate != sample_rate:
    audio_data = resample_poly(audio_data, target_sample_rate, sample_rate)

  # if the audio data is too small in time length, zero-pad the start
  samples_min = round(time_min * target_sample_rate) # min number of samples given min time
  if len(audio_data) < samples_min:
    # TODO: maybe add an option to pad with gaussian white noise?
    zero_pad = np.zeros((samples_min - len(audio_data)) // 2) # create min number of extra samples
    audio_data = np.concatenate((zero_pad, audio_data, zero_pad)) # zero pad before the audio sample

  # normalize based on peak amplitude
  amp_max_abs = max(abs(np.min(audio_data)), np.max(audio_data))
  normalize_coeff = normalize / amp_max_abs
  audio_data *= normalize_coeff
    
  # convert to target quantization
  if target_dtype != audio_data.dtype:
    audio_data = audio_data.astype(target_dtype)

  return audio_data

def spectrogram_choice(audio_data, sample_rate=8000, spec_type="simple", resolution=128, \
                       hop_length=32, target_dtype=np.int16, samples_per_dft=256):
  """
  Generates a square aspect-ratio spectrogram of the input waveform as defined by the function parameters.

  Parameters:
  - audio_data: The audio data as an array.
  - sample_rate: The sample rate of the audio data.
  - spec_type: The "type" of spectrogram to be generated. {"simple", "cqt", "mel"}.
  - resolution: The resolution of the output image. 
                For DFTs, a non power-of-two number of bins will result in a larger DFT, 
                with uppermost bins being truncated. Thus, Nyquist frequency would not be represented in the spectrogram.
  - hop_length: The number of samples that each DFT/CQT/etc. jumps by.
  - target_dtype: The targeted datatype for the output spectrogram.
  - samples_per_dft: The number of samples included in a given DFT. Note that samples_per_dft = (bins - 1) * 2

  Returns:
  - bins: A 1-D array representing the frequency of each bin.
  - time: A 1-D array representing the time for each DFT/CQT.
  - power: A 2-D array representing the power for each bin at each time.

  Note that for only 'power' is necessary as an input to the CNN, 'bins' and 'time' are just axis labels.
  
  TODO: parameterize min-max bin frequencies for cqt & mel spectrograms.
  """

  if resolution > (samples_per_dft / 2 + 1):
    print(f"A spectrogram with N samples per DFT yields a DFT with N/2 + 1 bins. The resolution={resolution} is too high for samples_per_dft={samples_per_dft}.")

  bins = None 
  time = None
  power = None

  if spec_type == "simple":

    # calculate DFT overlap
    overlap_length = samples_per_dft - hop_length
    bins, time, power = spectrogram(audio_data, fs=sample_rate, nperseg=samples_per_dft, \
                                    noverlap=overlap_length)
    
    # delete lowest (0 Hz) bin, delete higher bins if resolution != number of output bins for DFT
    if (resolution != power.shape[0]):
      bins = bins[1:1+resolution]
      power = power[1:1+resolution]

  elif spec_type == "cqt":

    # male voices go down to 100 Hz, but giving some slack
    fmin = 60
    bins_per_octave = 20 # if resolution = 100, fmax = 60 * 2^5 = 1920

    # librosa only accepts floats, so recast
    audio_data = audio_data.astype(np.float32)
    power = np.abs(librosa.cqt(audio_data, sr=sample_rate, n_bins=resolution, \
                               bins_per_octave=bins_per_octave, hop_length=hop_length, fmin=fmin))
    
    # calculate frequency bins
    octave_ratio = 2 ** (1 / bins_per_octave)
    bins = [fmin * (octave_ratio ** i) for i in range(resolution)]
    bins = np.array(bins, dtype=int)

    # calculate time indices (linear)
    time = np.linspace(0, len(audio_data), power.shape[1])

  elif spec_type == "mel":

    fmin = 0
    fmax = sample_rate // 2
    n_mels = resolution
    hop_length = hop_length

    # librosa only accepts floats, so recast
    audio_data = audio_data.astype(np.float32)
    power = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate, n_mels=n_mels, fmin=fmin, \
                                           fmax=fmax, hop_length=hop_length, n_fft=samples_per_dft)
    
    # bin indices (linear)
    bins = np.linspace(0, power.shape[0], power.shape[0])

    # calculate time indices (linear)
    time = np.linspace(0, len(audio_data), power.shape[1])

  else:
    print("Error: Invalid value for spectrogram_choice argument \'spec_type\'!")
    exit()
  
  # (re)cast to desired type
  if target_dtype != power.dtype:
    power = power.astype(target_dtype)

  return bins, time, power
