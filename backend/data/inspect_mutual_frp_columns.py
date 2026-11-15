import pandas as pd

file_path = "datasets/processed/mutual_nearest_matches.csv"

df = pd.read_csv(file_path)

print("====================================")
print("MUTUAL MATCH FILE INSPECTION")
print("====================================")

print("\nTotal matched pairs:", len(df))

print("\nColumn names:")
for column in df.columns:
    print("-", column)

print("\nFirst five records:")
print(df.head().to_string(index=False))