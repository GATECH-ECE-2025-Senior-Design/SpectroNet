import random 
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

import torch
import torch.nn as nn 
import torch.optim as optim
from torchvision import transforms
from torch.utils.data import DataLoader, Subset, DataLoader, Dataset, TensorDataset




def split_data(df, test_size=0.2):
    X = df.iloc[:, 1:].values
    y = df.iloc[:, 0].values
    
    indices = np.random.permutation(len(X))
    split_index = int(len(X) * (1 - test_size))
    
    train_indices = indices[:split_index]
    val_indices = indices[split_index:]
    
    X_train = X[train_indices]
    y_train = y[train_indices]
    X_val = X[val_indices]
    y_val = y[val_indices]
    
    return X_train, y_train, X_val, y_val

class ResizedAudioDataset(Dataset):
    def __init__(self, X, y):
        self.X = X.reshape(-1, 28, 28).astype(np.uint8)   # Reshape hình ảnh về (28, 28)
        self.y = y
        self.transform = transforms.Compose([
            transforms.ToPILImage(), 
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
    
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        image = self.X[idx]
        label = self.y[idx]
        image = self.transform(image) 
        return image, label

class block(nn.Module):
    def __init__(self, in_channels, out_channels, identity_downsample=None, stride=1):
        super(block, self).__init__()
        self.expansion = 4 
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=stride, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.conv3 = nn.Conv2d(out_channels, out_channels*self.expansion, kernel_size=1, stride=1, padding=0)
        self.bn3 = nn.BatchNorm2d(out_channels*self.expansion)
        self.relu = nn.ReLU() 
        self.identyty_downsample = identity_downsample 
        
    def forward(self, x):
        identity = x 
        
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)
        
        x = self.conv3(x)
        x = self.bn3(x)
        
        # if self.identyty_downsample is not None:
        #     identity = self.identyty_downsample(identity)
            
        # x += identity 
        x = self.relu(x)
        return x 
    
    
class CNN(nn.Module):
    def __init__(self, block, layers, image_channels, num_classes):
        super(CNN, self).__init__() 
        self.in_channels = 64
        self.conv1 = nn.Conv2d(image_channels, 64, kernel_size=7, stride=1, padding=3)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        
        # ResNet layers 
        self.layer1 = self._make_layer(block, layers[0], out_channels=64, stride=1)
        self.layer2 = self._make_layer(block, layers[1], out_channels=128, stride=2)
        self.layer3 = self._make_layer(block, layers[2], out_channels=256, stride=2)
        self.layer4 = self._make_layer(block, layers[3], out_channels=512, stride=2)
        
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512*4, num_classes)
        
    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = x.reshape(x.shape[0], -1)
        x = self.fc(x) 
        return x 
        
    def _make_layer(self, block, num_residual_blocks, out_channels, stride):
        identity_downsample = None 
        layers = []
        
        if stride!=1 or self.in_channels != out_channels * 4:
            identity_downsample = nn.Sequential(
                nn.Conv2d(self.in_channels, out_channels*4, kernel_size=1, stride=stride),
                nn.BatchNorm2d(out_channels*4),   
            )
        
        layers.append(block(self.in_channels, out_channels, identity_downsample, stride))
        self.in_channels = out_channels * 4 

        for i in range(num_residual_blocks):
            layers.append(block(self.in_channels, out_channels))
        return nn.Sequential(*layers)
    
    
def AudioCNN(img_channel=1, num_classes=10):
    return CNN(block, [1,1,2,4], img_channel, num_classes)



def train(model, device, train_loader, optimizer, criterion):
    model.train()  # Chuyển mô hình sang chế độ train
    train_loss = 0.0
    correct_train = 0

    for data, target in train_loader:
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        pred_train = output.argmax(dim=1, keepdim=True)
        correct_train += pred_train.eq(target.view_as(pred_train)).sum().item()

    train_loss /= len(train_loader)
    train_accuracy = 100. * correct_train / len(train_loader.dataset)

    return train_loss, train_accuracy

def evaluate(model, device, test_loader, criterion):
    model.eval()  # Chuyển mô hình sang chế độ eval
    test_loss = 0.0
    correct_test = 0

    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()
            pred_test = output.argmax(dim=1, keepdim=True)
            correct_test += pred_test.eq(target.view_as(pred_test)).sum().item()

    test_loss /= len(test_loader.dataset)
    test_accuracy = 100. * correct_test / len(test_loader.dataset)

    return test_loss, test_accuracy



def predict(model, device, data_loader):
    model.eval()  
    all_predictions = []
    
    with torch.no_grad():
        for data in data_loader:
            data = data.to(device)
            outputs = model(data) 
            _, predicted = torch.max(outputs, 1) 
            all_predictions.extend(predicted.cpu().numpy())  
    
    return np.array(all_predictions)



            
class TestDataset(Dataset):
    def __init__(self, X):
        self.X = X.reshape(-1, 28, 28).astype(np.uint8)  # Reshape hình ảnh về (28, 28)
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        image = self.X[idx]
        image = self.transform(image)
        return image


def save_predictions(predictions, truth_values, output_csv_path):
    df_predictions = pd.DataFrame({
        'ImageId': np.arange(1, len(predictions) + 1),
        'Label': predictions,
        'Truth' : truth_values,
        'Output': 'true'
    })
    
    df_predictions.loc[df_predictions['Label'] != df_predictions['Truth'], 'Output'] = 'false'
    df_predictions.to_csv(output_csv_path, index=False)
    return df_predictions



