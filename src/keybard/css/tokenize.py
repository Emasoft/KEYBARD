#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSS tokenization constants.

Defines token types used in CSS color parsing.
"""

from __future__ import annotations

# Token constants for color parsing - these are regex patterns
OPEN_BRACE = r"\(\s*"
CLOSE_BRACE = r"\s*\)"
COMMA = r"\s*,\s*"
DECIMAL = r"-?\d+\.?\d*"
PERCENT = r"-?\d+\.?\d*%"
