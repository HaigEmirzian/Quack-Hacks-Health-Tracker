import torch
import torch.nn as nn
from torch.optim import Adam
import RNN_model


def handle_prediction(df):
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Preprocess data
        X_train, X_test, y_train, y_test, df, data_min, data_max = RNN_model.load_and_preprocess_data_from_df(df, window_size=30)
        train_loader, test_loader = RNN_model.prepare_data_loaders(X_train, X_test, y_train, y_test)

        # Train model
        model = RNN_model.Weight_Model().to(device)
        loss_fn = nn.MSELoss()
        optimizer = Adam(model.parameters(), lr=0.001)
        RNN_model.train_model(model, train_loader, loss_fn, optimizer, num_epochs=100)

        # Predict
        historical_weights = df["Weight"].values
        weight_tensor = torch.tensor(historical_weights).to(torch.float32)
        new_data = weight_tensor[-30:]
        predicted_weight = RNN_model.predict_weight(model, new_data, data_min, data_max)

        return {
            "prediction": round(float(predicted_weight)),
            "message": "Success"
        }
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        raise
