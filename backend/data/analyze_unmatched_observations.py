
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
    / "platform_match_coverage.csv"
)

# Load original observations and mutual matches.
observations = pd.read_csv(INPUT_FILE)
matches = pd.read_csv(MATCH_FILE)

print("\n====================================")
print("OBSERVATION MATCH COVERAGE")
print("====================================")

results = []

for platform in sorted(observations["platform"].unique()):

    platform_observations = observations[
        observations["platform"] == platform
    ]

    total = len(platform_observations)

    # Identify observations participating in mutual matches.
    matched_ids = set()

    if not matches.empty:

        for column in ["latitude_1", "longitude_1",
                       "time_1_utc", "platform_1"]:

            pass

        # Match records using platform, coordinates and timestamp.
        for _, row in matches.iterrows():

            if row["platform_1"] == platform:

                matched_ids.add((
                    platform,
                    round(float(row["latitude_1"]), 7),
                    round(float(row["longitude_1"]), 7),
                    str(row["time_1_utc"])
                ))

            if row["platform_2"] == platform:

                matched_ids.add((
                    platform,
                    round(float(row["latitude_2"]), 7),
                    round(float(row["longitude_2"]), 7),
                    str(row["time_2_utc"])
                ))

    observation_ids = set()

    for _, row in platform_observations.iterrows():

        observation_ids.add((
            platform,
            round(float(row["latitude"]), 7),
            round(float(row["longitude"]), 7),
            str(row["acq_datetime_utc"])
        ))

    matched_count = len(
        observation_ids.intersection(matched_ids)
    )

    unmatched_count = total - matched_count

    percentage = (
        matched_count / total * 100
        if total else 0
    )

    unmatched_percentage = (
        unmatched_count / total * 100
        if total else 0
    )

    results.append({
        "platform": platform,
        "total_observations": total,
        "matched_observations": matched_count,
        "unmatched_observations": unmatched_count,
        "matched_percentage": round(percentage, 2),
        "unmatched_percentage": round(
            unmatched_percentage, 2
        )
    })

    print(f"\n{platform}")
    print("Total observations:", total)
    print("Matched observations:", matched_count)
    print("Unmatched observations:", unmatched_count)
    print("Matched percentage:", round(percentage, 2), "%")
    print("Unmatched percentage:", round(unmatched_percentage, 2), "%")

result_df = pd.DataFrame(results)

result_df.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("OVERALL SUMMARY")
print("====================================")

print(
    result_df.to_string(index=False)
)

print("\nSaved results to:")
print(OUTPUT_FILE)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

