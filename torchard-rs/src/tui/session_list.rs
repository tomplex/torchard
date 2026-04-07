// torchard-rs/src/tui/session_list.rs
// Stub — will be replaced in Task 10

use crossterm::event::Event;
use ratatui::prelude::*;

use crate::manager::Manager;
use super::{ScreenAction, ScreenBehavior};

pub struct SessionListScreen;

impl SessionListScreen {
    pub fn new(_manager: &Manager) -> Self {
        Self
    }
}

impl ScreenBehavior for SessionListScreen {
    fn render(&self, _f: &mut Frame, _area: Rect, _manager: &Manager) {}

    fn handle_event(&mut self, _event: &Event, _manager: &mut Manager) -> ScreenAction {
        ScreenAction::None
    }
}
