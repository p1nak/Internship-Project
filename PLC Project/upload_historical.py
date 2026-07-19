# ==============================================================================
# Sand Plant Monitoring — Upload Historical PLC Data to InfluxDB
# ==============================================================================
"""
Reads the real PLC CSV data and writes it to InfluxDB Cloud.
Since the original data (Nov 2025) falls outside the retention period,
timestamps are shifted to start from 2 hours ago and spaced 1 minute apart.

Usage:
    python upload_historical.py
"""

from __future__ import annotations

import csv
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import config as cfg

logging.basicConfig(level="INFO", format=cfg.LOG_FORMAT)
logger = logging.getLogger("upload_historical")

# Path to the real PLC data
DATA_FILE = Path(__file__).resolve().parent / "data" / "real_plc_data.csv"

# Measurement name for real PLC data
MEASUREMENT = "SandPlantReal"

# Numeric fields to write (everything except id, timestamp)
NUMERIC_FIELDS = [
    "CYCLE_NO",
    "COMP_PRESET_PCT",
    "SAND_TEMP",
    "CORRECTED_PRESET",
    "READJUST_WATER",
    "AS1_MEASURE",
    "CORRECTED_WATER_1",
    "AS2_MEASURE",
    "CORRECTED_WATER_2",
    "AS3_MEASURE",
    "CORRECTED_WATER_3",
    "VARIATION",
    "TOTAL_WATER",
    "CYCLE_TIME",
    "COMP_STRENGTH_PRESET",
    "COMP_STRENGTH_MEASURED",
    "WEIGHT_BENTONITE",
    "WEIGHT_COALDUST",
    "WEIGHT_OLD_SAND",
    "FINAL_MEASURE",
    "Rtc_First_Cycle_Start",
    "Sand_Too_Wet_Fault",
]


def parse_float(value: str) -> float | None:
    """Safely parse a float value, returning None for empty strings."""
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def upload() -> None:
    """Read the CSV and write all rows to InfluxDB with shifted timestamps."""
    if not DATA_FILE.exists():
        logger.error("Data file not found: %s", DATA_FILE)
        sys.exit(1)

    # Connect to InfluxDB
    client = InfluxDBClient(
        url=cfg.INFLUXDB_URL,
        token=cfg.INFLUXDB_TOKEN,
        org=cfg.INFLUXDB_ORG,
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Read all rows first
    rows: list[dict[str, str]] = []
    with DATA_FILE.open(mode="r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(row)

    logger.info("Read %d rows from CSV", len(rows))

    # Shift timestamps: start from 2 hours ago, 1 minute apart per row
    # This keeps the data within the retention period
    now = datetime.now(tz=timezone.utc)
    start_time = now - timedelta(hours=2)

    points: list[Point] = []
    for i, row in enumerate(rows):
        ts = start_time + timedelta(minutes=i)

        # Build the point
        point = Point(MEASUREMENT).time(ts, WritePrecision.S)

        fields_added = 0
        for field in NUMERIC_FIELDS:
            val = parse_float(row.get(field, ""))
            if val is not None:
                point = point.field(field, val)
                fields_added += 1

        if fields_added > 0:
            points.append(point)

    logger.info(
        "Prepared %d points (timestamps: %s → %s)",
        len(points),
        start_time.strftime("%H:%M:%S UTC"),
        (start_time + timedelta(minutes=len(rows) - 1)).strftime("%H:%M:%S UTC"),
    )

    if not points:
        logger.error("No valid data points to upload!")
        client.close()
        sys.exit(1)

    # Write in batches of 50
    batch_size = 50
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        try:
            write_api.write(bucket=cfg.INFLUXDB_BUCKET, org=cfg.INFLUXDB_ORG, record=batch)
            logger.info("  Wrote batch %d–%d ✓", i + 1, min(i + batch_size, len(points)))
        except Exception:
            logger.exception("  Failed to write batch %d–%d", i + 1, i + batch_size)

    client.close()
    logger.info("Upload complete! %d points written to InfluxDB.", len(points))
    logger.info(
        "  Bucket: %s | Measurement: %s | Org: %s",
        cfg.INFLUXDB_BUCKET,
        MEASUREMENT,
        cfg.INFLUXDB_ORG,
    )


if __name__ == "__main__":
    upload()
