"""Help screen with keybind reference."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static


_HELP_TEXT = """\
[bold #00aaff]torchard[/bold #00aaff] — tmux session & worktree manager

[bold]Session List[/bold]
  [#00aaff]enter[/#00aaff]     Switch to session/tab
  [#00aaff]tab[/#00aaff]       Expand/collapse tabs
  [#00aaff]n[/#00aaff]         New… (session, tab, or PR review)
  [#00aaff]d[/#00aaff]         Delete session or kill tab
  [#00aaff]h[/#00aaff]         Conversation history
  [#00aaff].[/#00aaff]         Actions menu
  [#00aaff]j/k[/#00aaff]       Navigate up/down
  [#00aaff]/[/#00aaff]         Filter sessions
  [#00aaff]q[/#00aaff]         Quit

[bold]Actions menu (.)[/bold]
  Rename, change branch, launch claude,
  adopt, cleanup, settings

[bold]Cleanup View[/bold]
  [#00aaff]space/enter[/#00aaff]  Toggle selection
  [#00aaff]a[/#00aaff]           Select all
  [#00aaff]d[/#00aaff]           Delete selected
  [#00aaff]escape[/#00aaff]      Back

[dim]Press Escape to close this help.[/dim]\
"""


class HelpScreen(Screen):
    """Keybind reference."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="help-container"):
            yield Static(_HELP_TEXT, id="help-text")
        yield Footer()

    def action_dismiss(self) -> None:
        self.app.pop_screen()

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }
    #help-container {
        width: 50;
        height: auto;
        border: solid #00aaff;
        padding: 1 2;
        background: #16213e;
    }
    #help-text {
        color: #e0e0e0;
    }
    """
