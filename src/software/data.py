import kagglehub
import os

# download datasets
audio_mnist_path = kagglehub.dataset_download("sripaadsrinivasan/audio-mnist")
audio_noise_path = kagglehub.dataset_download("minsithu/audio-noise-dataset")

# print paths
print("Successfully downloaded Audio MNIST dataset to:", audio_mnist_path)
print("Successfully downloaded Background Noise dataset to:", audio_noise_path)