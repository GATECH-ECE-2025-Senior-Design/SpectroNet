import os
import spectrogram as spec
import numpy as np
import argparse
import noise_integration
import windowing

# get folder paths
current_directory = os.path.dirname(os.path.realpath(__file__))
datasets_folder = images_folder = os.path.join(current_directory, "..", "datasets")
digits_folder = os.path.join(datasets_folder, "digits")

# make images folder
images_folder = os.path.join(datasets_folder, "images")
os.makedirs(images_folder, exist_ok=True)

# parse command line arguments
parser = argparse.ArgumentParser(description="A parser to check if the user wants background noise mixed in.")
parser.add_argument('--noise', action='store_true', default=False, help="To enable mixing background noise.")
parser.add_argument('--snr', type=int, default=12, help="Signal to noise ratio if background noise is enabled.")
parser.add_argument('--windowing', type=str, default="end", help="The algorithm used to trigger the CNN, i.e. pass a square spectrogram in.")
parser.add_argument('--sr', type=int, default=6000, help="Define sample rate of the audio signal.")
parser.add_argument('--spec_type', type=str, default="mel", help="Define which spectrogram type is generated.")
parser.add_argument('--resolution', type=int, default=96, help="Define resolution (square) of the spectrogram.")
parser.add_argument('--dtype', type=str, default="int16", help="Define datatype of the audio/spectrogram.")
parser.add_argument('--hop', type=int, default=32, help="Define hop length for taking DFT/CQT.")
args = parser.parse_args()

#TODO:  Maybe parameterize the number of speakers to generate spectrograms for? 
#       Spec generation currently takes a long time.

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

# walk the Audio MNIST dataset
for subdir, dirs, files in os.walk(digits_folder):
    for file in files:
      file_name, file_extension = os.path.splitext(file)
      # ignore the txt file
      if file_extension == ".wav":
        # read wav
        audio_data = spec.read_wav(os.path.join(subdir, file), target_sample_rate=args.sr, target_dtype=dtype)
        # optionally mix noise
        if (args.noise):
          audio_data = noise_integration.add_noise(audio_data, args.snr)
        # generate spectrogram
        bins, time, power = spec.spectrogram_choice(audio_data, sample_rate=args.sr, spec_type=args.spec_type, \
                                                    num_bins=args.resolution, hop_length=args.hop, target_dtype=dtype)
        # apply windowing (for square image)
        power = windowing.window(power, audio_data, args.windowing)
        # save np array file
        np.save(os.path.join(images_folder, (file_name + ".npy")), power)


# Noise stuff
if (args.noise == True):
  print("Adding noise to dataset...")
  noise_integration.integrate_noise(args.snr)