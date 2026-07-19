# ==============================================================================
# Sand Plant Energy Monitoring — Dummy PLC Data Generator
# ==============================================================================
"""
Simulates realistic industrial PLC values for 10 machines.

Key design decisions:
  • Each machine maintains internal state so values evolve smoothly
    (random-walk with mean-reversion, not uniform random noise).
  • Energy is monotonically increasing (cumulative power × time).
  • Status transitions follow a Markov chain defined in config.py.
  • On Fault/Maintenance the machine draws near-zero current/power
    and temperature drifts upward.
  • Implements the DataSource ABC so it can be swapped with a real
    PLC reader without changing any downstream code.
"""

from __future__ import annotations

import logging
import random
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

import numpy as np

import config as cfg

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Abstract base class — the contract every data source must satisfy
# ──────────────────────────────────────────────────────────────────────────────
class DataSource(ABC):
    """Interface that both the dummy simulator and a real PLC reader implement."""

    @abstractmethod
    def read_all(self) -> list[dict[str, Any]]:
        """Return a list of dicts, one per machine, with the standard fields."""
        ...


# ──────────────────────────────────────────────────────────────────────────────
# Per-machine state container
# ──────────────────────────────────────────────────────────────────────────────
class _MachineState:
    """Holds the evolving state for a single simulated machine."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.status: str = "Running"

        # Initialise values near the midpoint of each range
        self.voltage: float = self._mid("Voltage")
        self.current: float = self._mid("Current")
        self.power: float = self._mid("Power")
        self.power_factor: float = self._mid("PowerFactor")
        self.frequency: float = self._mid("Frequency")
        self.temperature: float = self._mid("Temperature")
        self.energy: float = round(random.uniform(100.0, 500.0), 2)  # kWh seed

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _mid(param: str) -> float:
        r = cfg.VALUE_RANGES[param]
        return round((r["min"] + r["max"]) / 2, 4)

    @staticmethod
    def _walk(current: float, param: str, bias: float = 0.0) -> float:
        """Random walk with mean reversion, clamped to configured range."""
        r = cfg.VALUE_RANGES[param]
        midpoint = (r["min"] + r["max"]) / 2
        step = r["step_max"]

        # Mean-reversion pull (towards midpoint)
        reversion = 0.05 * (midpoint - current)
        delta = reversion + random.gauss(bias, step)
        new_val = current + delta
        return round(np.clip(new_val, r["min"], r["max"]), 4)

    # ── main update ───────────────────────────────────────────────────────────

    def tick(self) -> dict[str, Any]:
        """Advance the machine state by one polling cycle and return a record."""
        self._transition_status()
        self._update_values()
        return self._snapshot()

    def _transition_status(self) -> None:
        """Markov-chain status transition."""
        probs = cfg.STATUS_TRANSITION[self.status]
        states = list(probs.keys())
        weights = list(probs.values())
        self.status = random.choices(states, weights=weights, k=1)[0]

    def _update_values(self) -> None:
        """Generate the next set of realistic values."""
        is_active = self.status == "Running"

        if is_active:
            self.voltage = self._walk(self.voltage, "Voltage")
            self.current = self._walk(self.current, "Current")
            self.power = self._walk(self.power, "Power")
            self.power_factor = self._walk(self.power_factor, "PowerFactor")
            self.frequency = self._walk(self.frequency, "Frequency")
            self.temperature = self._walk(self.temperature, "Temperature")
        elif self.status == "Idle":
            # Idle — minimal draw, temperature cooling down
            self.voltage = self._walk(self.voltage, "Voltage")
            self.current = self._walk(max(self.current * 0.7, cfg.VALUE_RANGES["Current"]["min"]), "Current", bias=-0.5)
            self.power = self._walk(max(self.power * 0.7, cfg.VALUE_RANGES["Power"]["min"]), "Power", bias=-0.3)
            self.power_factor = self._walk(self.power_factor, "PowerFactor")
            self.frequency = self._walk(self.frequency, "Frequency")
            self.temperature = self._walk(self.temperature, "Temperature", bias=-0.4)
        else:
            # Fault / Maintenance — near-zero draw, temp may climb
            self.voltage = self._walk(self.voltage, "Voltage")
            self.current = self._walk(cfg.VALUE_RANGES["Current"]["min"], "Current", bias=-0.3)
            self.power = self._walk(cfg.VALUE_RANGES["Power"]["min"], "Power", bias=-0.2)
            self.power_factor = self._walk(self.power_factor, "PowerFactor", bias=-0.002)
            self.frequency = self._walk(self.frequency, "Frequency")
            temp_bias = 0.5 if self.status == "Fault" else -0.2
            self.temperature = self._walk(self.temperature, "Temperature", bias=temp_bias)

        # Energy is cumulative (kWh): power(kW) × interval(h)
        interval_hours = cfg.POLL_INTERVAL_SECONDS / 3600.0
        self.energy = round(self.energy + self.power * interval_hours, 4)

    def _snapshot(self) -> dict[str, Any]:
        """Return the current state as a flat dictionary."""
        return {
            "Timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "Machine": self.name,
            "Voltage": round(self.voltage, 2),
            "Current": round(self.current, 2),
            "Power": round(self.power, 2),
            "Energy": round(self.energy, 2),
            "PowerFactor": round(self.power_factor, 3),
            "Frequency": round(self.frequency, 2),
            "Temperature": round(self.temperature, 2),
            "Status": self.status,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Dummy PLC — concrete DataSource
# ──────────────────────────────────────────────────────────────────────────────
class DummyPLC(DataSource):
    """
    Simulates 10 industrial machines producing realistic, smoothly-evolving
    PLC telemetry.  Drop-in replacement target: implement DataSource with a
    real PLC client and swap the import in main.py.
    """

    def __init__(self, machines: list[str] | None = None) -> None:
        self._machines: list[_MachineState] = [
            _MachineState(name) for name in (machines or cfg.MACHINES)
        ]
        logger.info(
            "DummyPLC initialised with %d machines: %s",
            len(self._machines),
            [m.name for m in self._machines],
        )

    # ── public API ────────────────────────────────────────────────────────────

    def read_all(self) -> list[dict[str, Any]]:
        """Generate one reading per machine and return them all."""
        records: list[dict[str, Any]] = []
        for machine in self._machines:
            try:
                record = machine.tick()
                records.append(record)
            except Exception:
                logger.exception("Error generating data for machine %s", machine.name)
        logger.debug("Generated %d records", len(records))
        return records
