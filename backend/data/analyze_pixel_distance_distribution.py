
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "potential_overlaps.csv"
)

df = pd.read_csv(INPUT_FILE)

df["distance_meters"] = pd.to_numeric(
    df["distance_meters"]
)

df["time_difference_hours"] = pd.to_numeric(
    df["time_difference_hours"]
)

df["time_difference_min"] = (
    df["time_difference_hours"] * 60
)

# Retain cross-platform candidates within 60 minutes.
df = df[
    df["time_difference_min"] <= 60
].copy()

df["platform_pair"] = df.apply(
    lambda row: " + ".join(
        sorted([row["platform_1"], row["platform_2"]])
    ),
    axis=1
)

thresholds = [100, 250, 500, 750, 1000]

print("\n====================================")
print("PIXEL-LEVEL DISTANCE DISTRIBUTION")
print("Time limit: 60 minutes")
print("====================================")

for platform_pair, group in df.groupby("platform_pair"):

    print(f"\n{platform_pair}")

    print("Total pixel matches:", len(group))

    for threshold in thresholds:

        selected = group[
            group["distance_meters"] <= threshold
        ]

        percentage = (
            len(selected) / len(group) * 100
            if len(group) > 0 else 0
        )

        print(
            f"{threshold} m: "
            f"{len(selected)} pixel pairs "
            f"({percentage:.2f}%)"
        )

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
