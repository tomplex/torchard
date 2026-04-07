# Inline Interactions for Session List

Replace modal-based interactions in the SessionListScreen with inline alternatives that feel faster and more integrated. The session list gains modes that change rendering and input handling without pushing screens onto the stack.

## Status Line

A new persistent line between the table and the footer. Normally empty (or shows brief feedback like "Session renamed"). When an inline interaction is active, it shows the prompt/input.

```
┌─────────────────────────────────────────────────────┐
│ Session              Repo           Branch           │
│ ...                                                  │
│                                                      │
│ Delete session 'torchard'? [y] Yes  [n] No           │  ← status line
│ q Quit  / Filter  enter Switch  h/l Collapse/Expand  │  ← footer (always visible)
└─────────────────────────────────────────────────────┘
```

The footer keybindings remain visible at all times. The status line sits above it, vim-style.

## Changes

### 1. Inline Confirm (delete)

**Trigger:** `d` on a session or tab row.

**Behavior:** Status line shows the confirm prompt. For sessions: `Delete session '{name}'? [y] Yes [n] No`. For tabs: `Kill tab {index} in '{session}'? [y] Yes [n] No`. For unmanaged sessions: `Kill tmux session '{name}'? [y] Yes [n] No`.

**Keys:** `y`/`Y`/`Enter` confirms, `n`/`N`/`Escape` cancels. Status line clears. Normal keybindings suppressed during confirm.

**On confirm:** Same logic as current ConfirmModal callback — calls `manager.delete_session()`, `tmux::kill_window()`, or `tmux::kill_session()` as appropriate, then refreshes the table.

**Replaces:** ConfirmModal push from SessionListScreen.

### 2. Inline Rename

**Trigger:** `r` on a session or tab row.

**Behavior:** The name text in the Session column of the current row becomes an editable text input. Cursor visible, typing replaces text. Other columns (Repo, Branch) stay visible. The input is pre-filled with the current name, cursor at end.

**Keys:** Standard text editing (left/right, backspace, delete, home/end). `Enter` confirms, `Escape` cancels. Normal table keybindings (j/k, etc.) suppressed during rename.

**On confirm (session):** Sanitize via `tmux::sanitize_session_name`. Validate non-empty and non-duplicate via `manager.get_session_by_name`. Call `manager.rename_session`. On error, show error in status line.

**On confirm (tab):** Validate non-empty. Call `tmux::rename_window`. On error, show error in status line.

**After success:** Refresh table, status line shows brief "Renamed" feedback (clears on next action).

**Replaces:** RenameSessionScreen and RenameWindowScreen pushes from SessionListScreen.

### 3. Inline Review

**Trigger:** `R`.

**Behavior:** Status line becomes an input: `Review ({repo_name}): ▏  [tab] cycle repo [esc] cancel`. Text input for PR number or branch name. Tab cycles through repos (sorted by most recently active session, same as current ReviewScreen).

**On enter:** Status line shows "Checking out...". Calls `manager.checkout_and_review()` synchronously. On success, writes switch file and quits. On error, shows error in status line, input remains active for retry.

**Keys:** Standard text editing. `Tab` cycles repo. `Enter` submits. `Escape` cancels.

**Replaces:** ReviewScreen push.

### 4. Inline New Tab

**Trigger:** `t` (new direct keybinding).

**Precondition:** Current row is a managed session or a child of one. If not, no-op.

**Behavior:** Status line becomes an input: `New tab in '{session}': ▏  [enter] create [esc] cancel`. Text input for branch name.

**On enter:** Calls `manager.add_tab(session_id, branch_name)`, then `tmux::send_keys` to send "claude" + Enter, writes switch file, quits. On error, shows error in status line.

**Replaces:** NewTabScreen push and the "New..." picker ActionMenu (which decided between new session vs new tab).

### 5. Inline Action Menu

**Trigger:** `.` on a session or tab row.

**Behavior:** A small dropdown menu appears anchored near the current cursor row, overlaying the table. Positioned below the row if there's room, above if near the bottom of the table. Items are context-dependent (same logic as current ActionMenu):

Session-level (managed): Change branch, Launch claude.
Session-level (unmanaged): Adopt session.
Tab-level: (none — rename is now `r` directly, so no action menu for tabs)

**Keys:** `j`/`k`/`Up`/`Down` navigate, `Enter` selects, `Escape` dismisses.

**On select:** Same behavior as current `handle_action_picked` — pushes EditBranchScreen, or executes launch-claude inline, or pushes AdoptSessionScreen.

**Rendering:** Floating box with border, anchored to cursor row. Background matches `HEADER_BG`. Width auto-sized to content. Max height ~6 items.

**Replaces:** Centered modal ActionMenu for session list usage. The ActionMenu screen type still exists for use by other contexts if needed.

## Keybinding Changes

| Key | Before | After |
|-----|--------|-------|
| `r` | Rename (already direct) | Inline rename (no screen push) |
| `R` | Review (pushes screen) | Inline review (status line input) |
| `t` | (unused) | Inline new tab (status line input) |
| `n` | New picker menu → session or tab | New session wizard (always) |
| `d` | Delete (pushes ConfirmModal) | Inline confirm (status line) |
| `.` | Action menu (centered modal) | Action menu (anchored dropdown) |

## Implementation Approach

All changes are scoped to `session_list.rs`. The SessionListScreen gains an `InlineMode` enum:

```rust
enum InlineMode {
    None,
    Confirm { message: String, action: ConfirmAction },
    Rename { input: String, cursor: usize, row_key: String },
    Review { input: String, cursor: usize, repo_index: usize, repos: Vec<Repo> },
    NewTab { input: String, cursor: usize, session_id: i64, session_name: String },
    ActionMenu { items: Vec<(String, String)>, cursor: usize, anchor_row: u16 },
}
```

When `inline_mode` is not `None`, `handle_event` routes to mode-specific key handling and `render` draws the mode-specific UI (status line content, in-row input, or dropdown).

## Screens Affected

- `session_list.rs` — major changes (inline mode state machine, rendering, key handling)
- `tui/mod.rs` — layout adds status line; `n` keybinding change
- Other screen files — no changes (ConfirmModal, ReviewScreen, etc. still exist for other callers)

## Out of Scope

- Inline interactions for other screens (cleanup confirm, etc.) — those keep using modals
- Removing the modal screen types from code — they're still used elsewhere
- New features — this is purely a UX improvement to existing interactions
