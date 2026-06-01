"""Shared plugin utility helpers for file-based plugin discovery."""

import logging
import os

logger = logging.getLogger(__name__)


def _is_file_plugins_disabled() -> bool:
    """Return whether file plugin discovery is disabled via environment."""
    raw_value = os.getenv("CANTEEN_DISABLE_FILE_PLUGINS", "")
    return raw_value.strip().lower() in {"1", "true", "yes"}
