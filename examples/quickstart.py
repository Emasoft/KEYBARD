#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KEYBARD Quickstart Example

A minimal example showing the basics of KEYBARD keyboard input handling.
This is the simplest way to get started with KEYBARD.

Run with: uv run examples/quickstart.py
"""

from keybard import KeyboardReader
from keybard.events import Key, Paste, Resize

print("🎹 KEYBARD Quickstart Demo")
print("=" * 50)
print("\nPress any key to see it detected.")
print("Try combinations like Ctrl+C, Alt+Enter, Shift+Tab")
print("Press 'q' or Ctrl+C to quit.\n")

# Create a keyboard reader
with KeyboardReader() as reader:
    while True:
        # Read the next key (blocking)
        event = reader.read_key()

        # Check event type and handle it
        if isinstance(event, Key):
            print(f"  Key: {event.key}")

            # Quit on 'q' or Ctrl+C
            if event.key in ("q", "ctrl+c"):
                print("\n👋 Goodbye!")
                break

        elif isinstance(event, Paste):
            print(f"  Paste: {repr(event.text)}")

        elif isinstance(event, Resize):
            print(f"  Resize: {event.size.width}x{event.size.height}")
