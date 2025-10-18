#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Driver class for platform-specific terminal input handling.

This module provides the abstract base class that all platform-specific
drivers (Linux, Windows, Headless, Web) inherit from.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from keybard.geometry import Size
from keybard.message import Message

if TYPE_CHECKING:
    from keybard.reader import KeyboardReader


class Driver(ABC):
    """
    Base class for platform-specific keyboard/mouse input drivers.

    Drivers handle:
    - Entering/exiting raw terminal mode
    - Reading input from terminal
    - Parsing escape sequences
    - Forwarding events to the reader
    """

    def __init__(
        self,
        reader: KeyboardReader,
        *,
        debug: bool = False,
        mouse: bool = True,
        size: tuple[int, int] | None = None,
    ) -> None:
        """
        Initialize the driver.

        Args:
            reader: KeyboardReader instance that owns this driver
            debug: Enable debug logging
            mouse: Enable mouse support
            size: Override terminal size detection (width, height)
        """
        self._reader = reader
        self._debug = debug
        self._mouse = mouse
        self._size = Size(*size) if size else None
        self._auto_restart = True

    def process_message(self, message: Message) -> None:
        """
        Process a message from the parser.

        Forwards the message to the reader's callback.
        Works in both async and sync contexts.

        Args:
            message: Message to process (Event or terminal message)
        """
        # Try to get the running event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running - sync mode
            if hasattr(self._reader, "_handle_message"):
                self._reader._handle_message(message)
        else:
            # Event loop is running - async mode
            # Schedule the message to be posted to the async loop
            if hasattr(self._reader, "_post_message"):
                asyncio.run_coroutine_threadsafe(
                    self._reader._post_message(message),
                    loop=loop,
                )

    @abstractmethod
    def start_application_mode(self) -> None:
        """
        Enter raw terminal mode.

        Should configure the terminal for:
        - Raw input (no line buffering)
        - Mouse tracking (if enabled)
        - Bracketed paste mode
        - Focus events
        """
        pass

    @abstractmethod
    def stop_application_mode(self) -> None:
        """
        Exit raw terminal mode and restore original terminal state.

        Should:
        - Disable mouse tracking
        - Disable bracketed paste
        - Restore original termios settings
        """
        pass

    @abstractmethod
    def write(self, data: str) -> None:
        """
        Write data to the terminal.

        Args:
            data: String to write (usually escape sequences)
        """
        pass

    def flush(self) -> None:
        """Flush output buffer (if buffered)."""
        pass

    def close(self) -> None:
        """Cleanup resources (threads, file handles, etc.)."""
        pass

    def suspend_application_mode(self) -> None:
        """
        Suspend terminal mode (for Ctrl+Z).

        Default implementation calls stop_application_mode.
        """
        self.stop_application_mode()

    def resume_application_mode(self) -> None:
        """
        Resume terminal mode after suspend.

        Default implementation calls start_application_mode.
        """
        self.start_application_mode()

    class SignalResume(Message):
        """Signal that application resumed from suspend (SIGCONT)."""

        pass
