import numpy as np
from scipy.signal import find_peaks
import math

def window(power: np.ndarray, amplitude: np.ndarray, algorithm: str) -> np.ndarray:
  """
  Takes in the power values (spectrogram) and amplitudes of the original waveform, 
  "crops" the spectrogram into a square image, e.g. 100x100 by applying some trigger condition/algorithm.

  Parameters:
  - power: The power values for the given spectrogram (2D).
  - amplitude: The initial audio signal (1D).
  - algorithm: The algorithm applied to window the data.

  Returns:
    The spectrogram as a square image, after applying the trigger condition/algorithm.

  TODO: Implement some algorithms as functions of power and/or amplitude. 
        Maybe a rolling average for power in some bin, or amplitude reaching some value, etc.
        Make sure it works, test it!
  """
  if algorithm == "start": # keep the leftmost pixels of the image ** this is not a "real" algorithm
    return power[:, :power.shape[0]]
  elif algorithm == "mid": # keep the middle pixels of the image ** this is not a "real" algorithm
    height, width = power.shape
    start_col = math.floor((width - height) / 2)
    return power[:, start_col:start_col+height]
  elif algorithm == "end": # keep the rightmost pixels of the image ** this is not a "real" algorithm
    return power[:, -power.shape[0]:]
  elif algorithm == "roll_power": # window based on a rolling average of power at fundamental frequency bins
    # implementation is strange but have to select the important bins manually for now...
    # ideally, pick bins that cover the fundamental frequencies of voice (100-250 Hz)
    # this should be very easy to do in hardware
    # TODO: parameterize the bin range that is used for rolling average
    selected_bins = power[2:6, :]
    power_sum = np.sum(selected_bins, axis=0)

    # 96 DFT rolling average of powers in the specified bins
    power_sum_roll = np.convolve(power_sum, np.ones(96), 'valid') / 96

    # peaks of the rolling average
    peak_indices, _ = find_peaks(power_sum_roll) # avoid neighboring peaks

    # get highest peak (real world this will just be getting a peak that exceeds some power)
    # could modify code to return the first peak exceeding some threshold to test
    peak_heights = power_sum_roll[peak_indices]
    highest_peak_idx = peak_indices[np.argmax(peak_heights)] + (power.shape[0] // 2) # rolling avg idx is offset from correct idx

    # crop the spectrogram centered at the power peak
    start_idx = highest_peak_idx - (power.shape[0] // 2)
    end_idx = start_idx + power.shape[0]
 
    # check for out of bounds
    if start_idx < 0:
      # this is not a good outcome
      print("Start index for \'roll_power\' windowing is below zero! Setting the start index to zero.")
      start_idx = 0
      end_idx = power.shape[0]
    elif end_idx >= power.shape[1]:
      # this is not a good outcome either
      print("End index for \'roll_power\' windowing is past the end of the spectrogram! Setting the end index to the end.")
      end_idx = power.shape[1] - 1
      start_idx = end_idx - power.shape[0]

    return power[:, start_idx:end_idx]

  else:
    print("Invalid argument for windowing!")
    exit()

def crop(audio_data: np.ndarray, time: float, sr: int) -> np.ndarray:
  """
  Takes in *unaltered* digit audio file and crops the bits of silence at the start and end,
  then zero-pads the audio file uniformly to the specified time period. Doing this "centers"
  all digits within the same number of samples, so no additional windowing needs to be performed.

  Parameters:
  - audio_data: The audio data to crop.
  - time: The time period for the resulting audio data post-cropping. 
          Note that input audio data that exceeds this time will throw an error.
  - sr: The sample rate of the input (and output) audio data.

  Returns:
    The cropped audio data, which is (time * sr) samples in size.
  """
  audio_data_sq = audio_data ** 2 # square audio data to make all positive (also bias towards higher amplitudes)
  audio_data_sq_roll = np.convolve(audio_data_sq, np.ones(100), 'valid') / 100 # 100 sample sliding window
  crop_cond = np.max(audio_data_sq_roll) / 10 # crop once 1/10th of max amplitude is reached

  # crop indices, note that each sample of the rolling avg is indexed 50 behind the respective index in the audio data
  left_crop_idx = 0
  right_crop_idx = audio_data_sq_roll.size - 1

  # find left side cutoff
  while True:
    if audio_data_sq_roll[left_crop_idx] > crop_cond:
      break
    left_crop_idx += 1
    if left_crop_idx >= audio_data_sq_roll.size:
      print("uh oh")
      exit()

  # find right side cutoff
  while True:
    if audio_data_sq_roll[right_crop_idx] > crop_cond:
      break
    right_crop_idx -= 1
    if right_crop_idx < 0:
      print("oh no")
      exit()

  # amount of time to still include before/after the crop condition
  slack_time = 0.1
  slack_samples = round(slack_time * sr)

  # slack_samples to the left of the (middle of) left crop window
  left_crop = left_crop_idx + 50 - slack_samples
  if left_crop < 0:
    left_crop = 0

  # slack_samples to the right of the (middle of) right crop window
  right_crop = right_crop_idx + 50 + slack_samples
  if right_crop >= audio_data.size:
    right_crop = audio_data.size - 1

  # 100 samples left, 100 samples right of trigger
  audio_data = audio_data[left_crop : right_crop]
  samples_required = time * sr

  # zero pad left & right uniformly
  zero_pad_left = np.zeros(math.ceil((samples_required - audio_data.size) / 2))
  zero_pad_right = np.zeros(math.floor((samples_required - audio_data.size) / 2))
  return np.concatenate((zero_pad_left, audio_data, zero_pad_right))
