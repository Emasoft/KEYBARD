#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-end tests for KeyboardReader capturing arrow keys.

This test suite verifies that the KeyboardReader class correctly captures
the 4 arrow keys (up, down, left, right) using the top-level API.
"""

import pytest

from keybard import KeyboardReader
from keybard.events import Key


# ANSI escape sequences for arrow keys
ARROW_KEY_SEQUENCES = {
    "up": "\x1b[A",
    "down": "\x1b[B",
    "right": "\x1b[C",
    "left": "\x1b[D",
}


class MockHeadlessDriver:
    """Mock driver that simulates arrow key input for testing."""

    def __init__(self, reader, *, debug=False, mouse=False, size=None):
        """Initialize mock driver.

        Args:
            reader: KeyboardReader instance
            debug: Debug mode flag
            mouse: Mouse support flag (KEYBARD is keyboard-only)
            size: Terminal size override
        """
        self._reader = reader
        self._size = size
        self._simulated_keys = []

    def start_application_mode(self):
        """Start application mode (no-op for mock)."""
        pass

    def stop_application_mode(self):
        """Stop application mode (no-op for mock)."""
        pass

    def close(self):
        """Close driver (no-op for mock)."""
        pass

    def simulate_key(self, key_name: str):
        """Simulate a key press by its name.

        Args:
            key_name: Name of key to simulate ('up', 'down', 'left', 'right')
        """
        if key_name not in ARROW_KEY_SEQUENCES:
            raise ValueError(f"Unknown key: {key_name}")

        # Get the escape sequence for this key
        sequence = ARROW_KEY_SEQUENCES[key_name]

        # Parse the sequence using the reader's parser
        from keybard._xterm_parser import XTermParser

        parser = XTermParser()
        events = list(parser.feed(sequence))

        # Send events to the reader
        for event in events:
            self._reader._handle_message(event)


@pytest.fixture
def reader_with_mock():
    """Create a KeyboardReader with a mock driver for testing."""
    reader = KeyboardReader(driver="headless")

    # Replace the headless driver with our mock
    mock_driver = MockHeadlessDriver(reader, debug=False, mouse=False, size=None)
    reader._driver = mock_driver

    yield reader, mock_driver

    # Cleanup
    reader.stop()


def test_capture_arrow_up(reader_with_mock):
    """Test capturing the UP arrow key."""
    reader, mock_driver = reader_with_mock

    with reader:
        # Simulate UP arrow key press
        mock_driver.simulate_key("up")

        # Read the event
        event = reader.read_key(timeout=0.1)

        # Verify
        assert event is not None
        assert isinstance(event, Key)
        assert event.key == "up"


def test_capture_arrow_down(reader_with_mock):
    """Test capturing the DOWN arrow key."""
    reader, mock_driver = reader_with_mock

    with reader:
        # Simulate DOWN arrow key press
        mock_driver.simulate_key("down")

        # Read the event
        event = reader.read_key(timeout=0.1)

        # Verify
        assert event is not None
        assert isinstance(event, Key)
        assert event.key == "down"


def test_capture_arrow_left(reader_with_mock):
    """Test capturing the LEFT arrow key."""
    reader, mock_driver = reader_with_mock

    with reader:
        # Simulate LEFT arrow key press
        mock_driver.simulate_key("left")

        # Read the event
        event = reader.read_key(timeout=0.1)

        # Verify
        assert event is not None
        assert isinstance(event, Key)
        assert event.key == "left"


def test_capture_arrow_right(reader_with_mock):
    """Test capturing the RIGHT arrow key."""
    reader, mock_driver = reader_with_mock

    with reader:
        # Simulate RIGHT arrow key press
        mock_driver.simulate_key("right")

        # Read the event
        event = reader.read_key(timeout=0.1)

        # Verify
        assert event is not None
        assert isinstance(event, Key)
        assert event.key == "right"


def test_capture_all_four_arrows_in_sequence(reader_with_mock):
    """Test capturing all 4 arrow keys in sequence (up, down, left, right)."""
    reader, mock_driver = reader_with_mock

    with reader:
        # Simulate all 4 arrow keys in sequence
        expected_keys = ["up", "down", "left", "right"]

        for key_name in expected_keys:
            mock_driver.simulate_key(key_name)

        # Read all events
        events = []
        for _ in range(4):
            event = reader.read_key(timeout=0.1)
            assert event is not None
            events.append(event)

        # Verify all keys were captured in correct order
        assert len(events) == 4
        assert all(isinstance(event, Key) for event in events)
        assert [event.key for event in events] == expected_keys


def test_poll_multiple_arrow_keys(reader_with_mock):
    """Test using poll() to get multiple arrow key events."""
    reader, mock_driver = reader_with_mock

    with reader:
        # Simulate multiple arrow keys
        mock_driver.simulate_key("up")
        mock_driver.simulate_key("right")
        mock_driver.simulate_key("down")
        mock_driver.simulate_key("left")

        # Poll for all events (non-blocking)
        events = reader.poll()

        # Verify
        assert len(events) == 4
        assert all(isinstance(event, Key) for event in events)
        assert [event.key for event in events] == ["up", "right", "down", "left"]


def test_callback_receives_arrow_keys(reader_with_mock):
    """Test that callback function receives arrow key events."""
    captured_events = []

    def on_event(event):
        """Callback to capture events."""
        captured_events.append(event)

    # Create reader with callback
    reader = KeyboardReader(driver="headless", callback=on_event)
    mock_driver = MockHeadlessDriver(reader, debug=False, mouse=False, size=None)
    reader._driver = mock_driver

    with reader:
        # Simulate arrow keys
        mock_driver.simulate_key("up")
        mock_driver.simulate_key("down")

        # Events should be captured in callback
        assert len(captured_events) == 2
        assert captured_events[0].key == "up"
        assert captured_events[1].key == "down"


def test_arrow_keys_with_modifiers():
    """Test arrow keys with modifier keys (ctrl, shift, etc.)."""
    reader = KeyboardReader(driver="headless")

    # Test sequences for arrow keys with modifiers
    test_cases = [
        ("\x1b[1;2A", "shift+up"),  # Shift+Up
        ("\x1b[1;2B", "shift+down"),  # Shift+Down
        ("\x1b[1;2C", "shift+right"),  # Shift+Right
        ("\x1b[1;2D", "shift+left"),  # Shift+Left
        ("\x1b[1;5A", "ctrl+up"),  # Ctrl+Up
        ("\x1b[1;5B", "ctrl+down"),  # Ctrl+Down
        ("\x1b[1;5C", "ctrl+right"),  # Ctrl+Right
        ("\x1b[1;5D", "ctrl+left"),  # Ctrl+Left
    ]

    from keybard._xterm_parser import XTermParser

    with reader:
        for sequence, expected_key in test_cases:
            parser = XTermParser()
            events = list(parser.feed(sequence))

            assert len(events) == 1
            assert isinstance(events[0], Key)
            assert events[0].key == expected_key


def test_no_event_returns_none():
    """Test that read_key returns None when no event is available (timeout)."""
    reader = KeyboardReader(driver="headless")

    with reader:
        # Clear initial resize event from HeadlessDriver
        reader.poll()

        # No keys simulated, should timeout
        event = reader.read_key(timeout=0.1)
        assert event is None


def test_empty_poll_returns_empty_list():
    """Test that poll() returns empty list when no events are available."""
    reader = KeyboardReader(driver="headless")

    with reader:
        # Clear initial resize event from HeadlessDriver
        reader.poll()

        # No keys simulated after clearing
        events = reader.poll()
        assert events == []
