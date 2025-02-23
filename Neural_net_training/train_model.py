from tensorflow.keras.callbacks import ReduceLROnPlateau
from tensorflow.keras.callbacks import EarlyStopping
# early_stopping = EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)

# Reduce learning rate when val_loss stops improving
lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, verbose=1, min_lr=1e-6)

# Train model for 20 epochs
history = model.fit(
    train_dataset,  # Training dataset
    epochs=20,  # Number of epochs
    validation_data=valid_dataset,  # Validation dataset
    steps_per_epoch=(len(X) - train_size) // BATCH_SIZE,  # No repeat on validation,  # Ensure training steps are correctly calculated
    validation_steps=max((len(X) - train_size) // BATCH_SIZE, 1),  # Ensure validation steps run
    # callbacks=[early_stopping]  # Stops early if val_loss stops improving
)

# Check if training history is recorded
print(history.history.keys())