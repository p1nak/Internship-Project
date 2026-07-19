# ==============================================================================
# Sand Plant Monitoring — Main (Real PLC Data Format)
# ==============================================================================
"""
Entry point that generates data matching the REAL PLC format (sand muller system).
Uses the same InfluxDB + CSV pipeline but with the real column structure.

Usage:
    python main_real.py
"""

from __future__ import annotations

import logging
import signal
import time
from datetime import datetime, timezone
from typing import Any

import schedule
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import config as cfg
from csv_logger import CSVLogger
from dummy_real_plc import DummyRealPLC

# ──────────────────────────────────────────────────────────────────────────────
# Logging setup
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT)
logger = logging.getLogger("main_real")

# Measurement name matching the historical upload
MEASUREMENT = "SandPlantReal"

# CSV columns for the real format
REAL_CSV_COLUMNS = [
    "Timestamp", "CYCLE_NO", "COMP_PRESET_PCT", "SAND_TEMP",
    "CORRECTED_PRESET", "READJUST_WATER",
    "AS1_MEASURE", "CORRECTED_WATER_1",
    "AS2_MEASURE", "CORRECTED_WATER_2",
    "AS3_MEASURE", "CORRECTED_WATER_3",
    "VARIATION", "TOTAL_WATER", "CYCLE_TIME",
    "COMP_STRENGTH_PRESET", "COMP_STRENGTH_MEASURED",
    "WEIGHT_BENTONITE", "WEIGHT_COALDUST", "WEIGHT_OLD_SAND",
    "FINAL_MEASURE", "Rtc_First_Cycle_Start", "Sand_Too_Wet_Fault",
]

# Fields to write to InfluxDB
INFLUX_FIELDS = [
    "CYCLE_NO", "COMP_PRESET_PCT", "SAND_TEMP", "CORRECTED_PRESET",
    "READJUST_WATER", "AS1_MEASURE", "CORRECTED_WATER_1",
    "AS2_MEASURE", "CORRECTED_WATER_2", "AS3_MEASURE", "CORRECTED_WATER_3",
    "VARIATION", "TOTAL_WATER", "CYCLE_TIME",
    "COMP_STRENGTH_PRESET", "COMP_STRENGTH_MEASURED",
    "WEIGHT_BENTONITE", "WEIGHT_COALDUST", "WEIGHT_OLD_SAND",
    "FINAL_MEASURE", "Rtc_First_Cycle_Start", "Sand_Too_Wet_Fault",
]


class RealMonitor:
    """Orchestrates real-format PLC data collection and storage."""

    def __init__(self) -> None:
        self._plc = DummyRealPLC()
        self._csv_logger = CSVLogger(csv_path=cfg.LOG_DIR / "plc_real_data.csv")
        # Override CSV columns for real format
        self._csv_logger._columns = REAL_CSV_COLUMNS

        # InfluxDB connection
        self._client = InfluxDBClient(
            url=cfg.INFLUXDB_URL, token=cfg.INFLUXDB_TOKEN, org=cfg.INFLUXDB_ORG
        )
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)

        self._running = True
        self._cycle_count = 0

    def poll(self) -> None:
        """Execute one data-collection cycle."""
        self._cycle_count += 1
        records = self._plc.read_all()
        if not records:
            return

        rec = records[0]
        logger.info(
            "Cycle %.0f | Comp=%.0f | SandTemp=%.0f | Water=%.0f | "
            "AS1=%.0f AS2=%.0f AS3=%.0f | Final=%.0f | Wet=%d",
            rec["CYCLE_NO"], rec["COMP_PRESET_PCT"], rec["SAND_TEMP"],
            rec["TOTAL_WATER"], rec["AS1_MEASURE"], rec["AS2_MEASURE"],
            rec["AS3_MEASURE"], rec["FINAL_MEASURE"],
            int(rec["Sand_Too_Wet_Fault"]),
        )

        # Write to CSV
        self._csv_logger.write(records)

        # Write to InfluxDB
        self._write_influx(rec)

    def _write_influx(self, rec: dict[str, Any]) -> None:
        """Write a single record to InfluxDB."""
        try:
            point = Point(MEASUREMENT).time(
                datetime.now(tz=timezone.utc), WritePrecision.MS
            )
            for field in INFLUX_FIELDS:
                if field in rec and rec[field] is not None:
                    point = point.field(field, float(rec[field]))

            self._write_api.write(
                bucket=cfg.INFLUXDB_BUCKET, org=cfg.INFLUXDB_ORG, record=point
            )
            logger.debug("Wrote cycle %.0f to InfluxDB", rec["CYCLE_NO"])
        except Exception:
            logger.exception("Failed to write to InfluxDB")

    def stop(self) -> None:
        self._running = False
        logger.info("Shutdown requested…")

    def run(self) -> None:
        logger.info("Real PLC Monitor starting — polling every %ds", cfg.POLL_INTERVAL_SECONDS)

        schedule.every(cfg.POLL_INTERVAL_SECONDS).seconds.do(self.poll)
        self.poll()  # immediate first poll

        try:
            while self._running:
                schedule.run_pending()
                time.sleep(0.2)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received.")
        finally:
            self._client.close()
            logger.info("Monitor shut down after %d cycles.", self._cycle_count)


def main() -> None:
    monitor = RealMonitor()

    def _sig(sig: int, frame: Any) -> None:
        monitor.stop()

    signal.signal(signal.SIGINT, _sig)
    signal.signal(signal.SIGTERM, _sig)
    monitor.run()


if __name__ == "__main__":
    main()
