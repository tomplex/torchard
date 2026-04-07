// torchard-rs/src/main.rs
mod models;
mod db;
mod tmux;
mod git;
mod manager;
mod claude_session;
mod conversation_index;
mod fuzzy;
mod switch;
mod utils;
mod tui;

fn main() {
    switch::cleanup();

    let data_dir = dirs::data_dir().expect("no data dir");
    let db_path = data_dir.join("torchard").join("torchard.db");
    let first_run = !db_path.exists();
    let conn = db::init_db(&db_path);
    let mut mgr = manager::Manager::new(conn);
    if first_run {
        mgr.scan_existing();
    }

    let mut terminal = ratatui::init();
    let mut app = tui::App::new(mgr);
    app.run(&mut terminal);
    ratatui::restore();

    if let Some(action) = switch::read_switch() {
        match &action {
            switch::SwitchAction::Session { target } => {
                tmux::switch_client(target).ok();
            }
            switch::SwitchAction::Window { session, window } => {
                tmux::switch_client(&format!("{}:{}", session, window)).ok();
            }
        }
        switch::cleanup();
    }
}
