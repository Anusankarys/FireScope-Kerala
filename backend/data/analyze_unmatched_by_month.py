
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "kerala_with_timestamps.csv"
)

MATCH_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "mutual_nearest_matches.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "monthly_platform_match_coverage.csv"
)

# Load datasets
observations = pd.read_csv(INPUT_FILE)
matches = pd.read_csv(MATCH_FILE)

# Convert timestamps consistently
observations["acq_datetime_utc"] = pd.to_datetime(
    observations["acq_datetime_utc"], utc=True
)

matches["time_1_utc"] = pd.to_datetime(
    matches["time_1_utc"], utc=True
)
matches["time_2_utc"] = pd.to_datetime(
    matches["time_2_utc"], utc=True
)

# Create month column
observations["month"] = (
    observations["acq_datetime_utc"].dt.to_period("M").astype(str)
)

# Build matched observation keys
matched_keys = set()

for _, row in matches.iterrows():

    matched_keys.add((
        row["platform_1"],
        round(float(row["latitude_1"]), 7),
        round(float(row["longitude_1"]), 7),
        row["time_1_utc"]
    ))

    matched_keys.add((
        row["platform_2"],
        round(float(row["latitude_2"]), 7),
        round(float(row["longitude_2"]), 7),
        row["time_2_utc"]
    ))

# Identify matched observations
observations["observation_key"] = list(zip(
    observations["platform"],
    observations["latitude"].astype(float).round(7),
    observations["longitude"].astype(float).round(7),
    observations["acq_datetime_utc"]
))

observations["match_status"] = observations[
    "observation_key"
].isin(matched_keys)

# Monthly summary
results = []

for (platform, month), group in observations.groupby(
    ["platform", "month"]
):

    total = len(group)
    matched = int(group["match_status"].sum())
    unmatched = total - matched

    results.append({
        "platform": platform,
        "month": month,
        "total_observations": total,
        "matched_observations": matched,
        "unmatched_observations": unmatched,
        "matched_percentage": round(matched / total * 100, 2),
        "unmatched_percentage": round(unmatched / total * 100, 2)
    })

result_df = pd.DataFrame(results)

result_df = result_df.sort_values(
    ["platform", "month"]
)

# Save results
result_df.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("MONTHLY PLATFORM MATCH COVERAGE")
print("====================================")

for platform in sorted(result_df["platform"].unique()):

    print(f"\n{platform}")

    platform_data = result_df[
        result_df["platform"] == platform
    ]

    print(
        platform_data[
            [
                "month",
                "total_observations",
                "matched_observations",
                "unmatched_observations",
                "matched_percentage"
            ]
        ].to_string(index=False)
    )

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("\nSaved results to:")
print(OUTPUT_FILE)
