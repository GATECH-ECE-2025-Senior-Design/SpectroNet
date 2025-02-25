from tensorflow.keras import regularizers
# Define CNN Model (Matches Example
model = tf.keras.models.Sequential([
    tf.keras.layers.Input(shape=(IMAGE_HEIGHT, IMAGE_WIDTH, N_CHANNELS)),
    tf.keras.layers.Conv2D(32, 3, strides=2, padding='same', activation='relu',
                           kernel_regularizer=regularizers.l2(1e-3)),  # Add L2
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Conv2D(64, 3, padding='same', activation='relu', kernel_regularizer=regularizers.l2(1e-3)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Conv2D(128, 3, padding='same', activation='relu', kernel_regularizer=regularizers.l2(1e-3)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dropout(0.5),                           # Higher dropout to prevent memorization
    tf.keras.layers.Dense(N_CLASSES, activation='softmax')
])

# Compile model (Match Example)
model.compile(
    loss='sparse_categorical_crossentropy',  # Matches Example
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),  # Reduce learning rate
    metrics=['accuracy'],
)