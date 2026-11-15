
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
    / "daynight_match_coverage.csv"
)

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

observations = pd.read_csv(INPUT_FILE)
matches = pd.read_csv(MATCH_FILE)

print("\n====================================")
print("DAY AND NIGHT MATCH COVERAGE")
print("====================================")

# --------------------------------------------------
# 2. IDENTIFY MATCHED OBSERVATIONS
# --------------------------------------------------

matches["time_1_utc"] = pd.to_datetime(
    matches["time_1_utc"], utc=True
)

matches["time_2_utc"] = pd.to_datetime(
    matches["time_2_utc"], utc=True
)

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

observations["acq_datetime_utc"] = pd.to_datetime(
    observations["acq_datetime_utc"], utc=True
)

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
# 3. CLEAN DAY/NIGHT VALUES
# --------------------------------------------------

observations["daynight"] = (
    observations["daynight"]
    .astype(str)
    .str.strip()
    .str.upper()
)

print("\nDay/night values found:")

print(observations["daynight"].value_counts(dropna=False))

# --------------------------------------------------
# 4. OVERALL DAY/NIGHT SUMMARY
# --------------------------------------------------

overall = (
    observations
    .groupby(["daynight", "match_category"])
    .size()
    .unstack(fill_value=0)
)

for category in ["Matched", "Unmatched"]:

    if category not in overall.columns:
        overall[category] = 0

overall["total_observations"] = (
    overall["Matched"] + overall["Unmatched"]
)

overall["matched_percentage"] = (
    overall["Matched"]
    / overall["total_observations"]
    * 100
).round(2)

overall["unmatched_percentage"] = (
    overall["Unmatched"]
    / overall["total_observations"]
    * 100
).round(2)

print("\n====================================")
print("OVERALL DAY/NIGHT MATCH COVERAGE")
print("====================================")

print(overall.to_string())

# --------------------------------------------------
# 5. PLATFORM-WISE DAY/NIGHT SUMMARY
# --------------------------------------------------

platform_summary = (
    observations
    .groupby(
        ["platform", "daynight", "match_category"]
    )
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

for category in ["Matched", "Unmatched"]:

    if category not in platform_summary.columns:
        platform_summary[category] = 0

platform_summary["total_observations"] = (
    platform_summary["Matched"]
    + platform_summary["Unmatched"]
)

platform_summary["matched_percentage"] = (
    platform_summary["Matched"]
    / platform_summary["total_observations"]
    * 100
).round(2)

platform_summary["unmatched_percentage"] = (
    platform_summary["Unmatched"]
    / platform_summary["total_observations"]
    * 100
).round(2)

platform_summary = platform_summary.rename(columns={
    "Matched": "matched_observations",
    "Unmatched": "unmatched_observations"
})

print("\n====================================")
print("PLATFORM-WISE DAY/NIGHT COVERAGE")
print("====================================")

for platform in sorted(platform_summary["platform"].unique()):

    print(f"\n{platform}")

    platform_data = platform_summary[
        platform_summary["platform"] == platform
    ]

    print(platform_data.to_string(index=False))

# --------------------------------------------------
# 6. SAVE RESULTS
# --------------------------------------------------

platform_summary.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("\nSaved results to:")
print(OUTPUT_FILE)
