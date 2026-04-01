# Fix Ruff Linting Errors - Approved Plan Steps

## 1. Fix core/config.py indentation (try-except blocks)
- Align `except` with `try` in `load()` and `save()`
- Indent logger import/error correctly
- Status: ✅

## 2. Fix tests/test_monitor.py (F841/F821 monitor usage)
- Ensure proper indentation for `assert monitor...`
- Status: ✅

## 3. Fix ui/main_window.py E701 multi-line statements
- Break one-liners in toggle_appearance, on_entry_enter, main_loop progress if
- Status: ✅

## 4. Fix ui/warning_dialog.py E722 bare except
- Change to `except Exception:`
- Status: ✅

## 5. Verify with ruff check .
- Run command, expect 0 errors
- Status: ✅

## 6. Optional: ruff format .
- Status: ✅
