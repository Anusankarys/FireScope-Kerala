import pandas as pd
import geopandas as gpd
from pathlib import Path
from scipy.spatial.distance import cdist

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "overlap_groups.csv"
)

df = pd.read_csv(INPUT_FILE)

GROUP_ID = 433

group = df[df["group_id"] == GROUP_ID].copy()

gdf = gpd.GeoDataFrame(
    group,
    geometry=gpd.points_from_xy(
        group["longitude"],
        group["latitude"]
    ),
    crs="EPSG:4326"
).to_crs("EPSG:32643")

coordinates = list(
    zip(gdf.geometry.x, gdf.geometry.y)
)

distance_matrix = cdist(
    coordinates,
    coordinates
)

print("\n====================================")
print("INSPECTING GROUP", GROUP_ID)
print("====================================")

print("\nNumber of observations:", len(gdf))

print("\nObservations by platform:")
print(gdf["platform"].value_counts())

print("\nIndividual observations:\n")

print(
    gdf[
        [
            "platform",
            "latitude",
            "longitude",
            "acq_datetime_utc",
            "frp"
        ]
    ].to_string(index=False)
)

print("\nMaximum distance:", round(distance_matrix.max(), 2), "meters")

i, j = divmod(distance_matrix.argmax(), len(gdf))

print("\nFarthest observation pair:")

print(
    gdf.iloc[i][
        ["platform", "latitude", "longitude", "acq_datetime_utc"]
    ]
)

print(
    gdf.iloc[j][
        ["platform", "latitude", "longitude", "acq_datetime_utc"]
    ]
)

print("\n====================================")
print("GROUP INSPECTION COMPLETED")
print("====================================")
