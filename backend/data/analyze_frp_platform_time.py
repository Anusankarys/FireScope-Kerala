
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

# Calculate FRP differences
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

# Time categories
df["time_band"] = pd.cut(
    df["time_difference_min"],
    bins=[0, 15, 30, 45, 60],
    labels=[
        "0-15 min",
        "15-30 min",
        "30-45 min",
        "45-60 min"
    ],
    include_lowest=True
)

# Select the three major VIIRS combinations
viirs_pairs = [
    ("N20", "N21"),
    ("N20", "SNPP"),
    ("N21", "SNPP")
]

df = df[
    df.apply(
        lambda row: (
            row["platform_1"],
            row["platform_2"]
        ) in viirs_pairs,
        axis=1
    )
].copy()

# Summarize by platform pair and time band
summary = (
    df.groupby(
        ["platform_1", "platform_2", "time_band"],
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
print("PLATFORM-WISE FRP TIME ANALYSIS")
print("====================================")

print(summary.to_string())

output_file = (
    "datasets/processed/"
    "frp_platform_time_analysis.csv"
)

summary.to_csv(output_file)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("Generated file:")
print(output_file)
