import torch
import numpy as np
import os
from torch import nn, eq, inference_mode
from torch.nn import functional as F
from random import randint



def accuracy(y_pred, y_true):
    """Simple accuracy function: compares predicted vs. actual labels."""
    correct = eq(y_true, y_pred).sum().item()
    acc = (correct / len(y_pred)) * 100
    return acc


class Res_Layer(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=0):
        super().__init__()
        self.stride = stride

        # self.downsample  = nn.Conv2d(in_channels, out_channels, 1, stride=2, padding=0)
        self.in_channels  = in_channels
        self.out_channels = out_channels

        self.downsample = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, padding=0, bias=False),
            nn.BatchNorm2d(out_channels)
        )

        self.conv1       = nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride, padding=padding)
        self.bn1         = nn.BatchNorm2d(out_channels)
        self.conv2       = nn.Conv2d(in_channels=out_channels, out_channels=out_channels, kernel_size=kernel_size, stride=1, padding=padding)
        self.bn2         = nn.BatchNorm2d(out_channels)
        self.leaky_relu  = nn.LeakyReLU(negative_slope=0.1)


    def forward(self, x):
        identity = x
        # print(f'X size = {x.size()}')

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.leaky_relu(out)
        # print(f'X size = {out.size()}')

        out = self.conv2(out)
        out = self.bn2(out)
        # print(f'X size = {out.size()}')

        if (self.in_channels != self.out_channels or self.stride != 1):
            identity = self.downsample(identity)

        try:  
            out += identity
        except Exception as e:
            print(f'Exception occured: {e}')
            print(f'out size: {out.size()}, identity size {identity.size()}')
            print(f'in channels: {self.in_channels}, out channels: {self.out_channels}')
            raise


        out = self.leaky_relu(out)

        return out


class FACE(nn.Module):
    def __init__(self, num_classes=10):
        """
        A 5-block CNN (conv->BN->LeakyReLU->pool) with FC layers.
        Expects input shape (N, 1, 128, 128).
        """
        super().__init__()

        # Block 1
        self.layer1 = Res_Layer(in_channels=1, out_channels=32, kernel_size=5, stride=2, padding=2)

        # Block 2
        self.layer2 = Res_Layer(in_channels=32, out_channels=64, kernel_size=5, stride=2, padding=2)

        # Block 3
        self.layer3 = Res_Layer(in_channels=64, out_channels=128, kernel_size=3, stride=2, padding=1)

        # Block 4
        self.layer4 = Res_Layer(in_channels=128, out_channels=256, kernel_size=3, stride=2, padding=1)

        # Block 5
        self.layer5 = Res_Layer(in_channels=256, out_channels=256, kernel_size=3, stride=2, padding=1)

        # After 5 blocks => final feature map = (256, 4, 4) => 4096
        self.fc1 = nn.Linear(256 * 4 * 4, 256)
        self.bn_fc1 = nn.BatchNorm1d(256)
        self.dropout = nn.Dropout(p=0.3)
        self.fc2 = nn.Linear(256, num_classes)

        self.leaky_relu = nn.LeakyReLU(negative_slope=0.1)

    def forward(self, x):
        # print(f'X size = {x.size()}')
        x = self.layer1(x)
        # print(f'X size = {x.size()}')
        
        x = self.layer2(x)
        # print(f'X size = {x.size()}')
        
        x = self.layer3(x)
        # print(f'X size = {x.size()}')
        
        x = self.layer4(x)
        # print(f'X size = {x.size()}')
        
        x = self.layer5(x)
        # print(f'X size = {x.size()}')

        # Flatten
        x = x.view(x.size(0), -1)  # => (N, 4096)

        # FC layers
        x = self.fc1(x)
        x = self.bn_fc1(x)
        x = self.leaky_relu(x)
        x = self.dropout(x)
        x = self.fc2(x)

        return x


def train_step(model, dataloader, optim, loss_fn, accuracy_fn, device, epoch, log_dir, log_file):
    """
    Train the model for one epoch, logging batch-level metrics.
    Returns (epoch_avg_loss, epoch_avg_acc).
    """
    model.train()

    # Accumulate entire epoch's sample-level metrics to compute 1% min/max & std at epoch's end
    epoch_losses, epoch_accuracies, epoch_confidences = [], [], []

    # Create or open the batch log file for this epoch
    train_batch_log_path = f"{log_dir}/train_batch_log_epoch_{epoch+1}.csv"
    with open(train_batch_log_path, "w") as log_file:

        for batch_idx, (X, y, txt) in enumerate(dataloader):
            X, y = X.to(device), y.to(device)

            # Forward pass for the whole batch
            y_logits = model(X)
            loss = loss_fn(y_logits, y)

            # Backprop
            optim.zero_grad()
            loss.backward()
            optim.step()

            # Convert entire batch of predictions to metrics
            y_preds = y_logits.argmax(dim=1)
            batch_losses = []
            batch_accuracies = []
            batch_confidences = []

            # Compute sample-level metrics
            for i in range(len(X)):
                single_logits = y_logits[i].unsqueeze(0)
                single_target = y[i].unsqueeze(0)
                single_loss = loss_fn(single_logits, single_target).item()
                single_pred = single_logits.argmax(dim=1)
                single_acc = 1.0 if single_pred.item() == y[i].item() else 0.0

                # Probability (confidence) for the predicted class
                single_probs = torch.softmax(single_logits, dim=1)
                single_conf = single_probs.max().item()

                batch_losses.append(single_loss)
                batch_accuracies.append(single_acc)
                batch_confidences.append(single_conf)

            # Compute batch-level stats
            batch_loss_mean = np.mean(batch_losses)
            batch_loss_std = np.std(batch_losses)
            batch_loss_1pct_min = np.percentile(batch_losses, 1)
            batch_loss_1pct_max = np.percentile(batch_losses, 99)

            batch_acc_mean = 100.0 * np.mean(batch_accuracies)  # store as percentage
            batch_acc_std = np.std(batch_accuracies) * 100.0
            batch_acc_1pct_min = np.percentile(batch_accuracies, 1) * 100.0
            batch_acc_1pct_max = np.percentile(batch_accuracies, 99) * 100.0

            batch_conf_mean = np.mean(batch_confidences)
            batch_conf_std = np.std(batch_confidences)
            batch_conf_1pct_min = np.percentile(batch_confidences, 1)
            batch_conf_1pct_max = np.percentile(batch_confidences, 99)

            # Write to log
            log_file.write(
                f"Batch {batch_idx}: "
                f"Loss=> mean={batch_loss_mean:.5f}, std={batch_loss_std:.5f}, "
                f"1%min={batch_loss_1pct_min:.5f}, 1%max={batch_loss_1pct_max:.5f} | "
                f"Acc=> mean={batch_acc_mean:.2f}%, std={batch_acc_std:.2f}, "
                f"1%min={batch_acc_1pct_min:.2f}%, 1%max={batch_acc_1pct_max:.2f}% | "
                f"Conf=> mean={batch_conf_mean:.5f}, std={batch_conf_std:.5f}, "
                f"1%min={batch_conf_1pct_min:.5f}, 1%max={batch_conf_1pct_max:.5f}\n"
            )

            # Accumulate for entire epoch
            epoch_losses.extend(batch_losses)
            epoch_accuracies.extend(batch_accuracies)
            epoch_confidences.extend(batch_confidences)

            # Optional debug info
            if batch_idx % 50 == 0:
                print(f"\t[Train] Batch {batch_idx}: Loss = {loss:.5f}", file = log_file)

        # Now compute epoch-level stats
        ep_loss_mean = np.mean(epoch_losses)
        ep_loss_std = np.std(epoch_losses)
        ep_loss_1pct_min = np.percentile(epoch_losses, 1)
        ep_loss_1pct_max = np.percentile(epoch_losses, 99)

        ep_acc_mean = 100.0 * np.mean(epoch_accuracies)
        ep_acc_std = 100.0 * np.std(epoch_accuracies)
        ep_acc_1pct_min = 100.0 * np.percentile(epoch_accuracies, 1)
        ep_acc_1pct_max = 100.0 * np.percentile(epoch_accuracies, 99)

        ep_conf_mean = np.mean(epoch_confidences)
        ep_conf_std = np.std(epoch_confidences)
        ep_conf_1pct_min = np.percentile(epoch_confidences, 1)
        ep_conf_1pct_max = np.percentile(epoch_confidences, 99)

        # Write epoch summary to the same file
        log_file.write("\n=== Epoch Summary ===\n")
        log_file.write(
            f"Epoch {epoch+1} (Train): "
            f"Loss=> mean={ep_loss_mean:.5f}, std={ep_loss_std:.5f}, "
            f"1%min={ep_loss_1pct_min:.5f}, 1%max={ep_loss_1pct_max:.5f} | "
            f"Acc=> mean={ep_acc_mean:.2f}%, std={ep_acc_std:.2f}, "
            f"1%min={ep_acc_1pct_min:.2f}%, 1%max={ep_acc_1pct_max:.2f}% | "
            f"Conf=> mean={ep_conf_mean:.5f}, std={ep_conf_std:.5f}, "
            f"1%min={ep_conf_1pct_min:.5f}, 1%max={ep_conf_1pct_max:.5f}\n"
        )

    print(f"[Train] Epoch {epoch+1} => Loss: {ep_loss_mean:.5f}, Acc: {ep_acc_mean:.2f}%, Conf: {ep_conf_mean:.3f}", file = log_file)
    return ep_loss_mean, ep_acc_mean, ep_conf_mean


@inference_mode()
def eval_step(model, dataloader, loss_fn, accuracy_fn, device, epoch, log_dir, log_file):
    """
    Evaluate the model for one epoch, logging batch-level metrics.
    Returns (epoch_avg_loss, epoch_avg_acc).
    """
    model.eval()

    epoch_losses, epoch_accuracies, epoch_confidences = [], [], []

    test_batch_log_path = f"{log_dir}/test_batch_log_epoch_{epoch+1}.csv"
    with open(test_batch_log_path, "w") as log_file:
        for batch_idx, (X, y, txt) in enumerate(dataloader):
            X, y = X.to(device), y.to(device)

            y_logits = model(X)
            loss = loss_fn(y_logits, y)

            # Compute sample-level metrics
            batch_losses = []
            batch_accuracies = []
            batch_confidences = []

            for i in range(len(X)):
                single_logits = y_logits[i].unsqueeze(0)
                single_target = y[i].unsqueeze(0)
                single_loss = loss_fn(single_logits, single_target).item()

                single_pred = single_logits.argmax(dim=1)
                single_acc = 1.0 if single_pred.item() == y[i].item() else 0.0

                single_probs = torch.softmax(single_logits, dim=1)
                single_conf = single_probs.max().item()

                batch_losses.append(single_loss)
                batch_accuracies.append(single_acc)
                batch_confidences.append(single_conf)

            # Batch-level stats
            batch_loss_mean = np.mean(batch_losses)
            batch_loss_std = np.std(batch_losses)
            batch_loss_1pct_min = np.percentile(batch_losses, 1)
            batch_loss_1pct_max = np.percentile(batch_losses, 99)

            batch_acc_mean = 100.0 * np.mean(batch_accuracies)
            batch_acc_std = 100.0 * np.std(batch_accuracies)
            batch_acc_1pct_min = 100.0 * np.percentile(batch_accuracies, 1)
            batch_acc_1pct_max = 100.0 * np.percentile(batch_accuracies, 99)

            batch_conf_mean = np.mean(batch_confidences)
            batch_conf_std = np.std(batch_confidences)
            batch_conf_1pct_min = np.percentile(batch_confidences, 1)
            batch_conf_1pct_max = np.percentile(batch_confidences, 99)

            log_file.write(
                f"Batch {batch_idx}: "
                f"Loss=> mean={batch_loss_mean:.5f}, std={batch_loss_std:.5f}, "
                f"1%min={batch_loss_1pct_min:.5f}, 1%max={batch_loss_1pct_max:.5f} | "
                f"Acc=> mean={batch_acc_mean:.2f}%, std={batch_acc_std:.2f}, "
                f"1%min={batch_acc_1pct_min:.2f}%, 1%max={batch_acc_1pct_max:.2f}% | "
                f"Conf=> mean={batch_conf_mean:.5f}, std={batch_conf_std:.5f}, "
                f"1%min={batch_conf_1pct_min:.5f}, 1%max={batch_conf_1pct_max:.5f}\n"
            )

            epoch_losses.extend(batch_losses)
            epoch_accuracies.extend(batch_accuracies)
            epoch_confidences.extend(batch_confidences)

            if batch_idx % 50 == 0:
                print(f"\t[Test] Batch {batch_idx}: Loss = {loss:.5f}", file = log_file)

        # Epoch-level
        ep_loss_mean = np.mean(epoch_losses)
        ep_loss_std = np.std(epoch_losses)
        ep_loss_1pct_min = np.percentile(epoch_losses, 1)
        ep_loss_1pct_max = np.percentile(epoch_losses, 99)

        ep_acc_mean = 100.0 * np.mean(epoch_accuracies)
        ep_acc_std = 100.0 * np.std(epoch_accuracies)
        ep_acc_1pct_min = 100.0 * np.percentile(epoch_accuracies, 1)
        ep_acc_1pct_max = 100.0 * np.percentile(epoch_accuracies, 99)

        ep_conf_mean = np.mean(epoch_confidences)
        ep_conf_std = np.std(epoch_confidences)
        ep_conf_1pct_min = np.percentile(epoch_confidences, 1)
        ep_conf_1pct_max = np.percentile(epoch_confidences, 99)

        log_file.write("\n=== Epoch Summary ===\n")
        log_file.write(
            f"Epoch {epoch+1} (Test): "
            f"Loss=> mean={ep_loss_mean:.5f}, std={ep_loss_std:.5f}, "
            f"1%min={ep_loss_1pct_min:.5f}, 1%max={ep_loss_1pct_max:.5f} | "
            f"Acc=> mean={ep_acc_mean:.2f}%, std={ep_acc_std:.2f}, "
            f"1%min={ep_acc_1pct_min:.2f}%, 1%max={ep_acc_1pct_max:.2f}% | "
            f"Conf=> mean={ep_conf_mean:.5f}, std={ep_conf_std:.5f}, "
            f"1%min={ep_conf_1pct_min:.5f}, 1%max={ep_conf_1pct_max:.5f}\n"
        )

    print(f"[Test] Epoch {epoch+1} => Loss: {ep_loss_mean:.5f}, Acc: {ep_acc_mean:.2f}%, Conf: {ep_conf_mean:.3f}", file = log_file)
    return ep_loss_mean, ep_acc_mean, ep_conf_mean


# --------------------------
# Final Test - each datapoint
# --------------------------
def final_test_each_datapoint(model, dataset, loss_fn, device, output_path):
    """
    Test the model on each datapoint individually, logging the same metrics
    (mean, std, 1% min/max) for the entire test set.
    """
    model.eval()
    sample_losses, sample_accuracies, sample_confidences = [], [], []

    final_test_log = os.path.join(output_path, "final_test_each_sample.txt")
    with open(final_test_log, "w") as f:
        f.write("=== Final Test (Per-Data-Point) ===\n")
        for i in range(len(dataset)):
            X, y, txt = dataset[i]
            X = X.unsqueeze(0).to(device)
            y_tensor = torch.tensor([y], dtype=torch.long, device=device)

            with torch.inference_mode():
                logits = model(X)
                loss_val = loss_fn(logits, y_tensor).item()
                preds = logits.argmax(dim=1)
                acc = 1.0 if preds.item() == y else 0.0
                probs = torch.softmax(logits, dim=1)
                conf = probs.max().item()

                sample_losses.append(loss_val)
                sample_accuracies.append(acc)
                sample_confidences.append(conf)

        # Compute stats across the entire test set
        mean_loss = np.mean(sample_losses)
        std_loss = np.std(sample_losses)
        loss_1pct_min = np.percentile(sample_losses, 1)
        loss_1pct_max = np.percentile(sample_losses, 99)

        mean_acc = 100.0 * np.mean(sample_accuracies)
        std_acc = 100.0 * np.std(sample_accuracies)
        acc_1pct_min = 100.0 * np.percentile(sample_accuracies, 1)
        acc_1pct_max = 100.0 * np.percentile(sample_accuracies, 99)

        mean_conf = np.mean(sample_confidences)
        std_conf = np.std(sample_confidences)
        conf_1pct_min = np.percentile(sample_confidences, 1)
        conf_1pct_max = np.percentile(sample_confidences, 99)

        # Log to file
        f.write(
            f"Loss => mean={mean_loss:.5f}, std={std_loss:.5f}, "
            f"1%min={loss_1pct_min:.5f}, 1%max={loss_1pct_max:.5f}\n"
            f"Acc => mean={mean_acc:.2f}%, std={std_acc:.2f}, "
            f"1%min={acc_1pct_min:.2f}%, 1%max={acc_1pct_max:.2f}%\n"
            f"Conf => mean={mean_conf:.5f}, std={std_conf:.5f}, "
            f"1%min={conf_1pct_min:.5f}, 1%max={conf_1pct_max:.5f}\n"
        )

    return (mean_loss, mean_acc, mean_conf)
