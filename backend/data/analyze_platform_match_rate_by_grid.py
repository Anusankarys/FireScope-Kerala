
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

GRID_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "unmatched_spatial_distribution.csv"
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
    / "platform_match_rate_by_grid.csv"
)

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

observations = pd.read_csv(INPUT_FILE)
matches = pd.read_csv(MATCH_FILE)
grid_summary = pd.read_csv(GRID_FILE)

observations["acq_datetime_utc"] = pd.to_datetime(
    observations["acq_datetime_utc"], utc=True
)

matches["time_1_utc"] = pd.to_datetime(
    matches["time_1_utc"], utc=True
)

matches["time_2_utc"] = pd.to_datetime(
    matches["time_2_utc"], utc=True
)

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

# --------------------------------------------------
# 3. CREATE PROJECTED OBSERVATION POINTS
# --------------------------------------------------

gdf = gpd.GeoDataFrame(
    observations,
    geometry=gpd.points_from_xy(
        observations["longitude"],
        observations["latitude"]
    ),
    crs="EPSG:4326"
).to_crs(epsg=32643)

# --------------------------------------------------
# 4. RECREATE THE 10 KM GRID
# --------------------------------------------------

kerala = gpd.read_file(BOUNDARY_FILE)

kerala = kerala[
    kerala["shapeName"] == "Kerala"
].to_crs(epsg=32643)

kerala_geometry = kerala.geometry.iloc[0]

minx, miny, maxx, maxy = kerala_geometry.bounds

GRID_SIZE = 10000

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
    how="inner",
    predicate="intersects"
)

# --------------------------------------------------
# 6. SELECT TOP 10 GRID CELLS
# --------------------------------------------------

top_cells = (
    grid_summary.sort_values(
        ["Unmatched", "total_observations"],
        ascending=[False, False]
    )
    .head(10)["grid_id"]
    .tolist()
)

selected = joined[
    joined["grid_id"].isin(top_cells)
].copy()

# --------------------------------------------------
# 7. CALCULATE PLATFORM MATCH RATES
# --------------------------------------------------

summary = (
    selected
    .groupby(["grid_id", "platform", "match_status"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

# Ensure both status columns exist
for status in [True, False]:

    if status not in summary.columns:
        summary[status] = 0

summary = summary.rename(columns={
    True: "matched_observations",
    False: "unmatched_observations"
})

summary["total_observations"] = (
    summary["matched_observations"]
    + summary["unmatched_observations"]
)

summary["matched_percentage"] = (
    summary["matched_observations"]
    / summary["total_observations"]
    * 100
).round(2)

summary["unmatched_percentage"] = (
    summary["unmatched_observations"]
    / summary["total_observations"]
    * 100
).round(2)

summary = summary.sort_values(
    ["grid_id", "platform"]
)

# --------------------------------------------------
# 8. SAVE RESULTS
# --------------------------------------------------

summary.to_csv(OUTPUT_FILE, index=False)

# --------------------------------------------------
# 9. DISPLAY RESULTS
# --------------------------------------------------

print("\n====================================")
print("PLATFORM MATCH RATES BY GRID")
print("TOP 10 GRID CELLS")
print("====================================")

for cell_id in top_cells:

    cell_data = summary[
        summary["grid_id"] == cell_id
    ]

    print(f"\nGrid ID: {cell_id}")

    print(
        cell_data[
            [
                "platform",
                "total_observations",
                "matched_observations",
                "unmatched_observations",
                "matched_percentage",
                "unmatched_percentage"
            ]
        ].to_string(index=False)
    )

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("\nSaved results to:")
print(OUTPUT_FILE)
