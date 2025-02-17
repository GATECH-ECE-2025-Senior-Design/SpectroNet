import numpy as np
import math
import sys

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
  if algorithm == "end": # keep the rightmost pixels of the image ** this is temporary
    return power[:, -power.shape[0]:]
  elif algorithm == "mid": # keep the middle pixels of the image ** this is temporary
    height, width = power.shape
    start_col = (width - height) // 2
    return power[:, start_col:start_col+height]
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
  crop_cond = np.max(audio_data_sq_roll) / 10
  left_crop_idx = 0
  right_crop_idx = audio_data_sq_roll.size - 1

  while True:
    if audio_data_sq_roll[left_crop_idx] > crop_cond: # arbitrary cutoff
      break
    left_crop_idx += 1
    if left_crop_idx >= audio_data_sq_roll.size:
      np.set_printoptions(threshold=sys.maxsize)
      print(audio_data_sq_roll)
      print("uh oh")
      exit()

  while True:
    if audio_data_sq_roll[right_crop_idx] > crop_cond: # arbitrary cutoff
      break
    right_crop_idx -= 1
    if right_crop_idx < 0:
      print("oh no")
      exit()

  slack_time = 0.1
  slack_samples = round(slack_time * sr)
  left_crop = left_crop_idx + 50 - slack_samples # slack_samples to the left of the (middle of) left crop window
  if left_crop < 0:
    left_crop = 0
  right_crop = right_crop_idx + 50 + slack_samples # slack_samples to the right of the (middle of) right crop window
  if right_crop >= audio_data.size:
    right_crop = audio_data.size - 1

  audio_data = audio_data[left_crop : right_crop] # 100 samples left, 100 samples right of trigger
  # print((left_crop_idx, right_crop_idx))
  samples_required = time*sr
  zero_pad_left = np.zeros(math.ceil((samples_required - audio_data.size) / 2))
  zero_pad_right = np.zeros(math.floor((samples_required - audio_data.size) / 2))

  return np.concatenate((zero_pad_left, audio_data, zero_pad_right))
