# KEYBARD

<p align="center">
  <img src="assets/keybard_logo_hires.png" alt="KEYBARD Logo" width="400">
</p>

**Cross-platform keyboard input library for Python terminals**

---

## Project Information

- **Version**: 0.2.0a1 ⚠️ **ALPHA** - Under active development
- **Python**: 3.12+
- **Platforms**: Linux, macOS, Windows
- **License**: MIT
- **Type Annotations**: Fully typed (py.typed included)

### ⚠️ Alpha Software Warning

KEYBARD is currently in **alpha** status. The API may change in future releases. Use in production at your own risk. Please report any issues you encounter.

### What is KEYBARD?

KEYBARD is a lightweight, keyboard-only input library for Python terminal applications. It provides immediate, character-by-character keyboard input with full support for:

- ✓ Special keys (arrows, function keys, home/end, etc.)
- ✓ Modifier combinations (Ctrl+C, Alt+Enter, Shift+Tab, etc.)
- ✓ Paste detection (distinguishes pasted vs typed text)
- ✓ Terminal events (resize, focus/blur)
- ✓ Cross-platform support (Linux, macOS, Windows)
- ✓ Battle-tested XTerm parser (extracted from [Textual](https://github.com/Textualize/textual))

**Note**: KEYBARD is keyboard-only. No mouse support. For full TUI features including mouse, use [Textual](https://github.com/Textualize/textual) directly.

---

## Installation

### From GitHub (Development)

KEYBARD is not yet available on PyPI. Install from GitHub:

```bash
# Clone the repository
gh repo clone Emasoft/KEYBARD
cd KEYBARD

# Sync dependencies using uv
uv sync

# Build the wheel
uv build

# The wheel will be in dist/keybard-0.2.0a1-py3-none-any.whl
```

### Installing in Your Project

#### Option 1: Install Built Wheel

Add KEYBARD to your project using the built wheel:

```bash
# Navigate to your project
cd /path/to/your/project

# Add KEYBARD wheel as a dependency
uv add /path/to/KEYBARD/dist/keybard-0.2.0a1-py3-none-any.whl

# Or install directly in your venv
uv pip install /path/to/KEYBARD/dist/keybard-0.2.0a1-py3-none-any.whl
```

#### Option 2: Install as Editable (Development)

For development, install KEYBARD in editable mode to see changes immediately:

```bash
# Clone and navigate to KEYBARD
gh repo clone Emasoft/KEYBARD
cd KEYBARD

# Create/activate virtual environment
uv venv --python 3.12
source .venv/bin/activate  # On macOS/Linux
# or: .venv\Scripts\activate  # On Windows

# Install in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Or just editable without dev deps
uv pip install -e .
```

Now changes to the source code are immediately reflected without reinstalling.

Then import in your Python code:

```python
from keybard import KeyboardReader
```

---

## Common Use Cases

### 1. To Detect a Single Key Press

**Use Case**: Detect when user presses any key and show what was pressed.

**Input**: User presses a key (e.g., 'a', Enter, Ctrl+C, Arrow Up)
**Output**: The normalized key name (e.g., "a", "enter", "ctrl+c", "up")

**How to do it**:

```python
from keybard import KeyboardReader

with KeyboardReader() as reader:
    event = reader.read_key()
    if event:
        print(f"You pressed: {event.key}")
```

### 2. To Build an Interactive Menu

**Use Case**: Navigate menu options with arrow keys, select with Enter.

**Input**: Up/Down arrows to move, Enter to select, 'q' to quit
**Output**: Selected menu option

**How to do it**:

```python
from keybard import KeyboardReader

options = ["Start Game", "Settings", "Quit"]
selected = 0

with KeyboardReader() as reader:
    while True:
        # Display menu
        print("\033[2J\033[H")  # Clear screen
        for i, option in enumerate(options):
            prefix = "→ " if i == selected else "  "
            print(f"{prefix}{option}")

        # Handle input
        event = reader.read_key()

        if event.key == "up" and selected > 0:
            selected -= 1
        elif event.key == "down" and selected < len(options) - 1:
            selected += 1
        elif event.key == "enter":
            print(f"\nSelected: {options[selected]}")
            break
        elif event.key == "q":
            break
```

### 3. To Handle Keyboard Shortcuts

**Use Case**: Implement Ctrl+S to save, Ctrl+Q to quit, etc.

**Input**: Ctrl+S, Ctrl+Q, Ctrl+Z, etc.
**Output**: Execute corresponding action

**How to do it**:

```python
from keybard import KeyboardReader

with KeyboardReader() as reader:
    while True:
        event = reader.read_key()

        if event.key == "ctrl+s":
            print("💾 Saving...")
            # Your save logic here
        elif event.key == "ctrl+q":
            print("👋 Quitting...")
            break
        elif event.key == "ctrl+z":
            print("↩️  Undo")
            # Your undo logic here
```

### 4. To Process Multiple Keys Without Blocking

**Use Case**: Game loop that needs to check for input without waiting.

**Input**: Multiple rapid key presses (e.g., WASD for movement)
**Output**: Process all keys while maintaining 60 FPS

**How to do it**:

```python
from keybard import KeyboardReader
import time

with KeyboardReader() as reader:
    running = True
    player_x, player_y = 0, 0

    while running:
        # Non-blocking: get ALL pending keys
        events = reader.poll()

        for event in events:
            if event.key == "w":
                player_y -= 1
            elif event.key == "s":
                player_y += 1
            elif event.key == "a":
                player_x -= 1
            elif event.key == "d":
                player_x += 1
            elif event.key == "q":
                running = False

        # Game logic here
        print(f"\rPosition: ({player_x}, {player_y})", end="", flush=True)

        # Maintain frame rate
        time.sleep(1/60)  # 60 FPS
```

### 5. To Detect Pasted Text

**Use Case**: Distinguish between typed and pasted text.

**Input**: User types "hello" OR pastes "hello world"
**Output**: Different handling for typed vs pasted text

**How to do it**:

```python
from keybard import KeyboardReader
from keybard.events import Key, Paste

text = ""

with KeyboardReader() as reader:
    while True:
        event = reader.read_key()

        if isinstance(event, Key):
            if event.key == "ctrl+c":
                break
            elif event.character:
                text += event.character
                print(f"Typed: {event.character}")

        elif isinstance(event, Paste):
            text += event.text
            print(f"Pasted: {repr(event.text)}")
```

### 6. To Handle Terminal Resize

**Use Case**: Redraw UI when terminal is resized.

**Input**: User resizes terminal window
**Output**: Get new dimensions and redraw

**How to do it**:

```python
from keybard import KeyboardReader
from keybard.events import Resize

with KeyboardReader() as reader:
    while True:
        event = reader.read_key()

        if isinstance(event, Resize):
            width, height = event.size.width, event.size.height
            print(f"Terminal resized to {width}x{height}")
            # Redraw your UI here
```

### 7. To Use Callback-Based Architecture

**Use Case**: Event-driven application with callback for each key.

**Input**: Any key press
**Output**: Callback function called automatically

**How to do it**:

```python
from keybard import KeyboardReader

def on_key_press(event):
    print(f"Callback received: {event.key}")
    if event.key == "q":
        reader.stop()

reader = KeyboardReader(callback=on_key_press)
with reader:
    reader.run()  # Blocks here, calls callback for each event
```

---

## Timing-Based Event Model

KEYBARD v0.2.0+ includes an optional **timing-based event dispatcher** that transforms raw key events into higher-level events based on how long keys are held:

### Event Types

- **KeyClick**: Key pressed and released quickly (within delta threshold, default 1s)
- **KeyDown**: Key held beyond the delta threshold (emitted after waiting)
- **KeyUp**: Key released after a KeyDown event

This model allows you to distinguish between quick taps and prolonged holds, enabling different behaviors for short vs long key presses.

### Why Use This?

The timing-based model is useful when you want to:
- Trigger different actions for quick taps vs holding a key
- Implement vim-style holds (e.g., hold 'j' to scroll continuously)
- Create responsive UIs that react to hold duration
- Detect when users intentionally hold keys vs accidentally tap them

### Basic Usage

Enable the dispatcher when creating a KeyboardReader:

```python
from keybard import KeyboardReader
from keybard.dispatcher import DispatcherConfig
from keybard.events import KeyClick, KeyDown, KeyUp

# Configure timing thresholds
config = DispatcherConfig(
    delta=1.0,              # Click vs hold threshold (seconds)
    release_timeout=0.15,   # Time to wait for repeat to detect release
    emit_repeats=False,     # Whether to emit KeyDown on each repeat
)

with KeyboardReader(use_dispatcher=True, dispatcher_config=config) as reader:
    while True:
        event = reader.read_key()

        if isinstance(event, KeyClick):
            print(f"Quick tap: {event.key} (duration: {event.duration:.2f}s)")

        elif isinstance(event, KeyDown):
            print(f"Holding: {event.key} (hold_time: {event.hold_time:.2f}s)")

        elif isinstance(event, KeyUp):
            print(f"Released: {event.key} (total: {event.total_duration:.2f}s)")
```

### Configuration Options

The `DispatcherConfig` class allows you to customize timing behavior:

```python
from keybard.dispatcher import DispatcherConfig

config = DispatcherConfig(
    delta=1.0,              # Time threshold for click vs hold (default: 1.0s)
    release_timeout=0.15,   # Time to detect key release (default: 0.15s)
    emit_repeats=False,     # Emit KeyDown on each repeat (default: False)
    repeat_interval=0.05,   # Min time between repeat emissions (default: 0.05s)
)
```

### Example: Different Actions for Click vs Hold

```python
from keybard import KeyboardReader
from keybard.dispatcher import DispatcherConfig
from keybard.events import KeyClick, KeyDown, KeyUp

config = DispatcherConfig(delta=0.5)  # 0.5 second threshold

with KeyboardReader(use_dispatcher=True, dispatcher_config=config) as reader:
    while True:
        event = reader.read_key()

        if isinstance(event, KeyClick) and event.key == "space":
            print("Quick tap: Jump!")

        elif isinstance(event, KeyDown) and event.key == "space":
            print("Holding space: Charging jump...")

        elif isinstance(event, KeyUp) and event.key == "space":
            print(f"Released: Super jump! (charged for {event.total_duration:.1f}s)")

        elif isinstance(event, KeyClick) and event.key == "q":
            break
```

### Repeat Events

When `emit_repeats=True`, the dispatcher emits additional `KeyDown` events on each key repeat during a hold:

```python
config = DispatcherConfig(delta=0.5, emit_repeats=True, repeat_interval=0.1)

with KeyboardReader(use_dispatcher=True, dispatcher_config=config) as reader:
    while True:
        event = reader.read_key()

        if isinstance(event, KeyDown):
            if event.repeat_count == 0:
                print(f"Started holding: {event.key}")
            else:
                print(f"Still holding: {event.key} (repeat #{event.repeat_count})")
```

### Important Limitation: Terminal Key Repetition

**Critical to understand:** Terminal input only provides key press events, never explicit key release events. The dispatcher infers key state from OS/terminal key repetition behavior:

#### Keys WITH Repetition (letters, numbers, arrows, etc.)
- Holding generates rapid repeat events (~30/sec, OS-configured)
- ✅ Can detect KeyDown (repeats start) and KeyUp (repeats stop)
- ✅ Works as expected with timing-based events

#### Keys WITHOUT Repetition (Escape, modifiers alone, some F-keys)
- Holding generates NO additional events (only initial press)
- ⚠️ **Will always emit KeyClick** after delta timeout, even if still physically held
- ⚠️ Cannot detect true hold duration for these keys
- This is a fundamental terminal input limitation, not a library bug

#### Modifier Combinations
- Modifiers alone: Usually no repetition (single event only)
- Modifiers + repeating key: The combo repeats (e.g., Shift+A → AAAAA)
- ✅ Can detect KeyDown/KeyUp for combos with repeating keys

**Workaround:** For keys without repetition, use raw `Key` events (default mode without dispatcher) or accept that they will emit KeyClick after the delta timeout regardless of hold duration.

### Compatibility

The timing-based dispatcher is **optional** and **fully backward compatible**:

- **Without dispatcher** (default): You receive raw `Key` events immediately
- **With dispatcher**: You receive `KeyClick`, `KeyDown`, `KeyUp` events based on timing and repetition

Non-key events (Paste, Resize, etc.) are always passed through unchanged.

### Examples

See these examples for practical demonstrations:

- `examples/timed_keys.py` - Comprehensive timing-based events demo
- `examples/key_display.py --use-dispatcher` - Key display with dispatcher option

---

## Examples

The `examples/` directory contains working demonstrations:

### Quickstart Example

```bash
uv run examples/quickstart.py
```

Minimal 30-line example showing basic usage.

### Key Display Demo

```bash
uv run examples/key_display.py
```

Comprehensive demonstration showing:
- All key types (regular, function, special, arrows)
- Modifier combinations (Ctrl, Alt, Shift, Meta)
- Key state tracking (press, hold, release)
- Real-time event history with timestamps

Perfect for discovering what key combinations your terminal supports!

See `examples/README.md` for detailed documentation.

---

## API Reference

For complete API documentation including all classes, methods, and parameters, see:

**[API_REFERENCE.md](API_REFERENCE.md)** *(Generated from docstrings)*

Quick reference:

- **KeyboardReader**: Main class for reading keyboard input
  - `read_key(timeout=None)`: Read next key (blocking)
  - `poll()`: Get all pending keys (non-blocking)
  - `run()`: Run event loop with callback
  - `terminal_size`: Get current terminal dimensions

- **Event Types**:
  - `Key`: Keyboard key press (`.key` attribute) - default mode
  - `KeyClick`: Quick key press/release (`.key`, `.duration`) - timing mode
  - `KeyDown`: Key held past threshold (`.key`, `.hold_time`, `.repeat_count`) - timing mode
  - `KeyUp`: Key released after hold (`.key`, `.total_duration`) - timing mode
  - `Paste`: Pasted text (`.text` attribute)
  - `Resize`: Terminal resized (`.size` attribute)
  - `AppFocus`/`AppBlur`: Terminal focus events

- **Key Names**: Normalized format like `"ctrl+c"`, `"shift+up"`, `"alt+enter"`, `"f1"`, etc.

---

## Testing

```bash
# Run all tests (parallel, 16 workers)
uv run pytest -n 16 --dist=loadgroup

# Run with coverage
uv run pytest --cov=keybard --cov-report=term-missing

# Run specific test
uv run pytest tests/test_xterm_parser.py -v
```

**Test Status**: ✅ 337 passed, 2 skipped (includes timing dispatcher tests)

---

## Development

Want to contribute? See **[CONTRIBUTING.md](CONTRIBUTING.md)** for:
- Development setup
- Code standards
- Testing requirements
- Pull request process

Quick setup:

```bash
# Clone and setup
gh repo clone Emasoft/KEYBARD
cd KEYBARD
uv sync
uv run pre-commit install

# Quality checks
uv run ruff format --line-length=320 src/ tests/
uv run ruff check --fix
uv run mypy src/keybard
uv run pytest
```

---

## Roadmap

KEYBARD is under active development. Each item below is a specific, self-contained feature that can be contributed individually.

### Timing-Based Events (v0.3.0+)

- [x] Single key timing detection (KeyClick, KeyDown, KeyUp)
- [ ] Implement simultaneous key press detection (buffer keys within time window)
- [ ] Add ComboClick event emission for multi-key quick press/release
- [ ] Add ComboKeyDown event emission for multi-key holds
- [ ] Support configurable combo_window parameter in DispatcherConfig
- [ ] Add combo disambiguation logic (e.g., Ctrl first vs C first)
- [ ] Add tests for 2-key, 3-key, and 4+ key combinations
- [ ] Document combo detection limitations with terminal input

### Key State Tracking (v0.3.0+)

- [ ] Add `.is_pressed(key: str) -> bool` method to KeyboardReader
- [ ] Add `.pressed_keys() -> set[str]` method to KeyboardReader
- [ ] Implement key state tracking dict internally (key → press time)
- [ ] Add `.is_ctrl_pressed()`, `.is_alt_pressed()`, `.is_shift_pressed()` helpers
- [ ] Add `.get_modifiers() -> set[str]` method (returns active modifiers)
- [ ] Add key state change callbacks (on_key_press, on_key_release)
- [ ] Implement key state persistence across read_key() calls
- [ ] Add thread-safe locking for key state dict access

### Event Processing & Filtering (v0.3.0+)

- [ ] Add EventFilter base class with filter() method
- [ ] Implement DebounceFilter (ignore repeated events within time window)
- [ ] Implement ModifierFilter (only pass events with specific modifiers)
- [ ] Implement KeySequenceFilter (detect multi-key patterns like "gg", "jk")
- [ ] Add event transformation API (Event → Event mapping)
- [ ] Add event middleware chain support (multiple filters in sequence)
- [ ] Implement event rate limiting (max events per second)
- [ ] Add event logging filter for debugging

### Key Mapping & Remapping (v0.4.0+)

- [ ] Add KeyMapper class with add_mapping(from_key, to_key) method
- [ ] Support key-to-key remapping (e.g., "capslock" → "ctrl")
- [ ] Support key-to-sequence remapping (e.g., "f1" → "ctrl+s")
- [ ] Add context-aware mappings (different maps for different app states)
- [ ] Implement mapping file loading (.keybard or .json format)
- [ ] Add hot-reload support for mapping files
- [ ] Validate remapped key names against Keys enum
- [ ] Add mapping conflict detection and warnings

### Input Validation & Constraints (v0.4.0+)

- [ ] Add InputValidator base class with validate(event) method
- [ ] Implement AlphanumericValidator (only allow letters/numbers)
- [ ] Implement NumericValidator (only allow digits)
- [ ] Implement RegexValidator (validate against custom pattern)
- [ ] Add max_length constraint for text accumulation
- [ ] Add allowed_keys and blocked_keys filter validators
- [ ] Implement composable validators (AND, OR, NOT logic)
- [ ] Add validation error event type with reason

### Configuration & Settings (v0.4.0+)

- [ ] Add per-event-type timeout configuration
- [ ] Add configurable buffer sizes for event queue
- [ ] Implement settings save/load from JSON or TOML
- [ ] Add runtime configuration updates (without restart)
- [ ] Support environment variable overrides for all settings
- [ ] Add configuration validation with helpful error messages
- [ ] Implement config profiles (dev, prod, debug presets)
- [ ] Add config migration helpers for version upgrades

### Platform-Specific Enhancements (v0.4.0+)

#### Windows
- [ ] Detect Windows Terminal vs CMD vs PowerShell
- [ ] Add Windows Console virtual terminal sequences support
- [ ] Implement proper Windows Input Method Editor (IME) support
- [ ] Add Windows-specific key name normalization (e.g., Win key)
- [ ] Support Windows clipboard integration events
- [ ] Add Windows console color capability detection

#### Linux/Unix
- [ ] Add explicit support for Kitty keyboard protocol
- [ ] Implement enhanced key reporting mode detection
- [ ] Support tmux passthrough sequences
- [ ] Add detection for WSL1 vs WSL2 vs native Linux
- [ ] Implement proper locale-aware character mapping
- [ ] Add systemd notification support for long-running apps

#### macOS
- [ ] Add Option/Command key distinction (left vs right)
- [ ] Implement proper macOS dead key support
- [ ] Add detection for Terminal.app vs iTerm2 vs Alacritty
- [ ] Support macOS accessibility permissions detection
- [ ] Add macOS-specific keyboard layout detection

### Terminal Compatibility (v0.4.0+)

- [ ] Add comprehensive terminal capability database
- [ ] Implement terminfo query and parsing
- [ ] Add automatic feature detection via CSI queries
- [ ] Support graceful degradation for unsupported features
- [ ] Add terminal-specific workarounds registry
- [ ] Implement version detection for known terminals
- [ ] Add warnings for known buggy terminal versions
- [ ] Create terminal compatibility test suite

### Developer Tools & Debugging (Ongoing)

- [ ] Add verbose debug mode with detailed event logging
- [ ] Implement event timeline visualization (ASCII art)
- [ ] Add performance counters (events/sec, latency percentiles)
- [ ] Create interactive key code inspector tool
- [ ] Add memory profiling for long-running sessions
- [ ] Implement event capture/replay for testing
- [ ] Add assertion helpers for testing key sequences
- [ ] Create minimal reproducible example generator

### Documentation & Examples (Ongoing)

- [ ] Add example: Build a CLI text editor with vim keybindings
- [ ] Add example: Interactive menu system with arrow navigation
- [ ] Add example: Real-time game input handling (WASD movement)
- [ ] Add example: Password input with masked display
- [ ] Add example: Autocomplete with tab completion
- [ ] Add example: Multi-pane terminal UI with focus management
- [ ] Add tutorial: Migrating from input()/getpass()
- [ ] Add tutorial: Integrating with asyncio event loops
- [ ] Create video walkthrough of common use cases
- [ ] Add troubleshooting guide for common issues

### Testing Infrastructure (Ongoing)

- [ ] Add headless testing mode with simulated input
- [ ] Create test fixture for injecting key events
- [ ] Add property-based tests with Hypothesis
- [ ] Implement terminal emulator integration tests
- [ ] Add performance regression tests
- [ ] Create test coverage report automation
- [ ] Add mutation testing for critical paths
- [ ] Implement fuzz testing for parser robustness

### Type Safety & IDE Support (Ongoing)

- [ ] Add strict type annotations to all internal functions
- [ ] Create comprehensive .pyi stub files
- [ ] Add type guards for event type narrowing
- [ ] Implement Protocol classes for plugin interfaces
- [ ] Add TypedDict for configuration objects
- [ ] Create generic types for event handlers
- [ ] Add overload signatures for polymorphic methods
- [ ] Test type checking with mypy strict mode

### Performance Optimizations (v0.5.0+)

- [ ] Profile hot paths and optimize bottlenecks
- [ ] Implement zero-copy parsing where possible
- [ ] Add event pooling to reduce allocations
- [ ] Optimize key name string interning
- [ ] Add fast path for common key sequences
- [ ] Implement batched event processing option
- [ ] Add lazy initialization for unused features
- [ ] Create performance benchmarking suite

### Advanced Input Features (v1.0.0+)

#### Key Chords & Sequences
- [ ] Detect Emacs-style key chords (C-x C-s)
- [ ] Support Vi-style key sequences (gg, dd, yy)
- [ ] Add configurable chord timeout
- [ ] Implement partial chord feedback
- [ ] Support context-dependent chord interpretation
- [ ] Add chord conflict resolution

#### Macro System
- [ ] Record key sequences to macros
- [ ] Replay macros with configurable speed
- [ ] Save/load macros to files
- [ ] Support macro variables and interpolation
- [ ] Add conditional macro execution
- [ ] Implement macro loops and repetition

#### Text Input Helpers
- [ ] Add line editor with history (readline-like)
- [ ] Implement word completion system
- [ ] Add fuzzy search/filtering for suggestions
- [ ] Support multi-line text input
- [ ] Add undo/redo stack for text editing
- [ ] Implement clipboard integration

### Accessibility Features (v1.0.0+)

- [ ] Add screen reader event announcements
- [ ] Implement configurable key repeat rates
- [ ] Support sticky keys (hold modifiers across presses)
- [ ] Add toggle keys (caps lock, num lock indicators)
- [ ] Implement filter keys (ignore brief accidental presses)
- [ ] Support bounce keys (ignore rapid repeated presses)
- [ ] Add visual keyboard echo mode
- [ ] Implement sound feedback for key events

### Integration & Ecosystem (v1.0.0+)

- [ ] Add Rich library integration for styled output
- [ ] Create Textual widget wrapping KeyboardReader
- [ ] Add prompt_toolkit backend adapter
- [ ] Support Click command-line framework integration
- [ ] Create Typer integration examples
- [ ] Add pytest plugin for keyboard testing
- [ ] Implement MCP server for AI assistants
- [ ] Create VS Code extension for debugging

**Note**: Roadmap items are not committed and may change based on community feedback and priorities. Each checkbox represents a specific, self-contained contribution opportunity.

**Want to contribute?** Pick any unchecked item and see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines!

---

## Acknowledgments

KEYBARD's core keyboard parsing engine is derived from the **[Textual](https://github.com/Textualize/textual)** framework, created by Will McGugan and the team at Textualize.io.

### What We Extracted

- **XTerm Parser**: Battle-tested ANSI escape sequence parsing
- **Key System**: Comprehensive key enumeration and normalization
- **Terminal Drivers**: Cross-platform terminal control (Linux/macOS/Windows)
- **Event System**: Structured keyboard event hierarchy

**Original Textual Code**: Copyright (c) 2020-2024 Will McGugan and Textualize.io
**KEYBARD Adaptation**: Copyright (c) 2025 Emasoft
**License**: MIT (both projects)

The Textual framework is production-grade and battle-tested across dozens of terminal emulators and operating systems. By extracting and focusing solely on keyboard input, KEYBARD inherits this robustness while providing a lightweight, single-purpose library.

**If you need a full TUI framework** with widgets, layouts, CSS styling, mouse support, and more, please use [Textual](https://github.com/Textualize/textual) directly.

For detailed acknowledgments and technical details, see **[ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md)**.

---

## Contributing

We welcome contributions! Please see **[CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines.

**Quick links**:
- [Bug Reports](.github/ISSUE_TEMPLATE/bug_report.md)
- [Feature Requests](.github/ISSUE_TEMPLATE/feature_request.md)
- [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md)

---

## License

MIT License - see **[LICENSE](LICENSE)** file for details.

**Copyright (c) 2025 Emasoft**

Original Textual components: Copyright (c) 2020-2024 Will McGugan and Textualize.io

---

## Project Links

- **Repository**: https://github.com/Emasoft/KEYBARD
- **Issues**: https://github.com/Emasoft/KEYBARD/issues
- **Roadmap**: [See Roadmap section](#roadmap) - Planned features and improvements
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Acknowledgments**: [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## FAQ

**Q: Why not use `input()` or `getpass()`?**

A: Those are line-buffered and wait for Enter. KEYBARD gives you immediate, character-by-character input with full support for special keys and modifiers.

**Q: Does it work in Jupyter notebooks?**

A: No. KEYBARD requires direct terminal access. It won't work in Jupyter, IDEs, or other environments without a real terminal.

**Q: What about Windows?**

A: KEYBARD works on Windows using the Windows Console API.

**Q: How do I handle Ctrl+C without the program exiting?**

A: KEYBARD disables signal generation by default, allowing you to handle Ctrl+C as a regular key event. Set `KEYBARD_ALLOW_SIGNALS` environment variable to restore default signal behavior.

**Q: Does KEYBARD support mouse input?**

A: No. KEYBARD is keyboard-only by design. For mouse support, use the full [Textual](https://github.com/Textualize/textual) framework.

---

## Changelog

See **[CHANGELOG.md](CHANGELOG.md)** for version history and release notes.

### Latest Release: 0.2.0a1 (Alpha)

- Initial alpha release
- Cross-platform keyboard input (Linux, macOS, Windows)
- Battle-tested XTerm parser from Textual
- Blocking, non-blocking, and callback modes
- Support for special keys, modifiers, paste events
- Focus and resize event detection
- Comprehensive examples and documentation
