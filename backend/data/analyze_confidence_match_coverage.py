
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
    / "confidence_match_coverage.csv"
)

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

observations = pd.read_csv(INPUT_FILE)
matches = pd.read_csv(MATCH_FILE)

print("\n====================================")
print("CONFIDENCE-BASED MATCH COVERAGE")
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
# 3. CLEAN CONFIDENCE VALUES
# --------------------------------------------------

observations["confidence"] = (
    observations["confidence"]
    .astype(str)
    .str.strip()
    .str.lower()
)

# --------------------------------------------------
# 4. SEPARATE MODIS AND VIIRS
# --------------------------------------------------

modis = observations[
    observations["sensor_family"] == "MODIS"
].copy()

viirs = observations[
    observations["sensor_family"] == "VIIRS"
].copy()

# --------------------------------------------------
# 5. VIIRS CONFIDENCE ANALYSIS
# --------------------------------------------------

print("\n====================================")
print("VIIRS CONFIDENCE MATCH COVERAGE")
print("====================================")

viirs_summary = (
    viirs
    .groupby(["confidence", "match_category"])
    .size()
    .unstack(fill_value=0)
)

for category in ["Matched", "Unmatched"]:

    if category not in viirs_summary.columns:
        viirs_summary[category] = 0

viirs_summary["total_observations"] = (
    viirs_summary["Matched"]
    + viirs_summary["Unmatched"]
)

viirs_summary["matched_percentage"] = (
    viirs_summary["Matched"]
    / viirs_summary["total_observations"]
    * 100
).round(2)

viirs_summary["unmatched_percentage"] = (
    viirs_summary["Unmatched"]
    / viirs_summary["total_observations"]
    * 100
).round(2)

print(viirs_summary.to_string())

# --------------------------------------------------
# 6. VIIRS PLATFORM-WISE CONFIDENCE ANALYSIS
# --------------------------------------------------

print("\n====================================")
print("VIIRS PLATFORM-WISE CONFIDENCE")
print("====================================")

viirs_platform_summary = (
    viirs
    .groupby(
        ["platform", "confidence", "match_category"]
    )
    .size()
    .unstack(fill_value=0)
)

for category in ["Matched", "Unmatched"]:

    if category not in viirs_platform_summary.columns:
        viirs_platform_summary[category] = 0

viirs_platform_summary["total_observations"] = (
    viirs_platform_summary["Matched"]
    + viirs_platform_summary["Unmatched"]
)

viirs_platform_summary["matched_percentage"] = (
    viirs_platform_summary["Matched"]
    / viirs_platform_summary["total_observations"]
    * 100
).round(2)

viirs_platform_summary["unmatched_percentage"] = (
    viirs_platform_summary["Unmatched"]
    / viirs_platform_summary["total_observations"]
    * 100
).round(2)

print(viirs_platform_summary.to_string())

# --------------------------------------------------
# 7. MODIS NUMERIC CONFIDENCE ANALYSIS
# --------------------------------------------------

print("\n====================================")
print("MODIS NUMERIC CONFIDENCE ANALYSIS")
print("====================================")

modis["confidence_numeric"] = pd.to_numeric(
    modis["confidence"],
    errors="coerce"
)

modis = modis.dropna(
    subset=["confidence_numeric"]
).copy()

# Exploratory confidence bands.
# These are numerical ranges, not official quality classes.

modis["confidence_band"] = pd.cut(
    modis["confidence_numeric"],
    bins=[-1, 30, 60, 100],
    labels=["0-30", "31-60", "61-100"]
)

modis_summary = (
    modis
    .groupby(
        ["confidence_band", "match_category"],
        observed=False
    )
    .size()
    .unstack(fill_value=0)
)

for category in ["Matched", "Unmatched"]:

    if category not in modis_summary.columns:
        modis_summary[category] = 0

modis_summary["total_observations"] = (
    modis_summary["Matched"]
    + modis_summary["Unmatched"]
)

modis_summary["matched_percentage"] = (
    modis_summary["Matched"]
    / modis_summary["total_observations"].replace(0, pd.NA)
    * 100
).round(2)

modis_summary["unmatched_percentage"] = (
    modis_summary["Unmatched"]
    / modis_summary["total_observations"].replace(0, pd.NA)
    * 100
).round(2)

print(modis_summary.to_string())

# --------------------------------------------------
# 8. SAVE SEPARATE RESULTS
# --------------------------------------------------

viirs_output = OUTPUT_FILE.with_name(
    "viirs_confidence_match_coverage.csv"
)

modis_output = OUTPUT_FILE.with_name(
    "modis_confidence_match_coverage.csv"
)

viirs_platform_output = OUTPUT_FILE.with_name(
    "viirs_platform_confidence_match_coverage.csv"
)

viirs_summary.to_csv(viirs_output)
modis_summary.to_csv(modis_output)
viirs_platform_summary.to_csv(viirs_platform_output)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("\nSaved files:")
print(viirs_output)
print(modis_output)
print(viirs_platform_output)
