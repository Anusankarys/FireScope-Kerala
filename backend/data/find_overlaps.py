
import pandas as pd
import geopandas as gpd
from pathlib import Path
from scipy.spatial import cKDTree
from itertools import combinations

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
    / "potential_overlaps.csv"
)

# Preliminary matching thresholds
MAX_DISTANCE_METERS = 1000
MAX_TIME_HOURS = 24

# Load data
df = pd.read_csv(INPUT_FILE)

df["acq_datetime_utc"] = pd.to_datetime(
    df["acq_datetime_utc"],
    utc=True
)

# Convert coordinates to a metric coordinate system
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["longitude"],
        df["latitude"]
    ),
    crs="EPSG:4326"
).to_crs("EPSG:32643")

# Extract projected coordinates
coordinates = list(
    zip(gdf.geometry.x, gdf.geometry.y)
)

# Find spatially close pairs
tree = cKDTree(coordinates)

candidate_pairs = tree.query_pairs(
    r=MAX_DISTANCE_METERS,
    output_type="set"
)

overlaps = []

for i, j in candidate_pairs:

    first = gdf.iloc[i]
    second = gdf.iloc[j]

    # Ignore detections from the same platform
    if first["platform"] == second["platform"]:
        continue

    # Calculate time difference
    time_difference = abs(
        (
            first["acq_datetime_utc"]
            - second["acq_datetime_utc"]
        ).total_seconds()
    ) / 3600

    if time_difference > MAX_TIME_HOURS:
        continue

    # Calculate spatial distance
    distance = first.geometry.distance(
        second.geometry
    )

    overlaps.append({
        "platform_1": first["platform"],
        "platform_2": second["platform"],
        "latitude_1": first["latitude"],
        "longitude_1": first["longitude"],
        "latitude_2": second["latitude"],
        "longitude_2": second["longitude"],
        "time_1_utc": first["acq_datetime_utc"],
        "time_2_utc": second["acq_datetime_utc"],
        "time_difference_hours": round(
            time_difference, 2
        ),
        "distance_meters": round(distance, 2),
        "frp_1": first["frp"],
        "frp_2": second["frp"]
    })

# Save results
result = pd.DataFrame(overlaps)

if not result.empty:
    result = result.sort_values(
        by=["time_difference_hours", "distance_meters"]
    )

result.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("SATELLITE OVERLAP ANALYSIS")
print("====================================")

print("Total original observations:", len(gdf))
print("Spatial candidate pairs:", len(candidate_pairs))
print("Potential cross-platform overlaps:", len(result))

if not result.empty:
    print("\nPlatform pair distribution:")

    platform_pairs = result.apply(
        lambda row: " + ".join(
            sorted([row["platform_1"], row["platform_2"]])
        ),
        axis=1
    )

    print(platform_pairs.value_counts())

    print("\nFirst 10 potential overlaps:")
    print(result.head(10).to_string(index=False))

print("\nSaved:", OUTPUT_FILE)
print("\nOverlap analysis completed!")
