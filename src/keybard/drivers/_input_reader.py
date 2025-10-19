import sys

__all__ = ["InputReader"]

WINDOWS = sys.platform == "win32"

if WINDOWS:
    from keybard.drivers._input_reader_windows import InputReader
else:
    from keybard.drivers._input_reader_linux import (  # type: ignore[assignment]
        InputReader,
    )
