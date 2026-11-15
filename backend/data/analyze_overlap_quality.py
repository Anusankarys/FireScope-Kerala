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

print("\n====================================")
print("OVERLAP QUALITY ANALYSIS")
print("====================================")

print("\nDistance statistics (meters):")
print(df["distance_meters"].describe())

print("\nTime difference statistics (hours):")
print(df["time_difference_hours"].describe())

print("\nDistance categories:")

distance_bins = [0, 100, 250, 500, 750, 1000]
distance_labels = [
    "0-100 m",
    "100-250 m",
    "250-500 m",
    "500-750 m",
    "750-1000 m"
]

print(
    pd.cut(
        df["distance_meters"],
        bins=distance_bins,
        labels=distance_labels,
        include_lowest=True
    ).value_counts().sort_index()
)

print("\nTime difference categories:")

time_bins = [0, 1, 3, 6, 12, 24]
time_labels = [
    "0-1 hours",
    "1-3 hours",
    "3-6 hours",
    "6-12 hours",
    "12-24 hours"
]

print(
    pd.cut(
        df["time_difference_hours"],
        bins=time_bins,
        labels=time_labels,
        include_lowest=True
    ).value_counts().sort_index()
)

print("\n====================================")
print("QUALITY ANALYSIS COMPLETED")
print("====================================")
