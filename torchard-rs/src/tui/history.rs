// torchard-rs/src/tui/history.rs — stub

use crossterm::event::{Event, KeyCode, KeyEvent, KeyEventKind};
use ratatui::prelude::*;
use ratatui::widgets::{Block, Borders, Paragraph};

use crate::manager::Manager;
use super::{ScreenAction, ScreenBehavior};
use super::theme;

pub struct HistoryScreen {
    scope_label: Option<String>,
}

impl HistoryScreen {
    pub fn new(
        _manager: &Manager,
        _scope_paths: Option<Vec<String>>,
        scope_label: Option<String>,
    ) -> Self {
        Self { scope_label }
    }
}

impl ScreenBehavior for HistoryScreen {
    fn render(&self, f: &mut Frame, area: Rect, _manager: &Manager) {
        let title = match &self.scope_label {
            Some(label) => format!(" History — {} (TODO) ", label),
            None => " History (TODO) ".to_string(),
        };
        let block = Block::default()
            .title(title)
            .borders(Borders::ALL)
            .border_style(Style::default().fg(theme::ACCENT))
            .style(Style::default().fg(theme::TEXT).bg(theme::HEADER_BG));
        let inner = block.inner(area);
        f.render_widget(block, area);
        let msg = Paragraph::new("History screen — not yet implemented.\nPress Escape to go back.")
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
        false
    }
}
