# KEYBARD Dispatcher - Technical Architecture & Input Model

This document explains how KEYBARD's timing-based event dispatcher works within
the constraints of terminal input architecture.

---

## Terminal Input Architecture Position

### Where KEYBARD Operates

**Input Layer:** TTY/Terminal Escape Sequences (ANSI/XTerm)

```
Hardware → OS Kernel → Terminal Driver → TTY → Escape Sequences → KEYBARD Parser
                                                                         ↓
                                                                   Dispatcher
```

### What We Receive (TTY Layer)

From the terminal, we receive:
- ✅ **Escape sequences** when keys are pressed
- ✅ **Repeat sequences** when keys are held (OS key repeat)
- ❌ **NO explicit key release events** (TTY limitation)
- ❌ **NO hardware state information**

**Critical Constraint:** As documented in terminal input architecture:
> "Unix TTY (termios/curses): Bytes/escape seq on press + **No key-up** concept"
> "TTY delivers characters, not hardware state"

---

## OS Key Repeat Behavior (What We Use)

### Bucket 3: Repetition - "OS key repeat (global setting)"

| Attribute | Value |
|-----------|-------|
| **What repeats** | Repeated **text** events; often repeated **keydown** notifications (toolkit-dependent) after initial delay |
| **Control** | User sets delay/rate system-wide |
| **Enable/Disable** | System preferences; not per-key in your app |
| **Use/Gotchas** | "Great for typing `wwww`; unreliable for movement—ignore for controls" |

### How It Works

1. **User presses key** → First escape sequence arrives
2. **User holds key** → After OS delay (~500ms default):
   - OS starts sending **repeat** escape sequences
   - Repeat rate: typically 15-30/sec (OS configured)
3. **User releases key** → Repeats stop (no explicit release event)

### Which Keys Repeat

**Keys WITH OS Repetition:**
- ✅ Letters (a-z, A-Z)
- ✅ Numbers (0-9)
- ✅ Arrow keys (Up, Down, Left, Right)
- ✅ Punctuation/symbols
- ✅ Backspace, Delete
- ✅ Space, Tab, Enter

**Keys WITHOUT OS Repetition:**
- ❌ Modifiers alone (Ctrl, Alt, Shift, Meta)
- ❌ Escape key (usually)
- ❌ Some function keys (F1-F12, varies by OS)
- ❌ Some special keys (varies by terminal)

**Modifier Combinations:**
- ✅ Ctrl+A, Shift+Arrow, etc. → **Will repeat** if base key repeats
- ❌ Ctrl alone → **Won't repeat**

---

## Dispatcher Detection Strategy

### State Machine

```
Key Press → [PRESSED state]
              ↓
              ├─ No repeat for `delta` seconds → emit KeyClick
              │
              └─ Repeat arrives → [HELD state] → emit KeyDown
                                      ↓
                                      ├─ Repeats continue → (optional: emit more KeyDown)
                                      │
                                      └─ No repeat for `release_timeout` → emit KeyUp
```

### Timing Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `delta` | 1.0s | Click vs hold threshold |
| `release_timeout` | 0.15s | Time to wait for repeat to detect release |
| `emit_repeats` | False | Emit KeyDown on each repeat |
| `repeat_interval` | 0.05s | Min time between repeat emissions |

### Inference Logic

**KeyClick Detection:**
```
IF first_sequence_arrives:
    start_timer(delta)
    IF timer_expires AND no_repeat_received:
        → emit KeyClick (user tapped and released)
```

**KeyDown Detection:**
```
IF first_sequence_arrives THEN second_sequence_arrives:
    → repeat detected → key is held
    → emit KeyDown (with hold_time)
```

**KeyUp Detection:**
```
IF in_HELD_state AND no_repeat_for(release_timeout):
    → repeats stopped → key was released
    → emit KeyUp (with total_duration)
```

---

## Limitations & Workarounds

### Limitation 1: Keys Without OS Repeat

**Problem:**
Keys that don't generate OS repeats (Escape, modifiers alone) will:
- Always emit **KeyClick** after `delta` timeout
- Even if still physically held down
- Cannot detect true hold duration

**Why:**
- TTY doesn't provide key-up events
- OS doesn't repeat these keys
- We have no way to know the key is still held

**Workaround:**
- Use raw `Key` events (default mode without dispatcher)
- Accept KeyClick behavior
- Use system hooks if true up/down needed (see below)

### Limitation 2: No True Key Release Detection

**Problem:**
We infer release by **absence of repeats**, not an explicit release event.

**Implications:**
- `release_timeout` (default 0.15s) determines detection latency
- If OS repeat rate is very slow, detection might be delayed
- If user releases during OS repeat delay, we might not detect it until the next expected repeat doesn't arrive

**Workaround:**
- Tune `release_timeout` for your use case
- Accept the inherent latency (fundamental to terminal input)

### Limitation 3: Modifier State Unknown

**Problem:**
When Ctrl+A is held, we receive repeated "ctrl+a" sequences, but:
- We don't know if Ctrl is still physically held when 'a' releases
- We don't know if 'a' is still held when Ctrl releases

**Why:**
Terminal escape sequences combine modifiers with keys:
- We get: `ctrl+a`, `ctrl+a`, `ctrl+a`, ...
- Not: `ctrl_down`, `a_down`, `a_repeat`, `a_up`, `ctrl_up`

**Workaround:**
- Treat modifier combinations as atomic units
- Accept that release timing is coarse-grained

---

## Alternative: True Key Up/Down Detection

If you need **real hardware-level key up/down events** in a terminal application,
you must use system-level hooks:

### Linux
```python
from evdev import InputDevice, categorize, ecodes

dev = InputDevice('/dev/input/event0')
for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        if event.value == 1:   # Key down
            print(f'Down: {event.code}')
        elif event.value == 0:  # Key up
            print(f'Up: {event.code}')
```

**Requirements:**
- Root or proper udev permissions
- Access to `/dev/input/event*`
- System-wide hook (affects all inputs)

### Windows
```python
import ctypes
# Use ReadConsoleInputW for KEY_EVENT_RECORD with bKeyDown flag

# OR use higher-level library:
import keyboard
keyboard.on_press(lambda e: print(f'Down: {e.name}'))
keyboard.on_release(lambda e: print(f'Up: {e.name}'))
```

**Requirements:**
- Console INPUT API access or admin privileges
- Global hook

### macOS
```python
from pynput import keyboard

def on_press(key):
    print(f'Down: {key}')

def on_release(key):
    print(f'Up: {key}')

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
```

**Requirements:**
- Accessibility permissions
- System-wide hook

### Why KEYBARD Doesn't Use These

1. **Scope:** KEYBARD is a **terminal input library**, not a system-wide input hook
2. **Permissions:** System hooks require elevated privileges
3. **Compatibility:** TTY-based approach works over SSH, in containers, etc.
4. **Purpose:** Most terminal applications don't need hardware-level state

---

## Design Rationale

### Why This Approach?

**Advantages:**
- ✅ Works in pure terminal environment (no GUI, no system hooks)
- ✅ Works over SSH/remote connections
- ✅ No special permissions required
- ✅ Cross-platform (Linux, macOS, Windows)
- ✅ Uses standard terminal capabilities
- ✅ Good enough for most use cases (typing, TUI apps)

**Trade-offs:**
- ❌ No true key release events
- ❌ Dependent on OS key repeat settings
- ❌ Latency in release detection
- ❌ Keys without repeat cannot be detected as held

### Best Use Cases

**Good for:**
- Text input with timing (quick vs deliberate typing)
- TUI applications with key hold features
- vim-style hold-to-repeat (j/k scrolling)
- Distinguishing taps from holds (where repeat exists)

**Not suitable for:**
- Precise game controls (use system hooks or SDL)
- Real-time action games requiring frame-perfect input
- Applications needing modifier state tracking
- Anything requiring detection of non-repeating key holds

---

## Comparison with Other Input Models

| Feature | KEYBARD Dispatcher | System Hooks (evdev/pynput) | GUI Toolkit (Tk/Qt) |
|---------|-------------------|----------------------------|---------------------|
| True key up/down | ❌ (inferred) | ✅ | ✅ |
| Works in terminal | ✅ | ✅ | ❌ (needs window) |
| Works over SSH | ✅ | ❌ | ❌ |
| Needs permissions | ❌ | ✅ (root/admin) | ❌ |
| Latency | ~150ms | ~0ms | ~0ms |
| Keys without repeat | ❌ | ✅ | ✅ |
| Cross-platform | ✅ | ⚠️ (platform-specific code) | ✅ |

---

## References

### Input Architecture Buckets

1. **Text arrives without keydown:** IME, dead keys, paste, autocorrect
2. **Keydown without text:** Modifiers, navigation, function keys
3. **Repetition scenarios:** OS repeat, toolkit repeat, app-level hold loop

### Terminal Limitations (from architecture docs)

> "Unix TTY (termios/curses): Bytes/escape seq on press + **No key-up** concept"
> "TTY delivers characters, not hardware state"
> "If you need real up/down in a terminal app, use a system hook"

### KEYBARD's Position

- **Input source:** TTY escape sequences (Bucket 2 + Bucket 3)
- **Detection method:** OS key repeat pattern analysis
- **Trade-off:** Simplicity & compatibility vs. precision

---

## Conclusion

KEYBARD's dispatcher provides **best-effort timing-based events** within the
constraints of terminal input architecture. It's designed for:

- ✅ TUI applications that benefit from hold detection
- ✅ Environments where system hooks aren't feasible
- ✅ Use cases where ~150ms latency is acceptable

For applications requiring **hardware-level precision**, use system hooks or
GUI toolkits instead.

---

_Document Version: 1.0_  
_Date: 2025-10-18_  
_Author: Claude Code + User Input Architecture Documentation_
