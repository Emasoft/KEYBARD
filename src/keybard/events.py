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
