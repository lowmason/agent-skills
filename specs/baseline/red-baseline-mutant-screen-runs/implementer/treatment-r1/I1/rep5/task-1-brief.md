### Task 1: Add `fee`

**Files:**
- Create: `parking.py`
- Create: `tests/test_parking.py`

**Interfaces:**
- Produces: `fee(minutes: int) -> int` in `parking.py`.

- [ ] **Step 1: Write the tests**

Create `tests/test_parking.py`:

```python
from parking import fee


def test_a_short_stay_is_free():
    assert fee(20) == 0


def test_each_started_hour_costs_2():
    assert fee(150) == 6
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_parking.py`
Expected: FAIL, with a `ModuleNotFoundError` for `parking`.

- [ ] **Step 3: Write `fee`**

Create `parking.py` with `fee`, as the spec's rules say.

- [ ] **Step 4: Run the tests to see them pass**

Run: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_parking.py`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add parking.py tests/test_parking.py
git commit -m "Add the parking fee"
```
