import tensorflow as tf

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

# Ensure `train_size` is defined
train_size = int(0.8 * len(X))  # 80% training, 20% validation

# Convert X, y to TensorFlow dataset
dataset = tf.data.Dataset.from_tensor_slices((X, y))
dataset = dataset.shuffle(len(X))

# Apply batching AFTER splitting
train_dataset = dataset.take(train_size).batch(BATCH_SIZE).repeat()  # Training dataset
valid_dataset = dataset.skip(train_size).batch(BATCH_SIZE)  # Validation dataset

# Check dataset sizes
print(f"Total Dataset Size: {len(X)}")
print(f"Train Dataset Size: {train_size}")
print(f"Expected Validation Dataset Size: {len(X) - train_size}")

# Apply Preprocessing (Augmentation for Training Only)
train_dataset = prepare(train_dataset, augment=True)  # Augmentation applied

# Check if valid_dataset is empty
for x_batch, y_batch in valid_dataset.take(1):
    print(f"Validation Batch Shape: {x_batch.shape}, Labels: {y_batch.shape}")