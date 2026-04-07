from dataclasses import dataclass


@dataclass
class Repo:
    path: str
    name: str
    default_branch: str
    id: int | None = None


@dataclass
class Session:
    name: str
    repo_id: int
    base_branch: str
    created_at: str
    id: int | None = None
    last_selected_at: str | None = None


@dataclass
class Worktree:
    repo_id: int
    path: str
    branch: str
    created_at: str
    session_id: int | None = None
    tmux_window: int | None = None
    id: int | None = None


@dataclass
class SessionInfo:
    """A session enriched with live tmux state, returned by Manager.list_sessions."""
    id: int | None
    name: str
    repo_id: int | None
    base_branch: str | None
    created_at: str | None
    last_selected_at: str | None
    windows: int | None
    attached: bool
    live: bool
    managed: bool
