import os
import datetime
import numpy as np
import torch
import torchvision.transforms as T
import matplotlib.pyplot as plt

from FACE import FACE, train_step, eval_step, accuracy, final_test_each_datapoint
from dataset import create_audio_datasets

# --------------------------
# Hyperparameters
# --------------------------
BATCH_SIZE         = 64
EPOCHS             = 80
# INIT_LR            = 2.5e-5
# WEIGHT_DECAY       = 0.5e-6
INIT_LR            = 8e-5
WEIGHT_DECAY       = 1e-7
EARLYSTOP_PATIENCE = 7

# --------------------------
# Data transforms
# --------------------------
feature_transform = T.Compose([
    T.ToPILImage(),
    T.Resize((128, 128)),
    T.ToTensor()
])

label_transform = T.Compose([])

# --------------------------
# Paths & Setup
# --------------------------
current_directory = os.path.dirname(os.path.realpath(__file__))
datasets_folder   = os.path.join(current_directory, "..", "datasets")

input_dir = os.path.join(datasets_folder, "digits")
# input_dir = os.path.join(datasets_folder, "digits", "01")
output_dir = os.path.join(current_directory, "..", "output")
os.makedirs(output_dir, exist_ok=True)

# Create a timestamped output directory
# timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
run_output_dir = os.path.join(output_dir, "run_new_augmented_70_30_test_train_lr_8e-5_decay_1e-7")
os.makedirs(run_output_dir, exist_ok=True)
global_log = os.path.join(run_output_dir, "output.log")
global_log = open(global_log)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)} is available.", file=global_log)
else:
    print("No GPU available. Training on CPU.", file=global_log)

# Optional: Quick check of one file
# sample_wav = os.path.join(input_dir, "01", "2_01_0.wav")
# get_audio_info(sample_wav, show_melspec=True)

# --------------------------
# Create Datasets & Loaders
# --------------------------
train_ds, test_ds = create_audio_datasets(input_dir, feature_transform=feature_transform, label_transform=label_transform, train_size=0.80, seed=42)
train_dataloader = torch.utils.data.DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
test_dataloader  = torch.utils.data.DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False)

print("Length of training dataset:", len(train_ds), file=global_log)
print("Length of testing dataset:", len(test_ds), file=global_log)

train_images, train_labels, train_text = next(iter(train_dataloader))
print("Train batch shape:", train_images.shape, train_labels.shape, file=global_log)

# Example mel-spectrogram
# example_idx = 0
# get_audio_info(train_text[example_idx], show_melspec=True, label=train_labels[example_idx].item())

# --------------------------
# Model, Loss, Optim
# --------------------------
model = FACE(num_classes=10).to(device)
loss_fn = torch.nn.CrossEntropyLoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=INIT_LR,
    betas=(0.9, 0.999),
    weight_decay=WEIGHT_DECAY
)

# Reduce LR if test loss does not improve after 3 epochs
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.1, patience=3, verbose=True
)

# --------------------------
# Track Metrics (per epoch)
# --------------------------
train_loss_history = []
train_acc_history  = []
train_conf_history = []

test_loss_history = []
test_acc_history  = []
test_conf_history = []

best_loss = float('inf')
epochs_no_improve = 0

# --------------------------
# Training Loop
# --------------------------
for epoch in range(EPOCHS):
    print(f"\nEpoch {epoch+1}/{EPOCHS} --------------------------", file=global_log)

    # --- Train Step (with per-batch logging) ---
    tr_loss, tr_acc, tr_conf = train_step(
        model, train_dataloader, optimizer, loss_fn, accuracy, device, epoch, run_output_dir, global_log
    )

    # --- Eval Step (with per-batch logging) ---
    te_loss, te_acc, te_conf = eval_step(
        model, test_dataloader, loss_fn, accuracy, device, epoch, run_output_dir, global_log
    )

    # Store for plotting
    train_loss_history.append(tr_loss)
    train_acc_history.append(tr_acc)
    train_conf_history.append(tr_conf)

    test_loss_history.append(te_loss)
    test_acc_history.append(te_acc)
    test_conf_history.append(te_conf)

    # Scheduler step based on test_loss
    scheduler.step(te_loss)

    # Early Stopping
    if te_loss < best_loss:
        best_loss = te_loss
        epochs_no_improve = 0
        torch.save(model.state_dict(), "best_model_weights.pth")
        
    else:
        epochs_no_improve += 1
        if epochs_no_improve >= EARLYSTOP_PATIENCE:
            print(f"Early stopping triggered (no improvement for {EARLYSTOP_PATIENCE} epochs).", file=global_log)
            break

print("\nTraining complete!", file=global_log)



print("\nPerforming final per-datapoint test...", file=global_log)
model.load_state_dict(torch.load('best_model_weights.pth', weights_only=True))
final_loss, final_acc, final_conf = final_test_each_datapoint(
    model, test_ds, loss_fn, device, run_output_dir
)
print(f"Final Test - Per-Data-Point: Loss={final_loss:.5f}, Acc={final_acc:.2f}%, Conf={final_conf:.3f}", file=global_log)

# --------------------------
# Plot & Save Curves
# --------------------------
# We'll create a separate figure for each metric (Loss, Acc, Conf),
# each containing both training + testing lines.

# 1) Loss
plt.figure(figsize=(7,5))
plt.plot(train_loss_history, label='Train Loss')
plt.plot(test_loss_history, label='Test Loss')
plt.title('Loss vs. Epoch')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
loss_plot_path = os.path.join(run_output_dir, 'loss_vs_epoch.png')
plt.savefig(loss_plot_path)
plt.close()

# 2) Accuracy
plt.figure(figsize=(7,5))
plt.plot(train_acc_history, label='Train Acc')
plt.plot(test_acc_history, label='Test Acc')
plt.title('Accuracy vs. Epoch')
plt.xlabel('Epoch')
plt.ylabel('Accuracy (%)')
plt.legend()
acc_plot_path = os.path.join(run_output_dir, 'accuracy_vs_epoch.png')
plt.savefig(acc_plot_path)
plt.close()

# 3) Confidence
plt.figure(figsize=(7,5))
plt.plot(train_conf_history, label='Train Conf')
plt.plot(test_conf_history, label='Test Conf')
plt.title('Confidence vs. Epoch')
plt.xlabel('Epoch')
plt.ylabel('Confidence')
plt.legend()
conf_plot_path = os.path.join(run_output_dir, 'confidence_vs_epoch.png')
plt.savefig(conf_plot_path)
plt.close()

print("All logs and plots saved to:" +  run_output_dir, file=global_log)
