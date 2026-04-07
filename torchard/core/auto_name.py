"""Watch a Claude session and rename the tmux window based on the first user message."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path


def _find_session_jsonl(session_uuid: str) -> Path | None:
    """Find the JSONL file for a Claude session UUID."""
    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        return None
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        jsonl = project_dir / f"{session_uuid}.jsonl"
        if jsonl.exists():
            return jsonl
    return None


def _get_first_user_message(jsonl_path: Path) -> str | None:
    """Read the first user message from a Claude JSONL file."""
    with open(jsonl_path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") == "user":
                content = entry.get("message", {}).get("content", "")
                if isinstance(content, str) and content.strip():
                    return content.strip()
    return None


def _summarize(message: str, max_words: int = 4) -> str:
    """Turn a user message into a short kebab-case window name."""
    # Take first line, strip common prefixes
    first_line = message.split("\n")[0].strip()
    # Remove markdown headers
    first_line = first_line.lstrip("#").strip()
    # Take first few words
    words = first_line.split()[:max_words]
    # Clean up
    name = "-".join(w.lower().strip(".,!?:;\"'()[]{}") for w in words if w)
    # Truncate
    if len(name) > 30:
        name = name[:30].rsplit("-", 1)[0]
    return name or "claude"


def watch_and_rename(
    session_name: str,
    window_target: str,
    pane_pid: str | None = None,
    timeout: int = 120,
    poll_interval: float = 2.0,
) -> None:
    """Poll for a Claude session's first user message and rename the tmux window.

    Args:
        session_name: tmux session name
        window_target: tmux window target (e.g. "session:1")
        pane_pid: PID of the pane running claude (to find session UUID)
        timeout: max seconds to wait
        poll_interval: seconds between polls
    """
    if not pane_pid:
        return

    deadline = time.time() + timeout
    session_uuid = None

    while time.time() < deadline:
        # Wait for Claude to write its session UUID
        pid_file = Path("/tmp/claude-sessions") / f"pid-{pane_pid}"
        if pid_file.exists():
            session_uuid = pid_file.read_text().strip()
            if session_uuid:
                break
        time.sleep(poll_interval)

    if not session_uuid:
        return

    # Wait for the JSONL file and first user message
    while time.time() < deadline:
        jsonl = _find_session_jsonl(session_uuid)
        if jsonl:
            msg = _get_first_user_message(jsonl)
            if msg:
                name = _summarize(msg)
                subprocess.run(
                    ["tmux", "rename-window", "-t", window_target, name],
                    capture_output=True,
                )
                return
        time.sleep(poll_interval)
