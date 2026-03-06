"""
Application logging setup with rotation.

Previously a plain FileHandler was used (no rotation), which risked unbounded
log growth. Now we use RotatingFileHandler (10 MB × 10 backups) for each logger.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from . import config


LOG_MAX_BYTES = 10_000_000  # 10 MB
LOG_BACKUP_COUNT = 10


def _mk_rotating_handler(path: Path) -> RotatingFileHandler:
    path.parent.mkdir(parents=True, exist_ok=True)
    return RotatingFileHandler(
        filename=str(path),
        mode="a",
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
        delay=False,
    )


def setup_logger(name: str, logfile: Path) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = _mk_rotating_handler(logfile)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger


# Public loggers
app_logger = setup_logger("app", config.LOGS_DIR / "app.log")
backup_logger = setup_logger("backup", config.LOGS_DIR / "backup.log")
csv_logger = setup_logger("csv", config.LOGS_DIR / "CSV.log")


# Alias для обратной совместимости
logger = app_logger
