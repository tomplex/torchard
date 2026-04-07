"""Reusable action menu modal."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView, Static


class ActionMenu(ModalScreen[str | None]):
    """A quick-pick modal that returns the key of the selected action."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("j,down", "cursor_down", "Down", show=False),
        Binding("k,up", "cursor_up", "Up", show=False),
    ]

    def __init__(self, title: str, items: list[tuple[str, str, str]]) -> None:
        """items: list of (key, label, hint) tuples."""
        super().__init__()
        self._title = title
        self._items = items

    def compose(self) -> ComposeResult:
        with Vertical(id="action-menu-container"):
            yield Static(f"[bold]{self._title}[/bold]", id="action-menu-title")
            yield ListView(id="action-menu-list")

    def on_mount(self) -> None:
        lv = self.query_one("#action-menu-list", ListView)
        for key, label, hint in self._items:
            hint_display = f"  [dim]{hint}[/dim]" if hint else ""
            lv.append(ListItem(Label(f"{label}{hint_display}"), id=f"action-{key}"))
        lv.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id and item_id.startswith("action-"):
            self.dismiss(item_id[len("action-"):])

    def action_cursor_down(self) -> None:
        self.query_one(ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(ListView).action_cursor_up()

    def action_cancel(self) -> None:
        self.dismiss(None)

    DEFAULT_CSS = """
    ActionMenu {
        align: center middle;
    }
    #action-menu-container {
        background: #16213e;
        border: solid #00aaff;
        padding: 1 2;
        width: 50;
        height: auto;
        max-height: 20;
    }
    #action-menu-title {
        text-align: center;
        color: #00aaff;
        margin-bottom: 1;
    }
    #action-menu-list {
        height: auto;
        max-height: 14;
    }
    """
