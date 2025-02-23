from google.colab import drive
import os
import shutil
import zipfile

# Mount Google Drive
drive.mount('/content/drive')

# Define the path to the zip file
zip_path = "/content/drive/My Drive/images_4.zip"

# Check if the file exists
if os.path.exists(zip_path):
    print("images_4.zip found in Google Drive!")
else:
    print("images_4.zip NOT found! Check the file path.")

folder_path = "/content/spectrogram_data"

# Check if folder exists before trying to delete
if os.path.exists(folder_path):
    shutil.rmtree(folder_path)  # Deletes the entire folder and its contents

# Recreate the empty folder
os.makedirs(folder_path, exist_ok=True)

# Define extraction path
extract_path = "/content/spectrogram_data"

# Extract zip file
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

print("Extraction complete! Files extracted to:", extract_path)

# Define the correct path inside spectrogram_data
spectrogram_folder = "/content/spectrogram_data/images"

# List first 20 files
spectrogram_files = os.listdir(spectrogram_folder)

# Print filenames
print("Files inside 'images':", spectrogram_files[:20])