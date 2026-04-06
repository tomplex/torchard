"""Textual application entry point."""

from __future__ import annotations

from textual.app import App

from torchard.core.manager import Manager
from torchard.tui.views.session_list import SessionListScreen


class TorchardApp(App):
    """Torchard TUI — tmux session and worktree manager."""

    CSS = """
    .hidden {
        display: none;
    }
    Screen {
        background: #1a1a2e;
    }
    #session-filter {
        dock: top;
        margin: 0 1;
        height: 3;
    }
    DataTable {
        background: #1a1a2e;
        color: #e0e0e0;
        height: 1fr;
    }
    DataTable > .datatable--header {
        background: #16213e;
        color: #00aaff;
        text-style: bold;
    }
    DataTable > .datatable--cursor {
        background: #0f3460;
        color: #ffffff;
    }
    DataTable > .datatable--hover {
        background: #16213e;
    }
    Footer {
        background: #16213e;
        color: #aaaaaa;
    }
    Footer > .footer--highlight {
        background: #0f3460;
        color: #00aaff;
    }
    Footer > .footer--key {
        color: #00aaff;
        text-style: bold;
    }
    """

    def __init__(self, manager: Manager) -> None:
        super().__init__()
        self._manager = manager

    def on_mount(self) -> None:
        self.push_screen(SessionListScreen(self._manager))
