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

### key_display.py - Comprehensive Key State Tracker

A visual demonstration of KEYBARD's keyboard input detection capabilities showing not just
what keys are pressed, but tracking their states (press/hold/release).

**What it demonstrates:**

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
# From the repository root
uv run examples/key_display.py

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

- Uses `KeyboardReader.poll()` for non-blocking event retrieval
- Tracks key state with `KeyTracker` class monitoring press/hold/release
- Infers KEY-UP events using 150ms timeout (no events = key released)
- Separates modifiers from base keys for clearer display
- Shows millisecond-precision timestamps for timing analysis
- Displays currently held keys at bottom of screen
- Updates display at 100 FPS (10ms poll interval) for responsive feedback
- Uses Rich library for beautiful table formatting and colors
- Color codes: CLICK=green, KEY-DOWN=yellow, KEY-UP=red

## Creating Your Own Examples

KEYBARD makes it easy to create interactive terminal applications. Here's a minimal example:

```python
#!/usr/bin/env python3
from keybard import KeyboardReader
from keybard.events import Key

# Create reader
reader = KeyboardReader()

# Start reading keys
with reader:
    while True:
        # Get all pending events (non-blocking)
        events = reader.poll()

        for event in events:
            if isinstance(event, Key):
                print(f"Key pressed: {event.key}")

                if event.key == "q":
                    exit(0)
```

### Key Concepts

1. **Non-blocking input**: Use `poll()` to get all pending events without blocking
2. **Blocking input**: Use `read_key(timeout=...)` to wait for a single key
3. **Event types**: Check `isinstance(event, Key)` to filter key events
4. **Key names**: Access normalized key names via `event.key` (e.g., "ctrl+c", "shift+up")
5. **Context manager**: Use `with reader:` to automatically start/stop the reader
6. **Modifiers**: Modifiers are part of the key name (e.g., "ctrl+c", not separate events)

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
