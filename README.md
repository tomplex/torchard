# torchard

TUI for managing tmux sessions and git worktrees together. Built with [textual](https://github.com/Textualize/textual).

Each tmux session is bound to a repo and branch. New tabs within a session automatically create worktrees. torchard handles session creation, navigation, worktree lifecycle and cleanup from a single interface.

## Install

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```
git clone git@github.com:tomplex/torchard.git
cd torchard
uv sync
```

Add a tmux keybind to launch it as a popup:

```tmux
bind -n M-s display-popup -E -w 80% -h 70% "/path/to/torchard/.venv/bin/torchard"
```

On first launch, torchard scans your repos and worktrees directories (configurable via `S` settings) and discovers live tmux sessions.

## What it does

**Session list** is the main view. Shows all tmux sessions sorted with the current session on top. `enter` to switch, `tab` to expand and see live windows with running commands. Claude Code sessions show up with a `✦` marker. `/` to filter.

**New session** (`n`) walks through picking a repo, branch, session name and (for monorepos) a working subdirectory. Feature branches get a worktree with a 3-window layout: claude, diff and shell.

**New tab** (`w`) creates a worktree branching from the session's branch and launches Claude Code in it.

**PR checkout** (`p`) takes a PR number or branch name (via `gh`), fetches it, creates a worktree and session, launches Claude Code, and switches to it.

**History** (`h`) browses Claude Code conversation history (`~/.claude/conversation-index.md`), scoped to the current session's repo or globally. `enter` resumes a conversation with `claude --resume` in its original directory.

**Cleanup** (`c`) shows all worktrees with staleness detection (merged or remote-deleted branches). Select and bulk-delete.

**Settings** (`S`) configure repos directory, worktrees directory, etc.

## Keybinds

| Key | Action |
|-----|--------|
| `enter` | Switch to session (or specific window if expanded) |
| `tab` | Expand/collapse session windows |
| `/` | Filter sessions |
| `n` | New session |
| `w` | New worktree tab |
| `g` | Launch Claude Code in session |
| `p` | Checkout PR/branch |
| `d` | Delete session |
| `r` | Rename session or tab |
| `b` | Change session branch |
| `a` | Adopt unmanaged session |
| `h` | Conversation history |
| `c` | Cleanup worktrees |
| `x` | Kill tab (on expanded window) |
| `S` | Settings |
| `?` | Help |
| `q` | Quit |

## Data

Session and worktree metadata lives in `~/.local/share/torchard/torchard.db` (SQLite). Worktrees are created at `<worktrees_dir>/<repo-name>/<branch-name>` (default `~/dev/worktrees/`). Both directories are configurable in settings.
