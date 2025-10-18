#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for event classes.

This module tests all event types used in KEYBARD keyboard input handling.
"""

from keybard.events import AppBlur, AppFocus, CursorPosition, Event, Key, Paste, Resize
from keybard.geometry import Size


class TestEvent:
    """Tests for Event base class."""

    def test_event_is_message(self):
        """Test that Event is a Message subclass."""
        event = Event()
        assert hasattr(event, "__post_init__")


class TestKey:
    """Tests for Key event."""

    def test_key_creation(self):
        """Test creating Key event."""
        key = Key(key="a", character="a")
        assert key.key == "a"
        assert key.character == "a"

    def test_key_with_modifier(self):
        """Test creating Key event with modifier."""
        key = Key(key="ctrl+c", character=None)
        assert key.key == "ctrl+c"
        assert key.character is None

    def test_key_special(self):
        """Test creating Key event for special key."""
        key = Key(key="escape", character="\x1b")
        assert key.key == "escape"
        assert key.character == "\x1b"


class TestPaste:
    """Tests for Paste event."""

    def test_paste_creation(self):
        """Test creating Paste event."""
        paste = Paste(text="hello world")
        assert paste.text == "hello world"

    def test_paste_empty_text(self):
        """Test creating Paste event with empty text."""
        paste = Paste(text="")
        assert paste.text == ""

    def test_paste_multiline(self):
        """Test creating Paste event with multiline text."""
        paste = Paste(text="line1\nline2\nline3")
        assert paste.text == "line1\nline2\nline3"


class TestResize:
    """Tests for Resize event."""

    def test_resize_creation(self):
        """Test creating Resize event."""
        size = Size(80, 24)
        resize = Resize(size=size, pixel_size=(1280, 768))
        assert resize.size == size
        assert resize.pixel_size == (1280, 768)

    def test_resize_without_pixel_size(self):
        """Test creating Resize event without pixel size."""
        size = Size(80, 24)
        resize = Resize(size=size)
        assert resize.size == size
        assert resize.pixel_size is None

    def test_resize_from_dimensions(self):
        """Test creating Resize event from dimension tuples."""
        resize = Resize.from_dimensions((80, 24), (1280, 768))
        assert resize.size == Size(80, 24)
        assert resize.pixel_size == (1280, 768)

    def test_resize_from_dimensions_size_tuple(self):
        """Test from_dimensions creates correct Size object."""
        resize = Resize.from_dimensions((100, 50), (1600, 900))
        assert resize.size.width == 100
        assert resize.size.height == 50
        assert resize.pixel_size == (1600, 900)


class TestAppFocus:
    """Tests for AppFocus event."""

    def test_app_focus_creation(self):
        """Test creating AppFocus event."""
        focus = AppFocus()
        assert isinstance(focus, Event)


class TestAppBlur:
    """Tests for AppBlur event."""

    def test_app_blur_creation(self):
        """Test creating AppBlur event."""
        blur = AppBlur()
        assert isinstance(blur, Event)


class TestCursorPosition:
    """Tests for CursorPosition event."""

    def test_cursor_position_creation(self):
        """Test creating CursorPosition event."""
        pos = CursorPosition(x=10, y=20)
        assert pos.x == 10
        assert pos.y == 20

    def test_cursor_position_zero(self):
        """Test creating CursorPosition at origin."""
        pos = CursorPosition(x=0, y=0)
        assert pos.x == 0
        assert pos.y == 0
