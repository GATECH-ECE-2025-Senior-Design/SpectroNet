from tensorflow.keras import mixed_precision
import tensorflow as tf

gpus = tf.config.list_physical_devices('GPU')
print(f"Number of GPUs available: {len(gpus)}")
for gpu in gpus:
    print(gpu)

# Enable Mixed Precision for Faster Training
mixed_precision.set_global_policy('mixed_float16')

# Check Policy
print(f"Mixed precision enabled: {mixed_precision.global_policy()}")