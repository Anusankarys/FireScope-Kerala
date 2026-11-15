import pandas as pd
import geopandas as gpd
from pathlib import Path
from scipy.spatial.distance import pdist

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "overlap_groups.csv"
)

df = pd.read_csv(INPUT_FILE)

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["longitude"],
        df["latitude"]
    ),
    crs="EPSG:4326"
).to_crs("EPSG:32643")

results = []

for group_id, group in gdf.groupby("group_id"):

    coordinates = list(
        zip(
            group.geometry.x,
            group.geometry.y
        )
    )

    if len(coordinates) < 2:
        continue

    distances = pdist(coordinates)

    results.append({
        "group_id": group_id,
        "observations": len(group),
        "platforms": group["platforms_in_group"].iloc[0],
        "maximum_distance_m": round(distances.max(), 2),
        "mean_pairwise_distance_m": round(distances.mean(), 2),
        "time_span_hours": (
            pd.to_datetime(
                group["acq_datetime_utc"],
                utc=True
            ).max()
            -
            pd.to_datetime(
                group["acq_datetime_utc"],
                utc=True
            ).min()
        ).total_seconds() / 3600
    })

result = pd.DataFrame(results)

result = result.sort_values(
    "maximum_distance_m",
    ascending=False
)

print("\n====================================")
print("GROUP SPATIAL SPREAD ANALYSIS")
print("====================================")

print("\nMaximum group diameter statistics:")

print(
    result["maximum_distance_m"].describe()
)

print("\nGroups exceeding 500 metres:")
print(
    (result["maximum_distance_m"] > 500).sum()
)

print("\nGroups exceeding 1000 metres:")
print(
    (result["maximum_distance_m"] > 1000).sum()
)

print("\nLargest 10 groups by spatial spread:")

print(
    result.head(10).to_string(index=False)
)

print("\n====================================")
print("SPATIAL SPREAD ANALYSIS COMPLETED")
print("====================================")