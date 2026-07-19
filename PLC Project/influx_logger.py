# ==============================================================================
# Sand Plant Energy Monitoring — InfluxDB Logger
# ==============================================================================
"""
Writes PLC telemetry data to InfluxDB 2.x using the official Python client.

• Uses batched writes for efficiency.
• Tags: Machine, Status   (indexed for fast Grafana queries)
• Fields: Voltage, Current, Power, Energy, PowerFactor, Frequency, Temperature
• Measurement: SandPlant
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import config as cfg

logger = logging.getLogger(__name__)


class InfluxLogger:
    """Writes PLC records to an InfluxDB 2.x bucket."""

    MEASUREMENT: str = "SandPlant"

    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
        org: str | None = None,
        bucket: str | None = None,
    ) -> None:
        self._url: str = url or cfg.INFLUXDB_URL
        self._token: str = token or cfg.INFLUXDB_TOKEN
        self._org: str = org or cfg.INFLUXDB_ORG
        self._bucket: str = bucket or cfg.INFLUXDB_BUCKET
        self._client: InfluxDBClient | None = None
        self._write_api = None
        self._connect()

    # ── connection ────────────────────────────────────────────────────────────

    def _connect(self) -> None:
        """Establish a connection to InfluxDB."""
        try:
            self._client = InfluxDBClient(
                url=self._url,
                token=self._token,
                org=self._org,
            )
            self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
            logger.info(
                "Connected to InfluxDB at %s (org=%s, bucket=%s)",
                self._url,
                self._org,
                self._bucket,
            )
        except Exception:
            logger.exception("Failed to connect to InfluxDB at %s", self._url)
            self._client = None
            self._write_api = None

    # ── public API ────────────────────────────────────────────────────────────

    def write(self, records: list[dict[str, Any]]) -> None:
        """Write a batch of PLC records to InfluxDB."""
        if not records:
            logger.warning("No records to write — skipping InfluxDB write.")
            return

        if self._write_api is None:
            logger.error("InfluxDB write API not available. Attempting reconnect…")
            self._connect()
            if self._write_api is None:
                logger.error("Reconnect failed — dropping %d records.", len(records))
                return

        points: list[Point] = []
        for rec in records:
            try:
                point = (
                    Point(self.MEASUREMENT)
                    .tag("Machine", rec["Machine"])
                    .tag("Status", rec["Status"])
                    .field("Voltage", float(rec["Voltage"]))
                    .field("Current", float(rec["Current"]))
                    .field("Power", float(rec["Power"]))
                    .field("Energy", float(rec["Energy"]))
                    .field("PowerFactor", float(rec["PowerFactor"]))
                    .field("Frequency", float(rec["Frequency"]))
                    .field("Temperature", float(rec["Temperature"]))
                    .time(datetime.now(tz=timezone.utc), WritePrecision.MS)
                )
                points.append(point)
            except (KeyError, ValueError, TypeError):
                logger.exception("Skipping malformed record: %s", rec)

        try:
            self._write_api.write(bucket=self._bucket, org=self._org, record=points)
            logger.debug("Wrote %d points to InfluxDB", len(points))
        except Exception:
            logger.exception("Failed to write %d points to InfluxDB", len(points))

    # ── cleanup ───────────────────────────────────────────────────────────────

    def close(self) -> None:
        """Gracefully close the InfluxDB client."""
        if self._client:
            try:
                self._client.close()
                logger.info("InfluxDB connection closed.")
            except Exception:
                logger.exception("Error closing InfluxDB connection")
