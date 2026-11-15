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

OUTPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "overlap_groups.csv"
)

MAX_DISTANCE = 500
MAX_TIME_HOURS = 1

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
    r=MAX_DISTANCE,
    output_type="set"
)

parent = list(range(len(gdf)))

def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

def union(a, b):
    root_a = find(a)
    root_b = find(b)

    if root_a != root_b:
        parent[root_b] = root_a

valid_pairs = 0

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

    if time_difference <= MAX_TIME_HOURS:
        union(i, j)
        valid_pairs += 1

groups = defaultdict(list)

for i in range(len(gdf)):
    groups[find(i)].append(i)

results = []

group_number = 0

for indices in groups.values():

    if len(indices) < 2:
        continue

    group = gdf.iloc[indices]

    platforms = sorted(group["platform"].unique())

    # Only retain groups containing multiple platforms
    if len(platforms) < 2:
        continue

    group_number += 1

    for index in indices:

        row = gdf.iloc[index]

        results.append({
            "group_id": group_number,
            "platform": row["platform"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "acq_datetime_utc": row["acq_datetime_utc"],
            "frp": row["frp"],
            "number_of_platforms": len(platforms),
            "platforms_in_group": ", ".join(platforms)
        })

result = pd.DataFrame(results)

result.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("MULTI-SATELLITE GROUP ANALYSIS")
print("====================================")

print("Total observations:", len(gdf))
print("Valid pairwise links:", valid_pairs)
print("Multi-satellite groups:", group_number)

if not result.empty:

    print("\nObservations in groups:", len(result))

    print("\nGroup size distribution:")
    print(
        result.groupby("group_id")
        .size()
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nPlatform count distribution:")
    print(
        result.groupby("group_id")["number_of_platforms"]
        .first()
        .value_counts()
        .sort_index()
        .to_string()
    )

print("\nSaved:", OUTPUT_FILE)
print("\nAnalysis completed!")