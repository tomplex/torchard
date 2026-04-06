"""Settings screen for managing torchard configuration."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Input, Label, Static

from torchard.core.db import get_all_config, set_config
from torchard.core.manager import Manager

_CONFIG_LABELS = {
    "repos_dir": "Repos directory",
    "worktrees_dir": "Worktrees directory",
}


class SettingsScreen(Screen):
    """View and edit torchard configuration."""

    BINDINGS = [
        Binding("escape", "dismiss", "Back"),
    ]

    def __init__(self, manager: Manager) -> None:
        super().__init__()
        self._manager = manager
        self._inputs: dict[str, Input] = {}

    def compose(self) -> ComposeResult:
        with Vertical(id="settings-container"):
            yield Static("[bold]Settings[/bold]", id="settings-title")
            yield Static("", id="settings-hint")

            config = get_all_config(self._manager._conn)
            for key in sorted(config):
                label = _CONFIG_LABELS.get(key, key)
                yield Label(f"{label}:", id=f"label-{key}")
                inp = Input(value=config[key], id=f"input-{key}")
                self._inputs[key] = inp
                yield inp

            yield Static("", id="settings-error")
            yield Static(
                "[dim]Enter[/dim] to save  [dim]Escape[/dim] to cancel",
                id="settings-footer-hint",
            )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#settings-hint", Static).update(
            "[dim]Edit values and press Enter to save.[/dim]"
        )
        first = list(self._inputs.values())
        if first:
            first[0].focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        error = self.query_one("#settings-error", Static)
        for key, inp in self._inputs.items():
            value = inp.value.strip()
            if not value:
                error.update(f"[red]{_CONFIG_LABELS.get(key, key)} cannot be empty.[/red]")
                inp.focus()
                return
            set_config(self._manager._conn, key, value)
        error.update("[green]Saved.[/green]")

    def action_dismiss(self) -> None:
        self.app.pop_screen()

    DEFAULT_CSS = """
    SettingsScreen {
        align: center middle;
    }
    #settings-container {
        width: 80;
        height: auto;
        padding: 2 4;
        border: solid $accent;
    }
    #settings-title {
        text-align: center;
        color: $accent;
        margin-bottom: 1;
    }
    #settings-hint {
        text-align: center;
        margin-bottom: 1;
    }
    #settings-error {
        margin-top: 1;
        min-height: 1;
        text-align: center;
    }
    #settings-footer-hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """
