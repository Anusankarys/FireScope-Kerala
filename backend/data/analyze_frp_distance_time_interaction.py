
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = BASE_DIR / "datasets" / "processed" / "mutual_nearest_matches.csv"
OUTPUT_FILE = BASE_DIR / "datasets" / "processed" / "frp_distance_time_interaction.csv"

df = pd.read_csv(INPUT_FILE)

for col in ["frp_1", "frp_2", "distance_meters", "time_difference_min"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=[
    "frp_1", "frp_2", "distance_meters", "time_difference_min"
])

df = df[
    (df["frp_1"] > 0) &
    (df["frp_2"] > 0)
].copy()

df["signed_difference"] = df["frp_1"] - df["frp_2"]
df["absolute_difference"] = df["signed_difference"].abs()

df["distance_band"] = pd.cut(
    df["distance_meters"],
    bins=[0, 100, 250, 500],
    labels=["0-100m", "100-250m", "250-500m"],
    include_lowest=True
)

df["time_band"] = pd.cut(
    df["time_difference_min"],
    bins=[0, 15, 30, 45, 60],
    labels=["0-15min", "15-30min", "30-45min", "45-60min"],
    include_lowest=True
)

df = df[
    df["distance_band"].notna() &
    df["time_band"].notna()
]

viirs_pairs = [
    ("N20", "N21"),
    ("N20", "SNPP"),
    ("N21", "SNPP")
]

df = df[
    df.apply(
        lambda row: (row["platform_1"], row["platform_2"]) in viirs_pairs,
        axis=1
    )
]

summary = (
    df.groupby(
        ["platform_1", "platform_2", "distance_band", "time_band"],
        observed=True
    )
    .agg(
        matched_pairs=("absolute_difference", "count"),
        mean_signed_difference=("signed_difference", "mean"),
        median_signed_difference=("signed_difference", "median"),
        mean_absolute_difference=("absolute_difference", "mean"),
        median_absolute_difference=("absolute_difference", "median")
    )
    .reset_index()
)

summary.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("FRP DISTANCE-TIME INTERACTION ANALYSIS")
print("====================================")
print(summary.to_string(index=False))

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
print(f"Generated file: {OUTPUT_FILE}")
