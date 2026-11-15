
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import box

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "kerala_with_timestamps.csv"
)

MATCH_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "mutual_nearest_matches.csv"
)

BOUNDARY_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "geoBoundaries-IND-ADM1_simplified.geojson"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "unmatched_spatial_distribution.csv"
)

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

observations = pd.read_csv(INPUT_FILE)
matches = pd.read_csv(MATCH_FILE)

observations["acq_datetime_utc"] = pd.to_datetime(
    observations["acq_datetime_utc"], utc=True
)

matches["time_1_utc"] = pd.to_datetime(
    matches["time_1_utc"], utc=True
)

matches["time_2_utc"] = pd.to_datetime(
    matches["time_2_utc"], utc=True
)

print("\n====================================")
print("UNMATCHED SPATIAL DISTRIBUTION")
print("====================================")

# --------------------------------------------------
# 2. IDENTIFY MATCHED OBSERVATIONS
# --------------------------------------------------

matched_keys = set()

for _, row in matches.iterrows():

    matched_keys.add((
        row["platform_1"],
        round(float(row["latitude_1"]), 7),
        round(float(row["longitude_1"]), 7),
        row["time_1_utc"]
    ))

    matched_keys.add((
        row["platform_2"],
        round(float(row["latitude_2"]), 7),
        round(float(row["longitude_2"]), 7),
        row["time_2_utc"]
    ))

observations["observation_key"] = list(zip(
    observations["platform"],
    observations["latitude"].astype(float).round(7),
    observations["longitude"].astype(float).round(7),
    observations["acq_datetime_utc"]
))

observations["match_status"] = observations[
    "observation_key"
].isin(matched_keys)

observations["match_category"] = observations[
    "match_status"
].map({
    True: "Matched",
    False: "Unmatched"
})

# --------------------------------------------------
# 3. CONVERT TO GEOGRAPHIC DATAFRAME
# --------------------------------------------------

gdf = gpd.GeoDataFrame(
    observations,
    geometry=gpd.points_from_xy(
        observations["longitude"],
        observations["latitude"]
    ),
    crs="EPSG:4326"
)

# Project to UTM 43N for distance-based grid analysis
gdf = gdf.to_crs(epsg=32643)

# --------------------------------------------------
# 4. CREATE KERALA GRID
# --------------------------------------------------

kerala = gpd.read_file(BOUNDARY_FILE)

kerala = kerala[
    kerala["shapeName"] == "Kerala"
].to_crs(epsg=32643)

kerala_geometry = kerala.geometry.iloc[0]

minx, miny, maxx, maxy = kerala_geometry.bounds

GRID_SIZE = 10000  # 10 km grid cells

grid_cells = []
grid_ids = []

grid_id = 0

x = minx

while x < maxx:

    y = miny

    while y < maxy:

        cell = box(
            x,
            y,
            x + GRID_SIZE,
            y + GRID_SIZE
        )

        if cell.intersects(kerala_geometry):

            clipped_cell = cell.intersection(
                kerala_geometry
            )

            if not clipped_cell.is_empty:

                grid_cells.append(clipped_cell)
                grid_ids.append(grid_id)

                grid_id += 1

        y += GRID_SIZE

    x += GRID_SIZE

grid = gpd.GeoDataFrame(
    {"grid_id": grid_ids},
    geometry=grid_cells,
    crs="EPSG:32643"
)

# --------------------------------------------------
# 5. ASSIGN OBSERVATIONS TO GRID CELLS
# --------------------------------------------------

joined = gpd.sjoin(
    gdf,
    grid,
    how="left",
    predicate="intersects"
)

# --------------------------------------------------
# 6. SUMMARIZE MATCHED AND UNMATCHED COUNTS
# --------------------------------------------------

summary = joined.pivot_table(
    index="grid_id",
    columns="match_category",
    values="platform",
    aggfunc="count",
    fill_value=0
)

for category in ["Matched", "Unmatched"]:

    if category not in summary.columns:
        summary[category] = 0

summary["total_observations"] = (
    summary["Matched"] + summary["Unmatched"]
)

summary["unmatched_percentage"] = (
    summary["Unmatched"]
    / summary["total_observations"]
    * 100
).round(2)

summary = summary.reset_index()

# --------------------------------------------------
# 7. ADD GRID CENTRE COORDINATES
# --------------------------------------------------

grid["grid_center"] = grid.geometry.centroid

grid["center_longitude"] = (
    grid["grid_center"].to_crs(epsg=4326).x
)

grid["center_latitude"] = (
    grid["grid_center"].to_crs(epsg=4326).y
)

result = grid.merge(
    summary,
    on="grid_id",
    how="left"
)

result = result.drop(columns=["geometry", "grid_center"])

result = result.fillna({
    "Matched": 0,
    "Unmatched": 0,
    "total_observations": 0,
    "unmatched_percentage": 0
})

# --------------------------------------------------
# 8. SAVE RESULTS
# --------------------------------------------------

result.to_csv(OUTPUT_FILE, index=False)

print("\nTotal grid cells:", len(result))

print(
    "Grid cells containing observations:",
    int((result["total_observations"] > 0).sum())
)

print(
    "Total observations:",
    int(result["total_observations"].sum())
)

print(
    "Total matched observations:",
    int(result["Matched"].sum())
)

print(
    "Total unmatched observations:",
    int(result["Unmatched"].sum())
)

print("\nTop 10 grid cells by unmatched percentage:")

populated = result[
    result["total_observations"] > 0
]

print(
    populated.sort_values(
        ["unmatched_percentage", "total_observations"],
        ascending=[False, False]
    )[
        [
            "grid_id",
            "center_latitude",
            "center_longitude",
            "total_observations",
            "Matched",
            "Unmatched",
            "unmatched_percentage"
        ]
    ].head(10).to_string(index=False)
)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("\nSaved results to:")
print(OUTPUT_FILE)
