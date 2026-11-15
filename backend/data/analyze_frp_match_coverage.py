
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
    / "frp_match_coverage.csv"
)

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

observations = pd.read_csv(INPUT_FILE)
matches = pd.read_csv(MATCH_FILE)

print("\n====================================")
print("FRP-BASED MATCH COVERAGE ANALYSIS")
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
# 3. CONVERT FRP TO NUMERIC
# --------------------------------------------------

observations["frp"] = pd.to_numeric(
    observations["frp"],
    errors="coerce"
)

print("\nFRP data quality:")

print("Total observations:", len(observations))
print("Missing FRP values:", observations["frp"].isna().sum())
print("Valid FRP values:", observations["frp"].notna().sum())

# --------------------------------------------------
# 4. FRP STATISTICS BY MATCH STATUS
# --------------------------------------------------

print("\n====================================")
print("FRP STATISTICS BY MATCH STATUS")
print("====================================")

overall_summary = (
    observations
    .groupby("match_category")["frp"]
    .agg(
        observation_count="count",
        mean_frp="mean",
        median_frp="median",
        minimum_frp="min",
        maximum_frp="max",
        standard_deviation="std"
    )
    .round(3)
)

print(overall_summary.to_string())

# --------------------------------------------------
# 5. PLATFORM-WISE FRP STATISTICS
# --------------------------------------------------

print("\n====================================")
print("PLATFORM-WISE FRP STATISTICS")
print("====================================")

platform_summary = (
    observations
    .groupby(["platform", "match_category"])["frp"]
    .agg(
        observation_count="count",
        mean_frp="mean",
        median_frp="median",
        minimum_frp="min",
        maximum_frp="max",
        standard_deviation="std"
    )
    .round(3)
)

print(platform_summary.to_string())

# --------------------------------------------------
# 6. CREATE EXPLORATORY FRP BANDS
# --------------------------------------------------

# These are exploratory bins, not official fire
# severity or fire-intensity classifications.

observations["frp_band"] = pd.cut(
    observations["frp"],
    bins=[-0.001, 1, 5, 10, 20, float("inf")],
    labels=[
        "0-1",
        ">1-5",
        ">5-10",
        ">10-20",
        ">20"
    ],
    include_lowest=True
)

# --------------------------------------------------
# 7. OVERALL FRP BAND MATCH COVERAGE
# --------------------------------------------------

print("\n====================================")
print("OVERALL FRP BAND MATCH COVERAGE")
print("====================================")

band_summary = (
    observations
    .dropna(subset=["frp_band"])
    .groupby(["frp_band", "match_category"], observed=False)
    .size()
    .unstack(fill_value=0)
)

for category in ["Matched", "Unmatched"]:

    if category not in band_summary.columns:
        band_summary[category] = 0

band_summary["total_observations"] = (
    band_summary["Matched"]
    + band_summary["Unmatched"]
)

band_summary["matched_percentage"] = (
    band_summary["Matched"]
    / band_summary["total_observations"].replace(0, pd.NA)
    * 100
).round(2)

band_summary["unmatched_percentage"] = (
    band_summary["Unmatched"]
    / band_summary["total_observations"].replace(0, pd.NA)
    * 100
).round(2)

print(band_summary.to_string())

# --------------------------------------------------
# 8. PLATFORM-WISE FRP BAND MATCH COVERAGE
# --------------------------------------------------

print("\n====================================")
print("PLATFORM-WISE FRP BAND COVERAGE")
print("====================================")

platform_band_summary = (
    observations
    .dropna(subset=["frp_band"])
    .groupby(
        ["platform", "frp_band", "match_category"],
        observed=False
    )
    .size()
    .unstack(fill_value=0)
)

for category in ["Matched", "Unmatched"]:

    if category not in platform_band_summary.columns:
        platform_band_summary[category] = 0

platform_band_summary["total_observations"] = (
    platform_band_summary["Matched"]
    + platform_band_summary["Unmatched"]
)


platform_band_summary["matched_percentage"] = (
    platform_band_summary["Matched"]
    .div(platform_band_summary["total_observations"].replace(0, float("nan")))
    .mul(100)
    .round(2)
)

platform_band_summary["unmatched_percentage"] = (
    platform_band_summary["Unmatched"]
    .div(platform_band_summary["total_observations"].replace(0, float("nan")))
    .mul(100)
    .round(2)
)


print(platform_band_summary.to_string())

# --------------------------------------------------
# 9. SAVE RESULTS
# --------------------------------------------------

overall_output = OUTPUT_FILE

platform_output = OUTPUT_FILE.with_name(
    "platform_frp_match_coverage.csv"
)

band_output = OUTPUT_FILE.with_name(
    "frp_band_match_coverage.csv"
)

platform_band_output = OUTPUT_FILE.with_name(
    "platform_frp_band_match_coverage.csv"
)

overall_summary.to_csv(overall_output)
platform_summary.to_csv(platform_output)
band_summary.to_csv(band_output)
platform_band_summary.to_csv(platform_band_output)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("\nSaved files:")
print(overall_output)
print(platform_output)
print(band_output)
print(platform_band_output)
