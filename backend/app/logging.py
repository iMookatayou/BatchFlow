from __future__ import annotations

import logging
import sys
from typing import Optional


def configure_logging(environment: str = "local") -> None:
    """
    Minimal structured logging setup.
    Production can replace formatter/handlers later without touching app logic.
    """
    level = logging.INFO if environment in ("staging", "prod", "production") else logging.DEBUG

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers in reload/dev
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or "app")
