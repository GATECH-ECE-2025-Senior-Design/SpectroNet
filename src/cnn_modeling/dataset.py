import os
import random

import numpy as np
import torch
from torch.utils.data import Dataset
from librosa import load as ld
from librosa.feature import melspectrogram
from librosa import power_to_db
from librosa.display import specshow
import matplotlib.pyplot as plt

def wav2melSpec(AUDIO_PATH):
    audio, sr = ld(AUDIO_PATH)
    return melspectrogram(y=audio, sr=sr)

def imgSpec(ms_feature):
    fig, ax = plt.subplots()
    ms_dB = power_to_db(ms_feature, ref=np.max)
    print(ms_feature.shape)
    img = specshow(ms_dB, x_axis='time', y_axis='mel', ax=ax)
    fig.colorbar(img, ax=ax, format='%+2.0f dB')
    ax.set(title='Mel-frequency spectrogram')

class AudioDataset(Dataset):
    def __init__(
        self,
        file_list,
        label_list,
        feature_transform=None,
        label_transform=None
    ):
        """
        :param file_list: List of full paths to audio files.
        :param label_list: Corresponding labels (digits).
        :param feature_transform: Transform to apply to the mel-spectrogram (numpy -> tensor).
        :param label_transform: Transform to apply to labels, if desired.
        """
        self.file_list = file_list
        self.label_list = label_list
        self.feature_transform = feature_transform
        self.label_transform = label_transform

    def __getitem__(self, idx):
        try:
            spec = wav2melSpec(self.file_list[idx])
            if self.feature_transform:
                spec = self.feature_transform(spec)

            label = self.label_list[idx]
            if self.label_transform:
                label = self.label_transform(label)

            return spec, label, self.file_list[idx]
        except Exception as e:
            # If there's an error, print warning and fall back to first file
            print(f"Warning: failed loading {self.file_list[idx]} with error {e}.")
            # Return something safe (e.g., re-process the first file)
            spec = wav2melSpec(self.file_list[0])
            if self.feature_transform:
                spec = self.feature_transform(spec)
            label = self.label_list[0]
            if self.label_transform:
                label = self.label_transform(label)
            return spec, label, self.file_list[0]

    def __len__(self):
        return len(self.file_list)

def create_audio_datasets(
    path,
    feature_transform=None,
    label_transform=None,
    train_size=0.70,
):
    """
    Create both train and test AudioDataset objects at once, ensuring
    an 80/20 split is done *only once* for each (digit, speaker) group.

    :param path: Path to the dataset root. Subfolders "01".."60" each contain .wav.
    :param feature_transform: Feature transform to apply (e.g. mel-spec -> tensor).
    :param label_transform: Transform to apply to labels.
    :param train_size: Fraction of the data to use for training.
    :param seed: Random seed for reproducibility.
    :return: (train_dataset, test_dataset)
    """


    # Dictionary to group files by (digit, speaker)
    grouped_files = {}

    # Collect and group the files
    for dirname, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".wav"):
                # filename format: "2_01_0.wav"
                parts = filename.split("_")
                if len(parts) < 3:
                    continue
                digit = int(parts[0])
                speaker = parts[1]  # "01"

                full_path = os.path.join(dirname, filename)
                key = (digit, speaker)
                if key not in grouped_files:
                    grouped_files[key] = []
                grouped_files[key].append(full_path)

    # Split each group
    train_files, train_labels = [], []
    test_files, test_labels = [], []

    for (digit, speaker), flist in grouped_files.items():
        np.random.shuffle(flist)

        
        split_idx = int(train_size * len(flist))

        train_subset = flist[:split_idx]
        test_subset = flist[split_idx:]

        train_files.extend(train_subset)
        test_files.extend(test_subset)

        train_labels.extend([digit] * len(train_subset))
        test_labels.extend([digit] * len(test_subset))

    # Create the actual Datasets
    train_dataset = AudioDataset(
        train_files,
        train_labels,
        feature_transform=feature_transform,
        label_transform=label_transform
    )
    test_dataset = AudioDataset(
        test_files,
        test_labels,
        feature_transform=feature_transform,
        label_transform=label_transform
    )

    return train_dataset, test_dataset
