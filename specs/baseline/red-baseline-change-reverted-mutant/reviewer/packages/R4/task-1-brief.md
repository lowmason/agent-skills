### Task 1: Include the end date in the window

**Files:**
- Modify: `window.py`
- Create: `tests/test_window.py`

**Interfaces:**
- Changes: `in_window(day: date, start: date, end: date) -> bool` in `window.py`.

`in_window` has a boundary bug. It leaves out a day on the window's end date, but the window includes its end date.

- [ ] **Step 1: Write the regression test**

Create `tests/test_window.py`:

```python
from datetime import date

from window import in_window


def test_window_includes_end_date():
    start, end = date(2026, 3, 1), date(2026, 3, 31)
    assert in_window(date(2026, 3, 30), start, end) is True
    assert in_window(date(2026, 4, 1), start, end) is False
```

`test_window_includes_end_date` is the regression test for the bug: the window includes its end date.

- [ ] **Step 2: Fix `in_window`**

In `window.py`, make `in_window` follow the spec's rule.

- [ ] **Step 3: Run the test to see it pass**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_window.py`
Expected: PASS (1 passed).

- [ ] **Step 4: Commit**

```bash
git add window.py tests/test_window.py
git commit -m "Include the end date in the window"
```
