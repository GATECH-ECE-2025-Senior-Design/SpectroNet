import noise_integration
from scipy.io import wavfile
import os
import spectrogram as spec

current_directory = os.path.dirname(os.path.realpath(__file__))
datasets_folder = os.path.join(current_directory, "..", "datasets")
digits_folder = os.path.join(datasets_folder, "digits")
noise_folder = os.path.join(datasets_folder, "noise")

audio_data = wavfile.read(os.path.join(digits_folder, '01/0_01_0.wav'))

audio_data_as_int16 = noise_integration.float32_to_fixed_point(audio_data, 2, 14, 'int16')
audio_data_as_int8 = noise_integration.float32_to_fixed_point(audio_data, 1, 7, 'int8')

print(audio_data_as_int16)

print(audio_data_as_int8)
