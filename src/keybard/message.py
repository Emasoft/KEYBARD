#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Message class for all events and messages in keybard.

All keyboard/mouse events and terminal messages inherit from this base class.
"""

from __future__ import annotations

import time


class Message:
    """
    Base class for all events and messages.

    Provides a timestamp for when the message was created.
    """

    def __init__(self) -> None:
        """Initialize message with current timestamp."""
        self.timestamp: float = time.time()
