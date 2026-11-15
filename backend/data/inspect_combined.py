
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

file = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "kerala_all_satellites.csv"
)

df = pd.read_csv(file)

print("TOTAL RECORDS:", len(df))

print("\n1. DATASET COLUMNS")
print(df.columns.tolist())

print("\n2. MISSING VALUES")
print(df.isnull().sum())

print("\n3. DATE COVERAGE")
dates = pd.to_datetime(df["acq_date"], errors="coerce")
print("First observation:", dates.min())
print("Last observation:", dates.max())

print("\n4. SENSOR DISTRIBUTION")
print(df["sensor_family"].value_counts())

print("\n5. PLATFORM DISTRIBUTION")
print(df["platform"].value_counts())

print("\n6. ARCHIVE / NRT DISTRIBUTION")
print(df["data_status"].value_counts())

print("\n7. CONFIDENCE VALUES BY SENSOR")
print(
    df.groupby("sensor_family")["confidence"]
    .value_counts(dropna=False)
)

print("\n8. EXACT DUPLICATE ROWS")
print(df.duplicated().sum())

print("\nInspection completed!")
