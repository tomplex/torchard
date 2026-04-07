"""Checkout a PR or branch into a worktree and launch claude."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Input, Static

from torchard.core import git, tmux
from torchard.core.manager import Manager
from torchard.core.models import Repo


class ReviewScreen(Screen):
    """Enter a PR number or branch name to check out and review."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, manager: Manager) -> None:
        super().__init__()
        self._manager = manager
        self._repos = manager.get_repos()
        # Default to the repo with the most recently active session
        sessions = manager.get_sessions()
        repo_last_active: dict[int, str] = {}
        for s in sessions:
            if s.last_selected_at and (s.repo_id not in repo_last_active
                    or s.last_selected_at > repo_last_active[s.repo_id]):
                repo_last_active[s.repo_id] = s.last_selected_at
        self._repos.sort(
            key=lambda r: repo_last_active.get(r.id, ""),
            reverse=True,
        )
        self._selected_repo: Repo | None = self._repos[0] if self._repos else None

    def compose(self) -> ComposeResult:
        with Vertical(id="review-container"):
            yield Static("[bold]Review[/bold]", id="review-title")
            if len(self._repos) > 1:
                yield Static("Repo [dim](tab to cycle)[/dim]", id="review-repo-label")
            yield Static(self._repo_display(), id="review-repo")
            yield Static(
                "PR number or branch name",
                id="review-hint",
            )
            yield Input(placeholder="e.g. 1234 or feat/my-branch", id="review-input")
            yield Static("", id="review-error")
            yield Static(
                "[dim]Enter[/dim] to checkout  [dim]Escape[/dim] to cancel",
                id="review-footer-hint",
            )
        yield Footer()

    def _repo_display(self) -> str:
        if not self._selected_repo:
            return "[red]No repos configured[/red]"
        return f"[bold]{self._selected_repo.name}[/bold] [dim]{self._selected_repo.path}[/dim]"

    def on_mount(self) -> None:
        self.query_one("#review-input", Input).focus()

    def key_tab(self) -> None:
        if len(self._repos) <= 1:
            return
        idx = self._repos.index(self._selected_repo) if self._selected_repo else -1
        self._selected_repo = self._repos[(idx + 1) % len(self._repos)]
        self.query_one("#review-repo", Static).update(self._repo_display())

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        error = self.query_one("#review-error", Static)

        if not self._selected_repo:
            error.update("[red]No repos configured. Create a session first.[/red]")
            return

        if not value:
            error.update("[red]Please enter a PR number or branch name.[/red]")
            return

        error.update("[dim]Checking out...[/dim]")
        self.run_worker(lambda: self._do_checkout(value), thread=True)

    def _do_checkout(self, pr_or_branch: str) -> None:
        try:
            session, worktree_path = self._manager.checkout_and_review(
                self._selected_repo.path, pr_or_branch,
            )
        except (git.GitError, tmux.TmuxError) as exc:
            self.app.call_from_thread(
                self.query_one("#review-error", Static).update,
                f"[red]{exc}[/red]",
            )
            return

        # Write switch file and exit
        from torchard.tui.switch import write_switch
        write_switch({"type": "session", "target": session.name})
        self.app.call_from_thread(self.app.exit)

    def action_cancel(self) -> None:
        self.app.pop_screen()

    DEFAULT_CSS = """
    ReviewScreen {
        align: center middle;
    }
    #review-container {
        width: 70;
        height: auto;
        padding: 2 4;
        border: solid $accent;
    }
    #review-title {
        text-align: center;
        margin-bottom: 1;
    }
    #review-repo-label {
        color: $text-muted;
    }
    #review-repo {
        margin-bottom: 1;
    }
    #review-hint {
        color: $text-muted;
    }
    #review-input {
        margin-bottom: 1;
    }
    #review-error {
        color: $error;
        margin-bottom: 1;
        min-height: 1;
    }
    #review-footer-hint {
        text-align: center;
        color: $text-muted;
    }
    """
