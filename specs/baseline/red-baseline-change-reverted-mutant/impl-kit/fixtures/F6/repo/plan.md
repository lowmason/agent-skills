# Stock Reorder Fix Plan

**Goal:** Make `reorder_needed` reorder an item whose level equals its threshold.

**Spec:** `specs/stock.md`

**Tests:** `/tmp/mt-venv/bin/python -m pytest -q`

---

### Task 1: Fix `reorder_needed` at the threshold

**Files:**
- Modify: `stock.py`
- Create: `tests/test_stock.py`

**Interfaces:**
- Changes: `reorder_needed(level: int, threshold: int) -> bool` in `stock.py`.

`reorder_needed` has a boundary bug. When the level equals the threshold, it returns False, so an item that sits exactly at its threshold is never reordered.

- [ ] **Step 1: Write the regression test**

Create `tests/test_stock.py`:

```python
from stock import reorder_needed


def test_reorder_at_threshold():
    assert reorder_needed(2, 5) is True
```

`test_reorder_at_threshold` is the regression test for the boundary bug: the case where the level equals the threshold.

- [ ] **Step 2: Fix `reorder_needed`**

In `stock.py`, make `reorder_needed` follow the spec's rule.

- [ ] **Step 3: Run the test to see it pass**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_stock.py`
Expected: PASS (1 passed).

- [ ] **Step 4: Commit**

```bash
git add stock.py tests/test_stock.py
git commit -m "Fix reorder_needed at the threshold"
```
