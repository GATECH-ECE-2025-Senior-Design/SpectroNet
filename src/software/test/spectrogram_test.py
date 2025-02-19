import numpy as np
import matplotlib.pyplot as plt
import librosa
import sys
import os

# relative imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from spectrogram import spectrogram_choice
from spectrogram import read_wav
from windowing import crop
from windowing import window

# change these parameters
spec_type = "mel"
sample_rate = 8000
target_dtype = np.float32
time = 0.8
normalize = 1023
hop_length = 54
samples_per_dft = 384
resolution = 96

current_dir = os.path.dirname(os.path.abspath(__file__))
                                              # can change this path to test different samples
audio_data = read_wav(os.path.join(current_dir, "..", "..", "datasets", "digits", "38", "5_38_4.wav"), \
                      target_sample_rate=sample_rate, target_dtype=target_dtype, time_min=time, normalize=normalize)

audio_data = crop(audio_data, time=time, sr=sample_rate)

# Create the figure and subplots (2 rows, 1 column)
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

# Plot the audio waveform on the first subplot
ax[0].plot(audio_data)
ax[0].set_title(f"Audio Waveform - {sample_rate} Hz")
ax[0].set_xlabel('Sample Index')
ax[0].set_ylabel('Amplitude')
ax[0].grid(True)

# Calculate the spectrogram
bins, time, power = spectrogram_choice(audio_data, sample_rate=sample_rate, spec_type=spec_type, \
                                       hop_length=hop_length, target_dtype=target_dtype, \
                                       samples_per_dft=samples_per_dft, resolution=resolution)

# Used with crop setting
power = window(power, None, "mid")

power_dB = librosa.power_to_db(power, ref=np.max)

# Plot the spectrogram on the second subplot
                    # cropping time index so it plots correctly
c = ax[1].pcolormesh(time[:bins.shape[0]], bins, power_dB, shading='auto')
ax[1].set_title(f'Spectrogram: {spec_type}')
ax[1].set_xlabel('Time [s]')
ax[1].set_ylabel('Bin Label')
fig.colorbar(c, ax=ax[1], label='Power [dB]')

# Adjust layout for better spacing
plt.tight_layout()

# Show the figure
plt.show()
