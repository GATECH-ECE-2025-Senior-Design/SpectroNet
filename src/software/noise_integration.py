import random
import os
from pydub import AudioSegment
from pydub.silence import detect_leading_silence
import threading
import socket
import numpy as np

# Run this file to integrate noise into the dataset - it currently is set to output a bunch of 
# noisy WAV files into datasets/noisy_digits with the SNR set below

# get folder paths
current_directory = os.path.dirname(os.path.realpath(__file__))
datasets_folder = os.path.join(current_directory, "..", "datasets")
digits_folder = os.path.join(datasets_folder, "digits")
noise_folder = os.path.join(datasets_folder, "noise")
noisy_digits_folder = os.path.join(datasets_folder, "noisy_digits")

if(socket.gethostname().find("linlab") != -1):
    noisy_digits_folder = "/usr/scratch/spectronet/noisy_digits"
    # print("linlab detected, using scratch folder")

if (os.path.exists(noisy_digits_folder) == False):
    os.makedirs(noisy_digits_folder)

def float32_to_fixed_point(arr, m, n):
    arr = arr.astype(np.float32)
    scale = 2 ** n
    fixed_point_array = np.round(arr * scale).astype(np.int32)
    max_val = (1 << (m + n - 1)) - 1
    min_val = - (1 << (m + n - 1))
    fixed_point_array = np.clip(fixed_point_array, min_val, max_val)
    return fixed_point_array

# Because the noise samples are considerably longer than the number samples
# I will clip a random portion of the noise sample and overlay the digit on it.
# I may also overlay a second noise sample, decided by random choice
def add_noise(digit_untrimmed: AudioSegment, SNR: int, num_noise_samples: int, verbose: bool, file: str, std_length: int) -> AudioSegment:
    """Adds (a) random sample(s) of background noise to a single audio file and removes silent padding from initial digit sample"""
    # Check argument first - throw an exception if it's something impossible
    if (num_noise_samples < 1):
        raise ValueError("Cannot add a non-positive amount of noise to the digit - num_noise_samples must be greater than 0")
    # Code to trim the silence from the beginning and end of the digit
    trim_leading_silence = lambda x: x[detect_leading_silence(x, -60) :]
    trim_trailing_silence = lambda x: trim_leading_silence(x.reverse()).reverse()
    strip_silence = lambda x: trim_trailing_silence(trim_leading_silence(x))
    digit_unpadded = strip_silence(digit_untrimmed)
    silence = AudioSegment.silent(duration=((std_length - len(digit_unpadded)) / 2), frame_rate=digit_unpadded.frame_rate)
    digit = silence + digit_unpadded + silence
    # Create the noise sample - overlay multiple noise samples on top of each other
    for i in range(num_noise_samples):
        noise_sample_num = random.randint(1,10)
        # choose a random noise sample
        noise_sample = AudioSegment.from_file(os.path.join(noise_folder, f'sample-{noise_sample_num}.webm'), format="webm")
        noise_sample_segment = noise_sample[:random.randint(0, len(noise_sample) - len(digit))]
        # print("Adding noise sample " + str(noise_sample_num) + " to " + file + ", SNR: " + str(SNR) + "dB")
        # Overlay it onto the existing noise, making sure that it follows the defined SNR
        if (i == 0):
            if ((noise_sample_segment.dBFS + SNR) > digit.dBFS):
                noise = noise_sample_segment + (digit.dBFS - noise_sample_segment.dBFS - SNR)
                if ((digit.dBFS - noise_sample_segment.dBFS - SNR) > 0):
                    raise Exception("you're cooked lil bro")
            else:
                noise = noise_sample_segment
        else:
            if ((noise_sample_segment.dBFS + SNR) > digit.dBFS):
                noise = noise.overlay(noise_sample_segment,
                                        gain_during_overlay = (digit.dBFS - noise_sample.dBFS - SNR))
            else:
                noise = noise.overlay(noise_sample_segment)
    
    return digit.overlay(noise)
        

    

# Add noise to all the files in a digits folder
# Output the noisy files to datasets/noisy_digits/{num}
def make_noisy_folder(path: str, SNR: int, num_noise_samples: int, verbose, len: int):
      noisy_digits_subfolder = os.path.join(noisy_digits_folder, os.path.basename(os.path.normpath(path)))
      if (os.path.exists(noisy_digits_subfolder) == False):
          os.mkdir(noisy_digits_subfolder)
      for file in os.listdir(path):
          digit = AudioSegment.from_file(os.path.normpath(os.path.join(path,file)))
          noisy_digit = add_noise(digit, SNR, num_noise_samples, verbose, file, len)
          noisy_digit_path = os.path.join(noisy_digits_subfolder, os.path.basename(file))
          noisy_digit.export(noisy_digit_path, format="wav", bitrate="768k", parameters=['-f', 'f32le'])


def integrate_noise(SNR: int, num_noise_samples: int, verbose: bool, len: int):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    datasets_folder = os.path.join(current_directory, "..", "datasets")
    digits_folder = os.path.join(datasets_folder, "digits")
    noise_folder = os.path.join(datasets_folder, "noise")
    noisy_digits_folder = os.path.join(datasets_folder, "noisy_digits")

    if(socket.gethostname().find("linlab") != -1):
        noisy_digits_folder = "/usr/scratch/spectronet/noisy_digits"
        print("linlab detected, using scratch folder")

    if (os.path.exists(noisy_digits_folder) == False):
        os.makedirs(noisy_digits_folder)

    """Creates a new dataset by integrating (a) randomly chosen
    sample(s) of noise into the existing digit dataset

    New dataset can be found in src/datasets/noisy_digits

    NOTE: Takes quite a while to run"""
    threads = []
    i = 0
    # Loop through all the folders and create a noisy dataset
    for subdir in os.listdir(digits_folder):
        folder = os.path.join(digits_folder, subdir)
        threads.append(threading.Thread(target=make_noisy_folder, args=(folder, SNR, num_noise_samples, verbose, len)))
        threads[i].start()
        i += 1

    # The actually multithreaded part
    i = 0
    for thread in threads:
        threads[i].join()
        i += 1

def integrate_noise_for_one_folder(SNR: int, num_noise_samples: int, verbose: bool, len: int, input_folder, output_folder):
    assert len >= 880, "Digit length must be greater than 880 ms"
    noisy_digits_folder = output_folder
    for file in os.listdir(input_folder):
          digit = AudioSegment.from_file(os.path.normpath(os.path.join(input_folder,file)))
          noisy_digit = add_noise(digit, SNR, num_noise_samples, verbose, file, len)
          noisy_digit_path = os.path.join(output_folder, os.path.basename(file))
          noisy_digit.export(noisy_digit_path, format="wav", bitrate="768k", parameters=['-f', 's16le'])