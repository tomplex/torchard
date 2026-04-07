// torchard-rs/src/tui/help.rs
// Stub — will be replaced in Task 9

use crossterm::event::Event;
use ratatui::prelude::*;

use crate::manager::Manager;
use super::{ScreenAction, ScreenBehavior};

pub struct HelpScreen;

impl ScreenBehavior for HelpScreen {
    fn render(&self, _f: &mut Frame, _area: Rect, _manager: &Manager) {}

    fn handle_event(&mut self, _event: &Event, _manager: &mut Manager) -> ScreenAction {
        ScreenAction::None
    }

    fn is_modal(&self) -> bool {
        true
    }
}
