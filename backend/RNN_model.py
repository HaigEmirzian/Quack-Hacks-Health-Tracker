from pandas import read_excel
from sklearn.model_selection import train_test_split
import torch 
from torch.nn import Sequential
from torch import nn
from torch.optim import Adam
from torch.utils.data import TensorDataset

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_and_preprocess_data(file_path, window_size=30):
    df = read_excel(file_path)
    return load_and_preprocess_data_from_df(df, window_size)


def prepare_data_loaders(X_train, X_test, y_train, y_test, batch_size=32):
    train_data = TensorDataset(X_train, y_train)
    test_data = TensorDataset(X_test, y_test)

    train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_data, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader


class Weight_Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = Sequential(
            nn.LSTM(input_size=1, hidden_size=64, num_layers=2, batch_first=True),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        lstm_out, _ = self.model[0](x)
        lstm_out_last = lstm_out[:, -1, :]
        output = self.model[1](lstm_out_last)
        return output


def train_model(model, train_loader, loss_fn, optimizer, num_epochs):
    for epoch in range(1, num_epochs + 1):
        epoch_loss = 0
        for batch in train_loader:
            X_batch, y_batch = batch
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            y_batch = y_batch.view(-1, 1)

            # Forward pass
            y_hat = model(X_batch)
            loss = loss_fn(y_hat, y_batch)

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

<<<<<<< HEAD
        if epoch % 100 == 0:
=======
        if epoch % 10 == 0:
>>>>>>> 8f2a03704a78bce46c181e882e9349174b184952
            print(f"Epoch {epoch} Loss: {epoch_loss / len(train_loader)}")


def evaluate_model(model, test_loader, loss_fn, data_min, data_max):
    model.eval()
    all_predictions = []
    all_targets = []
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            y_batch = y_batch.view(-1, 1)
            y_hat = model(X_batch)
            all_predictions.append(y_hat)
            all_targets.append(y_batch)
    
    predictions = torch.cat(all_predictions, dim=0)
    targets = torch.cat(all_targets, dim=0)
    mse = torch.mean((predictions - targets) ** 2)
    rmse = torch.sqrt(mse)
    rmse_pounds = rmse.item() * (data_max - data_min)

    print(f"\nTest RMSE in pounds: {rmse_pounds:.4f} lbs")


def predict_weight(model, new_data, data_min, data_max):
    model.eval()
    new_data = (new_data - data_min) / (data_max - data_min)
    new_data = new_data.clone().detach().float().to(device)
    new_data = new_data.view(1, -1, 1)
    
    with torch.no_grad():
        prediction = model(new_data)

    denormalized_prediction = prediction.item() * (data_max - data_min) + data_min
    print(f"\nFuture weight: {denormalized_prediction:.0f} pounds")
    
    return float(denormalized_prediction)


def load_and_preprocess_data_from_df(df, window_size=30):
    weights = df['Weight'].values
    weight_tensor = torch.tensor(weights).to(torch.float32)
    
    data_min = weight_tensor.min()
    data_max = weight_tensor.max()
    
    def normalize_data(weight_tensor, data_min, data_max):
        return (weight_tensor - data_min) / (data_max - data_min)

    normalized_weights = normalize_data(weight_tensor, data_min, data_max)

    def sliding_window(normalized_weights, window_size):
        for i in range(len(normalized_weights) - window_size):
            window = normalized_weights[i:i + window_size]
            output = normalized_weights[i + window_size]
            yield window, output

    data = list(sliding_window(normalized_weights, window_size))
    X = [x[0] for x in data]
    y = [x[1] for x in data]
    
    X = torch.stack(X).numpy()
    y = torch.stack(y).numpy()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.float32)

    return X_train, X_test, y_train, y_test, df, data_min, data_max


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, df, data_min, data_max = load_and_preprocess_data("Weight_Loss_Journey.xlsx", window_size=30)
    
    train_loader, test_loader = prepare_data_loaders(X_train, X_test, y_train, y_test)

    model = Weight_Model().to(device)
    loss_fn = nn.MSELoss()
    optimizer = Adam(model.parameters(), lr=0.001)

<<<<<<< HEAD
    train_model(model, train_loader, loss_fn, optimizer, num_epochs=1000)
=======
    train_model(model, train_loader, loss_fn, optimizer, num_epochs=100)
>>>>>>> 8f2a03704a78bce46c181e882e9349174b184952

    evaluate_model(model, test_loader, loss_fn, data_min, data_max)

    historical_weights = df['Weight'].values
    weight_tensor = torch.tensor(historical_weights).to(torch.float32)

    new_data = weight_tensor[-30:]
    predicted_weight = predict_weight(model, new_data, data_min, data_max)
