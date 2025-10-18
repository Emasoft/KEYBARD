#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for HeadlessDriver.

Tests the headless (do-nothing) driver used for testing.
"""

from unittest.mock import Mock, patch

from keybard.drivers.headless_driver import HeadlessDriver
from keybard.events import Resize


class TestHeadlessDriverBasics:
    """Tests for HeadlessDriver basic functionality."""

    def test_headless_driver_creation(self):
        """Test HeadlessDriver initialization."""
        reader = Mock()
        driver = HeadlessDriver(reader)

        assert driver._reader is reader

    def test_headless_driver_is_headless_property(self):
        """Test is_headless property returns True."""
        reader = Mock()
        driver = HeadlessDriver(reader)

        assert driver.is_headless is True

    def test_write_does_nothing(self):
        """Test write method does nothing."""
        reader = Mock()
        driver = HeadlessDriver(reader)

        # Should not raise any errors
        driver.write("test data")

    def test_disable_input_does_nothing(self):
        """Test disable_input method does nothing."""
        reader = Mock()
        driver = HeadlessDriver(reader)

        # Should not raise any errors
        driver.disable_input()

    def test_stop_application_mode_does_nothing(self):
        """Test stop_application_mode does nothing."""
        reader = Mock()
        driver = HeadlessDriver(reader)

        # Should not raise any errors
        driver.stop_application_mode()


class TestHeadlessDriverTerminalSize:
    """Tests for HeadlessDriver terminal size handling."""

    def test_get_terminal_size_default(self):
        """Test _get_terminal_size with default values."""
        reader = Mock()
        driver = HeadlessDriver(reader)

        width, height = driver._get_terminal_size()

        # Should return some valid size
        assert isinstance(width, int)
        assert isinstance(height, int)
        assert width > 0
        assert height > 0

    def test_get_terminal_size_with_custom_size(self):
        """Test _get_terminal_size with custom size."""
        reader = Mock()
        driver = HeadlessDriver(reader, size=(100, 50))

        width, height = driver._get_terminal_size()

        assert width == 100
        assert height == 50

    @patch("shutil.get_terminal_size")
    def test_get_terminal_size_exception_fallback(self, mock_get_size):
        """Test _get_terminal_size fallback when shutil raises exception."""
        # Make both calls raise an exception
        mock_get_size.side_effect = OSError("Terminal size unavailable")

        reader = Mock()
        driver = HeadlessDriver(reader)

        width, height = driver._get_terminal_size()

        # Should fallback to default 80x25
        assert width == 80
        assert height == 25


class TestHeadlessDriverApplicationMode:
    """Tests for HeadlessDriver application mode."""

    def test_start_application_mode_sends_resize_event(self):
        """Test start_application_mode sends initial Resize event."""
        reader = Mock()
        reader._handle_message = Mock()
        driver = HeadlessDriver(reader, size=(80, 24))

        driver.start_application_mode()

        # Should have called _handle_message with Resize event
        reader._handle_message.assert_called_once()
        event = reader._handle_message.call_args[0][0]

        assert isinstance(event, Resize)
        assert event.size.width == 80
        assert event.size.height == 24
