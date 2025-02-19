import sys
import os
import numpy as np
import librosa
import matplotlib.pyplot as plt

# relative imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from spectrogram import spectrogram_choice
from spectrogram import read_wav
from windowing import window
from windowing import crop

current_dir = os.path.dirname(os.path.abspath(__file__))
                                              # can change this path to test different samples
audio_data = read_wav(os.path.join(current_dir, "..", "..", "datasets", "digits", "38", "5_38_4.wav"), \
                      target_sample_rate=8000, target_dtype=np.float32, time_min=10, normalize=1023)

# haven't used noise integration yet, so just gaussian noise for now
noise = np.random.normal(0, 50, size=audio_data.size)

audio_data_noisy = audio_data + noise

# calculate the spectrogram
bins, time, power = spectrogram_choice(audio_data_noisy, sample_rate=8000, spec_type="mel", \
                                       hop_length=32, target_dtype=np.float32, \
                                       samples_per_dft=384, resolution=96)
# convert power to dB
power_dB = librosa.power_to_db(power, ref=np.max)

# pre-windowing
plt.pcolormesh(time[:power_dB.shape[1]], bins, power_dB, shading='auto')
plt.show()

# test windowing
power_dB = window(power_dB, audio_data_noisy, "roll_power")

# post-windowing
plt.pcolormesh(time[:bins.shape[0]], bins, power_dB, shading='auto')
plt.show()
