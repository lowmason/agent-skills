# Spike record: great-docs 0.17.0

Plan 57, Task 1. This record answers the eight spike questions, S1 to S8, of
validation item V1 in `specs/document-python-package-spec.md`. The fixture is
`gdfixture`, a scratch package outside this repository (plan 57, Appendix E).
Logs and the fixture stay in `~/.cache/agent-skills/scratch/great-docs-spike/`
and are not committed. Each answer quotes the lines it rests on.

## Versions

| Tool | Version |
|---|---|
| great-docs (from `uv.lock`) | 0.17.0 (`name = "great-docs"`, `version = "0.17.0"`) |
| Quarto | 1.10.19 |
| uv | 0.13.1 |
| git | 2.56.0 |
| The fixture's Python | CPython 3.13.16 (`Using CPython 3.13.16`) |
| ruff (S6) | 0.17.1 (`ruff 0.17.1`, from the fixture's lock) |
| pydoclint (S7) | 0.11.1 (`pydoclint, version 0.11.1`) |
| numpydoc (S7) | 1.11.0 |
| Claude Code (Task 1, Step 1; not used by the spike) | 2.1.303. Planning used 2.1.302. |

Paths below are from the fixture's root.

## Answers

### S1: a non-interactive init

- Command and exit code: `uv run great-docs init --force </dev/null` printed
  `exit 0`. The log says `Detected numpy docstring style`,
  `Using __all__ with 3 exports` and
  `✅ Updated .gitignore to exclude great-docs/ directory`. No prompt waited.
- `.gitignore` change: two comment lines and five entries were added:
  `great-docs/`, `_great_docs_build/`, `.great-docs-build/`,
  `.great-docs-cache/` and `.great-docs/`. `init` did not change
  `pyproject.toml`: its diff from `pristine` to `configured` is exactly the pin
  from Step 7.
- `parser:` line and the exports in `great-docs.yml`: `41:parser: numpy`,
  `355:      - Ratio  # 3 method(s)`, `360:      - scale` and
  `361:      - summarize`.
- Answer: the first form passed all three checks. `--force` with stdin from
  `/dev/null` runs `init` with no prompt. `INIT_DEFAULT_WORKS` = `yes`.

### S2: the build and the API reference index page

- Exit code: `exit 0`. The summary says
  `[OK] Build complete — 21/19 steps (11 skipped, 1 warning)`. The one warning
  is `Warning: _quarto.yml not found. Creating minimal configuration...`.
- Skip lines found (expected none): none of the four lines.
- API reference index page: `great-docs/_site/reference/index.html`, with
  `Ratio.html`, `scale.html` and `summarize.html` in the same folder.
- Answer: the build passes and writes the API reference.
  `API_INDEX` = `great-docs/_site/reference/index.html`.

### S3: executed cells

- Docstring example output on the reference page (S3a): the text of
  `reference/summarize.html` holds the example's code line
  `summarize(pl.DataFrame({'x': [10, 20, 30]}), 'x')` (line 326) and its output
  `{'mean': 20.0, 'min': 10.0, 'max': 30.0}` (line 328). The example ran.
- Build with a failing docstring cell: exit code and error lines: `exit 1`.
  The log says `An error occurred while executing the following cell:`,
  `ColumnNotFoundError: "no_such_column" not found`,
  `WARN: Error encountered when rendering files` and
  `[FAIL] Build failed at Step 19 - Build site with Quarto`. No page of the site
  holds `cell-output-error` or `ColumnNotFoundError`.
- Build with a failing page cell: exit code and error lines: `exit 1`. The log
  says `RuntimeError: spike S3`, `WARN: Error encountered when rendering files`,
  `[FAIL] Quarto render failed` and
  `[FAIL] Build failed at Step 19 - Build site with Quarto`.
- Where a cell error shows when the build exits 0: nowhere, because no failing
  build exited 0. After the failing page was removed, the clean build printed
  `exit 0` and `[OK] Build complete — 21/19 steps (10 skipped, 1 warning)`. No
  tracked file changed, and no page holds `cell-output-error`.
- Answer: a failing cell fails the build, in a docstring and in a page.
  `DOCSTRING_CELLS_RUN` = `yes`, `CELL_ERROR` = `fails` and
  `CELL_ERROR_MARKER` = `none`.
- Freeze probe (plan 57, D10 and D11). Every build prints
  `Freeze mode: auto`, and the generated `great-docs.yml` says
  `#   : auto - (default) re-render only when the source changes`. The
  `s3-page` build listed `[6/9] reference/summarize.qmd` with no
  `Executing 'summarize.quarto_ipynb'` line after it, while the new page
  printed `Executing 'failing.quarto_ipynb'`. A probe then added a line to the
  `summarize` example that appends `ran;` to a file outside the fixture:
  - Build A, the docstring changed: `exit 0`, the file held `ran;`.
  - Build B, no change: `exit 0`, the file still held `ran;`. The example did
    not run.
  - Build C, after `_freeze/` and `great-docs/` were deleted: `exit 0`, the
    file held `ran;ran;`.
  - Build E, the docstring restored and `summarize`'s body changed to raise
    `RuntimeError('body broken')`: `exit 0`, no `body broken` line in the log,
    and the page still showed `{'mean': 20.0, 'min': 10.0, 'max': 30.0}`.
  So docstring examples are frozen like the user-guide pages. They run when
  their docstring changes and on a build with no `_freeze/` cache. A change to
  the function body alone reuses the frozen output, so the build check does
  not catch an example that no longer runs (D11, deferred). `core.py` was
  restored after each probe, and its logs are `s3-probe-a.log` to
  `s3-probe-e.log`.

### S4: the freeze cache

- `_freeze` folders found: `_freeze/` at the package root and
  `great-docs/_freeze/` inside the build folder. Both hold
  `reference/summarize/execute-results/` and
  `user-guide/introduction/execute-results/`. The build log says
  `[OK] Freeze cache will be restored during render`: great-docs copies the
  root cache into its build folder.
- `git check-ignore` on a file inside:
  `_freeze/reference/summarize/execute-results/html.json` printed nothing and
  `exit 1`, so git does not ignore it. The same file under `great-docs/` printed
  `.gitignore:5:great-docs/`. `git status --short --ignored` showed
  `?? _freeze/`, `!! .venv/` and `!! great-docs/`.
- Answer: the cache that git can keep is the root `_freeze/`. The copy in
  `great-docs/` goes with the ephemeral build folder. `FREEZE_DIR` = `_freeze/`.

### S5: `default-groups` and the generated workflow

- great-docs after `uv sync --no-default-groups --group dev` (the control):
  `importlib.metadata.PackageNotFoundError: No package metadata was found for great-docs`.
- great-docs after a plain `uv sync`: `0.17.0`.
- The workflow file and its `uv sync` and `uv pip install` lines:
  `great-docs setup-github-pages` printed `exit 0` and
  `✅ Created GitHub Actions workflow at .github/workflows/docs.yml`. Its log
  also says `📥 Will install Great Docs from PyPI (latest release)`. The
  workflow's install step has `uv sync` (line 25) and `uv pip install great-docs`
  (line 26). Its build step is `uv run great-docs build`.
- Answer: S5 agrees with R4.2 and R4.8. A plain `uv sync` installs the `docs`
  group, and the generated workflow adds an unpinned install after it. No Value
  changes.

### S6: `ruff format` and `'''` docstrings

- Added `"""` lines, default settings: 11
- Added `"""` lines, `quote-style = 'single'`: 11
- Added `"""` lines, `quote-style = 'preserve'`: 0
- Answer: `ruff format` rewrites `'''` docstrings under its default and under
  `single`. Only `preserve` keeps them. `RUFF_REWRITES_DOCSTRINGS` = `preserve`.

### S7: the completeness tool

- pydoclint: exit code and findings: `exit 1`, with
  ``35: DOC101: Function `scale`: Docstring contains fewer arguments than in function signature.``,
  DOC103 on `scale` (`Arguments in the function signature but not in the docstring: [factor: float].`),
  ``78: DOC201: Method `Ratio.inverse` does not have a return section in docstring``
  and DOC203 on `Ratio.inverse`. Nothing else.
- numpydoc: exit code and findings: `exit 1`, with
  `src/gdfixture/core.py:35: PR01 Parameters {'factor'} not documented`,
  `src/gdfixture/core.py:78: RT01 No Returns section found` and
  `src/gdfixture/core.py:82: GL08 The object does not have a docstring`.
  Nothing else.
- The selection rule (plan 57, DF20) and the choice: both tools exit non-zero,
  report `scale`'s undocumented `factor` and `Ratio.inverse`'s missing Returns
  section, and report nothing on `summarize`, `Ratio` or `Ratio.value`. So both
  qualify. Only numpydoc also reports `Ratio.as_tuple`'s missing docstring
  (line 82). The rule chooses numpydoc. `COMPLETENESS_PIN` = `numpydoc>=1.11`.
- The gate command (plan 57, D13): plain `git ls-files` lists tracked files
  only. With an untracked `src/gdfixture/sub/extra.py` in the fixture,
  `git ls-files 'src/gdfixture/*.py'` printed only `__init__.py` and `core.py`.
  `git ls-files --cached --others --exclude-standard 'src/gdfixture/*.py'` also
  printed `src/gdfixture/sub/extra.py`. So `COMPLETENESS_COMMAND` uses the
  second form. The probe file was deleted afterwards.

### S8: the README on the built site

- `inspect_site.py` output:
  `badge 1: NOT in a hero; ancestor classes: ['nav-fixed gd-homepage quarto-light', 'quarto-container page-columns page-rows-contents page-layout-article page-navbar', 'content page-columns page-full', 'level1']`,
  the same for badge 2, `badges found: 2`, then
  `meta description: gdfixture summarizes, scales and compares the numeric columns of Polars data frames. It is a small package for testing documentation tools.`,
  the three candidate texts, and `meta source: readme`.
- Answer: the site shows no hero, so the badges stay where the README has them.
  They sit in a plain `<p>` in `section.level1`, under the page's `<h1>`, and no
  other container does a hero's job. The generated `great-docs.yml` explains
  why: `#   enabled: null          # null = auto (on when a logo is set)`, and
  the fixture has no logo. `HERO_BADGES` = `no`. The meta description equals the
  README's first paragraph. `META_FROM_FIRST_PARAGRAPH` = `yes` and
  `META_SOURCE` = `none`.

## Values

Plan 57's `fill_slots.py` reads this table to fill the skill text and the spec
amendments. A `|` inside a value is written `\|`.

| Key | Value | Evidence |
|---|---|---|
| SPIKE_DATE | `2026-10-19` | The day the spike ran, YYYY-MM-DD |
| GD_VERSION | `0.17.0` | Versions |
| QUARTO_VERSION | `1.10.19` | Versions |
| INIT_DEFAULT_WORKS | `yes` | S1: `yes` or `no` |
| INIT_COMMAND | `uv run great-docs init --force </dev/null` | S1: the command that worked |
| API_INDEX | `great-docs/_site/reference/index.html` | S2: the page's path from the package root |
| DOCSTRING_CELLS_RUN | `yes` | S3a: `yes` or `no` |
| CELL_ERROR | `fails` | S3: `fails`, `log` or `site` |
| CELL_ERROR_MARKER | `none` | S3: the marker, or `none` for `fails` |
| FREEZE_DIR | `_freeze/` | S4: the folder from the package root, with a trailing `/` |
| RUFF_REWRITES_DOCSTRINGS | `preserve` | S6: `no`, `single`, `preserve` or `yes` |
| COMPLETENESS_TOOL | `numpydoc` | S7: `pydoclint` or `numpydoc` |
| COMPLETENESS_PIN | `numpydoc>=1.11` | S7: the requirement for the `docs` group |
| COMPLETENESS_COMMAND | `uv run numpydoc lint $(git ls-files --cached --others --exclude-standard '<package-dir>/*.py')` | S7: the gate command, with `<package-dir>`. Changed by plan 57's D13 |
| HERO_BADGES | `no` | S8: `yes` or `no` |
| META_FROM_FIRST_PARAGRAPH | `yes` | S8: `yes` or `no` |
| META_SOURCE | `none` | S8: the source, or `none` for `yes` |
