import collections

test_files = [
    "9_19_47.npy",
    "5_09_28.npy",
    "0_48_15.npy",
    "7_38_43.npy",
    "8_25_46.npy",
    "3_50_17.npy",
    "4_13_46.npy",
    "0_27_17.npy",
    "4_43_9.npy",
    "4_37_47.npy",
    "5_20_31.npy",
    "9_56_10.npy",
    "2_51_29.npy",
    "7_28_0.npy",
    "8_37_26.npy",
    "8_59_19.npy",
    "9_57_37.npy",
    "0_46_38.npy",
    "2_37_28.npy",
    "5_27_33.npy"
]

for file in test_files:
    label = extract_label(file)
    print(f"File: {file} → Extracted Label: {label}")

print("Class Distribution:", collections.Counter(y))