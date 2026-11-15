
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FOLDER = PROJECT_ROOT / "datasets" / "processed"
OUTPUT_FOLDER = PROJECT_ROOT / "datasets" / "processed"

all_data = []

for file in sorted(INPUT_FOLDER.glob("*_kerala.csv")):

    print("Reading:", file.name)

    # Read values as strings to preserve original data
    df = pd.read_csv(file, dtype=str)

    # Identify sensor family
    if "_M-C61_" in file.name:
        sensor_family = "MODIS"
    else:
        sensor_family = "VIIRS"

    # Identify archive or NRT
    if "fire_archive" in file.name:
        data_status = "archive"
    else:
        data_status = "NRT"

    # Add source information
    df["sensor_family"] = sensor_family
    df["platform"] = (
        df["satellite"]
        if "satellite" in df.columns
        else "Unknown"
    )
    df["data_status"] = data_status
    df["source_file"] = file.name

    all_data.append(df)

# Combine all observations
combined = pd.concat(
    all_data,
    ignore_index=True,
    sort=False
)

# Save combined dataset
output_file = OUTPUT_FOLDER / "kerala_all_satellites.csv"

combined.to_csv(output_file, index=False)

print("\n================================")
print("DATASET COMBINATION COMPLETED")
print("================================")

print("Total observations:", len(combined))
print("\nSensor distribution:")
print(combined["sensor_family"].value_counts())

print("\nPlatform distribution:")
print(combined["platform"].value_counts())

print("\nData status distribution:")
print(combined["data_status"].value_counts())

print("\nSaved to:", output_file)
