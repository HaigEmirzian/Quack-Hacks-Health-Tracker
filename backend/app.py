from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
import io
from predict import handle_prediction
import requests
import time

from filterData import filterData
from aggregate_weekly import aggregateWeekly

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="")
CORS(app)

allowed_files = {"xlsx", "csv"}

globalSavedInsights = None

def get_databricks_insight(category_name, category_data):
    """
    Send CSV data to the Databricks API and return the generated insight.
    
    Args:
        category_name (str): The category name (e.g., 'stepcount').
        category_data (str): The content of the CSV file as a string.
    
    Returns:
        str: The insight from the API or an error message if the request fails.
    """
    url = "https://dbc-81784a62-a9c5.cloud.databricks.com/serving-endpoints/QuackHacks_Health_Insights/invocations"
    
    # Retrieve token from environment variable
    token = os.getenv("DATABRICKS_TOKEN")
    if not token:
        raise ValueError("DATABRICKS_TOKEN environment variable is not set")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Format the prompt with category name and data
    prompt = f"""I will provide you with data from a specific category in the Apple Health app. Your task is to analyze the data and detect any significant patterns, trends, or anomalies. Please give a TWO SENTENCE summary and suggest potential correlations or insights that are useful. Only include normal sentence structure and do not go longer than TWO SENTENCES.

Category: {category_name}

Data:
{category_data}
"""
    
    payload = {
        "max_tokens": 200,
        "messages": [
            {
                "content": prompt,
                "role": "user"
            }
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            # Assuming the insight is in 'choices[0].message.content' (adjust if different)
            data = response.json()
            insight = data.get("choices", [{}])[0].get("message", {}).get("content", "No insight found")
            return insight
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
    except Exception as e:
        return f"Error generating insight: {str(e)}"


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


UPLOAD_FOLDER = "appleHealth/"
AGGREGATED_DIR = "aggregated/"

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
        
        global globalSavedInsights

        #Erroring function
        filterData()
        aggregateWeekly()

        # Generate insights from specific CSV files
        insights = {}
        specific_files = ["activeenergyburned.csv", "heartrate.csv", "stepcount.csv"]

        for csv_file in specific_files:
            csv_path = os.path.join(AGGREGATED_DIR, csv_file)
            if os.path.exists(csv_path):
                with open(csv_path, "r") as f:
                    category_data = f.read()
                category_name = os.path.splitext(csv_file)[0]
                insight = get_databricks_insight(category_name, category_data)
                insights[csv_file] = insight
                print(insights)
            else:
                insights[csv_file] = f"File not found: {csv_file}"
            # Return success message and insights

            #Cache insights
            globalSavedInsights = insights
        return jsonify({
                "message": f"File uploaded successfully as '{fixed_filename}' to '{file_path}'.",
                "insights": insights
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error saving file: {str(e)}"}), 500
    
MAX_WAIT_TIME = 60  # Maximum wait time in seconds
CHECK_INTERVAL = 1  # How often to check (in seconds)

@app.route("/overallInsights", methods=["GET"])
def overallInsights():
    # Start a timer to track how long we've waited
    start_time = time.time()
    print(f"GLOBALINSIGHTS: {globalSavedInsights}")
    
    # Wait until globalSavedInsights is set or timeout occurs
    while not globalSavedInsights:
        if time.time() - start_time > MAX_WAIT_TIME:
            return jsonify({"error": "Timeout waiting for insights"}), 500
        time.sleep(CHECK_INTERVAL)
    
    # Once globalSavedInsights is set, proceed with the API call
    url = "https://dbc-81784a62-a9c5.cloud.databricks.com/serving-endpoints/QuackHacks_Health_Insights/invocations"
    
    # Retrieve token from environment variable
    token = os.getenv("DATABRICKS_TOKEN")
    if not token:
        raise ValueError("DATABRICKS_TOKEN environment variable is not set")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    print(f"GLOBALINSIGHTS: {globalSavedInsights}")

    # Format the prompt with the insights
    prompt = f"""
        Here is a list of all of the health insights which are derived from Apple Watch Data. Tell me the overall standing of my health according to these insights in TWO SENTENCES. Use normal sentence format only.

        Insights:
        {globalSavedInsights} 
    """

    payload = {
        "max_tokens": 200,
        "messages": [
            {
                "content": prompt,
                "role": "user"
            }
        ],
        "temperature": 0.1
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            insight = data.get("choices", [{}])[0].get("message", {}).get("content", "No overall insight found")
            return insight
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
    except Exception as e:
        return f"Error generating insight: {str(e)}"
    
@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return jsonify({"message": "Success!"})

if __name__ == "__main__":
    app.run(debug=True)
