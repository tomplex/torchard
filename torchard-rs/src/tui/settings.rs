// torchard-rs/src/tui/settings.rs — stub

use crossterm::event::{Event, KeyCode, KeyEvent, KeyEventKind};
use ratatui::prelude::*;
use ratatui::widgets::{Block, Borders, Paragraph};

use crate::manager::Manager;
use super::{ScreenAction, ScreenBehavior};
use super::theme;

pub struct SettingsScreen {
    _placeholder: (),
}

impl SettingsScreen {
    pub fn new(_manager: &Manager) -> Self {
        Self { _placeholder: () }
    }
}

impl ScreenBehavior for SettingsScreen {
    fn render(&self, f: &mut Frame, area: Rect, _manager: &Manager) {
        let block = Block::default()
            .title(" Settings (TODO) ")
            .borders(Borders::ALL)
            .border_style(Style::default().fg(theme::ACCENT))
            .style(Style::default().fg(theme::TEXT).bg(theme::HEADER_BG));
        let inner = block.inner(area);
        f.render_widget(block, area);
        let msg = Paragraph::new("Settings screen — not yet implemented.\nPress Escape to go back.")
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
