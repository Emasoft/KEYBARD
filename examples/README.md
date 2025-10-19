# KEYBARD Examples

This directory contains examples demonstrating KEYBARD's keyboard input handling capabilities.

## Requirements

All examples require KEYBARD and Rich to be installed:

```bash
# Install KEYBARD with dependencies
uv pip install -e ".[dev]"

# Or if Rich is not installed
uv pip install rich
```

## Examples

### quickstart.py - Minimal Getting Started Example

The simplest possible example showing KEYBARD basics in under 30 lines of code.

**What it demonstrates:**

- Basic `KeyboardReader` usage with context manager
- Blocking input with `read_key()`
- Event type checking (`Key`, `Paste`, `Resize`)
- Simple quit handling on 'q' or Ctrl+C

**How to run:**

```bash
uv run examples/quickstart.py
```

Perfect for understanding the fundamentals before moving to more complex examples!

---

### timed_keys.py - Timing-Based Events Demo

An interactive demonstration of KEYBARD's timing-based event model that distinguishes between quick taps and prolonged holds.

**What it demonstrates:**

- **Timing-based events**:
  - `KeyClick` - Quick press and release (within delta threshold, default 1.0s)
  - `KeyDown` - Key held past the delta threshold (emitted after waiting)
  - `KeyUp` - Key released after being held
- **Configurable delta threshold**: Adjust the time threshold for click vs hold
- **Real-time event history**: Table showing the last 15 events with timestamps
- **Terminal limitation warnings**: Clear in-UI warnings about keys without OS repetition
- **Visual demonstration**: Color-coded display (Click=green, KeyDown=yellow, KeyUp=red)

**How to run:**

```bash
uv run examples/timed_keys.py
```

**What you'll see:**

The demo displays a help panel explaining the timing model, followed by a table showing recent events:

| Time     | Event Type | Key | Duration/Time |
|----------|------------|-----|---------------|
| 12:34:56 | CLICK      | a   | 0.123s        |
| 12:34:58 | KEY-DOWN   | b   | 1.002s        |
| 12:35:00 | KEY-UP     | b   | 2.456s        |

**Controls:**

- **Tap 'a' quickly** → See CLICK event
- **Hold 'b' for 2 seconds** → See KEY-DOWN (after 1s wait), then KEY-UP on release
- Press **q** or **Ctrl+C** to quit

**Important limitation:**

The demo includes prominent warnings about terminal key repetition:
- Keys WITH OS repetition (a-z, 0-9, arrows): Can detect KeyDown/KeyUp
- Keys WITHOUT repetition (Escape, modifiers alone): Always emit Click after delta
- This is a fundamental terminal input constraint, not a library bug

The KeyDown event only appears AFTER the delta timeout has passed while the key is still held. This is expected behavior - the dispatcher must wait to distinguish between a quick tap and a hold.

**Technical details:**

- Uses `KeyEventDispatcher` with configurable `DispatcherConfig`
- Non-blocking event polling with `KeyboardReader.poll()`
- Rich table display with color-coded event types
- Delta threshold default: 1.0s (configurable)
- Release timeout: 0.15s for inferring key release
- Demonstrates OS key repeat pattern detection

---

### key_display.py - Comprehensive Key State Tracker

A visual demonstration of KEYBARD's keyboard input detection capabilities showing not just
what keys are pressed, but tracking their states (press/hold/release).

**What it demonstrates:**

- **Two Operating Modes**:
  - **Manual tracking mode** (default): Demonstrates custom repeat-based key state detection
  - **Dispatcher mode** (`--use-dispatcher`): Uses built-in timing-based event system
- **Key States**:
  - `CLICK` (green) - Initial key press
  - `KEY-DOWN` (yellow) - Key is being held down (repeat events)
  - `KEY-UP` (red) - Key was released (inferred from timeout)
- **Modifiers in separate column**: CTRL, SHIFT, ALT, META shown separately
- **Regular keys**: A-Z, 0-9, all symbols (@#$%^&*()_+-=[]{}\\|;:'",.<>/?)
- **Function keys**: F1-F12 (and F13-F20 if supported)
- **Special keys**: Home, End, PageUp, PageDown, Insert, Delete, Tab, Enter, Escape
- **Arrow keys**: Up (↑), Down (↓), Left (←), Right (→)
- **Modifier combinations**:
  - Ctrl+Key (e.g., Ctrl+C, Ctrl+P, Ctrl+Enter, Ctrl+@)
  - Alt+Key (e.g., Alt+Enter, Alt+[, Alt+~)
  - Shift+Key (e.g., Shift+Tab, Shift+Enter, Shift+Delete, Shift+Up)
  - Meta/Cmd/Win+Key (platform-dependent)
- **Multiple modifiers**: Ctrl+Shift+X, Ctrl+Alt+Delete, Cmd+Option+Esc, etc.
- **Real-time state tracking**: Shows which keys are currently held down
- **Event types**: Key events, Paste events, Resize events
- **Millisecond timestamps**: Precise timing of each event

**How to run:**

```bash
# Manual tracking mode (default) - demonstrates custom key state detection
uv run examples/key_display.py

# Dispatcher mode - uses built-in timing system (recommended)
uv run examples/key_display.py --use-dispatcher

# Dispatcher mode with custom delta threshold (0.5 seconds)
uv run examples/key_display.py --use-dispatcher --delta 0.5

# Or make it executable and run directly
chmod +x examples/key_display.py
./examples/key_display.py
```

**What you'll see:**

The demo displays a help panel at the top, followed by a table showing the 20 most recent
key events with state transitions.

**Table format:**

|     Time      | Modifier  |     Key      | Event Type  |      Visual       |
|---------------|-----------|--------------|-------------|-------------------|
| HH:MM:SS.mmm  | CTRL      |   C          | CLICK       | CTRL+C (colored)  |
| HH:MM:SS.mmm  | SHIFT     |   UP         | CLICK       | SHIFT+↑           |
| HH:MM:SS.mmm  | SHIFT     |   UP         | KEY-DOWN    | SHIFT+↑           |
| HH:MM:SS.mmm  | SHIFT     |   UP         | KEY-UP      | SHIFT+↑           |

Each row shows:
- **Time**: Millisecond-precision timestamp (HH:MM:SS.mmm)
- **Modifier**: Modifier keys (CTRL, SHIFT, ALT, META) or empty if none
- **Key**: The base key name (C, UP, PAGEUP, F1, etc.)
- **Event Type**: CLICK (green), KEY-DOWN (yellow), or KEY-UP (red)
- **Visual**: Color-coded representation combining modifiers and key

At the bottom, you'll see a list of currently held keys.

**Controls:**

- Press **any key** briefly to see a CLICK event
- **Hold a key down** to see CLICK → KEY-DOWN progression
- **Release the key** to see a KEY-UP event (after 150ms timeout)
- Try holding **arrow keys**, **Ctrl+C**, **Shift+PageUp**, etc.
- Press **q** or **Ctrl+C** to quit

**Examples of keys to try:**

Regular keys:
- Letters: `a`, `b`, `c`, `A`, `B`, `C` (shift is automatic)
- Numbers: `1`, `2`, `3`, `!`, `@`, `#` (shift variants)
- Symbols: `[`, `]`, `;`, `'`, `,`, `.`, `/`, `\`, etc.

Function and special keys:
- `F1`, `F2`, `F3`, ... `F12`
- `Home`, `End`, `PageUp`, `PageDown`
- `Insert`, `Delete`, `Backspace`
- `Tab`, `Enter`, `Escape`
- `Up`, `Down`, `Left`, `Right`

Ctrl combinations:
- `Ctrl+C`, `Ctrl+P`, `Ctrl+S`, `Ctrl+Z`
- `Ctrl+Enter`, `Ctrl+Backspace`, `Ctrl+Delete`
- `Ctrl+Up`, `Ctrl+Down`, `Ctrl+Left`, `Ctrl+Right`
- `Ctrl+@`, `Ctrl+[`, `Ctrl+]`

Alt/Option combinations:
- `Alt+Enter`, `Alt+Backspace`, `Alt+Delete`
- `Alt+[`, `Alt+]`, `Alt+~`, `Alt+/`
- `Alt+Up`, `Alt+Down`, `Alt+Left`, `Alt+Right`

Shift combinations:
- `Shift+Tab`, `Shift+Enter`, `Shift+Backspace`, `Shift+Delete`
- `Shift+Up`, `Shift+Down`, `Shift+Left`, `Shift+Right`
- `Shift+Home`, `Shift+End`, `Shift+PageUp`, `Shift+PageDown`
- `Shift+F1`, `Shift+F2`, etc.

Multiple modifiers:
- `Ctrl+Shift+X`, `Ctrl+Shift+Enter`
- `Ctrl+Alt+Delete`, `Ctrl+Alt+Backspace`
- `Cmd+Option+Esc` (macOS), `Win+Alt+X` (Windows)
- `Shift+Alt+Tab`, `Ctrl+Shift+Alt+Key`

**Technical details:**

- **Manual Mode** (default):
  - Uses `KeyboardReader.poll()` for non-blocking event retrieval
  - Implements custom `KeyTracker` class to demonstrate state detection
  - Infers KEY-UP events using 150ms timeout (no events = key released)
  - Educational: shows how to build timing-based detection manually
- **Dispatcher Mode** (`--use-dispatcher`):
  - Uses built-in `KeyEventDispatcher` with configurable `DispatcherConfig`
  - Receives `KeyClick`, `KeyDown`, `KeyUp` events directly from KEYBARD
  - More accurate timing and recommended for production use
- **Display Features**:
  - Separates modifiers from base keys for clearer display
  - Millisecond-precision timestamps for timing analysis
  - Shows currently held keys at bottom of screen (manual mode)
  - Updates display at ~100 FPS (10ms poll interval) for responsive feedback
  - Rich library for beautiful table formatting and colors
  - Color codes: CLICK=green, KEY-DOWN=yellow, KEY-UP=red

## Creating Your Own Examples

KEYBARD makes it easy to create interactive terminal applications. Here are the essential patterns:

### Pattern 1: Simple Blocking Input (like quickstart.py)

For interactive prompts and simple CLI tools:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from keybard import KeyboardReader
from keybard.events import Key

# Context manager ensures terminal cleanup on exit
with KeyboardReader() as reader:
    while True:
        # Block until a key is pressed
        event = reader.read_key()

        if isinstance(event, Key):
            print(f"Key pressed: {event.key}")

            if event.key == "q":
                break
```

### Pattern 2: Non-Blocking Game Loop (like key_display.py)

For games, animations, or real-time UIs:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from keybard import KeyboardReader
from keybard.events import Key

with KeyboardReader() as reader:
    while True:
        # Get all pending events without blocking
        events = reader.poll()

        for event in events:
            if isinstance(event, Key):
                if event.key == "q":
                    exit(0)
                # Process other keys...

        # Update game state, render, etc.
        # ...

        # Prevent CPU spinning
        time.sleep(0.01)
```

### Pattern 3: Timing-Based Events (like timed_keys.py)

For applications that need to distinguish quick taps from holds:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from keybard import KeyboardReader
from keybard.dispatcher import DispatcherConfig
from keybard.events import KeyClick, KeyDown, KeyUp

# Configure timing threshold
config = DispatcherConfig(delta=0.5)  # 500ms threshold

with KeyboardReader(use_dispatcher=True, dispatcher_config=config) as reader:
    while True:
        events = reader.poll()

        for event in events:
            if isinstance(event, KeyClick):
                print(f"Quick tap: {event.key}")
            elif isinstance(event, KeyDown):
                print(f"Holding: {event.key}")
            elif isinstance(event, KeyUp):
                print(f"Released: {event.key}")
```

### Key Concepts

1. **Context Manager**: Use `with reader:` to automatically start/stop the reader and restore terminal state
2. **Blocking Input**: Use `read_key(timeout=...)` to wait for a single key (good for prompts)
3. **Non-Blocking Input**: Use `poll()` to get all pending events without waiting (good for games/UIs)
4. **Event Types**: Check `isinstance(event, Key)` to filter different event types
5. **Key Names**: Access normalized key names via `event.key` (e.g., "ctrl+c", "shift+up", "a")
6. **Modifiers**: Modifiers are part of the key name (e.g., "ctrl+c", not separate events)
7. **Timing Events**: Enable dispatcher to get `KeyClick`, `KeyDown`, `KeyUp` instead of raw `Key` events
8. **Terminal Cleanup**: Always use the context manager - it restores terminal state even if your code crashes

### Ideas for More Examples

- **Text editor**: Line-based editor with cursor movement and text insertion
- **Menu navigator**: Arrow keys to navigate, Enter to select
- **Game controls**: WASD movement with simultaneous key support
- **Form input**: Tab between fields, arrow keys for selection
- **Terminal UI**: Full TUI with panels, menus, and keyboard shortcuts
- **Vim-like modal editor**: Different key bindings for different modes
- **Command palette**: Ctrl+P style fuzzy search interface
- **File browser**: Navigate directories with arrow keys

## Troubleshooting

### Example doesn't start

- Make sure KEYBARD is installed: `uv pip install -e .`
- Check that Rich is installed: `uv pip install rich`

### Keys don't respond

- Ensure your terminal supports keyboard input
- Try running in a different terminal emulator
- Check that no other program is capturing keyboard input

### Some key combinations don't work

- Not all terminals support all key combinations
- Some combinations may be captured by your OS or terminal emulator
- Common conflicts: Ctrl+S (terminal freeze), Cmd+Q (quit application on macOS)
- Try the example to see which combinations your terminal supports

### Display issues

- Your terminal must support ANSI color codes
- Try resizing the terminal if the display appears corrupted
- Modern terminals (iTerm2, Alacritty, Windows Terminal, etc.) work best
- For best results, use a terminal with good Unicode support

## Platform Differences

KEYBARD works on Linux, macOS, and Windows, but some key combinations may differ:

- **macOS**: `Cmd` key instead of `Win` key, `Option` instead of `Alt` (though Alt works too)
- **Windows**: `Win` key for Windows-specific combinations
- **Linux**: Varies by desktop environment and window manager

The `key_display.py` example is the best way to discover what combinations work on your system.

## License

These examples are part of the KEYBARD project and are released under the MIT license.
