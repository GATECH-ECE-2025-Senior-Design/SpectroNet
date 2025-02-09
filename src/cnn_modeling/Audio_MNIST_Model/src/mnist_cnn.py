from mnist_funcs import *


# Hyperparameter
IS_TRAIN = True   # if you want to train again from the beginning, set IS_TRAIN = True

NUM_EPOCHS = 50 
BATCH_SIZE = 64
LEARNING_RATE = 0.01 



df = pd.read_csv('../dataset/train.csv')


# print(df.head(5))
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)} is available.")
else:
    print("No GPU available. Training will run on CPU.")

X_train, y_train, X_val, y_val = split_data(df)
train_dataset = ResizedAudioDataset(X_train, y_train)
val_dataset = ResizedAudioDataset(X_val, y_val)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

print(X_train.shape)
print(y_train.shape)
print(X_val.shape)
print(y_val.shape)
for data, target in train_loader:
    print(data.shape)  
    print(target.shape)
    plt.imshow(data[0].reshape((28, 28)), cmap='gray')
    print(target[0].item())
    break


num_classes = 10
num_images_per_class = 10 
class_images = {i: [] for i in range(num_classes)}

for img, label in train_dataset:
    if len(class_images[label])<num_images_per_class:
        class_images[label].append(img)

fig, axes = plt.subplots(nrows=num_classes, ncols=num_images_per_class, figsize=(12, 12))
fig.suptitle('MNIST dataset - 10x10 Grid', fontsize=16)

for class_idx in range(num_classes):
    for img_idx in range(num_images_per_class):
        ax = axes[class_idx, img_idx]
        img = class_images[class_idx][img_idx].numpy().squeeze()
        ax.imshow(img, cmap='gray')
        ax.axis('off')
        
# plt.tight_layout()
# plt.subplots_adjust(top=0.95)
# plt.show()


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
net = AudioCNN(num_classes=num_classes).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=LEARNING_RATE, momentum=0.9)


if IS_TRAIN:
    print("TRAININGGGGG")
    train_losses = []
    val_losses = []
    train_accuracies = []
    val_accuracies = []
    best_accuracy = 0.0
    best_model = None

    for epoch in range(NUM_EPOCHS):
        print(f'Start training epoch: {epoch+1}/{NUM_EPOCHS}')

        epoch_train_loss, train_accuracy = train(net, device, train_loader, optimizer, criterion)
        train_losses.append(epoch_train_loss)
        train_accuracies.append(train_accuracy)

        val_loss, val_accuracy = evaluate(net, device, val_loader, criterion)
        val_losses.append(val_loss)
        val_accuracies.append(val_accuracy)

        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            best_model = net.state_dict()
            torch.save(best_model, 'best_model.pth')

        print(f'Epoch {epoch + 1}, Train Loss: {epoch_train_loss:.4f}, val Loss: {val_loss:.4f}, '
              f'Train Accuracy: {train_accuracy:.2f}%, val Accuracy: {val_accuracy:.2f}%')

    
if IS_TRAIN:
    # Plotting the results
    epochs = range(1, NUM_EPOCHS + 1)
    plt.figure(figsize=(12, 5))

    # Plot train and val loss
    plt.subplot(1, 2, 1)
    plt.plot(epochs, train_losses, 'r', label='Training loss')
    plt.plot(epochs, val_losses, 'b', label='val loss')
    plt.title('Training and val loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    # Plot train and val accuracy
    plt.subplot(1, 2, 2)
    plt.plot(epochs, train_accuracies, 'r', label='Training accuracy')
    plt.plot(epochs, val_accuracies, 'b', label='val accuracy')
    plt.title('Training and val accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy (%)')
    plt.legend()

    # plt.show()

    # Save the best model
    torch.save(best_model, 'best_model.pth')
    print(f'Best model saved with accuracy: {best_accuracy:.2f}%')
    
    
if IS_TRAIN:
    model = net.to(device)
    model.load_state_dict(torch.load('best_model.pth', map_location=device)) 
    model.eval()
else:
    model = net.to(device)
    model.load_state_dict(torch.load('best_model.pth', map_location=device)) 
    model.eval()
    
val_loss, val_accuracy = evaluate(model, device, val_loader, criterion)
print(f'val Loss: {val_loss:.4f}, val Accuracy: {val_accuracy:.2f}%')



indices = random.sample(range(len(val_dataset)), 10)
samples = torch.utils.data.Subset(val_dataset, indices)
sample_loader = DataLoader(samples, batch_size=BATCH_SIZE, shuffle=False)

with torch.no_grad():
    for data, target in sample_loader:
        data, target = data.to(device), target.to(device)
        output = model(data)
        pred = output.argmax(dim=1, keepdim=True)

        for i in range(len(data)):
            plt.imshow(data[i].cpu().numpy().transpose(1, 2, 0), cmap='gray')
            plt.title(f'Predicted: {pred[i].item()}, Actual: {target[i].item()}')
            # plt.show()
            
df_test = pd.read_csv('../dataset/test.csv')
real_values = df_test.iloc[:, 0]

df_test.drop(columns=df_test.columns[0], axis=1, inplace=True)

X_test = df_test.values  
test_dataset = TestDataset(X_test)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
predictions = predict(model, device, test_loader)

df_predictions = save_predictions(predictions, real_values, '/home/hice1/jcochran66/code/practice_CNN/PracticeCNN/submission.csv')
# df_predictions.head(5)
def save_predictions(predictions, truth_values, output_csv_path):
    df_predictions = pd.DataFrame({
        'ImageId': np.arange(1, len(predictions) + 1),
        'Label': predictions,
        'Truth' : truth_values,
        'Output': 'true'
    })