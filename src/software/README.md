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

- --noise: (default False) Whether or not to mix background noise into spoken digits.
- --snr: (default None) If background noise is toggled, the signal-to-noise ratio between spoken digits and background noise.
- --windowing: (default "end") The windowing algorithm applied to the spectrograms to crop into square images.

### Usage

```python
python dataset_generation.py --noise --snr 15 --windowing mid
```

## NOTE: Noise integration is not currently supported. Will be fixed in the future by Jahan.
