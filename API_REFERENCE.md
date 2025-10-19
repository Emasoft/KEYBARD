# KEYBARD API Reference

**Version**: 0.3.0a1 (Alpha)

This document provides the complete API reference for KEYBARD. All public APIs are fully type-annotated and documented.

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
    use_dispatcher: bool = False,
    dispatcher_config: DispatcherConfig | None = None,
) -> None:
```

**Parameters**:

- `debug` (bool): Enable debug logging. Default: `False`
- `driver` (str | None): Force specific driver ("linux", "windows", "headless", "web"). Default: auto-detect
- `size` (tuple[int, int] | None): Override terminal size detection (width, height). Default: auto-detect
- `callback` (Callable | None): Callback function called for each event. Default: `None`
- `use_dispatcher` (bool): Enable timing-based event dispatcher. Default: `False`
- `dispatcher_config` (DispatcherConfig | None): Configuration for dispatcher. Default: `None` (uses defaults)

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
    """Run the event loop (blocks until stop() is called).

    This method requires a callback to be set in __init__.
    It's useful for callback-based architecture where you want
    all event handling to happen in the callback.

    Returns:
        None (blocks until stop() is called from within callback or another thread)

    Raises:
        ValueError: If no callback was provided in __init__

    Example:
        ```python
        def on_event(event):
            print(f"Event: {event}")
            if event.key == "q":
                reader.stop()

        reader = KeyboardReader(callback=on_event)
        with reader:
            reader.run()  # Blocks here, callback handles events
        ```
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

#### start()

Start the keyboard reader and put terminal into raw mode.

```python
def start(self) -> None:
    """Start reading keyboard/mouse input from the terminal.

    Returns:
        None
    """
```

**Example**:

```python
reader = KeyboardReader()
reader.start()
# ... use reader ...
reader.stop()
```

---

#### stop()

Stop the keyboard reader and restore terminal to normal mode.

```python
def stop(self) -> None:
    """Stop reading and restore terminal to normal mode.

    Returns:
        None
    """
```

**Example**:

```python
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


### Timing-Based Keyboard Events

**Available when using the dispatcher** (set `use_dispatcher=True` in KeyboardReader).

The timing-based event model transforms raw `Key` events into higher-level events based on timing and key repetition behavior. This allows distinguishing between quick taps and prolonged holds.

See [README.md - Timing-Based Event Model](README.md#timing-based-event-model) for usage examples and limitations.

---

### KeyClick

Key was pressed and released quickly (within delta threshold).

```python
class KeyClick(Event):
    """Quick key press and release."""
    key: str              # Normalized key name
    character: str | None # Original character if printable
    duration: float       # Time between press and release (seconds)
```

**Attributes**:

- `key` (str): Normalized key name
- `character` (str | None): Original character if printable
- `duration` (float): Time in seconds between press and release

**Example**:

```python
if isinstance(event, KeyClick):
    if event.key == "space":
        print("Quick tap: Jump!")
```

---

### KeyDown

Key has been held down past the delta threshold.

```python
class KeyDown(Event):
    """Key held past threshold."""
    key: str              # Normalized key name
    character: str | None # Original character if printable
    hold_time: float      # Time key has been held (seconds)
    repeat_count: int     # Number of repeats (0 for initial, >0 for repeats)
```

**Attributes**:

- `key` (str): Normalized key name
- `character` (str | None): Original character if printable
- `hold_time` (float): Time in seconds the key has been held
- `repeat_count` (int): Number of repeats received (0 for initial KeyDown)

**Example**:

```python
if isinstance(event, KeyDown):
    if event.key == "space" and event.repeat_count == 0:
        print("Holding space: Charging jump...")
```

---

### KeyUp

Key was released after a KeyDown event.

```python
class KeyUp(Event):
    """Key released after being held."""
    key: str               # Normalized key name
    character: str | None  # Original character if printable
    total_duration: float  # Total time key was held (seconds)
```

**Attributes**:

- `key` (str): Normalized key name
- `character` (str | None): Original character if printable
- `total_duration` (float): Total time in seconds the key was held

**Example**:

```python
if isinstance(event, KeyUp):
    if event.key == "space":
        print(f"Released: Super jump! (charged for {event.total_duration:.1f}s)")
```

---

### ComboClick

**FUTURE FEATURE - NOT YET IMPLEMENTED**

Multiple keys pressed together and all released quickly.

```python
class ComboClick(Event):
    """Quick multi-key press (future feature)."""
    keys: list[str]        # List of key names in the combo
    primary_key: str       # Last key pressed (usually non-modifier)
    character: str | None  # Original character if applicable
    duration: float        # Time from first press to last release
```

**Status**: Event type defined but not currently emitted by dispatcher. Modifier combinations (Ctrl+C, etc.) come from the terminal parser as atomic Key events.

---

### ComboKeyDown

**FUTURE FEATURE - NOT YET IMPLEMENTED**

Multiple keys pressed together and held past delta.

```python
class ComboKeyDown(Event):
    """Multi-key hold (future feature)."""
    keys: list[str]        # List of key names in the combo
    primary_key: str       # Last key pressed (usually non-modifier)
    character: str | None  # Original character if applicable
    hold_time: float       # Time since first key press
```

**Status**: Event type defined but not currently emitted by dispatcher. Modifier combinations come from the terminal parser as atomic Key events.

---

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
---

### DispatcherConfig

Configuration for the timing-based event dispatcher.

```python
class DispatcherConfig:
    """Configuration for KeyEventDispatcher."""
    delta: float = 1.0              # Time threshold for click vs hold (seconds)
    release_timeout: float = 0.15   # Time to wait for repeat to detect release (seconds)
    emit_repeats: bool = False      # Whether to emit KeyDown on each repeat
    repeat_interval: float = 0.05   # Min time between repeat emissions (seconds)
```

**Attributes**:

- `delta` (float): Time threshold to distinguish click from hold. Default: 1.0 seconds
- `release_timeout` (float): Time to wait for key repeat before inferring release. Default: 0.15 seconds
- `emit_repeats` (bool): Whether to emit additional KeyDown events on each key repeat. Default: False
- `repeat_interval` (float): Minimum time between repeat event emissions (when `emit_repeats=True`). Default: 0.05 seconds

**Example**:

```python
from keybard import KeyboardReader
from keybard.dispatcher import DispatcherConfig

config = DispatcherConfig(
    delta=0.5,           # 500ms threshold
    emit_repeats=True,   # Emit on each repeat
    repeat_interval=0.1  # 100ms between repeats
)

with KeyboardReader(use_dispatcher=True, dispatcher_config=config) as reader:
    # Use timing-based events
    pass
```

**See Also**: [README.md - Timing-Based Event Model](README.md#timing-based-event-model) for usage examples.

---

### KeyEventDispatcher

The dispatcher that transforms raw Key events into timing-based events.

```python
class KeyEventDispatcher:
    """Dispatcher that transforms immediate key events into timing-based events.

    This dispatcher receives raw Key events from the parser and emits:
    - KeyClick: Press + release within delta threshold
    - KeyDown: Key held past delta (emitted after waiting)
    - KeyUp: Key released after KeyDown

    The dispatcher buffers events and uses timers to determine the appropriate
    event type based on timing. This allows distinguishing between quick taps
    and prolonged holds.

    Modifier combinations (Ctrl+C, Shift+A, etc.) are received from the terminal
    parser as atomic Key events (e.g., key="ctrl+c") and are treated as single keys.

    Args:
        callback: Function to call with timed events
        config: Configuration for timing thresholds
    """
```

**Note**: You typically don't instantiate this directly - use `KeyboardReader(use_dispatcher=True)` instead.

---

#### feed()

Feed an event to the dispatcher for processing.

```python
def feed(self, event: Event) -> None:
    """Feed an event to the dispatcher.

    Key events are processed through the timing state machine.
    All other events are passed through immediately.

    Args:
        event: Event from the parser (Key, Paste, Resize, etc.)

    Returns:
        None
    """
```

**Parameters**:

- `event` (Event): Event to process (Key events are transformed, others pass through)

**Returns**: `None`

---

#### stop()

Stop the dispatcher and cancel all pending timers.

```python
def stop(self) -> None:
    """Stop the dispatcher and cancel all pending timers.

    Call this when shutting down to ensure clean cleanup.

    Returns:
        None
    """
```

**Returns**: `None`

**Example**:

```python
# Usually called automatically by KeyboardReader.stop()
# But if using dispatcher manually:
dispatcher.stop()
```

---

## Utility Functions

### format_key()

Format a key identifier for display in the UI.

```python
def format_key(key: str) -> str:
    """Format a key identifier for display in the UI.

    Converts internal key names to human-friendly display formats, using
    Unicode symbols for common keys (arrows, enter, backspace) and printable
    characters where appropriate.

    Args:
        key: The key identifier (e.g., "ctrl+c", "up", "enter", "exclamation_mark")

    Returns:
        Formatted display string (e.g., "↑" for "up", "⏎" for "enter", "!" for "exclamation_mark")
    """
```

**Parameters**:

- `key` (str): The key identifier to format

**Returns**: `str` - Human-friendly display string with Unicode symbols

**Example**:

```python
from keybard.keys import format_key

# Format arrow keys
print(format_key("up"))      # → "↑"
print(format_key("down"))    # → "↓"
print(format_key("left"))    # → "←"
print(format_key("right"))   # → "→"

# Format special keys
print(format_key("enter"))   # → "⏎"
print(format_key("escape"))  # → "esc"

# Format punctuation
print(format_key("exclamation_mark"))  # → "!"
print(format_key("at"))                # → "@"
```

---

### key_to_character()

Convert a key identifier to its character representation.

```python
def key_to_character(key: str) -> str | None:
    """Given a key identifier, return the character associated with it.

    Args:
        key: The key identifier.

    Returns:
        A key if one could be found, otherwise `None`.
    """
```

**Parameters**:

- `key` (str): The key identifier

**Returns**: `str | None` - The character, or `None` if the key has no character representation

**Example**:

```python
from keybard.keys import key_to_character

# Get character from key name
print(key_to_character("a"))              # → "a"
print(key_to_character("space"))          # → " "
print(key_to_character("exclamation_mark")) # → "!"

# Keys with modifiers have no character
print(key_to_character("ctrl+c"))         # → None

# Special keys have no character
print(key_to_character("enter"))          # → None
print(key_to_character("escape"))         # → None
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

This API reference is for **KEYBARD 0.3.0a1 (Alpha)**.

For the latest version, see [CHANGELOG.md](CHANGELOG.md).

---

## See Also

- [README.md](README.md) - Getting started and common use cases
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide
- [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md) - Credits and origins
- [examples/](examples/) - Working code examples
