
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
    r=1000,
    output_type="set"
)

records = []

for i, j in candidate_pairs:

    first = gdf.iloc[i]
    second = gdf.iloc[j]

    if first["platform"] == second["platform"]:
        continue

    distance = first.geometry.distance(second.geometry)

    time_difference = abs(
        (
            first["acq_datetime_utc"]
            - second["acq_datetime_utc"]
        ).total_seconds()
    ) / 60

    if time_difference > 60:
        continue

    platforms = tuple(sorted([
        first["platform"],
        second["platform"]
    ]))

    acquisitions = tuple(sorted([
        (first["platform"], first["acq_datetime_utc"]),
        (second["platform"], second["acq_datetime_utc"])
    ]))

    records.append({
        "platform_pair": " + ".join(platforms),
        "distance_m": distance,
        "time_difference_min": time_difference,
        "acquisition_pair": str(acquisitions)
    })

matches = pd.DataFrame(records)

distance_thresholds = [250, 500, 750, 1000]
time_thresholds = [15, 30, 45, 60]

print("\n====================================")
print("DISTANCE THRESHOLD COMPARISON")
print("Time limit fixed at 60 minutes")
print("====================================")

for platform in sorted(matches["platform_pair"].unique()):

    subset = matches[matches["platform_pair"] == platform]

    print(f"\n{platform}")

    for threshold in distance_thresholds:

        selected = subset[
            subset["distance_m"] <= threshold
        ]

        print(
            f"{threshold} m: "
            f"{len(selected)} pixel pairs, "
            f"{selected['acquisition_pair'].nunique()} "
            "acquisition pairs"
        )

print("\n====================================")
print("TIME THRESHOLD COMPARISON")
print("Distance limit fixed at 500 metres")
print("====================================")

for platform in sorted(matches["platform_pair"].unique()):

    subset = matches[matches["platform_pair"] == platform]

    print(f"\n{platform}")

    for threshold in time_thresholds:

        selected = subset[
            (subset["distance_m"] <= 500)
            &
            (subset["time_difference_min"] <= threshold)
        ]

        print(
            f"{threshold} minutes: "
            f"{len(selected)} pixel pairs, "
            f"{selected['acquisition_pair'].nunique()} "
            "acquisition pairs"
        )

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
