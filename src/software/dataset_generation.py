import os
import spectrogram as spec
import numpy as np
import argparse
import noise_integration

# get folder paths
current_directory = os.path.dirname(os.path.realpath(__file__))
datasets_folder = images_folder = os.path.join(current_directory, "..", "datasets")
digits_folder = os.path.join(datasets_folder, "digits")

# make images folder
images_folder = os.path.join(datasets_folder, "images")
os.makedirs(images_folder, exist_ok=True)

# parse command line arguments
parser = argparse.ArgumentParser(description="A parser to check if the user wants background noise mixed in.")
parser.add_argument('--noise', action='store_true', default=False, help="Set to True to log in.")
parser.add_argument('--snr', type=int, default=None, help="Signal to noise ratio if background noise is enabled.")
args = parser.parse_args()

# TODO: Add runtime arguments for bins, hop size, quantization, etc. -- currently hard-coded
# Also parameterize the number of speakers/samples to process, currently takes a very long time to process all samples

# walk the Audio MNIST dataset
for subdir, dirs, files in os.walk(digits_folder):
    for file in files:
      file_name, file_extension = os.path.splitext(file)
      # ignore the txt file
      if file_extension == ".wav":
        # read wav
        audio_data = spec.read_wav(os.path.join(subdir, file), target_sample_rate=6000, target_dtype=np.int16)
        # optionally mix noise
        if (args.noise):
          audio_data = noise_integration.add_noise(audio_data, args.snr)
        # generate spectrogram
        bins, time, power = spec.spectrogram_choice(audio_data, sample_rate=6000, spec_type="cqt", num_bins=100, hop_length=32, target_dtype=np.int16)
        # save np array file
        np.save(os.path.join(images_folder, (file_name + ".npy")), power)