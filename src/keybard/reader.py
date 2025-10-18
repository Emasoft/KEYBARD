#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main API for the KEYBARD library.

This module provides the KeyboardReader class, which is the primary interface
for reading keyboard and mouse input from the terminal.

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

import queue
import sys
from threading import Event as ThreadEvent
from typing import Callable, Literal

from keybard.dispatcher import DispatcherConfig, KeyEventDispatcher
from keybard.driver import Driver
from keybard.events import Event
from keybard.geometry import Size
from keybard.message import Message


class KeyboardReader:
    """
    Cross-platform keyboard input reader.

    This is the main entry point for the keybard library. It provides a simple
    interface for reading keyboard events from the terminal.

    The reader automatically detects the appropriate driver for your platform
    (Linux/macOS or Windows) and handles all the low-level terminal setup.

    KEYBARD is keyboard-only - no mouse support.

    Args:
        debug: Enable debug logging (set KEYBARD_DEBUG env var)
        driver: Force specific driver ("linux", "windows", "headless", "web").
                If None, auto-detects based on platform.
        size: Override terminal size detection (width, height)
        callback: Optional callback function called for each event
        use_dispatcher: Enable timing-based event model (KeyClick/KeyDown/KeyUp)
        dispatcher_config: Configuration for timing thresholds (requires use_dispatcher=True)

    Example:
        Simple blocking read:
        ```python
        with KeyboardReader() as reader:
            while True:
                event = reader.read_key()
                if event.key == "ctrl+c":
                    break
                print(f"Pressed: {event.key}")
        ```

        Non-blocking poll:
        ```python
        with KeyboardReader() as reader:
            while running:
                for event in reader.poll():
                    handle_event(event)
                # Do other work...
                time.sleep(0.01)
        ```

        Callback-based:
        ```python
        def on_event(event):
            print(f"Event: {event}")

        with KeyboardReader(callback=on_event) as reader:
            reader.run()  # Blocks, calling callback for each event
        ```
    """

    def __init__(
        self,
        *,
        debug: bool = False,
        driver: Literal["linux", "windows", "headless", "web"] | None = None,
        size: tuple[int, int] | None = None,
        callback: Callable[[Event], None] | None = None,
        use_dispatcher: bool = False,
        dispatcher_config: DispatcherConfig | None = None,
    ):
        """Initialize the keyboard reader."""
        self.debug = debug
        self._use_dispatcher = use_dispatcher
        self._callback = callback
        self._queue: queue.Queue[Event] = queue.Queue()
        self._running = ThreadEvent()

        # Setup dispatcher if enabled
        self._dispatcher: KeyEventDispatcher | None
        if self._use_dispatcher:
            # Create dispatcher that feeds into our queue/callback
            self._dispatcher = KeyEventDispatcher(callback=self._dispatch_event, config=dispatcher_config)
        else:
            self._dispatcher = None

        self._driver = self._create_driver(driver, size)

    def _create_driver(
        self,
        driver_name: Literal["linux", "windows", "headless", "web"] | None,
        size: tuple[int, int] | None,
    ) -> Driver:
        """
        Create the appropriate driver for the platform.

        Args:
            driver_name: Name of driver to create, or None for auto-detect
            size: Optional terminal size override

        Returns:
            Driver instance

        Raises:
            ValueError: If driver_name is invalid
        """
        if driver_name is None:
            # Auto-detect platform
            if sys.platform == "win32":
                driver_name = "windows"
            else:
                driver_name = "linux"

        if driver_name == "linux":
            from keybard.drivers.linux_driver import LinuxDriver

            return LinuxDriver(self, debug=self.debug, mouse=False, size=size)
        elif driver_name == "windows":
            from keybard.drivers.windows_driver import WindowsDriver

            return WindowsDriver(self, debug=self.debug, mouse=False, size=size)
        elif driver_name == "headless":
            from keybard.drivers.headless_driver import HeadlessDriver

            return HeadlessDriver(self, debug=self.debug, mouse=False, size=size)
        elif driver_name == "web":
            from keybard.drivers.web_driver import WebDriver

            return WebDriver(self, debug=self.debug, mouse=False, size=size)
        else:
            raise ValueError(f"Unknown driver: {driver_name}")

    def _dispatch_event(self, event: Event) -> None:
        """
        Internal: dispatch event to queue and callback.

        This is called by the dispatcher (if enabled) or directly by _handle_message.

        Args:
            event: Event to dispatch (timed or raw)
        """
        self._queue.put(event)
        if self._callback:
            self._callback(event)

    def _handle_message(self, message: Message) -> None:
        """
        Internal: handle message from driver (sync mode).

        Args:
            message: Message from parser (Event or terminal message)
        """
        # KEYBARD is keyboard-only - no mouse events exist to filter
        if isinstance(message, Event):
            if self._dispatcher:
                # Route through dispatcher for timing-based events
                self._dispatcher.feed(message)
            else:
                # Direct dispatch (original behavior)
                self._dispatch_event(message)

    async def _post_message(self, message: Message) -> None:
        """
        Internal: post message from driver (async mode).

        This method is called when the driver is running in an async context.

        Args:
            message: Message from parser (Event or terminal message)
        """
        # KEYBARD is keyboard-only - no mouse events exist to filter
        # In async mode, still use the queue but called from async context
        if isinstance(message, Event):
            if self._dispatcher:
                # Route through dispatcher for timing-based events
                self._dispatcher.feed(message)
            else:
                # Direct dispatch (original behavior)
                self._dispatch_event(message)

    def __enter__(self) -> KeyboardReader:
        """
        Context manager entry - start reading.

        Returns:
            self for use in with statement
        """
        self.start()
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit - stop reading and cleanup."""
        self.stop()

    def start(self) -> None:
        """Start reading keyboard/mouse input from the terminal."""
        self._running.set()
        self._driver.start_application_mode()

    def stop(self) -> None:
        """Stop reading and restore terminal to normal mode."""
        self._running.clear()
        if self._dispatcher:
            self._dispatcher.stop()
        self._driver.stop_application_mode()
        self._driver.close()

    def read_key(self, timeout: float | None = None) -> Event | None:
        """
        Read the next keyboard/mouse event (blocking).

        This method blocks until an event is available or the timeout expires.

        Args:
            timeout: Maximum seconds to wait. None means wait forever.

        Returns:
            Event object or None if timeout occurred

        Example:
            ```python
            # Wait up to 1 second for a key
            event = reader.read_key(timeout=1.0)
            if event:
                print(f"Got: {event.key}")
            else:
                print("Timeout - no key pressed")
            ```
        """
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def poll(self) -> list[Event]:
        """
        Get all pending events without blocking.

        Returns all events currently in the queue and returns immediately.
        Returns an empty list if no events are pending.

        Returns:
            List of Event objects (may be empty)

        Example:
            ```python
            while running:
                events = reader.poll()
                for event in events:
                    handle_event(event)
                time.sleep(0.01)  # Do other work
            ```
        """
        events = []
        while not self._queue.empty():
            try:
                events.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return events

    def run(self) -> None:
        """
        Run the event loop (blocks until stop() is called).

        This method requires a callback to be set in __init__.
        It's useful for callback-based architecture where you want
        all event handling to happen in the callback.

        Raises:
            ValueError: If no callback was provided in __init__

        Example:
            ```python
            def on_event(event):
                print(f"Event: {event}")
                if event.key == "q":
                    reader.stop()

            reader = KeyboardReader(callback=on_event)
            with reader:
                reader.run()  # Blocks here, callback handles events
            ```
        """
        if not self._callback:
            raise ValueError("run() requires callback parameter in __init__")

        while self._running.is_set():
            # Just sleep - callback already called in _handle_message
            # Read events to keep the queue empty, but callback is already invoked by _handle_message
            self.read_key(timeout=0.1)

    @property
    def terminal_size(self) -> Size | None:
        """
        Get the current terminal size if known.

        Returns:
            Size object with width and height in cells, or None if unknown
        """
        return self._driver._size
