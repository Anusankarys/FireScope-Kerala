
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FOLDER = PROJECT_ROOT / "datasets" / "processed"

for file in sorted(PROCESSED_FOLDER.glob("*.csv")):

    df = pd.read_csv(file)

    print("\n" + "=" * 55)
    print("FILE:", file.name)
    print("Records:", len(df))
    print("Columns:", df.columns.tolist())

    if "acq_date" in df.columns and len(df) > 0:
        print("First date:", df["acq_date"].min())
        print("Last date:", df["acq_date"].max())

print("\nProcessed data verification completed!")
