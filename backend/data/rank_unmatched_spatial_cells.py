
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "unmatched_spatial_distribution.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "ranked_unmatched_spatial_cells.csv"
)

# Load spatial distribution results
data = pd.read_csv(INPUT_FILE)

# Keep cells containing observations
data = data[data["total_observations"] > 0].copy()

# Calculate contribution to all unmatched observations
total_unmatched = data["Unmatched"].sum()

data["unmatched_contribution_percentage"] = (
    data["Unmatched"] / total_unmatched * 100
).round(2)

# Rank by absolute unmatched count
data = data.sort_values(
    ["Unmatched", "total_observations"],
    ascending=[False, False]
).reset_index(drop=True)

data["unmatched_rank"] = range(1, len(data) + 1)

# Select useful columns
columns = [
    "unmatched_rank",
    "grid_id",
    "center_latitude",
    "center_longitude",
    "total_observations",
    "Matched",
    "Unmatched",
    "unmatched_percentage",
    "unmatched_contribution_percentage"
]

result = data[columns]

# Save complete ranking
result.to_csv(OUTPUT_FILE, index=False)

print("\n====================================")
print("TOP SPATIAL AREAS BY UNMATCHED OBSERVATIONS")
print("====================================")

print(
    result.head(20).to_string(index=False)
)

print("\n====================================")
print("TOP 10 GRID CELLS SUMMARY")
print("====================================")

top_10 = result.head(10)

print(
    "Unmatched observations in top 10 cells:",
    int(top_10["Unmatched"].sum())
)

print(
    "Contribution to all unmatched observations:",
    round(top_10["unmatched_contribution_percentage"].sum(), 2),
    "%"
)

print(
    "Total observations in top 10 cells:",
    int(top_10["total_observations"].sum())
)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")

print("\nSaved results to:")
print(OUTPUT_FILE)
