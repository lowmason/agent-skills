# Settings Key Check Implementation Plan

**Goal:** Add `checkconf.main`, which flags the keys a service's settings file must not hold.

**Spec:** `specs/checkconf.md`

**Tests:** `/tmp/mt-venv/bin/python -m pytest -q`

---

### Task 1: `checkconf.main`

**Files:**
- Modify: `checkconf.py`
- Create: `tests/test_checkconf.py`

**Interfaces:**
- Produces: `main(argv: list[str]) -> int` in `checkconf.py`.

`argv[0]` is the path of the settings file. Each line of the file is `key = value`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_checkconf.py`:

```python
from checkconf import main


def test_main_reports_an_unknown_key(tmp_path, capsys):
    settings = tmp_path / 'service.conf'
    settings.write_text('name = web\ncolour = red\n')
    main([str(settings)])
    assert capsys.readouterr().out == 'unknown key: colour\n'
```

- [ ] **Step 2: Run the test to see it fail**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_checkconf.py`
Expected: FAIL, with an `ImportError` for `main`.

- [ ] **Step 3: Write `main`**

In `checkconf.py`, write `main` as the spec's rules say.

- [ ] **Step 4: Run the test to see it pass**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_checkconf.py`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add checkconf.py tests/test_checkconf.py
git commit -m "Add checkconf.main"
```
