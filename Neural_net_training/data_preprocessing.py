import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split

# Define Preprocessing Function
def prepare(ds, augment=False):
    # rescale = tf.keras.Sequential([tf.keras.layers.Rescaling(1./255)])  # Normalize input

    augmentations = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),  # Flip spectrogram
        tf.keras.layers.RandomRotation(0.1),  # Rotate slightly
        tf.keras.layers.RandomZoom(0.1)  # Apply zoom distortions
    ])

    # Apply rescaling to both datasets
    # ds = ds.map(lambda x, y: (rescale(x, training=True), y))

    # Apply augmentation only to training dataset
    if augment:
        ds = ds.map(lambda x, y: (augmentations(x, training=True), y))

    return ds

# Get unique speaker IDs
unique_speakers = np.unique(speaker_ids)

# Split speakers into training (80%) and validation (20%) groups
train_speakers, val_speakers = train_test_split(unique_speakers, test_size=0.2, random_state=42)


# Create masks to select samples based on speaker IDs
train_mask = np.isin(speaker_ids, train_speakers)
val_mask = np.isin(speaker_ids, val_speakers)

# Split the data using the masks
X_train, y_train = X[train_mask], y[train_mask]
X_val, y_val = X[val_mask], y[val_mask]

# Check dataset sizes
print(f"Total Dataset Size: {len(X)}")
print(f"Train Dataset Size: {len(X_train)}")
print(f"Expected Validation Dataset Size: {len(X_val)}")

# Convert X, y to TensorFlow dataset
# --- Create tf.data.Datasets ---
train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
train_dataset = train_dataset.shuffle(len(X_train)).batch(BATCH_SIZE).repeat()

valid_dataset = tf.data.Dataset.from_tensor_slices((X_val, y_val))
valid_dataset = valid_dataset.batch(BATCH_SIZE)

# Apply Preprocessing (Augmentation for Training Only)
train_dataset = prepare(train_dataset, augment=True)  # Augmentation applied

# Check if valid_dataset is empty
for x_batch, y_batch in valid_dataset.take(1):
    print(f"Validation Batch Shape: {x_batch.shape}, Labels: {y_batch.shape}")