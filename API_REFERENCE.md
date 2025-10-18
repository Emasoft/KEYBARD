# KEYBARD API Reference

**Version**: 0.2.0a1 (Alpha)

This document provides the complete API reference for KEYBARD. All public APIs are fully type-annotated.

---

## Core Classes

### KeyboardReader

The main class for reading keyboard input from the terminal.

```python
class KeyboardReader:
    """Read keyboard input from the terminal.

    Supports blocking, non-blocking, and callback-based input modes.
    Automatically handles platform-specific terminal control.
    """
```

#### Constructor

```python
def __init__(
    self,
    *,
    debug: bool = False,
    driver: str | None = None,
    size: tuple[int, int] | None = None,
    callback: Callable[[Event], None] | None = None,
) -> None:
```

**Parameters**:

- `debug` (bool): Enable debug logging. Default: `False`
- `driver` (str | None): Force specific driver ("linux", "windows", "headless", "web"). Default: auto-detect
- `size` (tuple[int, int] | None): Override terminal size detection (width, height). Default: auto-detect
- `callback` (Callable | None): Callback function called for each event. Default: `None`

**Example**:

```python
# Basic usage
reader = KeyboardReader()

# With debug logging
reader = KeyboardReader(debug=True)

# With callback
def on_event(event):
    print(f"Event: {event.key}")
reader = KeyboardReader(callback=on_event)
```

---

#### read_key()

Read the next keyboard event (blocking).

```python
def read_key(self, timeout: float | None = None) -> Event | None:
    """Read next keyboard event.

    Args:
        timeout: Maximum seconds to wait. None = wait forever.

    Returns:
        Event object or None if timeout occurred.
    """
```

**Parameters**:

- `timeout` (float | None): Maximum seconds to wait for a key. `None` = wait forever. Default: `None`

**Returns**: `Event | None` - Event object or `None` if timeout

**Example**:

```python
# Wait forever for a key
event = reader.read_key()

# Wait up to 1 second
event = reader.read_key(timeout=1.0)
if event is None:
    print("Timeout!")
```

---

#### poll()

Get all pending events without blocking.

```python
def poll(self) -> list[Event]:
    """Get all pending keyboard events.

    Returns immediately with all available events.
    Returns empty list if no events are pending.

    Returns:
        List of Event objects (may be empty).
    """
```

**Returns**: `list[Event]` - List of pending events (empty if none)

**Example**:

```python
# Non-blocking check for events
events = reader.poll()
for event in events:
    print(f"Got: {event.key}")
```

---

#### run()

Run the event loop (blocks until stop() is called).

```python
def run(self) -> None:
    """Run event loop with callback.

    Requires a callback to be set in __init__.
    Blocks until stop() is called.

    Raises:
        ValueError: If no callback was provided.
    """
```

**Example**:

```python
def on_event(event):
    if event.key == "q":
        reader.stop()

reader = KeyboardReader(callback=on_event)
with reader:
    reader.run()  # Blocks here
```

---

#### start() / stop()

Manually start/stop the reader.

```python
def start(self) -> None:
    """Start the keyboard reader."""

def stop(self) -> None:
    """Stop the keyboard reader."""
```

**Example**:

```python
reader = KeyboardReader()
reader.start()
# ... use reader ...
reader.stop()

# Or use context manager (recommended)
with KeyboardReader() as reader:
    # ... use reader ...
    pass  # Automatically stopped
```

---

#### terminal_size

Get current terminal size.

```python
@property
def terminal_size(self) -> Size | None:
    """Get current terminal dimensions.

    Returns:
        Size object with .width and .height, or None if unknown.
    """
```

**Returns**: `Size | None` - Terminal dimensions or `None`

**Example**:

```python
size = reader.terminal_size
if size:
    print(f"Terminal: {size.width}x{size.height}")
```

---

## Event Types

All events inherit from the base `Event` class.

### Key

Keyboard key press event.

```python
class Key(Event):
    """A key was pressed."""
    key: str           # Normalized key name (e.g., "ctrl+c", "a", "up")
    character: str | None  # Original character if printable
```

**Attributes**:

- `key` (str): Normalized key name
- `character` (str | None): Original character if this was a printable key

**Key Name Format**:

- Regular keys: `"a"`, `"b"`, `"1"`, `"@"`, `"space"`
- Special keys: `"enter"`, `"escape"`, `"tab"`, `"backspace"`, `"delete"`
- Arrow keys: `"up"`, `"down"`, `"left"`, `"right"`
- Function keys: `"f1"`, `"f2"`, ... `"f12"`
- With modifiers: `"ctrl+c"`, `"alt+enter"`, `"shift+tab"`, `"ctrl+alt+delete"`

**Example**:

```python
if isinstance(event, Key):
    if event.key == "ctrl+c":
        break
    elif event.character:
        text += event.character
```

---

### Paste

Bracketed paste event (text was pasted, not typed).

```python
class Paste(Event):
    """Text was pasted."""
    text: str  # The pasted text content
```

**Attributes**:

- `text` (str): The complete pasted text

**Example**:

```python
if isinstance(event, Paste):
    print(f"Pasted: {event.text}")
    buffer += event.text
```

---

### Resize

Terminal window was resized.

```python
class Resize(Event):
    """Terminal was resized."""
    size: Size                          # New size in cells (width, height)
    pixel_size: tuple[int, int] | None  # New size in pixels (if available)
```

**Attributes**:

- `size` (Size): New terminal size in cells
- `pixel_size` (tuple[int, int] | None): New size in pixels (terminal-dependent)

**Example**:

```python
if isinstance(event, Resize):
    width, height = event.size.width, event.size.height
    print(f"Resized to {width}x{height}")
    redraw_ui()
```

---

### AppFocus

Terminal window gained focus.

```python
class AppFocus(Event):
    """Terminal gained focus."""
```

**Example**:

```python
if isinstance(event, AppFocus):
    print("Terminal focused")
    resume_animation()
```

---

### AppBlur

Terminal window lost focus.

```python
class AppBlur(Event):
    """Terminal lost focus."""
```

**Example**:

```python
if isinstance(event, AppBlur):
    print("Terminal blurred")
    pause_animation()
```

---

## Supporting Types

### Size

Terminal dimensions.

```python
class Size:
    """Terminal size in cells."""
    width: int   # Terminal width in characters
    height: int  # Terminal height in lines
```

**Attributes**:

- `width` (int): Terminal width in characters
- `height` (int): Terminal height in lines

**Example**:

```python
size = reader.terminal_size
if size:
    cells = size.width * size.height
    print(f"Terminal has {cells} cells")
```

---

## Key Name Reference

KEYBARD normalizes all key names to a consistent lowercase format with modifiers.

### Regular Characters

- Letters: `"a"` through `"z"`
- Numbers: `"0"` through `"9"`
- Symbols: `"space"`, `"@"`, `"#"`, `"$"`, `"["`, `"]"`, etc.

### Special Keys

- `"enter"`, `"return"`
- `"escape"`, `"esc"`
- `"tab"`
- `"backspace"`
- `"delete"`, `"del"`
- `"insert"`, `"ins"`
- `"home"`
- `"end"`
- `"pageup"`, `"pgup"`
- `"pagedown"`, `"pgdn"`

### Arrow Keys

- `"up"`, `"down"`, `"left"`, `"right"`

### Function Keys

- `"f1"` through `"f12"`
- Some terminals support `"f13"` through `"f24"`

### Modifiers

Modifiers are combined with `+`:

- `ctrl+KEY`: Ctrl modifier
- `alt+KEY`: Alt/Option modifier
- `shift+KEY`: Shift modifier
- `meta+KEY`: Meta/Cmd/Win modifier

**Examples**:

- `"ctrl+c"`, `"ctrl+s"`, `"ctrl+z"`
- `"alt+enter"`, `"alt+f4"`
- `"shift+tab"`, `"shift+up"`
- `"ctrl+shift+x"`, `"ctrl+alt+delete"`

**Note**: Not all modifier combinations are supported by all terminals. Use the `examples/key_display.py` demo to discover what works on your terminal.

---

## Type Annotations

KEYBARD is fully type-annotated. Enable type checking:

```python
from keybard import KeyboardReader
from keybard.events import Key, Paste, Resize

# Type checker will validate usage
reader: KeyboardReader = KeyboardReader()
event: Key | Paste | Resize | None = reader.read_key(timeout=1.0)
```

The `py.typed` marker is included in the package for PEP 561 compliance.

---

## Error Handling

KEYBARD follows a fail-fast approach:

- Invalid parameters raise `ValueError`
- Terminal errors propagate immediately
- No silent fallbacks or error suppression

**Example**:

```python
try:
    reader = KeyboardReader()
    reader.start()
    # ... use reader ...
except Exception as e:
    print(f"Terminal error: {e}")
    # Handle or exit
```

---

## Environment Variables

### KEYBARD_ALLOW_SIGNALS

Control signal generation for Ctrl+C.

- **Default**: Signals disabled (Ctrl+C is a regular key)
- **Set to any value**: Restore default signal behavior (Ctrl+C sends SIGINT)

**Example**:

```bash
# Allow Ctrl+C to send SIGINT
export KEYBARD_ALLOW_SIGNALS=1
python my_app.py
```

---

## Platform Notes

### Linux/macOS

- Uses `termios` and `tty` for terminal control
- Signal handlers: SIGWINCH (resize), SIGTSTP (suspend), SIGCONT (resume)
- Best support for all features

### Windows

- Uses Windows Console API
- Some key combinations differ from Unix
- Full keyboard support, limited signal handling

### Terminals

Tested on:

- **Linux**: GNOME Terminal, Alacritty, Kitty, Konsole
- **macOS**: Terminal.app, iTerm2, Alacritty
- **Windows**: Windows Terminal, cmd.exe, PowerShell

---

## Thread Safety

`KeyboardReader` is **not thread-safe**. Use from a single thread only.

---

## Performance

- Non-blocking `poll()` is optimized for game loops and real-time apps
- Parallel test execution: 322 tests in 0.84s (16 workers)
- Low overhead: Minimal CPU usage when idle

---

## Version

This API reference is for **KEYBARD 0.2.0a1 (Alpha)**.

For the latest version, see [CHANGELOG.md](CHANGELOG.md).

---

## See Also

- [README.md](README.md) - Getting started and common use cases
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide
- [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md) - Credits and origins
- [examples/](examples/) - Working code examples
