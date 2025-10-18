#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for terminal capability messages.

Tests TerminalSupportsSynchronizedOutput and InBandWindowResize messages.
"""

from keybard.messages import InBandWindowResize, TerminalSupportsSynchronizedOutput


class TestTerminalSupportsSynchronizedOutput:
    """Tests for TerminalSupportsSynchronizedOutput message."""

    def test_creation(self):
        """Test creating TerminalSupportsSynchronizedOutput message."""
        msg = TerminalSupportsSynchronizedOutput()
        assert isinstance(msg, TerminalSupportsSynchronizedOutput)


class TestInBandWindowResize:
    """Tests for InBandWindowResize message."""

    def test_creation(self):
        """Test creating InBandWindowResize message."""
        msg = InBandWindowResize(supported=True, enabled=True)
        assert msg.supported is True
        assert msg.enabled is True

    def test_creation_not_supported(self):
        """Test creating InBandWindowResize with not supported."""
        msg = InBandWindowResize(supported=False, enabled=False)
        assert msg.supported is False
        assert msg.enabled is False

    def test_from_setting_parameter_not_recognized(self):
        """Test from_setting_parameter with value 1 (not recognized)."""
        msg = InBandWindowResize.from_setting_parameter(1)
        assert msg.supported is False
        assert msg.enabled is False

    def test_from_setting_parameter_set(self):
        """Test from_setting_parameter with value 2 (set)."""
        msg = InBandWindowResize.from_setting_parameter(2)
        assert msg.supported is True
        assert msg.enabled is True

    def test_from_setting_parameter_reset(self):
        """Test from_setting_parameter with value 3 (reset)."""
        msg = InBandWindowResize.from_setting_parameter(3)
        assert msg.supported is True
        assert msg.enabled is False

    def test_from_setting_parameter_permanently_set(self):
        """Test from_setting_parameter with value 4 (permanently set)."""
        msg = InBandWindowResize.from_setting_parameter(4)
        assert msg.supported is True
        assert msg.enabled is False
