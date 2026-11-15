import geopandas as gpd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

boundary_file = (
    PROJECT_ROOT
    / "datasets"
    / "geoBoundaries-IND-ADM1_simplified.geojson"
)

gdf = gpd.read_file(boundary_file)

kerala = gdf[
    gdf["shapeName"].str.contains(
        "Kerala", case=False, na=False
    )
]

print("Kerala features found:", len(kerala))

if not kerala.empty:
    print("\nKerala state name:")
    print(kerala["shapeName"].to_string(index=False))

    print("\nKerala geographical bounds:")
    print(kerala.total_bounds)
else:
    print("Kerala was not found.")