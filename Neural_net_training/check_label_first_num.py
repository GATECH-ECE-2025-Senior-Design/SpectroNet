import collections

test_files = [
    "9_19_47_noisy.npy",
    "5_09_28_noisy.npy",
    "0_48_15_noisy.npy",
    "7_38_43_noisy.npy",
    "8_25_46_noisy.npy",
    "3_50_17_noisy.npy",
    "4_13_46_noisy.npy",
    "0_27_17_noisy.npy",
    "4_43_9_noisy.npy",
    "4_37_47_noisy.npy",
    "5_20_31_noisy.npy",
    "9_56_10_noisy.npy",
    "2_51_29_noisy.npy",
    "7_28_0_noisy.npy",
    "8_37_26_noisy.npy",
    "8_59_19_noisy.npy",
    "9_57_37_noisy.npy",
    "0_46_38_noisy.npy",
    "2_37_28_noisy.npy",
    "5_27_33_noisy.npy"
]

for file in test_files:
    label = extract_label(file)
    print(f"File: {file} → Extracted Label: {label}")

print("Class Distribution:", collections.Counter(y))

# Check speaker distribution
print("Speaker Distribution:", collections.Counter(speaker_ids))