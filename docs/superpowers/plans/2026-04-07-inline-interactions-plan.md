# Inline Interactions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace modal-based interactions in SessionListScreen with inline alternatives (status line confirms, in-row rename, status line inputs, anchored dropdown menu).

**Architecture:** Add an `InlineMode` enum to SessionListScreen. When active, it intercepts key handling and modifies rendering. All changes are in `session_list.rs` with a minor layout change in `tui/mod.rs`.

**Tech Stack:** Rust, ratatui, crossterm (existing stack — no new dependencies)

**Spec:** `docs/superpowers/specs/2026-04-07-inline-interactions-design.md`

---

## File Structure

```
src/tui/session_list.rs  — major changes (InlineMode, rendering, key handling)
```

No new files. No other files modified.

---

## Task 1: Add InlineMode enum and status line to layout

**Files:**
- Modify: `src/tui/session_list.rs`

Add the `InlineMode` enum, a `status_message` field for feedback, and update the render layout to include a status line between the table and footer.

- [ ] **Step 1: Add InlineMode enum and ConfirmAction enum above SessionListScreen struct**

```rust
#[derive(Debug, Clone)]
enum ConfirmAction {
    DeleteSession { session_id: i64 },
    KillTab { session_name: String, window_index: i64 },
    KillSession { session_name: String },
}

#[derive(Debug)]
enum InlineMode {
    None,
    Confirm { message: String, action: ConfirmAction },
    Rename { input: String, cursor: usize, is_session: bool, session_id: Option<i64>, session_name: String, window_index: Option<i64> },
    Review { input: String, cursor: usize, repo_index: usize, repos: Vec<Repo> },
    NewTab { input: String, cursor: usize, session_id: i64, session_name: String },
    ActionMenu { items: Vec<(String, String)>, cursor: usize },
}
```

- [ ] **Step 2: Add `inline_mode` and `status_message` fields to SessionListScreen**

Add to the struct:
```rust
pub struct SessionListScreen {
    // ... existing fields ...
    inline_mode: InlineMode,
    status_message: Option<String>,
}
```

Initialize both in `new()`: `inline_mode: InlineMode::None, status_message: None`.

- [ ] **Step 3: Update render layout to include status line**

Change the layout from 3 chunks (filter, table, footer) to 4 chunks (filter, table, status line, footer):

```rust
let status_height = match &self.inline_mode {
    InlineMode::None => if self.status_message.is_some() { 1 } else { 0 },
    _ => 1,
};

let chunks = Layout::default()
    .direction(Direction::Vertical)
    .constraints([
        Constraint::Length(filter_height),  // filter
        Constraint::Min(0),                 // table
        Constraint::Length(status_height),   // status line
        Constraint::Length(1),              // footer
    ])
    .split(area);
```

Render the status line in `chunks[2]`:
```rust
// Status line
match &self.inline_mode {
    InlineMode::None => {
        if let Some(ref msg) = self.status_message {
            let status = Paragraph::new(msg.as_str())
                .style(Style::default().fg(theme::TEXT_DIM).bg(theme::BG));
            f.render_widget(status, chunks[2]);
        }
    }
    InlineMode::Confirm { message, .. } => {
        let status = Paragraph::new(message.as_str())
            .style(Style::default().fg(theme::YELLOW).bg(theme::BG));
        f.render_widget(status, chunks[2]);
    }
    _ => {} // Other modes rendered in later tasks
}
```

Move footer to `chunks[3]`.

- [ ] **Step 4: Update handle_event to check inline_mode first**

At the top of `handle_event`, before the existing key handling, add:

```rust
// If an inline mode is active, route to mode-specific handler
match &self.inline_mode {
    InlineMode::None => {}
    InlineMode::Confirm { .. } => return self.handle_confirm_key(*code, manager),
    // Other modes added in later tasks
    _ => return ScreenAction::None,
}
```

This goes after the mouse handling and the `Event::Key` extraction, but before the filter check.

- [ ] **Step 5: Add stub `handle_confirm_key` method**

```rust
fn handle_confirm_key(&mut self, code: KeyCode, manager: &mut Manager) -> ScreenAction {
    match code {
        KeyCode::Char('y') | KeyCode::Char('Y') | KeyCode::Enter => {
            // Will be implemented in Task 2
            self.inline_mode = InlineMode::None;
            ScreenAction::None
        }
        KeyCode::Char('n') | KeyCode::Char('N') | KeyCode::Esc => {
            self.inline_mode = InlineMode::None;
            ScreenAction::None
        }
        _ => ScreenAction::None,
    }
}
```

- [ ] **Step 6: Verify it compiles and tests pass**

Run: `cargo build && cargo test`

- [ ] **Step 7: Commit**

```
git commit -am "add InlineMode enum and status line to session list layout"
```

---

## Task 2: Inline confirm for delete

**Files:**
- Modify: `src/tui/session_list.rs`

Replace the ConfirmModal push in `action_delete` with setting `InlineMode::Confirm`, and implement `handle_confirm_key`.

- [ ] **Step 1: Rewrite `action_delete` to use InlineMode::Confirm**

Replace the current `action_delete` method. Instead of pushing `Screen::Confirm(...)` and setting `PendingAction`, it should set `self.inline_mode`:

For tab rows (`win:` prefix):
```rust
self.inline_mode = InlineMode::Confirm {
    message: format!("Kill tab {} in '{}'? [y] Yes  [n] No", window_index, session_name),
    action: ConfirmAction::KillTab { session_name, window_index },
};
```

For managed sessions:
```rust
let msg = if session.live {
    format!("Delete session '{}' (tmux session will be killed)? [y] Yes  [n] No", session.name)
} else {
    format!("Delete session '{}'? [y] Yes  [n] No", session.name)
};
self.inline_mode = InlineMode::Confirm {
    message: msg,
    action: ConfirmAction::DeleteSession { session_id: session.id.unwrap() },
};
```

For unmanaged sessions:
```rust
self.inline_mode = InlineMode::Confirm {
    message: format!("Kill tmux session '{}'? [y] Yes  [n] No", session.name),
    action: ConfirmAction::KillSession { session_name: session.name.clone() },
};
```

Return `ScreenAction::None` (no screen push).

- [ ] **Step 2: Implement `handle_confirm_key`**

```rust
fn handle_confirm_key(&mut self, code: KeyCode, manager: &mut Manager) -> ScreenAction {
    let action = match &self.inline_mode {
        InlineMode::Confirm { action, .. } => action.clone(),
        _ => return ScreenAction::None,
    };

    match code {
        KeyCode::Char('y') | KeyCode::Char('Y') | KeyCode::Enter => {
            match action {
                ConfirmAction::DeleteSession { session_id } => {
                    let _ = manager.delete_session(session_id, false);
                }
                ConfirmAction::KillTab { session_name, window_index } => {
                    let _ = tmux::kill_window(&session_name, window_index);
                }
                ConfirmAction::KillSession { session_name } => {
                    let _ = tmux::kill_session(&session_name);
                }
            }
            self.inline_mode = InlineMode::None;
            self.refresh(manager);
            ScreenAction::None
        }
        KeyCode::Char('n') | KeyCode::Char('N') | KeyCode::Esc => {
            self.inline_mode = InlineMode::None;
            ScreenAction::None
        }
        _ => ScreenAction::None,
    }
}
```

- [ ] **Step 3: Remove the `ConfirmDeleteTab`, `ConfirmDeleteSession`, `ConfirmKillSession` variants from `PendingAction`**

These are no longer needed since delete no longer pushes a ConfirmModal. Remove them from the enum and from the `on_child_result` match arms.

- [ ] **Step 4: Verify it compiles, test manually**

Run: `cargo build`
Test: launch the app, press `d` on a session — status line should show the confirm prompt. `y` confirms, `n` cancels.

- [ ] **Step 5: Commit**

```
git commit -am "replace delete confirm modal with inline status line prompt"
```

---

## Task 3: Inline rename

**Files:**
- Modify: `src/tui/session_list.rs`

Replace `action_rename` (which pushes RenameSessionScreen/RenameWindowScreen) with inline editing in the table row.

- [ ] **Step 1: Rewrite `action_rename` to set InlineMode::Rename**

For tab rows:
```rust
let parts: Vec<&str> = row_key.splitn(3, ':').collect();
let session_name = parts[1].to_string();
let window_index: i64 = parts[2].parse().unwrap_or(0);
let windows = tmux::list_windows(&session_name);
if let Some(win) = windows.iter().find(|w| w.index == window_index) {
    self.inline_mode = InlineMode::Rename {
        input: win.name.clone(),
        cursor: win.name.len(),
        is_session: false,
        session_id: None,
        session_name,
        window_index: Some(window_index),
    };
}
```

For session rows:
```rust
self.inline_mode = InlineMode::Rename {
    input: session.name.clone(),
    cursor: session.name.len(),
    is_session: true,
    session_id: session.id,
    session_name: session.name.clone(),
    window_index: None,
};
```

Return `ScreenAction::None`.

- [ ] **Step 2: Add `handle_rename_key` method**

```rust
fn handle_rename_key(&mut self, code: KeyCode, modifiers: crossterm::event::KeyModifiers, manager: &mut Manager) -> ScreenAction {
    let (input, cursor, is_session, session_id, session_name, window_index) = match &mut self.inline_mode {
        InlineMode::Rename { input, cursor, is_session, session_id, session_name, window_index } => {
            (input, cursor, *is_session, *session_id, session_name.clone(), *window_index)
        }
        _ => return ScreenAction::None,
    };

    match code {
        KeyCode::Enter => {
            let name = input.trim().to_string();
            if name.is_empty() {
                self.status_message = Some("Name cannot be empty.".to_string());
                self.inline_mode = InlineMode::None;
                return ScreenAction::None;
            }
            if is_session {
                let sanitized = tmux::sanitize_session_name(&name);
                if let Some(id) = session_id {
                    if manager.get_session_by_name(&sanitized).is_some() && sanitized != session_name {
                        self.status_message = Some(format!("Session '{}' already exists.", sanitized));
                        return ScreenAction::None;
                    }
                    if let Err(e) = manager.rename_session(id, &sanitized) {
                        self.status_message = Some(format!("Error: {}", e));
                        self.inline_mode = InlineMode::None;
                        return ScreenAction::None;
                    }
                }
            } else if let Some(win_idx) = window_index {
                if let Err(e) = tmux::rename_window(&session_name, win_idx, &name) {
                    self.status_message = Some(format!("Error: {}", e));
                    self.inline_mode = InlineMode::None;
                    return ScreenAction::None;
                }
            }
            self.status_message = Some("Renamed.".to_string());
            self.inline_mode = InlineMode::None;
            self.refresh(manager);
            ScreenAction::None
        }
        KeyCode::Esc => {
            self.inline_mode = InlineMode::None;
            ScreenAction::None
        }
        _ => {
            // Delegate to shared text input handler
            use super::rename::input_handle_key;
            // Need to re-borrow mutably
            if let InlineMode::Rename { input, cursor, .. } = &mut self.inline_mode {
                input_handle_key(input, cursor, code, modifiers);
            }
            ScreenAction::None
        }
    }
}
```

- [ ] **Step 3: Route rename keys in handle_event**

In the `handle_event` inline mode dispatch (added in Task 1 step 4), add:

```rust
InlineMode::Rename { .. } => {
    if let Event::Key(KeyEvent { code, modifiers, kind: KeyEventKind::Press, .. }) = event {
        return self.handle_rename_key(*code, *modifiers, manager);
    }
    return ScreenAction::None;
}
```

- [ ] **Step 4: Render the rename input in the table row**

In the render method, when `InlineMode::Rename` is active, override the Session column cell for the current row with an input widget. The key challenge: ratatui's `Table` doesn't support per-cell widgets. Instead, after rendering the table, overlay a `Paragraph` at the correct position.

Calculate the row position: `table_area.y + 1 (header) + cursor - scroll_offset`. Render a `Paragraph` with the input text and cursor highlight on top of the Session column area.

```rust
InlineMode::Rename { ref input, cursor: cursor_pos, .. } => {
    // Show input hint in status line
    let hint = Paragraph::new("[enter] confirm  [esc] cancel")
        .style(Style::default().fg(theme::TEXT_DIM).bg(theme::BG));
    f.render_widget(hint, chunks[2]);

    // Overlay input on the current row's Session column
    let table_area = chunks[1];
    let selected = self.table_state.selected().unwrap_or(0);
    let scroll_offset = self.table_state.offset();
    let visible_row = selected - scroll_offset;
    let row_y = table_area.y + 1 + visible_row as u16; // +1 for header

    if row_y < table_area.y + table_area.height {
        let session_col_width = table_area.width * 40 / 100; // matches Percentage(40)
        let input_area = Rect::new(table_area.x, row_y, session_col_width, 1);

        // Render input with cursor
        let before: String = input.chars().take(*cursor_pos).collect();
        let cursor_char = input.chars().nth(*cursor_pos).unwrap_or(' ');
        let after: String = input.chars().skip(*cursor_pos + 1).collect();

        let spans = vec![
            Span::styled(&before, Style::default().fg(theme::TEXT).bg(theme::CURSOR_BG)),
            Span::styled(
                cursor_char.to_string(),
                Style::default().fg(theme::BG).bg(theme::ACCENT),
            ),
            Span::styled(&after, Style::default().fg(theme::TEXT).bg(theme::CURSOR_BG)),
        ];
        let input_widget = Paragraph::new(Line::from(spans))
            .style(Style::default().bg(theme::CURSOR_BG));
        f.render_widget(input_widget, input_area);
    }
}
```

- [ ] **Step 5: Clear status_message on any non-inline action**

At the start of the normal key handling (after the inline mode dispatch), add:
```rust
self.status_message = None;
```

This clears feedback messages like "Renamed." when the user takes their next action.

- [ ] **Step 6: Verify it compiles, test manually**

Run: `cargo build`
Test: press `r` on a session — name should become editable in the row. Type, enter to confirm, escape to cancel.

- [ ] **Step 7: Commit**

```
git commit -am "replace rename modal with inline in-row editing"
```

---

## Task 4: Inline review

**Files:**
- Modify: `src/tui/session_list.rs`

Replace `action_review` (which pushes ReviewScreen) with a status line input.

- [ ] **Step 1: Rewrite `action_review` to set InlineMode::Review**

```rust
fn action_review(&mut self, manager: &Manager) -> ScreenAction {
    let mut repos = manager.get_repos();
    if repos.is_empty() {
        self.status_message = Some("No repos configured.".to_string());
        return ScreenAction::None;
    }
    // Sort by most recently active session
    let sessions = manager.get_sessions();
    let mut repo_last_active: HashMap<i64, String> = HashMap::new();
    for s in &sessions {
        if let Some(ref ts) = s.last_selected_at {
            let id = s.repo_id;
            if !repo_last_active.contains_key(&id) || ts > repo_last_active.get(&id).unwrap() {
                repo_last_active.insert(id, ts.clone());
            }
        }
    }
    repos.sort_by(|a, b| {
        let a_ts = a.id.and_then(|id| repo_last_active.get(&id));
        let b_ts = b.id.and_then(|id| repo_last_active.get(&id));
        b_ts.cmp(&a_ts)
    });

    self.inline_mode = InlineMode::Review {
        input: String::new(),
        cursor: 0,
        repo_index: 0,
        repos,
    };
    ScreenAction::None
}
```

- [ ] **Step 2: Add `handle_review_key` method**

```rust
fn handle_review_key(&mut self, code: KeyCode, modifiers: crossterm::event::KeyModifiers, manager: &mut Manager) -> ScreenAction {
    match code {
        KeyCode::Tab => {
            if let InlineMode::Review { repo_index, repos, .. } = &mut self.inline_mode {
                if repos.len() > 1 {
                    *repo_index = (*repo_index + 1) % repos.len();
                }
            }
            ScreenAction::None
        }
        KeyCode::Enter => {
            let (input, repo) = match &self.inline_mode {
                InlineMode::Review { input, repo_index, repos, .. } => {
                    (input.trim().to_string(), repos.get(*repo_index).cloned())
                }
                _ => return ScreenAction::None,
            };
            let repo = match repo {
                Some(r) => r,
                None => return ScreenAction::None,
            };
            if input.is_empty() {
                self.status_message = Some("Please enter a PR number or branch name.".to_string());
                return ScreenAction::None;
            }
            // Show checking out status
            self.status_message = Some("Checking out...".to_string());
            self.inline_mode = InlineMode::None;

            match manager.checkout_and_review(&repo.path, &input) {
                Ok((session, _worktree_path)) => {
                    return ScreenAction::Switch(SwitchAction::Session {
                        target: session.name,
                    });
                }
                Err(e) => {
                    self.status_message = Some(format!("Error: {}", e));
                    ScreenAction::None
                }
            }
        }
        KeyCode::Esc => {
            self.inline_mode = InlineMode::None;
            ScreenAction::None
        }
        _ => {
            use super::rename::input_handle_key;
            if let InlineMode::Review { input, cursor, .. } = &mut self.inline_mode {
                input_handle_key(input, cursor, code, modifiers);
            }
            ScreenAction::None
        }
    }
}
```

- [ ] **Step 3: Route review keys in handle_event**

```rust
InlineMode::Review { .. } => {
    if let Event::Key(KeyEvent { code, modifiers, kind: KeyEventKind::Press, .. }) = event {
        return self.handle_review_key(*code, *modifiers, manager);
    }
    return ScreenAction::None;
}
```

- [ ] **Step 4: Render review input in status line**

In the render match on `self.inline_mode`, add:

```rust
InlineMode::Review { ref input, cursor: cursor_pos, repo_index, ref repos } => {
    let repo_name = repos.get(*repo_index).map(|r| r.name.as_str()).unwrap_or("?");
    let prefix = format!("Review ({}): ", repo_name);
    let suffix = if repos.len() > 1 { "  [tab] cycle repo  [esc] cancel" } else { "  [esc] cancel" };

    let before: String = input.chars().take(*cursor_pos).collect();
    let cursor_char = input.chars().nth(*cursor_pos).unwrap_or(' ');
    let after: String = input.chars().skip(*cursor_pos + 1).collect();

    let spans = vec![
        Span::styled(&prefix, Style::default().fg(theme::ACCENT)),
        Span::styled(&before, Style::default().fg(theme::TEXT)),
        Span::styled(cursor_char.to_string(), Style::default().fg(theme::BG).bg(theme::ACCENT)),
        Span::styled(&after, Style::default().fg(theme::TEXT)),
        Span::styled(suffix, Style::default().fg(theme::TEXT_DIM)),
    ];
    let status = Paragraph::new(Line::from(spans)).style(Style::default().bg(theme::BG));
    f.render_widget(status, chunks[2]);
}
```

- [ ] **Step 5: Verify it compiles, test manually**

Run: `cargo build`
Test: press `R` — status line shows review input with repo name. Type, tab cycles repo, enter checks out, escape cancels.

- [ ] **Step 6: Commit**

```
git commit -am "replace review modal with inline status line input"
```

---

## Task 5: Inline new tab

**Files:**
- Modify: `src/tui/session_list.rs`

Add `t` keybinding for inline new-tab and change `n` to always push the new-session wizard directly.

- [ ] **Step 1: Add `action_new_tab` method**

```rust
fn action_new_tab(&mut self, _manager: &Manager) -> ScreenAction {
    // Find the managed session for the current row
    let session = match self.current_session() {
        Some(s) if s.managed => s.clone(),
        _ => {
            // Try parent session if on a child row
            if let Some(key) = self.current_row_key() {
                if key.starts_with("win:") {
                    let parts: Vec<&str> = key.splitn(3, ':').collect();
                    if parts.len() >= 2 {
                        let session_name = parts[1];
                        if let Some(s) = self.sessions.iter().find(|s| s.name == session_name && s.managed) {
                            let s = s.clone();
                            self.inline_mode = InlineMode::NewTab {
                                input: String::new(),
                                cursor: 0,
                                session_id: s.id.unwrap(),
                                session_name: s.name.clone(),
                            };
                            return ScreenAction::None;
                        }
                    }
                }
            }
            self.status_message = Some("No managed session selected.".to_string());
            return ScreenAction::None;
        }
    };
    if let Some(id) = session.id {
        self.inline_mode = InlineMode::NewTab {
            input: String::new(),
            cursor: 0,
            session_id: id,
            session_name: session.name.clone(),
        };
    }
    ScreenAction::None
}
```

- [ ] **Step 2: Add `handle_new_tab_key` method**

```rust
fn handle_new_tab_key(&mut self, code: KeyCode, modifiers: crossterm::event::KeyModifiers, manager: &mut Manager) -> ScreenAction {
    match code {
        KeyCode::Enter => {
            let (input, session_id, session_name) = match &self.inline_mode {
                InlineMode::NewTab { input, session_id, session_name, .. } => {
                    (input.trim().to_string(), *session_id, session_name.clone())
                }
                _ => return ScreenAction::None,
            };
            if input.is_empty() {
                self.status_message = Some("Branch name cannot be empty.".to_string());
                return ScreenAction::None;
            }
            self.inline_mode = InlineMode::None;
            match manager.add_tab(session_id, &input) {
                Ok(_) => {
                    tmux::send_keys(
                        &format!("{}:{}", session_name, input),
                        &["claude", "Enter"],
                    );
                    return ScreenAction::Switch(SwitchAction::Session {
                        target: session_name,
                    });
                }
                Err(e) => {
                    self.status_message = Some(format!("Error: {}", e));
                    ScreenAction::None
                }
            }
        }
        KeyCode::Esc => {
            self.inline_mode = InlineMode::None;
            ScreenAction::None
        }
        _ => {
            use super::rename::input_handle_key;
            if let InlineMode::NewTab { input, cursor, .. } = &mut self.inline_mode {
                input_handle_key(input, cursor, code, modifiers);
            }
            ScreenAction::None
        }
    }
}
```

- [ ] **Step 3: Route new-tab keys in handle_event**

```rust
InlineMode::NewTab { .. } => {
    if let Event::Key(KeyEvent { code, modifiers, kind: KeyEventKind::Press, .. }) = event {
        return self.handle_new_tab_key(*code, *modifiers, manager);
    }
    return ScreenAction::None;
}
```

- [ ] **Step 4: Render new-tab input in status line**

```rust
InlineMode::NewTab { ref input, cursor: cursor_pos, ref session_name, .. } => {
    let prefix = format!("New tab in '{}': ", session_name);
    let suffix = "  [enter] create  [esc] cancel";

    let before: String = input.chars().take(*cursor_pos).collect();
    let cursor_char = input.chars().nth(*cursor_pos).unwrap_or(' ');
    let after: String = input.chars().skip(*cursor_pos + 1).collect();

    let spans = vec![
        Span::styled(&prefix, Style::default().fg(theme::ACCENT)),
        Span::styled(&before, Style::default().fg(theme::TEXT)),
        Span::styled(cursor_char.to_string(), Style::default().fg(theme::BG).bg(theme::ACCENT)),
        Span::styled(&after, Style::default().fg(theme::TEXT)),
        Span::styled(suffix, Style::default().fg(theme::TEXT_DIM)),
    ];
    let status = Paragraph::new(Line::from(spans)).style(Style::default().bg(theme::BG));
    f.render_widget(status, chunks[2]);
}
```

- [ ] **Step 5: Update keybindings — `t` for new-tab, `n` for new-session directly**

In `handle_event`, change:
```rust
KeyCode::Char('n') => self.action_new_picker(manager),
```
to:
```rust
KeyCode::Char('n') => {
    let screen = super::new_session::NewSessionScreen::new(manager);
    ScreenAction::Push(Screen::NewSession(screen))
}
KeyCode::Char('t') => self.action_new_tab(manager),
```

Remove `action_new_picker`, `handle_new_picked`, and the `PendingAction::NewPicker` variant (no longer needed).

- [ ] **Step 6: Update footer keybindings**

Change the footer bindings to reflect new keys:
```rust
let bindings = vec![
    ("q", "Quit"),
    ("/", "Filter"),
    ("enter", "Switch"),
    ("h/l", "Collapse/Expand"),
    ("n", "New"),
    ("t", "Tab"),
    ("r", "Rename"),
    ("R", "Review"),
    ("d", "Delete"),
    ("H", "History"),
    (".", "Actions"),
    ("c", "Cleanup"),
    ("S", "Settings"),
    ("?", "Help"),
];
```

- [ ] **Step 7: Verify it compiles, test manually**

Run: `cargo build`
Test: `t` on a managed session opens inline new-tab input. `n` always opens the wizard. Enter creates the tab and switches.

- [ ] **Step 8: Commit**

```
git commit -am "add inline new-tab input and direct n for new-session"
```

---

## Task 6: Inline action menu (anchored dropdown)

**Files:**
- Modify: `src/tui/session_list.rs`

Replace the centered modal ActionMenu with a dropdown anchored near the cursor row.

- [ ] **Step 1: Rewrite `action_action_menu` to set InlineMode::ActionMenu**

Keep the same item-building logic (context-aware items based on session/tab row), but instead of pushing `Screen::ActionMenu(...)`, set:

```rust
self.inline_mode = InlineMode::ActionMenu {
    items,  // Vec<(String, String)> — (key, label)
    cursor: 0,
};
```

Remove the "rename" and "rename-tab" items from the action menu (these are now `r` directly).

Return `ScreenAction::None`.

- [ ] **Step 2: Add `handle_action_menu_key` method**

```rust
fn handle_action_menu_key(&mut self, code: KeyCode, manager: &mut Manager) -> ScreenAction {
    let (items, menu_cursor) = match &mut self.inline_mode {
        InlineMode::ActionMenu { items, cursor } => (items.clone(), cursor),
        _ => return ScreenAction::None,
    };

    match code {
        KeyCode::Char('j') | KeyCode::Down => {
            if let InlineMode::ActionMenu { cursor, items } = &mut self.inline_mode {
                if *cursor + 1 < items.len() {
                    *cursor += 1;
                }
            }
            ScreenAction::None
        }
        KeyCode::Char('k') | KeyCode::Up => {
            if let InlineMode::ActionMenu { cursor, .. } = &mut self.inline_mode {
                *cursor = cursor.saturating_sub(1);
            }
            ScreenAction::None
        }
        KeyCode::Enter => {
            let selected_key = items.get(*menu_cursor).map(|(k, _)| k.clone());
            self.inline_mode = InlineMode::None;
            if let Some(key) = selected_key {
                return self.handle_action_picked(Some(key), manager);
            }
            ScreenAction::None
        }
        KeyCode::Esc => {
            self.inline_mode = InlineMode::None;
            ScreenAction::None
        }
        _ => ScreenAction::None,
    }
}
```

- [ ] **Step 3: Route action menu keys in handle_event**

```rust
InlineMode::ActionMenu { .. } => {
    if let Event::Key(KeyEvent { code, kind: KeyEventKind::Press, .. }) = event {
        return self.handle_action_menu_key(*code, manager);
    }
    return ScreenAction::None;
}
```

- [ ] **Step 4: Render the anchored dropdown**

After the table is rendered, if `InlineMode::ActionMenu` is active, overlay a floating box near the cursor row:

```rust
InlineMode::ActionMenu { ref items, cursor: menu_cursor } => {
    // Draw hint in status line
    let hint = Paragraph::new("[j/k] navigate  [enter] select  [esc] cancel")
        .style(Style::default().fg(theme::TEXT_DIM).bg(theme::BG));
    f.render_widget(hint, chunks[2]);

    // Calculate dropdown position anchored to cursor row
    let table_area = chunks[1];
    let selected = self.table_state.selected().unwrap_or(0);
    let scroll_offset = self.table_state.offset();
    let visible_row = selected - scroll_offset;
    let anchor_y = table_area.y + 1 + visible_row as u16;

    let menu_height = items.len().min(8) as u16 + 2; // +2 for border
    let menu_width = items.iter().map(|(_, label)| label.len()).max().unwrap_or(10) as u16 + 6; // padding + border

    // Position: below if room, above if not
    let menu_y = if anchor_y + 1 + menu_height <= table_area.y + table_area.height {
        anchor_y + 1
    } else {
        anchor_y.saturating_sub(menu_height)
    };

    let menu_area = Rect::new(
        table_area.x + 2,
        menu_y,
        menu_width.min(table_area.width - 4),
        menu_height.min(table_area.height),
    );

    // Clear area and draw menu
    f.render_widget(ratatui::widgets::Clear, menu_area);

    let menu_items: Vec<Line> = items.iter().enumerate().map(|(i, (_, label))| {
        if i == *menu_cursor {
            Line::from(Span::styled(
                format!(" {} ", label),
                Style::default().fg(Color::White).bg(theme::CURSOR_BG),
            ))
        } else {
            Line::from(Span::styled(
                format!(" {} ", label),
                Style::default().fg(theme::TEXT),
            ))
        }
    }).collect();

    let menu_block = Block::default()
        .borders(ratatui::widgets::Borders::ALL)
        .border_style(Style::default().fg(theme::ACCENT))
        .style(Style::default().bg(theme::HEADER_BG));

    let menu_widget = Paragraph::new(menu_items).block(menu_block);
    f.render_widget(menu_widget, menu_area);
}
```

- [ ] **Step 5: Remove `PendingAction::ActionMenu` variant and clean up**

Remove `PendingAction::ActionMenu` from the enum. The `handle_action_picked` method stays — it's still called by the inline menu on enter. But remove the `on_child_result` match arm for `PendingAction::ActionMenu`.

If `PendingAction` is now just `None`, you can remove the enum entirely and the `pending_action` field. Check if any remaining variants are needed.

- [ ] **Step 6: Verify it compiles, test manually**

Run: `cargo build`
Test: press `.` on a session — dropdown appears near the row. j/k navigate, enter selects, escape dismisses.

- [ ] **Step 7: Commit**

```
git commit -am "replace centered action menu modal with anchored dropdown"
```

---

## Task 7: Final cleanup and polish

**Files:**
- Modify: `src/tui/session_list.rs`

- [ ] **Step 1: Remove unused PendingAction if fully emptied**

If all PendingAction variants have been removed in previous tasks, remove the enum and `pending_action` field entirely.

- [ ] **Step 2: Ensure escape clears any active inline mode before quitting**

In the `Esc` handling, check if inline_mode is active first:
```rust
KeyCode::Esc => {
    if !matches!(self.inline_mode, InlineMode::None) {
        self.inline_mode = InlineMode::None;
        return ScreenAction::None;
    }
    if !self.filter.is_empty() {
        self.filter.clear();
        self.refresh(manager);
        ScreenAction::None
    } else {
        ScreenAction::Quit
    }
}
```

(This should already be handled by the inline mode dispatch at the top of handle_event, but belt-and-suspenders.)

- [ ] **Step 3: Verify all inline modes suppress normal keybindings**

Confirm that when any InlineMode is active, the normal keybinding match arm is never reached (the inline mode dispatch at the top of handle_event returns early for all non-None modes).

- [ ] **Step 4: Run full test suite**

Run: `cargo test`
Expected: All 40 tests pass.

- [ ] **Step 5: Build release and test manually**

Run: `cargo build --release`
Test all interactions end-to-end: `d` (inline confirm), `r` (inline rename), `R` (inline review), `t` (inline new tab), `.` (anchored dropdown), `n` (new session wizard).

- [ ] **Step 6: Commit**

```
git commit -am "clean up inline interactions and remove unused PendingAction"
```
