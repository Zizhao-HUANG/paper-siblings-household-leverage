"""
Structured logging configuration.

Call ``setup_logging()`` once at application startup (CLI or webapp).
All modules use ``logging.getLogger(__name__)`` and inherit this config.
"""

from __future__ import annotations

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure root logger with a structured formatter.

    Parameters
    ----------
    level : int
        Logging level (default: ``logging.INFO``).
    """
    fmt = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers on repeated calls
    if not root.handlers:
        root.addHandler(handler)
