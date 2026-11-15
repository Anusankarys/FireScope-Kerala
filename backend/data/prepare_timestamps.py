
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "kerala_all_satellites.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "kerala_with_timestamps.csv"
)

df = pd.read_csv(INPUT_FILE, dtype=str)

# Preserve original acquisition fields
df["acq_date"] = df["acq_date"].str.strip()
df["acq_time"] = df["acq_time"].str.strip().str.zfill(4)

# Create a UTC acquisition timestamp
df["acq_datetime_utc"] = pd.to_datetime(
    df["acq_date"] + " " + df["acq_time"],
    format="%Y-%m-%d %H%M",
    errors="coerce",
    utc=True
)

print("Total records:", len(df))
print(
    "Valid timestamps:",
    df["acq_datetime_utc"].notna().sum()
)
print(
    "Invalid timestamps:",
    df["acq_datetime_utc"].isna().sum()
)

print("\nSample timestamps:")
print(
    df[
        ["satellite", "acq_date", "acq_time",
         "acq_datetime_utc"]
    ].head(10).to_string(index=False)
)

df.to_csv(OUTPUT_FILE, index=False)

print("\nSaved:", OUTPUT_FILE)
