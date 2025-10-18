#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event classes for keyboard input.

This module defines all the event types that the XTermParser can generate.
KEYBARD is keyboard-only - no mouse support.
"""

from __future__ import annotations

from dataclasses import dataclass

from keybard.geometry import Size
from keybard.message import Message


@dataclass
class Event(Message):
    """Base class for all events."""

    def __post_init__(self) -> None:
        """Initialize the Message base class after dataclass init."""
        super().__init__()


@dataclass
class Key(Event):
    """
    Keyboard key press event.

    Attributes:
        key: Normalized key name (e.g., "ctrl+c", "a", "escape", "shift+up")
        character: Original character if this was a single printable character
    """

    key: str
    character: str | None = None


@dataclass
class Paste(Event):
    """
    Bracketed paste event.

    Indicates text was pasted into the terminal (as opposed to typed).

    Attributes:
        text: The pasted text content
    """

    text: str


@dataclass
class Resize(Event):
    """
    Terminal was resized.

    Attributes:
        size: New terminal size in cells (width, height)
        pixel_size: New terminal size in pixels (width, height), if available
    """

    size: Size
    pixel_size: tuple[int, int] | None = None

    @classmethod
    def from_dimensions(cls, size: tuple[int, int], pixel_size: tuple[int, int]) -> Resize:
        """
        Create a Resize event from dimension tuples.

        Args:
            size: Terminal size in cells (width, height)
            pixel_size: Terminal size in pixels (width, height)

        Returns:
            New Resize event
        """
        return cls(Size(*size), pixel_size)


@dataclass
class AppFocus(Event):
    """Terminal window gained focus."""

    pass


@dataclass
class AppBlur(Event):
    """Terminal window lost focus."""

    pass


@dataclass
class CursorPosition(Event):
    """
    Cursor position report from terminal.

    Internal event used by drivers, not exposed in public API.
    """

    x: int
    y: int


# =============================================================================
# Timing-based keyboard events
# =============================================================================


@dataclass
class KeyClick(Event):
    """
    Key was pressed and released within the configured delta threshold.

    This indicates a quick press-and-release action (default: < 1 second).

    Attributes:
        key: Normalized key name (e.g., "ctrl+c", "a", "escape")
        character: Original character if single printable character
        duration: Time in seconds between press and release
    """

    key: str
    character: str | None = None
    duration: float = 0.0


@dataclass
class KeyDown(Event):
    """
    Key has been held down for longer than the delta threshold.

    This event is emitted AFTER the delta time has passed while the key
    is still being held. It indicates the user is holding the key.

    When emit_repeats is enabled in DispatcherConfig, this event is also
    emitted on each key repeat during the hold.

    Attributes:
        key: Normalized key name
        character: Original character if single printable character
        hold_time: Time in seconds the key has been held when event was emitted
        repeat_count: Number of repeats received (0 for initial KeyDown, >0 for repeats)
    """

    key: str
    character: str | None = None
    hold_time: float = 0.0
    repeat_count: int = 0


@dataclass
class KeyUp(Event):
    """
    Key was released after a KeyDown event.

    This is only emitted for keys that were held long enough to trigger
    a KeyDown event. Quick press-release cycles emit KeyClick instead.

    Attributes:
        key: Normalized key name
        character: Original character if single printable character
        total_duration: Total time in seconds the key was held
    """

    key: str
    character: str | None = None
    total_duration: float = 0.0


@dataclass
class ComboClick(Event):
    """
    Multiple keys were pressed together and all released within delta.

    **FUTURE FEATURE - NOT YET IMPLEMENTED**

    This event type is defined for future implementation. Currently, the
    dispatcher does not detect simultaneous key presses as combos. Modifier
    combinations like Ctrl+C come from the terminal parser as atomic Key
    events (key="ctrl+c") and are handled as single keys.

    Represents a quick multi-key press (e.g., Ctrl+Shift+C pressed and
    released quickly).

    Attributes:
        keys: List of key names in the combo, sorted
        primary_key: The last key pressed (usually the non-modifier)
        character: Original character if applicable
        duration: Time in seconds from first press to last release
    """

    keys: list[str]
    primary_key: str
    character: str | None = None
    duration: float = 0.0


@dataclass
class ComboKeyDown(Event):
    """
    Multiple keys pressed together, held past the delta threshold.

    **FUTURE FEATURE - NOT YET IMPLEMENTED**

    This event type is defined for future implementation. Currently, the
    dispatcher does not detect simultaneous key presses as combos. Modifier
    combinations like Ctrl+Shift+Arrow come from the terminal parser as
    atomic Key events and are handled as single keys.

    Represents holding a key combination (e.g., holding Ctrl+Shift+Arrow).

    Attributes:
        keys: List of key names in the combo, sorted
        primary_key: The last key pressed (usually the non-modifier)
        character: Original character if applicable
        hold_time: Time in seconds since first key press
    """

    keys: list[str]
    primary_key: str
    character: str | None = None
    hold_time: float = 0.0
