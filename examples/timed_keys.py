#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KEYBARD Timing-Based Events Example

Demonstrates the timing-based event model that distinguishes between:
- CLICK: Quick press and release (within delta threshold, default 1.0s)
- KEY-DOWN: Key held past the delta threshold
- KEY-UP: Key released after being held

This model allows applications to respond differently to quick taps vs
prolonged holds, enabling richer interaction patterns.

Note: Modifier combinations (Ctrl+C, Shift+A, etc.) come from the terminal
parser as atomic Key events and are handled like single keys.

IMPORTANT LIMITATION:
Terminal input only provides key press events, never key release events.
The dispatcher infers hold/release from OS key repetition behavior:
- Keys WITH repetition (a-z, 0-9, arrows): Can detect KeyDown/KeyUp
- Keys WITHOUT repetition (Escape, modifiers alone): Always emit Click after delta
This is a fundamental constraint of terminal input, not a library bug.

Press Ctrl+C or 'q' to quit.
"""

import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from keybard import DispatcherConfig, KeyboardReader
from keybard.events import Key, KeyClick, KeyDown, KeyUp, Paste, Resize


def create_help_panel(delta: float) -> Panel:
    """Create a help panel showing how the timing model works."""
    help_text = Text()
    help_text.append("KEYBARD Timing-Based Event Model\n", style="bold cyan")
    help_text.append(
        f"Delta threshold: {delta:.1f}s\n\n",
        style="dim",
    )

    help_text.append("Event Types:\n", style="bold yellow")

    help_text.append("  • ", style="dim")
    help_text.append("CLICK", style="green")
    help_text.append(" - Press & release within ", style="dim")
    help_text.append(f"{delta:.1f}s\n", style="cyan")

    help_text.append("  • ", style="dim")
    help_text.append("KEY-DOWN", style="yellow")
    help_text.append(f" - Held for >{delta:.1f}s", style="dim")
    help_text.append(" (reported after waiting)\n", style="dim")

    help_text.append("  • ", style="dim")
    help_text.append("KEY-UP", style="red")
    help_text.append(" - Released after KEY-DOWN\n\n", style="dim")

    help_text.append("Try this:\n", style="bold green")
    help_text.append("  1. Tap 'a' quickly → ", style="dim")
    help_text.append("CLICK", style="green")
    help_text.append("\n")

    help_text.append("  2. Hold 'b' for 2 seconds → ", style="dim")
    help_text.append("KEY-DOWN", style="yellow")
    help_text.append(" then ", style="dim")
    help_text.append("KEY-UP\n", style="red")

    help_text.append("  3. Press Ctrl+C to quit", style="dim")

    help_text.append("\n\nNotice the delay before KEY-DOWN!\n", style="bold yellow")

    help_text.append("\n⚠️  ", style="dim")
    help_text.append("LIMITATION:", style="bold red")
    help_text.append(" Keys without OS repetition\n", style="dim")
    help_text.append("(Escape, modifiers alone) will emit CLICK after\n", style="dim")
    help_text.append("delta timeout even if still held. This is a\n", style="dim")
    help_text.append("fundamental terminal input constraint.\n", style="dim")

    return Panel(
        help_text,
        title="[bold green]Timing-Based Events Demo[/bold green]",
        border_style="green",
    )


def format_event(event) -> tuple[str, str, str, str]:
    """Format an event for display.

    Returns: (event_type, key_info, duration, color)

    Color coding makes different event types immediately distinguishable:
    - Green (CLICK): Quick taps, positive/complete actions
    - Yellow (KEY-DOWN): Warning/attention, key is being held
    - Red (KEY-UP): Stop/release, hold completed
    """
    if isinstance(event, KeyClick):
        # Quick tap: show how fast it was (duration = press to release time)
        return (
            "CLICK",
            event.key,
            f"{event.duration:.3f}s",  # Precision helps see timing patterns
            "green",  # Green = quick/successful action
        )
    elif isinstance(event, KeyDown):
        # Hold detected: show how long it's been held so far
        return (
            "KEY-DOWN",
            event.key,
            f"{event.hold_time:.3f}s",  # Time from press to detection
            "yellow",  # Yellow = in-progress state
        )
    elif isinstance(event, KeyUp):
        # Release after hold: show total hold duration
        return (
            "KEY-UP",
            event.key,
            f"{event.total_duration:.3f}s",  # Complete hold time
            "red",  # Red = completion/stop
        )
    elif isinstance(event, Key):
        # Raw key events shouldn't appear when dispatcher is enabled
        # This is a fallback for debugging or unexpected configurations
        return (
            "RAW-KEY",
            event.key,
            "N/A",
            "white",  # Neutral color for unexpected events
        )
    elif isinstance(event, Paste):
        # Pasted text: show character count since content may be large
        return (
            "PASTE",
            f"{len(event.text)} chars",
            "N/A",  # Paste events have no meaningful duration
            "cyan",
        )
    elif isinstance(event, Resize):
        # Terminal resize: show new dimensions
        return (
            "RESIZE",
            f"{event.size.width}×{event.size.height}",
            "N/A",  # Resize is instant, no duration
            "dim",  # Dim = background/environmental event
        )
    else:
        # Unknown event type: display class name for debugging
        return (
            type(event).__name__,
            str(event),
            "N/A",
            "white",
        )


def main():
    """Run the timing-based events demo.

    This demo shows the timing-based event model in action, making the
    delta threshold and timing behavior visually clear to users.
    """
    console = Console()

    # Configure delta threshold (time to distinguish click from hold)
    # Delta of 1.0s is good for demos - clearly shows the delay before KEY-DOWN
    # In real apps, you might use shorter values (0.3-0.5s) for more responsive UI
    delta = 1.0  # 1 second - configurable
    config = DispatcherConfig(delta=delta)

    # Display initial help
    console.clear()
    console.print(create_help_panel(delta))
    console.print()

    history = []  # Event history for display
    max_history = 15  # Keep display focused and prevent memory growth

    # Enable dispatcher to get timing-based events instead of raw Key events
    # The dispatcher transforms raw Key repeats into Click/KeyDown/KeyUp semantics
    with KeyboardReader(use_dispatcher=True, dispatcher_config=config) as reader:
        console.print("[dim]Listening for keyboard input with timing detection...[/dim]\n")
        # Emphasize the delay to help users understand the timing model
        console.print("[yellow]Notice: KEY-DOWN events appear after a 1-second delay![/yellow]\n")

        while True:
            # Poll for events (non-blocking)
            # Non-blocking is essential for maintaining responsive UI updates
            events = reader.poll()

            for event in events:
                # Handle quit commands
                # Only check Click events because KeyDown/KeyUp come later
                if isinstance(event, KeyClick):
                    if event.key == "q" or event.key == "ctrl+c":
                        console.print("\n[bold green]Goodbye![/bold green]")
                        return

                # Format and add to history for display
                event_type, key_info, duration, color = format_event(event)
                timestamp = time.strftime("%H:%M:%S")  # Second precision is sufficient
                history.append((timestamp, event_type, key_info, duration, color))

                # Keep only recent history to prevent unbounded growth
                # Also keeps the display focused on current activity
                if len(history) > max_history:
                    history = history[-max_history:]

                # Redraw display on every event to show immediate feedback
                # This makes the timing behavior clear and visible to users
                console.clear()
                console.print(create_help_panel(delta))
                console.print()

                # Create event history table
                table = Table(
                    show_header=True,
                    header_style="bold magenta",
                    box=None,
                    padding=(0, 1),
                    show_lines=True,
                )
                table.add_column("Time", style="dim", width=10, no_wrap=True)
                table.add_column("Event Type", width=18)
                table.add_column("Key", style="cyan", width=25)
                table.add_column("Duration/Time", style="yellow", width=15)

                for ts, evt_type, key, dur, clr in history:
                    evt_colored = f"[{clr}]{evt_type}[/{clr}]"
                    table.add_row(ts, evt_colored, key, dur)

                console.print(table)
                console.print()

            # Small delay to avoid busy-waiting and reduce CPU usage
            # 10ms provides ~100 FPS polling rate - more than enough for keyboard input
            # Without this, the loop would consume 100% CPU constantly checking for events
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
