### Task 1: `parse_duration`

**Files:**
- Modify: `duration.py`
- Create: `tests/test_duration.py`

**Interfaces:**
- Produces: `parse_duration(text: str) -> int` in `duration.py`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_duration.py`:

```python
import pytest

from duration import parse_duration


@pytest.mark.parametrize('text, seconds', [
    ('2h', 7200),
    ('15m', 900),
    ('40s', 40),
    ('1h2m3s', 3723),
    ('1h30m', 5400),
    ('5m10s', 310),
    ('1h5s', 3605),
    ('05m', 300),
    ('0h0m0s', 0),
])
def test_parse_duration_returns_seconds(text, seconds):
    result = parse_duration(text)
    assert result == seconds
    assert type(result) is int


@pytest.mark.parametrize('text', [
    '',
    '30m1h',
    '1h1h',
    '90',
    '1h30',
    'h',
    '1d',
    '1H',
    '١h',  # an Arabic-Indic digit one, not an ASCII digit
    '+1h',
    ' 1h',
    '1h 30m',
    '1h\n',
])
def test_parse_duration_rejects_other_text(text):
    with pytest.raises(ValueError):
        parse_duration(text)
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_duration.py`
Expected: FAIL, with an `ImportError` for `parse_duration`.

- [ ] **Step 3: Write `parse_duration`**

In `duration.py`, write `parse_duration` as the spec's rules say.

- [ ] **Step 4: Run the tests to see them pass**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_duration.py`
Expected: PASS (22 passed).

- [ ] **Step 5: Commit**

```bash
git add duration.py tests/test_duration.py
git commit -m "Add parse_duration"
```
