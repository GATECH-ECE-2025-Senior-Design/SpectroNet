from tensorflow.keras.callbacks import ReduceLROnPlateau
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Callback to save the best model based on validation loss
checkpoint = ModelCheckpoint("best_model.keras", monitor="val_loss", 
                             save_best_only=True, verbose=1)

# early_stopping = EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True, verbose=1)

# Reduce learning rate when val_loss stops improving
lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, verbose=1, min_lr=1e-6)

# Train model for 20 epochs
history = model.fit(
    train_dataset,  # Training dataset
    epochs=20,  # Number of epochs
    validation_data=valid_dataset,  # Validation dataset
    steps_per_epoch = len(X_train) // BATCH_SIZE,  # No repeat on validation,  # Ensure training steps are correctly calculated
    validation_steps = len(X_val) // BATCH_SIZE,  # Ensure validation steps run
    callbacks=[checkpoint, lr_scheduler]  # Stops early if val_loss stops improving
)

# Check if training history is recorded
print(history.history.keys())