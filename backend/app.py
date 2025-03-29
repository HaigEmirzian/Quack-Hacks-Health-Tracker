from flask import Flask, request, jsonify, render_template, url_for
from flask_cors import CORS
import RNN_model
import torch
import torch.nn as nn
from torch.optim import Adam
import pandas as pd
import io

app = Flask(__name__)
CORS(app)

allowed_files = {'xlsx', 'csv'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_files

@app.route('/', methods=['GET'])
def home():
    return render_template('../frontend/index.html')

@app.route('/prediction', methods=['POST'])
def prediction():
    if request.method == "POST":
        file = request.files.get("file")
        
        if file is None or file.filename == "":
            return jsonify({"error": "No file uploaded"})
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"})
        
        try:
            # Read file content
            file_content = file.read()
            if file.filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                df = pd.read_excel(io.BytesIO(file_content))

            # Configure device
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

            # Process data with fixed window size of 30
            X_train, X_test, y_train, y_test, df, data_min, data_max = RNN_model.load_and_preprocess_data_from_df(df, window_size=30)
            train_loader, test_loader = RNN_model.prepare_data_loaders(X_train, X_test, y_train, y_test)

            # Initialize and train model
            model = RNN_model.Weight_Model().to(device)
            loss_fn = nn.MSELoss()
            optimizer = Adam(model.parameters(), lr=0.001)

            RNN_model.train_model(model, train_loader, loss_fn, optimizer, num_epochs=1000)

            # Get prediction
            historical_weights = df['Weight'].values
            weight_tensor = torch.tensor(historical_weights).to(torch.float32)
            new_data = weight_tensor[-30:]
            predicted_weight = RNN_model.predict_weight(model, new_data, data_min, data_max)

            return jsonify({
                'prediction': round(float(predicted_weight)),
                'message': 'Success'
            })
            
        except Exception as e:
            return jsonify({"error": f'Error during prediction: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)