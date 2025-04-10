import os
import glob
from pydub import AudioSegment

# Define input and output directories
input_dir = "AudioSamples"
output_dir = "WAVs"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Get a list of all .m4a files in the input directory
m4a_files = glob.glob(os.path.join(input_dir, "*.m4a"))

for file in m4a_files:
    # Extract the base name without extension
    base_name = os.path.splitext(os.path.basename(file))[0]
    
    # Define the output path for the .wav file
    wav_path = os.path.join(output_dir, base_name + ".wav")
    
    # Load the m4a file and export it as .wav
    audio = AudioSegment.from_file(file, format="m4a")
    audio.export(wav_path, format="wav")
    
    print(f"Converted {file} -> {wav_path}")