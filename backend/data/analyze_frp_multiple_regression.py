
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR / "datasets" / "processed" /
    "mutual_nearest_matches.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "datasets" / "processed" /
    "frp_regression_results.csv"
)

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

# Dependent variable
df["absolute_frp_difference"] = (
    df["frp_1"] - df["frp_2"]
).abs()

# Keep the three main VIIRS platform pairs
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

# Predictor variables
X = df[
    ["distance_meters", "time_difference_min"]
].copy()

# Add platform-pair indicators
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

y = df["absolute_frp_difference"]

# Fit multiple linear regression
model = LinearRegression()
model.fit(X, y)

predictions = model.predict(X)

r2 = r2_score(y, predictions)
rmse = np.sqrt(mean_squared_error(y, predictions))

print("\n====================================")
print("FRP MULTIPLE LINEAR REGRESSION")
print("====================================")

print(f"Total matched pairs: {len(df)}")
print(f"R-squared: {r2:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"Mean absolute FRP difference: {y.mean():.4f}")

print("\n====================================")
print("REGRESSION COEFFICIENTS")
print("====================================")

results = pd.DataFrame({
    "variable": X.columns,
    "coefficient": model.coef_
})

results.loc[len(results)] = [
    "intercept",
    model.intercept_
]

print(results.to_string(index=False))

print("\n====================================")
print("INTERPRETATION OF CONTINUOUS VARIABLES")
print("====================================")

for variable in ["distance_meters", "time_difference_min"]:
    coefficient = model.coef_[list(X.columns).index(variable)]

    print(f"{variable}: {coefficient:.6f}")

    if coefficient > 0:
        print("Positive association with absolute FRP difference.")
    elif coefficient < 0:
        print("Negative association with absolute FRP difference.")
    else:
        print("No linear association in the fitted model.")

results.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
print(f"Generated file: {OUTPUT_FILE}")
