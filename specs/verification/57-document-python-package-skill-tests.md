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
| GREEN: date and cost | TO-RECORD |

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

TO-RECORD

## REFACTOR

TO-RECORD

## Trigger test

TO-RECORD

## End-to-end run

TO-RECORD

## Verdict

TO-RECORD
