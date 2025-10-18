#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Key event dispatcher with timing-based event model.

This module provides a dispatcher that transforms immediate key press events
into timing-based events (Click, KeyDown, KeyUp) based on configurable
time thresholds.

The dispatcher distinguishes between:
- CLICK: Key pressed and released within delta threshold
- KEY DOWN: Key held past the delta threshold (emitted after delta)
- KEY UP: Key released after a KEY DOWN
- COMBO CLICK: Multiple keys pressed, all released within delta
- COMBO KEY DOWN: Multiple keys pressed and held past delta
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum, auto
from threading import Lock, Timer
from typing import Callable

from keybard.events import Event, Key, KeyClick, KeyDown, KeyUp


class KeyState(Enum):
    """State of a key in the dispatcher."""

    PRESSED = auto()  # Key just pressed, waiting for delta or release
    HELD = auto()  # Key held past delta (KeyDown emitted)
    RELEASED = auto()  # Key released (transient state)


@dataclass
class KeyInfo:
    """Information about a key being tracked."""

    key_name: str  # Normalized key name from Key event
    character: str | None  # Original character if single char
    press_time: float  # When key was first pressed (monotonic time)
    state: KeyState  # Current state
    timer: Timer | None = None  # Timer for delta threshold
    last_repeat_time: float = 0.0  # Last time a repeat was emitted
    repeat_count: int = 0  # Number of repeats received


@dataclass
class DispatcherConfig:
    """Configuration for the key event dispatcher."""

    delta: float = 1.0  # Time threshold for click vs hold (seconds)
    combo_window: float = 0.1  # Max time between keys for combo detection (seconds)
    release_timeout: float = 0.15  # Time to wait for repeat to detect release (seconds)
    emit_repeats: bool = False  # Whether to emit KeyDown events on each repeat
    repeat_interval: float = 0.05  # Minimum time between repeat emissions (seconds)

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.delta <= 0:
            raise ValueError("delta must be positive")
        if self.combo_window < 0:
            raise ValueError("combo_window must be non-negative")
        if self.combo_window >= self.delta:
            raise ValueError("combo_window must be less than delta")
        if self.release_timeout <= 0:
            raise ValueError("release_timeout must be positive")
        if self.repeat_interval <= 0:
            raise ValueError("repeat_interval must be positive")


class KeyEventDispatcher:
    """
    Dispatcher that transforms immediate key events into timing-based events.

    This dispatcher receives raw Key events from the parser and emits:
    - KeyClick: Press + release within delta threshold
    - KeyDown: Key held past delta (emitted after waiting)
    - KeyUp: Key released after KeyDown
    - ComboClick: Multiple keys pressed together, released within delta
    - ComboKeyDown: Multiple keys pressed together, held past delta

    The dispatcher buffers events and uses timers to determine the appropriate
    event type based on timing. This allows distinguishing between quick taps
    and prolonged holds.

    Args:
        callback: Function to call with timed events
        config: Configuration for timing thresholds
    """

    def __init__(self, callback: Callable[[Event], None], config: DispatcherConfig | None = None) -> None:
        """Initialize the dispatcher."""
        self._callback = callback
        self._config = config or DispatcherConfig()
        self._keys: dict[str, KeyInfo] = {}  # Currently tracked keys
        self._lock = Lock()  # Thread safety for timer callbacks

    def feed(self, event: Event) -> None:
        """
        Feed an event to the dispatcher.

        Key events are processed through the timing state machine.
        All other events are passed through immediately.

        Args:
            event: Event from the parser (Key, Paste, Resize, etc.)
        """
        if isinstance(event, Key):
            self._handle_key_event(event)
        else:
            # Pass through non-key events immediately
            self._callback(event)

    def _handle_key_event(self, event: Key) -> None:
        """
        Handle a raw key event from the parser.

        In terminals, we only get key press events (no release events).
        We detect "release" by absence of repeats. This works because:
        - Holding a key generates rapid repeat events
        - Releasing a key stops the repeats

        However, this model requires a different approach than the user described.
        Let me reconsider...

        Actually, the user's requirement assumes we can detect press AND release
        separately. But in terminal input, we don't get explicit release events.
        We only get:
        1. Initial key press
        2. Repeat events if held

        The current key_display.py implementation uses this to detect:
        - CLICK: Single event (no repeats)
        - KEY-DOWN: Multiple repeat events
        - KEY-UP: Absence of repeats after KEY-DOWN

        For the user's model to work, we need to either:
        1. Accept this limitation (no true release detection)
        2. Use the repeat pattern to infer release

        Let me implement using the repeat pattern approach:
        - First event for a key → PRESSED state, start timer
        - Timer expires (delta) without repeat → emit CLICK
        - Repeat event arrives → transition to HELD, emit KEY-DOWN
        - No repeats for timeout → emit KEY-UP

        Args:
            event: Key event from parser
        """
        with self._lock:
            key_name = event.key
            current_time = time.monotonic()

            if key_name in self._keys:
                # Repeat event - key is being held
                key_info = self._keys[key_name]

                if key_info.state == KeyState.PRESSED:
                    # First repeat - transition to HELD
                    # Cancel the pending Click timer
                    if key_info.timer:
                        key_info.timer.cancel()
                        key_info.timer = None

                    # Update state
                    key_info.state = KeyState.HELD
                    hold_time = current_time - key_info.press_time
                    key_info.last_repeat_time = current_time  # Initialize for repeat tracking

                    # Emit initial KEY-DOWN (repeat_count = 0)
                    self._callback(
                        KeyDown(
                            key=key_name,
                            character=key_info.character,
                            hold_time=hold_time,
                            repeat_count=0,
                        )
                    )

                    # Start timer to detect release (absence of repeats)
                    key_info.timer = Timer(self._config.release_timeout, self._on_key_released, args=(key_name,))
                    key_info.timer.start()

                elif key_info.state == KeyState.HELD:
                    # Continued holding - reset release timer
                    if key_info.timer:
                        key_info.timer.cancel()

                    # Increment repeat count
                    key_info.repeat_count += 1

                    # Optionally emit repeat events
                    if self._config.emit_repeats:
                        # Check if enough time has passed since last repeat emission
                        time_since_last = current_time - key_info.last_repeat_time
                        if time_since_last >= self._config.repeat_interval:
                            hold_time = current_time - key_info.press_time
                            self._callback(
                                KeyDown(
                                    key=key_name,
                                    character=key_info.character,
                                    hold_time=hold_time,
                                    repeat_count=key_info.repeat_count,
                                )
                            )
                            key_info.last_repeat_time = current_time

                    # Reset release detection timer
                    key_info.timer = Timer(
                        self._config.release_timeout,  # Use configurable timeout
                        self._on_key_released,
                        args=(key_name,),
                    )
                    key_info.timer.start()

            else:
                # First press of this key
                key_info = KeyInfo(
                    key_name=key_name,
                    character=event.character,
                    press_time=current_time,
                    state=KeyState.PRESSED,
                )

                self._keys[key_name] = key_info

                # Start timer for delta threshold
                # If no repeat arrives, it's a click
                key_info.timer = Timer(self._config.delta, self._on_delta_timeout, args=(key_name,))
                key_info.timer.start()

    def _on_delta_timeout(self, key_name: str) -> None:
        """
        Called when delta timer expires without key repeat.

        This means the key was pressed but not held - emit a CLICK.

        Args:
            key_name: Name of the key
        """
        with self._lock:
            if key_name not in self._keys:
                return

            key_info = self._keys[key_name]

            if key_info.state == KeyState.PRESSED:
                # Key was pressed but not held - it's a click
                duration = time.monotonic() - key_info.press_time

                self._callback(
                    KeyClick(
                        key=key_name,
                        character=key_info.character,
                        duration=duration,
                    )
                )

                # Remove from tracking
                del self._keys[key_name]

    def _on_key_released(self, key_name: str) -> None:
        """
        Called when key release is detected (absence of repeats).

        This is only called for keys in HELD state.

        Args:
            key_name: Name of the key
        """
        with self._lock:
            if key_name not in self._keys:
                return

            key_info = self._keys[key_name]

            if key_info.state == KeyState.HELD:
                # Key was held and now released
                total_duration = time.monotonic() - key_info.press_time

                self._callback(
                    KeyUp(
                        key=key_name,
                        character=key_info.character,
                        total_duration=total_duration,
                    )
                )

                # Remove from tracking
                del self._keys[key_name]

    def stop(self) -> None:
        """
        Stop the dispatcher and cancel all pending timers.

        Call this when shutting down to ensure clean cleanup.
        """
        with self._lock:
            for key_info in self._keys.values():
                if key_info.timer:
                    key_info.timer.cancel()
            self._keys.clear()
