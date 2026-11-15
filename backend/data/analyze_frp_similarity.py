
import pandas as pd
import numpy as np

# -----------------------------------------
# LOAD MUTUAL MATCH DATA
# -----------------------------------------

input_file = "datasets/processed/mutual_nearest_matches.csv"

df = pd.read_csv(input_file)

df["frp_1"] = pd.to_numeric(df["frp_1"], errors="coerce")
df["frp_2"] = pd.to_numeric(df["frp_2"], errors="coerce")

# Keep valid positive FRP pairs
df = df.dropna(subset=["frp_1", "frp_2"])
df = df[(df["frp_1"] > 0) & (df["frp_2"] > 0)].copy()

# -----------------------------------------
# CALCULATE PAIRWISE FRP DIFFERENCES
# -----------------------------------------

df["frp_difference"] = df["frp_2"] - df["frp_1"]

df["absolute_frp_difference"] = (
    df["frp_difference"].abs()
)

df["mean_pair_frp"] = (
    df["frp_1"] + df["frp_2"]
) / 2

# Symmetric percentage difference
df["percentage_difference"] = (
    df["absolute_frp_difference"]
    / df["mean_pair_frp"]
) * 100

df["frp_ratio"] = df["frp_2"] / df["frp_1"]

# -----------------------------------------
# OVERALL FRP SIMILARITY
# -----------------------------------------

print("\n====================================")
print("FRP SIMILARITY ANALYSIS")
print("====================================")

print("\nValid matched pairs:", len(df))

print("\nOVERALL FRP STATISTICS")

print("Mean FRP - Satellite 1:", round(df["frp_1"].mean(), 3))
print("Mean FRP - Satellite 2:", round(df["frp_2"].mean(), 3))

print("Median FRP - Satellite 1:", round(df["frp_1"].median(), 3))
print("Median FRP - Satellite 2:", round(df["frp_2"].median(), 3))

print("\nFRP DIFFERENCE")

print(
    "Mean signed difference:",
    round(df["frp_difference"].mean(), 3)
)

print(
    "Mean absolute difference:",
    round(df["absolute_frp_difference"].mean(), 3)
)

print(
    "Median absolute difference:",
    round(df["absolute_frp_difference"].median(), 3)
)

print(
    "Mean percentage difference:",
    round(df["percentage_difference"].mean(), 2), "%"
)

print(
    "Median percentage difference:",
    round(df["percentage_difference"].median(), 2), "%"
)

print(
    "Mean FRP ratio:",
    round(df["frp_ratio"].mean(), 3)
)

print(
    "Overall Pearson correlation:",
    round(df["frp_1"].corr(df["frp_2"]), 3)
)

# -----------------------------------------
# FRP SIMILARITY BY PLATFORM PAIR
# -----------------------------------------

summary = (
    df.groupby(["platform_1", "platform_2"])
    .agg(
        matched_pairs=("frp_1", "count"),
        mean_frp_1=("frp_1", "mean"),
        mean_frp_2=("frp_2", "mean"),
        mean_absolute_difference=(
            "absolute_frp_difference", "mean"
        ),
        median_absolute_difference=(
            "absolute_frp_difference", "median"
        ),
        mean_percentage_difference=(
            "percentage_difference", "mean"
        ),
        median_percentage_difference=(
            "percentage_difference", "median"
        ),
        mean_frp_ratio=("frp_ratio", "mean"),
        correlation=("frp_1", lambda x: np.nan)
    )
)

# Calculate correlation separately for each platform pair
correlations = (
    df.groupby(["platform_1", "platform_2"])
    .apply(
        lambda group: group["frp_1"].corr(group["frp_2"]),
        include_groups=False
    )
)

summary["correlation"] = correlations

summary = summary.round(3)

print("\n====================================")
print("FRP SIMILARITY BY PLATFORM PAIR")
print("====================================")

print(summary.to_string())

# -----------------------------------------
# SAVE RESULTS
# -----------------------------------------

pair_output = (
    "datasets/processed/frp_similarity_by_pair.csv"
)

summary_output = (
    "datasets/processed/frp_similarity_by_platform.csv"
)

df.to_csv(pair_output, index=False)
summary.to_csv(summary_output)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("Generated files:")
print(pair_output)
print(summary_output)
