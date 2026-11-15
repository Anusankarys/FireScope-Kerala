
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "datasets" / "processed" / "mutual_nearest_matches.csv"
OUTPUT_FILE = BASE_DIR / "datasets" / "processed" / "frp_outliers_by_pair.csv"

df = pd.read_csv(INPUT_FILE)

for col in ["frp_1", "frp_2"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["frp_1", "frp_2"]).copy()
df = df[(df["frp_1"] > 0) & (df["frp_2"] > 0)].copy()

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
        lambda row: (row["platform_1"], row["platform_2"])
        in valid_pairs,
        axis=1
    )
].copy()

df["outlier_status"] = "Normal"

print("\n====================================")
print("FRP OUTLIERS BY VIIRS PLATFORM PAIR")
print("====================================")

for (p1, p2), group in df.groupby(["platform_1", "platform_2"]):

    values = group["absolute_frp_difference"]

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    lower = max(0, q1 - 1.5 * iqr)
    upper = q3 + 1.5 * iqr

    mask = (
        (df["platform_1"] == p1) &
        (df["platform_2"] == p2)
    )

    outlier_mask = (
        (df.loc[mask, "absolute_frp_difference"] < lower) |
        (df.loc[mask, "absolute_frp_difference"] > upper)
    )

    df.loc[df.loc[mask].index[outlier_mask], "outlier_status"] = "Outlier"

    count = int(outlier_mask.sum())

    print(f"\nPlatform pair: {p1} + {p2}")
    print(f"Matched pairs: {len(group)}")
    print(f"Median difference: {values.median():.4f}")
    print(f"Mean difference: {values.mean():.4f}")
    print(f"IQR: {iqr:.4f}")
    print(f"Upper outlier threshold: {upper:.4f}")
    print(f"Potential outliers: {count}")
    print(f"Outlier percentage: {count / len(group) * 100:.2f}%")

df.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
print(f"VIIRS matched pairs: {len(df)}")
print(f"Generated file: {OUTPUT_FILE}")
