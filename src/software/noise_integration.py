import random
import os
from pydub import AudioSegment
from pydub.silence import detect_leading_silence
import threading

# Run this file to integrate noise into the dataset - it currently is set to output a bunch of 
# noisy WAV files into datasets/noisy_digits with the SNR set below

# get folder paths
current_directory = os.path.dirname(os.path.realpath(__file__))
datasets_folder = os.path.join(current_directory, "..", "datasets")
digits_folder = os.path.join(datasets_folder, "digits")
noise_folder = os.path.join(datasets_folder, "noise")
noisy_digits_folder = os.path.join(datasets_folder, "noisy_digits")

if (os.path.exists(noisy_digits_folder) == False):
    os.mkdir(noisy_digits_folder)


# Because the noise samples are considerably longer than the number samples
# I will clip a random portion of the noise sample and overlay the digit on it.
# I may also overlay a second noise sample, decided by random choice
def add_noise(digit_untrimmed: AudioSegment, SNR: int, num_noise_samples: int, verbose: bool, file: str) -> AudioSegment:
    """Adds (a) random sample(s) of background noise to a single audio file and removes silent padding from initial digit sample"""
    # Check argument first - throw an exception if it's something impossible
    if (num_noise_samples < 1):
        raise ValueError("Cannot add a non-positive amount of noise to the digit - num_noise_samples must be greater than 0")
    # Code to trim the silence from the beginning and end of the digit
    # Reference used: https://stackoverflow.com/a/69331596
    trim_leading_silence = lambda x: x[detect_leading_silence(x) :]
    trim_trailing_silence = lambda x: trim_leading_silence(x.reverse()).reverse()
    strip_silence = lambda x: trim_trailing_silence(trim_leading_silence(x))
    digit : AudioSegment = strip_silence(digit_untrimmed)
    noise: AudioSegment

    # Create the noise sample - overlay multiple noise samples on top of each other
    for i in range(num_noise_samples):
        noise_sample_num = random.randint(1,10)
        # choose a random noise sample
        noise_sample = AudioSegment.from_file(os.path.join(noise_folder, f'sample-{noise_sample_num}.webm'), format="webm")
        print("Adding noise sample " + noise_sample_num + "to " + file + ", SNR: " + SNR + "dB")
        # Overlay it onto the existing noise, making sure that it follows the defined SNR
        if ((noise_sample.dBFS + SNR) > digit.dBFS):
            noise = noise.overlay(noise_sample[:random.randint(0, len(noise_sample) - len(digit))],
                                    gain_during_overlay = (noise_sample.dBFS - digit.dBFS + SNR))
        else:
            noise = noise.overlay(noise_sample[:random.randint(0, len(noise_sample) - len(digit))])
    
    return digit.overlay(noise)
        

    

# Add noise to all the files in a digits folder
# Output the noisy files to datasets/noisy_digits/{num}
def make_noisy_folder(path: str, SNR: int, num_noise_samples: int, verbose):
      noisy_digits_subfolder = os.path.join(noisy_digits_folder, os.path.basename(os.path.normpath(path)))
      if (os.path.exists(noisy_digits_subfolder) == False):
          os.mkdir(noisy_digits_subfolder)
      for file in os.listdir(path):
          digit = AudioSegment.from_file(os.path.normpath(os.path.join(path,file)))
          noisy_digit = add_noise(digit, SNR, num_noise_samples, verbose, file)
          noisy_digit_path = os.path.join(noisy_digits_subfolder, os.path.basename(file))
          noisy_digit.export(noisy_digit_path, format="wav")


def integrate_noise(SNR: int, num_noise_samples: int, verbose: bool):
    """Creates a new dataset by integrating (a) randomly chosen
    sample(s) of noise into the existing digit dataset

    New dataset can be found in src/datasets/noisy_digits

    NOTE: Takes quite a while to run"""
    threads = []
    i = 0
    # Loop through all the folders and create a noisy dataset
    for subdir in os.listdir(digits_folder):
        folder = os.path.join(digits_folder, subdir)
        threads.append(threading.Thread(target=make_noisy_folder, args=(folder, SNR, num_noise_samples, verbose)))
        threads[i].start()
        i += 1

    # The actually multithreaded part
    i = 0
    for thread in threads:
        threads[i].join()
        i += 1