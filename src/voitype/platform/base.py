"""Abstract base classes for platform backends."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ClipboardBackend(ABC):
    @abstractmethod
    def get_text(self) -> str:
        """Read text from clipboard."""

    @abstractmethod
    def get_selection(self) -> str:
        """Read the primary selection (highlighted text)."""

    @abstractmethod
    def set_text(self, text: str) -> None:
        """Write text to clipboard."""


class InputBackend(ABC):
    @abstractmethod
    def paste(self, terminal: bool = False) -> None:
        """Simulate Ctrl+V (or Ctrl+Shift+V for terminals)."""

    @abstractmethod
    def copy(self) -> None:
        """Simulate Ctrl+C to copy selection to clipboard."""

    @abstractmethod
    def is_terminal(self) -> bool:
        """Check if the focused window is a terminal."""
