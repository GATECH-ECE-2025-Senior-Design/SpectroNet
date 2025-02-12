import os
import spectrogram as spec
import numpy as np
import argparse
import noise_integration
import windowing
import math

# get folder paths
current_directory = os.path.dirname(os.path.realpath(__file__))
datasets_folder = images_folder = os.path.join(current_directory, "..", "datasets")
digits_folder = os.path.join(datasets_folder, "digits")

# make images folder
images_folder = os.path.join(datasets_folder, "images")
os.makedirs(images_folder, exist_ok=True)

# parse command line arguments
parser = argparse.ArgumentParser(description="A parser to check if the user wants background noise mixed in.")
parser.add_argument('--enable_noise', action='store_true', default=False, help="To enable mixing background noise.")
parser.add_argument('--snr', type=int, default=12, help="Signal to noise ratio if background noise is enabled.")
parser.add_argument('--windowing', type=str, default="end", help="The algorithm used to trigger the CNN, i.e. pass a square spectrogram in.")
parser.add_argument('--sr', type=int, default=6000, help="Define sample rate of the audio signal.")
parser.add_argument('--spec_type', type=str, default="mel", help="Define which spectrogram type is generated.")
parser.add_argument('--resolution', type=int, default=96, help="Define resolution (square) of the spectrogram.")
parser.add_argument('--dtype', type=str, default="int16", help="Define datatype of the audio/spectrogram.")
parser.add_argument('--time', type=float, default=0.5, help="Define the time period that is included in a spectrogram.")
parser.add_argument('-v', '--verbose', action='store_true', default=False, help="Verbose output to console.")
parser.add_argument('--noise_samples', type=int, default=1, help="Define number of noise samples to overlay on each digit.")
args = parser.parse_args()

#TODO:  Maybe parameterize the number of speakers to generate spectrograms for? 
#       Spec generation currently takes a long time.

num_samples_per_square = args.time * args.sr # total number of samples contained by square spectrogram
hop_length = 0 # calculate below
# Determine hop length based on time parameter
if args.spec_type == "simple":
  dft_bins = 2 ** (args.resolution.bit_length()) # same code as in spectrogram.py
  samples_per_dft = dft_bins * 2 # same code as in spectrogram.py
  num_hop_samples_per_square = num_samples_per_square - samples_per_dft # total number of samples minus the first dft
  hop_length = math.ceil(num_hop_samples_per_square / (args.resolution - 1))
elif args.spec_type == "cqt":
  print("Not yet implemented.")
  exit()
elif args.spec_type == "mel":
  n_fft = 1024 # same code as in spectrogram.py
  num_hop_samples_per_square = num_samples_per_square - n_fft # total number of samples minus the first dft
  hop_length = math.ceil(num_hop_samples_per_square / (args.resolution - 1))

# Choose datatype (hard-coded, sorry)
dtype = None
if args.dtype == "int8":
  dtype = np.int8
elif args.dtype == "int16":
  dtype = np.int16
elif args.dtype == "int32":
  dtype = np.int32
elif args.dtype == "fp8":
  dtype = np.float8
elif args.dtype == "fp16":
  dtype = np.float16
elif args.dtype == "fp32":
  dtype = np.float32
else:
  print("Invalid argument \'dtype\'!")
  exit()

# Run the noise integration separately from the rest of the dataset
# Notes: noise gen preserves sample rate of digit, resamples noise
# should it have a different sample rate from the digit
if (args.enable_noise):
  noise_integration.integrate_noise(args.snr, args.noise_samples, args.verbose)
  digits_folder = os.path.join(datasets_folder, "noisy_digits")

# walk the Audio MNIST dataset
for subdir, dirs, files in os.walk(digits_folder):
    for file in files:
      file_name, file_extension = os.path.splitext(file)
      # ignore the txt file
      if file_extension == ".wav":
        # read wav
        audio_data = spec.read_wav(os.path.join(subdir, file), target_sample_rate=args.sr, target_dtype=dtype)       
        # generate spectrogram
        bins, time, power = spec.spectrogram_choice(audio_data, sample_rate=args.sr, spec_type=args.spec_type, \
                                                    num_bins=args.resolution, hop_length=hop_length, target_dtype=dtype)
        # apply windowing (for square image)
        power = windowing.window(power, audio_data, args.windowing)
        # save np array file
        np.save(os.path.join(images_folder, (file_name + ".npy")), power)