
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "kerala_with_timestamps.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "daily_satellite_detections.csv"
)

df = pd.read_csv(INPUT_FILE)

df["acq_date"] = pd.to_datetime(df["acq_date"])

# Create a complete calendar
all_dates = pd.date_range(
    start=df["acq_date"].min(),
    end=df["acq_date"].max(),
    freq="D"
)

platforms = sorted(df["platform"].dropna().unique())

# Count detections per date and platform
daily = df.pivot_table(
    index="acq_date",
    columns="platform",
    values="latitude",
    aggfunc="count",
    fill_value=0
)

# Include every calendar date and platform
daily = daily.reindex(
    index=all_dates,
    columns=platforms,
    fill_value=0
)

daily.index.name = "acq_date"

# Add total detections across platforms
daily["total_detections"] = daily.sum(axis=1)

# Save daily dataset
daily.to_csv(OUTPUT_FILE)

print("COMPLETE DAILY CALENDAR")
print("=" * 55)

print("First date:", daily.index.min())
print("Last date:", daily.index.max())
print("Total calendar days:", len(daily))

print("\nDaily detection statistics:")
print(daily.describe().round(2))

print("\nDays with zero detections from all platforms:")
print((daily["total_detections"] == 0).sum())

print("\nSaved:", OUTPUT_FILE)
