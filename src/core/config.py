"""
Global configuration for TraderBook.

IMPORTANT: This module now uses a *user data directory* resolved via
core.paths.load_user_data_dir() instead of assuming that data lives inside
the application install tree.

No filesystem I/O (mkdir) is performed at import time; call
core.paths.ensure_user_data_dir() early in app startup.

All other modules should import paths from here (TRADES_FILE, etc.).
"""

from __future__ import annotations

from pathlib import Path

from .paths import (
    get_app_dir,
    load_user_data_dir,
)

# ------------------------------------------------------------------#
# Directories
# ------------------------------------------------------------------#

APP_DIR = get_app_dir()  # read-only code location
USER_DATA_DIR = load_user_data_dir()  # writable; typically ~/Documents/TraderBook

# For backward compatibility, we expose DATA_DIR = USER_DATA_DIR (old code expected "data/")
DATA_DIR = USER_DATA_DIR

# ------------------------------------------------------------------#
# Data files
# ------------------------------------------------------------------#
TRADES_FILE = DATA_DIR / "trades.csv"
SETUPS_FILE = DATA_DIR / "setups.csv"
GROUPS_FILE = DATA_DIR / "groups.csv"

LANGUAGE_FILE = DATA_DIR / "language.txt"
TIMEZONE_FILE = DATA_DIR / "timezone.txt"
REWARD_RISK_FILE = DATA_DIR / "reward_risk.txt"

# ------------------------------------------------------------------#
# Subdirectories
# ------------------------------------------------------------------#
LOGS_DIR = DATA_DIR / "logs"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
ENTRY_SCREENSHOTS_DIR = SCREENSHOTS_DIR / "screenshots_entry"
EXIT_SCREENSHOTS_DIR = SCREENSHOTS_DIR / "screenshots_exit"
SETUP_IMAGES_DIR = DATA_DIR / "setup_images"
BACKUPS_DIR = DATA_DIR / "backups"

# ------------------------------------------------------------------#
# CSV schema columns (unchanged)
# ------------------------------------------------------------------#
TRADES_COLUMNS = [
    "id", "market", "pair", "entry_date", "entry_price", "entry_size",
    "stop_loss", "tp1", "tp1_perc", "tp2", "tp2_perc", "tp3", "tp3_perc",
    "result_price", "release_date", "result", "profit_percent", "avg_rr",
    "timeframe", "status", "direction", "trade_type", "session",
    "entry_screenshot_1", "entry_screenshot_1_desc",
    "entry_screenshot_2", "entry_screenshot_2_desc",
    "exit_screenshot_1", "exit_screenshot_1_desc",
    "exit_screenshot_2", "exit_screenshot_2_desc",
    "notes",
]
SETUPS_COLUMNS = [
    "id", "setup_name", "description", "image_1", "image_1_desc", "image_2", "image_2_desc",
]
GROUPS_COLUMNS = [
    "group_name", "description",
]
