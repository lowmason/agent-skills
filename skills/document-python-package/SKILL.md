---
name: document-python-package
description: >
  Use when documenting a Python package with Great Docs: setting up or building
  its docs site, running great-docs init, build or lint, writing numpy
  docstrings or user-guide pages for it, making its README serve as the site
  homepage, adding executed or frozen examples, or deploying the site to GitHub
  Pages. Also triggers when a repo has a great-docs.yml file or a great-docs/
  build folder.
license: MIT
compatibility: >
  Requires uv to run bundled scripts (dependencies are declared inline); Python
  3.11+. Also requires git, Quarto and great-docs >=0.17.0,<0.18, and the
  preflight script fetches Posit's official Great Docs skills from github.com.
metadata:
  author: Lowell Mason
  version: "1.0"
---

# Document a Python Package with Great Docs

Great Docs builds a Quarto site from a package's docstrings, README and
user-guide pages. Posit publishes five official skills for it. This skill is a
thin layer over them for great-docs 0.17.x and public packages (github.com,
PyPI, GitHub Pages). It adds a preflight, a few conventions and a done gate.

The layer exists because the release and the official text disagree. In
0.17.x, `great-docs init` writes `great-docs.yml` at the project root, and
`build` writes an ephemeral `great-docs/` folder. The main branch and its
skills describe an unreleased `docs/` layout. So the official skills are read
only from the release tag that matches the locked version, and the preflight
fetches that copy.

## Preflight first

Run it from the package root, and act on its last line:

```bash
uv run <this-skill-dir>/scripts/preflight.py
```

Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.

It prints `key: value` lines: `great-docs` (the version that `uv.lock` pins),
`range`, `in-range`, `layout`, `config`, `quarto`, `skills` (the cached
official skills) and, last, `next:`.

| `next:` | Do |
|---|---|
| `pin` | Pin, then run the preflight again |
| `init` | Init |
| `ready` | The sections the task needs, then the gate |
| `stop: …` | Stop and report the line. Never work around it |

Exit 1 is a stop:

- **Version outside `>=0.17.0,<0.18`.** Pin back into the range and run `uv lock`. Widening the range is a repo change after a new spike, never a decision at run time.
- **Layout `docs` or `both`.** Report the paths. That layout belongs to an unreleased great-docs.
- **Fetch failed** (no network, no tag, no git). Report git's error. Never fall back to the main branch, the docs site or `great-docs skill install`.
- **Quarto missing.** Point the user to https://quarto.org/docs/get-started/.

## Which text wins

Highest first:

1. The installed CLI's `--help` (`uv run great-docs <command> --help`) and the files that `init` actually wrote.
2. This skill's conventions. Where they conflict with the official text, they win.
3. The cached official skills, under the preflight's `skills:` path, for everything else:
   - CLI use and builds: `great-docs/SKILL.md`
   - `great-docs.yml`: `configure-site/SKILL.md`
   - Docstrings: `revise-docstrings/SKILL.md`
   - User-guide pages: `write-user-guide/SKILL.md`
   - `author-skills/SKILL.md`, only when the user asks to curate the package's published skill

Never read main-branch text or the docs site's skills, and never run
`great-docs skill install`. The cached skills' script folders are reference
only: never run their scripts.

| The official skills say | Do instead |
|---|---|
| `pip install great-docs`, `pip install --upgrade great-docs` or `uv pip install --upgrade great-docs` | The pinned `docs` group and `uv lock` (Pin). No upgrade outside the range |
| `pip install -e .` before a build | `uv sync` and `uv run`, which install the project itself |
| Run the bundled `setup-env.sh` | Never run it. Pin replaces it |
| Run the bundled `run-build.sh`, or a bare `great-docs build` | `uv run great-docs build </dev/null`, inside the gate |
| `great-docs init --force` to reset a config | Never run `init` when a config exists |
| A bare `great-docs <command>` | `uv run great-docs <command>` |

## Pin

Add the pin to `pyproject.toml`, then run `uv lock`:

```toml
[dependency-groups]
docs = ['great-docs>=0.17.0,<0.18', 'numpydoc>=1.11']

[tool.uv]
default-groups = ['dev', 'docs']   # the package's existing groups, plus docs
```

The pin's range equals the preflight's range. uv's default for
`default-groups` is `['dev']`, so without `docs` in that list a plain
`uv sync`, locally or in CI, skips the pin. Then run the preflight again: it
fetches the official skills and names the next step.

numpydoc reads its checks from `pyproject.toml`. Add this table with the pin:

```toml
[tool.numpydoc_validation]
checks = ['PR01', 'RT01', 'GL08']
exclude = ['\._\w+$']
```

## Init

Only when the preflight says `next: init` (no config yet):

```bash
uv run great-docs init --force </dev/null
```

With no config to delete, `--force` only skips the `.gitignore` prompt, and
`</dev/null` keeps any other prompt from waiting.
Then check two things in `great-docs.yml`: `parser: numpy`, and the package's
`__all__` exports listed.

When a config exists, never run `init`, because `--force` deletes the config.
Edit `great-docs.yml` as `configure-site` describes.

## Docstrings

- Write numpy style on every `__all__` export and on the public methods of each exported class.
- `revise-docstrings` covers the Great Docs details, such as `%seealso`.
- For bulk drafts, dispatch the `docs-writer` agent (its docstrings lane) with the numpy and completeness rules in the brief. When that agent is not installed, draft directly.
- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''` docstrings, ignore D300. A package that runs `ruff format` keeps them only with `quote-style = 'preserve'` in its ruff settings.

## The README is the homepage

With `homepage: index`, one README serves GitHub, PyPI and the site:

- Put the badges in one block at the top. The site shows the block as it stands.
- Make the first paragraph a plain summary of one or two sentences. It becomes the site's meta description.
- Use absolute URLs for images and links, because PyPI does not resolve relative paths.
- Use no GitHub-only syntax, such as `> [!NOTE]` alerts or Mermaid blocks. PyPI shows them as plain text.
- The `docs-writer` agent drafts the README (its README lane) when it is installed, and `write-with-asd-ste100` shapes the prose.

## User-guide pages

Follow `write-user-guide`. `write-with-asd-ste100` shapes the prose.

## Executed examples

- Docstring examples run when their docstring changes, and on any build with no `_freeze/` cache, such as CI without a committed cache. Keep them fast and deterministic: no MCMC, no network, fixed seeds.
- Put slow work, such as MCMC, in user-guide pages under `freeze: auto`. Commit the `_freeze/` cache, so that CI renders the pages without running the code again.
- After the code on a frozen page changes, render locally and commit the new cache.

## Deploy

```bash
uv run great-docs setup-github-pages
```

Then delete the generated `uv pip install great-docs` line from the workflow,
because `uv sync` already installs the pinned `docs` group. Do this again
after every regeneration of the workflow.

## The gate

The docs are done only when all three checks pass, run from the package root:

1. `uv run great-docs lint` exits 0.
2. `uv run great-docs build </dev/null` passes, which takes all of these:
   - The command exits 0.
   - Its output has none of the four lines that mean the build went on with no API reference:
     - `Skipping API reference configuration`
     - `API reference skipped (non-Python project)`
     - `No documentable exports found — skipping API reference`
     - `API reference disabled (reference: false), skipping`
   - `great-docs/_site/reference/index.html` exists.
3. `uv run numpydoc lint $(git ls-files '<package-dir>/*.py')` exits 0. `<package-dir>` is the folder that holds the package's `__init__.py`, so the check covers every `__all__` export.

After the gate, run `uv run great-docs check-links`, and
`uv run great-docs proofread` when `harper-cli` is installed. Report what they
find. They never block.

A failed check means the work is not done. Name the check and give its output.

| Thought | Reality |
|---|---|
| "The build passed, so the docs are done." | A build can exit 0 with no API reference. Check its output and the index page, then run lint and the completeness check. |
| "Lint shows no errors, so we are done." | Lint only warns about a public method with no docstring, and it does not check sections. The completeness check is the third gate. |
| "The user is in a hurry, so the rest can wait." | Report what passed and what did not. Never call the docs done before all three pass. |

## License

This skill is MIT licensed: see [LICENSE](LICENSE). Posit's official Great
Docs skills are MIT licensed, Copyright (c) 2026 Posit Software, PBC. The
preflight fetches them at run time into a cache outside this skill. This
skill bundles none of their text.
