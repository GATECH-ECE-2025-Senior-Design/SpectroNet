# Software Folder README

This folder contains scripts to download relevant datasets, process audio files, and generate spectrograms of spoken digits mixed with background noise. The primary files involved in these tasks are data.py and dataset_generation.py. Below you will find the console arguments you can use when running them.

## data.py: Download Relevant Datasets

### Description:

The data.py script is responsible for downloading the relevant datasets for spoken digits and background noise. It automatically fetches these datasets and stores them in the datasets folder.

### Console Arguments:

- --login: (default False) Use to log into kaggle from the console. If not toggled, you must be logged into kaggle on your computer.

### Usage

```python
python data.py --login
```

## dataset_generation.py: Download Relevant Datasets

### Description:

The dataset_generation.py script processes the spoken digits dataset by mixing it with background noise, generating spectrograms, and applying a trigger condition/algorithm to the spectrograms to produce square images. These spectrogram images are saved in datasets/images.

### Console Arguments:

- --enable_noise [no value]: (default False) Whether or not to mix background noise into spoken digits.
- --snr: (default None) If background noise is toggled, the signal-to-noise ratio between spoken digits and background noise (12 --> spoken digits are 12dB louder than background noise).
- --crop [no value]: (default False) Whether to crop audio files and equally pad left and right with silence for the length of the clip to be equal to specified time period. Note that enabling cropping disables windowing, as all audio files become "square"
- --windowing: (default "end") The windowing algorithm applied to the spectrograms to crop into square images. Choices: {"end", "mid"}
- --sr: (default 8000) The sample rate in which the audio files are resampled to.
- --spec_type: (default "simple") The type of spectrogram used in generating the dataset. Choices: {"simple", "cqt", "mel"}
- --resolution: (default 96) The resolution of the generated spectrogram. Note that all spectrograms fed into the CNN are square images, with the vertical resolution being the number of bins and the horizontal resolution being the number of DFT/CQT taken. Hop length may have to be adjusted for the final square image to cover the correct amount of time (~0.5 seconds).
- --dtype: (default int16) The datatype for the audio signal and all subsequent processing. Choices: {"int8", "int16", "int32", "float8", "float16", "float32"}
- --time: (default 0.5) The amount of time that is FULLY included within a square spectrogram. This means that all samples within this period are both the leftmost and rightmost sample of a DFT sample within the square spectrogram.
- --samples_per_dft: (default 256) The number of samples within any given DFT taken while generating the dataset.

### Usage

```python
python dataset_generation.py --noise --snr 15 --windowing mid
```

## NOTE: Noise integration is not currently supported. Will be fixed in the future by Jahan.