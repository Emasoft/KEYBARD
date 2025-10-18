# Contributing to KEYBARD

Thank you for your interest in contributing to KEYBARD! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Getting Started

1. Fork and clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/KEYBARD.git
cd KEYBARD
```

2. Create a virtual environment and install dependencies:

```bash
# Create virtual environment
uv venv --python 3.12

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install development dependencies
uv pip install -e ".[dev]"
```

3. Install pre-commit hooks:

```bash
uv run pre-commit install
```

## Development Workflow

### Code Style

KEYBARD follows these code quality standards:

- **Formatting**: Use `ruff format` (NOT black)
- **Linting**: Use `ruff check`
- **Type checking**: Use `mypy`
- **Line length**: 320 characters maximum

### Running Checks

```bash
# Format code
uv run ruff format --line-length=320 src/ tests/

# Run linter
uv run ruff check --fix --output-format=full

# Type checking
uv run mypy src/keybard --pretty

# Run all checks
make check  # If Makefile exists
```

### Running Tests

```bash
# Run all tests (parallel execution with 16 workers)
uv run pytest -n 16 --dist=loadgroup

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_xterm_parser.py

# Run specific test function
uv run pytest tests/test_xterm_parser.py::test_bracketed_paste -vvv

# Run with coverage report
uv run pytest --cov=keybard --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov=keybard --cov-report=html
open htmlcov/index.html
```

### Before Committing

1. **Format your code**:
   ```bash
   uv run ruff format --line-length=320 src/ tests/
   ```

2. **Fix linting issues**:
   ```bash
   uv run ruff check --fix
   ```

3. **Run type checks**:
   ```bash
   uv run mypy src/keybard
   ```

4. **Run tests**:
   ```bash
   uv run pytest
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

Pre-commit hooks will automatically run on commit and fix formatting issues.

## Contribution Guidelines

### Code Standards

1. **Type Annotations**: All functions must have type annotations
   ```python
   def parse_key(sequence: str) -> Key | None:
       ...
   ```

2. **Docstrings**: Use Google-style docstrings (without markdown):
   ```python
   def parse_escape_sequence(data: str) -> Event | None:
       """Parse an ANSI escape sequence into an Event.

       Args:
           data: The escape sequence string to parse.

       Returns:
           An Event object if parsing succeeds, None otherwise.
       """
   ```

3. **Error Handling**: Follow fail-fast approach - let errors propagate
   - No error handling workarounds
   - No fallbacks or silent failures
   - Code either works or exits

4. **File Organization**:
   - Keep source files under 10KB when possible
   - Split large modules into smaller, focused modules
   - Use `_prefix.py` naming for internal/private modules

5. **Testing**:
   - Write real tests, not mocks (unless absolutely necessary)
   - Test coverage should include edge cases
   - Use descriptive test function names
   - Add docstrings to test functions explaining what they test

### What to Contribute

We welcome contributions in these areas:

- **Bug fixes**: Fix issues or unexpected behavior
- **Documentation**: Improve README, examples, or inline documentation
- **Tests**: Add test coverage for untested code paths
- **Examples**: Add new examples demonstrating KEYBARD features
- **Performance**: Optimize slow code paths
- **Platform support**: Improve cross-platform compatibility

### What NOT to Contribute

Please avoid these types of contributions:

- **Mouse support**: KEYBARD is keyboard-only by design
- **UI frameworks**: This is a low-level input library, not a TUI framework
- **Breaking changes**: Without prior discussion in an issue
- **Mocked tests**: Real tests only (use actual terminal when possible)
- **Backward compatibility code**: Only one version of code should exist

## Pull Request Process

1. **Create an issue first** (for non-trivial changes)
   - Discuss your proposed changes
   - Get feedback before investing time in implementation

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**:
   - Write code following our standards
   - Add tests for new functionality
   - Update documentation as needed

4. **Run all checks**:
   ```bash
   uv run ruff format --line-length=320 src/ tests/
   uv run ruff check --fix
   uv run mypy src/keybard
   uv run pytest
   ```

5. **Commit with clear messages**:
   ```bash
   git commit -m "Add support for XYZ key combination"
   ```

6. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

7. **PR Requirements**:
   - All tests must pass
   - Code must be formatted and linted
   - Type checks must pass
   - Include tests for new functionality
   - Update documentation if needed

## Project Structure

```
KEYBARD/
├── src/keybard/           # Main package source
│   ├── __init__.py        # Package exports
│   ├── reader.py          # KeyboardReader main class
│   ├── keys.py            # Key definitions and normalization
│   ├── events.py          # Event classes
│   ├── _xterm_parser.py   # XTerm escape sequence parser
│   └── drivers/           # Platform-specific drivers
│       ├── linux_driver.py
│       ├── windows_driver.py
│       ├── headless_driver.py
│       └── web_driver.py
├── tests/                 # Test suite
├── examples/              # Example programs
├── docs/                  # Additional documentation
└── pyproject.toml         # Project configuration
```

## Testing Philosophy

KEYBARD follows these testing principles:

1. **Real tests only**: No mocks unless absolutely necessary
2. **Real terminals**: Use actual terminal I/O when possible
3. **Edge cases**: Test boundary conditions and error paths
4. **Fast feedback**: Tests should run quickly (parallel execution)
5. **Clear failures**: Test names should indicate what failed

## Git Commit Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor" not "Moves cursor")
- Limit first line to 72 characters
- Reference issues and pull requests liberally

Examples:
```
Add support for F13-F24 function keys
Fix parsing of Ctrl+Shift key combinations
Update README with new installation instructions
Refactor XTerm parser for better performance
```

## Questions?

- **Issues**: https://github.com/Emasoft/KEYBARD/issues
- **Discussions**: Use GitHub Discussions for questions and ideas

## License

By contributing to KEYBARD, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

KEYBARD is built on code extracted from [Textual](https://github.com/Textualize/textual). When contributing, please respect the original work and maintain code quality standards.

Thank you for contributing to KEYBARD!
