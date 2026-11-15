
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "datasets" / "processed" / "mutual_nearest_matches.csv"
OUTPUT_FILE = BASE_DIR / "datasets" / "processed" / "frp_outlier_analysis.csv"

df = pd.read_csv(INPUT_FILE)

for col in ["frp_1", "frp_2"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["frp_1", "frp_2"]).copy()

df = df[
    (df["frp_1"] > 0) &
    (df["frp_2"] > 0)
].copy()

df["absolute_frp_difference"] = (
    df["frp_1"] - df["frp_2"]
).abs()

values = df["absolute_frp_difference"]

q1 = values.quantile(0.25)
q2 = values.quantile(0.50)
q3 = values.quantile(0.75)

iqr = q3 - q1
lower_bound = max(0, q1 - 1.5 * iqr)
upper_bound = q3 + 1.5 * iqr

df["outlier_status"] = np.where(
    (values < lower_bound) | (values > upper_bound),
    "Outlier",
    "Normal"
)

print("\n====================================")
print("FRP DIFFERENCE DISTRIBUTION")
print("====================================")

print(f"Total pairs: {len(df)}")
print(f"Mean: {values.mean():.4f}")
print(f"Median: {q2:.4f}")
print(f"Standard deviation: {values.std():.4f}")
print(f"Minimum: {values.min():.4f}")
print(f"Maximum: {values.max():.4f}")
print(f"Q1: {q1:.4f}")
print(f"Q3: {q3:.4f}")
print(f"IQR: {iqr:.4f}")

print("\n====================================")
print("IQR OUTLIER DETECTION")
print("====================================")

print(f"Lower bound: {lower_bound:.4f}")
print(f"Upper bound: {upper_bound:.4f}")

outlier_count = (df["outlier_status"] == "Outlier").sum()
normal_count = (df["outlier_status"] == "Normal").sum()

print(f"Normal pairs: {normal_count}")
print(f"Outlier pairs: {outlier_count}")
print(f"Outlier percentage: {outlier_count / len(df) * 100:.2f}%")

print("\n====================================")
print("LARGEST FRP DIFFERENCES")
print("====================================")

columns = [
    "platform_1",
    "platform_2",
    "frp_1",
    "frp_2",
    "absolute_frp_difference",
    "distance_meters",
    "time_difference_min"
]

print(
    df.nlargest(10, "absolute_frp_difference")[columns]
    .to_string(index=False)
)

df.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
print(f"Generated file: {OUTPUT_FILE}")
