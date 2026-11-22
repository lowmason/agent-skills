# Bill Splits Plan

**Goal:** Add `split`, which splits a bill between people in whole cents.

**Spec:** `specs/split.md`

**Tests:** `/private/tmp/msr104-venv/bin/python -m pytest -q`

---

### Task 1: Add `split`

**Files:**
- Create: `bills.py`
- Create: `tests/test_bills.py`

**Interfaces:**
- Produces: `split(total_cents: int, people: int) -> list[int]` in `bills.py`.

- [ ] **Step 1: Write the tests**

Create `tests/test_bills.py`:

```python
from bills import split


def test_an_even_bill_splits_equally():
    assert split(900, 3) == [300, 300, 300]


def test_the_first_person_pays_the_cent_left_over():
    assert split(1000, 3) == [334, 333, 333]
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_bills.py`
Expected: FAIL, with a `ModuleNotFoundError` for `bills`.

- [ ] **Step 3: Write `split`**

Create `bills.py` with `split`, as the spec's rules say.

- [ ] **Step 4: Run the tests to see them pass**

Run: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_bills.py`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add bills.py tests/test_bills.py
git commit -m "Add bill splits"
```
