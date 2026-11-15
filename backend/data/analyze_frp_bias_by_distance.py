
import pandas as pd

# Load matched observations
input_file = "datasets/processed/mutual_nearest_matches.csv"
df = pd.read_csv(input_file)

# Convert numeric columns
numeric_columns = [
    "frp_1",
    "frp_2",
    "distance_meters"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Remove invalid values
df = df.dropna(subset=numeric_columns)

df = df[
    (df["frp_1"] > 0) &
    (df["frp_2"] > 0)
].copy()

# Calculate signed FRP difference
# Positive = platform 1 reports higher FRP
df["signed_frp_difference"] = (
    df["frp_1"] - df["frp_2"]
)

df["platform_1_higher"] = (
    df["signed_frp_difference"] > 0
)

df["platform_2_higher"] = (
    df["signed_frp_difference"] < 0
)

df["equal_frp"] = (
    df["signed_frp_difference"] == 0
)

# Distance categories
df["distance_band"] = pd.cut(
    df["distance_meters"],
    bins=[0, 100, 250, 500],
    labels=["0-100m", "100-250m", "250-500m"],
    include_lowest=True
)

# Focus on major VIIRS combinations
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

# -----------------------------------------
# GROUP BY PLATFORM AND DISTANCE
# -----------------------------------------

summary = (
    df.groupby(
        ["platform_1", "platform_2", "distance_band"],
        observed=False
    )
    .agg(
        matched_pairs=("signed_frp_difference", "count"),
        mean_signed_difference=(
            "signed_frp_difference", "mean"
        ),
        median_signed_difference=(
            "signed_frp_difference", "median"
        ),
        mean_absolute_difference=(
            "signed_frp_difference",
            lambda x: x.abs().mean()
        ),
        platform_1_higher_count=(
            "platform_1_higher", "sum"
        ),
        platform_2_higher_count=(
            "platform_2_higher", "sum"
        ),
        equal_count=("equal_frp", "sum")
    )
)

# Calculate percentages
summary["platform_1_higher_percentage"] = (
    summary["platform_1_higher_count"]
    / summary["matched_pairs"].replace(0, float("nan"))
) * 100

summary["platform_2_higher_percentage"] = (
    summary["platform_2_higher_count"]
    / summary["matched_pairs"].replace(0, float("nan"))
) * 100

summary["equal_percentage"] = (
    summary["equal_count"]
    / summary["matched_pairs"].replace(0, float("nan"))
) * 100

summary = summary.round(3)

# -----------------------------------------
# DISPLAY RESULTS
# -----------------------------------------

print("\n====================================")
print("FRP BIAS BY PLATFORM AND DISTANCE")
print("====================================")

print(summary.to_string())

# -----------------------------------------
# SAVE RESULTS
# -----------------------------------------

output_file = (
    "datasets/processed/"
    "frp_bias_by_distance.csv"
)

summary.to_csv(output_file)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("Generated file:")
print(output_file)

