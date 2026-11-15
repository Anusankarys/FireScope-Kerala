import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "overlap_groups.csv"
)

df = pd.read_csv(INPUT_FILE)

print("\n====================================")
print("LARGEST OVERLAP GROUP INSPECTION")
print("====================================")

group_summary = (
    df.groupby("group_id")
    .agg(
        observations=("platform", "count"),
        platforms=("platforms_in_group", "first"),
        first_time=("acq_datetime_utc", "min"),
        last_time=("acq_datetime_utc", "max"),
        min_latitude=("latitude", "min"),
        max_latitude=("latitude", "max"),
        min_longitude=("longitude", "min"),
        max_longitude=("longitude", "max")
    )
    .reset_index()
)

group_summary["time_span_hours"] = (
    pd.to_datetime(group_summary["last_time"], utc=True)
    - pd.to_datetime(group_summary["first_time"], utc=True)
).dt.total_seconds() / 3600

group_summary = group_summary.sort_values(
    "observations",
    ascending=False
)

print("\nTop 10 largest groups:\n")

print(
    group_summary.head(10).to_string(index=False)
)

print("\n====================================")
print("GROUP INSPECTION COMPLETED")
print("====================================")