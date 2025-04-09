import subprocess
import os
import time
import zipfile

# Run the command and capture the output
result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)

# Print the output
print(result.stdout)


# Function to extract ZIP file in chunks
def extract_zip_in_chunks(zip_file, extract_folder, batch_size):
    if not os.path.exists(zip_file):
        print(f"Warning: {zip_file} not found!")
        return

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        total_files = len(file_list)

        print(f"Found {total_files} files in {zip_file}.")

        start_time = time.time()
        for i in range(0, total_files, batch_size):
            batch_files = file_list[i : i + batch_size]
            # Extract only the current batch
            zip_ref.extractall(path=extract_folder, members=batch_files)
            print(f"Extracted {i + len(batch_files)} / {total_files} files...")
        
        elapsed_time = time.time() - start_time
        print(f"Extraction of {zip_file} complete!")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        print(f"Extracted folder: {extract_folder}\n")

# Define batch size for both extractions
BATCH_SIZE = 1000  # Extract 1000 files at a time

# --- Extraction for images_train.zip ---
zip_file_train = "images_train.zip"
extract_folder_train = "images_train"

# Remove existing extraction folder if it exists and recreate it
if os.path.exists(extract_folder_train):
    os.system(f"rm -rf {extract_folder_train}")  # Ensure a fresh start
os.makedirs(extract_folder_train, exist_ok=True)

# Extract the training ZIP file in chunks
extract_zip_in_chunks(zip_file_train, extract_folder_train, BATCH_SIZE)

# --- Extraction for images_test.zip ---
zip_file_test = "images_test.zip"
extract_folder_test = "images_test"

# Remove existing extraction folder if it exists and recreate it
if os.path.exists(extract_folder_test):
    os.system(f"rm -rf {extract_folder_test}")  # Ensure a fresh start
os.makedirs(extract_folder_test, exist_ok=True)

# Extract the test ZIP file in chunks
extract_zip_in_chunks(zip_file_test, extract_folder_test, BATCH_SIZE)
