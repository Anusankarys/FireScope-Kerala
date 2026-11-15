
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

# Convert numeric columns.
df["distance_meters"] = pd.to_numeric(
    df["distance_meters"]
)

df["time_difference_hours"] = pd.to_numeric(
    df["time_difference_hours"]
)

df["time_difference_min"] = (
    df["time_difference_hours"] * 60
)

# Apply exploratory matching limits.
df = df[
    (df["distance_meters"] <= 500)
    &
    (df["time_difference_min"] <= 60)
].copy()

# Create a consistent platform-pair label.
df["platform_pair"] = df.apply(
    lambda row: " + ".join(
        sorted([row["platform_1"], row["platform_2"]])
    ),
    axis=1
)

# Identify each unique pair of satellite acquisitions.
df["acquisition_pair"] = df.apply(
    lambda row: tuple(sorted([
        (row["platform_1"], row["time_1_utc"]),
        (row["platform_2"], row["time_2_utc"])
    ])),
    axis=1
)

# Count pixel matches within each acquisition pair.
acquisitions = (
    df.groupby(["platform_pair", "acquisition_pair"])
    .agg(
        time_difference_min=("time_difference_min", "first"),
        pixel_pair_count=("time_difference_min", "size")
    )
    .reset_index()
)

print("\n====================================")
print("UNIQUE ACQUISITION TIME DISTRIBUTION")
print("500 metres / 60 minutes")
print("====================================")

for platform_pair, group in acquisitions.groupby("platform_pair"):

    print(f"\n{platform_pair}")

    print(
        "Unique acquisition pairs:",
        len(group)
    )

    print(
        "Total pixel matches:",
        group["pixel_pair_count"].sum()
    )

    print(
        "Mean time difference:",
        round(group["time_difference_min"].mean(), 2),
        "minutes"
    )

    print(
        "Median time difference:",
        round(group["time_difference_min"].median(), 2),
        "minutes"
    )

    print(
        "Minimum time difference:",
        round(group["time_difference_min"].min(), 2),
        "minutes"
    )

    print(
        "Maximum time difference:",
        round(group["time_difference_min"].max(), 2),
        "minutes"
    )

    bins = [0, 15, 30, 45, 60]

    labels = [
        "0-15 minutes",
        "15-30 minutes",
        "30-45 minutes",
        "45-60 minutes"
    ]

    group = group.copy()

    group["time_interval"] = pd.cut(
        group["time_difference_min"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    print("\nAcquisition-pair time intervals:")

    print(
        group["time_interval"].value_counts(sort=False)
    )

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
