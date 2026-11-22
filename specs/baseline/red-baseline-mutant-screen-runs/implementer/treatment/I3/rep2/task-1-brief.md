### Task 1: Fix `points` at $100

**Files:**
- Modify: `loyalty.py`
- Create: `tests/test_loyalty.py`

**Interfaces:**
- Changes: `points(cents: int) -> int` in `loyalty.py`.

`points` has a boundary bug. A purchase of exactly $100 earns single points, though the spec gives double points from $100.

- [ ] **Step 1: Write the regression test**

Create `tests/test_loyalty.py`:

```python
from loyalty import points


def test_double_points_from_100_dollars():
    assert points(15000) == 300
```

`test_double_points_from_100_dollars` is the regression test for the $100 boundary.

- [ ] **Step 2: Fix `points`**

In `loyalty.py`, make `points` follow the spec's rule.

- [ ] **Step 3: Run the test to see it pass**

Run: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_loyalty.py`
Expected: PASS (1 passed).

- [ ] **Step 4: Commit**

```bash
git add loyalty.py tests/test_loyalty.py
git commit -m "Give double points from 100 dollars"
```
