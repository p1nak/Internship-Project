# ==============================================================================
# Sand Plant Energy Monitoring — Configuration
# ==============================================================================
"""
Central configuration file for the Sand Plant Energy Monitoring system.
All tunable parameters are defined here to ensure consistency across modules
and to make future changes easy (e.g., switching from dummy to real PLC).
"""

from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Project Paths
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent
LOG_DIR: Path = BASE_DIR / "logs"
CSV_FILE: Path = LOG_DIR / "plc_data.csv"

# ──────────────────────────────────────────────────────────────────────────────
# Polling
# ──────────────────────────────────────────────────────────────────────────────
POLL_INTERVAL_SECONDS: int = 2

# ──────────────────────────────────────────────────────────────────────────────
# Machine Definitions
# ──────────────────────────────────────────────────────────────────────────────
MACHINES: list[str] = [
    "Knockout",
    "BC1",
    "BC2",
    "BC5",
    "Blower",
    "Rotor",
    "Pump",
    "SF900",
    "Crusher",
    "Conveyor",
]

# ──────────────────────────────────────────────────────────────────────────────
# Machine Statuses & Transition Probabilities
# ──────────────────────────────────────────────────────────────────────────────
STATUSES: list[str] = ["Running", "Idle", "Maintenance", "Fault"]

# Markov-chain transition matrix — row = current state, columns = STATUSES
# Rows sum to 1.0.  Machines mostly stay in their current state.
STATUS_TRANSITION: dict[str, dict[str, float]] = {
    "Running":     {"Running": 0.92, "Idle": 0.04, "Maintenance": 0.02, "Fault": 0.02},
    "Idle":        {"Running": 0.30, "Idle": 0.60, "Maintenance": 0.07, "Fault": 0.03},
    "Maintenance": {"Running": 0.10, "Idle": 0.05, "Maintenance": 0.83, "Fault": 0.02},
    "Fault":       {"Running": 0.05, "Idle": 0.05, "Maintenance": 0.10, "Fault": 0.80},
}

# ──────────────────────────────────────────────────────────────────────────────
# Realistic Value Ranges (used by the dummy PLC simulator)
# ──────────────────────────────────────────────────────────────────────────────
VALUE_RANGES: dict[str, dict[str, float]] = {
    "Voltage":     {"min": 410.0, "max": 420.0, "step_max": 0.5},
    "Current":     {"min": 5.0,   "max": 35.0,  "step_max": 1.0},
    "Power":       {"min": 2.0,   "max": 25.0,  "step_max": 0.8},
    "PowerFactor": {"min": 0.90,  "max": 1.00,  "step_max": 0.005},
    "Frequency":   {"min": 49.80, "max": 50.20, "step_max": 0.02},
    "Temperature": {"min": 30.0,  "max": 70.0,  "step_max": 0.8},
}

# ──────────────────────────────────────────────────────────────────────────────
# Alarm Thresholds
# ──────────────────────────────────────────────────────────────────────────────
ALARM_TEMP_THRESHOLD: float = 65.0   # °C
ALARM_POWER_THRESHOLD: float = 22.0  # kW

# ──────────────────────────────────────────────────────────────────────────────
# InfluxDB Connection
# ──────────────────────────────────────────────────────────────────────────────
INFLUXDB_URL: str = "https://eu-central-1-1.aws.cloud2.influxdata.com"
INFLUXDB_TOKEN: str = "hKtlggJWj_OiEBnPBKG8apArIc9VmPcgttkQHPO2UjA8twd1EOeNBf7FwKadXOsh2OUfquWZhFcrKxsEGvlrTQ=="
INFLUXDB_ORG: str = "jetli-motors-energy"
INFLUXDB_BUCKET: str = "energy-readings"

# ──────────────────────────────────────────────────────────────────────────────
# CSV Columns (single source of truth)
# ──────────────────────────────────────────────────────────────────────────────
CSV_COLUMNS: list[str] = [
    "Timestamp",
    "Machine",
    "Voltage",
    "Current",
    "Power",
    "Energy",
    "PowerFactor",
    "Frequency",
    "Temperature",
    "Status",
]

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s | %(name)-18s | %(levelname)-7s | %(message)s"
