# Batch 6: Strengthen Manager API boundary

**Date:** 2026-04-06
**Classification:** architectural
**Commit:** `f213bdc`

## Findings Resolved
- #9: Defined `SessionInfo` dataclass in models.py; `list_sessions()` now returns `list[SessionInfo]` instead of `list[dict]`; all view code migrated from dict key access to typed attribute access
- #10: Added public wrapper methods to Manager (`get_repos`, `get_sessions`, `get_worktrees_for_session`, `touch_session`, `get_session_by_name`); migrated 20+ call sites across 7 view files from `_manager._conn` to the public API; only `settings.py` (config) and `cleanup.py` (`get_worktrees`) still use `_conn` as those wrappers were out of scope

## Verification
```
95 passed in 0.08s
```

## Notes
Added 7 new tests: `test_unmanaged_session_included`, `test_session_info_has_all_fields` (contract tests for SessionInfo), and 5 tests for the new Manager wrapper methods. These were written before the migration to serve as a safety net. The test count grew from 88 to 95.
