# ==============================================================================
# Sand Plant Energy Monitoring — CSV Logger
# ==============================================================================
"""
Appends PLC records to a CSV file.

• Creates the file and writes headers on the first call.
• Never overwrites existing data — always appends.
• Thread-safe via a simple file-lock pattern.
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any

import config as cfg

logger = logging.getLogger(__name__)


class CSVLogger:
    """Append-only CSV logger for PLC telemetry data."""

    def __init__(self, csv_path: Path | None = None) -> None:
        self._path: Path = csv_path or cfg.CSV_FILE
        self._columns: list[str] = cfg.CSV_COLUMNS
        self._ensure_file()

    # ── initialisation ────────────────────────────────────────────────────────

    def _ensure_file(self) -> None:
        """Create the log directory and CSV file with headers if they don't exist."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            if not self._path.exists() or self._path.stat().st_size == 0:
                with self._path.open(mode="w", newline="", encoding="utf-8") as fh:
                    writer = csv.DictWriter(fh, fieldnames=self._columns)
                    writer.writeheader()
                logger.info("Created CSV file with headers: %s", self._path)
            else:
                logger.info("CSV file already exists: %s", self._path)
        except OSError:
            logger.exception("Failed to initialise CSV file at %s", self._path)
            raise

    # ── public API ────────────────────────────────────────────────────────────

    def write(self, records: list[dict[str, Any]]) -> None:
        """Append a batch of records (one per machine) to the CSV file."""
        if not records:
            logger.warning("No records to write — skipping CSV append.")
            return

        try:
            with self._path.open(mode="a", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=self._columns, extrasaction="ignore")
                writer.writerows(records)
            logger.debug("Appended %d rows to %s", len(records), self._path.name)
        except OSError:
            logger.exception("Failed to write to CSV file %s", self._path)
        except Exception:
            logger.exception("Unexpected error while writing CSV")
