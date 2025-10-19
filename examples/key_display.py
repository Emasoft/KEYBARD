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

import argparse
import time
from dataclasses import dataclass
from typing import Dict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from keybard import KeyboardReader
from keybard.dispatcher import DispatcherConfig
from keybard.events import Key, KeyClick, KeyDown, KeyUp, Paste, Resize


@dataclass
class KeyState:
    """Track the state of a key.

    Stores timing information to distinguish between:
    - Single taps (CLICK): key seen once, not repeated
    - Holds (KEY-DOWN): key repeated, indicating it's being held
    - Releases (KEY-UP): key not seen recently after being held
    """

    key: str  # Normalized key name (e.g., "ctrl+c", "a", "up")
    first_seen: float  # Timestamp when key was first pressed (for duration calculation)
    last_seen: float  # Timestamp of most recent repeat (used to detect release)
    repeat_count: int  # Number of repeats seen (0 = just pressed, >0 = being held)


class KeyTracker:
    """Track key press, hold, and release states.

    Terminals don't send explicit key-up events - they only send key-down and repeats.
    This tracker infers release by detecting when repeats stop coming.
    """

    def __init__(self, release_timeout: float = 0.15):
        # Dictionary mapping active key names to their state
        self.keys: Dict[str, KeyState] = {}
        # Time threshold to consider a key released (typical key repeat interval is 30-50ms)
        # Using 150ms is safe to catch releases without false positives
        self.release_timeout = release_timeout
        # History is unused in this class but kept for potential extensions
        self.history = []

    def process_key(self, key: str, timestamp: float) -> str:
        """Process a key event and return the event type.

        Returns: "CLICK", "KEY-DOWN", or None if just updating state

        The logic here implements a state machine:
        1. First press → CLICK (optimistic: assume it's a tap until proven otherwise)
        2. First repeat → KEY-DOWN (now we know it's being held)
        3. Subsequent repeats → None (already know it's held, just update timing)
        """
        if key in self.keys:
            # Key already pressed - this is a repeat event from terminal
            # Repeats only happen when a key is physically held down
            state = self.keys[key]
            state.last_seen = timestamp  # Update to prevent false release detection
            state.repeat_count += 1

            # Emit KEY-DOWN only on first repeat to avoid flooding with events
            # We want to signal "now being held" once, not spam the event stream
            if state.repeat_count == 1:
                return "KEY-DOWN"  # First repeat transitions CLICK → KEY-DOWN
            else:
                # Subsequent repeats just update timing, no new event needed
                # This prevents hundreds of KEY-DOWN events from a single hold
                return None
        else:
            # First time seeing this key - create initial state
            # We optimistically call it a CLICK, even though it might become a hold
            # This ensures responsive UIs that don't wait to see if it's a hold
            self.keys[key] = KeyState(key=key, first_seen=timestamp, last_seen=timestamp, repeat_count=0)
            return "CLICK"

    def check_releases(self, current_time: float) -> list[tuple[str, str]]:
        """Check for keys that should be marked as released.

        Since terminals don't send explicit key-up events, we infer release by
        detecting when key repeat events stop arriving. If we haven't seen a repeat
        for longer than release_timeout, the key must have been released.
        """
        releases = []
        keys_to_remove = []

        for key, state in self.keys.items():
            # Calculate time since we last saw this key
            time_since_last_seen = current_time - state.last_seen

            if time_since_last_seen > self.release_timeout:
                # No repeat events for too long → user must have released the key
                # Only emit KEY-UP if the key was actually held (repeat_count > 0)
                # If repeat_count == 0, it was just a tap that we already reported as CLICK
                if state.repeat_count > 0:
                    releases.append((key, "KEY-UP"))
                # Clean up state regardless of whether we emit KEY-UP
                # This prevents memory leaks from accumulating dead key states
                keys_to_remove.append(key)

        # Remove released keys from tracking (can't delete during iteration)
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


def create_help_panel(use_dispatcher: bool = False) -> Panel:
    """Create a help panel showing what to try."""
    help_text = Text()
    help_text.append("KEYBARD Key State Tracker\n", style="bold cyan")
    if use_dispatcher:
        help_text.append("Using: KeyEventDispatcher (timing-based events)\n", style="green")
    else:
        help_text.append("Using: Manual key tracking (repeat-based detection)\n", style="yellow")
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
    """Create a color-coded visual representation of the key.

    Uses rich markup to colorize different key types for easy visual scanning.
    Color choices help users quickly identify key categories in the output.
    """
    # Arrow keys get Unicode symbols for better visual recognition
    # Symbols are more intuitive than text (← vs "LEFT")
    arrows = {"UP": "↑", "DOWN": "↓", "LEFT": "←", "RIGHT": "→"}
    if base_key in arrows:
        visual = f"[cyan]{arrows[base_key]}[/cyan]"  # Cyan for navigation keys
    elif base_key.startswith("F") and base_key[1:].isdigit():
        visual = f"[green]{base_key}[/green]"  # Green for function keys
    elif len(base_key) == 1 and base_key.isalnum():
        visual = f"[yellow]{base_key}[/yellow]"  # Yellow for regular alphanumeric
    else:
        visual = f"[white]{base_key}[/white]"  # White for special keys

    # Color-code modifiers to distinguish them from base keys
    # Each modifier gets a distinct color for quick recognition
    if modifiers:
        mod_parts = []
        for mod in modifiers.split("+"):
            if mod == "CTRL":
                mod_parts.append("[red]CTRL[/red]")  # Red = primary/important
            elif mod == "SHIFT":
                mod_parts.append("[blue]SHIFT[/blue]")  # Blue = modifier
            elif mod == "ALT":
                mod_parts.append("[magenta]ALT[/magenta]")  # Magenta = alternate
            elif mod == "META":
                mod_parts.append("[green]META[/green]")  # Green = system
            else:
                mod_parts.append(f"[white]{mod}[/white]")  # Unknown modifiers in white
        return "+".join(mod_parts) + "+" + visual
    else:
        return visual


def main():
    """Run the key display demo."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="KEYBARD Key Display Example")
    parser.add_argument(
        "--use-dispatcher",
        action="store_true",
        help="Use KeyEventDispatcher instead of manual tracking",
    )
    parser.add_argument(
        "--delta",
        type=float,
        default=1.0,
        help="Delta threshold for click vs hold (seconds, default: 1.0)",
    )
    args = parser.parse_args()

    console = Console()

    # Display initial help
    console.clear()
    console.print(create_help_panel(use_dispatcher=args.use_dispatcher))
    console.print()

    # Create key tracker (only if not using dispatcher)
    # The dispatcher provides built-in timing-based events, so manual tracking is redundant
    tracker = None if args.use_dispatcher else KeyTracker(release_timeout=0.15)
    history = []  # Recent events to display in scrolling table
    max_history = 20  # Limit history to prevent memory growth and keep UI readable

    # Setup reader with optional dispatcher
    # Two modes demonstrate different approaches to detecting key states:
    # 1. Dispatcher mode: Uses built-in timing logic (more accurate, recommended)
    # 2. Manual mode: Custom repeat-based detection (educational, shows how it works)
    if args.use_dispatcher:
        config = DispatcherConfig(delta=args.delta, release_timeout=0.15)
        reader = KeyboardReader(use_dispatcher=True, dispatcher_config=config)
    else:
        reader = KeyboardReader()

    with reader:
        console.print("[dim]Listening for keyboard input...[/dim]\n")

        while True:
            current_time = time.time()
            # Track changes to avoid redrawing the UI unnecessarily
            # Redrawing on every loop iteration causes flicker and wastes CPU
            has_changes = False

            # Check for key releases (manual tracker only)
            # This must happen before polling to ensure releases are detected promptly
            # even if no new events arrive (user stopped pressing keys)
            if tracker:
                releases = tracker.check_releases(current_time)
                if releases:
                    has_changes = True
                    for key, event_type in releases:
                        modifiers, base_key = parse_modifiers_and_key(key)
                        timestamp = time.strftime("%H:%M:%S.%f")[:-3]  # Milliseconds for precise timing
                        visual = format_key_visual(base_key, modifiers)
                        history.append((timestamp, modifiers, base_key, event_type, visual))

            # Poll for new events (non-blocking)
            # Using poll() instead of read_key() allows us to:
            # 1. Check for releases on each loop iteration
            # 2. Maintain a responsive UI even when no keys are pressed
            # 3. Process multiple events in a single iteration
            events = reader.poll()

            if events:
                has_changes = True

            for event in events:
                # Handle dispatcher events (timing-based)
                # These events come from KeyEventDispatcher which uses precise timing
                if isinstance(event, KeyClick):
                    # Check for quit commands before processing
                    if event.key == "q" or event.key == "ctrl+c":
                        console.print("\n[bold green]Goodbye![/bold green]")
                        return

                    modifiers, base_key = parse_modifiers_and_key(event.key)
                    timestamp = time.strftime("%H:%M:%S.%f")[:-3]
                    visual = format_key_visual(base_key, modifiers)
                    history.append((timestamp, modifiers, base_key, "CLICK", visual))

                elif isinstance(event, KeyDown):
                    modifiers, base_key = parse_modifiers_and_key(event.key)
                    timestamp = time.strftime("%H:%M:%S.%f")[:-3]
                    visual = format_key_visual(base_key, modifiers)
                    # Only show first KEY-DOWN (repeat_count == 0) to avoid spam
                    # Subsequent repeats just update internal state without new events
                    if event.repeat_count == 0:
                        history.append((timestamp, modifiers, base_key, "KEY-DOWN", visual))

                elif isinstance(event, KeyUp):
                    modifiers, base_key = parse_modifiers_and_key(event.key)
                    timestamp = time.strftime("%H:%M:%S.%f")[:-3]
                    visual = format_key_visual(base_key, modifiers)
                    history.append((timestamp, modifiers, base_key, "KEY-UP", visual))

                # Handle raw Key events (manual tracker only)
                # These are the basic events from the terminal parser
                elif isinstance(event, Key):
                    # Check for quit first, before tracking state
                    if event.key == "q" or event.key == "ctrl+c":
                        console.print("\n[bold green]Goodbye![/bold green]")
                        return

                    # Track key state with manual tracker to infer CLICK/DOWN/UP
                    # This demonstrates how to build timing-based detection manually
                    if tracker:
                        event_type = tracker.process_key(event.key, current_time)

                        # Only add to history if it's a state transition (not just a repeat update)
                        # event_type is None for subsequent repeats to avoid flooding the display
                        if event_type:
                            modifiers, base_key = parse_modifiers_and_key(event.key)
                            timestamp = time.strftime("%H:%M:%S.%f")[:-3]  # Milliseconds
                            visual = format_key_visual(base_key, modifiers)
                            history.append((timestamp, modifiers, base_key, event_type, visual))

                elif isinstance(event, Paste):
                    timestamp = time.strftime("%H:%M:%S.%f")[:-3]
                    history.append((timestamp, "", "PASTE", f"{len(event.text)} chars", f"[dim]{len(event.text)} characters[/dim]"))

                elif isinstance(event, Resize):
                    timestamp = time.strftime("%H:%M:%S.%f")[:-3]
                    history.append((timestamp, "", "RESIZE", f"{event.size.width}×{event.size.height}", "[dim]Terminal resize[/dim]"))

            # Keep only recent history to prevent unbounded memory growth
            # Also keeps the UI focused on recent activity rather than overwhelming with old events
            if len(history) > max_history:
                history = history[-max_history:]

            # Only redraw if something changed - critical for performance
            # Constant redrawing causes flicker and wastes CPU cycles
            # Also require history to exist to avoid drawing empty tables
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
                console.print(create_help_panel(use_dispatcher=args.use_dispatcher))
                console.print()
                console.print(table)
                console.print()

                # Show current state (manual tracker only)
                if tracker:
                    if tracker.keys:
                        held_keys = ", ".join([f"[yellow]{k}[/yellow]" for k in tracker.keys.keys()])
                        console.print(f"[dim]Currently held: {held_keys}[/dim]")
                    else:
                        console.print("[dim]No keys currently held[/dim]")
                else:
                    console.print("[dim]Using KeyEventDispatcher for timing-based events[/dim]")

            # Small delay to avoid busy-waiting and reduce CPU usage
            # 10ms is short enough for responsive UI but long enough to prevent CPU spinning
            # Without this, the loop would consume 100% CPU checking for events constantly
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
