#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal capability and state messages.

These messages report terminal capabilities and configuration changes.
"""

from __future__ import annotations

from dataclasses import dataclass

from keybard.message import Message


@dataclass
class TerminalSupportsSynchronizedOutput(Message):
    """
    Terminal supports synchronized output mode.

    Synchronized output reduces flicker by buffering updates.
    See: https://gist.github.com/christianparpart/d8a62cc1ab659194337d73e399004036
    """

    def __post_init__(self) -> None:
        """Initialize the Message base class after dataclass init."""
        super().__init__()


@dataclass
class InBandWindowResize(Message):
    """
    Terminal supports in-band window resize reporting.

    This allows the terminal to report resize events with pixel dimensions.

    Attributes:
        supported: Terminal supports the in-band resize protocol
        enabled: In-band resize reporting is currently enabled
    """

    supported: bool
    enabled: bool

    def __post_init__(self) -> None:
        """Initialize the Message base class after dataclass init."""
        super().__init__()

    @classmethod
    def from_setting_parameter(cls, setting_parameter: int) -> InBandWindowResize:
        """
        Create InBandWindowResize from terminal mode report parameter.

        Args:
            setting_parameter: Value from terminal mode report
                1 = not recognized
                2 = set
                3 = reset
                4 = permanently set

        Returns:
            InBandWindowResize message
        """
        supported = setting_parameter in (2, 3, 4)
        enabled = setting_parameter == 2
        return cls(supported, enabled)
