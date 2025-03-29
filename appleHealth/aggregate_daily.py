import os
import pandas as pd

input_dir = "export"
output_dir = "aggregated"
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if not filename.endswith(".csv"):
        continue

    path = os.path.join(input_dir, filename)
    df = pd.read_csv(path)

    # Skip if no value or startDate
    if "value" not in df.columns or "startDate" not in df.columns:
        continue

    # Parse startDate and coerce bad values to NaT
    df["startDate"] = pd.to_datetime(df["startDate"], errors="coerce")
    df = df.dropna(subset=["startDate", "value"])

    # Convert value to numeric if it's not already
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    # Group by date (ignore time)
    df["date"] = df["startDate"].dt.date
    df_daily = df.groupby("date")["value"].agg(["sum", "mean", "min", "max", "count"]).reset_index()

    # Save to new file
    out_path = os.path.join(output_dir, filename)
    df_daily.to_csv(out_path, index=False)
    print(f"Aggregated: {filename} -> {out_path}")
