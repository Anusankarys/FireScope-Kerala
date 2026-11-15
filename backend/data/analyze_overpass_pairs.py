
import pandas as pd
import geopandas as gpd
from pathlib import Path
from scipy.spatial import cKDTree

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

same_time_pairs = []
different_time_pairs = []

for i, j in candidate_pairs:

    first = gdf.iloc[i]
    second = gdf.iloc[j]

    if first["platform"] != second["platform"]:
        continue

    time_difference = abs(
        (
            first["acq_datetime_utc"]
            - second["acq_datetime_utc"]
        ).total_seconds()
    ) / 3600

    if time_difference > 1:
        continue

    record = {
        "platform": first["platform"],
        "distance_meters": round(
            first.geometry.distance(second.geometry), 2
        ),
        "time_difference_minutes": round(
            time_difference * 60, 2
        )
    }

    if (
        first["acq_datetime_utc"]
        == second["acq_datetime_utc"]
    ):
        same_time_pairs.append(record)
    else:
        different_time_pairs.append(record)

same_df = pd.DataFrame(same_time_pairs)
different_df = pd.DataFrame(different_time_pairs)

print("\n====================================")
print("SAME-PLATFORM OVERPASS ANALYSIS")
print("====================================")

print("Same acquisition-time pairs:", len(same_df))
print("Different acquisition-time pairs:", len(different_df))

if not same_df.empty:

    print("\nSame-time pairs by platform:")

    print(
        same_df["platform"]
        .value_counts()
        .to_string()
    )

    print("\nAverage distance for same-time pairs:")

    print(
        same_df.groupby("platform")["distance_meters"]
        .mean()
        .round(2)
        .to_string()
    )

if not different_df.empty:

    print("\nDifferent-time pairs by platform:")

    print(
        different_df["platform"]
        .value_counts()
        .to_string()
    )

    print("\nTime difference in minutes:")

    print(
        different_df["time_difference_minutes"]
        .describe()
        .round(2)
        .to_string()
    )

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
