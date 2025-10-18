#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Driver base class.

Tests the abstract driver infrastructure including message processing,
lifecycle methods, and platform-specific driver inheritance.
"""

import asyncio
from typing import Any
from unittest.mock import Mock

import pytest

from keybard.driver import Driver
from keybard.events import Key
from keybard.geometry import Size
from keybard.message import Message


class ConcreteDriver(Driver):
    """Concrete implementation of Driver for testing."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize concrete driver."""
        super().__init__(*args, **kwargs)
        self.started = False
        self.stopped = False
        self.write_buffer: list[str] = []
        self.flushed = False
        self.closed = False

    def start_application_mode(self) -> None:
        """Enter application mode."""
        self.started = True

    def stop_application_mode(self) -> None:
        """Exit application mode."""
        self.stopped = True

    def write(self, data: str) -> None:
        """Write data to buffer."""
        self.write_buffer.append(data)

    def flush(self) -> None:
        """Flush output buffer."""
        self.flushed = True

    def close(self) -> None:
        """Close driver."""
        self.closed = True


class TestDriverInitialization:
    """Tests for Driver initialization."""

    def test_driver_basic_initialization(self):
        """Test driver initialization with minimal parameters."""
        reader = Mock()
        driver = ConcreteDriver(reader)

        assert driver._reader is reader
        assert driver._debug is False
        assert driver._mouse is True
        assert driver._size is None
        assert driver._auto_restart is True

    def test_driver_initialization_with_debug(self):
        """Test driver initialization with debug enabled."""
        reader = Mock()
        driver = ConcreteDriver(reader, debug=True)

        assert driver._debug is True

    def test_driver_initialization_with_mouse_disabled(self):
        """Test driver initialization with mouse disabled."""
        reader = Mock()
        driver = ConcreteDriver(reader, mouse=False)

        assert driver._mouse is False

    def test_driver_initialization_with_size(self):
        """Test driver initialization with custom size."""
        reader = Mock()
        driver = ConcreteDriver(reader, size=(100, 50))

        assert isinstance(driver._size, Size)
        assert driver._size.width == 100
        assert driver._size.height == 50


class TestDriverMessageProcessing:
    """Tests for Driver message processing."""

    def test_process_message_sync_mode(self):
        """Test process_message in sync mode (no event loop)."""
        reader = Mock()
        reader._handle_message = Mock()

        driver = ConcreteDriver(reader)
        message = Key(key="a", character="a")

        driver.process_message(message)

        reader._handle_message.assert_called_once_with(message)

    def test_process_message_sync_mode_no_handler(self):
        """Test process_message when reader has no _handle_message."""
        reader = Mock(spec=[])  # Mock with no attributes

        driver = ConcreteDriver(reader)
        message = Key(key="a", character="a")

        # Should not raise an error
        driver.process_message(message)

    @pytest.mark.asyncio
    async def test_process_message_async_mode(self):
        """Test process_message in async mode (event loop running)."""
        reader = Mock()

        # Create a coroutine that can be awaited
        async def mock_post_message(msg: Message) -> None:
            """Mock async message posting."""
            reader._posted_messages.append(msg)

        reader._posted_messages: list[Message] = []
        reader._post_message = mock_post_message

        driver = ConcreteDriver(reader)
        message = Key(key="b", character="b")

        # Process message in async context
        driver.process_message(message)

        # Give the event loop time to process
        await asyncio.sleep(0.01)

        # Verify message was posted
        assert len(reader._posted_messages) == 1
        assert reader._posted_messages[0] is message

    @pytest.mark.asyncio
    async def test_process_message_async_mode_no_handler(self):
        """Test process_message in async mode when reader has no _post_message."""
        reader = Mock(spec=[])

        driver = ConcreteDriver(reader)
        message = Key(key="c", character="c")

        # Should not raise an error
        driver.process_message(message)
        await asyncio.sleep(0.01)


class TestDriverLifecycleMethods:
    """Tests for Driver lifecycle methods."""

    def test_start_application_mode(self):
        """Test start_application_mode is called."""
        reader = Mock()
        driver = ConcreteDriver(reader)

        driver.start_application_mode()

        assert driver.started is True

    def test_stop_application_mode(self):
        """Test stop_application_mode is called."""
        reader = Mock()
        driver = ConcreteDriver(reader)

        driver.stop_application_mode()

        assert driver.stopped is True

    def test_write(self):
        """Test write method."""
        reader = Mock()
        driver = ConcreteDriver(reader)

        driver.write("test data")

        assert driver.write_buffer == ["test data"]

    def test_flush(self):
        """Test flush method."""
        reader = Mock()
        driver = ConcreteDriver(reader)

        driver.flush()

        assert driver.flushed is True

    def test_close(self):
        """Test close method."""
        reader = Mock()
        driver = ConcreteDriver(reader)

        driver.close()

        assert driver.closed is True

    def test_suspend_application_mode(self):
        """Test suspend_application_mode calls stop_application_mode."""
        reader = Mock()
        driver = ConcreteDriver(reader)

        driver.suspend_application_mode()

        assert driver.stopped is True

    def test_resume_application_mode(self):
        """Test resume_application_mode calls start_application_mode."""
        reader = Mock()
        driver = ConcreteDriver(reader)

        driver.resume_application_mode()

        assert driver.started is True


class TestDriverSignalResume:
    """Tests for Driver.SignalResume message."""

    def test_signal_resume_creation(self):
        """Test SignalResume message creation."""
        signal = Driver.SignalResume()

        assert isinstance(signal, Message)
        assert isinstance(signal, Driver.SignalResume)
