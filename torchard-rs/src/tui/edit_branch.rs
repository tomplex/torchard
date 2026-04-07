// torchard-rs/src/tui/edit_branch.rs — stub

use crossterm::event::{Event, KeyCode, KeyEvent, KeyEventKind};
use ratatui::prelude::*;
use ratatui::widgets::{Block, Borders, Paragraph};

use crate::manager::Manager;
use super::{ScreenAction, ScreenBehavior};
use super::theme;

pub struct EditBranchScreen {
    session_id: i64,
    session_name: String,
}

impl EditBranchScreen {
    pub fn new(_manager: &Manager, session_id: i64, session_name: String) -> Self {
        Self { session_id, session_name }
    }
}

impl ScreenBehavior for EditBranchScreen {
    fn render(&self, f: &mut Frame, area: Rect, _manager: &Manager) {
        let block = Block::default()
            .title(format!(" Change branch — {} (TODO) ", self.session_name))
            .borders(Borders::ALL)
            .border_style(Style::default().fg(theme::ACCENT))
            .style(Style::default().fg(theme::TEXT).bg(theme::HEADER_BG));
        let inner = block.inner(area);
        f.render_widget(block, area);
        let msg = Paragraph::new(format!(
            "Edit branch screen — not yet implemented.\nSession ID: {}\nPress Escape to go back.",
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
