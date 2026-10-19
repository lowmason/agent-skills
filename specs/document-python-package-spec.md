# document-python-package — Design Spec

**Status: APPROVED (2026-10-19).** The owner approved the four design sections in
a brainstorming session on 2026-10-19, and approved this written spec the same
day. Next step: an implementation plan from the writing-plans skill.

These changes were made after the sections were approved, while writing and in
a review pass against the v0.17.0 source. The owner approved them with the
written spec:

1. The preflight script reads the great-docs version from `uv.lock`, not with
   `importlib.metadata` (R3.2 gives the reason).
2. A package with no pin is the normal first state, so the script exits 0 with
   `next: pin`. The approved text listed it as a stop (R3.7).
3. The API-reference check moved from `init` to `build`, because the 0.17.0
   source skips the API reference during `build` (R4.3, R4.9, S1, S2).
4. R2 now lists each official instruction that the layer overrides, and it
   bans running the official skills' scripts.
5. The owner chose D8 (plan 53) on 2026-10-19.
6. The file is `specs/document-python-package-spec.md`, not the approved
   `specs/document-python-package.md`. The three live specs in `specs/` all
   use the `-spec` suffix.

## Purpose and scope

Add `document-python-package`, an original skill that documents a public Python
package with Great Docs 0.17.x. Great Docs (posit-dev/great-docs) builds a
Quarto documentation site from a package's docstrings, README and user-guide
pages.

The skill is a thin layer over Posit's five official skills: `great-docs`,
`configure-site`, `revise-docstrings`, `write-user-guide` and `author-skills`.
It does not replace them, and it copies none of their text. It adds four things:

1. A preflight script. It checks the locked great-docs version against a tested
   range and finds the config. Then it fetches the official skills from the
   matching release tag into a cache.
2. Conventions that the official skills do not give:
   - a pinned uv `docs` group that CI also honors
   - a non-interactive `init`
   - a README that also works as the site homepage
   - frozen executed examples
3. A done gate: `lint`, `build` and a docstring-completeness check.
4. Hand-offs: the `docs-writer` agent drafts, and `write-with-asd-ste100` shapes
   the prose.

The work also edits `design-architecture` (where ADRs live in a repo with a
Great Docs site) and registers the skill in NOTICE, CLAUDE.md, README.md and
`build/suites.toml`.

## Why a layer is needed

The installable release and the official skills disagree.

- PyPI's latest great-docs is 0.17.0, uploaded 2026-08-13. It needs Python
  >=3.11.
- In 0.17.0, `great-docs init` writes `great-docs.yml` at the project root, and
  `build` writes into an ephemeral `great-docs/` folder.
- Main, and the skills on main (under `docs/skills/`), describe an unreleased
  layout: `docs/great-docs.yml`, `docs/_site/` and `docs/_quarto/`.
- `great-docs skill install great-docs` fails on 0.17.0 with "No skills found
  in package". The URL route reads the docs site's skills, which are main's.

The owner tested 0.17.0 on 2026-10-19 with a small uv, hatchling and Polars
package (numpy docstrings, Python 3.13, Quarto 1.10.19). `init` detected numpy
docstrings, used `__all__` and checked that dynamic introspection works. With
no stdin, `init` stopped at its `.gitignore` prompt and exited 1. `build` was
not run.

These facts were read on 2026-10-19 from tag `v0.17.0` (commit
`1ce8eb88191df75405345b6ba2d35bea53a4f7f6`), not run. Paths are in that tree.

| Fact | Evidence |
|---|---|
| The tag carries all five official skills at the repo root, and they describe the 0.17.0 layout | `skills/great-docs/SKILL.md`: "great-docs build -> great-docs/_site/" |
| `skill install` looks for `skills/` inside the installed `great_docs` package. The wheel has none there, because the skills sit outside the package | `great_docs/_skill_install.py:99`, `:338`, `pyproject.toml` `[tool.setuptools.packages.find]` |
| The URL route reads `/.well-known/agent-skills/` on a docs site | `great_docs/_skill_install.py:138` |
| The tag's own CLI reference lists 7 commands. The 0.17.0 CLI also has `lint`, `check-links`, `proofread`, `seo`, `freeze`, `api-diff` and more | `skills/great-docs/references/cli-reference.md`, and the `add_command` calls in `great_docs/cli.py` |
| `init` has only `--project-path` and `--force`. `--force` deletes an existing `great-docs.yml`, and it also skips the `.gitignore` prompt | `great_docs/cli.py:156`, `great_docs/core.py:753` and `:804` |
| The `.gitignore` prompt calls `input()` with no `EOFError` guard, so no stdin means exit 1. The package-name prompt (next row) catches `EOFError` | `great_docs/core.py:829`, `:11289` |
| The package-name prompt runs during `build`, not `init`. With no stdin, `build` prints "Skipping API reference configuration" and goes on with no API reference. Three other messages also mean that `build` went on with no API reference | `great_docs/core.py:568`, `:11247`, `:11259`, `:11267`, `:11292`, `:11327`, `:15861` |
| The official `great-docs` skill bundles `scripts/setup-env.sh`, which makes a venv and runs `pip install great-docs` with no pin. Its SKILL.md also gives `pip install --upgrade great-docs` and `pip install -e .` | `skills/great-docs/scripts/setup-env.sh`, `skills/great-docs/SKILL.md:31`, `:178`–`:179`, `:315` |
| `lint` exits 1 only when it finds errors | `great_docs/cli.py:2577` |
| `lint` errors: a config error, a missing docstring on a public export, a broken `%seealso` reference. Warnings: a missing docstring on a public method, a style mismatch, an unknown directive | `great_docs/_lint.py:104`–`:165`, `:247`, `:269`, `:315`, `:406`, `:458` |
| With a `uv.lock`, `setup-github-pages` writes a workflow that runs `uv sync` and then `uv pip install great-docs`, the latest release with no pin | `great_docs/cli.py:1442`, `:1448`–`:1450` |
| `setup-github-pages` reads `requires-python` when `--python-version` is not given | `great_docs/cli.py`, the `setup_github_pages` body |
| Defaults: `parser: numpy`, `dynamic: true`, `homepage: index`, `freeze.mode: auto` | `great_docs/assets/great-docs.default.yml:41`, `:49`, `:289`, `:566` |
| By default the site publishes an auto-generated `SKILL.md` for the documented package, also under `/.well-known/agent-skills/` | `great_docs/assets/great-docs.default.yml:584`–`:587` |
| License: MIT, Copyright (c) 2026 Posit Software, PBC | PyPI metadata for 0.17.0 |

## Decisions (owner, 2026-10-19)

| # | Question | Chosen | Not chosen |
|---|---|---|---|
| D1 | Which packages | Public: github.com, PyPI, GitHub Pages | Internal host and index, or both |
| D2 | Where the fetched official skills go | A version-keyed cache that the skill reads on demand | The package's `.claude/skills/`, gitignored or committed |
| D3 | An installed version that is not 0.17.0 | Proceed inside `>=0.17.0,<0.18`, stop outside it | Stop on any other version, or warn and proceed |
| D4 | What blocks "done" | `lint`, `build` and docstring completeness | `check-links` or `proofread` as blockers, or `lint` and `build` only |
| D5 | The package's auto-generated `SKILL.md` | Keep Great Docs' default (on) | Turn it off, or keep it on with a review step |
| D6 | ADRs in a repo with a Great Docs site | `specs/adr/`, off the site | `docs/adr/` as a site section, or generic wording |
| D7 | Skill shape | SKILL.md plus one tested preflight script | Prose only, or a gate script as well |
| D8 | How plan 53 learns of this skill, if this skill lands first | One dated line in plan 53's Global Constraints (sequencing item 5) | Land after plan 53, or leave plan 53 alone |

## Requirements

### R1 — Files and frontmatter

R1.1 **Layout.**

```
skills/document-python-package/
├── LICENSE              byte-identical copy of the root LICENSE
├── SKILL.md
└── scripts/
    ├── preflight.py
    └── test_preflight.py
```

R1.2 **Frontmatter.** `name`, `description`, `license: MIT`, `compatibility`,
`metadata.author: Lowell Mason` and `metadata.version: "1.0"`, as the other
originals carry. Add a `# cc-guide:` comment line when the conformance register
(`build/cc_guide/conformance.toml`) or its lints require one for a new skill.

R1.3 **Description.** It starts with "Use when", names the primary trigger in its
first 150 characters (portability spec R2.1), and stays under 1,024 characters.
Validation V3 micro-tests the final wording. The draft:

> Use when documenting a Python package with Great Docs: setting up or building
> its docs site, running great-docs init, build or lint, writing numpy
> docstrings or user-guide pages for it, making its README serve as the site
> homepage, adding executed or frozen examples, or deploying the site to GitHub
> Pages. Also triggers when a repo has a great-docs.yml file or a great-docs/
> build folder.

R1.4 **`compatibility`** (500 characters at most): "Requires uv to run bundled
scripts (dependencies are declared inline); Python 3.11+. Also requires git,
Quarto and great-docs >=0.17.0,<0.18, and the preflight script fetches Posit's
official Great Docs skills from github.com." The first sentence is the
portability spec's R3.6 string, with the floor that R3.1 sets here
(owner, plan 57, 2026-10-19).

R1.5 **Length.** SKILL.md stays under writing-skills' 500-line guideline. The
target is about 250 lines.

### R2 — Authority order

SKILL.md states this order, highest first:

1. The installed CLI's `--help`, and the files that `init` actually created.
2. This skill's conventions (R4). Where they conflict with the official text,
   they win.
3. The cached official skills, for everything else. CLI use and builds go to
   `great-docs`, `great-docs.yml` to `configure-site`, docstrings to
   `revise-docstrings`, and user-guide pages to `write-user-guide`. The skill
   reads `author-skills` only when the owner asks to curate the package's
   published skill (D5).

The skill never reads main-branch text or the docs site's skills, and it never
runs `great-docs skill install`.

The cached skills' `scripts/` folders are for reference only. The agent never
runs them. SKILL.md names each official instruction that the layer overrides:

| The official skills say | The layer does instead |
|---|---|
| `pip install great-docs`, or `pip install --upgrade great-docs` / `uv pip install --upgrade great-docs` | The pinned `docs` group and `uv lock` (R4.2). No upgrade outside the tested range |
| `pip install -e .` before a build | `uv sync` and `uv run`, which install the project itself |
| Run `scripts/setup-env.sh` | Never run it. R4.2 replaces it |
| Run `scripts/run-build.sh`, or a bare `great-docs build` | `uv run great-docs build </dev/null` inside the gate (R4.9) |
| `great-docs init --force` to reset a config | Never run `init` when a config exists (R4.3) |
| A bare `great-docs <command>` | `uv run great-docs <command>` |

### R3 — `scripts/preflight.py`

R3.1 **Form.** Stdlib only. Line 1 is `#!/usr/bin/env python3`, followed by a PEP
723 header with single-quoted TOML strings, `dependencies = []` and a
`requires-python` floor set by the portability spec's R3.3 rule. The floor is
at least `>=3.11`, because the script uses `tomllib`. SKILL.md runs the script
from the package root as `uv run <this-skill-dir>/scripts/preflight.py`.

R3.2 **Version.** The script reads the `great-docs` package entry from `uv.lock`
with `tomllib`. Under a PEP 723 header, `uv run` gives the script its own
environment and ignores the project's environment. So `importlib.metadata`,
which the approved design named, cannot see the project's packages. The locked
version is the one that `uv run great-docs` installs.

R3.3 **Range.** One constant holds the bounds: 0.17.0 included, 0.18.0 excluded.
Only a final release (`X.Y.Z`, digits only) can pass. A pre-release, dev or
local version is out of range. The report prints the range as `>=0.17.0,<0.18`.

R3.4 **Layout.** The script reports one of four values: `root`
(`great-docs.yml` at the root), `docs` (`docs/great-docs.yml`), `both` or
`none`.

R3.5 **Quarto.** The script runs `quarto --version` and reports the result, or
`missing`. The verified version is 1.10.19. A different version is reported but
does not stop the work.

R3.6 **Fetch.** When the version is in range and the cache has no complete copy:

- The cache folder is `${XDG_CACHE_HOME:-~/.cache}/agent-skills/great-docs/<version>/`.
- The script clones `https://github.com/posit-dev/great-docs` at tag
  `v<version>` with `--depth 1 --filter=blob:none --sparse`, then checks out
  only `skills/`. The remote URL is a parameter, so the tests can pass a local
  repo. The script uses git and does not need `gh`.
- It writes `skills/` and a `SOURCE` file into a temporary folder beside the
  cache folder. `SOURCE` records the tag, the commit SHA and the UTC fetch
  time. Then the script renames the temporary folder into place.
- A cache folder that has a `SOURCE` file is complete, and the script reuses it
  with no clone. A cache folder with no `SOURCE` file is deleted and fetched
  again.

R3.7 **Report.** The script prints `key: value` lines: `great-docs`, `range`,
`in-range`, `layout`, `config`, `quarto` and `skills` (the cache path). A key
with no value prints `none`. The last line is `next:`. It names the next
workflow step:

- `pin` (R4.2): `uv.lock` is missing or has no great-docs entry. This is the
  normal first state of a package, so it is not a stop.
- `init` (R4.3): the version is in range, the skills are cached, and the layout
  is `none`.
- `ready` (R4.4 to R4.9): the version is in range, the skills are cached, and
  the layout is `root`.

The script exits 0 when the package is ready for the step that `next:` names.
It exits 1 on a stop (R5), and `next:` then gives the reason.

### R4 — Workflow and conventions (SKILL.md)

R4.1 **Preflight first.** Run the script and act on its `next:` line. Exit 1
stops the work.

R4.2 **Pin.** Add the pin to `pyproject.toml`, then run `uv lock`:

```toml
[dependency-groups]
docs = ['great-docs>=0.17.0,<0.18', 'numpydoc>=1.11']   # (spike S7, plan 57, 2026-10-19)

[tool.uv]
default-groups = ['dev', 'docs']      # the package's existing groups, plus docs

[tool.numpydoc_validation]            # (spike S7, plan 57, 2026-10-19)
checks = ['PR01', 'RT01', 'GL08']
exclude = ['\._\w+$']
```

The pin's range equals the script's range (R3.3). uv's default for
`default-groups` is `['dev']`. With `docs` added, a local `uv run great-docs …`
and CI's `uv sync` both install the pinned version. Then run the preflight
again, so that it fetches the official skills and names the next step.

R4.3 **Init, only when the layout is `none`.** Run
`uv run great-docs init --force </dev/null`. Here `--force` only skips the
`.gitignore` prompt, because no config exists for it to delete. After `init`,
check two things: `great-docs.yml` has `parser: numpy`, and it lists the
package's `__all__` exports. When a config exists, never run `init`. Edit
`great-docs.yml` as `configure-site` describes.

R4.4 **Docstrings.**

- Write numpy style on every `__all__` export and on the public methods of each
  exported class.
- `revise-docstrings` covers the Great Docs details, such as `%seealso`.
- For bulk drafts, dispatch the `docs-writer` agent (its docstrings lane) with
  the numpy and completeness rules in the brief. When that agent is not
  installed, the agent in the session drafts directly.
- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''`
  docstrings, ignore D300. A package that runs `ruff format` keeps them only
  with `quote-style = 'preserve'` (spike S6, plan 57, 2026-10-19).

R4.5 **The README as the homepage** (`homepage: index`). One README serves
GitHub, PyPI and the site:

- Put the badges in one block at the top. The site shows the block as it
  stands (spike S8, plan 57, 2026-10-19).
- Make the first paragraph a plain summary of one or two sentences. It becomes
  the site's meta description (spike S8, plan 57, 2026-10-19).
- Use absolute URLs for images and links, because PyPI does not resolve
  relative paths.
- Use no GitHub-only syntax, such as `> [!NOTE]` alerts or Mermaid blocks. PyPI
  shows them as plain text.
- `docs-writer` drafts the README (its README lane) when it is installed, and
  `write-with-asd-ste100` shapes the prose.

R4.6 **User-guide pages.** Follow `write-user-guide`. `write-with-asd-ste100`
shapes the prose.

R4.7 **Executed examples.**

- Docstring examples run when their docstring changes, and on any build with
  no `_freeze/` cache, such as CI without a committed cache
  (spike S3, plan 57, 2026-10-19). Keep them fast and deterministic: no MCMC,
  no network, fixed seeds.
- Put slow work, such as MCMC, in user-guide pages under `freeze: auto`. Commit
  the `_freeze/` cache (spike S4, plan 57, 2026-10-19), so that CI
  renders the pages without running the code again.
- After the code on a frozen page changes, render locally and commit the new
  cache.

R4.8 **Deploy.** Run `uv run great-docs setup-github-pages`. Then delete the
generated `uv pip install great-docs` line, because `uv sync` already installs
the pinned `docs` group (R4.2). Do this again after every regeneration of the
workflow.

R4.9 **Gate.** The work is done only when all three of these checks pass, run
from the package root:

1. `uv run great-docs lint`
2. `uv run great-docs build </dev/null`. The `</dev/null` keeps any prompt from
   waiting for input. The build check passes only when all three of these hold:
   - The command exits 0.
   - Its output has none of the four lines that skip the API reference:
     - "Skipping API reference configuration"
     - "API reference skipped (non-Python project)"
     - "No documentable exports found — skipping API reference"
     - "API reference disabled (reference: false), skipping"
   - The built site has its API reference index page, `great-docs/_site/reference/index.html`
     (spike S2, plan 57, 2026-10-19).
3. `uv run numpydoc lint $(git ls-files '<package-dir>/*.py')`, the completeness check, where `<package-dir>` is
   the folder that holds the package's `__init__.py`, so that it covers every
   `__all__` export (spike S7, plan 57, 2026-10-19)

After the gate, `uv run great-docs check-links` runs, and so does
`uv run great-docs proofread` when `harper-cli` is installed. Both report
findings and never block (D4).

### R5 — Stops

In each case below, the skill stops and reports. It never works around the
problem.

- **The version is outside the range** (preflight): the report gives the version
  and the range. The fix is to pin back into the range and run `uv lock`.
  Widening the range is a repo change after a new spike, never a decision taken
  at run time.
- **The layout is `docs` or `both`** (preflight): the report gives the paths it
  found.
- **The fetch fails**, for example with no network, no tag or no git
  (preflight): the report gives git's error. The skill never falls back to main,
  the docs site or `skill install`.
- **Quarto is missing** (preflight): the report points to Quarto's install page.
- **A gate check fails** (the agent): the work is not done. The report names the
  check and gives its output. A build that skipped the API reference is a
  failed gate check (R4.9).

### R6 — Repo integration

R6.1 **NOTICE.** Add `document-python-package/` to the list of originals, and add
this paragraph (wording approved by the owner on 2026-10-19):

> document-python-package/ is an original work by Lowell Mason (MIT). At run
> time, its scripts/preflight.py fetches the official Great Docs skills from
> posit-dev/great-docs (MIT, Copyright (c) 2026 Posit Software, PBC). It takes
> them from the release tag that matches the installed great-docs version, keeps
> them in a cache outside this repository, and records the tag's commit. The
> skill bundles, reproduces and adapts none of their text. It only names those
> skills and sends the agent to them.

Both changes go into the commit that creates `SKILL.md`, because
`build/check_provenance.py` fails on a skill that has no NOTICE entry.

R6.2 **CLAUDE.md.** Add the skill to the originals list, and change "20
originals" to "21 originals".

R6.3 **README.md.** Add a row to the "Mine" table. The row says what the skill
adds: the preflight, the pin, the README rules, frozen examples and the
three-check gate. It also says that the skill builds on Posit's skills without
copying them.

R6.4 **design-architecture.** In SKILL.md's "Where ADRs live", add one bullet
(D6): "**Use `specs/adr/` when the repo publishes a Great Docs site.** The site
serves the package's users, and ADRs serve its maintainers." `scripts/new_adr.py`
does not change. Its default is already `specs/adr`, and its MkDocs text is
still true.

R6.5 **Suite.** Register `document-python-package` in `build/suites.toml`, with
directory `skills/document-python-package/scripts` and `with = ['pytest']`.

R6.6 **Dependencies.** No `DEPENDENCIES` entry in `install.py` is expected,
because `write-with-asd-ste100` and `docs-writer` are hand-offs by whole name.
The dependency-drift test decides. If it flags a reference, the plan records it
as hard (`DEPENDENCIES`) or soft (`SOFT_REFERENCES`, with a reason).

## Sequencing and constraints

1. The spike (V1) is the plan's first task. Its record goes to
   `specs/verification/<plan-id>-great-docs-0.17.0.md`. Its results amend this
   spec before any skill text is written.
2. `preflight.py` is written test-first: red, then green.
3. SKILL.md follows writing-skills: the RED baseline (V3) runs before SKILL.md
   is written, and GREEN runs after.
4. The NOTICE entry lands in the commit that creates `SKILL.md` (R6.1).
5. Plan 53 (agent-skills portability) has not run yet. This skill conforms to
   the portability spec's R1–R4 from its first commit. Its script has a PEP 723
   header and runs with `uv run`, its folder carries a `LICENSE` copy, and its
   frontmatter carries `license`. Plan 53's planning record counts 17 runnable
   scripts. Plan 52's vendored `write-with-asd-ste100/scripts/ste-lint.py`
   landed after that count and makes 18, so `preflight.py` makes 19
   (owner, plan 57, 2026-10-19). If this skill lands first, its plan
   adds one dated line to plan 53's Global Constraints (D8). The line names
   `document-python-package/scripts/preflight.py` as a script that already
   conforms. It also says that the skill's `LICENSE` copy already exists and
   that plan 53's executor should expect 19 scripts
   (owner, plan 57, 2026-10-19). If plan 53 lands first, nothing extra is
   needed.

## Validation and acceptance

**V1 — Spike.** The spike uses a scratch fixture package outside the repo: uv,
hatchling and Polars, numpy `'''` docstrings, Python 3.13, Quarto 1.10.19 and
great-docs 0.17.0. It answers eight questions. Each answer is recorded with the
pinned versions. An answer that contradicts this spec amends the spec, with a
dated tag, before the next task starts.

| # | Question | If the answer contradicts the spec |
|---|---|---|
| S1 | Does `init --force </dev/null` exit 0, write `.gitignore` and list the `__all__` exports in `great-docs.yml`? | R4.3 changes its command |
| S2 | Does `build </dev/null` succeed end to end, and where in the built site is the API reference index page? | If the build fails, the plan stops and the owner decides. The page's path goes into R4.9 |
| S3 | Does a failing `{python}` cell fail the build, in a docstring and in a page? | The gate (R4.9) gains a check that fails on a cell error |
| S4 | Where does `_freeze/` land? | R4.7 names the path |
| S5 | With `docs` in `default-groups`, does `uv sync` install the pin? | R4.8 changes the workflow's `uv sync` to `uv sync --group docs` |
| S6 | Does `ruff format` rewrite `'''` docstrings? | R4.4's D300 note applies only to packages that do not run `ruff format` |
| S7 | Which tool flags a missing parameter and a missing Returns section in a numpy docstring: pydoclint or numpydoc's validator? | R4.2 and R4.9 name the chosen tool, its version floor and its command |
| S8 | On the built site, do the badges move into the hero, and does the first paragraph become the meta description? | R4.5's two site claims change to what the build shows |

**Spike results** (spike S1–S8, plan 57, 2026-10-19). The spike answered
all eight questions with great-docs 0.17.0 and Quarto 1.10.19.
Its record is `specs/verification/57-great-docs-0.17.0.md`. Each requirement
that an answer changed carries that answer's tag.

**V2 — `preflight.py` tests.** They use pytest and the stdlib, with no network:

- Version: 0.16.9 is out, 0.17.0 is in, 0.17.5 is in, 0.18.0 is out and
  0.18.0rc1 is out. A package with no `uv.lock`, and a `uv.lock` with no
  great-docs entry, both give `next: pin`.
- Layout: `root`, `docs`, `both` and `none`.
- Fetch, against a local bare repo tagged `v0.17.0` that holds a `skills/` tree:
  - A fresh fetch writes `SOURCE` with the tag's SHA.
  - A complete cache is reused with no clone.
  - A failed clone leaves no cache folder.
  - A cache folder with no `SOURCE` file is replaced.
- Quarto: present and missing, by control of `PATH`.
- The report's keys, its `next:` line and the exit codes.

**V3 — Skill behavior** (writing-skills, RED then GREEN):

- Five scenarios, including "set up Great Docs for this package", "the
  build passed, so are the docs done?" (a pressure case) and "add an MCMC
  example to the docs".
- The RED run watches for five mistakes. Each mistake must flip in the GREEN
  run.
  - skills taken from main or the docs site
  - a bare `init`
  - a pin in a group that `uv sync` skips
  - the unpinned CI line left in
  - `lint` alone called "done"
- The scenarios run as decision-only `claude -p --tools ""` calls. Each call
  starts from a fresh `/tmp` subfolder that was never the repo's working
  directory. One end-to-end run on the spike's fixture covers real tool use.
- A five-query trigger smoke test checks the description. The standing decision
  rules out the description optimization loop.

**V4 — Repo gates.** The new suite passes, the dependency-drift test passes, and
`build/run_commit_lints.sh` passes on a clean clone.

## Out of scope

- Great Docs' post-migration `docs/` layout, until a new spike verifies it and
  widens the range.
- Internal hosts and package indexes (D1).
- Curating the package's published `SKILL.md` (D5).
- Pinning Quarto.
- Any copy, adaptation or summary of the official skills' text.

## Sources

- posit-dev/great-docs, tag `v0.17.0` (commit
  `1ce8eb88191df75405345b6ba2d35bea53a4f7f6`), read with `gh api` on
  2026-10-19. Main was read the same day, for comparison only.
- PyPI's JSON metadata for great-docs 0.17.0, read on 2026-10-19.
- The owner's test notes from the brainstorming session on 2026-10-19.
- `specs/agent-skills-portability-spec.md`, R1–R4, and
  `specs/plans/53-agent-skills-portability.md`.
