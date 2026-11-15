import io
from fastapi.responses import StreamingResponse
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_FILE = (
    BASE_DIR / "datasets" / "processed" /
    "firescope_harmonized.csv"
)

app = FastAPI(
    title="FireScope API",
    description="Kerala Satellite Fire Detection and Harmonization",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_csv(DATA_FILE)

df["latitude"] = pd.to_numeric(df["latitude"])
df["longitude"] = pd.to_numeric(df["longitude"])
df["frp"] = pd.to_numeric(df["frp"])
df["acq_datetime_utc"] = pd.to_datetime(
    df["acq_datetime_utc"], utc=True
)

@app.get("/")
def home():
    return {
        "project": "FireScope",
        "message": "FireScope API is running successfully",
        "total_detections": len(df)
    }


@app.get("/api/summary")
def summary():

    return {
        "total_detections": int(len(df)),
        "matched_detections": int(
            (df["match_status"] == "matched").sum()
        ),
        "unmatched_detections": int(
            (df["match_status"] == "unmatched").sum()
        ),
        "platforms": {
            str(k): int(v)
            for k, v in df["platform"].value_counts().items()
        },
        "sensor_families": {
            str(k): int(v)
            for k, v in df["sensor_family"].value_counts().items()
        },
        "average_frp": round(float(df["frp"].mean()), 2),
        "first_date": str(df["acq_datetime_utc"].min().date()),
        "last_date": str(df["acq_datetime_utc"].max().date())
    }


@app.get("/api/detections")
def detections(
    platform: str = Query(default="All"),
    status: str = Query(default="All"),
    limit: int = Query(default=5000, ge=1, le=10000)

):

    result = df.copy()

    if platform != "All":
        result = result[result["platform"] == platform]

    if status != "All":
        result = result[result["match_status"] == status]

    result = result.sort_values(
    "acq_datetime_utc",
    ascending=False
).head(limit)

    columns = [
        "latitude",
        "longitude",
        "platform",
        "sensor_family",
        "frp",
        "acq_datetime_utc",
        "daynight",
        "confidence",
        "match_status",
        "data_status"
    ]

    result = result[columns].copy()

    result["acq_datetime_utc"] = (
        result["acq_datetime_utc"].astype(str)
    )

    return {
        "count": len(result),
        "detections": result.where(
            pd.notna(result), None
        ).to_dict(orient="records")
    }


@app.get("/api/platforms")
def platforms():
    return {
        "platforms": sorted(
            df["platform"].dropna().unique().tolist()
        )
    }


@app.get("/api/activity")
def activity():
    daily = (
        df.set_index("acq_datetime_utc")
        .resample("D")
        .size()
    )

    monthly = (
        df.set_index("acq_datetime_utc")
        .resample("MS")
        .size()
    )

    daynight = df["daynight"].value_counts().to_dict()

    return {
        "daily": [
            {"date": str(date.date()), "detections": int(count)}
            for date, count in daily.items()
        ],
        "monthly": [
            {"month": date.strftime("%Y-%m"), "detections": int(count)}
            for date, count in monthly.items()
        ],
        "daynight": {
            str(key): int(value)
            for key, value in daynight.items()
        }
    }

@app.get("/api/export")
def export_csv(
    platform: str = Query(default="All"),
    status: str = Query(default="All")
):
    # Copy the original dataset
    result = df.copy()

    # Apply platform filter
    if platform != "All":
        result = result[result["platform"] == platform]

    # Apply match-status filter
    if status != "All":
        result = result[result["match_status"] == status]

    # Sort newest detections first
    result = result.sort_values(
        by="acq_datetime_utc",
        ascending=False
    )

    # Prepare CSV file in memory
    csv_buffer = io.StringIO()
    result.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=firescope_detections.csv"
        }
    )
