#!/bin/bash

# 🚀 **Step 1: Run Data Preparation Script**
echo "📂 Running data.py to set up datasets..."
python data.py

# ✅ Check if dataset folders exist after data.py runs
# if [ ! -d "../datasets/digits_train" ] || [ ! -d "../datasets/digits_val" ] || [ ! -d "../datasets/digits_test" ]; then
if [ ! -d "../datasets/digits_train" ] || [ ! -d "../datasets/digits_test" ]; then
    echo "❌ Error: One or more required dataset folders ('digits_train', 'digits_val', 'digits_test') not found!"
    exit 1
fi

# 🚀 **Step 2: Augment Training Data**
echo "🎛️ Running augment_digits_train.py..."
python augment_digits_train.py --input_dir "../datasets/digits_train"
echo "🎛️ Running augment_digits_train.py on test data..."
python augment_digits_train.py --input_dir "../datasets/digits_test"

# 🔥 **Step 3: Delete old spectrogram datasets (Ensure Fresh Start)**
echo "🗑️ Removing old spectrogram datasets..."
for dataset in "images_train" "images_val" "images_test"; do
    if [ -d "../datasets/$dataset" ]; then
        rm -rf "../datasets/$dataset"
        echo "✅ Deleted old $dataset/"
    fi
done

# 🚀 **Step 4: Generate Spectrograms for Train, Validation, and Test Sets**
# dataset_names=("train" "val" "test")
# dataset_dirs=("digits_train" "digits_val" "digits_test")

dataset_names=("train" "test")
dataset_dirs=("digits_train" "digits_test")

for i in "${!dataset_names[@]}"; do
    dataset="${dataset_names[$i]}"
    input_dir="../datasets/${dataset_dirs[$i]}"
    output_dir="../datasets/images_$dataset"

    echo "🚀 Generating Spectrograms for $dataset Set..."
    python dataset_generation.py --input_dir "$input_dir" --output_dir "$output_dir" \
        --crop --samples_per_dft 384 --sr 8000 --resolution 96 --dtype float32 --spec_type mel --time 0.8

    # Check if spectrogram generation was successful
    if [ ! -d "$output_dir" ] || [ -z "$(ls -A "$output_dir")" ]; then
        echo "❌ Error: Spectrogram generation for $dataset Set failed!"
        exit 1
    fi
done

# 📦 **Step 5: Compress Train, Validation, and Test Sets**
# for dataset in "train" "val" "test"; do
for dataset in "train" "test"; do
    output_dir="../datasets/images_$dataset"
    zip_file="images_$dataset.zip"

    echo "📦 Compressing $dataset Set..."
    rm -f "$zip_file"  # Delete previous compressed file
    cd "$output_dir" || exit
    zip -r -j "../../software/$zip_file" .  # Use `-j` to remove paths
    cd - || exit
done

echo "✅ Dataset preparation, augmentation, spectrogram generation, and compression complete!"