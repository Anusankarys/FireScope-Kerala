
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
    / "mutual_nearest_matches.csv"
)

DISTANCE_LIMIT = 500
TIME_LIMIT_MINUTES = 60

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

df["acq_datetime_utc"] = pd.to_datetime(
    df["acq_datetime_utc"],
    utc=True
)

df["latitude"] = pd.to_numeric(df["latitude"])
df["longitude"] = pd.to_numeric(df["longitude"])

# --------------------------------------------------
# 2. PROJECT COORDINATES
# --------------------------------------------------

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["longitude"],
        df["latitude"]
    ),
    crs="EPSG:4326"
).to_crs("EPSG:32643")

gdf = gdf.reset_index(drop=True)

coordinates = list(zip(
    gdf.geometry.x,
    gdf.geometry.y
))

platforms = sorted(gdf["platform"].unique())

all_mutual_matches = []

print("\n====================================")
print("MUTUAL NEAREST-NEIGHBOUR ANALYSIS")
print("Distance limit:", DISTANCE_LIMIT, "metres")
print("Time limit:", TIME_LIMIT_MINUTES, "minutes")
print("====================================")

# --------------------------------------------------
# 3. ANALYSE EACH PLATFORM COMBINATION
# --------------------------------------------------

for platform_a, platform_b in combinations(platforms, 2):

    indices_a = gdf.index[
        gdf["platform"] == platform_a
    ].tolist()

    indices_b = gdf.index[
        gdf["platform"] == platform_b
    ].tolist()

    coords_a = [coordinates[i] for i in indices_a]
    coords_b = [coordinates[i] for i in indices_b]

    tree_a = cKDTree(coords_a)
    tree_b = cKDTree(coords_b)

    # Store the nearest eligible partner for each observation.
    best_a = {}
    best_b = {}

    eligible_pairs = []

    # --------------------------------------------------
    # 4. FIND ALL ELIGIBLE CROSS-PLATFORM PAIRS
    # --------------------------------------------------

    for local_a, global_a in enumerate(indices_a):

        nearby_b = tree_b.query_ball_point(
            coords_a[local_a],
            r=DISTANCE_LIMIT
        )

        first = gdf.iloc[global_a]

        for local_b in nearby_b:

            global_b = indices_b[local_b]
            second = gdf.iloc[global_b]

            time_difference = abs(
                (
                    first["acq_datetime_utc"]
                    - second["acq_datetime_utc"]
                ).total_seconds()
            ) / 60

            if time_difference > TIME_LIMIT_MINUTES:
                continue

            distance = (
                gdf.geometry.iloc[global_a]
                .distance(gdf.geometry.iloc[global_b])
            )

            eligible_pairs.append({
                "index_a": global_a,
                "index_b": global_b,
                "distance_m": distance,
                "time_difference_min": time_difference
            })

            # Nearest eligible partner for A.
            rank_a = (
                distance,
                time_difference,
                global_b
            )

            if (
                global_a not in best_a
                or rank_a < best_a[global_a][0]
            ):
                best_a[global_a] = (
                    rank_a,
                    global_b
                )

            # Nearest eligible partner for B.
            rank_b = (
                distance,
                time_difference,
                global_a
            )

            if (
                global_b not in best_b
                or rank_b < best_b[global_b][0]
            ):
                best_b[global_b] = (
                    rank_b,
                    global_a
                )

    # --------------------------------------------------
    # 5. IDENTIFY MUTUAL NEAREST NEIGHBOURS
    # --------------------------------------------------

    mutual_pairs = []

    for pair in eligible_pairs:

        index_a = pair["index_a"]
        index_b = pair["index_b"]

        if (
            best_a.get(index_a, (None, None))[1] == index_b
            and
            best_b.get(index_b, (None, None))[1] == index_a
        ):

            first = gdf.iloc[index_a]
            second = gdf.iloc[index_b]

            mutual_pairs.append({
                "platform_1": platform_a,
                "platform_2": platform_b,
                "latitude_1": first["latitude"],
                "longitude_1": first["longitude"],
                "latitude_2": second["latitude"],
                "longitude_2": second["longitude"],
                "time_1_utc": first["acq_datetime_utc"],
                "time_2_utc": second["acq_datetime_utc"],
                "time_difference_min": pair["time_difference_min"],
                "distance_meters": pair["distance_m"],
                "frp_1": first["frp"],
                "frp_2": second["frp"]
            })

    all_mutual_matches.extend(mutual_pairs)

    print("\n------------------------------------")
    print(f"{platform_a} + {platform_b}")
    print("------------------------------------")

    print(
        "Eligible pixel pairs:",
        len(eligible_pairs)
    )

    print(
        "Observations with at least one eligible match:",
        len(set(
            [p["index_a"] for p in eligible_pairs]
            + [p["index_b"] for p in eligible_pairs]
        ))
    )

    print(
        "Mutual nearest-neighbour pairs:",
        len(mutual_pairs)
    )

    print(
        "Observations in mutual matches:",
        len(mutual_pairs) * 2
    )

    if mutual_pairs:

        distances = [
            p["distance_meters"]
            for p in mutual_pairs
        ]

        times = [
            p["time_difference_min"]
            for p in mutual_pairs
        ]

        print(
            "Mean mutual-match distance:",
            round(sum(distances) / len(distances), 2),
            "metres"
        )

        print(
            "Mean mutual-match time difference:",
            round(sum(times) / len(times), 2),
            "minutes"
        )

# --------------------------------------------------
# 6. SAVE RESULTS
# --------------------------------------------------

result_df = pd.DataFrame(all_mutual_matches)

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n====================================")
print("OVERALL SUMMARY")
print("====================================")

print(
    "Total mutual nearest-neighbour pairs:",
    len(result_df)
)

print(
    "Total eligible matches are counted separately "
    "for each platform combination."
)

print("\nSaved results to:")
print(OUTPUT_FILE)

print("\n====================================")
print("ANALYSIS COMPLETED")
print("====================================")
