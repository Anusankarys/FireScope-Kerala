
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

# Keep cross-platform matches within 500 metres
# and 60 minutes.
df = df[
    (df["distance_meters"] <= 500)
    &
    (df["time_difference_min"] <= 60)
].copy()

# Create platform-pair labels.
df["platform_pair"] = (
    df[["platform_1", "platform_2"]]
    .apply(lambda row: " + ".join(sorted(row)), axis=1)
)

print("\n====================================")
print("PLATFORM-PAIR TIME DISTRIBUTION")
print("500 metres / 60 minutes")
print("====================================")

for platform_pair, group in df.groupby("platform_pair"):

    print(f"\n{platform_pair}")
    print("Total pixel pairs:", len(group))

    print(
        "Minimum time difference:",
        round(group["time_difference_min"].min(), 2),
        "minutes"
    )

    print(
        "Median time difference:",
        round(group["time_difference_min"].median(), 2),
        "minutes"
    )

    print(
        "Mean time difference:",
        round(group["time_difference_min"].mean(), 2),
        "minutes"
    )

    print(
        "Maximum time difference:",
        round(group["time_difference_min"].max(), 2),
        "minutes"
    )

    print("\nTime intervals:")

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

    print(
        group["time_interval"]
        .value_counts(sort=False)
    )

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
