
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "datasets" / "processed" / "mutual_nearest_matches.csv"
OUTPUT_FILE = BASE_DIR / "datasets" / "processed" / "frp_ols_results.csv"

df = pd.read_csv(INPUT_FILE)

numeric_columns = [
    "frp_1",
    "frp_2",
    "distance_meters",
    "time_difference_min"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=numeric_columns).copy()

df = df[
    (df["frp_1"] > 0) &
    (df["frp_2"] > 0)
].copy()

df["absolute_frp_difference"] = (
    df["frp_1"] - df["frp_2"]
).abs()

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

# Predictors
X = df[["distance_meters", "time_difference_min"]].copy()

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

y = df["absolute_frp_difference"]

# OLS with HC3 robust standard errors
model = sm.OLS(y, X).fit(cov_type="HC3")

print("\n====================================")
print("FRP OLS REGRESSION WITH HC3")
print("====================================")

print(f"Observations: {len(df)}")
print(f"R-squared: {model.rsquared:.4f}")
print(f"Adjusted R-squared: {model.rsquared_adj:.4f}")
print(f"F-statistic: {model.fvalue:.4f}")
print(f"Model p-value: {model.f_pvalue:.6f}")

print("\n====================================")
print("REGRESSION RESULTS")
print("====================================")

print(model.summary())

# Export coefficients and statistical tests
results = pd.DataFrame({
    "variable": model.params.index,
    "coefficient": model.params.values,
    "robust_standard_error": model.bse.values,
    "p_value": model.pvalues.values,
    "ci_lower_95": model.conf_int()[0].values,
    "ci_upper_95": model.conf_int()[1].values
})

results.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
print(f"Generated file: {OUTPUT_FILE}")