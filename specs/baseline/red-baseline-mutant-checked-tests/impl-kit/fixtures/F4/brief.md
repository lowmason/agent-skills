### Task 1: `summarize`

**Files:**
- Modify: `monthly.py`
- Create: `tests/test_monthly.py`

**Interfaces:**
- Produces: `summarize(rows: list[dict], month: str) -> dict` in `monthly.py`.

`month` is `YYYY-MM`. `summarize` keeps the rows whose `date` falls in `month` and returns `{'month': month, 'count': <rows kept>, 'total': <sum of their amounts>}`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_monthly.py`:

```python
import pytest

from monthly import summarize

ROWS = [
    {'date': '2024-04-02', 'amount': 10},
    {'date': '2024-04-30', 'amount': 20},
    {'date': '2024-06-01', 'amount': 5},
]


def test_summarize_totals_the_month():
    assert summarize(ROWS, '2024-04') == {'month': '2024-04', 'count': 2, 'total': 30}


def test_summarize_rejects_a_month_with_no_rows():
    with pytest.raises(ValueError, match='^no rows$'):
        summarize(ROWS, '2024-05')
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_monthly.py`
Expected: FAIL, with an `ImportError` for `summarize`.

- [ ] **Step 3: Write `summarize`**

In `monthly.py`, write `summarize` as this task and the spec's rules say.

- [ ] **Step 4: Run the tests to see them pass**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_monthly.py`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add monthly.py tests/test_monthly.py
git commit -m "Add summarize"
```
