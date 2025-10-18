# Changelog

All notable changes to KEYBARD will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0a1] - 2025-10-18 (Alpha)

### Added
- Initial release of KEYBARD as standalone keyboard input library
- Cross-platform keyboard input support (Linux, macOS, Windows)
- Battle-tested XTerm parser extracted from Textual framework
- Three operational modes: blocking (`read_key()`), non-blocking (`poll()`), and callback-based (`run()`)
- Support for special keys, modifiers, and key combinations
- Bracketed paste event detection
- Focus event detection (AppFocus/AppBlur)
- Resize event detection with pixel-accurate dimensions (when supported)
- Comprehensive key display example (`examples/key_display.py`) with:
  - Real-time event visualization
  - State tracking (CLICK/KEY-DOWN/KEY-UP)
  - Millisecond-precision timestamps
  - Color-coded display for different key types
  - Scrolling history of last 15 events

### Changed
- Focused codebase: Removed mouse support (keyboard-only)
- Removed debug/log panel code (3,236 lines deleted)
- Removed syntax highlighting dependencies (tree-sitter parsers)
- Removed unused modules: 18 modules and 1 test utility (52KB dead code)
- Removed obsolete validation module and tests

### Technical Details
- Python requirement: >=3.12
- All 379 core tests passing
- Full type annotation support
- MIT License

### Acknowledgments
- Core parsing engine extracted from [Textual](https://github.com/Textualize/textual)
- Original Textual code: Copyright (c) 2020-2024 Will McGugan and Textualize.io
- KEYBARD adaptation: Copyright (c) 2025 Emasoft

## [Unreleased]

### Planned
- Additional examples and tutorials
- Performance optimizations
- Extended documentation

---

[0.2.0a1]: https://github.com/Emasoft/KEYBARD/releases/tag/v0.2.0a1
