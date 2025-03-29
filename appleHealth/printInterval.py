import pandas as pd
import os

data_dir = "export"  # folder with your CSVs
intervals = []

for file in os.listdir(data_dir):
    if not file.endswith(".csv"):
        continue

    path = os.path.join(data_dir, file)
    df = pd.read_csv(path)

    if "startDate" not in df.columns:
        continue

    df["startDate"] = pd.to_datetime(df["startDate"], errors="coerce")
    df = df.dropna(subset=["startDate"]).sort_values("startDate")

    if len(df) < 2:
        continue

    # Compute time differences
    df["time_diff"] = df["startDate"].diff().dt.total_seconds()

    avg_interval_seconds = df["time_diff"].mean()
    total_records = len(df)

    intervals.append(
        {"file": file, "total_records": total_records, "avg_interval_secs": avg_interval_seconds, "avg_interval_minutes": avg_interval_seconds / 60, "avg_interval_hours": avg_interval_seconds / 3600}
    )

# Display results
summary_df = pd.DataFrame(intervals)

print(summary_df.to_string(index=False))
