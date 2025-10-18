from __future__ import annotations

from keybard import events
from keybard.driver import Driver
from keybard.geometry import Size


class HeadlessDriver(Driver):
    """A do-nothing driver for testing."""

    @property
    def is_headless(self) -> bool:
        """Is the driver running in 'headless' mode?"""
        return True

    def _get_terminal_size(self) -> tuple[int, int]:
        if self._size is not None:
            return self._size
        width: int | None = 80
        height: int | None = 25
        import shutil

        try:
            width, height = shutil.get_terminal_size()
        except (AttributeError, ValueError, OSError):
            try:
                width, height = shutil.get_terminal_size()
            except (AttributeError, ValueError, OSError):
                pass
        width = width or 80
        height = height or 25
        return width, height

    def write(self, data: str) -> None:
        """Write data to the output device.

        Args:
            data: Raw data.
        """
        # Nothing to write as this is a headless driver.

    def start_application_mode(self) -> None:
        """Start application mode."""

        def send_size_event() -> None:
            """Send first resize event."""
            terminal_size = self._get_terminal_size()
            width, height = terminal_size
            keybard_size = Size(width, height)
            event = events.Resize(keybard_size, keybard_size)
            self.process_message(event)

        send_size_event()

    def disable_input(self) -> None:
        """Disable further input."""

    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""
        # Nothing to do
