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

# make images folder
images_folder = os.path.join(datasets_folder, "images")
os.makedirs(images_folder, exist_ok=True)

# parse command line arguments
parser = argparse.ArgumentParser(description="A parser to check if the user wants background noise mixed in.")
parser.add_argument('--enable_noise', action='store_true', default=False, help="To enable mixing background noise.")
parser.add_argument('--snr', type=int, default=12, help="Signal to noise ratio if background noise is enabled.")
parser.add_argument('--crop', action='store_true', default=False, help="Crops audio, then pads left & right to desired time. Use with windowing=mid")
parser.add_argument('--windowing', type=str, default="mid", help="The algorithm used to create a square spectrogram.")
parser.add_argument('--sr', type=int, default=8000, help="Define sample rate of the audio signal.")
parser.add_argument('--spec_type', type=str, default="simple", help="Define which spectrogram type is generated.")
parser.add_argument('--resolution', type=int, default=96, help="Define resolution (square) of the spectrogram.")
parser.add_argument('--dtype', type=str, default="float32", help="Define datatype of the audio/spectrogram.")
parser.add_argument('--time', type=float, default=1, help="Define the time period that is included in a spectrogram.")
parser.add_argument('-v', '--verbose', action='store_true', default=False, help="Verbose output to console.")
parser.add_argument('--noise_samples', type=int, default=1, help="Number of noise samples to overlay on each digit.")
parser.add_argument('--samples_per_dft', type=int, default=256, help="Number of samples used for each DFT.")
# Add new arguments for specifying dataset paths
parser.add_argument('--input_dir', type=str, default="../datasets/digits", help="Directory containing raw .wav files.")
parser.add_argument('--output_dir', type=str, default="../datasets/images", help="Directory to save generated spectrograms.")
args = parser.parse_args()

# Ensure input directory exists
if not os.path.exists(args.input_dir):
    raise FileNotFoundError(f"❌ Error: Input directory '{args.input_dir}' does not exist!")

# Ensure output directory exists
os.makedirs(args.output_dir, exist_ok=True)  # ✅ Create output directory if it doesn't exist

# ✅ Assigning directories
digits_folder = args.input_dir  # Use CLI argument for dataset path
images_folder = args.output_dir  # Use CLI argument for spectrograms

# ------------------------------------------------------------------------
# 🆕 Recursively find .wav files in digits_folder (subfolders included)
# ------------------------------------------------------------------------
all_wav_paths = []
for root, dirs, files in os.walk(digits_folder):
    for file in files:
        if file.endswith(".wav"):
            full_path = os.path.join(root, file)
            all_wav_paths.append(full_path)

if not all_wav_paths:
    raise FileNotFoundError(f"❌ Error: No .wav files found in '{digits_folder}' (including subfolders)!")

print(f"🔍 Found {len(all_wav_paths)} .wav files in {digits_folder} (recursively).")
print(f"📂 Spectrograms will be saved in {images_folder}")

# TODO: Maybe parameterize the number of speakers to generate spectrograms for? 
#       Spec generation currently takes a long time.

num_samples_per_square = args.time * args.sr  # total samples for a square spectrogram
hop_length = 0  # Will calculate below

# determine hop length based on time parameter
if args.spec_type == "simple":
    # total number of samples minus the first dft
    num_hop_samples_per_square = num_samples_per_square - args.samples_per_dft
    hop_length = max(1, math.floor(num_hop_samples_per_square / (args.resolution - 1)))

elif args.spec_type == "cqt":
    num_hop_samples_per_square = num_samples_per_square - args.samples_per_dft
    hop_length = max(1, math.floor(num_hop_samples_per_square / (args.resolution - 1)))

elif args.spec_type == "mel":
    num_hop_samples_per_square = num_samples_per_square - args.samples_per_dft
    # For mel, we often do ceil
    hop_length = max(1, math.ceil(num_hop_samples_per_square / (args.resolution - 1)))

# get dtype argument in usable form
dtype = np.dtype(args.dtype).type

# If noise is enabled, run noise_integration
if args.enable_noise:
    noise_integration.integrate_noise(args.snr, args.noise_samples, args.verbose)
    digits_folder = "/Users/padmamithra/Downloads/SpectroNet/src/datasets/noisy_digits"
    # (But note: you may also want to recrawl the new folder if you are actually using it.)

# Walk all .wav files we found
for wav_path in all_wav_paths:
    file_name, file_extension = os.path.splitext(os.path.basename(wav_path))
    if file_extension.lower() == ".wav":
        # read wav
        audio_data = spec.read_wav(wav_path, target_sample_rate=args.sr, target_dtype=dtype)

        # apply cropping if specified
        if args.crop:
            audio_data = windowing.crop(audio_data, args.time, args.sr)

        # generate spectrogram
        bins, times, power = spec.spectrogram_choice(
            audio_data,
            sample_rate=args.sr,
            spec_type=args.spec_type,
            resolution=args.resolution,
            hop_length=hop_length,
            target_dtype=dtype,
            samples_per_dft=args.samples_per_dft
        )

        # apply windowing (for a square image)
        if not args.crop:
            power = windowing.window(power, audio_data, args.windowing)
        else:
            # cropping might produce slightly wide images, so just crop
            power = windowing.window(power, audio_data, "mid")

        # convert power to decibels
        power_dB = librosa.power_to_db(power, ref=np.max)

        # save .npy
        out_path = os.path.join(images_folder, (file_name + ".npy"))
        np.save(out_path, power_dB)

print(f"✅ Done generating spectrograms for {len(all_wav_paths)} WAV files.")