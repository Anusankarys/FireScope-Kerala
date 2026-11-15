
import json
import geopandas as gpd
import pandas as pd
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FOLDER = PROJECT_ROOT / "datasets" / "raw"

BOUNDARY_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "geoBoundaries-IND-ADM1_simplified.geojson"
)

OUTPUT_FOLDER = PROJECT_ROOT / "datasets" / "processed"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. LOAD KERALA BOUNDARY
# ==========================================

print("Loading Kerala geographical boundary...")

boundary = gpd.read_file(BOUNDARY_FILE)

kerala = boundary[
    boundary["shapeName"].str.contains(
        "Kerala", case=False, na=False
    )
]

if len(kerala) != 1:
    raise ValueError(
        f"Expected one Kerala boundary, found {len(kerala)}"
    )

kerala_geometry = kerala.geometry.iloc[0]

print("Kerala boundary loaded successfully!")


# ==========================================
# 3. PROCESS NASA JSON FILES
# ==========================================

for file in RAW_FOLDER.rglob("*.json"):

    print("\nProcessing:", file.name)

    with open(file, "r", encoding="utf-8") as f:
        records = json.load(f)

    if not records:
        print("No records found. Skipping.")
        continue

    df = pd.DataFrame(records)

    # Convert coordinates to numeric values
    df["latitude"] = pd.to_numeric(
        df["latitude"], errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"], errors="coerce"
    )

    # Remove records with invalid coordinates
    df = df.dropna(
        subset=["latitude", "longitude"]
    )

    # Create geographical points
    points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            df["longitude"],
            df["latitude"]
        ),
        crs="EPSG:4326"
    )

    # Filter observations inside Kerala
    filtered = points[
        points.geometry.intersects(kerala_geometry)
    ].copy()

    # Remove geometry before saving CSV
    filtered = filtered.drop(columns=["geometry"])

    # Save filtered observations
    output_file = OUTPUT_FOLDER / (
        file.stem + "_kerala.csv"
    )

    filtered.to_csv(output_file, index=False)

    print("Original records:", len(records))
    print("Kerala records:", len(filtered))
    print("Saved:", output_file.name)


print("\n================================")
print("KERALA DATA FILTERING COMPLETED")
print("================================")
