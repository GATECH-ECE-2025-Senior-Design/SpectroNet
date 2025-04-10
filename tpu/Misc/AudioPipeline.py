# from pydub import AudioSegment

# # #Load m4a file
# # audio = AudioSegment.from_file("One.m4a", format="m4a")
# # #Export to a .wav file
# # audio.export("One.wav", format="wav")

# import librosa
# import numpy as np
# import matplotlib.pyplot as plt
# import cv2
# from tflite_runtime.interpreter import Interpreter
# from tflite_runtime.interpreter import load_delegate

# # ----- 1. Load the Audio File -----
# audio_path = "2_02_31.wav"
# y, sr = librosa.load(audio_path, sr=None)

# # ----- 2. Create a Mel Spectrogram -----
# # Generate the spectrogram (using 128 Mel bands initially)
# S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
# S_dB = librosa.power_to_db(S, ref=np.max)

# # ----- 3. Normalize and Convert to 8-bit -----
# # Normalize the dB values to the 0-255 range
# S_dB_norm = 255 * (S_dB - np.min(S_dB)) / (np.max(S_dB) - np.min(S_dB))
# S_dB_norm = S_dB_norm.astype(np.uint8)

# # ----- 4. Resize to 96x96 -----
# # Use OpenCV to resize the spectrogram to 96x96 pixels
# spectrogram_resized = cv2.resize(S_dB_norm, (96, 96))

# # Optional: visualize the resized spectrogram
# plt.figure(figsize=(4, 4))
# plt.imshow(spectrogram_resized, aspect='auto', origin='lower', cmap='viridis')
# plt.title('96x96 Spectrogram')
# plt.colorbar()
# plt.show()

# np.save("one.npy", spectrogram_resized)
# import librosa
# import numpy as np
# import matplotlib.pyplot as plt
# import cv2
# from pydub import AudioSegment
# audio_files_directory = "AudioSamples"
# audio_files = [f"{audio_files_directory}/{file}" for file in os.listdir(audio_files_directory) if file.endswith(".m4a")]
# # Uncomment these lines if you need to convert an m4a file to wav
# for audio_file in audio_files:
#     audio = AudioSegment.from_file(audio_file, format="m4a")
#     audio.export(audio_file.replace(".m4a", ".wav"), format="wav")



# # ----- 1. Load the Audio File -----
# audio_path = "One.wav"
# y, sr = librosa.load(audio_path, sr=None)

# # ----- 2. Create a Mel Spectrogram -----
# # Generate the mel spectrogram with 128 Mel bands
# S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)

# # Convert to decibel (dB) scale using a dynamic range of 80 dB so that values lie in [-80, 0]
# S_dB = librosa.power_to_db(S, ref=np.max, top_db=80)
# S_dB = np.clip(S_dB, -80, 0)  # Ensure the values are within [-80, 0]

# # ----- 3. Resize to 96x96 -----
# # Resize the spectrogram to 96x96 pixels using OpenCV
# spectrogram_resized = cv2.resize(S_dB, (96, 96))

# # Optional: visualize the resized spectrogram
# plt.figure(figsize=(4, 4))
# plt.imshow(spectrogram_resized, aspect='auto', origin='lower', cmap='viridis')
# plt.title('96x96 Spectrogram (dB values)')
# plt.colorbar()
# plt.show()

# # ----- 4. Save the Spectrogram to one.npy -----
# np.save("one.npy", spectrogram_resized)

# import os
# import glob
# from pydub import AudioSegment
# import librosa
# import numpy as np
# import cv2

# # Create the output directory if it doesn't exist
# output_dir = "NPYs"
# os.makedirs(output_dir, exist_ok=True)

# # Get a list of all .m4a files in the AudioSamples directory
# audio_files = glob.glob(os.path.join("AudioSamples", "*.m4a"))

# for file in audio_files:
#     # Get the base name (without extension) for naming output files
#     base_name = os.path.splitext(os.path.basename(file))[0]
    
#     # Define paths for temporary wav file and final npy file
#     wav_path = os.path.join("AudioSamples", base_name + ".wav")
#     npy_path = os.path.join(output_dir, base_name + ".npy")
    
#     # ----- Convert .m4a to .wav -----
#     audio = AudioSegment.from_file(file, format="m4a")
#     audio.export(wav_path, format="wav")
    
#     # ----- Load the WAV File -----
#     y, sr = librosa.load(wav_path, sr=None)
    
#     # ----- Create a Mel Spectrogram -----
#     # Generate mel spectrogram with 128 Mel bands and fmax of 8000 Hz
#     S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
#     # Convert the power spectrogram to dB scale using a top_db of 80,
#     # so that the values range from -80 to 0 dB.
#     S_dB = librosa.power_to_db(S, ref=np.max, top_db=80)
#     S_dB = np.clip(S_dB, -80, 0)
    
#     # ----- Resize the Spectrogram to 96x96 -----
#     spectrogram_resized = cv2.resize(S_dB, (96, 96))
    
#     # ----- Save the Resized Spectrogram as a .npy File -----
#     np.save(npy_path, spectrogram_resized)
    
#     # Remove the temporary .wav file to clean up
#     os.remove(wav_path)

#     print(f"Processed {file} -> {npy_path}")
import os
import glob
from pydub import AudioSegment
import librosa
import numpy as np
import cv2

# Mapping dictionary to convert word names to numbers.
# This works regardless of whether the file name is capitalized.
word_to_num = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10"
}

# Create the output directory if it doesn't exist
output_dir = "NPYs"
os.makedirs(output_dir, exist_ok=True)

# Get a list of all .m4a files in the AudioSamples directory
audio_files = glob.glob(os.path.join("AudioSamples", "*.m4a"))

for file in audio_files:
    # Get the base name (without extension) for naming output files
    base_name = os.path.splitext(os.path.basename(file))[0]
    
    # Map the base name to a number if applicable (case-insensitive)
    new_name = word_to_num.get(base_name.lower(), base_name)
    
    # Define paths for temporary wav file and final npy file
    wav_path = os.path.join("AudioSamples", base_name + ".wav")
    npy_path = os.path.join(output_dir, new_name + ".npy")
    
    # ----- Convert .m4a to .wav -----
    audio = AudioSegment.from_file(file, format="m4a")
    audio.export(wav_path, format="wav")
    
    # ----- Load the WAV File -----
    y, sr = librosa.load(wav_path, sr=None)
    
    # ----- Create a Mel Spectrogram -----
    # Generate mel spectrogram with 128 Mel bands and fmax of 8000 Hz
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    # Convert to decibel scale with a top_db of 80 so values range from -80 to 0 dB.
    S_dB = librosa.power_to_db(S, ref=np.max, top_db=80)
    S_dB = np.clip(S_dB, -80, 0)
    
    # ----- Resize the Spectrogram to 96x96 -----
    spectrogram_resized = cv2.resize(S_dB, (96, 96))
    
    # ----- Save the Resized Spectrogram as a .npy File -----
    np.save(npy_path, spectrogram_resized)
    
    # Remove the temporary .wav file to clean up
    os.remove(wav_path)
    
    print(f"Processed {file} -> {npy_path}")
