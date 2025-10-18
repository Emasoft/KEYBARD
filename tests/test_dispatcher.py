#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for KeyEventDispatcher timing-based event model.

These tests verify that the dispatcher correctly transforms raw Key events
into timing-based events (KeyClick, KeyDown, KeyUp) based on timing thresholds.
"""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import MagicMock

import pytest

from keybard.dispatcher import DispatcherConfig, KeyEventDispatcher
from keybard.events import Key, KeyClick, KeyDown, KeyUp, Paste, Resize
from keybard.geometry import Size


class TestDispatcherConfig:
    """Test DispatcherConfig validation."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = DispatcherConfig()
        assert config.delta == 1.0
        assert config.combo_window == 0.1
        assert config.release_timeout == 0.15
        assert config.emit_repeats is False
        assert config.repeat_interval == 0.05

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = DispatcherConfig(delta=0.5, combo_window=0.05, release_timeout=0.2, emit_repeats=True, repeat_interval=0.1)
        assert config.delta == 0.5
        assert config.combo_window == 0.05
        assert config.release_timeout == 0.2
        assert config.emit_repeats is True
        assert config.repeat_interval == 0.1

    def test_invalid_delta(self) -> None:
        """Test that negative delta raises ValueError."""
        with pytest.raises(ValueError, match="delta must be positive"):
            DispatcherConfig(delta=0.0)

        with pytest.raises(ValueError, match="delta must be positive"):
            DispatcherConfig(delta=-1.0)

    def test_invalid_combo_window(self) -> None:
        """Test that negative combo_window raises ValueError."""
        with pytest.raises(ValueError, match="combo_window must be non-negative"):
            DispatcherConfig(combo_window=-0.1)

    def test_combo_window_too_large(self) -> None:
        """Test that combo_window >= delta raises ValueError."""
        with pytest.raises(ValueError, match="combo_window must be less than delta"):
            DispatcherConfig(delta=1.0, combo_window=1.0)

        with pytest.raises(ValueError, match="combo_window must be less than delta"):
            DispatcherConfig(delta=1.0, combo_window=1.5)

    def test_invalid_release_timeout(self) -> None:
        """Test that invalid release_timeout raises ValueError."""
        with pytest.raises(ValueError, match="release_timeout must be positive"):
            DispatcherConfig(release_timeout=0.0)

        with pytest.raises(ValueError, match="release_timeout must be positive"):
            DispatcherConfig(release_timeout=-0.1)

    def test_invalid_repeat_interval(self) -> None:
        """Test that invalid repeat_interval raises ValueError."""
        with pytest.raises(ValueError, match="repeat_interval must be positive"):
            DispatcherConfig(repeat_interval=0.0)

        with pytest.raises(ValueError, match="repeat_interval must be positive"):
            DispatcherConfig(repeat_interval=-0.05)


class TestKeyEventDispatcher:
    """Test KeyEventDispatcher event transformation."""

    def test_passthrough_non_key_events(self) -> None:
        """Test that non-Key events are passed through immediately."""
        callback = MagicMock()
        dispatcher = KeyEventDispatcher(callback=callback)

        # Test Paste event
        paste = Paste(text="Hello")
        dispatcher.feed(paste)
        callback.assert_called_once_with(paste)

        # Test Resize event
        callback.reset_mock()
        resize = Resize(size=Size(80, 24))
        dispatcher.feed(resize)
        callback.assert_called_once_with(resize)

    def test_single_key_click(self) -> None:
        """Test that single key press without repeat generates KeyClick."""
        events: list[Any] = []
        config = DispatcherConfig(delta=0.1, combo_window=0.05)  # Short delta for faster testing
        dispatcher = KeyEventDispatcher(callback=lambda e: events.append(e), config=config)

        # Simulate single key press
        dispatcher.feed(Key(key="a", character="a"))

        # Wait for delta timeout
        time.sleep(0.15)

        # Should receive KeyClick after delta expires
        assert len(events) == 1
        assert isinstance(events[0], KeyClick)
        assert events[0].key == "a"
        assert events[0].character == "a"
        assert events[0].duration >= 0.1

        dispatcher.stop()

    def test_key_hold_generates_keydown_and_keyup(self) -> None:
        """Test that holding a key generates KeyDown followed by KeyUp."""
        events: list[Any] = []
        config = DispatcherConfig(delta=0.1, combo_window=0.05, release_timeout=0.1)
        dispatcher = KeyEventDispatcher(callback=lambda e: events.append(e), config=config)

        # Simulate first key press
        dispatcher.feed(Key(key="b", character="b"))
        time.sleep(0.05)

        # Simulate repeat (indicates key is held)
        dispatcher.feed(Key(key="b", character="b"))

        # Should receive KeyDown immediately after first repeat
        assert len(events) == 1
        assert isinstance(events[0], KeyDown)
        assert events[0].key == "b"
        assert events[0].character == "b"
        assert events[0].repeat_count == 0

        # Wait for release timeout
        time.sleep(0.15)

        # Should receive KeyUp after timeout
        assert len(events) == 2
        assert isinstance(events[1], KeyUp)
        assert events[1].key == "b"

        dispatcher.stop()

    def test_key_hold_with_multiple_repeats(self) -> None:
        """Test that multiple repeats during hold work correctly."""
        events: list[Any] = []
        config = DispatcherConfig(delta=0.1, combo_window=0.05, release_timeout=0.1, emit_repeats=False)
        dispatcher = KeyEventDispatcher(callback=lambda e: events.append(e), config=config)

        # First press
        dispatcher.feed(Key(key="c", character="c"))
        time.sleep(0.05)

        # Multiple repeats
        dispatcher.feed(Key(key="c", character="c"))
        time.sleep(0.05)
        dispatcher.feed(Key(key="c", character="c"))
        time.sleep(0.05)
        dispatcher.feed(Key(key="c", character="c"))

        # Should only get one KeyDown (first repeat)
        assert len(events) == 1
        assert isinstance(events[0], KeyDown)

        # Wait for release
        time.sleep(0.15)

        # Should get KeyUp
        assert len(events) == 2
        assert isinstance(events[1], KeyUp)

        dispatcher.stop()

    def test_emit_repeats_enabled(self) -> None:
        """Test that emit_repeats=True emits KeyDown on each repeat."""
        events: list[Any] = []
        config = DispatcherConfig(delta=0.1, combo_window=0.05, release_timeout=0.1, emit_repeats=True, repeat_interval=0.01)
        dispatcher = KeyEventDispatcher(callback=lambda e: events.append(e), config=config)

        # First press
        dispatcher.feed(Key(key="d", character="d"))
        time.sleep(0.05)

        # First repeat (triggers transition to HELD)
        dispatcher.feed(Key(key="d", character="d"))
        time.sleep(0.02)

        # Second repeat (should emit another KeyDown)
        dispatcher.feed(Key(key="d", character="d"))
        time.sleep(0.02)

        # Third repeat (should emit another KeyDown)
        dispatcher.feed(Key(key="d", character="d"))

        # Should get initial KeyDown plus additional repeats
        keydown_events = [e for e in events if isinstance(e, KeyDown)]
        assert len(keydown_events) >= 2  # Initial + at least one repeat
        assert keydown_events[0].repeat_count == 0
        assert keydown_events[1].repeat_count > 0

        dispatcher.stop()

    def test_modifier_keys(self) -> None:
        """Test that modifier key combinations work correctly."""
        events: list[Any] = []
        config = DispatcherConfig(delta=0.1, combo_window=0.05)
        dispatcher = KeyEventDispatcher(callback=lambda e: events.append(e), config=config)

        # Simulate Ctrl+C press without hold
        dispatcher.feed(Key(key="ctrl+c", character=None))
        time.sleep(0.15)

        # Should receive KeyClick
        assert len(events) == 1
        assert isinstance(events[0], KeyClick)
        assert events[0].key == "ctrl+c"

        dispatcher.stop()

    def test_special_keys(self) -> None:
        """Test that special keys (arrows, function keys) work correctly."""
        events: list[Any] = []
        config = DispatcherConfig(delta=0.1, combo_window=0.05, release_timeout=0.1)
        dispatcher = KeyEventDispatcher(callback=lambda e: events.append(e), config=config)

        # Simulate arrow key hold
        dispatcher.feed(Key(key="up", character=None))
        time.sleep(0.05)
        dispatcher.feed(Key(key="up", character=None))  # Repeat

        # Should get KeyDown
        assert len(events) == 1
        assert isinstance(events[0], KeyDown)
        assert events[0].key == "up"

        # Wait for release
        time.sleep(0.15)

        # Should get KeyUp
        assert len(events) == 2
        assert isinstance(events[1], KeyUp)

        dispatcher.stop()

    def test_concurrent_keys(self) -> None:
        """Test handling of multiple keys pressed in sequence."""
        events: list[Any] = []
        config = DispatcherConfig(delta=0.1, combo_window=0.05)
        dispatcher = KeyEventDispatcher(callback=lambda e: events.append(e), config=config)

        # Press two different keys quickly
        dispatcher.feed(Key(key="x", character="x"))
        time.sleep(0.05)
        dispatcher.feed(Key(key="y", character="y"))

        # Wait for delta timeouts
        time.sleep(0.15)

        # Should get two KeyClick events
        assert len(events) == 2
        assert all(isinstance(e, KeyClick) for e in events)
        assert events[0].key == "x"
        assert events[1].key == "y"

        dispatcher.stop()

    def test_stop_cancels_timers(self) -> None:
        """Test that stop() cancels all pending timers."""
        events: list[Any] = []
        config = DispatcherConfig(delta=0.5)  # Long delta
        dispatcher = KeyEventDispatcher(callback=lambda e: events.append(e), config=config)

        # Press key
        dispatcher.feed(Key(key="z", character="z"))

        # Stop immediately (before delta expires)
        dispatcher.stop()

        # Wait past delta
        time.sleep(0.6)

        # Should NOT receive any events (timer was cancelled)
        assert len(events) == 0

    def test_thread_safety(self) -> None:
        """Test that dispatcher is thread-safe (basic smoke test)."""
        events: list[Any] = []
        config = DispatcherConfig(delta=0.1, combo_window=0.05)
        dispatcher = KeyEventDispatcher(callback=lambda e: events.append(e), config=config)

        # Feed multiple events rapidly
        for i in range(10):
            dispatcher.feed(Key(key=f"key{i}", character=None))
            time.sleep(0.01)

        # Wait for all timers
        time.sleep(0.2)

        # Should have events (exact count depends on timing)
        assert len(events) > 0

        dispatcher.stop()
