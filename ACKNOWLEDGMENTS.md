# Acknowledgments

## Textual Framework

KEYBARD's core keyboard parsing engine is derived from the [Textual](https://github.com/Textualize/textual) framework, created by Will McGugan and the team at Textualize.io.

### What We Extracted

The following components were adapted from Textual:

1. **XTerm Parser** (`_xterm_parser.py`)
   - State machine-based ANSI escape sequence parser
   - Handles partial sequences across multiple input chunks
   - Timeout-based disambiguation (e.g., ESC key vs escape sequence start)
   - Bracketed paste mode support
   - Mouse event parsing (removed in KEYBARD)
   - Terminal capability detection and mode reporting

2. **Key System** (`keys.py`)
   - Comprehensive key enumeration (Keys enum)
   - Key name normalization and aliasing
   - Unicode character to key name mapping
   - Modifier combination handling (Ctrl, Alt, Shift, Meta)
   - Key display formatting

3. **Terminal Drivers** (`drivers/`)
   - **LinuxDriver**: Unix-like terminal support via termios/tty
   - **WindowsDriver**: Windows Console API integration
   - **HeadlessDriver**: Non-interactive testing/CI support
   - **WebDriver**: Browser-based terminal emulation
   - Signal handling (SIGWINCH, SIGTSTP, SIGCONT)
   - Threading model for non-blocking I/O

4. **Event System** (`events.py`)
   - Base Event class hierarchy
   - Key events with modifier tracking
   - Paste events for bracketed paste mode
   - Resize events with pixel-accurate dimensions
   - Focus events (AppFocus/AppBlur)
   - Terminal capability reporting events

5. **Supporting Infrastructure**
   - Color system (`color.py`)
   - Geometry primitives (`geometry.py`)
   - Filter system for line processing (`filter.py`)

### Original Textual License

The original Textual framework is licensed under the MIT License:

```
MIT License

Copyright (c) 2020-2024 Will McGugan and Textualize.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### What KEYBARD Changed

KEYBARD is a focused extraction with the following modifications:

- **Removed mouse support**: KEYBARD is keyboard-only
- **Removed TUI framework**: No widgets, layouts, or rendering system
- **Removed syntax highlighting**: No tree-sitter parsers or code highlighting
- **Simplified API**: Three main methods instead of full application framework
- **Standalone operation**: No dependency on Textual's app lifecycle or message pump
- **Enhanced examples**: Added comprehensive key display demo with state tracking

### Why This Matters

The Textual framework is a comprehensive, production-grade TUI (Text User Interface) framework. Its terminal input handling has been battle-tested across:

- Dozens of terminal emulators (iTerm2, Terminal.app, Windows Terminal, Alacritty, Kitty, etc.)
- Multiple operating systems (Linux, macOS, Windows)
- Edge cases in ANSI escape sequence parsing
- Real-world applications used by thousands of developers

By extracting and focusing solely on the keyboard input components, KEYBARD inherits this robustness while providing a lightweight, single-purpose library for developers who need reliable keyboard input without the full TUI framework.

## Why Use Textual's Code?

1. **Battle-tested**: Used in production by many applications
2. **Cross-platform**: Works reliably on Linux, macOS, Windows
3. **Edge-case handling**: Handles terminal quirks and incompatibilities
4. **Actively maintained**: Textual is actively developed and improved
5. **High-quality**: Well-documented, well-tested, professionally maintained

## Links

- **Textual Framework**: https://github.com/Textualize/textual
- **Textual Documentation**: https://textual.textualize.io/
- **Textualize.io**: https://www.textualize.io/
- **Will McGugan**: https://github.com/willmcgugan

## Thank You

A huge thank you to Will McGugan (@willmcgugan) and the entire Textualize team for creating and maintaining Textual. Their work on terminal handling has benefited the entire Python community, and KEYBARD is proud to build upon their foundation.

If you need a full-featured TUI framework with widgets, layouts, CSS styling, and more, please use [Textual](https://github.com/Textualize/textual) directly. KEYBARD is only for those who need lightweight, keyboard-only input handling.

---

**KEYBARD Maintainer**: Emasoft (https://github.com/Emasoft)
**KEYBARD License**: MIT (see LICENSE file)
**Original Textual Code**: Copyright (c) 2020-2024 Will McGugan and Textualize.io
**KEYBARD Adaptation**: Copyright (c) 2025 Emasoft
