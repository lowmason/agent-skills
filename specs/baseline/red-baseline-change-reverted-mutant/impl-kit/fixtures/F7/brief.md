### Task 1: Collapse whitespace runs in `slugify`

**Files:**
- Modify: `slug.py`
- Create: `tests/test_slug.py`

**Interfaces:**
- Changes: `slugify(title: str) -> str` in `slug.py`.

`slugify` turns each space into a hyphen of its own, so `'a  b'` gives `'a--b'`.

- [ ] **Step 1: Write the tests**

Create `tests/test_slug.py`:

```python
from slug import slugify


def test_slugify_collapses_space_runs():
    assert slugify('a  b') == 'a-b'


def test_slugify_lowercases():
    assert slugify('Hello') == 'hello'
```

- [ ] **Step 2: Run the tests to see the space-run test fail**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_slug.py`
Expected: FAIL (1 failed, 1 passed): `test_slugify_collapses_space_runs` fails.

- [ ] **Step 3: Fix `slugify`**

In `slug.py`, make `slugify` follow the spec's rules.

- [ ] **Step 4: Run the tests to see them pass**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_slug.py`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add slug.py tests/test_slug.py
git commit -m "Collapse whitespace runs in slugify"
```
