import os
import pandas as pd


def aggregateWeekly():
    input_dir = "export"
    output_dir = "aggregated"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if not filename.endswith(".csv"):
            continue

        path = os.path.join(input_dir, filename)
        df = pd.read_csv(path)

        # Skip if required columns are missing
        if "value" not in df.columns or "startDate" not in df.columns:
            continue

        # Parse startDate as datetime and drop bad values
        df["startDate"] = pd.to_datetime(df["startDate"], errors="coerce")
        df = df.dropna(subset=["startDate", "value"])

        # Convert value to numeric and drop bad ones
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])

        # Set startDate as index and resample by week to compute the weekly mean
        df.set_index("startDate", inplace=True)
        df_weekly = df["value"].resample("W").mean().round(3).dropna().reset_index()

        # Convert datetime to date only (no time)
        df_weekly["startDate"] = df_weekly["startDate"].dt.date

        # Rename columns for clarity: 'date' and 'mean'
        df_weekly.columns = ["date", "mean"]

        out_path = os.path.join(output_dir, filename)
        df_weekly.to_csv(out_path, index=False)
        print(f"Aggregated: {filename} -> {out_path}")


if __name__ == "__main__":
    aggregateWeekly()