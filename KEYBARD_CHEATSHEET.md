# KEYBARD Quick Reference Cheatsheet

**Version:** 0.3.0a1
**Comprehensive reference for KEYBARD keyboard input library**

---

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Concepts](#core-concepts)
3. [Usage Patterns](#usage-patterns)
4. [KeyboardReader API](#keyboardreader-api)
5. [Event Types](#event-types)
6. [DispatcherConfig](#dispatcherconfig)
7. [Key Identifiers Reference](#key-identifiers-reference)
8. [Functional Keys (Kitty Protocol)](#functional-keys-kitty-protocol)
9. [Key Functions](#key-functions)
10. [Key Aliases](#key-aliases)
11. [Key Display Formatting](#key-display-formatting)
12. [Color Constants](#color-constants)
13. [Binary Encoding](#binary-encoding)
14. [ANSI Escape Sequences](#ansi-escape-sequences)

---

## Installation & Setup

| Command | Purpose |
|---------|---------|
| `uv add keybard rich` | Install KEYBARD and Rich library |
| `from keybard import KeyboardReader, DispatcherConfig` | Import main classes |
| `from keybard.events import Key, KeyClick, KeyDown, KeyUp` | Import event types |

---

## Core Concepts

| Term | Meaning |
|------|---------|
| **KeyboardReader** | Manages the PTY reader, normalizes escape sequences and emits `Event` objects |
| **Event** subclasses | `Key`, `Paste`, `Resize`, `KeyClick`, `KeyDown`, `KeyUp`, `ComboClick`, `ComboKeyDown` |
| **Key names** | Normalized strings from `keybard.keys.Keys` (e.g. `"up"`, `"down"`, `"escape"`, `"ctrl+c"`) |
| **Dispatcher** | Optional timing layer that converts repeated key streams into `KeyClick`/`KeyDown`/`KeyUp` |

---

## Usage Patterns

### Pattern 1: Blocking `read_key()` Loop

```python
from keybard import KeyboardReader
from keybard.events import Key

with KeyboardReader() as reader:
    while True:
        event = reader.read_key()
        if not isinstance(event, Key):
            continue

        key = event.key.lower()
        if key == "up":
            handle_up()
        elif key == "down":
            handle_down()
        elif key in {"escape", "ctrl+c"}:
            break
```

| Feature | Description |
|---------|-------------|
| **Mode** | Blocking - waits for each key press |
| **Best for** | Simple CLI tools, menu navigation |
| **Returns** | Single `Event` object per call |

### Pattern 2: Non-blocking `poll()` Loop

```python
with KeyboardReader() as reader:
    while True:
        for event in reader.poll():
            # Process event
            pass
        update_ui()
```

| Feature | Description |
|---------|-------------|
| **Mode** | Non-blocking - returns immediately |
| **Best for** | TUIs that need continuous refresh |
| **Returns** | List of all pending events |

### Pattern 3: Timing-Aware Events (Dispatcher)

```python
config = DispatcherConfig(delta=1.0, release_timeout=0.15)
with KeyboardReader(use_dispatcher=True, dispatcher_config=config) as reader:
    for event in reader.poll():
        if isinstance(event, KeyClick):
            pass  # Quick tap (< 1s)
        elif isinstance(event, KeyDown):
            pass  # Key held past delta
        elif isinstance(event, KeyUp):
            pass  # Inferred release
```

| Feature | Description |
|---------|-------------|
| **Mode** | Non-blocking with timing detection |
| **Best for** | Apps that need to distinguish tap vs hold |
| **Returns** | Timing-aware event types |

---

## KeyboardReader API

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_dispatcher` | `bool` | `False` | Enable timing-based event dispatcher |
| `dispatcher_config` | `DispatcherConfig \| None` | `None` | Configuration for dispatcher |

### Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `read_key(timeout=None)` | `Event \| None` | **Blocking** - Wait for single key event (with optional timeout) |
| `poll()` | `list[Event]` | **Non-blocking** - Get all pending events |
| `start()` | `None` | Start the reader manually (alternative to context manager) |
| `stop()` | `None` | Stop the reader manually |

### Context Manager

| Pattern | Description |
|---------|-------------|
| `with KeyboardReader() as reader:` | Recommended - automatically calls `start()`/`stop()` |
| Manual `start()/stop()` | Alternative if context manager not suitable |

---

## Event Types

### Core Event Types

| Event Class | When Emitted | Attributes |
|-------------|--------------|------------|
| `Key` | Every key press (raw mode) | `key: str`, `character: str \| None` |
| `Paste` | Bracketed paste detected | `text: str` |
| `Resize` | Terminal window resized | `size: Size` (width, height) |
| `AppFocus` | Terminal gained focus | - |
| `AppBlur` | Terminal lost focus | - |

### Timing-Based Event Types (Dispatcher Only)

| Event Class | When Emitted | Attributes |
|-------------|--------------|------------|
| `KeyClick` | Quick press/release (< delta) | `key: str`, `character: str \| None`, `duration: float` |
| `KeyDown` | Key held past delta threshold | `key: str`, `character: str \| None`, `hold_time: float`, `repeat_count: int` |
| `KeyUp` | Key released after KeyDown | `key: str`, `character: str \| None`, `total_duration: float` |
| `ComboClick` ⚠️ | **FUTURE** - Multiple keys quick press | `keys: list[str]`, `primary_key: str`, `duration: float` |
| `ComboKeyDown` ⚠️ | **FUTURE** - Multiple keys held | `keys: list[str]`, `primary_key: str`, `hold_time: float` |

⚠️ **Note**: Combo events not yet implemented in v0.3.0a1

---

## DispatcherConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `delta` | `float` | `1.0` | Time threshold (seconds) distinguishing click vs hold |
| `release_timeout` | `float` | `0.15` | Time without repeats before emitting `KeyUp` |
| `emit_repeats` | `bool` | `False` | Emit `KeyDown` on each key repeat |
| `repeat_interval` | `float` | `0.05` | Minimum time between repeat emissions |

### Timing Behavior

| Key Type | Repetition | Dispatcher Behavior |
|----------|------------|---------------------|
| Letters, numbers, arrows | ✅ OS repeats | Can detect `KeyDown`/`KeyUp` |
| Escape, standalone modifiers | ❌ No repeat | Always `KeyClick` + timeout `KeyUp` |
| Modified keys (Ctrl+C, etc.) | Varies | Depends on base key repetition |

---

## Key Identifiers Reference

### Arrow Keys

| Physical Key | `event.key` Value |
|--------------|-------------------|
| Up Arrow | `"up"` |
| Down Arrow | `"down"` |
| Left Arrow | `"left"` |
| Right Arrow | `"right"` |

### Special Keys

| Physical Key | `event.key` Value |
|--------------|-------------------|
| Escape | `"escape"` |
| Enter/Return | `"enter"` or `"return"` |
| Backspace | `"backspace"` |
| Tab | `"tab"` |
| Shift+Tab | `"shift+tab"` (or `"backtab"`) |
| Space | `"space"` |
| Home | `"home"` |
| End | `"end"` |
| Insert | `"insert"` |
| Delete | `"delete"` |
| PageUp | `"pageup"` |
| PageDown | `"pagedown"` |

### Function Keys

| Physical Key | `event.key` Value |
|--------------|-------------------|
| F1-F12 | `"f1"` ... `"f12"` |
| F13-F24 | `"f13"` ... `"f24"` |

### Control Key Combinations

| Combination | `event.key` Value | Notes |
|-------------|-------------------|-------|
| Ctrl+A-Z | `"ctrl+a"` ... `"ctrl+z"` | |
| Ctrl+0-9 | `"ctrl+0"` ... `"ctrl+9"` | |
| Ctrl+Space | `"ctrl+at"` or `"ctrl+space"` | Alias for Ctrl+@ |
| Ctrl+C | `"ctrl+c"` | Common interrupt |
| Ctrl+D | `"ctrl+d"` | Common EOF |
| Ctrl+I | `"ctrl+i"` | Alias for Tab |
| Ctrl+J | `"ctrl+j"` | Alias for Newline |
| Ctrl+M | `"ctrl+m"` | Alias for Enter |
| Ctrl+[ | `"ctrl+left_square_bracket"` | Alias for Escape |
| Ctrl+\\ | `"ctrl+backslash"` | |
| Ctrl+] | `"ctrl+right_square_bracket"` | |
| Ctrl+^ | `"ctrl+circumflex_accent"` | |
| Ctrl+_ | `"ctrl+underscore"` | |

### Shift Key Combinations

| Combination | `event.key` Value |
|-------------|-------------------|
| Shift+Arrow | `"shift+up"`, `"shift+down"`, `"shift+left"`, `"shift+right"` |
| Shift+Home/End | `"shift+home"`, `"shift+end"` |
| Shift+PageUp/PageDown | `"shift+pageup"`, `"shift+pagedown"` |
| Shift+Insert/Delete | `"shift+insert"`, `"shift+delete"` |
| Shift+F1-F24 | Not directly mapped (use Ctrl+Shift+F or other combos) |

### Ctrl+Shift Combinations

| Combination | `event.key` Value |
|-------------|-------------------|
| Ctrl+Shift+0-9 | `"ctrl+shift+0"` ... `"ctrl+shift+9"` |
| Ctrl+Shift+Arrow | `"ctrl+shift+up"`, `"ctrl+shift+down"`, `"ctrl+shift+left"`, `"ctrl+shift+right"` |
| Ctrl+Shift+Home/End | `"ctrl+shift+home"`, `"ctrl+shift+end"` |
| Ctrl+Shift+PageUp/PageDown | `"ctrl+shift+pageup"`, `"ctrl+shift+pagedown"` |
| Ctrl+Shift+Insert/Delete | `"ctrl+shift+insert"`, `"ctrl+shift+delete"` |
| Ctrl+Shift+F1-F24 | `"ctrl+shift+f1"` ... `"ctrl+shift+f24"` (xterm) |

### Ctrl+Arrow and Ctrl+Navigation

| Combination | `event.key` Value |
|-------------|-------------------|
| Ctrl+Left/Right | `"ctrl+left"`, `"ctrl+right"` |
| Ctrl+Up/Down | `"ctrl+up"`, `"ctrl+down"` |
| Ctrl+Home/End | `"ctrl+home"`, `"ctrl+end"` |
| Ctrl+PageUp/PageDown | `"ctrl+pageup"`, `"ctrl+pagedown"` |
| Ctrl+Insert/Delete | `"ctrl+insert"`, `"ctrl+delete"` |

### Ctrl+Function Keys

| Combination | `event.key` Value |
|-------------|-------------------|
| Ctrl+F1-F24 | `"ctrl+f1"` ... `"ctrl+f24"` |

### Alt/Meta Combinations

| Combination | `event.key` Value | Notes |
|-------------|-------------------|-------|
| Alt+Letter | `"alt+<letter>"` | e.g., `"alt+a"` |
| Meta+Letter | `"meta+<letter>"` | macOS Cmd key |

### Special Internal Keys

| Key | `event.key` Value | Purpose |
|-----|-------------------|---------|
| Any | `"<any>"` | Matches any key |
| ScrollUp | `"<scroll-up>"` | Scroll event |
| ScrollDown | `"<scroll-down>"` | Scroll event |
| Ignore | `"<ignore>"` | Key binding should do nothing |

---

## Functional Keys (Kitty Protocol)

Extended key protocol support (Kitty keyboard protocol).

### Extended Function Keys

| Escape Code | Key Name |
|-------------|----------|
| `27u` | `"escape"` |
| `13u` | `"enter"` |
| `9u` | `"tab"` |
| `127u` | `"backspace"` |
| `2~` | `"insert"` |
| `3~` | `"delete"` |

### Navigation (Kitty Extended)

| Escape Code | Key Name |
|-------------|----------|
| `1D` | `"left"` |
| `1C` | `"right"` |
| `1A` | `"up"` |
| `1B` | `"down"` |
| `5~` | `"pageup"` |
| `6~` | `"pagedown"` |
| `1H`, `1~`, `7~` | `"home"` |
| `1F`, `4~`, `8~` | `"end"` |

### Lock Keys (Kitty Extended)

| Escape Code | Key Name |
|-------------|----------|
| `57358u` | `"caps_lock"` |
| `57359u` | `"scroll_lock"` |
| `57360u` | `"num_lock"` |
| `57361u` | `"print_screen"` |
| `57362u` | `"pause"` |
| `57363u` | `"menu"` |

### Function Keys F13-F35 (Kitty Extended)

| Range | Escape Codes |
|-------|--------------|
| F13-F24 | `57376u` ... `57387u` |
| F25-F35 | `57388u` ... `57398u` |

### Keypad Keys (Kitty Extended)

| Escape Code | Key Name |
|-------------|----------|
| `57399u` - `57408u` | Keypad `"0"` - `"9"` |
| `57409u` | `"decimal"` |
| `57410u` | `"divide"` |
| `57411u` | `"multiply"` |
| `57412u` | `"subtract"` |
| `57413u` | `"add"` |
| `57414u` | `"enter"` |
| `57415u` | `"equal"` |

### Media Keys (Kitty Extended)

| Escape Code | Key Name |
|-------------|----------|
| `57428u` | `"media_play"` |
| `57429u` | `"media_pause"` |
| `57430u` | `"media_play_pause"` |
| `57431u` | `"media_reverse"` |
| `57432u` | `"media_stop"` |
| `57433u` | `"media_fast_forward"` |
| `57434u` | `"media_rewind"` |
| `57435u` | `"media_track_next"` |
| `57436u` | `"media_track_previous"` |
| `57437u` | `"media_record"` |

### Volume Keys (Kitty Extended)

| Escape Code | Key Name |
|-------------|----------|
| `57438u` | `"lower_volume"` |
| `57439u` | `"raise_volume"` |
| `57440u` | `"mute_volume"` |

### Modifier Keys (Kitty Extended)

| Escape Code | Key Name |
|-------------|----------|
| `57441u` - `57446u` | Left: `shift`, `control`, `alt`, `super`, `hyper`, `meta` |
| `57447u` - `57452u` | Right: `shift`, `control`, `alt`, `super`, `hyper`, `meta` |
| `57453u` | `"iso_level3_shift"` |
| `57454u` | `"iso_level5_shift"` |

---

## Key Functions

### Core Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `format_key(key: str) -> str` | Returns display representation | Converts key name to display format (e.g., `"up"` → `"↑"`) |
| `key_to_character(key: str) -> str \| None` | Extracts character from key | Returns printable character if available |

### Internal Functions

| Function | Purpose |
|----------|---------|
| `_character_to_key(character: str) -> str` | Convert single character to key name |
| `_get_unicode_name_from_key(key: str) -> str` | Get Unicode name from key |
| `_get_key_aliases(key: str) -> list[str]` | Return all aliases for given key |
| `_normalize_key_list(keys: str) -> str` | Normalize comma-separated key list |

---

## Key Aliases

### Primary Aliases

| Key | Aliases |
|-----|---------|
| `"tab"` | `["ctrl+i"]` |
| `"enter"` | `["ctrl+m"]` |
| `"escape"` | `["ctrl+left_square_bracket"]` |
| `"ctrl+at"` | `["ctrl+space"]` |
| `"ctrl+j"` | `["newline"]` |

### Backward Compatibility Aliases (Legacy)

| New Name | Old Alias |
|----------|-----------|
| `ControlShiftLeft` | `ShiftControlLeft` |
| `ControlShiftRight` | `ShiftControlRight` |
| `ControlShiftHome` | `ShiftControlHome` |
| `ControlShiftEnd` | `ShiftControlEnd` |

---

## Key Display Formatting

Visual symbols used for key display (e.g., in help text, UI).

| Key Name | Display Symbol |
|----------|----------------|
| `"up"` | `"↑"` |
| `"down"` | `"↓"` |
| `"left"` | `"←"` |
| `"right"` | `"→"` |
| `"backspace"` | `"⌫"` |
| `"escape"` | `"esc"` |
| `"enter"` | `"⏎"` |
| `"minus"` | `"-"` |
| `"space"` | `"space"` |
| `"pagedown"` | `"pgdn"` |
| `"pageup"` | `"pgup"` |
| `"delete"` | `"del"` |

---

## Color Constants

### ANSI Color Names

| Color Name | CSS Prefix | RGB |
|------------|------------|-----|
| `"black"` | `ansi_black` | `(0, 0, 0)` |
| `"red"` | `ansi_red` | `(128, 0, 0)` |
| `"green"` | `ansi_green` | `(0, 128, 0)` |
| `"yellow"` | `ansi_yellow` | `(128, 128, 0)` |
| `"blue"` | `ansi_blue` | `(0, 0, 128)` |
| `"magenta"` | `ansi_magenta` | `(128, 0, 128)` |
| `"cyan"` | `ansi_cyan` | `(0, 128, 128)` |
| `"white"` | `ansi_white` | `(192, 192, 192)` |

### Bright ANSI Colors

| Color Name | CSS Prefix | RGB |
|------------|------------|-----|
| `"bright_black"` | `ansi_bright_black` | `(128, 128, 128)` |
| `"bright_red"` | `ansi_bright_red` | `(255, 0, 0)` |
| `"bright_green"` | `ansi_bright_green` | `(0, 255, 0)` |
| `"bright_yellow"` | `ansi_bright_yellow` | `(255, 255, 0)` |
| `"bright_blue"` | `ansi_bright_blue` | `(0, 0, 255)` |
| `"bright_magenta"` | `ansi_bright_magenta` | `(255, 0, 255)` |
| `"bright_cyan"` | `ansi_bright_cyan` | `(0, 255, 255)` |
| `"bright_white"` | `ansi_bright_white` | `(255, 255, 255)` |

### Common Web Colors (Subset)

| Color Name | RGB |
|------------|-----|
| `"transparent"` | `(0, 0, 0, 0)` |
| `"black"` | `(0, 0, 0)` |
| `"white"` | `(255, 255, 255)` |
| `"red"` | `(255, 0, 0)` |
| `"green"` | `(0, 128, 0)` |
| `"blue"` | `(0, 0, 255)` |
| `"yellow"` | `(255, 255, 0)` |
| `"orange"` | `(255, 165, 0)` |
| `"purple"` | `(128, 0, 128)` |
| `"pink"` | `(255, 192, 203)` |
| `"cyan"` | `(0, 255, 255)` |
| `"magenta"` | `(255, 0, 255)` |

**Note**: Full web color list includes 140+ named colors. See `_color_constants.py` for complete mapping.

---

## Binary Encoding

KEYBARD includes binary serialization utilities (based on Bencode with extensions).

### Supported Data Types

| Python Type | Encoded Prefix | Example |
|-------------|----------------|---------|
| `None` | `N` | `b"N"` |
| `bool` (True) | `T` | `b"T"` |
| `bool` (False) | `F` | `b"F"` |
| `int` | `i<num>e` | `i42e` |
| `bytes` | `<len>:<bytes>` | `5:hello` |
| `str` | `s<len>:<utf8>` | `s5:hello` |
| `list` | `l<items>e` | `li1ei2ee` |
| `tuple` | `t<items>e` | `ti1ei2ee` |
| `dict` | `d<pairs>e` | `ds3:keyi42ee` |

### Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `dump(data: object) -> bytes` | Encode data structure to bytes | Serializes Python objects |
| `load(encoded: bytes) -> object` | Decode bytes to data structure | Deserializes to Python objects |

### Exception

| Exception | When Raised |
|-----------|-------------|
| `DecodeError` | Problem decoding data (malformed, truncated, etc.) |

---

## ANSI Escape Sequences

### Synchronization Markers

| Sequence | Purpose |
|----------|---------|
| `\x1b[?2026h` | `SYNC_START` - Begin synchronized output |
| `\x1b[?2026l` | `SYNC_END` - End synchronized output |

### Control Characters (Subset)

| Byte | Keys Enum | Description |
|------|-----------|-------------|
| `\x00` | `Keys.ControlAt` | Ctrl+@ (also Ctrl+Space) |
| `\x03` | `Keys.ControlC` | Ctrl+C (interrupt) |
| `\x04` | `Keys.ControlD` | Ctrl+D (exit) |
| `\x08` | `Keys.Backspace` | Backspace (Ctrl+H) |
| `\x09` | `Keys.Tab` | Tab (Ctrl+I) |
| `\x0a` | `Keys.ControlJ` | Newline (Ctrl+J) |
| `\x0d` | `Keys.Enter` | Enter/Return (Ctrl+M) |
| `\x1b` | `Keys.Escape` | Escape (Ctrl+[) |
| `\x7f` | `Keys.Backspace` | Backspace (ASCII DEL) |

### Arrow Keys (Normal Cursor Mode)

| Sequence | Keys Enum |
|----------|-----------|
| `\x1b[A` | `Keys.Up` |
| `\x1b[B` | `Keys.Down` |
| `\x1b[C` | `Keys.Right` |
| `\x1b[D` | `Keys.Left` |
| `\x1b[H` | `Keys.Home` |
| `\x1b[F` | `Keys.End` |

### Arrow Keys (Application Cursor Mode)

| Sequence | Keys Enum | Terminal |
|----------|-----------|----------|
| `\x1bOA` | `Keys.Up` | Tmux, Emacs ansi-term |
| `\x1bOB` | `Keys.Down` | Tmux, Emacs ansi-term |
| `\x1bOC` | `Keys.Right` | Tmux, Emacs ansi-term |
| `\x1bOD` | `Keys.Left` | Tmux, Emacs ansi-term |
| `\x1bOH` | `Keys.Home` | Application mode |
| `\x1bOF` | `Keys.End` | Application mode |

### Shift + Arrow Keys

| Sequence | Keys Enum | Terminal |
|----------|-----------|----------|
| `\x1b[1;2A` | `Keys.ShiftUp` | xterm, gnome-terminal |
| `\x1b[1;2B` | `Keys.ShiftDown` | xterm, gnome-terminal |
| `\x1b[1;2C` | `Keys.ShiftRight` | xterm, gnome-terminal |
| `\x1b[1;2D` | `Keys.ShiftLeft` | xterm, gnome-terminal |
| `\x1b[a` | `Keys.ShiftUp` | rxvt |
| `\x1b[b` | `Keys.ShiftDown` | rxvt |
| `\x1b[c` | `Keys.ShiftRight` | rxvt |
| `\x1b[d` | `Keys.ShiftLeft` | rxvt |

### Ctrl + Arrow Keys

| Sequence | Keys Enum | Terminal |
|----------|-----------|----------|
| `\x1b[1;5A` | `Keys.ControlUp` | Cursor mode |
| `\x1b[1;5B` | `Keys.ControlDown` | Cursor mode |
| `\x1b[1;5C` | `Keys.ControlRight` | Cursor mode |
| `\x1b[1;5D` | `Keys.ControlLeft` | Cursor mode |
| `\x1bf` | `Keys.ControlRight` | iTerm natural editing |
| `\x1bb` | `Keys.ControlLeft` | iTerm natural editing |
| `\x1bOa` - `\x1bOd` | Control arrows | rxvt |

### Function Keys (F1-F4)

| Sequence | Keys Enum | Terminal |
|----------|-----------|----------|
| `\x1bOP` | `Keys.F1` | Standard |
| `\x1bOQ` | `Keys.F2` | Standard |
| `\x1bOR` | `Keys.F3` | Standard |
| `\x1bOS` | `Keys.F4` | Standard |
| `\x1b[[A` - `\x1b[[E` | F1-F5 | Linux console |
| `\x1b[11~` - `\x1b[14~` | F1-F4 | rxvt-unicode |

### Function Keys (F5-F12)

| Sequence | Keys Enum |
|----------|-----------|
| `\x1b[15~` | `Keys.F5` |
| `\x1b[17~` | `Keys.F6` |
| `\x1b[18~` | `Keys.F7` |
| `\x1b[19~` | `Keys.F8` |
| `\x1b[20~` | `Keys.F9` |
| `\x1b[21~` | `Keys.F10` |
| `\x1b[23~` | `Keys.F11` |
| `\x1b[24~` | `Keys.F12` |

### Extended Function Keys (F13-F24 Xterm)

| Sequence | Keys Enum |
|----------|-----------|
| `\x1b[1;2P` | `Keys.F13` |
| `\x1b[1;2Q` | `Keys.F14` |
| `\x1b[1;2R` | `Keys.F15` |
| `\x1b[1;2S` | `Keys.F16` |
| `\x1b[15;2~` | `Keys.F17` |
| `\x1b[17;2~` | `Keys.F18` |
| `\x1b[18;2~` | `Keys.F19` |
| `\x1b[19;2~` | `Keys.F20` |
| `\x1b[20;2~` | `Keys.F21` |
| `\x1b[21;2~` | `Keys.F22` |
| `\x1b[23;2~` | `Keys.F23` |
| `\x1b[24;2~` | `Keys.F24` |

### Navigation Keys

| Sequence | Keys Enum | Terminal |
|----------|-----------|----------|
| `\x1b[1~` | `Keys.Home` | tmux |
| `\x1b[2~` | `Keys.Insert` | Standard |
| `\x1b[3~` | `Keys.Delete` | Standard |
| `\x1b[4~` | `Keys.End` | tmux |
| `\x1b[5~` | `Keys.PageUp` | Standard |
| `\x1b[6~` | `Keys.PageDown` | Standard |
| `\x1b[7~` | `Keys.Home` | xrvt |
| `\x1b[8~` | `Keys.End` | xrvt |

### Shift+Tab (BackTab)

| Sequence | Keys Enum | Terminal |
|----------|-----------|----------|
| `\x1b[Z` | `Keys.BackTab` | Standard |
| `\x1b\x09` | `Keys.BackTab` | Linux console |
| `\x1b[~` | `Keys.BackTab` | Windows console |

### Ignored Sequences

Special sequences that KEYBARD explicitly ignores:

| Sequence | Reason | Notes |
|----------|--------|-------|
| `\x1b[E` | Keypad 5 (no num mode) | Xterm |
| `\x1b[G` | Keypad 5 (no num mode) | Linux console |
| `\x1b[3;13~` | Ctrl+Cmd+Del | Kitty on macOS |
| `\x1b[1;13H` | Ctrl+Cmd+Home | Kitty on macOS |
| `\x1b[49;13u` - `\x1b[57;13u` | Ctrl+Cmd+Number | Kitty on macOS |

**Note**: Full ANSI sequence mapping contains 200+ entries. See `_ansi_sequences.py` for complete reference.

---

## Terminal Limitations

| Limitation | Explanation |
|------------|-------------|
| **No key-up events** | Terminal input only provides key press events (escape sequences), never explicit key release |
| **OS key repeat only** | Key repetition controlled by OS; varies by key type (letters/numbers repeat, Escape/modifiers don't) |
| **Inferred release** | Dispatcher infers key release from absence of repeats, not from explicit release events |
| **Escape ambiguity** | Single Escape key vs start of escape sequence distinguished by timeout |
| **Raw mode required** | Reader must be active (`with reader:` or manual `start()`/`stop()`), or terminal stays in raw mode |

---

## Integration Tips

| Tip | Description |
|-----|-------------|
| **Rich + KEYBARD** | Pairs well - draw using `Console.screen()`, read keys with KEYBARD |
| **Portable TUIs** | Use KEYBARD for cross-platform keyboard input |
| **Always check types** | Use `isinstance(event, Key)` before accessing event attributes |
| **Lowercase comparisons** | Normalize with `event.key.lower()` for case-insensitive matching |
| **Context manager** | Always use `with KeyboardReader():` to ensure proper cleanup |

---

## References

- **Source Documentation**: `/docs/keybard_basic_usage.md`
- **API Reference**: `API_REFERENCE.md`
- **Technical Architecture**: `TECHNICAL_ARCHITECTURE.md`
- **Full Source**: `src/keybard/keys.py`, `src/keybard/_ansi_sequences.py`, `src/keybard/_keyboard_protocol.py`

---

**End of Cheatsheet** | KEYBARD v0.3.0a1 | https://github.com/Emasoft/KEYBARD
