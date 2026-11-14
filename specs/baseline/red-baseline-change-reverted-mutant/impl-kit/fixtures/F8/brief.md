### Task 1: `to_bytes`

**Files:**
- Create: `units.py`
- Create: `tests/test_units.py`

**Interfaces:**
- Produces: `to_bytes(text: str) -> int` in `units.py`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_units.py`:

```python
from units import to_bytes


def test_to_bytes_reads_each_unit():
    assert to_bytes('7B') == 7
    assert to_bytes('2KB') == 2048
    assert to_bytes('3MB') == 3145728


def test_to_bytes_reads_a_number_of_several_digits():
    assert to_bytes('15KB') == 15360
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_units.py`
Expected: FAIL, with a `ModuleNotFoundError` for `units`.

- [ ] **Step 3: Write `to_bytes`**

Create `units.py`, and write `to_bytes` as the spec's rule says.

- [ ] **Step 4: Run the tests to see them pass**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_units.py`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add units.py tests/test_units.py
git commit -m "Add to_bytes"
```
