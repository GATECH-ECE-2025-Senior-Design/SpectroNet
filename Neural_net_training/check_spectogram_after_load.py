import os
import numpy as np
import matplotlib.pyplot as plt
import random
# %matplotlib inline

# Pick a random spectrogram files to visualize
random_files = random.sample(npy_files, 3)

plt.figure(figsize=(12, 4))
for i, file in enumerate(random_files):
    file_path = os.path.join(spectrogram_folder, file)
    spectrogram = np.load(file_path)

    # plt.subplot(1, 3, i+1)
    plt.imshow(spectrogram, cmap="inferno", aspect="auto")
    plt.title(file)
    plt.axis("off")

plt.show()