# ==============================================================================
# Sand Plant Monitoring — Dummy PLC for Real Data Format
# ==============================================================================
"""
Simulates PLC data matching the REAL data format from the sand mixing/muller system.
Generates realistic values based on the actual data ranges observed in the CSV.

This replaces the generic energy monitoring dummy — same DataSource ABC interface.
"""

from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from typing import Any

import numpy as np

from dummy_plc import DataSource
import config as cfg

logger = logging.getLogger(__name__)


class DummyRealPLC(DataSource):
    """
    Simulates a sand plant muller/mixer producing cycle-based PLC data
    matching the exact columns from the real PLC export.
    """

    def __init__(self) -> None:
        self._cycle_no: float = 83.0
        # Initialize values near the midpoints of observed ranges
        self._comp_preset_pct: float = 5000.0
        self._sand_temp: float = 5000.0
        self._corrected_preset: float = 6500.0
        self._readjust_water: float = 5000.0
        self._as1_measure: float = 5000.0
        self._corrected_water_1: float = 3000.0
        self._as2_measure: float = 5000.0
        self._corrected_water_2: float = 5000.0
        self._as3_measure: float = 5000.0
        self._corrected_water_3: float = 3000.0
        self._variation: float = 5000.0
        self._total_water: float = 5000.0
        self._cycle_time: float = 0.0
        self._comp_strength_preset: float = 5000.0
        self._comp_strength_measured: float = 0.0
        self._weight_bentonite: float = 0.0
        self._weight_coaldust: float = 0.0
        self._weight_old_sand: float = 0.0
        self._final_measure: float = 5000.0
        self._rtc_first_cycle_start: float = 1.0
        self._sand_too_wet_fault: float = 0.0

        logger.info("DummyRealPLC initialised (sand muller simulation)")

    @staticmethod
    def _walk(current: float, min_val: float, max_val: float, step: float, bias: float = 0.0) -> float:
        """Random walk with clamping."""
        midpoint = (min_val + max_val) / 2
        reversion = 0.03 * (midpoint - current)
        delta = reversion + random.gauss(bias, step)
        return round(float(np.clip(current + delta, min_val, max_val)), 1)

    def read_all(self) -> list[dict[str, Any]]:
        """Generate one record per cycle (single machine system)."""
        try:
            self._cycle_no += 1

            # Update values with realistic random walks based on observed data ranges
            self._comp_preset_pct = self._walk(self._comp_preset_pct, 2000, 10000, 300)
            self._sand_temp = self._walk(self._sand_temp, 500, 26000, 800)
            self._corrected_preset = self._walk(self._corrected_preset, 5000, 10000, 200)
            self._readjust_water = self._walk(self._readjust_water, 3000, 10000, 400)
            self._as1_measure = self._walk(self._as1_measure, 0, 15000, 500)
            self._corrected_water_1 = self._walk(self._corrected_water_1, -12000, 10000, 600)
            self._as2_measure = self._walk(self._as2_measure, 0, 10000, 400)
            self._corrected_water_2 = self._walk(self._corrected_water_2, -11000, 10000, 500)
            self._as3_measure = self._walk(self._as3_measure, 0, 10000, 400)
            self._corrected_water_3 = self._walk(self._corrected_water_3, -11000, 10000, 500)
            self._variation = self._walk(self._variation, -3000, 10000, 400)
            self._total_water = self._walk(self._total_water, 0, 10000, 300)
            self._comp_strength_preset = self._walk(self._comp_strength_preset, 0, 10000, 300)
            self._comp_strength_measured = self._walk(self._comp_strength_measured, 0, 500, 20)
            self._weight_bentonite = self._walk(self._weight_bentonite, 0, 200, 10)
            self._weight_coaldust = self._walk(self._weight_coaldust, 0, 200, 10)
            self._weight_old_sand = self._walk(self._weight_old_sand, 0, 500, 20)
            self._final_measure = self._walk(self._final_measure, 4000, 10000, 300)

            # Fault flags: small probability of triggering
            self._sand_too_wet_fault = 1.0 if random.random() < 0.05 else 0.0
            self._rtc_first_cycle_start = 1.0 if random.random() < 0.8 else 0.0

            record = {
                "Timestamp": datetime.now(tz=timezone.utc).isoformat(),
                "CYCLE_NO": self._cycle_no,
                "COMP_PRESET_PCT": self._comp_preset_pct,
                "SAND_TEMP": self._sand_temp,
                "CORRECTED_PRESET": self._corrected_preset,
                "READJUST_WATER": self._readjust_water,
                "AS1_MEASURE": self._as1_measure,
                "CORRECTED_WATER_1": self._corrected_water_1,
                "AS2_MEASURE": self._as2_measure,
                "CORRECTED_WATER_2": self._corrected_water_2,
                "AS3_MEASURE": self._as3_measure,
                "CORRECTED_WATER_3": self._corrected_water_3,
                "VARIATION": self._variation,
                "TOTAL_WATER": self._total_water,
                "CYCLE_TIME": self._cycle_time,
                "COMP_STRENGTH_PRESET": self._comp_strength_preset,
                "COMP_STRENGTH_MEASURED": self._comp_strength_measured,
                "WEIGHT_BENTONITE": self._weight_bentonite,
                "WEIGHT_COALDUST": self._weight_coaldust,
                "WEIGHT_OLD_SAND": self._weight_old_sand,
                "FINAL_MEASURE": self._final_measure,
                "Rtc_First_Cycle_Start": self._rtc_first_cycle_start,
                "Sand_Too_Wet_Fault": self._sand_too_wet_fault,
            }

            logger.debug("Cycle %d generated", self._cycle_no)
            return [record]

        except Exception:
            logger.exception("Error generating real-format PLC data")
            return []
