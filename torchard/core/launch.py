"""Helpers for launching claude in tmux windows with auto-naming."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def launch_claude_in_window(session_name: str, window_name: str) -> None:
    """Send 'claude' to a tmux window and start the auto-namer in the background."""
    target = f"{session_name}:{window_name}"
    subprocess.run(["tmux", "send-keys", "-t", target, "claude", "Enter"], capture_output=True)

    # Get the pane PID so the auto-namer can find the Claude session UUID
    result = subprocess.run(
        ["tmux", "display-message", "-t", target, "-p", "#{pane_pid}"],
        capture_output=True, text=True,
    )
    pane_pid = result.stdout.strip()
    if not pane_pid:
        return

    # Launch auto-namer in background
    auto_name_bin = Path(sys.executable).parent / "torchard-auto-name"
    if auto_name_bin.exists():
        subprocess.Popen(
            [str(auto_name_bin), target, pane_pid],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
