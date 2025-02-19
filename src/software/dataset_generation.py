import spectrogram as spec
import numpy as np
import noise_integration
import windowing
import argparse
import librosa
import math
import os
# debug
# import matplotlib.pyplot as plt

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
parser.add_argument('--crop', action='store_true', default=False, help="Crops audio, then pads left & right to desired time. Use with windowing=mid")
parser.add_argument('--windowing', type=str, default="mid", help="The algorithm used to trigger the CNN, i.e. pass a square spectrogram in.")
parser.add_argument('--sr', type=int, default=8000, help="Define sample rate of the audio signal.")
parser.add_argument('--spec_type', type=str, default="simple", help="Define which spectrogram type is generated.")
parser.add_argument('--resolution', type=int, default=96, help="Define resolution (square) of the spectrogram.")
parser.add_argument('--dtype', type=str, default="float32", help="Define datatype of the audio/spectrogram.")
parser.add_argument('--time', type=float, default=1, help="Define the time period that is included in a spectrogram.")
parser.add_argument('-v', '--verbose', action='store_true', default=False, help="Verbose output to console.")
parser.add_argument('--noise_samples', type=int, default=1, help="Define number of noise samples to overlay on each digit.")
parser.add_argument('--samples_per_dft', type=int, default=256, help="Number of samples used for each DFT.")
parser.add_argument('--time_min', type=float, default=1, help="The minimum time length for input files, files below this are zero-padded.")
args = parser.parse_args()

# TODO: Maybe parameterize the number of speakers to generate spectrograms for? 
#       Spec generation currently takes a long time.

num_samples_per_square = args.time * args.sr # total number of samples contained by a square spectrogram
hop_length = 0 # calculate below

# determine hop length based on time parameter
if args.spec_type == "simple":

  # total number of samples minus the first dft
  num_hop_samples_per_square = num_samples_per_square - args.samples_per_dft

  # calculate hop length to cover remaining samples with remaining DFTs
  # floor rounding could cause a slightly wider than square image, if so just chop off first/last couple DFTs.
  hop_length = math.floor(num_hop_samples_per_square / (args.resolution - 1))

elif args.spec_type == "cqt":
  
  # total number of samples minus the first dft
  num_hop_samples_per_square = num_samples_per_square - args.samples_per_dft

  # calculate hop length to cover remaining samples with remaining DFTs
  # floor rounding could cause a slightly wider than square image, if so just chop off first/last couple DFTs.
  hop_length = math.floor(num_hop_samples_per_square / (args.resolution - 1))

elif args.spec_type == "mel":
  
  # total number of samples minus the first dft
  num_hop_samples_per_square = num_samples_per_square - args.samples_per_dft

  # calculate hop length to cover remaining samples with remaining DFTs
  # somehow ceil rounding doesn't overshoot the hop length??
  hop_length = math.ceil(num_hop_samples_per_square / (args.resolution - 1))

# get datatype argument in usable form
dtype = np.dtype(args.dtype).type

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
        audio_data = spec.read_wav(os.path.join(subdir, file), target_sample_rate=args.sr, \
                                   target_dtype=dtype, time_min=args.time_min)    
        # apply cropping if specified
        if args.crop:
          audio_data = windowing.crop(audio_data, args.time, args.sr)
        # generate spectrogram
        bins, time, power = spec.spectrogram_choice(audio_data, sample_rate=args.sr, spec_type=args.spec_type, \
                                                    resolution=args.resolution, hop_length=hop_length, \
                                                    target_dtype=dtype, samples_per_dft=args.samples_per_dft)
        
        # apply windowing (for a square image)
        if not args.crop:
          power = windowing.window(power, audio_data, args.windowing)
        else:
          # cropping might produce slightly wide images, just crop the sides off
          power = windowing.window(power, audio_data, "mid")

        # save as dB power instead of absolute power
        power_dB = librosa.power_to_db(power, ref=np.max)

        # debug
        # plt.pcolormesh(time[:bins.shape[0]], bins, power_dB, shading='auto')
        # plt.show()

        # save np array file
        np.save(os.path.join(images_folder, (file_name + ".npy")), power_dB)