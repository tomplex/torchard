# torchard TODO

## Workflow improvements

- **Quick-launch claude in current session** - `g` opens a new tab in the highlighted session with claude already running
- **Duplicate/clone a session** - create a new session with the same repo/branch as an existing one
- **Session notes/labels** - attach a short description to a session so you remember what you were doing

## Approach 3 (workspace orchestrator)

- **Auto-refresh** - poll tmux state on a timer so window counts, attached status, and running commands stay current
- **Resurrect integration** - manage the resurrect hook directly, or offer "resume last claude" for a session whose tmux died
- **Workspace snapshots** - save a session's window layout (worktrees, commands) and restore it. Like resurrect but torchard-aware.
- **Git status per worktree** - show dirty/clean/ahead/behind in the expanded view (async)

## Quality of life

- **Notification when a background claude finishes** - watch claude panes for process exit
- **CLI subcommands** alongside the TUI - `torchard review 1234`, `torchard new fdy main`, `torchard list` for scripting
