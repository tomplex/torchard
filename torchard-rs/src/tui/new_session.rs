// torchard-rs/src/tui/new_session.rs — stub

use crossterm::event::{Event, KeyCode, KeyEvent, KeyEventKind};
use ratatui::prelude::*;
use ratatui::widgets::{Block, Borders, Paragraph};

use crate::manager::Manager;
use super::{ScreenAction, ScreenBehavior};
use super::theme;

pub struct NewSessionScreen {
    _placeholder: (),
}

impl NewSessionScreen {
    pub fn new(_manager: &Manager) -> Self {
        Self { _placeholder: () }
    }
}

impl ScreenBehavior for NewSessionScreen {
    fn render(&self, f: &mut Frame, area: Rect, _manager: &Manager) {
        let block = Block::default()
            .title(" New Session (TODO) ")
            .borders(Borders::ALL)
            .border_style(Style::default().fg(theme::ACCENT))
            .style(Style::default().fg(theme::TEXT).bg(theme::HEADER_BG));
        let inner = block.inner(area);
        f.render_widget(block, area);
        let msg = Paragraph::new("New session screen — not yet implemented.\nPress Escape to go back.")
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
