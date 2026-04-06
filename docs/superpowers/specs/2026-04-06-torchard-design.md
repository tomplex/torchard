# torchard - tmux session & worktree manager

## Background

My tmux workflow has evolved organically into a pattern where each session represents a project or feature, and each window (tab) within a session represents a distinct chunk of work. For work stuff, a session maps to a feature branch on a repo, and each tab gets its own git worktree branching off that feature branch. For personal projects, it's the same structure but the base branch is just main/master.

I've accumulated a handful of small scripts to manage pieces of this - `worktree-pick.sh` for creating sessions from a directory picker, a resurrect hook for persisting Claude sessions, an fzf-based session switcher. These work but they don't talk to each other and there's no central place to manage the full lifecycle: creating sessions with associated repos/branches, spinning up worktrees as new tabs, cleaning up stale worktrees when I'm done.

## Problem

No unified tool to:
- Create tmux sessions that are "bound" to a repo and base branch
- Automatically create worktrees when adding tabs to a session
- Track which worktrees belong to which sessions
- Clean up worktrees when work is done
- Navigate between sessions (replacing the current fzf picker)

## Solution

A Python TUI app called **torchard** (tmux + orchard) that consolidates session/worktree management into a single tool. It replaces the existing `Alt-s` session picker and `prefix+N` worktree picker with a richer interface that handles creation, navigation and cleanup.

## Technical Design

### Architecture

Three layers, separated so future features (pane process awareness, resurrect integration, workspace restore) can slot in without rewriting:

1. **Core layer** (`torchard/core/`) - pure logic, no UI. Manages SQLite database, wraps tmux and git CLI calls, defines domain model. Independently testable.
2. **TUI layer** (`torchard/tui/`) - textual app that presents views and dispatches to the core layer. Knows nothing about git or tmux directly.
3. **Entry point** - a `torchard` command (via pyproject.toml `[project.scripts]`) that launches the TUI.

### Data Model (SQLite)

```
repos
  id              INTEGER PRIMARY KEY
  path            TEXT    -- absolute path to main checkout (e.g. /Users/tom/dev/fdy)
  name            TEXT    -- short name (e.g. "fdy")
  default_branch  TEXT    -- main/master, auto-detected

sessions
  id              INTEGER PRIMARY KEY
  name            TEXT    -- tmux session name
  repo_id         INTEGER -- FK to repos
  base_branch     TEXT    -- branch that new worktrees branch from
  created_at      TEXT

worktrees
  id              INTEGER PRIMARY KEY
  session_id      INTEGER -- FK to sessions (nullable, for pre-existing worktrees)
  repo_id         INTEGER -- FK to repos
  path            TEXT    -- absolute path to the worktree
  branch          TEXT    -- branch name
  tmux_window     INTEGER -- window index in the session (nullable)
  created_at      TEXT
```

`worktrees.session_id` is nullable so torchard can discover and track existing worktrees it didn't create. The DB lives at `~/.local/share/torchard/torchard.db`.

### TUI Views

**Main view (session list)** - the default view, replaces `Alt-s`. Shows all sessions with their repo and base branch. Keyboard and mouse navigation.

```
torchard

Sessions
────────
▸ tc-model-train-feature-store   fdy     tc/model-train-feature-store
  td-drift_report_v2             fdy     td/drift_report_v2
  stormgate                      stormg  main
  claude-review                  claude  main

[n] new session  [w] new tab  [d] delete
[enter] switch   [c] cleanup  [?] help
```

- Arrow/vim keys or mouse click to navigate, `enter` to switch session
- `n` opens new session flow
- `w` opens new tab flow for highlighted session
- `d` deletes session (with confirmation, optionally cleans up worktrees)
- `c` opens cleanup view

**New session flow** - short wizard:
1. Pick a repo (from known repos, or add new one by path)
2. Pick or name a base branch (fuzzy search over existing branches, or type new)
3. Name the session (auto-suggested from branch name)
4. Session created, switched into it

**New tab flow:**
1. Name the worktree/branch
2. Worktree created off session's base branch, new tmux window opens in that directory

**Cleanup view** - worktrees grouped by session with status indicators (merged? remote branch deleted? no session attached?). Select and bulk-delete.

### tmux Integration

Single keybind replaces both `Alt-s` and `prefix+N`:

```tmux
bind -n M-s display-popup -E -w 80% -h 70% "torchard"
```

torchard talks to tmux via CLI subprocess calls (`tmux new-session`, `tmux new-window`, `tmux switch-client`, etc.). No plugin or API needed.

### Worktree Convention

New worktrees go to `~/dev/worktrees/<repo>/<branch-name>`, matching existing layout.

### First-run Adoption

On first run, torchard scans `~/dev/worktrees/` and active tmux sessions to populate its database with existing state.

### Project Structure

```
~/dev/torchard/
  pyproject.toml          -- uv, dependencies (textual, etc.)
  torchard/
    __init__.py
    __main__.py           -- entry point
    core/
      __init__.py
      db.py               -- SQLite setup, migrations, queries
      models.py           -- dataclasses for repos, sessions, worktrees
      tmux.py             -- tmux CLI wrapper
      git.py              -- git/worktree CLI wrapper
      manager.py          -- orchestration logic (create session, add tab, cleanup)
    tui/
      __init__.py
      app.py              -- textual App subclass
      views/
        __init__.py
        session_list.py   -- main view
        new_session.py    -- new session wizard
        new_tab.py        -- new tab flow
        cleanup.py        -- cleanup view
```

### Dependencies

- `textual` - TUI framework
- `sqlite3` - stdlib, no extra dep

### Open Questions

- Should torchard auto-detect repos by scanning `~/dev/` for git repos, or only track repos that are explicitly added? My guess is auto-detect on first run, then only track explicitly added ones going forward.
- Branch naming convention for worktree tabs - should torchard enforce a prefix pattern (e.g. `<session-base>/<tab-name>`) or let the user name freely? I think free naming is right, with the session's base branch as the branch point regardless.
- Multiple sessions can exist for the same repo with different base branches - this is intentional and expected (e.g. two feature branches on `fdy` at the same time).
