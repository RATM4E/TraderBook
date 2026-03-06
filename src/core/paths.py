"""
Path utilities for TraderBook.

This module abstracts the *application install directory* (read-only code)
from the *user data directory* (writable CSV, logs, screenshots, backups).

Default user data directory: ~/Documents/TraderBook  (Windows-friendly)

A small JSON config is stored in %APPDATA%/TraderBook/config.json to remember
a user-selected data directory (future feature). For now we always use default,
but reading/writing via this module keeps things forward-compatible.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

APP_NAME = "TraderBook"
CONFIG_FILE_NAME = "config.json"


# ------------------------------------------------------------------#
# App (install) directory
# ------------------------------------------------------------------#
def get_app_dir() -> Path:
    """
    Root folder of the installed application (code).
    Derives two levels up from this file:
        core/ -> src/ -> <install root>
    """
    return Path(__file__).resolve().parents[1].parent


# ------------------------------------------------------------------#
# Config storage (APPDATA)
# ------------------------------------------------------------------#
def get_config_dir() -> Path:
    """Return %APPDATA%/TraderBook (Roaming)."""
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME
    # Fallback: ~/.config/TraderBook (non-Windows safety)
    return Path.home() / ".config" / APP_NAME


def _config_path() -> Path:
    return get_config_dir() / CONFIG_FILE_NAME


# ------------------------------------------------------------------#
# User data directory
# ------------------------------------------------------------------#
def get_default_user_data_dir() -> Path:
    """Default writable path: ~/Documents/TraderBook."""
    return Path.home() / "Documents" / APP_NAME


def load_user_data_dir() -> Path:
    """
    Load user data dir from config.json; if missing or invalid, return default.
    No directories are created here.
    """
    cfg_file = _config_path()
    if cfg_file.is_file():
        try:
            data = json.loads(cfg_file.read_text(encoding="utf-8"))
            p = Path(data.get("user_data_dir", "")).expanduser()
            if p.is_dir():
                return p
        except Exception:
            pass
    return get_default_user_data_dir()


def save_user_data_dir(path: Path) -> None:
    """Persist chosen user data dir to config.json."""
    cfg_dir = get_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    payload = {"user_data_dir": str(Path(path).expanduser().resolve())}
    (_config_path()).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


# ------------------------------------------------------------------#
# Directory bootstrap
# ------------------------------------------------------------------#
def ensure_user_data_dir(path: Path) -> None:
    """
    Create the standard TraderBook folder structure inside *path* if missing.

    We *do not* create CSV files here; that remains the responsibility of
    file_manager.initialize_files() so schema migrations stay centralized.
    """
    # root
    path.mkdir(parents=True, exist_ok=True)

    # subfolders
    (path / "logs").mkdir(exist_ok=True)
    (path / "screenshots").mkdir(exist_ok=True)
    (path / "screenshots" / "screenshots_entry").mkdir(exist_ok=True)
    (path / "screenshots" / "screenshots_exit").mkdir(exist_ok=True)
    (path / "setup_images").mkdir(exist_ok=True)
    (path / "backups").mkdir(exist_ok=True)

    # user setting files are created lazily when saved
    # (language.txt, timezone.txt, reward_risk.txt, trades.csv, setups.csv, groups.csv)
