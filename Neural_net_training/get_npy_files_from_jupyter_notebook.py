import os
import shutil
import zipfile
# Define the path to the zip file (adjust this to your file's location)
zip_path = "images_4.zip"
# Check if the file exists
if os.path.exists(zip_path):
    print("Zip file found!")
else:
    print("Zip file NOT found! Check the file path.")
# Define the folder where you want to extract the contents
extract_folder = "extracted_images"
# Remove the folder if it exists (to start fresh)
if os.path.exists(extract_folder):
    shutil.rmtree(extract_folder)
# Recreate the empty folder
os.makedirs(extract_folder, exist_ok=True)
# Extract the zip file
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_folder)
    
print("Extraction complete! Files extracted to:", extract_folder)
    
# Define the path to the 'images' folder inside the extracted folder
spectrogram_folder = os.path.join(extract_folder, "images")
# List the first 20 files in the images folder
files = os.listdir(spectrogram_folder)
print("Files inside 'images':", files[:20])