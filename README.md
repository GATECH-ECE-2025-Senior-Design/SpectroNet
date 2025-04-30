# How to use gpu_demo_dataset_generation branch
> This is the dataset generation part of the gpu branch

## Description
- Made to generate dataset (with injected noise) with digit classes 0-9 from Audio MINST dataset


## Table of Contents
1. [How to run branch to generate dataset](#how-to-run-branch-to-generate-dataset)
2. [What each file does inside the bash file](#what-each-file-does-inside-the-bash-file)
3. [Running the Training Notebooks on PACE ICE Jupyter](#running-the-training-notebooks-on-pace-ice-jupyter)

## How to run branch to generate dataset
Step-by-step instructions to get the project running locally.
1. Download Prerequisites: Can all be found in SpectroNet/sw/software/requirements.txt
2. Clone the repo 
3. Login to kaggle (https://www.kaggle.com/)
   - If you do not have an account in kaggle, you must create one so that data.py can properly access the audio MINST dataset 
4. Go to SpectroNet/sw/software/ and run ls -l generate_datasets.sh
   - Should return that generate_datasets.sh exists
   - Make generate_datasets.sh readable with command: chmod +x sw/software/generate_datasets.sh
5. Run ./generate_datasets.sh
   - Note: This will take a while to run
   - When done, you should have 2 zip files called images_train.zip and images_test.zip in SpectroNet/sw/training

## What each file does inside the bash file

1. **`data.py`**  
   * Gets the `.wav` files from the MNIST dataset on Kaggle and splits them into training and test datasets (70 – 30 split respectively)

2. **`augment_digits_train.py`**  
   Augments the `.wav` files with many different transformations. Each original `.wav` file is passed through the following augmentations (2 variants per type) in the `augment_pipeline`:

   - **Random Gain**  
     Scales the overall amplitude by a random factor between **0.7× and 1.3×** to simulate different recording levels.

   - **Background Noise**  
     Mixes in real noise (from `noise_augment/PCAFETER`) at a **random signal-to-noise ratio (0–20 dB)** to model noisy environments.

   - **Reverberation**  
     Convolves the audio with a room-impulse response (RIR) and re-normalizes energy, adding realistic echo/reverb.

   - **Pitch Shift**  
     Shifts pitch up or down by a random amount within **±2 semitones**, emulating speaker variation or recording speed changes.

   - **Time Stretch**  
     Speeds up or slows down the audio by a random rate between **0.9× and 1.1×**, preserving pitch.

   - **Time Shift**  
     Circularly rolls the waveform by up to **±10%** of its length, simulating misalignment or clipping at start/end.

   - **Random Filter**  
     Applies a 4th-order Butterworth filter of random type—low-pass, high-pass, or band-pass—with cutoff(s) chosen uniformly in **300–3000 Hz**.

   - **Random Clipping**  
     With **20% probability**, clips the waveform samples to ± a random threshold between **0.2 and 0.9** of max amplitude, mimicking distortion.

   *Each augmentation is applied with its own probability (noise: 50%, reverb: 30%, pitch/stretch: 50%, filter: 30%, clipping: 20%), and every file generates two new variants per augmentation run.*

3. **`dataset_generation.py`**  
   Generates spectrogram `.npy` files from all `.wav` inputs using these steps:

   - **Recursive WAV discovery**  
     Walks `--input_dir` and its subfolders to collect all `.wav` files for processing.

   - **Argument-driven configuration**  
     Accepts flags for sample rate (`--sr`), spectrogram type (`--spec_type`), output resolution (`--resolution`), data type (`--dtype`), time window (`--time`), noise mixing (`--enable_noise` + `--snr` + `--noise_samples`), cropping (`--crop`), windowing method (`--windowing`), DFT size (`--samples_per_dft`), verbosity (`--verbose`), and input/output directories.

   - **Optional noise integration**  
     When `--enable_noise` is set, calls `noise_integration.integrate_noise(...)` to overlay background noise on the raw `.wav` dataset before spectrogramming.

   - **Spectrogram parameters calculation**  
     Computes the number of time samples per spectrogram (`time × sr`), hop length (based on resolution and DFT size), and target NumPy dtype.

   - **Job creation**  
     Wraps each `.wav` path into a `SpectroJob(wav_path, out_path)` tuple pointing to a `.npy` output file in `--output_dir`.

   - **Audio loading & optional cropping**  
     Uses `spec.read_wav()` to load at the target sample rate/dtype, then—if `--crop`—applies `windowing.crop()` to center/pad to the exact time window.

   - **Spectrogram computation**  
     Calls `spec.spectrogram_choice(...)` to generate a power spectrogram (simple, Mel, or CQT) at the chosen resolution, hop length, and DFT size.

   - **Windowing**  
     Applies `windowing.window()` (using the selected `--windowing` mode or “mid” if cropped) to shape the spectrogram.

   - **dB conversion & saving**  
     Converts power to decibels via `librosa.power_to_db()` and saves the resulting 2D array as a NumPy `.npy` file.

   - **Batched multiprocessing**  
     Splits the job list into batches (default 100 files) and uses a `ProcessPoolExecutor` (up to 30 workers) to parallelize spectrogram creation across CPUs.

   - **Progress & error handling**  
     Prints batch-level progress (`Processing batch X/Y …`) and reports per-file errors without stopping the overall run.

   *Uses 8000 S/s sample rate, 96×96 resolution, 384 samples per DFT, computed hop length ≈64, Mel spectrogram, and float32 dtype for GPU.*

4. **Compression**  
   Finally, the script zips the newly created `images_train` and `images_test` folders into `images_train.zip` and `images_test.zip` in `SpectroNet/sw/training`.

## Running the Training Notebooks on PACE ICE Jupyter
> If you’re working on the PACE ICE cluster and want to launch the training pipelines from this repository, follow these steps:

1. Clone this branch and `cd` into the training folder:
   - cd SpectroNet/sw/training
2. Create & activate a Python 3.10 environment (Conda or virtualenv) and install dependencies
   - conda create -n spectronet_py10 python=3.10 -y
   - conda activate spectronet_py10
   - (pip install -r requirements_training.txt)
3. Install the custom CUDA Jupyter kernel, so that your notebooks can see GPU acceleration:
   - jupyter kernelspec install --user TF-2.10.1_CUDA-11.8_kernelspec.tar.gz
4. Launch JupyterLab on PACE ICE and select the new kernel
   - In JupyterLab pick the kernel named TF-2.10.1_CUDA-11.8
5. Open and run one of the training notebooks:
   - Full_training_pipeline_with_best_arch_aug_training.ipynb
   - Full_training_pipeline_with_all_archs_aug_training__stats_to_excel_spreadsheet.ipynb
   - Make sure the TF-2.10.1_CUDA-11.8 kernel is selected so you get GPU support.

