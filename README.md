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
  - `Key`: Keyboard key press (`.key` attribute)
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

**Test Status**: ✅ 322 passed, 2 skipped

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
