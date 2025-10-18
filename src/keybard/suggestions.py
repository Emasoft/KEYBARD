#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suggestion utilities for error messages.

Provides fuzzy matching for suggesting corrections.
"""

from __future__ import annotations

from difflib import get_close_matches


def get_suggestion(word: str, possibilities: list[str]) -> str | None:
    """
    Get the closest match suggestion for a word.

    Uses fuzzy string matching to find the most similar possibility.

    Args:
        word: The word to find suggestions for
        possibilities: List of valid possibilities

    Returns:
        Closest match or None if no good match found

    Examples:
        >>> get_suggestion("blu", ["red", "green", "blue"])
        'blue'
        >>> get_suggestion("xyz", ["red", "green", "blue"])
        None
    """
    matches = get_close_matches(word, possibilities, n=1, cutoff=0.6)
    return matches[0] if matches else None
