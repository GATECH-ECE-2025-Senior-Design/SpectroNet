import numpy as np
import sounddevice as sd
import torch
import torchaudio
import torch.nn.functional as F
import matplotlib.pyplot as plt
import time
import tensorflow as tf  # For Keras model loading

# --- Load the trained model ---
model = tf.keras.models.load_model("best_model.keras")
print("Loaded model.")

# --- Configuration parameters ---
sample_rate = 8000            # samples per second
n_fft = 384                   # FFT window size
hop_length = 64               # hop size
n_mels = 96                   # number of mel bins

# Buffer length to get 96 time frames
buffer_length = 6464
audio_buffer = np.zeros(buffer_length, dtype=np.float32)
current_mel_spec = None

# Device for torch (GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- Create mel spectrogram transform (power spectrogram) ---
mel_transform = torchaudio.transforms.MelSpectrogram(
    sample_rate=sample_rate,
    n_fft=n_fft,
    hop_length=hop_length,
    n_mels=n_mels,
    power=2.0
).to(device)

# --- Set up matplotlib display ---
plt.ion()
fig, ax = plt.subplots()
img_data = np.zeros((n_mels, 96))
img = ax.imshow(img_data, aspect='auto', origin='lower', interpolation='none', cmap='Greens')
ax.set_title('Real-Time Mel Spectrogram')
ax.set_xlabel('Time Frames')
ax.set_ylabel('Mel Bins')
plt.colorbar(img, ax=ax)
plt.show()

def audio_callback(indata, frames, time_info, status):
    global audio_buffer, current_mel_spec
    if status:
        print("Audio status:", status)
    
    # Update the rolling buffer with new samples (assuming single channel)
    new_samples = indata[:, 0]
    num_new = len(new_samples)
    audio_buffer = np.roll(audio_buffer, -num_new)
    audio_buffer[-num_new:] = new_samples

    # --- Active Signal Cropping ---
    # Lower the threshold slightly to capture quieter speech portions
    threshold = 0.005  
    active_indices = np.where(np.abs(audio_buffer) > threshold)[0]
    if len(active_indices) > 0:
        last_active = active_indices[-1]
        start_idx = max(0, last_active - buffer_length + 1)
        cropped_buffer = audio_buffer[start_idx:last_active+1]
        if len(cropped_buffer) < buffer_length:
            cropped_buffer = np.pad(cropped_buffer, (buffer_length - len(cropped_buffer), 0), mode='constant')
    else:
        cropped_buffer = audio_buffer

    # Convert cropped buffer to torch tensor and compute mel spectrogram
    audio_tensor = torch.tensor(cropped_buffer, dtype=torch.float32, device=device).unsqueeze(0)  # [1, buffer_length]
    mel_spec = mel_transform(audio_tensor)  # shape: [1, n_mels, time_frames]

    # --- Convert to decibel scale using per-example peak as reference ---
    ref_value = mel_spec.max() if mel_spec.max() > 0 else torch.tensor(1e-10, device=device)
    mel_spec_db = 10 * torch.log10(torch.clamp(mel_spec / ref_value, min=1e-10))
    mel_spec_db = torch.clamp(mel_spec_db, min=-80)

    # --- Ensure fixed 96 time frames ---
    current_frames = mel_spec_db.shape[-1]
    if current_frames >= 96:
        mel_spec_db = mel_spec_db[..., -96:]
    else:
        pad_amt = 96 - current_frames
        mel_spec_db = F.pad(mel_spec_db, (pad_amt, 0), mode='constant', value=-80)
    
    # Debug print: show the dB range
    spec_np = mel_spec_db.cpu().numpy()
    print(f"Spectrogram dB range: min={spec_np.min():.2f} max={spec_np.max():.2f}")
    current_mel_spec = mel_spec_db

# --- Set up the audio input stream ---
stream = sd.InputStream(
    channels=1,
    samplerate=sample_rate,
    callback=audio_callback,
    blocksize=hop_length,
    # device=3,  # Uncomment and adjust if needed.
)

# Open a file to write predictions.
with open("predictions.txt", "w") as pred_file:
    # Write the device being used as the first line in predictions.txt.
    if device.type == "cuda":
        pred_file.write("Using GPU\n")
    else:
        pred_file.write("Using CPU\n")
    pred_file.write("Starting live audio stream and visualization. Speak into your microphone!\n")
    with stream:
        start_time = time.time()
        duration = 10  # Run for 10 seconds.
        while time.time() - start_time < duration:
            if current_mel_spec is not None:
                # Get current spectrogram (shape: [n_mels, 96] with dB values in approximately [-80, 0])
                spec_img = current_mel_spec.cpu().numpy()[0]
                img.set_data(spec_img)
                img.set_clim(-80, 0)
                fig.canvas.draw_idle()

                # --- PREPROCESS FOR MODEL ---
                # Normalize from [-80, 0] to [0, 1] and add channel dimension.
                normalized_spec = (spec_img + 80.0) / 80.0
                input_spec = normalized_spec.reshape(1, n_mels, 96, 1)

                # --- Only run prediction if there is significant signal ---
                if not np.allclose(spec_img, -80, atol=1e-3):
                    pred = model.predict(input_spec)
                    softmax_prob = pred[0]
                    max_prob = softmax_prob.max()
                    if max_prob > 0.98:
                        predicted_class = int(softmax_prob.argmax())
                        prediction_text = f"Prediction: {predicted_class} with probability {max_prob:.2f}\n"
                        print(prediction_text.strip())
                        pred_file.write(prediction_text)
                        pred_file.flush()
                else:
                    print("Skipping prediction due to silence.")
            plt.pause(0.01)
