
import pandas as pd
import geopandas as gpd
from pathlib import Path
from scipy.spatial import cKDTree
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "kerala_with_timestamps.csv"
)

df = pd.read_csv(INPUT_FILE)

df["acq_datetime_utc"] = pd.to_datetime(
    df["acq_datetime_utc"],
    utc=True
)

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["longitude"],
        df["latitude"]
    ),
    crs="EPSG:4326"
).to_crs("EPSG:32643")

coordinates = list(zip(gdf.geometry.x, gdf.geometry.y))

tree = cKDTree(coordinates)

candidate_pairs = tree.query_pairs(
    r=500,
    output_type="set"
)

acquisition_matches = defaultdict(int)
matched_observations = set()

for i, j in candidate_pairs:

    first = gdf.iloc[i]
    second = gdf.iloc[j]

    if first["platform"] == second["platform"]:
        continue

    time_difference = abs(
        (
            first["acq_datetime_utc"]
            - second["acq_datetime_utc"]
        ).total_seconds()
    ) / 3600

    if time_difference > 1:
        continue

    first_acquisition = (
        first["platform"],
        first["acq_datetime_utc"]
    )

    second_acquisition = (
        second["platform"],
        second["acq_datetime_utc"]
    )

    # Keep acquisition combinations in a consistent order
    acquisition_pair = tuple(
        sorted([first_acquisition, second_acquisition])
    )

    acquisition_matches[acquisition_pair] += 1

    matched_observations.add(i)
    matched_observations.add(j)

print("\n====================================")
print("ACQUISITION-LEVEL MATCH ANALYSIS")
print("====================================")

print("Pixel-level matching pairs:", sum(acquisition_matches.values()))

print(
    "Unique acquisition-pair combinations:",
    len(acquisition_matches)
)

print(
    "Unique observations matched:",
    len(matched_observations)
)

print("\nPlatform-pair acquisition combinations:")

platform_pair_counts = defaultdict(int)

for acquisition_pair in acquisition_matches:

    platforms = tuple(sorted([
        acquisition_pair[0][0],
        acquisition_pair[1][0]
    ]))

    platform_pair_counts[platforms] += 1

for platforms, count in sorted(
    platform_pair_counts.items(),
    key=lambda item: item[1],
    reverse=True
):
    print(f"{platforms[0]} + {platforms[1]}: {count}")

print("\n====================================")
print("TOP 10 ACQUISITION-PAIR COMBINATIONS")
print("====================================")

top_matches = sorted(
    acquisition_matches.items(),
    key=lambda item: item[1],
    reverse=True
)[:10]

for rank, (pair, count) in enumerate(top_matches, start=1):

    first, second = pair

    print(f"\nRank: {rank}")
    print(
        f"{first[0]} at {first[1]}"
    )
    print(
        f"{second[0]} at {second[1]}"
    )
    print("Pixel-level matching pairs:", count)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
