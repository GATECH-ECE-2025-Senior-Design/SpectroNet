import os
import spectrogram as spec
import numpy as np
import argparse
import noise_integration
import windowing
import math
import matplotlib.pyplot as plt
import librosa

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
parser.add_argument('--dtype', type=str, default="int16", help="Define datatype of the audio/spectrogram.")
parser.add_argument('--time', type=float, default=1, help="Define the time period that is included in a spectrogram.")
parser.add_argument('-v', '--verbose', action='store_true', default=False, help="Verbose output to console.")
parser.add_argument('--noise_samples', type=int, default=1, help="Define number of noise samples to overlay on each digit.")
parser.add_argument('--samples_per_dft', type=int, default=256, help="Number of samples used for each DFT.")
args = parser.parse_args()

#TODO:  Maybe parameterize the number of speakers to generate spectrograms for? 
#       Spec generation currently takes a long time.

num_samples_per_square = args.time * args.sr # total number of samples contained by square spectrogram
hop_length = 0 # calculate below

# Determine hop length based on time parameter
if args.spec_type == "simple":
  num_hop_samples_per_square = num_samples_per_square - args.samples_per_dft # total number of samples minus the first dft
  # num_hop_samples_per_square -= 2 * (args.samples_per_dft - 1)  # Also subtract two (DFT - 1) from left & right, 
                                                                # for left & right samples to be fully included in spectrogram
  hop_length = math.floor(num_hop_samples_per_square / (args.resolution - 1)) # calculate hop length to cover specified time
elif args.spec_type == "cqt":
  print("Not yet implemented.")
  exit()
elif args.spec_type == "mel":
  num_hop_samples_per_square = num_samples_per_square - args.samples_per_dft # total number of samples minus the first dft
  num_hop_samples_per_square -= 2 * (args.samples_per_dft - 1)  # Also subtract two (DFT - 1) from left & right, 
                                                                # for left & right samples to be fully included in spectrogram
  hop_length = math.ceil(num_hop_samples_per_square / (args.resolution - 1)) # calculate hop length to cover specified time

# Choose datatype (hard-coded, sorry)
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
        audio_data = spec.read_wav(os.path.join(subdir, file), target_sample_rate=args.sr, target_dtype=dtype)    
        # plt.plot(audio_data)
        # plt.show()
        # print(audio_data.size)
        if args.crop:
          audio_data = windowing.crop(audio_data, args.time, args.sr)
        # print(audio_data.size)
        # generate spectrogram
        bins, time, power = spec.spectrogram_choice(audio_data, sample_rate=args.sr, spec_type=args.spec_type, \
                                                    resolution=args.resolution, hop_length=hop_length, \
                                                    target_dtype=dtype, samples_per_dft=args.samples_per_dft)
        # print(power.shape)
        # plt.imshow(power, cmap='hot', interpolation='none')
        # plt.show()
        # apply windowing (for square image)
        if not args.crop:
          power = windowing.window(power, audio_data, args.windowing)
        # save as dB power instead of absolute power
        power_dB = librosa.power_to_db(power, ref=np.max)
        # save np array file
        np.save(os.path.join(images_folder, (file_name + ".npy")), power_dB)