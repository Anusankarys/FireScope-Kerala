
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
    / "unmatched_hourly_distribution.csv"
)

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

observations = pd.read_csv(INPUT_FILE)
matches = pd.read_csv(MATCH_FILE)

observations["acq_datetime_utc"] = pd.to_datetime(
    observations["acq_datetime_utc"], utc=True
)

matches["time_1_utc"] = pd.to_datetime(
    matches["time_1_utc"], utc=True
)

matches["time_2_utc"] = pd.to_datetime(
    matches["time_2_utc"], utc=True
)

print("\n====================================")
print("UNMATCHED HOURLY DISTRIBUTION")
print("====================================")

# --------------------------------------------------
# 2. IDENTIFY MATCHED OBSERVATIONS
# --------------------------------------------------

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

observations["observation_key"] = list(zip(
    observations["platform"],
    observations["latitude"].astype(float).round(7),
    observations["longitude"].astype(float).round(7),
    observations["acq_datetime_utc"]
))

observations["match_status"] = observations[
    "observation_key"
].isin(matched_keys)

observations["match_category"] = observations[
    "match_status"
].map({
    True: "Matched",
    False: "Unmatched"
})

# --------------------------------------------------
# 3. EXTRACT UTC HOUR
# --------------------------------------------------

observations["acquisition_hour_utc"] = (
    observations["acq_datetime_utc"].dt.hour
)

# --------------------------------------------------
# 4. HOURLY SUMMARY BY PLATFORM
# --------------------------------------------------

summary = (
    observations
    .groupby(
        ["platform", "acquisition_hour_utc", "match_category"]
    )
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

for category in ["Matched", "Unmatched"]:

    if category not in summary.columns:
        summary[category] = 0

summary["total_observations"] = (
    summary["Matched"] + summary["Unmatched"]
)

summary["matched_percentage"] = (
    summary["Matched"]
    / summary["total_observations"]
    * 100
).round(2)

summary["unmatched_percentage"] = (
    summary["Unmatched"]
    / summary["total_observations"]
    * 100
).round(2)

summary = summary.rename(columns={
    "Matched": "matched_observations",
    "Unmatched": "unmatched_observations"
})

summary = summary.sort_values(
    ["platform", "acquisition_hour_utc"]
)

# --------------------------------------------------
# 5. SAVE RESULTS
# --------------------------------------------------

summary.to_csv(OUTPUT_FILE, index=False)

# --------------------------------------------------
# 6. DISPLAY RESULTS
# --------------------------------------------------

print("\nHourly matching coverage by platform:")

for platform in sorted(summary["platform"].unique()):

    print(f"\n{platform}")

    platform_data = summary[
        summary["platform"] == platform
    ]

    print(
        platform_data[
            [
                "acquisition_hour_utc",
                "total_observations",
                "matched_observations",
                "unmatched_observations",
                "matched_percentage",
                "unmatched_percentage"
            ]
        ].to_string(index=False)
    )

# --------------------------------------------------
# 7. OVERALL HOURLY SUMMARY
# --------------------------------------------------

overall = (
    observations
    .groupby(["acquisition_hour_utc", "match_category"])
    .size()
    .unstack(fill_value=0)
)

for category in ["Matched", "Unmatched"]:

    if category not in overall.columns:
        overall[category] = 0

overall["total_observations"] = (
    overall["Matched"] + overall["Unmatched"]
)

overall["unmatched_percentage"] = (
    overall["Unmatched"]
    / overall["total_observations"]
    * 100
).round(2)

print("\n====================================")
print("OVERALL HOURLY MATCH COVERAGE")
print("====================================")

print(overall.to_string())

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("\nSaved results to:")
print(OUTPUT_FILE)
