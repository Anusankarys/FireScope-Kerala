
import pandas as pd
import geopandas as gpd
from pathlib import Path
from scipy.spatial import cKDTree
from collections import Counter

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

match_counts = Counter()
matched_pairs = []

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

    match_counts[i] += 1
    match_counts[j] += 1

    matched_pairs.append((i, j))

print("\n====================================")
print("CROSS-PLATFORM MATCH MULTIPLICITY")
print("====================================")

print("Total cross-platform pairs:", len(matched_pairs))

print(
    "Unique observations with at least one match:",
    len(match_counts)
)

print(
    "Observations without a cross-platform match:",
    len(gdf) - len(match_counts)
)

multiplicity = Counter(match_counts.values())

print("\nNumber of potential partners per observation:")

for number in sorted(multiplicity):
    print(
        f"{number} partner(s): {multiplicity[number]} observations"
    )

print("\nObservations with multiple partners:")

multiple = sum(
    count for partners, count in multiplicity.items()
    if partners > 1
)

print(multiple)

matched_platforms = Counter(
    gdf.iloc[index]["platform"]
    for index in match_counts
)

print("\nMatched observations by platform:")

for platform, count in matched_platforms.most_common():
    print(f"{platform}: {count}")

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
