# trellis

TUI for managing tmux sessions and git worktrees together.

Each tmux session is bound to a repo and branch. New tabs within a session automatically create worktrees. trellis handles session creation, navigation, worktree lifecycle and cleanup from a single interface.

## Install

Requires a Rust toolchain ([rustup](https://rustup.rs/)).

```
git clone git@github.com:tomplex/trellis.git
cd trellis
cargo install --path .
```

This installs the `trellis` binary into `~/.cargo/bin`. Add a tmux keybind to launch it as a popup:

```tmux
bind -n M-s display-popup -E -w 80% -h 70% "trellis"
```

On first launch, trellis scans your repos and worktrees directories (configurable via `S` settings) and discovers live tmux sessions.

## What it does

**Session list** is the main view. Shows all tmux sessions sorted with the current session on top. `enter` to switch, `tab` to expand and see live windows with running commands. Claude Code panes show up with a `✦` marker and a status (`working…`, `needs input`, `idle`). `/` to filter.

**New session** (`n`) walks through picking a repo, branch, session name and (for monorepos) a working subdirectory. Feature branches get a worktree with a 2-window layout: claude and shell.

**New tab** (`t`) creates a worktree branching from the session's branch and launches Claude Code in it.

**PR review** (`R`) takes a PR number or branch name (via `gh`), fetches it, creates a worktree and session, launches Claude Code, and switches to it.

**History** (`H`) browses Claude Code conversation history, scoped to the current session's repo or globally. `enter` resumes a conversation with `claude --resume` in its original directory.

**Cleanup** (`c`) shows all worktrees with staleness detection (merged or remote-deleted branches). Select and bulk-delete.

**Actions menu** (`.`) opens a per-session menu — change branch, launch Claude, or adopt an unmanaged session.

**Settings** (`S`) configures repos directory, worktrees directory, etc.

## Keybinds

| Key | Action |
|-----|--------|
| `enter` | Switch to session (or specific window if expanded) |
| `tab` | Expand/collapse session windows |
| `j` / `k` | Navigate up/down |
| `/` | Filter sessions |
| `n` | New session |
| `t` | New worktree tab |
| `R` | PR review (PR number or branch) |
| `r` | Rename session |
| `d` | Delete session or kill tab |
| `.` | Actions menu (change branch, launch claude, adopt) |
| `H` | Conversation history |
| `c` | Cleanup worktrees |
| `S` | Settings |
| `?` | Help |
| `q` | Quit |

## Data

Session and worktree metadata lives in `~/.local/share/trellis/trellis.db` (SQLite). Worktrees are created at `<worktrees_dir>/<repo-name>/<branch-name>` (default `~/dev/worktrees/`). Both directories are configurable in settings.
