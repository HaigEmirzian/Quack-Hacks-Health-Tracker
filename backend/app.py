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

globalSavedInsights = {}

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
    prompt = f"""I will provide you with data from a specific category in the Apple Health app. Your task is to analyze the data and detect any significant patterns, trends, or anomalies. Please give a very short summary and suggest potential correlations or insights that are useful. Only include normal sentence structure.

Category: {category_name}

Data:
{category_data}

Please provide an analysis of any recurring patterns, changes over time, or noteworthy trends based on the data.
"""
    
    payload = {
        "max_tokens": 75,
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

        return jsonify(
        {
            "insights": {
                "activeenergyburned.csv": "The data on active energy burned shows a significant increase over time, with values rising substantially from 2015 to 2022 and remaining high thereafter. A notable pattern is the fluctuation in energy burned on a weekly basis, with some weeks showing much higher values than others. There appears to be a seasonal trend, with higher energy burned during certain periods of the year, potentially",
                "heartrate.csv": "The data shows a general fluctuation in heart rate over time, with some notable increases and decreases. One potential correlation is that heart rate tends to be higher in the winter months, as seen in the data from 2017 and 2024-2025, where heart rates are often above 80. Additionally, there appears to be a trend of increasing heart rate variability",
                "stepcount.csv": "The provided data on step count from the Apple Health app shows significant variability over time, but some patterns and trends can be observed. There is a notable increase in step count over the years, with a general upward trend from 2015 to 2023, indicating an improvement in physical activity. However, there are periods of fluctuation, with some weeks showing significantly lower step",
            },
            "message": "File uploaded successfully as 'uploadData.xml' to 'appleHealth/uploadData.xml'.",
        }
    )


        file.save(file_path)
        
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
                insight = "This is a hard coded response -- get_databricks_insight(category_name, category_data)"
                insights[csv_file] = insight
                print(insights)
            else:
                insights[csv_file] = f"File not found: {csv_file}"
            print(time.time())
            # Return success message and insights

            #Cache insights
            globalSavedInsights = insights
        return jsonify({
                "message": f"File uploaded successfully as '{fixed_filename}' to '{file_path}'.",
                "insights": insights
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error saving file: {str(e)}"}), 500
    
@app.route("/overallInsights", methods=["GET"])
def overallInsights():
    # Check if globalOverallInsight is empty or not defined
    if not globalSavedInsights:  # Assumes globalOverallInsight is defined globally
        return jsonify({"error": "No insights available"}), 400

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
    prompt = f"""
        Here is a list of all of the health insights which are derived from Apple Watch Data. Tell me the overall standing of my health according to these insights in a very brief summary. Use normal sentence format only.

        Insights:
        {globalSavedInsights} 
    """

    payload = {
        "max_tokens": 100,
        "messages": [
            {
                "content": prompt,
                "role": "user"
            }
        ],
        "temperature": 0.1
    }

    try:
        '''
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            # Assuming the insight is in 'choices[0].message.content' (adjust if different)
            data = response.json()
            insight = data.get("choices", [{}])[0].get("message", {}).get("content", "No overall insight found")
            return insight
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")'''
        return "THIS IS A HARD CODED RESPONSE"
    except Exception as e:
        return f"Error generating insight: {str(e)}"

@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return jsonify({"message": "Success!"})

if __name__ == "__main__":
    app.run(debug=True)
