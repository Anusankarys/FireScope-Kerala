
import pandas as pd
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "datasets" / "processed"

INPUT_FILE = DATA_DIR / "kerala_with_timestamps.csv"
MATCH_FILE = DATA_DIR / "mutual_nearest_matches.csv"
OUTPUT_FILE = DATA_DIR / "firescope_harmonized.csv"


def make_key(platform, latitude, longitude, timestamp):
    """Create a consistent identifier for a satellite observation."""
    time_value = pd.to_datetime(timestamp, utc=True, errors="coerce")

    if pd.isna(time_value):
        return None

    return (
        str(platform),
        round(float(latitude), 7),
        round(float(longitude), 7),
        int(time_value.timestamp())
    )


print("Loading original Kerala detections...")

df = pd.read_csv(INPUT_FILE)
matches = pd.read_csv(MATCH_FILE)

# Count mutual matching relationships for each observation.
match_counts = Counter()

for row in matches.itertuples(index=False):
    key1 = make_key(
        row.platform_1,
        row.latitude_1,
        row.longitude_1,
        row.time_1_utc
    )

    key2 = make_key(
        row.platform_2,
        row.latitude_2,
        row.longitude_2,
        row.time_2_utc
    )

    if key1 is not None:
        match_counts[key1] += 1

    if key2 is not None:
        match_counts[key2] += 1

# Classify every original observation.
df["match_partner_count"] = [
    match_counts.get(
        make_key(
            row.platform,
            row.latitude,
            row.longitude,
            row.acq_datetime_utc
        ),
        0
    )
    for row in df.itertuples(index=False)
]

df["match_status"] = df["match_partner_count"].apply(
    lambda count: "matched" if count > 0 else "unmatched"
)

# Add a clear project identifier.
df["project"] = "FireScope"

# Preserve all original detections.
df.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("FIRESCOPE HARMONIZED DATASET")
print("====================================")

print(f"Total original detections: {len(df)}")
print(f"Mutual matching relationships: {len(matches)}")

print("\nMatch status:")
print(df["match_status"].value_counts().to_string())

print("\nPlatform distribution:")
print(df["platform"].value_counts().to_string())

print("\nSensor family distribution:")
print(df["sensor_family"].value_counts().to_string())

print("\nMissing values:")
print(df.isnull().sum().to_string())

print("\nOutput saved:")
print(OUTPUT_FILE)

print("\nDATASET CREATION COMPLETED")
