
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "potential_overlaps.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "acquisition_spatial_distribution.csv"
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

# Retain pairs within 60 minutes.
# The input already contains spatial candidates
# generated within 1,000 metres.
df = df[
    df["time_difference_min"] <= 60
].copy()

df["platform_pair"] = df.apply(
    lambda row: " + ".join(
        sorted([row["platform_1"], row["platform_2"]])
    ),
    axis=1
)

# Identify unique acquisition combinations.
df["acquisition_pair"] = df.apply(
    lambda row: tuple(sorted([
        (row["platform_1"], row["time_1_utc"]),
        (row["platform_2"], row["time_2_utc"])
    ])),
    axis=1
)

# Summarize spatial relationships for each acquisition pair.
acquisitions = (
    df.groupby(["platform_pair", "acquisition_pair"])
    .agg(
        pixel_pair_count=("distance_meters", "size"),
        minimum_distance_m=("distance_meters", "min"),
        mean_distance_m=("distance_meters", "mean"),
        median_distance_m=("distance_meters", "median"),
        maximum_distance_m=("distance_meters", "max"),
        time_difference_min=("time_difference_min", "first")
    )
    .reset_index()
)

# Save detailed acquisition-level results.
acquisitions.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("ACQUISITION SPATIAL DISTRIBUTION")
print("Time limit: 60 minutes")
print("Candidate distance limit: 1,000 metres")
print("====================================")

for platform_pair, group in acquisitions.groupby("platform_pair"):

    print(f"\n{platform_pair}")

    print("Unique acquisition pairs:", len(group))

    print(
        "Total pixel matches:",
        group["pixel_pair_count"].sum()
    )

    for column, label in [
        ("mean_distance_m", "Mean acquisition-pair distance"),
        ("median_distance_m", "Median acquisition-pair distance"),
        ("maximum_distance_m", "Maximum acquisition-pair distance")
    ]:

        print(
            f"{label}:",
            round(group[column].mean(), 2),
            "metres"
        )

    print("\nAcquisition pairs by minimum distance:")

    bins = [0, 100, 250, 500, 750, 1000]

    labels = [
        "0-100 m",
        "100-250 m",
        "250-500 m",
        "500-750 m",
        "750-1000 m"
    ]

    group = group.copy()

    group["distance_interval"] = pd.cut(
        group["minimum_distance_m"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    print(
        group["distance_interval"]
        .value_counts(sort=False)
    )

print("\nSaved detailed results to:")
print(OUTPUT_FILE)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
