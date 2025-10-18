#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scalar value parsing for CSS.

Provides utilities to parse percentage strings.
"""

from __future__ import annotations


def percentage_string_to_float(percentage: str) -> float:
    """
    Convert percentage string to float.

    Args:
        percentage: String like "50%" or "75.5%"

    Returns:
        Float value (0.5 for "50%", 0.755 for "75.5%")

    Examples:
        >>> percentage_string_to_float("50%")
        0.5
        >>> percentage_string_to_float("100%")
        1.0
        >>> percentage_string_to_float("33.33%")
        0.3333
    """
    # Strip both whitespace and the % sign to handle " 25% " correctly
    return float(percentage.strip().rstrip("%")) / 100.0
