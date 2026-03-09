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

APP_DIR = get_app_dir()       # read-only code location
USER_DATA_DIR = load_user_data_dir()  # writable; typically ~/Documents/TraderBook

# Aliases used across the codebase
BASE_DIR = APP_DIR            # src/ root — for locating locales, assets
DATA_DIR = USER_DATA_DIR      # writable user data

# ------------------------------------------------------------------#
# Data files
# ------------------------------------------------------------------#
TRADES_FILE  = DATA_DIR / "trades.csv"
SETUPS_FILE  = DATA_DIR / "setups.csv"
GROUPS_FILE  = DATA_DIR / "groups.csv"

LANGUAGE_FILE    = DATA_DIR / "language.txt"
TIMEZONE_FILE    = DATA_DIR / "timezone.txt"
REWARD_RISK_FILE = DATA_DIR / "reward_risk.txt"

# ------------------------------------------------------------------#
# Subdirectories
# ------------------------------------------------------------------#
LOGS_DIR          = DATA_DIR / "logs"
SCREENSHOTS_DIR   = DATA_DIR / "screenshots"
SETUP_IMAGES_DIR  = DATA_DIR / "setup_images"
BACKUPS_DIR       = DATA_DIR / "backups"

ENTRY_SCREENSHOTS_DIR = SCREENSHOTS_DIR / "screenshots_entry"
EXIT_SCREENSHOTS_DIR  = SCREENSHOTS_DIR / "screenshots_exit"

# Aliases for backward compatibility
SCREENSHOTS_ENTRY_DIR = ENTRY_SCREENSHOTS_DIR
SCREENSHOTS_EXIT_DIR  = EXIT_SCREENSHOTS_DIR

# ------------------------------------------------------------------#
# Formats
# ------------------------------------------------------------------#
DATE_FORMAT = "%Y-%m-%d"

# ------------------------------------------------------------------#
# CSV schema columns
# ------------------------------------------------------------------#
TRADES_COLUMNS = [
    "trade_deal", "market", "pair",
    "entry_date", "release_date",
    "entry_point", "stop_loss",
    "take_profit_one", "take_profit_one_percent",
    "take_profit_two", "take_profit_two_percent",
    "take_profit_three", "take_profit_three_percent",
    "risk_percent", "tick_size",
    "trade_setup", "trade_setup_group",
    "timeframe", "type", "session",
    "avg_rr", "profit_percent", "result", "status",
    "trend_tag", "notion_text", "screenshot",
    "entry_screenshot_1", "entry_screenshot_2", "entry_screenshot_3",
    "entry_description_1", "entry_description_2", "entry_description_3",
    "exit_screenshot_1", "exit_screenshot_2", "exit_screenshot_3",
    "exit_description_1", "exit_description_2", "exit_description_3",
]
SETUPS_COLUMNS = [
    "id", "setup_name", "group_name", "description",
    "image_1", "image_1_desc",
    "image_2", "image_2_desc",
]
GROUPS_COLUMNS = [
    "group_name", "description",
]
