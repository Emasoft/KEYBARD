#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KEYBARD Key Display Example

A comprehensive demonstration of keyboard input detection showing all types of keys,
key combinations, and key states (press/hold/release).

This example displays:
- Regular keys: A-Z, 0-9, symbols (@#$%^&*()_+-=[]{}\\|;:'",.<>/?)
- Function keys: F1-F12, F13-F20
- Special keys: Home, End, PageUp, PageDown, Insert, Delete, Tab, Enter, Escape
- Arrow keys: Up, Down, Left, Right
- Modifier keys: Ctrl, Alt, Shift, Meta/Win/Cmd
- Modifier combinations: Ctrl+C, Alt+Enter, Shift+Tab, Cmd+Option+X, etc.
- Key states: CLICK (single press), KEY-DOWN (held), KEY-UP (released)

Press Ctrl+C or 'q' to quit.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from keybard import KeyboardReader
from keybard.events import Key, Paste, Resize
import time
from dataclasses import dataclass
from typing import Dict


@dataclass
class KeyState:
    """Track the state of a key."""

    key: str
    first_seen: float
    last_seen: float
    repeat_count: int


class KeyTracker:
    """Track key press, hold, and release states."""

    def __init__(self, release_timeout: float = 0.15):
        self.keys: Dict[str, KeyState] = {}
        self.release_timeout = release_timeout
        self.history = []

    def process_key(self, key: str, timestamp: float) -> str:
        """
        Process a key event and return the event type.

        Returns: "CLICK", "KEY-DOWN", or None if just updating state
        """
        if key in self.keys:
            # Key already pressed - this is key repeat (holding)
            state = self.keys[key]
            state.last_seen = timestamp
            state.repeat_count += 1

            # After first repeat, return KEY-DOWN
            if state.repeat_count == 1:
                return "CLICK"
            elif state.repeat_count == 2:
                return "KEY-DOWN"
            else:
                # Subsequent repeats - update state but don't add new event
                return None
        else:
            # First time seeing this key
            self.keys[key] = KeyState(key=key, first_seen=timestamp, last_seen=timestamp, repeat_count=0)
            return "CLICK"

    def check_releases(self, current_time: float) -> list[tuple[str, str]]:
        """Check for keys that should be marked as released."""
        releases = []
        keys_to_remove = []

        for key, state in self.keys.items():
            if current_time - state.last_seen > self.release_timeout:
                # Key hasn't been seen recently - mark as released
                if state.repeat_count > 0:
                    releases.append((key, "KEY-UP"))
                keys_to_remove.append(key)

        # Remove released keys
        for key in keys_to_remove:
            del self.keys[key]

        return releases


def parse_modifiers_and_key(key_name: str) -> tuple[str, str]:
    """
    Split a key name into modifiers and base key.

    Returns: (modifiers, base_key)
    Examples:
        "ctrl+c" -> ("CTRL", "C")
        "ctrl+shift+x" -> ("CTRL+SHIFT", "X")
        "a" -> ("", "A")
    """
    if "+" not in key_name:
        return ("", key_name.upper())

    parts = key_name.split("+")
    modifiers = []
    base_key = parts[-1]

    for part in parts[:-1]:
        if part == "ctrl":
            modifiers.append("CTRL")
        elif part == "shift":
            modifiers.append("SHIFT")
        elif part == "alt":
            modifiers.append("ALT")
        elif part == "meta":
            modifiers.append("META")
        else:
            modifiers.append(part.upper())

    return ("+".join(modifiers), base_key.upper())


def create_help_panel() -> Panel:
    """Create a help panel showing what to try."""
    help_text = Text()
    help_text.append("KEYBARD Key State Tracker\n", style="bold cyan")
    help_text.append("Shows: CLICK (press), KEY-DOWN (held), KEY-UP (released)\n\n", style="dim")

    help_text.append("Try pressing and holding:\n", style="bold yellow")
    help_text.append("  • Arrow keys: ", style="dim")
    help_text.append("Up, Down, Left, Right\n", style="cyan")

    help_text.append("  • Modifiers: ", style="dim")
    help_text.append("Ctrl+C, Alt+Enter, Shift+Tab, Ctrl+Shift+X\n", style="cyan")

    help_text.append("  • Special keys: ", style="dim")
    help_text.append("Home, End, PageUp, PageDown, Insert, Delete\n", style="cyan")

    help_text.append("  • Function keys: ", style="dim")
    help_text.append("F1-F12\n", style="cyan")

    help_text.append("\nPress and HOLD a key to see KEY-DOWN events!\n", style="bold green")
    help_text.append("Release it to see KEY-UP events.\n\n", style="bold green")

    help_text.append("Press ", style="dim")
    help_text.append("q", style="bold red")
    help_text.append(" or ", style="dim")
    help_text.append("Ctrl+C", style="bold red")
    help_text.append(" to quit", style="dim")

    return Panel(help_text, title="[bold green]KEYBARD Key State Demo[/bold green]", border_style="green")


def format_key_visual(base_key: str, modifiers: str) -> str:
    """Create a color-coded visual representation of the key."""
    # Arrow keys get special symbols
    arrows = {"UP": "↑", "DOWN": "↓", "LEFT": "←", "RIGHT": "→"}
    if base_key in arrows:
        visual = f"[cyan]{arrows[base_key]}[/cyan]"
    elif base_key.startswith("F") and base_key[1:].isdigit():
        visual = f"[green]{base_key}[/green]"
    elif len(base_key) == 1 and base_key.isalnum():
        visual = f"[yellow]{base_key}[/yellow]"
    else:
        visual = f"[white]{base_key}[/white]"

    # Color modifiers
    if modifiers:
        mod_parts = []
        for mod in modifiers.split("+"):
            if mod == "CTRL":
                mod_parts.append("[red]CTRL[/red]")
            elif mod == "SHIFT":
                mod_parts.append("[blue]SHIFT[/blue]")
            elif mod == "ALT":
                mod_parts.append("[magenta]ALT[/magenta]")
            elif mod == "META":
                mod_parts.append("[green]META[/green]")
            else:
                mod_parts.append(f"[white]{mod}[/white]")
        return "+".join(mod_parts) + "+" + visual
    else:
        return visual


def main():
    """Run the key display demo."""
    console = Console()

    # Display initial help
    console.clear()
    console.print(create_help_panel())
    console.print()

    # Create key tracker
    tracker = KeyTracker(release_timeout=0.15)
    history = []
    max_history = 20

    with KeyboardReader() as reader:
        console.print("[dim]Listening for keyboard input...[/dim]\n")

        while True:
            current_time = time.time()
            has_changes = False  # Track if anything changed this iteration

            # Check for key releases
            releases = tracker.check_releases(current_time)
            if releases:
                has_changes = True
                for key, event_type in releases:
                    modifiers, base_key = parse_modifiers_and_key(key)
                    timestamp = time.strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
                    visual = format_key_visual(base_key, modifiers)
                    history.append((timestamp, modifiers, base_key, event_type, visual))

            # Poll for new events (non-blocking)
            events = reader.poll()

            if events:
                has_changes = True

            for event in events:
                # Handle quit commands
                if isinstance(event, Key):
                    if event.key == "q" or event.key == "ctrl+c":
                        console.print("\n[bold green]Goodbye![/bold green]")
                        return

                    # Track key state
                    event_type = tracker.process_key(event.key, current_time)

                    if event_type:  # Only add if it's a new state transition
                        modifiers, base_key = parse_modifiers_and_key(event.key)
                        timestamp = time.strftime("%H:%M:%S.%f")[:-3]  # milliseconds
                        visual = format_key_visual(base_key, modifiers)
                        history.append((timestamp, modifiers, base_key, event_type, visual))

                elif isinstance(event, Paste):
                    timestamp = time.strftime("%H:%M:%S.%f")[:-3]
                    history.append((timestamp, "", "PASTE", f"{len(event.text)} chars", f"[dim]{len(event.text)} characters[/dim]"))

                elif isinstance(event, Resize):
                    timestamp = time.strftime("%H:%M:%S.%f")[:-3]
                    history.append((timestamp, "", "RESIZE", f"{event.size.width}×{event.size.height}", "[dim]Terminal resize[/dim]"))

            # Keep only recent history
            if len(history) > max_history:
                history = history[-max_history:]

            # Only redraw if something changed
            if has_changes and history:
                # Create display table
                table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 1), show_lines=True)
                table.add_column("Time", style="dim", width=12, no_wrap=True)
                table.add_column("Modifier", style="cyan", width=20)
                table.add_column("Key", style="white", width=15)
                table.add_column("Event Type", width=12)
                table.add_column("Visual", width=35)

                for ts, mod, key, evt, vis in history:
                    # Color code event types
                    if evt == "CLICK":
                        evt_colored = f"[green]{evt}[/green]"
                    elif evt == "KEY-DOWN":
                        evt_colored = f"[yellow]{evt}[/yellow]"
                    elif evt == "KEY-UP":
                        evt_colored = f"[red]{evt}[/red]"
                    else:
                        evt_colored = f"[white]{evt}[/white]"

                    table.add_row(ts, mod, key, evt_colored, vis)

                # Clear and redisplay
                console.clear()
                console.print(create_help_panel())
                console.print()
                console.print(table)
                console.print()

                # Show current state
                if tracker.keys:
                    held_keys = ", ".join([f"[yellow]{k}[/yellow]" for k in tracker.keys.keys()])
                    console.print(f"[dim]Currently held: {held_keys}[/dim]")
                else:
                    console.print("[dim]No keys currently held[/dim]")

            # Small delay to avoid busy-waiting
            time.sleep(0.01)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[bold green]Goodbye![/bold green]")
    except Exception as e:
        console = Console()
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise
