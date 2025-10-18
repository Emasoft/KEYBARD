#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KEYBARD - Cross-platform keyboard input library.

This library provides a simple, unified API for reading keyboard input
from the terminal on Linux, macOS, and Windows.

KEYBARD is keyboard-only - no mouse support.

Example:
    ```python
    from keybard import KeyboardReader

    with KeyboardReader() as reader:
        while True:
            event = reader.read_key()
            if event and event.key == "ctrl+c":
                break
            if event:
                print(f"Got: {event.key}")
    ```
"""

from __future__ import annotations

# =============================================================================
# Core API - KeyboardReader is the primary entry point
# =============================================================================
from keybard.reader import KeyboardReader

# =============================================================================
# Event classes for type hints and event handling
# =============================================================================
from keybard.events import (
    AppBlur,
    AppFocus,
    Event,
    Key,
    Paste,
    Resize,
)

# =============================================================================
# Geometry types for terminal size and regions
# =============================================================================
from keybard.geometry import (
    Offset,
    Region,
    Size,
    Spacing,
    clamp,
)

# =============================================================================
# Keys enum and key manipulation functions
# =============================================================================
from keybard.keys import (
    Keys,
    format_key,
    key_to_character,
)

# =============================================================================
# Color support
# =============================================================================
from keybard.color import (
    Color,
    ColorParseError,
    Gradient,
    HSL,
    HSV,
    Lab,
    lab_to_rgb,
    rgb_to_lab,
)

# =============================================================================
# Constants and configuration
# =============================================================================
from keybard.constants import (
    DIM_FACTOR,
    ESCAPE_DELAY,
    SMOOTH_SCROLL,
)

# =============================================================================
# High-level tools - Simple APIs for common tasks
# =============================================================================
from keybard import tools

__all__ = [
    # -------------------------------------------------------------------------
    # Main API
    # -------------------------------------------------------------------------
    "KeyboardReader",
    # -------------------------------------------------------------------------
    # Event types (keyboard-only, no mouse events)
    # -------------------------------------------------------------------------
    "Event",
    "Key",
    "Paste",
    "Resize",
    "AppFocus",
    "AppBlur",
    # -------------------------------------------------------------------------
    # Geometry types
    # -------------------------------------------------------------------------
    "Size",
    "Offset",
    "Region",
    "Spacing",
    "clamp",
    # -------------------------------------------------------------------------
    # Keys and key formatting
    # -------------------------------------------------------------------------
    "Keys",
    "format_key",
    "key_to_character",
    # -------------------------------------------------------------------------
    # Color support
    # -------------------------------------------------------------------------
    "Color",
    "ColorParseError",
    "Gradient",
    "HSL",
    "HSV",
    "Lab",
    "lab_to_rgb",
    "rgb_to_lab",
    # -------------------------------------------------------------------------
    # Constants
    # -------------------------------------------------------------------------
    "ESCAPE_DELAY",
    "SMOOTH_SCROLL",
    "DIM_FACTOR",
    # -------------------------------------------------------------------------
    # High-level tools (simple APIs)
    # -------------------------------------------------------------------------
    "tools",
]

__version__ = "0.2.0a1"
