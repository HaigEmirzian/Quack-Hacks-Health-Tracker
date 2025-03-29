from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
import io
from predict import handle_prediction

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="")
CORS(app)

allowed_files = {"xlsx", "csv"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_files


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/prediction", methods=["POST"])
def prediction():
    file = request.files.get("file")

    if file is None or file.filename == "":
        return jsonify({"error": "No file uploaded"})
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"})

    try:
        file_content = file.read()
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_excel(io.BytesIO(file_content))

        # Call the external prediction handler
        result = handle_prediction(df)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Error during prediction: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True)
