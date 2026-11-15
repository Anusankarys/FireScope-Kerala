import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "potential_overlaps.csv"
)

df = pd.read_csv(INPUT_FILE)

thresholds = [
    (250, 1),
    (500, 1),
    (500, 3),
    (1000, 1),
    (1000, 3),
    (1000, 6),
    (1000, 24)
]

results = []

for max_distance, max_time in thresholds:

    matched = df[
        (df["distance_meters"] <= max_distance) &
        (df["time_difference_hours"] <= max_time)
    ]

    results.append({
        "Maximum distance (m)": max_distance,
        "Maximum time (hours)": max_time,
        "Potential overlaps": len(matched)
    })

result_df = pd.DataFrame(results)

print("\n====================================")
print("MATCHING THRESHOLD COMPARISON")
print("====================================")

print(result_df.to_string(index=False))

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")