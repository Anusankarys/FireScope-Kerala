
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FOLDER = PROJECT_ROOT / "datasets" / "raw"

for file in RAW_FOLDER.rglob("*.json"):

    print("\n" + "=" * 60)
    print("FILE:", file.name)

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Data type:", type(data).__name__)

    if isinstance(data, list):
        print("Total records:", len(data))

        if data:
            print("\nAvailable columns:")
            print(list(data[0].keys()))

            print("\nFirst record:")
            print(data[0])

    elif isinstance(data, dict):
        print("Available keys:", list(data.keys()))
        print("\nSample data:")
        print(str(data)[:1000])
