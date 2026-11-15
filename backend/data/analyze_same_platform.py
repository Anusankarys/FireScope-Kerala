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

coordinates = list(
    zip(gdf.geometry.x, gdf.geometry.y)
)

tree = cKDTree(coordinates)

candidate_pairs = tree.query_pairs(
    r=500,
    output_type="set"
)

same_platform = []
cross_platform = []

for i, j in candidate_pairs:

    first = gdf.iloc[i]
    second = gdf.iloc[j]

    time_difference = abs(
        (
            first["acq_datetime_utc"]
            - second["acq_datetime_utc"]
        ).total_seconds()
    ) / 3600

    if time_difference > 1:
        continue

    distance = first.geometry.distance(second.geometry)

    record = {
        "platform_1": first["platform"],
        "platform_2": second["platform"],
        "distance_meters": round(distance, 2),
        "time_difference_hours": round(time_difference, 2)
    }

    if first["platform"] == second["platform"]:
        same_platform.append(record)
    else:
        cross_platform.append(record)

same_df = pd.DataFrame(same_platform)
cross_df = pd.DataFrame(cross_platform)

print("\n====================================")
print("SAME-PLATFORM VS CROSS-PLATFORM")
print("====================================")

print("Same-platform pairs:", len(same_df))
print("Cross-platform pairs:", len(cross_df))

if not same_df.empty:

    print("\nSame-platform distribution:")

    print(
        same_df["platform_1"]
        .value_counts()
        .to_string()
    )

    print("\nAverage same-platform distance:")

    print(
        same_df.groupby("platform_1")["distance_meters"]
        .mean()
        .round(2)
        .to_string()
    )

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")