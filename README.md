If you would like to see all of the steps below in a Colab notebook with everything ready to run, here is the link:  
📌 [Google Colab Notebook](https://colab.research.google.com/drive/18enfko92t783UyUtiDNBNvh0L2wlBvDs?usp=sharing)

> **Note:** You have to run **Steps 1-4** on your own to connect to your own Google Drive account that has the `images.zip` file with all of the `.npy` spectrograms to use.

Step 1:
Run dataset generation steps to get images folder (should have a bunch of .npy files). Once you complete dataset generation steps and cd into SpectroNet/src/datasets/images, running ls should show all the .npy files:
![Alt Text](READme_images/Screenshot-2025-02-22-at-6.28.02.png)

Step 2:
Zip the images folder (SpectroNet/src/datasets/images) to get images.zip, and put it into your google drive. Don’t put it into another folder inside your drive because otherwise you have to change the file paths in the files.

Specifically, you must change following variables that define the file paths:
In get_npy_files_from_google_drive.py:
Define the path to the zip file
zip_path = "/content/drive/My Drive/images_4.zip"

In extracts_label_loads_spectograms_load_dataset.py:
Define the path to the zip file
zip_path = "/content/drive/My Drive/images_4.zip"

Step 3:
Open a new notebook in Google colab. Change the runtime type to a T4 GPU:
![Alt Text](READme_images/Screenshot-2025-02-22-at-7.28.32.png)

![Alt Text](READme_images/Screenshot-2025-02-22-at-7.29.20.png)

Click save and now you are running a T4 GPU in colab. 
To check the number of GPUs and set the policy to mixed precision (float16 to speed up training, reduce memory usage, and still keep critical computations in float32 for numerical stability), copy and paste the code in check_gpu_mixed_precision.py. Correct output should be:

Number of GPUs available: 1
PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')
Mixed precision enabled: <DTypePolicy "mixed_float16">

If the above output is the same as what you have in colab, you have correctly set up the GPU and can move onto step 4.

Step 4:
Run the get_npy_files_from_google_drive.py code in a cell in colab to mount your google drive in colab (to access the images.zip currently in your Google Drive). There will be several pop ups asking for Google Drive access:

![Alt Text](READme_images/Screenshot-2025-02-22-at-6.44.52.png)
Click Connect to Drive

![Alt Text](READme_images/Screenshot-2025-02-22-at-6.45.00.png)
Click the google account that has the google drive containing your images.zip file.

![Alt Text](READme_images/Screenshot-2025-02-22-at-6.45.15.png)
Click continue

![Alt Text](READme_images/Screenshot-2025-02-22-at-6.45.07.png)
Click continue

If you run through the pop-ups as described in the above 4 steps, your colab should be granted access to your Google Drive and you will be able to access your images.zip file.

The code also checks if the file containing images.zip exists, and if not creates a folder in colab to put images.zip in. It then unzips the file and lists the first 20 files in the new folder in colab, which confirms that the .npy files are now able to be accessed inside colab.

Output after running get_npy_files_from_google_drive.py code in colab cell:

Mounted at /content/drive
images_4.zip found in Google Drive!
Extraction complete! Files extracted to: /content/spectrogram_data
Files inside 'images': ['5_48_11.npy', '8_06_12.npy', '2_10_27.npy', '0_04_41.npy', '4_01_36.npy', '8_26_47.npy', '2_11_36.npy', '8_59_30.npy', '0_36_33.npy', '3_16_3.npy', '0_05_19.npy', '5_47_1.npy', '2_29_8.npy', '0_27_23.npy', '9_53_9.npy', '8_34_36.npy', '0_53_44.npy', '0_57_39.npy', '3_56_41.npy', '0_06_47.npy']

If rerunning this step, will get the following as the first output line since you have already mounted the drive:
Drive already mounted at /content/drive; to attempt to forcibly remount, call drive.mount("/content/drive", force_remount=True).

Both are fine to continue to the next step

If the above output happens after running though the pop-ups and you see .npy files inside ‘images’ (as seen above in the correct output), file extraction from google drive was successful and you can move onto step 5.


Step 5:
Next, paste in the code from check_bad_spectogram.py into the next colab cell to see if there are any corrupted .npy files. If there is not, the following should be the correct output:

Checked 30000 files.
Unique spectrogram shapes found: {(96, 96)}
0 corrupt files: []
0 all-zero files: []
2_12_15.npy | Shape: (96, 96) | Min: -80.0 | Max: 0.0 | Mean: -65.06060028076172
8_12_25.npy | Shape: (96, 96) | Min: -80.0 | Max: 0.0 | Mean: -67.90231323242188
2_12_11.npy | Shape: (96, 96) | Min: -80.0 | Max: 0.0 | Mean: -65.53494262695312
1_10_22.npy | Shape: (96, 96) | Min: -80.0 | Max: 0.0 | Mean: -63.55265426635742
3_49_24.npy | Shape: (96, 96) | Min: -80.0 | Max: 0.0 | Mean: -65.1098861694336
Contains NaN? False
Contains Inf? False

If there is any other output than the one shown above (some random spectogram file numbers will be shown, but min, max, and mean should all be the same for every spectogram), redo data generation to get uncorrupted .npy files. Otherwise, Neural Net training validation accuracy and loss will suffer. Once the correct outputs for this step happens, move onto step 6.

Step 6: 
Paste in code from check_spectogram_after_load.py into a colab cell. First uncomment out the # %matplotlib inline from the imports and run it - if you don’t uncomment, the spectogram will not show inside a colab cell. This code picks a random spectogram file to show you. If this succeeds, you will be able to see a spectogram like so:
