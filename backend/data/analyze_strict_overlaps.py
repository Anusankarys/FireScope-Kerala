import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "potential_overlaps.csv"
)

df = pd.read_csv(INPUT_FILE)

# Apply strict exploratory matching criteria
strict = df[
    (df["distance_meters"] <= 500) &
    (df["time_difference_hours"] <= 1)
].copy()

# Standardize platform pair names
strict["platform_pair"] = strict.apply(
    lambda row: " + ".join(
        sorted([row["platform_1"], row["platform_2"]])
    ),
    axis=1
)

print("\n====================================")
print("STRICT SATELLITE OVERLAP ANALYSIS")
print("====================================")

print("Total potential overlaps:", len(strict))

print("\nOverlaps by satellite pair:")

print(
    strict["platform_pair"]
    .value_counts()
    .to_string()
)

print("\nAverage distance by satellite pair:")

print(
    strict.groupby("platform_pair")["distance_meters"]
    .mean()
    .round(2)
    .sort_values()
    .to_string()
)

print("\nAverage time difference by satellite pair:")

print(
    strict.groupby("platform_pair")["time_difference_hours"]
    .mean()
    .round(2)
    .sort_values()
    .to_string()
)

print("\n====================================")
print("STRICT ANALYSIS COMPLETED")
print("====================================")