
import pandas as pd
import numpy as np

input_file = "datasets/processed/mutual_nearest_matches.csv"

df = pd.read_csv(input_file)

# Convert numeric columns
numeric_columns = [
    "frp_1",
    "frp_2",
    "distance_meters",
    "time_difference_min"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df = df.dropna(subset=numeric_columns)

# Keep valid positive FRP values
df = df[(df["frp_1"] > 0) & (df["frp_2"] > 0)].copy()

# Calculate FRP disagreement
df["absolute_frp_difference"] = (
    df["frp_1"] - df["frp_2"]
).abs()

df["mean_pair_frp"] = (
    df["frp_1"] + df["frp_2"]
) / 2

df["percentage_difference"] = (
    df["absolute_frp_difference"]
    / df["mean_pair_frp"]
) * 100

# -----------------------------------------
# CORRELATION WITH DISTANCE AND TIME
# -----------------------------------------

print("\n====================================")
print("FRP DIFFERENCE FACTOR ANALYSIS")
print("====================================")

print("\nTotal valid pairs:", len(df))

print("\nCORRELATION WITH FRP DIFFERENCE")

for column in ["distance_meters", "time_difference_min"]:
    pearson = df[column].corr(
        df["absolute_frp_difference"],
        method="pearson"
    )

    spearman = df[column].corr(
        df["absolute_frp_difference"],
        method="spearman"
    )

    print(f"\n{column}")
    print("Pearson correlation:", round(pearson, 3))
    print("Spearman correlation:", round(spearman, 3))

# -----------------------------------------
# DISTANCE BAND ANALYSIS
# -----------------------------------------

df["distance_band"] = pd.cut(
    df["distance_meters"],
    bins=[0, 100, 250, 500],
    labels=["0-100m", "100-250m", "250-500m"],
    include_lowest=True
)

distance_summary = (
    df.groupby("distance_band", observed=False)
    .agg(
        matched_pairs=("absolute_frp_difference", "count"),
        mean_absolute_difference=(
            "absolute_frp_difference", "mean"
        ),
        median_absolute_difference=(
            "absolute_frp_difference", "median"
        ),
        mean_percentage_difference=(
            "percentage_difference", "mean"
        )
    )
    .round(2)
)

print("\n====================================")
print("FRP DIFFERENCE BY SPATIAL DISTANCE")
print("====================================")

print(distance_summary.to_string())

# -----------------------------------------
# TIME BAND ANALYSIS
# -----------------------------------------

df["time_band"] = pd.cut(
    df["time_difference_min"],
    bins=[0, 15, 30, 45, 60],
    labels=["0-15 min", "15-30 min", "30-45 min", "45-60 min"],
    include_lowest=True
)

time_summary = (
    df.groupby("time_band", observed=False)
    .agg(
        matched_pairs=("absolute_frp_difference", "count"),
        mean_absolute_difference=(
            "absolute_frp_difference", "mean"
        ),
        median_absolute_difference=(
            "absolute_frp_difference", "median"
        ),
        mean_percentage_difference=(
            "percentage_difference", "mean"
        )
    )
    .round(2)
)

print("\n====================================")
print("FRP DIFFERENCE BY TIME DIFFERENCE")
print("====================================")

print(time_summary.to_string())

# -----------------------------------------
# SAVE RESULTS
# -----------------------------------------

distance_summary.to_csv(
    "datasets/processed/frp_difference_by_distance.csv"
)

time_summary.to_csv(
    "datasets/processed/frp_difference_by_time.csv"
)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("Generated files:")
print("frp_difference_by_distance.csv")
print("frp_difference_by_time.csv")
