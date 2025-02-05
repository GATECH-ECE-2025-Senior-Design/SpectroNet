import torch
import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
    def __init__(self, num_classes=10):  # 0-9 = 10 classes
        super(Net, self).__init__()

        # Convolutional Layer 1
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=16, kernel_size=3, stride=1, padding=1)  # 1 dimension -- power by bin & time
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2, padding=0) # 48x48
        self.bn1 = nn.BatchNorm2d(16)  # Batch normalization to stabilize training
        
        # Convolutional Layer 2
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2, padding=0) # 24x24
        self.bn2 = nn.BatchNorm2d(32)  # Batch normalization
        
        # Convolutional Layer 3
        self.conv3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2, padding=0) # 12x12
        self.bn3 = nn.BatchNorm2d(64)  # Batch normalization
        
        # Fully Connected Layer 1
        self.fc1 = nn.Linear(64 * 12 * 12, 256)  # Smaller FC layer
        self.fc2 = nn.Linear(256, num_classes)  # Final classification layer

        # Dropout Layer (helps with noise)
        self.dropout = nn.Dropout(0.5)  # 50% dropout

    def forward(self, x):
        # Apply Conv1 + Pool1 + BatchNorm1
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        
        # Apply Conv2 + Pool2 + BatchNorm2
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        
        # Apply Conv3 + Pool3 + BatchNorm3
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        
        # Flatten the output from Conv3 layer
        x = x.view(-1, 64 * 12 * 12)
        
        # Apply FC1 + Dropout
        x = F.relu(self.fc1(x))
        x = self.dropout(x)  # Apply dropout during training
        
        # Apply FC2 (output layer)
        x = self.fc2(x)
        
        return x

