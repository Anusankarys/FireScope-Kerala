
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

acquisition_matches = defaultdict(list)

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

    acquisition_pair = tuple(
        sorted([first_acquisition, second_acquisition])
    )

    distance = first.geometry.distance(second.geometry)

    acquisition_matches[acquisition_pair].append({
        "distance": distance,
        "time_difference": time_difference
    })

records = []

for pair, matches in acquisition_matches.items():

    first, second = pair

    distances = [m["distance"] for m in matches]
    time_differences = [
        m["time_difference"] for m in matches
    ]

    records.append({
        "platform_1": first[0],
        "platform_2": second[0],
        "acquisition_1": first[1],
        "acquisition_2": second[1],
        "matching_pairs": len(matches),
        "mean_distance_m": sum(distances) / len(distances),
        "min_distance_m": min(distances),
        "max_distance_m": max(distances),
        "time_difference_hours": time_differences[0]
    })

result = pd.DataFrame(records)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "acquisition_pair_strength.csv"
)

result.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("ACQUISITION MATCHING STRENGTH")
print("====================================")

print("Total acquisition combinations:", len(result))

print("\nMatching-pair count statistics:")

print(
    result["matching_pairs"]
    .describe()
    .round(2)
    .to_string()
)

print("\nMean spatial distance statistics:")

print(
    result["mean_distance_m"]
    .describe()
    .round(2)
    .to_string()
)

print("\nAcquisition time difference statistics:")

print(
    (result["time_difference_hours"] * 60)
    .describe()
    .round(2)
    .to_string()
)

print("\nAcquisition combinations by matching strength:")

print("1 pair:",
      (result["matching_pairs"] == 1).sum())

print("2-5 pairs:",
      result["matching_pairs"].between(2, 5).sum())

print("6-10 pairs:",
      result["matching_pairs"].between(6, 10).sum())

print("More than 10 pairs:",
      (result["matching_pairs"] > 10).sum())

print("\nSaved file:")
print(OUTPUT_FILE)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
