
import pandas as pd
import numpy as np

# Load matched observations
input_file = "datasets/processed/mutual_nearest_matches.csv"
df = pd.read_csv(input_file)

# Convert FRP columns to numeric
df["frp_1"] = pd.to_numeric(df["frp_1"], errors="coerce")
df["frp_2"] = pd.to_numeric(df["frp_2"], errors="coerce")

# Remove invalid FRP values
df = df.dropna(subset=["frp_1", "frp_2"])
df = df[
    (df["frp_1"] > 0) &
    (df["frp_2"] > 0)
].copy()

# Signed difference: positive means platform 1 is higher
df["signed_frp_difference"] = df["frp_1"] - df["frp_2"]

df["absolute_frp_difference"] = (
    df["signed_frp_difference"].abs()
)

# Calculate direction of difference
df["platform_1_higher"] = (
    df["signed_frp_difference"] > 0
)

df["platform_2_higher"] = (
    df["signed_frp_difference"] < 0
)

df["equal_frp"] = (
    df["signed_frp_difference"] == 0
)

# -----------------------------------------
# OVERALL BIAS ANALYSIS
# -----------------------------------------

print("\n====================================")
print("OVERALL FRP BIAS ANALYSIS")
print("====================================")

print("Total valid matched pairs:", len(df))

print(
    "Mean signed FRP difference:",
    round(df["signed_frp_difference"].mean(), 3)
)

print(
    "Median signed FRP difference:",
    round(df["signed_frp_difference"].median(), 3)
)

print(
    "Platform 1 higher:",
    round(df["platform_1_higher"].mean() * 100, 2),
    "%"
)

print(
    "Platform 2 higher:",
    round(df["platform_2_higher"].mean() * 100, 2),
    "%"
)

print(
    "Equal FRP:",
    round(df["equal_frp"].mean() * 100, 2),
    "%"
)

# -----------------------------------------
# PLATFORM-PAIR BIAS ANALYSIS
# -----------------------------------------

summary = (
    df.groupby(["platform_1", "platform_2"])
    .agg(
        matched_pairs=("signed_frp_difference", "count"),
        mean_signed_difference=(
            "signed_frp_difference", "mean"
        ),
        median_signed_difference=(
            "signed_frp_difference", "median"
        ),
        mean_absolute_difference=(
            "absolute_frp_difference", "mean"
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

summary["platform_1_higher_percentage"] = (
    summary["platform_1_higher_count"]
    / summary["matched_pairs"] * 100
)

summary["platform_2_higher_percentage"] = (
    summary["platform_2_higher_count"]
    / summary["matched_pairs"] * 100
)

summary["equal_percentage"] = (
    summary["equal_count"]
    / summary["matched_pairs"] * 100
)

summary = summary.round(3)

print("\n====================================")
print("FRP BIAS BY PLATFORM PAIR")
print("====================================")

print(summary.to_string())

# -----------------------------------------
# SAVE RESULTS
# -----------------------------------------

df.to_csv(
    "datasets/processed/frp_signed_pair_differences.csv",
    index=False
)

summary.to_csv(
    "datasets/processed/frp_platform_bias_summary.csv"
)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("Generated files:")
print("frp_signed_pair_differences.csv")
print("frp_platform_bias_summary.csv")
