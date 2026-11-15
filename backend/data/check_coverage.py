
import json
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FOLDER = PROJECT_ROOT / "datasets" / "raw"

for file in RAW_FOLDER.rglob("*.json"):

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print(f"\n{file.name}: No records")
        continue

    df = pd.DataFrame(data)

    df["acq_date"] = pd.to_datetime(
        df["acq_date"], errors="coerce"
    )

    print("\n" + "=" * 55)
    print("FILE:", file.name)
    print("Total records:", len(df))

    print("First observation:",
          df["acq_date"].min())

    print("Last observation:",
          df["acq_date"].max())

    print("Latitude range:",
          df["latitude"].min(),
          "to",
          df["latitude"].max())

    print("Longitude range:",
          df["longitude"].min(),
          "to",
          df["longitude"].max())

    print("Missing values:")
    print(df.isnull().sum().to_dict())
