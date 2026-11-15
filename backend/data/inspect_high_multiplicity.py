
import pandas as pd
import geopandas as gpd
from pathlib import Path
from scipy.spatial import cKDTree
from collections import defaultdict, Counter

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

partners = defaultdict(list)

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

    distance = first.geometry.distance(second.geometry)

    partners[i].append((j, distance, time_difference))
    partners[j].append((i, distance, time_difference))

ranked = sorted(
    partners.items(),
    key=lambda item: len(item[1]),
    reverse=True
)

print("\n====================================")
print("TOP HIGH-MULTIPLICITY OBSERVATIONS")
print("====================================")

for rank, (index, matches) in enumerate(ranked[:10], start=1):

    observation = gdf.iloc[index]

    partner_platforms = Counter(
        gdf.iloc[partner_index]["platform"]
        for partner_index, _, _ in matches
    )

    max_distance = max(distance for _, distance, _ in matches)
    max_time = max(hours for _, _, hours in matches)

    print(f"\nRank: {rank}")
    print("Observation index:", index)
    print("Platform:", observation["platform"])
    print("Date/time UTC:", observation["acq_datetime_utc"])
    print("Latitude:", observation["latitude"])
    print("Longitude:", observation["longitude"])
    print("Number of partners:", len(matches))
    print("Partner platforms:", dict(partner_platforms))
    print("Maximum partner distance (m):", round(max_distance, 2))
    print("Maximum time difference (hours):", round(max_time, 2))

    print("Partner details:")

    for partner_index, distance, hours in matches:

        partner = gdf.iloc[partner_index]

        print(
            f"  {partner['platform']} | "
            f"{partner['acq_datetime_utc']} | "
            f"{distance:.2f} m | "
            f"{hours:.2f} hours"
        )

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
