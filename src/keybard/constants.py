#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constants used throughout the keybard library.

This module provides configuration constants and environment variable helpers.
"""

from __future__ import annotations

import os

# Timeout to distinguish single ESC key press from start of escape sequence
ESCAPE_DELAY: float = 0.01

# Enable smooth scrolling with in-band window resize
SMOOTH_SCROLL: bool = True

# Factor for dimming colors (used in filter.py)
DIM_FACTOR: float = 0.5


def _get_environ_bool(name: str, default: bool = False) -> bool:
    """
    Get a boolean value from an environment variable.

    Args:
        name: Environment variable name
        default: Default value if not set

    Returns:
        True if the environment variable is set to "1", False otherwise
    """
    return os.environ.get(name, "1" if default else "0") == "1"


def _get_environ_int(name: str, default: int, minimum: int | None = None) -> int:
    """
    Get an integer value from an environment variable.

    Args:
        name: Environment variable name
        default: Default value if not set or invalid
        minimum: Minimum allowed value (optional)

    Returns:
        Integer value from environment, or default if not set/invalid
    """
    try:
        value = int(os.environ.get(name, str(default)))
        if minimum is not None and value < minimum:
            return minimum
        return value
    except ValueError:
        return default


def _get_environ_port(name: str, default: int) -> int:
    """
    Get a port number from an environment variable.

    Args:
        name: Environment variable name
        default: Default port if not set or invalid

    Returns:
        Port number (0-65535) or default if invalid
    """
    try:
        value = int(os.environ.get(name, str(default)))
        if 0 <= value <= 65535:
            return value
        return default
    except ValueError:
        return default
