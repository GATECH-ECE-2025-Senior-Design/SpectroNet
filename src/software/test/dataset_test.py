import os
import matplotlib.pyplot as plt
import numpy as np

# get folder paths
current_directory = os.path.dirname(os.path.realpath(__file__))
datasets_folder = images_folder = os.path.join(current_directory, "..", "..", "datasets")
images_folder = os.path.join(datasets_folder, "images")

# grab an image
img_array = np.load(os.path.join(images_folder, '0_25_0.npy'))

# imshow rotates the image for some reason? But this is fine for now
plt.imshow(img_array)
plt.show()
