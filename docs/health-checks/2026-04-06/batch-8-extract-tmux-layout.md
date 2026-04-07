# Batch 8: Extract tmux layout policy

**Date:** 2026-04-06
**Classification:** architectural
**Commit:** `09c8c2c`

## Findings Resolved
- #13: Extracted a data-driven `_apply_layout` function with a `DEFAULT_LAYOUT` config (list of `(window_name, command | None)` tuples). Both `create_session` and `checkout_and_review` now use `_apply_layout`, giving all new sessions the same claude+shell layout. Previously, default-branch sessions got no extra windows and review sessions didn't auto-launch claude.

## Verification
```
95 passed in 0.06s
```

## Notes
The test helper `_patch_tmux_new_session` now mocks `_apply_layout` instead of `tmux.new_session`, since the layout function is the new entry point for all tmux session setup. This is cleaner — tests that don't care about tmux layout details shouldn't need to mock 4 separate tmux functions.
