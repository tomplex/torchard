// torchard-rs/src/tui/rename.rs — stubs

use crossterm::event::{Event, KeyCode, KeyEvent, KeyEventKind};
use ratatui::prelude::*;
use ratatui::widgets::{Block, Borders, Paragraph};

use crate::manager::Manager;
use super::{ScreenAction, ScreenBehavior};
use super::theme;

// ---------------------------------------------------------------------------
// RenameSessionScreen
// ---------------------------------------------------------------------------

pub struct RenameSessionScreen {
    session_id: i64,
    current_name: String,
}

impl RenameSessionScreen {
    pub fn new(_manager: &Manager, session_id: i64, current_name: String) -> Self {
        Self { session_id, current_name }
    }
}

impl ScreenBehavior for RenameSessionScreen {
    fn render(&self, f: &mut Frame, area: Rect, _manager: &Manager) {
        let block = Block::default()
            .title(format!(" Rename '{}' (TODO) ", self.current_name))
            .borders(Borders::ALL)
            .border_style(Style::default().fg(theme::ACCENT))
            .style(Style::default().fg(theme::TEXT).bg(theme::HEADER_BG));
        let inner = block.inner(area);
        f.render_widget(block, area);
        let msg = Paragraph::new(format!(
            "Rename session screen — not yet implemented.\nSession ID: {}\nPress Escape to go back.",
            self.session_id
        ))
        .style(Style::default().fg(theme::TEXT));
        f.render_widget(msg, inner);
    }

    fn handle_event(&mut self, event: &Event, _manager: &mut Manager) -> ScreenAction {
        if let Event::Key(KeyEvent { code: KeyCode::Esc, kind: KeyEventKind::Press, .. }) = event {
            return ScreenAction::Pop;
        }
        ScreenAction::None
    }

    fn is_modal(&self) -> bool {
        true
    }
}

// ---------------------------------------------------------------------------
// RenameWindowScreen
// ---------------------------------------------------------------------------

pub struct RenameWindowScreen {
    session_name: String,
    window_index: i64,
    current_name: String,
}

impl RenameWindowScreen {
    pub fn new(session_name: String, window_index: i64, current_name: String) -> Self {
        Self { session_name, window_index, current_name }
    }
}

impl ScreenBehavior for RenameWindowScreen {
    fn render(&self, f: &mut Frame, area: Rect, _manager: &Manager) {
        let block = Block::default()
            .title(format!(" Rename tab '{}' (TODO) ", self.current_name))
            .borders(Borders::ALL)
            .border_style(Style::default().fg(theme::ACCENT))
            .style(Style::default().fg(theme::TEXT).bg(theme::HEADER_BG));
        let inner = block.inner(area);
        f.render_widget(block, area);
        let msg = Paragraph::new(format!(
            "Rename window screen — not yet implemented.\n{}:{}\nPress Escape to go back.",
            self.session_name, self.window_index
        ))
        .style(Style::default().fg(theme::TEXT));
        f.render_widget(msg, inner);
    }

    fn handle_event(&mut self, event: &Event, _manager: &mut Manager) -> ScreenAction {
        if let Event::Key(KeyEvent { code: KeyCode::Esc, kind: KeyEventKind::Press, .. }) = event {
            return ScreenAction::Pop;
        }
        ScreenAction::None
    }

    fn is_modal(&self) -> bool {
        true
    }
}
