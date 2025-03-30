from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
import io
from predict import handle_prediction
import torch
import torch.nn as nn
from torch.optim import Adam
import RNN_model  # Make sure this import works
from datetime import datetime, timedelta

from filterData import filterData
from aggregate_daily import aggregateDaily

from filterData import filterData
from aggregate_daily import aggregateDaily

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="")
CORS(app, resources={r"/*": {"origins": "*"}})

allowed_files = {"xlsx", "csv", "xml"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_files

def generate_future_dates(last_date, num_days):
    future_dates = []
    current_date = last_date + pd.Timedelta(days=1)
    for _ in range(num_days):
        future_dates.append(current_date.strftime('%Y-%m-%d'))  # Already in YYYY-MM-DD format
        current_date += pd.Timedelta(days=1)
    return future_dates

def predict_future_weights(model, last_sequence, num_steps, data_min, data_max):
    predicted_weights = []
    current_sequence = ((last_sequence - data_min) / (data_max - data_min)).tolist()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    for _ in range(num_steps):
        input_tensor = torch.tensor(current_sequence[-30:]).to(device).unsqueeze(-1).float()  # Shape: [30, 1]
        input_tensor = input_tensor.unsqueeze(0)  # Shape: [1, 30, 1]
        model.eval()
        with torch.no_grad():
            output = model(input_tensor)
        predicted_value = output.item() * (data_max - data_min) + data_min
        predicted_weights.append(round(float((predicted_value))))  # Round to nearest whole number
        normalized_predicted_value = (predicted_value - data_min) / (data_max - data_min)
        current_sequence.append(normalized_predicted_value)
    return predicted_weights

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/weight", methods=["POST"])
def analyze_weight():
    print("Received weight analysis request")
    try:
        file = request.files.get("file")
        print(f"File received: {file.filename if file else 'No file'}")
        
        if file is None or file.filename == "":
            return jsonify({"error": "No file uploaded"}), 400
            
        try:
            # Read file content
            file_content = file.read()
            if file.filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                df = pd.read_excel(io.BytesIO(file_content))
            
            # Set the 'Date' column as the index
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            else:
                return jsonify({"error": "No 'Date' column found in the file"}), 400
            
            print(f"File processed, shape: {df.shape}")

            # Configure device
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            print(f"Using device: {device}")

            # Process data with fixed window size of 30
            X_train, X_test, y_train, y_test, df, data_min, data_max = RNN_model.load_and_preprocess_data_from_df(df, window_size=30)
            train_loader, test_loader = RNN_model.prepare_data_loaders(X_train, X_test, y_train, y_test)

            # Initialize and train model
            model = RNN_model.Weight_Model().to(device)
            loss_fn = nn.MSELoss()
            optimizer = Adam(model.parameters(), lr=0.001)

            print("Training model...")
            RNN_model.train_model(model, train_loader, loss_fn, optimizer, num_epochs=100)

            # Get single prediction using the original logic
            historical_weights = df['Weight'].values
            weight_tensor = torch.tensor(historical_weights).to(torch.float32)
            new_data = weight_tensor[-30:]
            predicted_weight = RNN_model.predict_weight(model, new_data, data_min, data_max)

            # Get multi-step predictions for the chart
            num_steps = 30  # Predict next 30 days
            predicted_weights = predict_future_weights(model, new_data, num_steps, data_min, data_max)
            
            last_date = pd.to_datetime(df.index[-1])
            future_dates = generate_future_dates(last_date, num_steps)
            
            # Ensure historical dates are in YYYY-MM-DD format without time
            historical = [{'date': date.strftime('%Y-%m-%d'), 'weight': float(weight)} for date, weight in zip(df.index, df['Weight'])]
            predicted = [{'date': date_str, 'weight': weight} for date_str, weight in zip(future_dates, predicted_weights)]
            
            # Prepare the response with the message and chart data
            message = f"Your predicted weight is {round(float(predicted_weight))} lbs in 30 days."
            return jsonify({
                "message": message,
                "historical": historical,
                "predicted": predicted
            })

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return jsonify({"error": f"Error processing file: {str(e)}"}), 400

    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

      
UPLOAD_FOLDER = "appleHealth/"

@app.route("/appleDataUpload", methods=["POST"])
def appleDataUpload():
    file = request.files.get("file")
    # Validate file
    if file is None or file.filename == "":
        return jsonify({"error": "No file uploaded"}), 400
    if not file.filename.endswith('.xml'):
        return jsonify({"error": "File type not allowed. Please upload an XML file."}), 400

    # Define the fixed filename
    fixed_filename = "uploadData.xml"
    file_path = os.path.join(UPLOAD_FOLDER, fixed_filename)

    # Save the file to the upload folder with the fixed filename
    try:
        file.save(file_path)
        
        #Erroring function
        #filterData()
        #aggregateDaily()
        
        return jsonify({"message": f"File uploaded successfully as '{fixed_filename}' to '{file_path}'."}), 200
    except Exception as e:
        return jsonify({"error": f"Error saving file: {str(e)}"}), 500

@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return jsonify({"message": "Success!"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)