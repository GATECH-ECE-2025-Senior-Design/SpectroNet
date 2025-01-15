import kagglehub
import os
import shutil
import argparse

# parse command line arguments
parser = argparse.ArgumentParser(description="A parser to check if the user needs to log into kaggle.")
parser.add_argument('--login', action='store_true', default=False, help="Set to True to log in.")
args = parser.parse_args()

# prompt user to log in to kagglehub
if args.login:
  kagglehub.login()

# download datasets
audio_mnist_path = kagglehub.dataset_download("sripaadsrinivasan/audio-mnist")
audio_noise_path = kagglehub.dataset_download("minsithu/audio-noise-dataset")

# print paths
print("Successfully downloaded Audio MNIST dataset to:", audio_mnist_path)
print("Successfully downloaded Background Noise dataset to:", audio_noise_path)

# create datasets folder if it does not exist, throw in gitignore
current_directory = os.path.dirname(os.path.realpath(__file__))
datasets_folder = os.path.join(current_directory, "datasets")
os.makedirs(datasets_folder, exist_ok=True)
gitignore_file = os.path.join(datasets_folder, ".gitignore")

# throw gitignore into the datasets folder
with open(gitignore_file, 'w') as f:
  f.write("*\n")
  f.write("!.gitignore\n")

# path to the "data" folder for Audio MNIST
audio_mnist_data_path = os.path.join(audio_mnist_path, "data")

# move datasets into our datasets folder
try:
    shutil.move(audio_mnist_data_path, datasets_folder)
    print(f"Folder '{audio_mnist_data_path}' has been moved to '{datasets_folder}'.")
    shutil.move(audio_noise_path, datasets_folder)
    print(f"Folder '{audio_noise_path}' has been moved to '{datasets_folder}'.")
except Exception as e:
  print(f"An error occured: {e}")
