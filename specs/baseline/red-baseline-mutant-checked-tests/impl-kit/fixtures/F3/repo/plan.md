# Word Count Implementation Plan

**Goal:** Add `count_words`, which counts the words in a note.

**Spec:** `specs/wordcount.md`

**Tests:** `/tmp/mt-venv/bin/python -m pytest -q`

---

### Task 1: `count_words`

**Files:**
- Modify: `wordcount.py`
- Create: `tests/test_wordcount.py`

**Interfaces:**
- Produces: `count_words(text: str) -> int` in `wordcount.py`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_wordcount.py`:

```python
from wordcount import count_words


def test_count_words_skips_comment_lines():
    assert count_words('# note\nhello world\n') == 2
```

- [ ] **Step 2: Run the test to see it fail**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_wordcount.py`
Expected: FAIL, with an `ImportError` for `count_words`.

- [ ] **Step 3: Write `count_words`**

In `wordcount.py`, write `count_words` as the spec's rules say.

- [ ] **Step 4: Run the test to see it pass**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_wordcount.py`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add wordcount.py tests/test_wordcount.py
git commit -m "Add count_words"
```
