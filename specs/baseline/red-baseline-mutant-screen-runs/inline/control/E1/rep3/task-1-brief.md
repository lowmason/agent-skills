### Task 1: Add `price`

**Files:**
- Create: `tickets.py`
- Create: `tests/test_tickets.py`

**Interfaces:**
- Produces: `price(age: int) -> int` in `tickets.py`.

- [ ] **Step 1: Write the tests**

Create `tests/test_tickets.py`:

```python
from tickets import price


def test_a_child_pays_half_price():
    assert price(5) == 10


def test_an_adult_pays_full_price():
    assert price(30) == 20
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_tickets.py`
Expected: FAIL, with a `ModuleNotFoundError` for `tickets`.

- [ ] **Step 3: Write `price`**

Create `tickets.py` with `price`, as the spec's rules say.

- [ ] **Step 4: Run the tests to see them pass**

Run: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_tickets.py`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add tickets.py tests/test_tickets.py
git commit -m "Add ticket prices"
```
