
import pandas as pd
import geopandas as gpd
from pathlib import Path

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

OUTPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "unmatched_platform_by_grid.csv"
)

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

observations = pd.read_csv(INPUT_FILE)
matches = pd.read_csv(MATCH_FILE)
grid = pd.read_csv(GRID_FILE)

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

observations["match_category"] = observations[
    "match_status"
].map({
    True: "Matched",
    False: "Unmatched"
})

# --------------------------------------------------
# 3. CONVERT OBSERVATIONS TO PROJECTED POINTS
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
# 4. RECREATE THE SAME 10 KM GRID
# --------------------------------------------------

from shapely.geometry import box

BOUNDARY_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "geoBoundaries-IND-ADM1_simplified.geojson"
)

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

grid_gdf = gpd.GeoDataFrame(
    {"grid_id": grid_ids},
    geometry=grid_cells,
    crs="EPSG:32643"
)

# --------------------------------------------------
# 5. ASSIGN OBSERVATIONS TO GRID CELLS
# --------------------------------------------------

joined = gpd.sjoin(
    gdf,
    grid_gdf,
    how="inner",
    predicate="intersects"
)

# --------------------------------------------------
# 6. SELECT TOP 10 CELLS
# --------------------------------------------------

top_cells = (
    grid.sort_values(
        ["Unmatched", "total_observations"],
        ascending=[False, False]
    )
    .head(10)["grid_id"]
    .tolist()
)

unmatched = joined[
    (joined["match_category"] == "Unmatched")
    & (joined["grid_id"].isin(top_cells))
].copy()

# --------------------------------------------------
# 7. PLATFORM CONTRIBUTION
# --------------------------------------------------

summary = (
    unmatched
    .groupby(["grid_id", "platform"])
    .size()
    .reset_index(name="unmatched_observations")
)

summary["platform_percentage"] = (
    summary["unmatched_observations"]
    / summary.groupby("grid_id")[
        "unmatched_observations"
    ].transform("sum")
    * 100
).round(2)

summary = summary.sort_values(
    ["grid_id", "unmatched_observations"],
    ascending=[True, False]
)

summary.to_csv(OUTPUT_FILE, index=False)

# --------------------------------------------------
# 8. DISPLAY RESULTS
# --------------------------------------------------

print("\n====================================")
print("UNMATCHED OBSERVATIONS BY PLATFORM")
print("TOP 10 GRID CELLS")
print("====================================")

for cell_id in top_cells:

    cell_data = summary[
        summary["grid_id"] == cell_id
    ]

    total = int(
        cell_data["unmatched_observations"].sum()
    )

    print(f"\nGrid ID: {cell_id}")
    print("Total unmatched observations:", total)

    if cell_data.empty:
        print("No unmatched observations found.")
    else:
        print(
            cell_data[
                [
                    "platform",
                    "unmatched_observations",
                    "platform_percentage"
                ]
            ].to_string(index=False)
        )

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("\nSaved results to:")
print(OUTPUT_FILE)
