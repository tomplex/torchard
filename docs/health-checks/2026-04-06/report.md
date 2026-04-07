# Codebase Health Check -- 2026-04-06

**Scope:** Full codebase (`.`)
**Context:** TUI tmux and worktree workflow app. All areas are actively being extended. No known pain points reported.

## Executive Summary

Torchard is a well-structured ~33-file Python TUI app with no critical findings. The codebase's main health themes are: (1) a handful of important complexity hotspots where monolithic methods mix too many responsibilities, (2) significant duplication of utility functions and wizard UI infrastructure across view files with no shared utility module, and (3) TUI views bypassing the Manager layer to access the database directly, eroding module boundaries. Addressing these would reduce the surface area for bugs when extending the app.

## Finding Counts

| Severity | Count |
|----------|-------|
| Critical | 0     |
| Important| 13    |
| Minor    | 15    |
| **Total**| **28** |

## Findings

### Critical

No critical findings.

### Important

#### 1. Monolithic `_refresh_table` with dead triple-sort pattern
- **Category:** Complexity, Confusing Code, Dead Code
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/views/session_list.py:195`
- **Details:** This ~90-line method mixes session sorting, fuzzy filtering, repo-grouped re-sorting, status dot selection, expand/collapse rendering, and cursor restoration all inline. The triple-sort pattern (lines 212-219) is particularly confusing -- the first sort via `_sort_key` is immediately overwritten by two subsequent sorts, making it dead code. The same triple-sort pattern repeats for grouped mode (lines 243-253).
- **Suggestion:** Extract sorting into a method with a single composite key, extract row-rendering into its own method, and remove the dead first sort pass.

#### 2. `scan_existing` has deep nesting and multiple responsibilities
- **Category:** Complexity
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/manager.py:363`
- **Details:** This ~95-line method handles three distinct discovery tasks (repos, worktrees, tmux sessions) in a single function. The worktree scanning section (lines 390-429) reaches 5 levels of nesting with interleaved filesystem checks and database operations.
- **Suggestion:** Split into three private methods (e.g., `_scan_repos`, `_scan_worktrees`, `_scan_tmux_sessions`) called from `scan_existing`.

#### 3. `_safe_id` utility duplicated across 4 files
- **Category:** DRY Violations
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/views/new_session.py:21`, `adopt_session.py:22`, `edit_branch.py:18`, `history.py:19`
- **Details:** The identical `_safe_id(text: str) -> str` using `re.sub(r"[^a-zA-Z0-9_-]", "_", text)` is copy-pasted in four view files. Any change to the sanitization rule requires updating all four. The copy in `history.py` is additionally never called (dead code).
- **Suggestion:** Extract into a shared `torchard/tui/utils.py` module and import from there.

#### 4. `_truncate` duplicated across 3 files with inconsistent behavior
- **Category:** DRY Violations, Inconsistent Patterns
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/views/session_list.py:610`, `history.py:23`, `cleanup.py:263`
- **Details:** Three separate `_truncate` functions exist. The session_list and history versions truncate from the right (appending "..."), while the cleanup version truncates from the left (prepending "..."). The two right-truncating copies are identical. A developer could easily confuse the two behaviors since they share the same name.
- **Suggestion:** Extract both variants into a shared module with explicit names (e.g., `truncate_end` and `truncate_start`).

#### 5. "Ensure repo exists" pattern repeated 3 times in Manager
- **Category:** DRY Violations
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/manager.py:93`, `manager.py:161`, `manager.py:217`
- **Details:** The same 4-line block -- `_get_repo_by_path`, check if None, `detect_default_branch`, `add_repo` -- appears identically in `create_session`, `adopt_session`, and `checkout_and_review`. Any change to repo registration logic requires updating all three.
- **Suggestion:** Extract a `_get_or_create_repo(self, repo_path: str) -> Repo` helper method.

#### 6. DataTable/Footer CSS theme duplicated across 3 locations
- **Category:** DRY Violations, Inconsistent Patterns
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/app.py:14`, `cleanup.py:209`, `history.py:232`
- **Details:** The exact same CSS rules for DataTable and Footer styling (background colors, cursor colors, accent colors) are copy-pasted in the app-level CSS and in `CleanupScreen` and `HistoryScreen` `DEFAULT_CSS`. The app-level CSS should already apply globally, making the per-screen copies redundant.
- **Suggestion:** Remove the duplicate CSS from individual screen `DEFAULT_CSS` blocks, relying on the global CSS in `TorchardApp.CSS`.

#### 7. Mixed subprocess tmux calls bypassing the tmux wrapper
- **Category:** Inconsistent Patterns, DRY Violations
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/manager.py:136`, `session_list.py:483`, `history.py:202`
- **Details:** The codebase has a dedicated `tmux.py` wrapper providing `rename_window`, `select_window`, `new_window`, etc. with consistent error handling (raising `TmuxError`). However, several call sites use raw `subprocess.run(["tmux", ...])` directly, silently discarding failures. This defeats the purpose of the wrapper and splits tmux interaction knowledge.
- **Suggestion:** Route all tmux subprocess calls through `tmux.py`, adding any missing wrapper functions as needed.

#### 8. Duplicated wizard infrastructure across NewSessionScreen and AdoptSessionScreen
- **Category:** DRY Violations, Extensibility
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/views/new_session.py:34`, `adopt_session.py:26`, `edit_branch.py:114`
- **Details:** Three screens implement nearly identical logic for: step-based wizard flow, repo/branch selection with filter, `_populate_branch_list`, `_confirm_list_selection`, `_select_branch_item`, and ad-hoc `_AdhocRepo`/`_DirRepo` inner classes (which duplicate the existing `Repo` dataclass). Changes to the wizard UX pattern must be applied in multiple places.
- **Suggestion:** Extract a reusable branch-picker widget or mixin, and use the `Repo` dataclass directly (with `id=None`) instead of ad-hoc inner classes.

#### 9. `list_sessions` returns untyped `list[dict]`
- **Category:** Extensibility
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/manager.py:459`
- **Details:** `Manager.list_sessions()` returns `list[dict]` with string keys like "id", "name", "repo_id", "attached", "live", etc. Every consumer accesses these via string keys with no type checking. Adding or renaming a field requires grep-and-fix with no compiler help. `session_list.py` alone references these dict keys in ~20 places.
- **Suggestion:** Define a `SessionInfo` dataclass to replace the raw dict, providing IDE support and catching key mismatches at type-check time.

#### 10. TUI views directly access Manager._conn (private attribute)
- **Category:** Extensibility, Naming & Organization
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/views/session_list.py:196`, `edit_branch.py:93`, `rename_session.py:65`, `adopt_session.py:116`, `history.py:179`, `new_session.py:353`, `cleanup.py:49`
- **Details:** 11+ call sites across 7 view files reach through Manager to access its private `_conn` attribute for direct DB calls. The Manager layer exists as an orchestration boundary, but views routinely bypass it. Any change to Manager's internal storage would require changes in every view file.
- **Suggestion:** Add public methods to Manager for the operations views need (e.g., `get_repos()`, `touch_session()`, `get_session_by_name()`).

#### 11. Inconsistent error handling -- bare Exception vs typed exceptions
- **Category:** Inconsistent Patterns
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/manager.py:323`, `new_session.py:412`, `cleanup.py:183`
- **Details:** The core layer defines typed exceptions (`GitError`, `TmuxError`) and raises them consistently. However, the manager and TUI layers almost always catch bare `Exception` instead of the specific types. This defeats the purpose of typed exceptions and could mask unexpected errors (e.g., `TypeError`, `AttributeError`).
- **Suggestion:** Catch the specific exception types (`GitError`, `TmuxError`) in the manager and TUI layers.

#### 12. `session_list.py` is a 613-line mega-file with mixed concerns
- **Category:** Naming & Organization
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/views/session_list.py:1`
- **Details:** This file contains two unrelated classes (`HelpScreen` and `SessionListScreen`), dead functions (`_get_claude_session_id`), a duplicate `_truncate` helper, and `_repo_color` wedged between import blocks. At 613 lines it is the largest file and combines presentation, orchestration, sorting, and help text.
- **Suggestion:** Extract `HelpScreen` into its own file. Remove dead code. Move shared utilities to a common module.

#### 13. `create_session` mixes tmux window layout policy with session creation
- **Category:** Extensibility, Complexity
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/manager.py:134`
- **Details:** Lines 134-140 hard-code a specific tmux window layout (rename to "claude", launch claude, create "shell" window, select window 1) in the middle of the session creation workflow. `checkout_and_review` (line 255) uses a different layout, showing the policy is already diverging. Adding a new layout requires modifying the core method.
- **Suggestion:** Extract window layout setup into a separate function that `create_session` delegates to.

### Minor

#### 14. Unused function `_get_claude_session_id`
- **Category:** Dead Code
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/views/session_list.py:597`
- **Details:** Defined at module level but never called anywhere. Appears to be leftover from a refactor.
- **Suggestion:** Remove the function.

#### 15. Unused function `fuzzy_filter`
- **Category:** Dead Code
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/fuzzy.py:38`
- **Details:** Defined in `fuzzy.py` but never imported or called. Only `fuzzy_match` is used.
- **Suggestion:** Remove `fuzzy_filter` or keep only if planned for near-term use.

#### 16. Unused import `os` in manager.py
- **Category:** Dead Code
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/manager.py:5`
- **Details:** `os` is imported but never referenced in the file.
- **Suggestion:** Remove the import.

#### 17. Unused import `tmux` in history.py action_resume
- **Category:** Dead Code
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/views/history.py:201`
- **Details:** `tmux` is imported inside `action_resume` but never used; the method calls `subprocess.run` directly instead.
- **Suggestion:** Remove the unused import.

#### 18. Unused `check` parameter in `_run` (both tmux.py and git.py)
- **Category:** Dead Code, Confusing Code
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/tmux.py:12`, `git.py:12`
- **Details:** Both `_run` functions accept a `check` parameter but hard-code `check=False` to `subprocess.run`, ignoring it. The tmux version defaults `check=True`, which is actively misleading.
- **Suggestion:** Remove the `check` parameter from both functions.

#### 19. Unused tmux function `select_window`
- **Category:** Dead Code
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/tmux.py:89`
- **Details:** Defined but never called. The manager uses raw `subprocess.run` for the same operation.
- **Suggestion:** Either remove the function or migrate callers to use it (see finding #7).

#### 20. Unused variable `created_worktree` in `create_session`
- **Category:** Dead Code
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/manager.py:102`
- **Details:** Set to `False`/`True` but never read. The subsequent logic uses `start_dir != repo_path` instead.
- **Suggestion:** Remove the variable.

#### 21. `Conversation.files` field populated but never read
- **Category:** Dead Code
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/history.py:25`
- **Details:** The `files` field on `Conversation` is populated during parsing via `_FILES_RE`, but nothing ever reads `.files`. The regex also exists solely for this purpose.
- **Suggestion:** Remove the `files` field and `_FILES_RE` regex, or use the field in the history view.

#### 22. `_sanitize_for_tmux` duplicated in 2 files
- **Category:** DRY Violations
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/views/new_session.py:26`, `rename_session.py:18`
- **Details:** Same function with minor variation (one has a fallback for empty strings). A third inline variant exists in `manager.py:243`. All encode the same tmux naming rule.
- **Suggestion:** Extract to a shared location (e.g., `tmux.py` since it encodes tmux constraints) and use everywhere.

#### 23. Hardcoded path `/Users/tom/` in history view
- **Category:** Confusing Code
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/views/history.py:110`
- **Details:** Line 110 replaces `/Users/tom/` with `~/` for display. This is hardcoded to a specific user's home directory rather than using `Path.home()`.
- **Suggestion:** Use `str(Path.home())` to compute the prefix dynamically.

#### 24. Linear scan lookups for entity retrieval in Manager
- **Category:** Complexity
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/manager.py:63`
- **Details:** `_get_repo_by_id`, `_get_repo_by_path`, `_get_session_by_id`, and `_get_worktree_by_id` each load all rows and iterate to find a match. In `get_stale_worktrees`, `_get_repo_by_id` is called per worktree, causing N full-table scans. Not a performance issue at current scale but adds cognitive overhead.
- **Suggestion:** Add direct single-row query functions to `db.py`.

#### 25. `_repo_color` function definition splits the import block
- **Category:** Naming & Organization
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/tui/views/session_list.py:32`
- **Details:** `_REPO_COLORS` and `_repo_color` are defined between two groups of imports, making the import section hard to scan.
- **Suggestion:** Move below all imports.

#### 26. `history.py` name is ambiguous between core and TUI layers
- **Category:** Naming & Organization
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/history.py:1`
- **Details:** Two files named `history.py` exist -- `core/history.py` (conversation-index parser) and `tui/views/history.py` (history browser). The core module is really a conversation-index parser.
- **Suggestion:** Rename `core/history.py` to `conversation_index.py`.

#### 27. `detect_subsystems` has hard-coded directory names
- **Category:** Extensibility
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/torchard/core/manager.py:35`
- **Details:** Scans only `("workers", "src", "libs", "pods")` as parent directories. Each new repo convention requires a code change.
- **Suggestion:** Make the list configurable, falling back to current defaults.

#### 28. Duplicated `_completed` test helper across test files
- **Category:** Inconsistent Patterns
- **Location:** `/Users/tom/dev/worktrees/torchard/health-check-20260406/tests/test_git.py:23`, `test_tmux.py:21`
- **Details:** The same mock factory function creating a `MagicMock` with `returncode`, `stdout`, `stderr` is defined identically in both test files.
- **Suggestion:** Extract to a shared test utility or conftest fixture.

## Category Summaries

### Dead Code
Several minor dead code items: an unused `_get_claude_session_id` function, unused `fuzzy_filter`, unused imports (`os`, `tmux`), unused function parameters (`check` in both `_run` wrappers), an unused `select_window` wrapper, an unused `created_worktree` variable, and an unpopulated-but-never-read `Conversation.files` field. Additionally, the first sort pass in `_refresh_table` is dead code overwritten by subsequent sorts. None are critical, but collectively they add noise.

### Complexity
Two important hotspots: `_refresh_table` in session_list.py (~90 lines mixing sorting, filtering, and rendering with a confusing triple-sort) and `scan_existing` in manager.py (~95 lines with 5-level nesting handling three separate discovery tasks). `create_session` also mixes orchestration with tmux layout concerns. Linear-scan database lookups add minor unnecessary complexity.

### DRY Violations
The most prominent theme. `_safe_id` is duplicated 4 times, `_truncate` 3 times (with inconsistent behavior), `_sanitize_for_tmux` twice, and the "ensure repo exists" pattern 3 times in Manager. CSS theme rules are copy-pasted across 3 files. The wizard infrastructure (repo/branch picker, step flow) is substantially duplicated between NewSessionScreen and AdoptSessionScreen. No shared TUI utility module exists.

### Confusing Code
The misleading `check` parameter (accepted but ignored, with a default of `True` in tmux.py) is the clearest confusing-code finding. The hardcoded `/Users/tom/` path would break for other users. The ad-hoc inner classes (`_AdhocRepo`, `_DirRepo`) duck-typing as `Repo` objects are surprising when reading `self._selected_repo`.

### Extensibility
Views directly accessing `Manager._conn` (11+ call sites across 7 files) is the most significant extensibility concern -- it couples the entire TUI layer to the database implementation. `list_sessions` returning untyped dicts means no compiler help when the schema changes. The tmux layout policy is embedded in `create_session` and already diverging from `checkout_and_review`.

### Inconsistent Patterns
Bare `Exception` catches in the manager/TUI layers undermine the typed exceptions (`GitError`, `TmuxError`) defined in the core layer. Raw subprocess tmux calls coexist with the tmux wrapper module. Test helpers are duplicated across test files.

### Naming & Organization
`session_list.py` at 613 lines is the largest file and contains mixed concerns (two classes, dead functions, misplaced definitions). The dual `history.py` naming across core and TUI layers is mildly ambiguous. No shared TUI utility module exists, leading to the utility function duplication noted in DRY Violations.
