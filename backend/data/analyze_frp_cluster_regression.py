
import pandas as pd
import numpy as np
import statsmodels.api as sm

from pathlib import Path
from scipy.stats import norm
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR / "datasets" / "processed" /
    "mutual_nearest_matches.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "datasets" / "processed" /
    "frp_cluster_regression_results.csv"
)

df = pd.read_csv(INPUT_FILE)

# Convert numerical columns
numeric_columns = [
    "frp_1",
    "frp_2",
    "distance_meters",
    "time_difference_min",
    "latitude_1",
    "longitude_1",
    "latitude_2",
    "longitude_2"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=numeric_columns).copy()

df = df[
    (df["frp_1"] > 0) &
    (df["frp_2"] > 0)
].copy()

# Keep the three VIIRS platform pairs
valid_pairs = [
    ("N20", "N21"),
    ("N20", "SNPP"),
    ("N21", "SNPP")
]

df = df[
    df.apply(
        lambda row: (
            row["platform_1"],
            row["platform_2"]
        ) in valid_pairs,
        axis=1
    )
].copy()

# Dependent variable
df["absolute_frp_difference"] = (
    df["frp_1"] - df["frp_2"]
).abs()

df["log_frp_difference"] = np.log1p(
    df["absolute_frp_difference"]
)

# Create unique observation identifiers
# Each observation is identified by platform, coordinates and UTC time.

df["observation_1"] = (
    df["platform_1"].astype(str) + "|" +
    df["latitude_1"].round(7).astype(str) + "|" +
    df["longitude_1"].round(7).astype(str) + "|" +
    df["time_1_utc"].astype(str)
)

df["observation_2"] = (
    df["platform_2"].astype(str) + "|" +
    df["latitude_2"].round(7).astype(str) + "|" +
    df["longitude_2"].round(7).astype(str) + "|" +
    df["time_2_utc"].astype(str)
)

# Independent variables
X = df[
    ["distance_meters", "time_difference_min"]
].copy()

platform_pair = (
    df["platform_1"] + "_" + df["platform_2"]
)

pair_dummies = pd.get_dummies(
    platform_pair,
    prefix="pair",
    drop_first=True,
    dtype=float
)

X = pd.concat([X, pair_dummies], axis=1)
X = sm.add_constant(X)

y = df["log_frp_difference"]

# Fit ordinary OLS
model = sm.OLS(y, X).fit()

# Two-way cluster-robust covariance
# Convert observation identifiers into numeric group codes
group_1 = pd.factorize(df["observation_1"])[0]
group_2 = pd.factorize(df["observation_2"])[0]

# Two-way cluster-robust covariance
cov_both, cov_obs1, cov_obs2 = cov_cluster_2groups(
    model,
    group_1,
    group_2,
    use_correction=True
)

# Calculate robust standard errors and tests
standard_errors = np.sqrt(
    np.maximum(np.diag(cov_both), 0)
)

z_statistics = model.params.to_numpy() / standard_errors

p_values = 2 * norm.sf(np.abs(z_statistics))

ci_lower = model.params.to_numpy() - 1.96 * standard_errors
ci_upper = model.params.to_numpy() + 1.96 * standard_errors

results = pd.DataFrame({
    "variable": model.params.index,
    "coefficient": model.params.to_numpy(),
    "cluster_robust_se": standard_errors,
    "z_statistic": z_statistics,
    "p_value": p_values,
    "ci_lower_95": ci_lower,
    "ci_upper_95": ci_upper
})

print("\n====================================")
print("FRP TWO-WAY CLUSTER REGRESSION")
print("====================================")

print(f"Observations: {len(df)}")
print(f"Unique first-side observations: {df['observation_1'].nunique()}")
print(f"Unique second-side observations: {df['observation_2'].nunique()}")
print(f"R-squared: {model.rsquared:.4f}")
print(f"Adjusted R-squared: {model.rsquared_adj:.4f}")

print("\n====================================")
print("CLUSTER-ROBUST COEFFICIENT RESULTS")
print("====================================")

print(results.to_string(index=False))

print("\n====================================")
print("SIGNIFICANCE SUMMARY")
print("====================================")

for _, row in results.iterrows():
    if row["variable"] == "const":
        continue

    if row["p_value"] < 0.05:
        conclusion = "Statistically significant at 5%"
    else:
        conclusion = "Not statistically significant at 5%"

    print(
        f"{row['variable']}: "
        f"p-value = {row['p_value']:.6f} -> {conclusion}"
    )

results.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
print(f"Generated file: {OUTPUT_FILE}")
