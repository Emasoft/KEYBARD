# Changelog

All notable changes to KEYBARD will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0a1] - 2025-10-18 (Alpha)

### Added

#### Core Features
- Initial release of KEYBARD as standalone keyboard input library
- Cross-platform keyboard input support (Linux, macOS, Windows)
- Battle-tested XTerm parser extracted from Textual framework
- Three operational modes: blocking (`read_key()`), non-blocking (`poll()`), and callback-based (`run()`)
- Support for special keys, modifiers, and key combinations
- Bracketed paste event detection
- Focus event detection (AppFocus/AppBlur)
- Resize event detection with pixel-accurate dimensions (when supported)

#### Timing-Based Event Dispatcher (NEW in 0.2.0a1)
- Optional timing-based event dispatcher for distinguishing taps vs holds
- `KeyClick` event: Quick press/release within delta threshold (default 1s)
- `KeyDown` event: Key held past delta threshold (emitted after waiting)
- `KeyUp` event: Key released after being held
- `DispatcherConfig` with 4 configurable parameters:
  - `delta`: Time threshold for click vs hold (default: 1.0s)
  - `release_timeout`: Time to detect release from repeat absence (default: 0.15s)
  - `emit_repeats`: Emit KeyDown on each key repeat (default: False)
  - `repeat_interval`: Min time between repeat emissions (default: 0.05s)
- Thread-safe timer management for concurrent key tracking
- Infers key release from absence of OS key repeat events
- `use_dispatcher` parameter in KeyboardReader constructor
- `dispatcher_config` parameter for custom timing configuration

#### Documentation
- Comprehensive README with 7 usage examples
- "Timing-Based Event Model" section (127 lines)
- "Important Limitation" section explaining terminal key repetition constraints
- API_REFERENCE.md with complete API documentation (709 lines)
- TECHNICAL_ARCHITECTURE.md explaining dispatcher internals (329 lines)
- VERIFICATION_REPORT.md documenting all quality checks
- Comprehensive ROADMAP with 150+ specific contribution opportunities organized in 16 categories

#### Examples
- `examples/key_display.py`: Real-time event visualization
  - Support for both manual tracking and dispatcher modes (`--use-dispatcher`)
  - Millisecond-precision timestamps
  - Color-coded display for different key types
  - Scrolling history of last 20 events
- `examples/timed_keys.py`: Interactive timing-based events demo (NEW)
  - Visual demonstration of KeyClick/KeyDown/KeyUp events
  - Configurable delta threshold
  - Real-time event history table
  - In-UI warnings about terminal input limitations
- `examples/quickstart.py`: Minimal 30-line getting started example

#### Testing
- 337 tests passing (100% pass rate), 2 skipped
- 15 new dispatcher-specific tests covering:
  - Configuration validation (5 tests)
  - Event transformation (9 tests)
  - Thread safety (1 test)
- All tests run in parallel with pytest-xdist (16 workers)

### Changed
- Focused codebase: Removed mouse support (keyboard-only)
- Removed debug/log panel code (3,236 lines deleted)
- Removed syntax highlighting dependencies (tree-sitter parsers)
- Removed unused modules: 18 modules and 1 test utility (52KB dead code)
- Removed obsolete validation module and tests
- Test count updated from 379 to 337 (removed obsolete tests)

### Fixed
- Removed incomplete combo detection feature (combo_window parameter)
- Marked ComboClick/ComboKeyDown events as "FUTURE FEATURE" (not yet implemented)
- Updated all documentation to accurately reflect current capabilities
- Fixed key_display.py flickering issue with proper state tracking

### Technical Details
- Python requirement: >=3.12
- 337 tests passing, 2 skipped (100% pass rate)
- Full type annotation support (mypy --strict compliant)
- Zero linting errors (ruff)
- Package size: 105 KB wheel, 82 KB source
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

## [0.3.0a1] - 2025-10-19 (Alpha)

### Added

#### Documentation Enhancement
- Complete docstring overhaul for all public APIs
- All 7 public functions now have complete Args, Returns, and Raises sections
- Enhanced `KeyboardReader` methods: `start()`, `stop()`, `run()`
- Enhanced `KeyEventDispatcher` methods: `feed()`, `stop()`
- Enhanced `Keys.value` property with Returns documentation
- Enhanced utility functions: `format_key()`, `key_to_character()`
- All docstrings follow Google-style format consistently

#### API Reference Updates
- Updated `API_REFERENCE.md` from 710 to 915 lines (+29% expansion)
- Added complete KeyEventDispatcher class documentation section
- Added new Utility Functions section with `format_key()` and `key_to_character()`
- Added 15+ practical code examples for utility functions
- Updated version references from 0.2.0a1 to 0.3.0a1 throughout

### Improved
- API documentation now 100% complete (all public APIs documented)
- Extracted and verified all docstrings directly from source code
- Ensured consistency between source code docstrings and API reference
- Added practical examples showing arrow key formatting and character conversion

### Quality Assurance
- All 337 tests still passing (100% pass rate)
- Zero linting errors (ruff check)
- Zero type checking errors (mypy on 47 source files)
- Complete documentation verification performed

---

[0.3.0a1]: https://github.com/Emasoft/KEYBARD/releases/tag/v0.3.0a1
[0.2.0a1]: https://github.com/Emasoft/KEYBARD/releases/tag/v0.2.0a1
