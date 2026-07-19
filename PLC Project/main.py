# ==============================================================================
# Sand Plant Energy Monitoring — Main Orchestrator
# ==============================================================================
"""
Entry point for the Sand Plant Energy Monitoring system.

Workflow:
  1. Initialise the data source (DummyPLC — swap with real PLC reader here).
  2. Initialise storage back-ends (CSV + InfluxDB).
  3. Every POLL_INTERVAL_SECONDS, read data and push it to both loggers.
  4. Handle graceful shutdown on Ctrl+C.

To switch to a real PLC, change the import and instantiation in _build_data_source().
"""

from __future__ import annotations

import logging
import signal
import sys
import time
from typing import Any

import schedule

import config as cfg
from csv_logger import CSVLogger
from dummy_plc import DataSource, DummyPLC
from influx_logger import InfluxLogger

# ──────────────────────────────────────────────────────────────────────────────
# Logging setup
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT)
logger = logging.getLogger("main")


# ──────────────────────────────────────────────────────────────────────────────
# Factory helpers — change only _build_data_source() to swap PLC
# ──────────────────────────────────────────────────────────────────────────────
def _build_data_source() -> DataSource:
    """
    Build and return the active data source.

    ┌──────────────────────────────────────────────────────────────────────┐
    │  To switch to a real PLC reader, replace the two lines below:       │
    │                                                                      │
    │      from plc_reader import PLCReader          # your module         │
    │      return PLCReader(host="192.168.1.10")     # your constructor    │
    └──────────────────────────────────────────────────────────────────────┘
    """
    return DummyPLC()


# ──────────────────────────────────────────────────────────────────────────────
# Core polling loop
# ──────────────────────────────────────────────────────────────────────────────
class Monitor:
    """Orchestrates data collection and storage."""

    def __init__(self) -> None:
        self._data_source: DataSource = _build_data_source()
        self._csv_logger: CSVLogger = CSVLogger()
        self._influx_logger: InfluxLogger = InfluxLogger()
        self._running: bool = True
        self._cycle_count: int = 0

    def poll(self) -> None:
        """Execute one data-collection cycle."""
        self._cycle_count += 1
        logger.info("── Cycle %d ──────────────────────────────────────", self._cycle_count)

        # 1. Read data from the source
        records: list[dict[str, Any]] = self._data_source.read_all()
        if not records:
            logger.warning("Data source returned no records.")
            return

        # 2. Log a summary to the console
        self._log_summary(records)

        # 3. Write to CSV
        self._csv_logger.write(records)

        # 4. Write to InfluxDB
        self._influx_logger.write(records)

    def _log_summary(self, records: list[dict[str, Any]]) -> None:
        """Print a compact human-readable summary of the current cycle."""
        for r in records:
            alarms: list[str] = []
            if r["Temperature"] > cfg.ALARM_TEMP_THRESHOLD:
                alarms.append("🔥 HIGH TEMP")
            if r["Power"] > cfg.ALARM_POWER_THRESHOLD:
                alarms.append("⚡ OVERLOAD")
            alarm_str = f"  ALARMS: {', '.join(alarms)}" if alarms else ""
            logger.info(
                "%-10s | %-12s | %6.1fV  %5.1fA  %5.1fkW  %7.2fkWh  PF %.3f  %5.2fHz  %5.1f°C%s",
                r["Machine"],
                r["Status"],
                r["Voltage"],
                r["Current"],
                r["Power"],
                r["Energy"],
                r["PowerFactor"],
                r["Frequency"],
                r["Temperature"],
                alarm_str,
            )

    def stop(self) -> None:
        """Signal the run loop to stop."""
        self._running = False
        logger.info("Shutdown requested — finishing current cycle…")

    def run(self) -> None:
        """Start the scheduled polling loop."""
        logger.info(
            "Sand Plant Monitor starting — polling every %ds",
            cfg.POLL_INTERVAL_SECONDS,
        )

        # Schedule the polling job
        schedule.every(cfg.POLL_INTERVAL_SECONDS).seconds.do(self.poll)

        # Run an initial poll immediately
        self.poll()

        try:
            while self._running:
                schedule.run_pending()
                time.sleep(0.2)  # Prevent busy-waiting
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received.")
        finally:
            self._influx_logger.close()
            logger.info("Monitor shut down cleanly after %d cycles.", self._cycle_count)


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    monitor = Monitor()

    # Handle Ctrl+C and SIGTERM gracefully
    def _signal_handler(sig: int, frame: Any) -> None:
        monitor.stop()

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    monitor.run()


if __name__ == "__main__":
    main()
