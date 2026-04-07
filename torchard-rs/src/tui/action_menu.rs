// torchard-rs/src/tui/action_menu.rs
// Stub — will be replaced in Task 8

use crossterm::event::Event;
use ratatui::prelude::*;

use crate::manager::Manager;
use super::{ScreenAction, ScreenBehavior};

pub struct ActionMenuScreen;

impl ScreenBehavior for ActionMenuScreen {
    fn render(&self, _f: &mut Frame, _area: Rect, _manager: &Manager) {}

    fn handle_event(&mut self, _event: &Event, _manager: &mut Manager) -> ScreenAction {
        ScreenAction::None
    }

    fn is_modal(&self) -> bool {
        true
    }
}
