"""Wayland platform backends using wl-clipboard and wtype."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable

from voitype.config import CFG
from voitype.platform.base import ClipboardBackend, InputBackend


class WaylandClipboard(ClipboardBackend):
    def get_text(self) -> str:
        try:
            result = subprocess.run(
                ["wl-paste", "--no-newline"],
                capture_output=True, text=True, timeout=2,
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def get_selection(self) -> str:
        try:
            result = subprocess.run(
                ["wl-paste", "--primary", "--no-newline"],
                capture_output=True, text=True, timeout=2,
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def set_text(self, text: str) -> None:
        try:
            subprocess.run(
                ["wl-copy"], input=text, text=True, timeout=2,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            pass


class WaylandInput(InputBackend):
    def paste(self, terminal: bool = False) -> None:
        try:
            if terminal:
                subprocess.run(
                    ["wtype", "-M", "ctrl", "-M", "shift", "-k", "v",
                     "-m", "shift", "-m", "ctrl"],
                    timeout=2,
                )
            else:
                subprocess.run(
                    ["wtype", "-M", "ctrl", "-k", "v", "-m", "ctrl"],
                    timeout=2,
                )
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    def copy(self) -> None:
        try:
            subprocess.run(
                ["wtype", "-M", "ctrl", "-k", "c", "-m", "ctrl"],
                timeout=2,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    def is_terminal(self) -> bool:
        # Try swaymsg (Sway)
        for cmd, parser in _WAYLAND_DETECTORS:
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=2,
                )
                if result.returncode == 0:
                    val = parser(result.stdout)
                    if val is not None:
                        return val
            except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError):
                continue
        return False


def _parse_sway(output: str) -> bool | None:
    """Parse swaymsg -t get_tree for focused window."""
    try:
        tree = json.loads(output)
        node = _find_focused_sway(tree)
        if node:
            app_id = (node.get("app_id") or "").lower()
            wm_class = (node.get("window_properties", {}).get("class") or "").lower()
            combined = f"{app_id} {wm_class}"
            return any(kw in combined for kw in CFG.TERMINAL_KEYWORDS)
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def _find_focused_sway(node: dict) -> dict | None:
    if node.get("focused"):
        return node
    for child in node.get("nodes", []) + node.get("floating_nodes", []):
        found = _find_focused_sway(child)
        if found:
            return found
    return None


def _parse_hyprland(output: str) -> bool | None:
    """Parse hyprctl activewindow -j."""
    try:
        data = json.loads(output)
        class_name = (data.get("class") or "").lower()
        title = (data.get("title") or "").lower()
        combined = f"{class_name} {title}"
        return any(kw in combined for kw in CFG.TERMINAL_KEYWORDS)
    except (json.JSONDecodeError, KeyError):
        return None


def _parse_niri(output: str) -> bool | None:
    """Parse niri msg -j focused-window."""
    try:
        data = json.loads(output)
        app_id = (data.get("app_id") or "").lower()
        title = (data.get("title") or "").lower()
        combined = f"{app_id} {title}"
        return any(kw in combined for kw in CFG.TERMINAL_KEYWORDS)
    except (json.JSONDecodeError, KeyError):
        return None


_WAYLAND_DETECTORS: list[tuple[list[str], Callable]] = [
    (["swaymsg", "-t", "get_tree"], _parse_sway),
    (["hyprctl", "activewindow", "-j"], _parse_hyprland),
    (["niri", "msg", "-j", "focused-window"], _parse_niri),
]
