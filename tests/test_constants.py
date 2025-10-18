#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for constants module.

Tests environment variable parsing and configuration constants.
"""

from keybard.constants import (
    DIM_FACTOR,
    ESCAPE_DELAY,
    SMOOTH_SCROLL,
    _get_environ_bool,
    _get_environ_int,
    _get_environ_port,
)


def test_constants_exist():
    """Test that all constants are defined with expected types."""
    assert isinstance(ESCAPE_DELAY, float)
    assert isinstance(SMOOTH_SCROLL, bool)
    assert isinstance(DIM_FACTOR, float)


def test_environ_int(monkeypatch):
    """Check minimum is applied."""
    monkeypatch.setenv("FOO", "-1")
    assert _get_environ_int("FOO", 1, minimum=0) == 0
    monkeypatch.setenv("FOO", "0")
    assert _get_environ_int("FOO", 1, minimum=0) == 0
    monkeypatch.setenv("FOO", "1")
    assert _get_environ_int("FOO", 1, minimum=0) == 1


def test_environ_int_invalid_value(monkeypatch):
    """Test _get_environ_int returns default for invalid string values."""
    monkeypatch.setenv("FOO", "not_a_number")
    assert _get_environ_int("FOO", 42) == 42

    monkeypatch.setenv("FOO", "12.5")
    assert _get_environ_int("FOO", 100) == 100

    monkeypatch.setenv("FOO", "")
    assert _get_environ_int("FOO", 7) == 7


def test_environ_int_missing_variable():
    """Test _get_environ_int returns default when variable not set."""
    assert _get_environ_int("NONEXISTENT_VAR", 99) == 99


def test_environ_int_no_minimum():
    """Test _get_environ_int without minimum constraint."""
    import os

    os.environ["FOO"] = "-100"
    assert _get_environ_int("FOO", 0, minimum=None) == -100
    del os.environ["FOO"]


def test_environ_bool(monkeypatch):
    """Anything other than "1" is False."""
    monkeypatch.setenv("BOOL", "1")
    assert _get_environ_bool("BOOL") is True
    monkeypatch.setenv("BOOL", "")
    assert _get_environ_bool("BOOL") is False
    monkeypatch.setenv("BOOL", "0")
    assert _get_environ_bool("BOOL") is False


def test_environ_bool_missing_variable():
    """Test _get_environ_bool returns default when variable not set."""
    assert _get_environ_bool("NONEXISTENT_BOOL") is False
    assert _get_environ_bool("NONEXISTENT_BOOL", default=True) is True


def test_environ_bool_with_default_true(monkeypatch):
    """Test _get_environ_bool with default=True."""
    # When default is True, absence or "0" should give False, "1" should give True
    assert _get_environ_bool("ANOTHER_NONEXISTENT", default=True) is True

    monkeypatch.setenv("BOOL2", "1")
    assert _get_environ_bool("BOOL2", default=True) is True

    monkeypatch.setenv("BOOL2", "0")
    assert _get_environ_bool("BOOL2", default=True) is False


def test_environ_port(monkeypatch):
    """Valid ports are between 0 and 65535."""
    monkeypatch.setenv("PORT", "-1")
    assert _get_environ_port("PORT", 80) == 80
    monkeypatch.setenv("PORT", "0")
    assert _get_environ_port("PORT", 80) == 0
    monkeypatch.setenv("PORT", "65535")
    assert _get_environ_port("PORT", 80) == 65535
    monkeypatch.setenv("PORT", "65536")
    assert _get_environ_port("PORT", 80) == 80


def test_environ_port_invalid_value(monkeypatch):
    """Test _get_environ_port returns default for invalid string values."""
    monkeypatch.setenv("PORT", "not_a_port")
    assert _get_environ_port("PORT", 8080) == 8080

    monkeypatch.setenv("PORT", "12.5")
    assert _get_environ_port("PORT", 3000) == 3000

    monkeypatch.setenv("PORT", "")
    assert _get_environ_port("PORT", 443) == 443


def test_environ_port_missing_variable():
    """Test _get_environ_port returns default when variable not set."""
    assert _get_environ_port("NONEXISTENT_PORT", 8000) == 8000
