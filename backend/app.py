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

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="")
CORS(app, resources={r"/*": {"origins": "*"}})

allowed_files = {"xlsx", "csv", "xml"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_files


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

            # Get prediction
            historical_weights = df['Weight'].values
            weight_tensor = torch.tensor(historical_weights).to(torch.float32)
            new_data = weight_tensor[-30:]
            predicted_weight = RNN_model.predict_weight(model, new_data, data_min, data_max)

            # return jsonify({
            #     "prediction": round(float(predicted_weight)),
            #     "message": "Success",
            #     "dataPoints": len(df),
            #     "startDate": df.index[0].strftime('%Y-%m-%d') if isinstance(df.index, pd.DatetimeIndex) else "N/A",
            #     "endDate": df.index[-1].strftime('%Y-%m-%d') if isinstance(df.index, pd.DatetimeIndex) else "N/A"
            # })
        
            return f"Your predicted weight is {round(float(predicted_weight))} lbs."

            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return jsonify({"error": f"Error processing file: {str(e)}"}), 400

    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


UPLOAD_FOLDER = "/appleHealth/"

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
        return jsonify({"message": f"File uploaded successfully as '{fixed_filename}' to '{file_path}'."}), 200
    except Exception as e:
        return jsonify({"error": f"Error saving file: {str(e)}"}), 500
    

@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return jsonify({"message": "Success!"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
