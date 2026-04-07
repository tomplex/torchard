# Resolution Plan

**Verification command:** `uv run pytest tests/ -v`
**Date:** 2026-04-06

## Won't Fix

### #8: Duplicated wizard infrastructure across NewSessionScreen and AdoptSessionScreen
Extraction requires designing a new Textual abstraction (branch-picker widget/mixin); the three screens work independently and the cost exceeds the maintenance benefit for a personal tool.

### #24: Linear scan lookups for entity retrieval in Manager
Tables have <100 rows; adding targeted DB queries adds code without measurable benefit at current scale.

### #27: `detect_subsystems` has hard-coded directory names
Personal tool where the list reflects actual repo structures; configuration infrastructure would be overkill.

### #28: Duplicated `_completed` test helper across test files
Two copies of a 5-line mock factory; extraction to conftest adds a file for negligible maintenance gain.

## Batches

### Batch 1: Create shared utility modules (foundation, mechanical)
Unblocks: #12
- #3: Extract `_safe_id` to `torchard/tui/utils.py`
- #4: Extract `_truncate` variants to `torchard/tui/utils.py`
- #22: Extract `_sanitize_for_tmux` to `torchard/core/tmux.py`

### Batch 2: Dead code removal (mechanical)
- #15: Remove unused `fuzzy_filter`
- #16: Remove unused `import os` in manager.py
- #17: Remove unused `import tmux` in history.py
- #18: Remove unused `check` parameter (tmux.py + git.py)
- #20: Remove unused `created_worktree` variable
- #21: Remove `Conversation.files` field and `_FILES_RE`
- #25: Move `_repo_color` below all imports in session_list.py

### Batch 3: Consistency and small DRY fixes (mechanical)
- #5: Extract `_get_or_create_repo` helper in Manager
- #6: Remove duplicated CSS from CleanupScreen and HistoryScreen
- #7: Route history.py raw tmux calls through wrapper
- #11: Replace bare `Exception` catches with typed exceptions
- #23: Fix hardcoded `/Users/tom/` path in history.py
- #26: Rename `core/history.py` to `conversation_index.py`

### Batch 4: Decompose `_refresh_table` (architectural)
- #1: Extract sorting and row-rendering from monolithic method

### Batch 5: Decompose `scan_existing` (architectural)
- #2: Split into `_scan_repos`, `_scan_worktrees`, `_scan_tmux_sessions`

### Batch 6: Strengthen Manager API boundary (architectural)
- #9: Define `SessionInfo` dataclass for `list_sessions`
- #10: Add public methods to Manager so views stop accessing `_conn`

### Batch 7: Extract HelpScreen from session_list.py (architectural)
- #12: Move HelpScreen to its own file, clean up session_list.py

### Batch 8: Extract tmux layout policy (architectural)
- #13: Separate window layout setup from session creation logic
