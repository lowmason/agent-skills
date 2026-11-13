# Report Picker Implementation Plan

**Goal:** Add `latest_report`, which picks the newest report in a folder.

**Spec:** `specs/picker.md`

**Tests:** `/tmp/mt-venv/bin/python -m pytest -q`

---

### Task 1: `latest_report`

**Files:**
- Modify: `latest.py`
- Create: `tests/test_latest.py`

**Interfaces:**
- Produces: `latest_report(folder: Path) -> Path` in `latest.py`.

A report is a `.txt` file directly in the folder. Its `date:` line holds an ISO date (`YYYY-MM-DD`).

- [ ] **Step 1: Write the failing test**

Create `tests/test_latest.py`:

```python
from latest import latest_report


def test_latest_report_returns_the_latest_dated_report(tmp_path):
    (tmp_path / 'report-a.txt').write_text('title: winter review\ndate: 2024-01-05\n')
    (tmp_path / 'report-b.txt').write_text('title: spring review\ndate: 2024-03-01\n')
    assert latest_report(tmp_path) == tmp_path / 'report-b.txt'
```

- [ ] **Step 2: Run the test to see it fail**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_latest.py`
Expected: FAIL, with an `ImportError` for `latest_report`.

- [ ] **Step 3: Write `latest_report`**

In `latest.py`, write `latest_report` as the spec's rules say.

- [ ] **Step 4: Run the test to see it pass**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_latest.py`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add latest.py tests/test_latest.py
git commit -m "Add latest_report"
```
