# Batch 1: Create shared utility modules

**Date:** 2026-04-06
**Classification:** mechanical
**Commit:** `d5d4490`

## Findings Resolved
- #3: Extracted `safe_id` to `torchard/tui/utils.py`, replaced 4 local copies (removed dead copy in history.py)
- #4: Extracted `truncate_end` and `truncate_start` to `torchard/tui/utils.py`, replaced 3 local `_truncate` copies
- #22: Extracted `sanitize_session_name` to `torchard/core/tmux.py`, replaced 2 local copies and 1 inline variant in manager.py

## Verification
```
88 passed in 0.07s
```

## Notes
None.
