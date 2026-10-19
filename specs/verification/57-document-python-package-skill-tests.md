# Skill tests: document-python-package

Plan 57, Tasks 2 and 4. This record covers validation item V3 of
`specs/document-python-package-spec.md`: a RED baseline before the skill text
existed, GREEN after it, a trigger test of the description and one end-to-end
run. The pre-registered rules, the prompts and the raw replies stay in the
test kit, `~/.cache/agent-skills/scratch/document-python-package-kit/`,
outside this repository.

## Setup

| Setting | Value |
|---|---|
| Claude Code (the held binary) | 2.1.303 |
| Model and effort | `claude-opus-5-5`, medium |
| Scenario calls | Decision-only: `--tools ""`, `--strict-mcp-config`, no budget flag, a scrubbed environment, each arm from a new folder under `/tmp` |
| Replies per scenario and arm | 5 |
| RED: date and cost | 2026-10-19, $2.71 for 25 replies |
| GREEN: date and cost | 2026-10-19, $3.60 for 25 replies |

## Scenarios and items

| Scenario | The user's request | Its item |
|---|---|---|
| `sc1-setup` | Set up Great Docs for a fresh package | M2, a bare `init`, and M3, a pin that a plain `uv sync` skips |
| `sc2-deploy` | Deploy the site, with the generated workflow given | M4, the unpinned CI line left in |
| `sc3-done` | Confirm that the docs are done after a build and a clean lint | M5, done without the gate |
| `sc4-mcmc` | Add an MCMC example | X1, the slow example in the wrong place |
| `sc5-official-skills` | Get the official skills and follow them | M1, the official skills from the wrong source |

## RED

RED ran before any skill text existed: no `skills/document-python-package/`
folder and no user-level copy. The environment keeps `HOME`, so the owner's
user-level settings load into every call. The replies show the owner's output
style. GREEN keeps the same settings.

Each item's count is out of the 5 replies of its own scenario:

| Item | Its scenario | RED (of 5) | Shows |
|---|---|---|---|
| M1, the official skills from the wrong source | `sc5-official-skills` | 2 | yes |
| M2, a bare `init` | `sc1-setup` | 5 | yes |
| M3, a pin that a plain `uv sync` skips | `sc1-setup` | 0 | no |
| M4, the unpinned CI line left in | `sc2-deploy` | 0 | no |
| M5, done without the gate | `sc3-done` | 5 | yes |
| X1, the slow example in the wrong place | `sc4-mcmc` | 4 | yes |

One quote for each item that showed:

- M1 (`sc5-official-skills-4`): `git clone --depth 1 https://github.com/posit-dev/great-docs /tmp/gd-skills-src/great-docs`, a clone of the default branch.
- M2 (`sc1-setup-1`): `uv run great-docs init`, with no `--force` and no input for its prompt.
- M5 (`sc3-done-1`): "After that you can merge." The steps before it fix one docstring and rerun lint and the build, with no completeness check.
- X1 (`sc4-mcmc-4`): "I would also leave freeze at its default if the cell runs in a few seconds."

M3 and M4 did not show. Every `sc1-setup` reply put great-docs in the `dev`
group with `uv add --dev`. uv's default `default-groups` is `['dev']`, so a
plain `uv sync` installs it. Every `sc2-deploy` reply deleted the
`uv pip install great-docs` line on its own. Outside its own scenario, M4
occurred once (`sc1-setup-4`): that reply ran `setup-github-pages` and kept
the generated workflow as it was. No reply was void.

Decision: rule 1 passes, because M1, M2 and M5 show. X1 shows too, so GREEN
must flip M1, M2, M5 and X1 (rule 3). M3 and M4 keep their text in SKILL.md,
because the spec requires it (rule 2). V3 could not test their flip.

## GREEN

GREEN ran after the bundle commit, with the committed SKILL.md in each
prompt. No reply was void. Each item's count is out of the 5 replies of its
own scenario:

| Item | Its scenario | RED (of 5) | GREEN (of 5) | Elsewhere in GREEN |
|---|---|---|---|---|
| M1, the official skills from the wrong source | `sc5-official-skills` | 2 | 0 | 0 |
| M2, a bare `init` | `sc1-setup` | 5 | 0 | 0 |
| M3, a pin that a plain `uv sync` skips | `sc1-setup` | 0 | 0 | 0 |
| M4, the unpinned CI line left in | `sc2-deploy` | 0 | 0 | 0 |
| M5, done without the gate | `sc3-done` | 5 | 0 | 0 |
| X1, the slow example in the wrong place | `sc4-mcmc` | 4 | 0 | 0 |

What the GREEN replies did in place of each item that RED showed:

- M1: all five `sc5-official-skills` replies read the official skills from
  the preflight's `skills:` cache, which the preflight fetches at the tag that
  matches the locked version.
- M2: all five `sc1-setup` replies run
  `uv run great-docs init --force </dev/null`.
- M5: all five `sc3-done` replies say that the docs are not done, and name
  the three gate checks that must still pass.
- X1: all five `sc4-mcmc` replies put the MCMC on a user-guide page with
  `freeze: auto` and commit its `_freeze/` cache.

Decision: rule 3 passes. M1, M2, M5 and X1 each occur in 0 of their own
scenario's 5 replies, and no item occurs anywhere in GREEN. M3 and M4 occur
nowhere either, but RED never showed them, so V3 could not test their flip
(rule 2).

The kit's `RESULTS.md` holds reading notes for M1, M3, M4, M5 and X1. They
were written after the RED replies were read and before any GREEN reply
existed, and both arms were read with them. Two RED verdicts depend on them:
`sc1-setup-4` (M4) and `sc3-done-3` (M5). Under M5's literal wording alone,
RED's M5 count is 4 of 5, so M5 still shows.

One reply did something that no item covers. `sc5-official-skills-3`
replaced gate check 3's `git ls-files` list with `find`, because its
environment said that the folder is not a git repository. The other four
`sc5-official-skills` replies said to report that instead. Outside a
repository, the check as written fails closed: the file list is empty, and
`numpydoc lint` with no files exits 2.

## REFACTOR

None: GREEN passed in its first run.

## Trigger test

Five queries, one call each, on 2026-10-19. Each call ran in a new git repo
staged from a fixture tag, with a copy of the skill in `.claude/skills/` and
tools on, up to `--max-turns 3`. All five calls listed the skill in their
init record. The five calls cost $2.01.

| Id | Fixture tag | Query | Expected | Result |
|---|---|---|---|---|
| t1 | `pristine` | "Set up a documentation website for this package with Great Docs." | trigger | triggered |
| t2 | `configured` | "great-docs build finished, but the site has no API reference. Why?" | trigger | triggered |
| t3 | `configured` | "Make the README double as the homepage of our docs site." | trigger | triggered |
| t4 | `configured` | "Deploy the documentation site to GitHub Pages." | trigger | triggered |
| t5 | `pristine` | "Set up an MkDocs site with mkdocs-material for this package." | no trigger | not triggered |

All five results are as expected, so the description needed no revision.

## End-to-end run

One run on 2026-10-19, `e2e-1`, in a staged copy of the `pristine` fixture,
with tools on, the owner's permission mode, `--max-budget-usd 15` and a fresh
`XDG_CACHE_HOME`. The prompt: "Set up Great Docs for this package, and tell me
when the docs are done." The run ended with exit 0 after 11 turns and 9 tool
calls. It cost $0.96, and no tool call was void.

| Criterion | Result | Evidence |
|---|---|---|
| E1, the skill loads first | pass | Call 1 calls the Skill tool with `document-python-package`, before any great-docs command. |
| E2, the preflight leads | pass | Call 2 runs the preflight: `next: pin`. Call 4 pins, runs `uv lock` and `uv sync`, and runs it again: `next: init`. Call 5 runs `init`. |
| E3, the pin | pass | `pyproject.toml` gets `docs = ['great-docs>=0.17.0,<0.18', 'numpydoc>=1.11']` and `default-groups = ['dev', 'docs']`. Call 4 runs `uv lock`. |
| E4, one `init` | pass | Call 5 runs `uv run great-docs init --force </dev/null`, the only `init`. It creates `great-docs.yml`. |
| E5, no forbidden install | pass | No call runs an official script, `great-docs skill install`, `pip install` or `uv pip install`. |
| E6, done only after the gate | pass | Call 7 runs lint, the build with its log and index-page checks, and numpydoc, after call 6's last source edit. All three exit 0. The final message says: "The docs are done. All three required checks pass." |
| E7, `gate.py` agrees | pass | In the run's repo afterwards, `gate.py` prints `PASS` for lint, the build and completeness, and exits 0. |

The run also fixed the fixture's three docstring gaps in `core.py`, the ones
that numpydoc found in the spike (S7). The final message leaves the untracked
`_freeze/` folder to the user, and offers to commit it or ignore it. No
criterion failed, so no `e2e-r1` ran.

## Verdict

The skill removed the four mistakes that RED showed (M1, M2, M5 and X1) with
no new one, its description triggered exactly as expected, and one end-to-end
run took a fresh package to a passing gate before it called the docs done.
V3 could not test M3 and M4, because RED never showed them.
