#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KEYBARD Quickstart Example

A minimal example showing the basics of KEYBARD keyboard input handling.
This is the simplest way to get started with KEYBARD.

This example demonstrates:
- Creating a KeyboardReader with default settings
- Using the context manager for automatic cleanup
- Reading keyboard events in a blocking loop
- Distinguishing between Key, Paste, and Resize events
- Normalizing key names (e.g., 'ctrl+c' instead of raw escape codes)

Run with: uv run examples/quickstart.py
"""

from keybard import KeyboardReader
from keybard.events import Key, Paste, Resize

print("🎹 KEYBARD Quickstart Demo")
print("=" * 50)
print("\nPress any key to see it detected.")
print("Try combinations like Ctrl+C, Alt+Enter, Shift+Tab")
print("Press 'q' or Ctrl+C to quit.\n")

# Create a keyboard reader using context manager to ensure terminal cleanup on exit
with KeyboardReader() as reader:
    while True:
        # Read the next key event - this blocks until a key is pressed
        # The blocking behavior simplifies logic for interactive CLI tools
        event = reader.read_key()

        # Handle different event types separately for clarity and type safety
        if isinstance(event, Key):
            # Display the normalized key name (lowercase with modifiers separated by '+')
            print(f"  Key: {event.key}")

            # Exit cleanly on 'q' or Ctrl+C - checking normalized names ensures consistency
            if event.key in ("q", "ctrl+c"):
                print("\n👋 Goodbye!")
                break

        elif isinstance(event, Paste):
            # Bracketed paste mode lets us detect pasted text vs typed text
            # Using repr() shows escape sequences and special characters clearly
            print(f"  Paste: {repr(event.text)}")

        elif isinstance(event, Resize):
            # Terminal resize events let us adapt UI to new dimensions
            # Size is reported in character cells (width × height)
            print(f"  Resize: {event.size.width}x{event.size.height}")
