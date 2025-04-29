#!/bin/bash

# Step 1: Run Data Preparation Script
echo "Running data.py to set up datasets..."
python data.py

# Check if the required dataset folders exist
if [ ! -d "../datasets/digits_train" ] || [ ! -d "../datasets/digits_test" ]; then
    echo "Error: One or more required dataset folders ('digits_train', 'digits_test') not found!"
    exit 1
fi

# Step 2: Augment the Data**
echo "Running augment_digits_train.py on training data..."
python augment_digits_train.py --input_dir "../datasets/digits_train"
echo "Running augment_digits_train.py on test data..."
python augment_digits_train.py --input_dir "../datasets/digits_test"

# Step 3: Delete old spectrogram datasets (Ensure a Fresh Start)**
echo "Removing old spectrogram datasets..."
for dataset in "images_train" "images_val" "images_test"; do
    if [ -d "../datasets/$dataset" ]; then
        rm -rf "../datasets/$dataset"
        echo "Deleted old $dataset/"
    fi
done

# Step 4: Generate Spectrograms for Train and Test Sets**
# (We are only processing 'train' and 'test' sets here.)
dataset_names=("train" "test")
dataset_dirs=("digits_train" "digits_test")

for i in "${!dataset_names[@]}"; do
    dataset="${dataset_names[$i]}"
    input_dir="../datasets/${dataset_dirs[$i]}"
    output_dir="../datasets/images_$dataset"

    echo "Generating Spectrograms for $dataset Set..."
    python dataset_generation.py --input_dir "$input_dir" --output_dir "$output_dir" \
        --crop --samples_per_dft 384 --sr 8000 --resolution 96 --dtype float32 --spec_type mel --time 0.8

    # Verify that spectrogram generation was successful
    if [ ! -d "$output_dir" ] || [ -z "$(ls -A "$output_dir")" ]; then
        echo "Error: Spectrogram generation for $dataset Set failed!"
        exit 1
    fi
done

# Step 5: Compress the Train and Test Spectrograms into ZIP Files in the training Folder**
# Adjust the destination path as needed – here we assume that relative to the current script location,
# "../training" is the training folder where you want the zip files.
for dataset in "train" "test"; do
    output_dir="../datasets/images_$dataset"
    zip_file="images_$dataset.zip"

    echo "Compressing $dataset Set..."
    # Delete any previous zip file in the training folder
    rm -f "../training/$zip_file"
    # Change directory into the spectrogram folder, zip its contents (flattening the directory structure),
    # and output the zip file to the training folder.
    cd "$output_dir" || exit
    zip -r -j "../../training/$zip_file" .
    cd - || exit
done

# Step 6: Clean Up Intermediate Data Folders**
echo "Cleaning up intermediate dataset directories..."
rm -rf ../datasets/digits_train ../datasets/digits_test ../datasets/images_train ../datasets/images_test
echo "Cleanup complete!"

echo "Dataset preparation, augmentation, spectrogram generation, compression, and cleanup complete!"
