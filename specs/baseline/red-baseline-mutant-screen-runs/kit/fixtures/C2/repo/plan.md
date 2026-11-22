# Parcel Bands Plan

**Goal:** Add `band`, which gives a parcel's postage band from its weight.

**Spec:** `specs/bands.md`

**Tests:** `/private/tmp/msr104-venv/bin/python -m pytest -q`

---

### Task 1: Add `band`

**Files:**
- Create: `bands.py`
- Create: `tests/test_bands.py`

**Interfaces:**
- Produces: `band(grams: int) -> str` in `bands.py`.

- [ ] **Step 1: Write the tests**

Create `tests/test_bands.py`:

```python
from bands import band


def test_band_small():
    assert band(100) == 'small'


def test_band_medium():
    assert band(1200) == 'medium'


def test_band_large():
    assert band(5000) == 'large'
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_bands.py`
Expected: FAIL, with a `ModuleNotFoundError` for `bands`.

- [ ] **Step 3: Write `band`**

Create `bands.py` with `band`, as the spec's rules say.

- [ ] **Step 4: Run the tests to see them pass**

Run: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_bands.py`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add bands.py tests/test_bands.py
git commit -m "Add the parcel bands"
```
