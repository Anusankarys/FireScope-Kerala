
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "acquisition_pair_strength.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "platform_pair_summary.csv"
)

df = pd.read_csv(INPUT_FILE)

# Summarize acquisition relationships by satellite pair
summary = (
    df.groupby(["platform_1", "platform_2"])
    .agg(
        acquisition_combinations=("matching_pairs", "count"),
        total_pixel_matches=("matching_pairs", "sum"),
        average_pixel_matches=("matching_pairs", "mean"),
        median_pixel_matches=("matching_pairs", "median"),
        maximum_pixel_matches=("matching_pairs", "max"),
        average_distance_m=("mean_distance_m", "mean"),
        average_time_difference_min=(
            "time_difference_hours",
            lambda x: x.mean() * 60
        )
    )
    .reset_index()
)

summary = summary.sort_values(
    "acquisition_combinations",
    ascending=False
)

summary.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("PLATFORM-PAIR STRENGTH COMPARISON")
print("====================================")

for _, row in summary.iterrows():

    pair_name = (
        f"{row['platform_1']} + {row['platform_2']}"
    )

    print(f"\n{pair_name}")

    print(
        "Acquisition combinations:",
        int(row["acquisition_combinations"])
    )

    print(
        "Total pixel matches:",
        int(row["total_pixel_matches"])
    )

    print(
        "Average pixel matches:",
        round(row["average_pixel_matches"], 2)
    )

    print(
        "Median pixel matches:",
        round(row["median_pixel_matches"], 2)
    )

    print(
        "Maximum pixel matches:",
        int(row["maximum_pixel_matches"])
    )

    print(
        "Average distance (m):",
        round(row["average_distance_m"], 2)
    )

    print(
        "Average time difference (min):",
        round(row["average_time_difference_min"], 2)
    )

print("\n====================================")
print("SUMMARY TABLE")
print("====================================")

print(summary.round(2).to_string(index=False))

print("\nSaved file:")
print(OUTPUT_FILE)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
