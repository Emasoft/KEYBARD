#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple logging stub for keybard.

Replaces Textual's logging system with a minimal implementation.
Only logs when KEYBARD_DEBUG environment variable is set.
"""

from __future__ import annotations

import os
import sys


def log(message: str, level: str = "info") -> None:
    """
    Log a message to stderr if debug mode is enabled.

    Args:
        message: Message to log
        level: Log level ("info", "warning", "error", "debug")
    """
    if os.environ.get("KEYBARD_DEBUG"):
        print(f"[KEYBARD {level.upper()}] {message}", file=sys.stderr)


def debug(message: str) -> None:
    """Log a debug message."""
    log(message, "debug")


def info(message: str) -> None:
    """Log an info message."""
    log(message, "info")


def warning(message: str) -> None:
    """Log a warning message."""
    log(message, "warning")


def error(message: str) -> None:
    """Log an error message."""
    log(message, "error")
