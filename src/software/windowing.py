import numpy as np

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
  if algorithm == "end": # keep the rightmost pixels of the image
    return power[:, -power.shape[0]:]
  else:
    print("Invalid argument for windowing!")
    exit()