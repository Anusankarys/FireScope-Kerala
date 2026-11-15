
import pandas as pd

input_file = "datasets/processed/mutual_nearest_matches.csv"

df = pd.read_csv(input_file)

numeric_columns = [
    "frp_1",
    "frp_2",
    "distance_meters",
    "time_difference_min"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df = df.dropna(subset=numeric_columns)

df = df[
    (df["frp_1"] > 0) &
    (df["frp_2"] > 0)
].copy()

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

# Distance categories
df["distance_band"] = pd.cut(
    df["distance_meters"],
    bins=[0, 100, 250, 500],
    labels=["0-100m", "100-250m", "250-500m"],
    include_lowest=True
)

# Focus on the three main VIIRS combinations
viirs_pairs = [
    ("N20", "N21"),
    ("N20", "SNPP"),
    ("N21", "SNPP")
]

df = df[
    df.apply(
        lambda row: (row["platform_1"], row["platform_2"])
        in viirs_pairs,
        axis=1
    )
].copy()

# Group by platform pair and distance
summary = (
    df.groupby(
        ["platform_1", "platform_2", "distance_band"],
        observed=False
    )
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
    .round(3)
)

print("\n====================================")
print("PLATFORM-WISE FRP DISTANCE ANALYSIS")
print("====================================")

print(summary.to_string())

# Save result
output_file = (
    "datasets/processed/"
    "frp_platform_distance_analysis.csv"
)

summary.to_csv(output_file)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("Generated file:")
print(output_file)
