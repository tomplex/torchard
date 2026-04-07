# Batch 3: Consistency and small DRY fixes

**Date:** 2026-04-06
**Classification:** mechanical
**Commit:** `b7c2425`

## Findings Resolved
- #5: Extracted `_get_or_create_repo` helper in Manager, replacing 3 duplicated 4-line blocks
- #6: Removed duplicated DataTable/Footer CSS from CleanupScreen and HistoryScreen DEFAULT_CSS
- #7: Replaced 4 raw `subprocess.run(["tmux", ...])` calls in history.py with tmux wrapper functions
- #11: Replaced 9 bare `except Exception` catches across 8 files with typed exceptions (GitError, TmuxError, ValueError)
- #23: Replaced hardcoded `/Users/tom/` with `str(Path.home()) + "/"` in history.py
- #26: Renamed `torchard/core/history.py` to `torchard/core/conversation_index.py`, updated imports

## Verification
```
88 passed in 0.06s
```

## Notes
The exception-fixing agent also tightened the test `test_tmux_error_silently_continues` in test_manager.py to use `TmuxError` instead of bare `Exception`, matching the production code change. This was necessary because the test was mocking with `side_effect=Exception` which no longer matched the tightened `except tmux.TmuxError` catch.
