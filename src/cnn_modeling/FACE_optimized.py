import torch
from torch import nn, eq, inference_mode
import torch.nn.functional as F
from random import randint
from dataset import get_audio_info


def accuracy(y_pred, y_true):
    """Simple accuracy function: compares predicted vs. actual labels."""
    correct = eq(y_true, y_pred).sum().item()
    acc = (correct / len(y_pred)) * 100
    return acc


class DepthwiseSeparableConv(nn.Module):
    """
    A depthwise-separable convolution block:
      - Depthwise conv (groups=in_channels)
      - BatchNorm
      - Pointwise conv (1x1)
      - Another BatchNorm
    """
    def __init__(self, in_ch, out_ch, kernel_size=3, stride=1, padding=1, negative_slope=0.1):
        super().__init__()
        self.depthwise = nn.Conv2d(
            in_channels=in_ch,
            out_channels=in_ch,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            groups=in_ch,  # ensures depthwise
            bias=False
        )
        self.bn_depth = nn.BatchNorm2d(in_ch)
        self.pointwise = nn.Conv2d(
            in_channels=in_ch,
            out_channels=out_ch,
            kernel_size=1,
            stride=1,
            padding=0,
            bias=False
        )
        self.bn_point = nn.BatchNorm2d(out_ch)
        self.activation = nn.LeakyReLU(negative_slope=negative_slope, inplace=True)

    def forward(self, x):
        x = self.depthwise(x)
        x = self.bn_depth(x)
        x = self.activation(x)
        x = self.pointwise(x)
        x = self.bn_point(x)
        x = self.activation(x)
        return x


class FACE(nn.Module):
    def __init__(self, num_classes=10, dropout_p=0.3):
        """
        FPGA-friendly CNN:
         - 5 blocks of depthwise-separable conv
         - Reduced channel widths (1->16->32->64->128->128)
         - MaxPooling after each block (stride=2)
         - Global Average Pooling + single FC for classification
        Expects input shape (N, 1, 128, 128).
        """
        super().__init__()
        # Block 1: 1 -> 16
        self.block1 = DepthwiseSeparableConv(in_ch=1, out_ch=16, kernel_size=3, stride=1, padding=1)
        
        # Block 2: 16 -> 32
        self.block2 = DepthwiseSeparableConv(in_ch=16, out_ch=32, kernel_size=3, stride=1, padding=1)
        
        # Block 3: 32 -> 64
        self.block3 = DepthwiseSeparableConv(in_ch=32, out_ch=64, kernel_size=3, stride=1, padding=1)
        
        # Block 4: 64 -> 128
        self.block4 = DepthwiseSeparableConv(in_ch=64, out_ch=128, kernel_size=3, stride=1, padding=1)
        
        # Block 5: 128 -> 128
        # (we keep the same number of channels, focusing on deeper features rather than width)
        self.block5 = DepthwiseSeparableConv(in_ch=128, out_ch=128, kernel_size=3, stride=1, padding=1)
        
        # Global Average Pooling to reduce final feature map from 4x4 -> 1x1
        # (since we do 5x max pool with stride=2 on 128x128)
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        
        # Final classification layer + dropout
        self.dropout = nn.Dropout(p=dropout_p)
        self.fc = nn.Linear(128, num_classes)

    def forward(self, x):
        # Each block has a depthwise-separable conv + BN + activation
        # Then we downsample with max_pool2d.
        
        # Block 1
        x = self.block1(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)  # 128->64
        
        # Block 2
        x = self.block2(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)  # 64->32
        
        # Block 3
        x = self.block3(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)  # 32->16
        
        # Block 4
        x = self.block4(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)  # 16->8
        
        # Block 5
        x = self.block5(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)  # 8->4
        
        # Global Average Pool: from (N, 128, 4, 4) -> (N, 128, 1, 1)
        x = self.gap(x)
        
        # Flatten to (N, 128)
        x = x.view(x.size(0), -1)
        
        # Dropout, then final FC
        x = self.dropout(x)
        x = self.fc(x)
        return x


def train_step(model, dataloader, optim, loss_fn, accuracy_fn, device):
    """
    Training loop for a single epoch.
    Returns epoch-averaged (loss, accuracy).
    """
    train_loss = 0.0
    train_acc = 0.0
    model.train()

    for batch_idx, (X, y, txt) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        # Forward pass
        y_logits = model(X)
        # Predictions
        y_preds = y_logits.argmax(dim=1)

        # Calculate metrics
        acc = accuracy_fn(y_preds, y)
        loss = loss_fn(y_logits, y)

        # Backprop
        optim.zero_grad()
        loss.backward()
        optim.step()

        # Accumulate
        train_loss += loss.item()
        train_acc  += acc

        if batch_idx % 50 == 0:
            sample_idx = randint(0, X.shape[0] - 1)
            print(f"\tBatch {batch_idx}: Train loss: {loss:.5f} | Train accuracy: {acc:.2f}%")
            get_audio_info(txt[sample_idx], label=y_preds[sample_idx].item())
            print("----------------------------------------")

    # Averages
    avg_loss = train_loss / len(dataloader)
    avg_acc  = train_acc / len(dataloader)
    print(f"Train loss: {avg_loss:.5f} | Train accuracy: {avg_acc:.2f}%")
    return avg_loss, avg_acc


@inference_mode()
def eval_step(model, dataloader, optim, loss_fn, accuracy_fn, device):
    """
    Evaluation loop for a single epoch.
    Returns epoch-averaged (loss, accuracy).
    """
    test_loss = 0.0
    test_acc  = 0.0
    model.eval()

    for batch_idx, (X, y, txt) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        y_logits = model(X)
        y_preds = y_logits.argmax(dim=1)

        acc = accuracy_fn(y_preds, y)
        loss = loss_fn(y_logits, y)

        test_loss += loss.item()
        test_acc  += acc

        if batch_idx % 50 == 0:
            sample_idx = randint(0, X.shape[0] - 1)
            print(f"\tBatch {batch_idx}: Test loss: {loss:.5f} | Test accuracy: {acc:.2f}%")
            get_audio_info(txt[sample_idx], label=y_preds[sample_idx].item())
            print("----------------------------------------")

    # Averages
    avg_loss = test_loss / len(dataloader)
    avg_acc  = test_acc / len(dataloader)
    print(f"Test loss: {avg_loss:.5f} | Test accuracy: {avg_acc:.2f}%")
    return avg_loss, avg_acc
