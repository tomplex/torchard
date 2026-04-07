"""CLI entry point for auto-naming a tmux window from Claude's first message.

Usage: torchard-auto-name <session>:<window> <pane_pid>

Designed to be launched in the background after starting claude in a tmux window.
"""

import sys

from torchard.core.auto_name import watch_and_rename


def main() -> None:
    if len(sys.argv) < 3:
        return
    window_target = sys.argv[1]
    pane_pid = sys.argv[2]
    session_name = window_target.split(":")[0]
    watch_and_rename(session_name, window_target, pane_pid)


if __name__ == "__main__":
    main()
