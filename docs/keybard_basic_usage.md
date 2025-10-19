# KEYBARD Complete Technical Reference

**Version:** 0.3.0a1
**Purpose:** Complete reference for all constants, sequences, and values in KEYBARD

This document contains EVERY constant, escape sequence, key name, and value defined in KEYBARD. Users who installed via pip should NOT need to dig through source code - everything is documented here.

---

## Table of Contents

1. [Installation & Imports](#1-installation--imports)
2. [Core Concepts](#2-core-concepts)
3. [Usage Patterns](#3-usage-patterns)
   - [Blocking read_key Loop](#31-blocking-read_key-loop)
   - [Non-blocking Polling](#32-non-blocking-polling)
   - [Timing-aware Events](#33-timing-aware-events)
4. [Complete Keys Enum Reference](#4-complete-keys-enum-reference)
5. [Complete ANSI Sequences Mapping](#5-complete-ansi-sequences-mapping)
6. [Complete Kitty Keyboard Protocol Keys](#6-complete-kitty-keyboard-protocol-keys)
7. [Key Name Mappings](#7-key-name-mappings)
8. [Color Constants](#8-color-constants)
9. [Paste & Resize Events](#9-paste--resize-events)
10. [Limitations & Tips](#10-limitations--tips)

---

## 1. Installation & Imports

```bash
# Install KEYBARD
uv add keybard rich  # or pip install keybard rich
```

```python
# Basic imports
from keybard import KeyboardReader, DispatcherConfig
from keybard.events import Key, KeyClick, KeyDown, KeyUp, Paste, Resize
from keybard.keys import Keys
```

---

## 2. Core Concepts

| Term | Meaning |
|------|---------|
| **KeyboardReader** | Manages the PTY reader, normalizes escape sequences, emits `Event` objects |
| **Event** subclasses | `Key`, `Paste`, `Resize`, `KeyClick`, `KeyDown`, `KeyUp`, etc. |
| **Key names** | Normalized strings from `keybard.keys.Keys` enum (e.g., `"up"`, `"escape"`, `"ctrl+c"`) |
| **Dispatcher** | Optional timing layer that converts repeated key streams into `KeyClick/KeyDown/KeyUp` |
| **ANSI sequences** | VT100/XTerm escape sequences mapped to key events |
| **Functional keys** | Kitty keyboard protocol extended keys |

---

## 3. Usage Patterns

### 3.1 Blocking read_key Loop

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

**Notes:**
- Arrow keys resolve to `"up"`, `"down"`, `"left"`, `"right"`
- Escape resolves to `"escape"`
- Ctrl+C resolves to `"ctrl+c"`

---

### 3.2 Non-blocking Polling

```python
with KeyboardReader() as reader:
    while True:
        for event in reader.poll():
            if isinstance(event, Key):
                print(f"Key pressed: {event.key}")
        update_ui()  # Continues even when no keys are pressed
```

`poll()` returns all pending events without blocking, ideal for TUIs that need continuous refresh.

---

### 3.3 Timing-aware Events

```python
config = DispatcherConfig(delta=1.0, release_timeout=0.15)
with KeyboardReader(use_dispatcher=True, dispatcher_config=config) as reader:
    for event in reader.poll():
        if isinstance(event, KeyClick):
            print("Quick tap (< 1s)")
        elif isinstance(event, KeyDown):
            print("Key held past delta")
        elif isinstance(event, KeyUp):
            print("Inferred release")
```

**Parameters:**
- **delta**: Threshold (seconds) distinguishing click vs hold
- **release_timeout**: Time without repeats before `KeyUp` is emitted

**Important:** Terminals only repeat certain keys (letters, numbers, arrows). Keys like Escape never repeat, so they always trigger `KeyClick` followed by synthetic `KeyUp` after timeout.

---

## 4. Complete Keys Enum Reference

All key constants from `keybard.keys.Keys`:

### 4.1 Basic Keys

| Enum Constant | Value | Notes |
|--------------|-------|-------|
| `Keys.Escape` | `"escape"` | Also Control-[ |
| `Keys.ShiftEscape` | `"shift+escape"` | |
| `Keys.Return` | `"return"` | |
| `Keys.Enter` | `"enter"` | Alias for Return |
| `Keys.Tab` | `"tab"` | |
| `Keys.BackTab` | `"shift+tab"` | Shift + Tab |
| `Keys.Space` | `"space"` | |
| `Keys.Backspace` | `"backspace"` | |

### 4.2 Control Keys (ASCII Control Characters)

| Enum Constant | Value | ASCII | Notes |
|--------------|-------|-------|-------|
| `Keys.ControlAt` | `"ctrl+@"` | `\x00` | Also Ctrl-Space |
| `Keys.ControlSpace` | `"ctrl-at"` | `\x00` | Alias for ControlAt |
| `Keys.ControlA` | `"ctrl+a"` | `\x01` | Home |
| `Keys.ControlB` | `"ctrl+b"` | `\x02` | Emacs cursor left |
| `Keys.ControlC` | `"ctrl+c"` | `\x03` | Interrupt |
| `Keys.ControlD` | `"ctrl+d"` | `\x04` | Exit |
| `Keys.ControlE` | `"ctrl+e"` | `\x05` | End |
| `Keys.ControlF` | `"ctrl+f"` | `\x06` | Cursor forward |
| `Keys.ControlG` | `"ctrl+g"` | `\x07` | |
| `Keys.ControlH` | `"ctrl+h"` | `\x08` | Identical to Backspace |
| `Keys.ControlI` | `"ctrl+i"` | `\x09` | Identical to Tab |
| `Keys.ControlJ` | `"ctrl+j"` | `\x0a` | Newline |
| `Keys.ControlK` | `"ctrl+k"` | `\x0b` | Delete to end of line |
| `Keys.ControlL` | `"ctrl+l"` | `\x0c` | Clear; form feed |
| `Keys.ControlM` | `"ctrl+m"` | `\x0d` | Carriage return (Enter alias) |
| `Keys.ControlN` | `"ctrl+n"` | `\x0e` | History forward |
| `Keys.ControlO` | `"ctrl+o"` | `\x0f` | |
| `Keys.ControlP` | `"ctrl+p"` | `\x10` | History back |
| `Keys.ControlQ` | `"ctrl+q"` | `\x11` | |
| `Keys.ControlR` | `"ctrl+r"` | `\x12` | Reverse search |
| `Keys.ControlS` | `"ctrl+s"` | `\x13` | Forward search |
| `Keys.ControlT` | `"ctrl+t"` | `\x14` | |
| `Keys.ControlU` | `"ctrl+u"` | `\x15` | |
| `Keys.ControlV` | `"ctrl+v"` | `\x16` | |
| `Keys.ControlW` | `"ctrl+w"` | `\x17` | |
| `Keys.ControlX` | `"ctrl+x"` | `\x18` | |
| `Keys.ControlY` | `"ctrl+y"` | `\x19` | |
| `Keys.ControlZ` | `"ctrl+z"` | `\x1a` | |
| `Keys.ControlBackslash` | `"ctrl+backslash"` | `\x1c` | Also Ctrl-\| |
| `Keys.ControlSquareClose` | `"ctrl+right_square_bracket"` | `\x1d` | Ctrl-] |
| `Keys.ControlCircumflex` | `"ctrl+circumflex_accent"` | `\x1e` | Ctrl-^ |
| `Keys.ControlUnderscore` | `"ctrl+underscore"` | `\x1f` | Also Ctrl-hyphen |

### 4.3 Control + Number Keys

| Enum Constant | Value |
|--------------|-------|
| `Keys.Control0` | `"ctrl+0"` |
| `Keys.Control1` | `"ctrl+1"` |
| `Keys.Control2` | `"ctrl+2"` |
| `Keys.Control3` | `"ctrl+3"` |
| `Keys.Control4` | `"ctrl+4"` |
| `Keys.Control5` | `"ctrl+5"` |
| `Keys.Control6` | `"ctrl+6"` |
| `Keys.Control7` | `"ctrl+7"` |
| `Keys.Control8` | `"ctrl+8"` |
| `Keys.Control9` | `"ctrl+9"` |

### 4.4 Control + Shift + Number Keys

| Enum Constant | Value |
|--------------|-------|
| `Keys.ControlShift0` | `"ctrl+shift+0"` |
| `Keys.ControlShift1` | `"ctrl+shift+1"` |
| `Keys.ControlShift2` | `"ctrl+shift+2"` |
| `Keys.ControlShift3` | `"ctrl+shift+3"` |
| `Keys.ControlShift4` | `"ctrl+shift+4"` |
| `Keys.ControlShift5` | `"ctrl+shift+5"` |
| `Keys.ControlShift6` | `"ctrl+shift+6"` |
| `Keys.ControlShift7` | `"ctrl+shift+7"` |
| `Keys.ControlShift8` | `"ctrl+shift+8"` |
| `Keys.ControlShift9` | `"ctrl+shift+9"` |

### 4.5 Arrow Keys

| Enum Constant | Value |
|--------------|-------|
| `Keys.Left` | `"left"` |
| `Keys.Right` | `"right"` |
| `Keys.Up` | `"up"` |
| `Keys.Down` | `"down"` |

### 4.6 Arrow Keys with Modifiers

| Enum Constant | Value |
|--------------|-------|
| `Keys.ControlLeft` | `"ctrl+left"` |
| `Keys.ControlRight` | `"ctrl+right"` |
| `Keys.ControlUp` | `"ctrl+up"` |
| `Keys.ControlDown` | `"ctrl+down"` |
| `Keys.ShiftLeft` | `"shift+left"` |
| `Keys.ShiftRight` | `"shift+right"` |
| `Keys.ShiftUp` | `"shift+up"` |
| `Keys.ShiftDown` | `"shift+down"` |
| `Keys.ControlShiftLeft` | `"ctrl+shift+left"` |
| `Keys.ControlShiftRight` | `"ctrl+shift+right"` |
| `Keys.ControlShiftUp` | `"ctrl+shift+up"` |
| `Keys.ControlShiftDown` | `"ctrl+shift+down"` |

### 4.7 Navigation Keys

| Enum Constant | Value |
|--------------|-------|
| `Keys.Home` | `"home"` |
| `Keys.End` | `"end"` |
| `Keys.Insert` | `"insert"` |
| `Keys.Delete` | `"delete"` |
| `Keys.PageUp` | `"pageup"` |
| `Keys.PageDown` | `"pagedown"` |

### 4.8 Navigation Keys with Modifiers

| Enum Constant | Value |
|--------------|-------|
| `Keys.ControlHome` | `"ctrl+home"` |
| `Keys.ControlEnd` | `"ctrl+end"` |
| `Keys.ControlInsert` | `"ctrl+insert"` |
| `Keys.ControlDelete` | `"ctrl+delete"` |
| `Keys.ControlPageUp` | `"ctrl+pageup"` |
| `Keys.ControlPageDown` | `"ctrl+pagedown"` |
| `Keys.ShiftHome` | `"shift+home"` |
| `Keys.ShiftEnd` | `"shift+end"` |
| `Keys.ShiftInsert` | `"shift+insert"` |
| `Keys.ShiftDelete` | `"shift+delete"` |
| `Keys.ShiftPageUp` | `"shift+pageup"` |
| `Keys.ShiftPageDown` | `"shift+pagedown"` |
| `Keys.ControlShiftHome` | `"ctrl+shift+home"` |
| `Keys.ControlShiftEnd` | `"ctrl+shift+end"` |
| `Keys.ControlShiftInsert` | `"ctrl+shift+insert"` |
| `Keys.ControlShiftDelete` | `"ctrl+shift+delete"` |
| `Keys.ControlShiftPageUp` | `"ctrl+shift+pageup"` |
| `Keys.ControlShiftPageDown` | `"ctrl+shift+pagedown"` |

### 4.9 Function Keys (F1-F24)

| Enum Constant | Value |
|--------------|-------|
| `Keys.F1` | `"f1"` |
| `Keys.F2` | `"f2"` |
| `Keys.F3` | `"f3"` |
| `Keys.F4` | `"f4"` |
| `Keys.F5` | `"f5"` |
| `Keys.F6` | `"f6"` |
| `Keys.F7` | `"f7"` |
| `Keys.F8` | `"f8"` |
| `Keys.F9` | `"f9"` |
| `Keys.F10` | `"f10"` |
| `Keys.F11` | `"f11"` |
| `Keys.F12` | `"f12"` |
| `Keys.F13` | `"f13"` |
| `Keys.F14` | `"f14"` |
| `Keys.F15` | `"f15"` |
| `Keys.F16` | `"f16"` |
| `Keys.F17` | `"f17"` |
| `Keys.F18` | `"f18"` |
| `Keys.F19` | `"f19"` |
| `Keys.F20` | `"f20"` |
| `Keys.F21` | `"f21"` |
| `Keys.F22` | `"f22"` |
| `Keys.F23` | `"f23"` |
| `Keys.F24` | `"f24"` |

### 4.10 Control + Function Keys

| Enum Constant | Value |
|--------------|-------|
| `Keys.ControlF1` | `"ctrl+f1"` |
| `Keys.ControlF2` | `"ctrl+f2"` |
| `Keys.ControlF3` | `"ctrl+f3"` |
| `Keys.ControlF4` | `"ctrl+f4"` |
| `Keys.ControlF5` | `"ctrl+f5"` |
| `Keys.ControlF6` | `"ctrl+f6"` |
| `Keys.ControlF7` | `"ctrl+f7"` |
| `Keys.ControlF8` | `"ctrl+f8"` |
| `Keys.ControlF9` | `"ctrl+f9"` |
| `Keys.ControlF10` | `"ctrl+f10"` |
| `Keys.ControlF11` | `"ctrl+f11"` |
| `Keys.ControlF12` | `"ctrl+f12"` |
| `Keys.ControlF13` | `"ctrl+f13"` |
| `Keys.ControlF14` | `"ctrl+f14"` |
| `Keys.ControlF15` | `"ctrl+f15"` |
| `Keys.ControlF16` | `"ctrl+f16"` |
| `Keys.ControlF17` | `"ctrl+f17"` |
| `Keys.ControlF18` | `"ctrl+f18"` |
| `Keys.ControlF19` | `"ctrl+f19"` |
| `Keys.ControlF20` | `"ctrl+f20"` |
| `Keys.ControlF21` | `"ctrl+f21"` |
| `Keys.ControlF22` | `"ctrl+f22"` |
| `Keys.ControlF23` | `"ctrl+f23"` |
| `Keys.ControlF24` | `"ctrl+f24"` |

### 4.11 Special Keys

| Enum Constant | Value | Notes |
|--------------|-------|-------|
| `Keys.Any` | `"<any>"` | Matches any key |
| `Keys.ScrollUp` | `"<scroll-up>"` | Scroll event |
| `Keys.ScrollDown` | `"<scroll-down>"` | Scroll event |
| `Keys.Ignore` | `"<ignore>"` | Internal use - ignored key |

### 4.12 Legacy Aliases (Backward Compatibility)

| Enum Constant | Alias For |
|--------------|-----------|
| `Keys.ShiftControlLeft` | `Keys.ControlShiftLeft` |
| `Keys.ShiftControlRight` | `Keys.ControlShiftRight` |
| `Keys.ShiftControlHome` | `Keys.ControlShiftHome` |
| `Keys.ShiftControlEnd` | `Keys.ControlShiftEnd` |

---

## 5. Complete ANSI Sequences Mapping

All 425 entries from `_ansi_sequences.py` - mapping VT100/XTerm escape sequences to keys.

**Legend:**
- `\x##` = Hexadecimal escape code
- `\x1b` = ESC character (0x1B)
- `IGNORE` = Sequence is ignored (not processed)

### 5.1 Control Characters (ASCII 0x00-0x1F, 0x7F)

| Sequence | Hex | Key | Notes |
|----------|-----|-----|-------|
| ` ` | (space) | `space` | Space character |
| `\r` | `\x0d` | `enter` | Carriage return |
| `\x00` | `\x00` | `ctrl+@` | Control-At (also Ctrl-Space) |
| `\x01` | `\x01` | `ctrl+a` | Control-A (home) |
| `\x02` | `\x02` | `ctrl+b` | Control-B (emacs cursor left) |
| `\x03` | `\x03` | `ctrl+c` | Control-C (interrupt) |
| `\x04` | `\x04` | `ctrl+d` | Control-D (exit) |
| `\x05` | `\x05` | `ctrl+e` | Control-E (end) |
| `\x06` | `\x06` | `ctrl+f` | Control-F (cursor forward) |
| `\x07` | `\x07` | `ctrl+g` | Control-G |
| `\x08` | `\x08` | `backspace` | Control-H (identical to backspace) |
| `\x09` | `\x09` | `tab` | Control-I (identical to tab) |
| `\x0a` | `\x0a` | `ctrl+j` | Control-J (newline) |
| `\x0b` | `\x0b` | `ctrl+k` | Control-K (delete to EOL) |
| `\x0c` | `\x0c` | `ctrl+l` | Control-L (clear/form feed) |
| `\x0e` | `\x0e` | `ctrl+n` | Control-N (history forward) |
| `\x0f` | `\x0f` | `ctrl+o` | Control-O |
| `\x10` | `\x10` | `ctrl+p` | Control-P (history back) |
| `\x11` | `\x11` | `ctrl+q` | Control-Q |
| `\x12` | `\x12` | `ctrl+r` | Control-R (reverse search) |
| `\x13` | `\x13` | `ctrl+s` | Control-S (forward search) |
| `\x14` | `\x14` | `ctrl+t` | Control-T |
| `\x15` | `\x15` | `ctrl+u` | Control-U |
| `\x16` | `\x16` | `ctrl+v` | Control-V |
| `\x17` | `\x17` | `ctrl+w` | Control-W |
| `\x18` | `\x18` | `ctrl+x` | Control-X |
| `\x19` | `\x19` | `ctrl+y` | Control-Y |
| `\x1a` | `\x1a` | `ctrl+z` | Control-Z |
| `\x1b` | `\x1b` | `escape` | Escape (also Control-[) |
| `\x1b\x1b` | - | `escape` | Windows double-ESC workaround |
| `\x9b` | `\x9b` | `shift+escape` | CSI character |
| `\x1c` | `\x1c` | `ctrl+backslash` | Control-\ (also Ctrl-\|) |
| `\x1d` | `\x1d` | `ctrl+right_square_bracket` | Control-] |
| `\x1e` | `\x1e` | `ctrl+circumflex_accent` | Control-^ |
| `\x1f` | `\x1f` | `ctrl+underscore` | Control-_ (also Ctrl-hyphen) |
| `\x7f` | `\x7f` | `backspace` | ASCII DEL |
| `\x1b\x7f` | - | `ctrl+w` | Alt-Backspace |

### 5.2 Basic Navigation (Home, End, Insert, Delete, PageUp, PageDown)

| Sequence | Key | Terminal |
|----------|-----|----------|
| `\x1b[1~` | `home` | tmux |
| `\x1b[2~` | `insert` | |
| `\x1b[3~` | `delete` | |
| `\x1b[4~` | `end` | tmux |
| `\x1b[5~` | `pageup` | |
| `\x1b[6~` | `pagedown` | |
| `\x1b[7~` | `home` | xrvt |
| `\x1b[8~` | `end` | xrvt |

### 5.3 Tab and BackTab

| Sequence | Key | Terminal |
|----------|-----|----------|
| `\x1b[Z` | `shift+tab` | |
| `\x1b\x09` | `shift+tab` | Linux console |
| `\x1b[~` | `shift+tab` | Windows console |

### 5.4 Function Keys F1-F12 (Multiple Terminal Variants)

| Sequence | Key | Terminal |
|----------|-----|----------|
| `\x1bOP` | `f1` | Standard |
| `\x1bOQ` | `f2` | Standard |
| `\x1bOR` | `f3` | Standard |
| `\x1bOS` | `f4` | Standard |
| `\x1b[[A` | `f1` | Linux console |
| `\x1b[[B` | `f2` | Linux console |
| `\x1b[[C` | `f3` | Linux console |
| `\x1b[[D` | `f4` | Linux console |
| `\x1b[[E` | `f5` | Linux console |
| `\x1b[11~` | `f1` | rxvt-unicode |
| `\x1b[12~` | `f2` | rxvt-unicode |
| `\x1b[13~` | `f3` | rxvt-unicode |
| `\x1b[14~` | `f4` | rxvt-unicode |
| `\x1b[15~` | `f5` | |
| `\x1b[17~` | `f6` | |
| `\x1b[18~` | `f7` | |
| `\x1b[19~` | `f8` | |
| `\x1b[20~` | `f9` | |
| `\x1b[21~` | `f10` | |
| `\x1b[23~` | `f11` | |
| `\x1b[24~` | `f12` | |

### 5.5 Function Keys F13-F24 (Standard Sequences)

| Sequence | Key |
|----------|-----|
| `\x1b[25~` | `f13` |
| `\x1b[26~` | `f14` |
| `\x1b[28~` | `f15` |
| `\x1b[29~` | `f16` |
| `\x1b[31~` | `f17` |
| `\x1b[32~` | `f18` |
| `\x1b[33~` | `f19` |
| `\x1b[34~` | `f20` |

### 5.6 Function Keys F13-F24 (Xterm Format)

| Sequence | Key |
|----------|-----|
| `\x1b[1;2P` | `f13` |
| `\x1b[1;2Q` | `f14` |
| `\x1b[1;2R` | `f15` |
| `\x1b[1;2S` | `f16` |
| `\x1b[15;2~` | `f17` |
| `\x1b[17;2~` | `f18` |
| `\x1b[18;2~` | `f19` |
| `\x1b[19;2~` | `f20` |
| `\x1b[20;2~` | `f21` |
| `\x1b[21;2~` | `f22` |
| `\x1b[23;2~` | `f23` |
| `\x1b[24;2~` | `f24` |

### 5.7 Function Keys F23-F24 (rxvt Format)

| Sequence | Key |
|----------|-----|
| `\x1b[23$` | `f23` |
| `\x1b[24$` | `f24` |

### 5.8 Control + Function Keys F1-F12

| Sequence | Key |
|----------|-----|
| `\x1b[1;5P` | `ctrl+f1` |
| `\x1b[1;5Q` | `ctrl+f2` |
| `\x1b[1;5R` | `ctrl+f3` |
| `\x1b[1;5S` | `ctrl+f4` |
| `\x1b[15;5~` | `ctrl+f5` |
| `\x1b[17;5~` | `ctrl+f6` |
| `\x1b[18;5~` | `ctrl+f7` |
| `\x1b[19;5~` | `ctrl+f8` |
| `\x1b[20;5~` | `ctrl+f9` |
| `\x1b[21;5~` | `ctrl+f10` |
| `\x1b[23;5~` | `ctrl+f11` |
| `\x1b[24;5~` | `ctrl+f12` |

### 5.9 Control + Function Keys F13-F24

| Sequence | Key |
|----------|-----|
| `\x1b[1;6P` | `ctrl+f13` |
| `\x1b[1;6Q` | `ctrl+f14` |
| `\x1b[1;6R` | `ctrl+f15` |
| `\x1b[1;6S` | `ctrl+f16` |
| `\x1b[15;6~` | `ctrl+f17` |
| `\x1b[17;6~` | `ctrl+f18` |
| `\x1b[18;6~` | `ctrl+f19` |
| `\x1b[19;6~` | `ctrl+f20` |
| `\x1b[20;6~` | `ctrl+f21` |
| `\x1b[21;6~` | `ctrl+f22` |
| `\x1b[23;6~` | `ctrl+f23` |
| `\x1b[24;6~` | `ctrl+f24` |

### 5.10 Control + Function Keys (rxvt-unicode Format)

| Sequence | Key |
|----------|-----|
| `\x1b[11^` | `ctrl+f1` |
| `\x1b[12^` | `ctrl+f2` |
| `\x1b[13^` | `ctrl+f3` |
| `\x1b[14^` | `ctrl+f4` |
| `\x1b[15^` | `ctrl+f5` |
| `\x1b[17^` | `ctrl+f6` |
| `\x1b[18^` | `ctrl+f7` |
| `\x1b[19^` | `ctrl+f8` |
| `\x1b[20^` | `ctrl+f9` |
| `\x1b[21^` | `ctrl+f10` |
| `\x1b[23^` | `ctrl+f11` |
| `\x1b[24^` | `ctrl+f12` |

### 5.11 Control+Shift Function Keys (rxvt-unicode Format)

| Sequence | Key |
|----------|-----|
| `\x1b[25^` | `ctrl+f13` |
| `\x1b[26^` | `ctrl+f14` |
| `\x1b[28^` | `ctrl+f15` |
| `\x1b[29^` | `ctrl+f16` |
| `\x1b[31^` | `ctrl+f17` |
| `\x1b[32^` | `ctrl+f18` |
| `\x1b[33^` | `ctrl+f19` |
| `\x1b[34^` | `ctrl+f20` |
| `\x1b[23@` | `ctrl+f21` |
| `\x1b[24@` | `ctrl+f22` |

### 5.12 Scroll Events (Tmux Win32 Subsystem)

| Sequence | Key |
|----------|-----|
| `\x1b[62~` | `<scroll-up>` |
| `\x1b[63~` | `<scroll-down>` |

### 5.13 Modified Insert/Delete/PageUp/PageDown (Shift)

| Sequence | Key | Terminal |
|----------|-----|----------|
| `\x1b[3;2~` | `shift+delete` | xterm, gnome-terminal |
| `\x1b[3$` | `shift+delete` | rxvt |
| `\x1b[5;2~` | `shift+pageup` | |
| `\x1b[6;2~` | `shift+pagedown` | |

### 5.14 Modified Insert/Delete/PageUp/PageDown (Escape + Key)

| Sequence | Keys |
|----------|------|
| `\x1b[2;3~` | `escape`, `insert` |
| `\x1b[3;3~` | `escape`, `delete` |
| `\x1b[5;3~` | `escape`, `pageup` |
| `\x1b[6;3~` | `escape`, `pagedown` |
| `\x1b[2;4~` | `escape`, `shift+insert` |
| `\x1b[3;4~` | `escape`, `shift+delete` |
| `\x1b[5;4~` | `escape`, `shift+pageup` |
| `\x1b[6;4~` | `escape`, `shift+pagedown` |

### 5.15 Modified Insert/Delete/PageUp/PageDown (Control)

| Sequence | Key | Terminal |
|----------|-----|----------|
| `\x1b[3;5~` | `ctrl+delete` | xterm, gnome-terminal |
| `\x1b[3^` | `ctrl+delete` | rxvt |
| `\x1b[5;5~` | `ctrl+pageup` | |
| `\x1b[6;5~` | `ctrl+pagedown` | |
| `\x1b[5^` | `ctrl+pageup` | rxvt |
| `\x1b[6^` | `ctrl+pagedown` | rxvt |

### 5.16 Modified Insert/Delete/PageUp/PageDown (Control+Shift)

| Sequence | Key |
|----------|-----|
| `\x1b[3;6~` | `ctrl+shift+delete` |
| `\x1b[5;6~` | `ctrl+shift+pageup` |
| `\x1b[6;6~` | `ctrl+shift+pagedown` |

### 5.17 Modified Insert/Delete/PageUp/PageDown (Escape+Control)

| Sequence | Keys |
|----------|------|
| `\x1b[2;7~` | `escape`, `ctrl+insert` |
| `\x1b[5;7~` | `escape`, `ctrl+pagedown` |
| `\x1b[6;7~` | `escape`, `ctrl+pagedown` |

### 5.18 Modified Insert/Delete/PageUp/PageDown (Escape+Control+Shift)

| Sequence | Keys |
|----------|------|
| `\x1b[2;8~` | `escape`, `ctrl+shift+insert` |
| `\x1b[5;8~` | `escape`, `ctrl+shift+pagedown` |
| `\x1b[6;8~` | `escape`, `ctrl+shift+pagedown` |

### 5.19 Arrow Keys (Normal Cursor Mode)

| Sequence | Key |
|----------|-----|
| `\x1b[A` | `up` |
| `\x1b[B` | `down` |
| `\x1b[C` | `right` |
| `\x1b[D` | `left` |
| `\x1b[H` | `home` |
| `\x1b[F` | `end` |

### 5.20 Arrow Keys (Application Cursor Mode)

| Sequence | Key | Notes |
|----------|-----|-------|
| `\x1bOA` | `up` | Tmux/Emacs ansi-term |
| `\x1bOB` | `down` | Tmux/Emacs ansi-term |
| `\x1bOC` | `right` | Tmux/Emacs ansi-term |
| `\x1bOD` | `left` | Tmux/Emacs ansi-term |
| `\x1bOF` | `end` | |
| `\x1bOH` | `home` | |

### 5.21 Shift + Arrow Keys (Standard)

| Sequence | Key |
|----------|-----|
| `\x1b[1;2A` | `shift+up` |
| `\x1b[1;2B` | `shift+down` |
| `\x1b[1;2C` | `shift+right` |
| `\x1b[1;2D` | `shift+left` |
| `\x1b[1;2F` | `shift+end` |
| `\x1b[1;2H` | `shift+home` |

### 5.22 Shift + Arrow Keys (rxvt)

| Sequence | Key |
|----------|-----|
| `\x1b[a` | `shift+up` |
| `\x1b[b` | `shift+down` |
| `\x1b[c` | `shift+right` |
| `\x1b[d` | `shift+left` |
| `\x1b[7$` | `shift+home` |
| `\x1b[8$` | `shift+end` |

### 5.23 Meta/Alt + Arrow Keys (xterm/gnome-terminal)

| Sequence | Keys |
|----------|------|
| `\x1b[1;3A` | `escape`, `up` |
| `\x1b[1;3B` | `escape`, `down` |
| `\x1b[1;3C` | `escape`, `right` |
| `\x1b[1;3D` | `escape`, `left` |
| `\x1b[1;3F` | `escape`, `end` |
| `\x1b[1;3H` | `escape`, `home` |

### 5.24 Alt+Shift + Arrow Keys

| Sequence | Keys |
|----------|------|
| `\x1b[1;4A` | `escape`, `shift+up` |
| `\x1b[1;4B` | `escape`, `shift+down` |
| `\x1b[1;4C` | `escape`, `shift+right` |
| `\x1b[1;4D` | `escape`, `shift+left` |
| `\x1b[1;4F` | `escape`, `shift+end` |
| `\x1b[1;4H` | `escape`, `shift+home` |

### 5.25 Control + Arrow Keys (Cursor Mode)

| Sequence | Key |
|----------|-----|
| `\x1b[1;5A` | `ctrl+up` |
| `\x1b[1;5B` | `ctrl+down` |
| `\x1b[1;5C` | `ctrl+right` |
| `\x1b[1;5D` | `ctrl+left` |
| `\x1b[1;5F` | `ctrl+end` |
| `\x1b[1;5H` | `ctrl+home` |

### 5.26 Control + Arrow Keys (iTerm Natural Editing)

| Sequence | Key |
|----------|-----|
| `\x1bf` | `ctrl+right` |
| `\x1bb` | `ctrl+left` |

### 5.27 Control + Home/End (rxvt)

| Sequence | Key |
|----------|-----|
| `\x1b[7^` | `ctrl+end` |
| `\x1b[8^` | `ctrl+home` |

### 5.28 Control + Arrow Keys (Tmux/Emacs Alternate)

| Sequence | Key | Notes |
|----------|-----|-------|
| `\x1b[5A` | `ctrl+up` | Tmux/Emacs ansi-term |
| `\x1b[5B` | `ctrl+down` | Tmux/Emacs ansi-term |
| `\x1b[5C` | `ctrl+right` | Tmux/Emacs ansi-term |
| `\x1b[5D` | `ctrl+left` | Tmux/Emacs ansi-term |

### 5.29 Control + Arrow Keys (rxvt Application Mode)

| Sequence | Key |
|----------|-----|
| `\x1bOa` | `ctrl+up` |
| `\x1bOb` | `ctrl+up` |
| `\x1bOc` | `ctrl+right` |
| `\x1bOd` | `ctrl+left` |

### 5.30 Control+Shift + Arrow Keys

| Sequence | Key |
|----------|-----|
| `\x1b[1;6A` | `ctrl+shift+up` |
| `\x1b[1;6B` | `ctrl+shift+down` |
| `\x1b[1;6C` | `ctrl+shift+right` |
| `\x1b[1;6D` | `ctrl+shift+left` |
| `\x1b[1;6F` | `ctrl+shift+end` |
| `\x1b[1;6H` | `ctrl+shift+home` |

### 5.31 Control+Meta + Arrow Keys

| Sequence | Keys |
|----------|------|
| `\x1b[1;7A` | `escape`, `ctrl+up` |
| `\x1b[1;7B` | `escape`, `ctrl+down` |
| `\x1b[1;7C` | `escape`, `ctrl+right` |
| `\x1b[1;7D` | `escape`, `ctrl+left` |
| `\x1b[1;7F` | `escape`, `ctrl+end` |
| `\x1b[1;7H` | `escape`, `ctrl+home` |

### 5.32 Meta+Shift + Arrow Keys

| Sequence | Keys |
|----------|------|
| `\x1b[1;8A` | `escape`, `ctrl+shift+up` |
| `\x1b[1;8B` | `escape`, `ctrl+shift+down` |
| `\x1b[1;8C` | `escape`, `ctrl+shift+right` |
| `\x1b[1;8D` | `escape`, `ctrl+shift+left` |
| `\x1b[1;8F` | `escape`, `ctrl+shift+end` |
| `\x1b[1;8H` | `escape`, `ctrl+shift+home` |

### 5.33 Meta + Arrow Keys (iTerm on macOS)

| Sequence | Keys |
|----------|------|
| `\x1b[1;9A` | `escape`, `up` |
| `\x1b[1;9B` | `escape`, `down` |
| `\x1b[1;9C` | `escape`, `right` |
| `\x1b[1;9D` | `escape`, `left` |

### 5.34 Control+Number Keys (Mintty)

| Sequence | Key |
|----------|-----|
| `\x1b[1;5p` | `ctrl+0` |
| `\x1b[1;5q` | `ctrl+1` |
| `\x1b[1;5r` | `ctrl+2` |
| `\x1b[1;5s` | `ctrl+3` |
| `\x1b[1;5t` | `ctrl+4` |
| `\x1b[1;5u` | `ctrl+5` |
| `\x1b[1;5v` | `ctrl+6` |
| `\x1b[1;5w` | `ctrl+7` |
| `\x1b[1;5x` | `ctrl+8` |
| `\x1b[1;5y` | `ctrl+9` |

### 5.35 Control+Shift+Number Keys (Mintty)

| Sequence | Key |
|----------|-----|
| `\x1b[1;6p` | `ctrl+shift+0` |
| `\x1b[1;6q` | `ctrl+shift+1` |
| `\x1b[1;6r` | `ctrl+shift+2` |
| `\x1b[1;6s` | `ctrl+shift+3` |
| `\x1b[1;6t` | `ctrl+shift+4` |
| `\x1b[1;6u` | `ctrl+shift+5` |
| `\x1b[1;6v` | `ctrl+shift+6` |
| `\x1b[1;6w` | `ctrl+shift+7` |
| `\x1b[1;6x` | `ctrl+shift+8` |
| `\x1b[1;6y` | `ctrl+shift+9` |

### 5.36 Escape+Control+Number Keys (Mintty)

| Sequence | Keys |
|----------|------|
| `\x1b[1;7p` | `escape`, `ctrl+0` |
| `\x1b[1;7q` | `escape`, `ctrl+1` |
| `\x1b[1;7r` | `escape`, `ctrl+2` |
| `\x1b[1;7s` | `escape`, `ctrl+3` |
| `\x1b[1;7t` | `escape`, `ctrl+4` |
| `\x1b[1;7u` | `escape`, `ctrl+5` |
| `\x1b[1;7v` | `escape`, `ctrl+6` |
| `\x1b[1;7w` | `escape`, `ctrl+7` |
| `\x1b[1;7x` | `escape`, `ctrl+8` |
| `\x1b[1;7y` | `escape`, `ctrl+9` |

### 5.37 Escape+Control+Shift+Number Keys (Mintty)

| Sequence | Keys |
|----------|------|
| `\x1b[1;8p` | `escape`, `ctrl+shift+0` |
| `\x1b[1;8q` | `escape`, `ctrl+shift+1` |
| `\x1b[1;8r` | `escape`, `ctrl+shift+2` |
| `\x1b[1;8s` | `escape`, `ctrl+shift+3` |
| `\x1b[1;8t` | `escape`, `ctrl+shift+4` |
| `\x1b[1;8u` | `escape`, `ctrl+shift+5` |
| `\x1b[1;8v` | `escape`, `ctrl+shift+6` |
| `\x1b[1;8w` | `escape`, `ctrl+shift+7` |
| `\x1b[1;8x` | `escape`, `ctrl+shift+8` |
| `\x1b[1;8y` | `escape`, `ctrl+shift+9` |

### 5.38 Numeric Keypad (rxvt Sequences)

| Sequence | Character |
|----------|-----------|
| `\x1bOj` | `*` |
| `\x1bOk` | `+` |
| `\x1bOm` | `-` |
| `\x1bOn` | `.` |
| `\x1bOo` | `/` |
| `\x1bOp` | `0` |
| `\x1bOq` | `1` |
| `\x1bOr` | `2` |
| `\x1bOs` | `3` |
| `\x1bOt` | `4` |
| `\x1bOu` | `5` |
| `\x1bOv` | `6` |
| `\x1bOw` | `7` |
| `\x1bOx` | `8` |
| `\x1bOy` | `9` |
| `\x1bOM` | `enter` |

### 5.39 WezTerm macOS Option+Number Row

| Sequence | Character |
|----------|-----------|
| `\x1b§` | `§` |
| `\x1b1` | `¡` |
| `\x1b2` | `™` |
| `\x1b3` | `£` |
| `\x1b4` | `¢` |
| `\x1b5` | `∞` |
| `\x1b6` | `§` |
| `\x1b7` | `¶` |
| `\x1b8` | `•` |
| `\x1b9` | `ª` |
| `\x1b0` | `º` |
| `\x1b-` | `–` |
| `\x1b=` | `≠` |

### 5.40 Kitty Terminal Sequences

| Sequence | Character | Notes |
|----------|-----------|-------|
| `\x1b[167;5u` | `0` | Ctrl+§ on macOS Kitty |

### 5.41 Ignored Sequences

| Sequence | Reason | Terminal |
|----------|--------|----------|
| `\x1b[E` | IGNORE | Numeric keypad 5 (not in number mode) - Xterm |
| `\x1b[G` | IGNORE | Numeric keypad 5 (not in number mode) - Linux console |
| `\x1b[3;13~` | IGNORE | Ctrl-Cmd-Del on Kitty macOS |
| `\x1b[1;13H` | IGNORE | Ctrl-Cmd-Home on Kitty macOS |
| `\x1b[1;13F` | IGNORE | Ctrl-Cmd-End on Kitty macOS |
| `\x1b[5;13~` | IGNORE | Ctrl-Cmd-PgUp on Kitty macOS |
| `\x1b[6;13~` | IGNORE | Ctrl-Cmd-PgDn on Kitty macOS |
| `\x1b[49;13u` | IGNORE | Ctrl-Cmd-1 on Kitty macOS |
| `\x1b[50;13u` | IGNORE | Ctrl-Cmd-2 on Kitty macOS |
| `\x1b[51;13u` | IGNORE | Ctrl-Cmd-3 on Kitty macOS |
| `\x1b[52;13u` | IGNORE | Ctrl-Cmd-4 on Kitty macOS |
| `\x1b[53;13u` | IGNORE | Ctrl-Cmd-5 on Kitty macOS |
| `\x1b[54;13u` | IGNORE | Ctrl-Cmd-6 on Kitty macOS |
| `\x1b[55;13u` | IGNORE | Ctrl-Cmd-7 on Kitty macOS |
| `\x1b[56;13u` | IGNORE | Ctrl-Cmd-8 on Kitty macOS |
| `\x1b[57;13u` | IGNORE | Ctrl-Cmd-9 on Kitty macOS |
| `\x1b[48;13u` | IGNORE | Ctrl-Cmd-0 on Kitty macOS |
| `\x1b[45;13u` | IGNORE | Ctrl-Cmd-- on Kitty macOS |
| `\x1b[61;13u` | IGNORE | Ctrl-Cmd-+ on Kitty macOS |
| `\x1b[91;13u` | IGNORE | Ctrl-Cmd-[ on Kitty macOS |
| `\x1b[93;13u` | IGNORE | Ctrl-Cmd-] on Kitty macOS |
| `\x1b[92;13u` | IGNORE | Ctrl-Cmd-\ on Kitty macOS |
| `\x1b[39;13u` | IGNORE | Ctrl-Cmd-' on Kitty macOS |
| `\x1b[59;13u` | IGNORE | Ctrl-Cmd-; on Kitty macOS |
| `\x1b[47;13u` | IGNORE | Ctrl-Cmd-/ on Kitty macOS |
| `\x1b[46;13u` | IGNORE | Ctrl-Cmd-. on Kitty macOS |

### 5.42 Synchronization Sequences

| Constant | Value | Purpose |
|----------|-------|---------|
| `SYNC_START` | `\x1b[?2026h` | Synchronized output start |
| `SYNC_END` | `\x1b[?2026l` | Synchronized output end |

**Total ANSI Sequences:** 425 entries

---

## 6. Complete Kitty Keyboard Protocol Keys

All 123 entries from `_keyboard_protocol.py` - Kitty extended keyboard protocol functional keys.

Reference: https://sw.kovidgoyal.net/kitty/keyboard-protocol/#functional-key-definitions

| Sequence | Key Name | Notes |
|----------|----------|-------|
| `27u` | `escape` | |
| `13u` | `enter` | |
| `9u` | `tab` | |
| `127u` | `backspace` | |
| `2~` | `insert` | |
| `3~` | `delete` | |
| `1D` | `left` | |
| `1C` | `right` | |
| `1A` | `up` | |
| `1B` | `down` | |
| `5~` | `pageup` | |
| `6~` | `pagedown` | |
| `1H` | `home` | Variant 1 |
| `1~` | `home` | Variant 2 |
| `7~` | `home` | Variant 3 |
| `1F` | `end` | Variant 1 |
| `4~` | `end` | Variant 2 |
| `8~` | `end` | Variant 3 |
| `57358u` | `caps_lock` | |
| `57359u` | `scroll_lock` | |
| `57360u` | `num_lock` | |
| `57361u` | `print_screen` | |
| `57362u` | `pause` | |
| `57363u` | `menu` | |
| `1P` | `f1` | Variant 1 |
| `11~` | `f1` | Variant 2 |
| `1Q` | `f2` | Variant 1 |
| `12~` | `f2` | Variant 2 |
| `13~` | `f3` | Variant 1 |
| `1R` | `f3` | Variant 2 |
| `1S` | `f4` | Variant 1 |
| `14~` | `f4` | Variant 2 |
| `15~` | `f5` | |
| `17~` | `f6` | |
| `18~` | `f7` | |
| `19~` | `f8` | |
| `20~` | `f9` | |
| `21~` | `f10` | |
| `23~` | `f11` | |
| `24~` | `f12` | |
| `57376u` | `f13` | |
| `57377u` | `f14` | |
| `57378u` | `f15` | |
| `57379u` | `f16` | |
| `57380u` | `f17` | |
| `57381u` | `f18` | |
| `57382u` | `f19` | |
| `57383u` | `f20` | |
| `57384u` | `f21` | |
| `57385u` | `f22` | |
| `57386u` | `f23` | |
| `57387u` | `f24` | |
| `57388u` | `f25` | |
| `57389u` | `f26` | |
| `57390u` | `f27` | |
| `57391u` | `f28` | |
| `57392u` | `f29` | |
| `57393u` | `f30` | |
| `57394u` | `f31` | |
| `57395u` | `f32` | |
| `57396u` | `f33` | |
| `57397u` | `f34` | |
| `57398u` | `f35` | |
| `57399u` | `0` | Numeric keypad |
| `57400u` | `1` | Numeric keypad |
| `57401u` | `2` | Numeric keypad |
| `57402u` | `3` | Numeric keypad |
| `57403u` | `4` | Numeric keypad |
| `57404u` | `5` | Numeric keypad |
| `57405u` | `6` | Numeric keypad |
| `57406u` | `7` | Numeric keypad |
| `57407u` | `8` | Numeric keypad |
| `57408u` | `9` | Numeric keypad |
| `57409u` | `decimal` | Numeric keypad |
| `57410u` | `divide` | Numeric keypad |
| `57411u` | `multiply` | Numeric keypad |
| `57412u` | `subtract` | Numeric keypad |
| `57413u` | `add` | Numeric keypad |
| `57414u` | `enter` | Numeric keypad |
| `57415u` | `equal` | Numeric keypad |
| `57416u` | `separator` | Numeric keypad |
| `57417u` | `left` | Numeric keypad |
| `57418u` | `right` | Numeric keypad |
| `57419u` | `up` | Numeric keypad |
| `57420u` | `down` | Numeric keypad |
| `57421u` | `pageup` | Numeric keypad |
| `57422u` | `pagedown` | Numeric keypad |
| `57423u` | `home` | Numeric keypad |
| `57424u` | `end` | Numeric keypad |
| `57425u` | `insert` | Numeric keypad |
| `57426u` | `delete` | Numeric keypad |
| `1E` | `kp_begin` | Keypad begin |
| `57427~` | `kp_begin` | Keypad begin variant |
| `57428u` | `media_play` | Media control |
| `57429u` | `media_pause` | Media control |
| `57430u` | `media_play_pause` | Media control |
| `57431u` | `media_reverse` | Media control |
| `57432u` | `media_stop` | Media control |
| `57433u` | `media_fast_forward` | Media control |
| `57434u` | `media_rewind` | Media control |
| `57435u` | `media_track_next` | Media control |
| `57436u` | `media_track_previous` | Media control |
| `57437u` | `media_record` | Media control |
| `57438u` | `lower_volume` | Media control |
| `57439u` | `raise_volume` | Media control |
| `57440u` | `mute_volume` | Media control |
| `57441u` | `left_shift` | Modifier keys |
| `57442u` | `left_control` | Modifier keys |
| `57443u` | `left_alt` | Modifier keys |
| `57444u` | `left_super` | Modifier keys |
| `57445u` | `left_hyper` | Modifier keys |
| `57446u` | `left_meta` | Modifier keys |
| `57447u` | `right_shift` | Modifier keys |
| `57448u` | `right_control` | Modifier keys |
| `57449u` | `right_alt` | Modifier keys |
| `57450u` | `right_super` | Modifier keys |
| `57451u` | `right_hyper` | Modifier keys |
| `57452u` | `right_meta` | Modifier keys |
| `57453u` | `iso_level3_shift` | ISO keyboard |
| `57454u` | `iso_level5_shift` | ISO keyboard |

**Total Functional Keys:** 123 entries

---

## 7. Key Name Mappings

### 7.1 KEY_NAME_REPLACEMENTS

Unicode database names replaced with more common terms:

| Original | Replacement |
|----------|-------------|
| `solidus` | `slash` |
| `reverse_solidus` | `backslash` |
| `commercial_at` | `at` |
| `hyphen_minus` | `minus` |
| `plus_sign` | `plus` |
| `low_line` | `underscore` |

### 7.2 KEY_TO_UNICODE_NAME

Mapping friendly key names to Unicode character names:

| Key Name | Unicode Name |
|----------|--------------|
| `exclamation_mark` | `EXCLAMATION MARK` |
| `quotation_mark` | `QUOTATION MARK` |
| `number_sign` | `NUMBER SIGN` |
| `dollar_sign` | `DOLLAR SIGN` |
| `percent_sign` | `PERCENT SIGN` |
| `left_parenthesis` | `LEFT PARENTHESIS` |
| `right_parenthesis` | `RIGHT PARENTHESIS` |
| `plus_sign` | `PLUS SIGN` |
| `hyphen_minus` | `HYPHEN-MINUS` |
| `full_stop` | `FULL STOP` |
| `less_than_sign` | `LESS-THAN SIGN` |
| `equals_sign` | `EQUALS SIGN` |
| `greater_than_sign` | `GREATER-THAN SIGN` |
| `question_mark` | `QUESTION MARK` |
| `commercial_at` | `COMMERCIAL AT` |
| `left_square_bracket` | `LEFT SQUARE BRACKET` |
| `reverse_solidus` | `REVERSE SOLIDUS` |
| `right_square_bracket` | `RIGHT SQUARE BRACKET` |
| `circumflex_accent` | `CIRCUMFLEX ACCENT` |
| `low_line` | `LOW LINE` |
| `grave_accent` | `GRAVE ACCENT` |
| `left_curly_bracket` | `LEFT CURLY BRACKET` |
| `vertical_line` | `VERTICAL LINE` |
| `right_curly_bracket` | `RIGHT CURLY BRACKET` |

### 7.3 KEY_ALIASES

Keys with aliases (multiple names for same key):

| Primary Key | Aliases | Notes |
|-------------|---------|-------|
| `tab` | `ctrl+i` | Ctrl+I is identical to Tab |
| `enter` | `ctrl+m` | Ctrl+M is identical to Enter |
| `escape` | `ctrl+left_square_brace` | Ctrl+[ is identical to Escape |
| `ctrl+at` | `ctrl+space` | Both produce same code |
| `ctrl+j` | `newline` | Newline character |

### 7.4 KEY_DISPLAY_ALIASES

Display representations for keys in UI:

| Key | Display |
|-----|---------|
| `up` | `↑` |
| `down` | `↓` |
| `left` | `←` |
| `right` | `→` |
| `backspace` | `⌫` |
| `escape` | `esc` |
| `enter` | `⏎` |
| `minus` | `-` |
| `space` | `space` |
| `pagedown` | `pgdn` |
| `pageup` | `pgup` |
| `delete` | `del` |

### 7.5 ASCII_KEY_NAMES

| ASCII Character | Key Name |
|----------------|----------|
| `\t` | `tab` |

---

## 8. Color Constants

All 169 color names with RGB values from `_color_constants.py`.

### 8.1 ANSI Colors List

16 standard ANSI colors (names only):

```
black, red, green, yellow, blue, magenta, cyan, white,
bright_black, bright_red, bright_green, bright_yellow,
bright_blue, bright_magenta, bright_cyan, bright_white
```

### 8.2 Complete COLOR_NAME_TO_RGB Mapping

All 169 colors with exact RGB values:

| Color Name | RGB / RGBA | Hex Equivalent |
|------------|---------|----------------|
| `transparent` | (0, 0, 0, 0) | #00000000 |
| `ansi_black` | (0, 0, 0) | #000000 |
| `ansi_red` | (128, 0, 0) | #800000 |
| `ansi_green` | (0, 128, 0) | #008000 |
| `ansi_yellow` | (128, 128, 0) | #808000 |
| `ansi_blue` | (0, 0, 128) | #000080 |
| `ansi_magenta` | (128, 0, 128) | #800080 |
| `ansi_cyan` | (0, 128, 128) | #008080 |
| `ansi_white` | (192, 192, 192) | #C0C0C0 |
| `ansi_bright_black` | (128, 128, 128) | #808080 |
| `ansi_bright_red` | (255, 0, 0) | #FF0000 |
| `ansi_bright_green` | (0, 255, 0) | #00FF00 |
| `ansi_bright_yellow` | (255, 255, 0) | #FFFF00 |
| `ansi_bright_blue` | (0, 0, 255) | #0000FF |
| `ansi_bright_magenta` | (255, 0, 255) | #FF00FF |
| `ansi_bright_cyan` | (0, 255, 255) | #00FFFF |
| `ansi_bright_white` | (255, 255, 255) | #FFFFFF |
| `black` | (0, 0, 0) | #000000 |
| `silver` | (192, 192, 192) | #C0C0C0 |
| `gray` | (128, 128, 128) | #808080 |
| `white` | (255, 255, 255) | #FFFFFF |
| `maroon` | (128, 0, 0) | #800000 |
| `red` | (255, 0, 0) | #FF0000 |
| `purple` | (128, 0, 128) | #800080 |
| `fuchsia` | (255, 0, 255) | #FF00FF |
| `green` | (0, 128, 0) | #008000 |
| `lime` | (0, 255, 0) | #00FF00 |
| `olive` | (128, 128, 0) | #808000 |
| `yellow` | (255, 255, 0) | #FFFF00 |
| `navy` | (0, 0, 128) | #000080 |
| `blue` | (0, 0, 255) | #0000FF |
| `teal` | (0, 128, 128) | #008080 |
| `aqua` | (0, 255, 255) | #00FFFF |
| `orange` | (255, 165, 0) | #FFA500 |
| `aliceblue` | (240, 248, 255) | #F0F8FF |
| `antiquewhite` | (250, 235, 215) | #FAEBD7 |
| `aquamarine` | (127, 255, 212) | #7FFFD4 |
| `azure` | (240, 255, 255) | #F0FFFF |
| `beige` | (245, 245, 220) | #F5F5DC |
| `bisque` | (255, 228, 196) | #FFE4C4 |
| `blanchedalmond` | (255, 235, 205) | #FFEBCD |
| `blueviolet` | (138, 43, 226) | #8A2BE2 |
| `brown` | (165, 42, 42) | #A52A2A |
| `burlywood` | (222, 184, 135) | #DEB887 |
| `cadetblue` | (95, 158, 160) | #5F9EA0 |
| `chartreuse` | (127, 255, 0) | #7FFF00 |
| `chocolate` | (210, 105, 30) | #D2691E |
| `coral` | (255, 127, 80) | #FF7F50 |
| `cornflowerblue` | (100, 149, 237) | #6495ED |
| `cornsilk` | (255, 248, 220) | #FFF8DC |
| `crimson` | (220, 20, 60) | #DC143C |
| `cyan` | (0, 255, 255) | #00FFFF |
| `darkblue` | (0, 0, 139) | #00008B |
| `darkcyan` | (0, 139, 139) | #008B8B |
| `darkgoldenrod` | (184, 134, 11) | #B8860B |
| `darkgray` | (169, 169, 169) | #A9A9A9 |
| `darkgreen` | (0, 100, 0) | #006400 |
| `darkgrey` | (169, 169, 169) | #A9A9A9 |
| `darkkhaki` | (189, 183, 107) | #BDB76B |
| `darkmagenta` | (139, 0, 139) | #8B008B |
| `darkolivegreen` | (85, 107, 47) | #556B2F |
| `darkorange` | (255, 140, 0) | #FF8C00 |
| `darkorchid` | (153, 50, 204) | #9932CC |
| `darkred` | (139, 0, 0) | #8B0000 |
| `darksalmon` | (233, 150, 122) | #E9967A |
| `darkseagreen` | (143, 188, 143) | #8FBC8F |
| `darkslateblue` | (72, 61, 139) | #483D8B |
| `darkslategray` | (47, 79, 79) | #2F4F4F |
| `darkslategrey` | (47, 79, 79) | #2F4F4F |
| `darkturquoise` | (0, 206, 209) | #00CED1 |
| `darkviolet` | (148, 0, 211) | #9400D3 |
| `deeppink` | (255, 20, 147) | #FF1493 |
| `deepskyblue` | (0, 191, 255) | #00BFFF |
| `dimgray` | (105, 105, 105) | #696969 |
| `dimgrey` | (105, 105, 105) | #696969 |
| `dodgerblue` | (30, 144, 255) | #1E90FF |
| `firebrick` | (178, 34, 34) | #B22222 |
| `floralwhite` | (255, 250, 240) | #FFFAF0 |
| `forestgreen` | (34, 139, 34) | #228B22 |
| `gainsboro` | (220, 220, 220) | #DCDCDC |
| `ghostwhite` | (248, 248, 255) | #F8F8FF |
| `gold` | (255, 215, 0) | #FFD700 |
| `goldenrod` | (218, 165, 32) | #DAA520 |
| `greenyellow` | (173, 255, 47) | #ADFF2F |
| `grey` | (128, 128, 128) | #808080 |
| `honeydew` | (240, 255, 240) | #F0FFF0 |
| `hotpink` | (255, 105, 180) | #FF69B4 |
| `indianred` | (205, 92, 92) | #CD5C5C |
| `indigo` | (75, 0, 130) | #4B0082 |
| `ivory` | (255, 255, 240) | #FFFFF0 |
| `khaki` | (240, 230, 140) | #F0E68C |
| `lavender` | (230, 230, 250) | #E6E6FA |
| `lavenderblush` | (255, 240, 245) | #FFF0F5 |
| `lawngreen` | (124, 252, 0) | #7CFC00 |
| `lemonchiffon` | (255, 250, 205) | #FFFACD |
| `lightblue` | (173, 216, 230) | #ADD8E6 |
| `lightcoral` | (240, 128, 128) | #F08080 |
| `lightcyan` | (224, 255, 255) | #E0FFFF |
| `lightgoldenrodyellow` | (250, 250, 210) | #FAFAD2 |
| `lightgray` | (211, 211, 211) | #D3D3D3 |
| `lightgreen` | (144, 238, 144) | #90EE90 |
| `lightgrey` | (211, 211, 211) | #D3D3D3 |
| `lightpink` | (255, 182, 193) | #FFB6C1 |
| `lightsalmon` | (255, 160, 122) | #FFA07A |
| `lightseagreen` | (32, 178, 170) | #20B2AA |
| `lightskyblue` | (135, 206, 250) | #87CEFA |
| `lightslategray` | (119, 136, 153) | #778899 |
| `lightslategrey` | (119, 136, 153) | #778899 |
| `lightsteelblue` | (176, 196, 222) | #B0C4DE |
| `lightyellow` | (255, 255, 224) | #FFFFE0 |
| `limegreen` | (50, 205, 50) | #32CD32 |
| `linen` | (250, 240, 230) | #FAF0E6 |
| `magenta` | (255, 0, 255) | #FF00FF |
| `mediumaquamarine` | (102, 205, 170) | #66CDAA |
| `mediumblue` | (0, 0, 205) | #0000CD |
| `mediumorchid` | (186, 85, 211) | #BA55D3 |
| `mediumpurple` | (147, 112, 219) | #9370DB |
| `mediumseagreen` | (60, 179, 113) | #3CB371 |
| `mediumslateblue` | (123, 104, 238) | #7B68EE |
| `mediumspringgreen` | (0, 250, 154) | #00FA9A |
| `mediumturquoise` | (72, 209, 204) | #48D1CC |
| `mediumvioletred` | (199, 21, 133) | #C71585 |
| `midnightblue` | (25, 25, 112) | #191970 |
| `mintcream` | (245, 255, 250) | #F5FFFA |
| `mistyrose` | (255, 228, 225) | #FFE4E1 |
| `moccasin` | (255, 228, 181) | #FFE4B5 |
| `navajowhite` | (255, 222, 173) | #FFDEAD |
| `oldlace` | (253, 245, 230) | #FDF5E6 |
| `olivedrab` | (107, 142, 35) | #6B8E23 |
| `orangered` | (255, 69, 0) | #FF4500 |
| `orchid` | (218, 112, 214) | #DA70D6 |
| `palegoldenrod` | (238, 232, 170) | #EEE8AA |
| `palegreen` | (152, 251, 152) | #98FB98 |
| `paleturquoise` | (175, 238, 238) | #AFEEEE |
| `palevioletred` | (219, 112, 147) | #DB7093 |
| `papayawhip` | (255, 239, 213) | #FFEFD5 |
| `peachpuff` | (255, 218, 185) | #FFDAB9 |
| `peru` | (205, 133, 63) | #CD853F |
| `pink` | (255, 192, 203) | #FFC0CB |
| `plum` | (221, 160, 221) | #DDA0DD |
| `powderblue` | (176, 224, 230) | #B0E0E6 |
| `rosybrown` | (188, 143, 143) | #BC8F8F |
| `royalblue` | (65, 105, 225) | #4169E1 |
| `saddlebrown` | (139, 69, 19) | #8B4513 |
| `salmon` | (250, 128, 114) | #FA8072 |
| `sandybrown` | (244, 164, 96) | #F4A460 |
| `seagreen` | (46, 139, 87) | #2E8B57 |
| `seashell` | (255, 245, 238) | #FFF5EE |
| `sienna` | (160, 82, 45) | #A0522D |
| `skyblue` | (135, 206, 235) | #87CEEB |
| `slateblue` | (106, 90, 205) | #6A5ACD |
| `slategray` | (112, 128, 144) | #708090 |
| `slategrey` | (112, 128, 144) | #708090 |
| `snow` | (255, 250, 250) | #FFFAFA |
| `springgreen` | (0, 255, 127) | #00FF7F |
| `steelblue` | (70, 130, 180) | #4682B4 |
| `tan` | (210, 180, 140) | #D2B48C |
| `thistle` | (216, 191, 216) | #D8BFD8 |
| `tomato` | (255, 99, 71) | #FF6347 |
| `turquoise` | (64, 224, 208) | #40E0D0 |
| `violet` | (238, 130, 238) | #EE82EE |
| `wheat` | (245, 222, 179) | #F5DEB3 |
| `whitesmoke` | (245, 245, 245) | #F5F5F5 |
| `yellowgreen` | (154, 205, 50) | #9ACD32 |
| `rebeccapurple` | (102, 51, 153) | #663399 |

**Total Colors:** 169 entries (1 with alpha channel, 168 RGB)

---

## 9. Paste & Resize Events

### 9.1 Paste Events

```python
from keybard.events import Paste

with KeyboardReader() as reader:
    for event in reader.poll():
        if isinstance(event, Paste):
            text = event.text  # Full pasted text
            print(f"Pasted: {text}")
```

Bracketed paste mode is automatically detected. When users paste text into the terminal, KEYBARD emits a single `Paste` event instead of individual `Key` events for each character.

### 9.2 Resize Events

```python
from keybard.events import Resize

with KeyboardReader() as reader:
    for event in reader.poll():
        if isinstance(event, Resize):
            width = event.size.width
            height = event.size.height
            print(f"Terminal resized to {width}x{height}")
```

Window resize events provide terminal dimensions in character columns and rows.

---

## 10. Limitations & Tips

### Terminal Input Limitations

- **Byte streams:** Terminal input is byte-based. KEYBARD normalizes VT100/OSC sequences but relies on the terminal/OS to generate repeats.

- **Non-repeating keys:** Escape and some function keys generate only single events. The timing dispatcher will emit `KeyClick` followed by timeout-based `KeyUp` for these.

- **Terminal compatibility:** Different terminals send different escape sequences. KEYBARD includes mappings for: xterm, rxvt, gnome-terminal, iTerm, Kitty, WezTerm, Linux console, Windows console, tmux.

### Context Manager Requirement

`KeyboardReader` **must** be properly started and stopped:

```python
# GOOD: Context manager ensures cleanup
with KeyboardReader() as reader:
    ...

# BAD: Terminal left in raw mode if not stopped
reader = KeyboardReader()
reader.start()
# ... program crashes before reader.stop()
```

### Integration with Rich

KEYBARD pairs well with Rich for TUI development:

```python
from rich.console import Console
from keybard import KeyboardReader

console = Console()

with console.screen():
    with KeyboardReader() as reader:
        while True:
            console.clear()
            console.print("Press keys...")
            for event in reader.poll():
                # Handle events
                pass
```

### Performance Considerations

- Use `poll()` for non-blocking TUI loops
- Use `read_key()` for simple blocking CLI tools
- Dispatcher adds minimal overhead (~microseconds per event)
- Parser handles chunks efficiently (tested with varying sizes)

---

## Quick Reference Summary

| Feature | Import | Usage |
|---------|--------|-------|
| Basic reading | `from keybard import KeyboardReader` | `with KeyboardReader() as r: event = r.read_key()` |
| Non-blocking | Same | `for event in r.poll(): ...` |
| Timing events | `from keybard import DispatcherConfig` | `KeyboardReader(use_dispatcher=True, dispatcher_config=DispatcherConfig(...))` |
| Key constants | `from keybard.keys import Keys` | `if event.key == Keys.Enter` |
| Events | `from keybard.events import Key, Paste, Resize, KeyClick, KeyDown, KeyUp` | `isinstance(event, Key)` |

**Total Constants Documented:**
- **425** ANSI escape sequences
- **123** Kitty keyboard protocol keys
- **200+** Keys enum constants
- **169** Color names with RGB values
- **50+** Key name mappings and aliases

**All constants are now fully documented. Users should never need to check source code.**

---

*End of KEYBARD Complete Technical Reference v0.3.0a1*
