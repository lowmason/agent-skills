# uv re-probe for package-versions (plan 66, Task 1)

Date: 2026-10-27. Script: `specs/verification/66-uv-probe.py`. It builds its tree in the system temp directory and never writes `uv.toml` or `.python-version` into this repository. Every uv call in it runs with `--no-cache`.

Command: `uv run --no-project python specs/verification/66-uv-probe.py | tee /tmp/66-uv-probe.out`. The run used Python 3.13 for the script itself, because the repository has no `.python-version` yet. The interpreter that runs the script does not affect the rows, because each row sets its own working directory and environment. Exit status: 1 (two FAIL rows).

## Probe table

`uv --version` (first line of the output below): `uv 0.13.1 (Homebrew 2026-10-14 aarch64-apple-darwin)`. Claude Code for step 5.3: 2.1.304.

uv 0.13.1 (Homebrew 2026-10-14 aarch64-apple-darwin)

| id | probe | expected | observed | result |
|---|---|---|---|---|
| P1 | CLI --exclude-newer limits --with (jax) | jax 0.12.0, not 0.12.0.1 | 0.12.0 | PASS |
| P7a | RFC 3339 cutoff 2026-10-06T11:43:04Z is read as written | polars < 2 (cutoff just before the upload) | 1.44.2 3.13 | PASS |
| P7b | RFC 3339 cutoff 2026-10-06T11:45:04Z is read as written | polars 2.0.0 (cutoff just after the upload) | 2.0.0 3.13 | PASS |
| P7c | bare dates around the upload date, TZ=UTC (the design uses RFC 3339, not a bare date) | record | 2026-10-05: 1.44.2; 2026-10-06: 2.0.0; 2026-10-07: 2.0.0 | RECORD |
| P7d | bare dates around the upload date, TZ=Pacific/Kiritimati (the design uses RFC 3339, not a bare date) | record | 2026-10-05: 1.44.2; 2026-10-06: 1.44.2; 2026-10-07: 2.0.0 | RECORD |
| P2a | CLI --exclude-newer does not limit a script header | polars 2.0.0 | 1.44.2 3.13 | FAIL |
| P2b | UV_EXCLUDE_NEWER does not limit a script header | polars 2.0.0 | 1.44.2 3.13 | FAIL |
| P2c | a [tool.uv] exclude-newer in the header limits it | polars < 2 | 1.44.2 3.14 | PASS |
| P3a | --python 3.13 resolves a bare polars header | polars 2.0.0 on 3.13 | 2.1.0 3.13 | PASS |
| P3b | --python 3.14 with polars>=2.0 resolves | polars 2.0.0 on 3.14 | 2.1.0 3.14 | PASS |
| P3c | no --python, no .python-version (script outside the repo): which interpreter and polars | record (the spec saw 3.14 and 1.44.2) | 2.1.0 3.14 | RECORD |
| P4a | root uv.toml date reaches --with in a subdirectory | polars < 2 | 1.44.2 3.13 | PASS |
| P4b | root uv.toml date reaches a script header in a subdirectory | polars < 2 | 1.44.2 3.13 | PASS |
| P4c | constraint- and override-dependencies in uv.toml do not affect --with | polars 2.0.0 | 2.1.0 3.13 | PASS |
| P4d | UV_CONSTRAINT does not affect --with | polars 2.0.0 | 2.1.0 3.13 | PASS |
| P4e | CLI --exclude-newer overrides the uv.toml date | polars 2.0.0 | 2.1.0 3.13 | PASS |
| P4f | UV_EXCLUDE_NEWER overrides the uv.toml date | polars 2.0.0 | 2.1.0 3.13 | PASS |
| P4g | --with polars==1.44.2 on a script run takes over from the header polars>=2.0 (no dates) | polars 1.44.2 | 1.44.2 | PASS |
| P5a | a script run by its real path takes the repo uv.toml, from another directory | polars < 2 | 1.44.2 3.13 | PASS |
| P5b | the same script through a symlink does not | polars 2.0.0 | 2.1.0 3.14 | PASS |
| P6a | .python-version is found from a subdirectory, also with --no-project | 3.13 (the bare default here is 3.14) | 3 13 | PASS |
| P6b | --directory finds .python-version from another working directory | 3.13 | 3 13 | PASS |
| P6c | --directory finds the uv.toml date too | polars < 2 | 1.44.2 3.13 | PASS |
| S1 | skills/uv.toml shadows the root date for a script header (real path) | polars 2.0.0 | 2.1.0 3.13 | PASS |
| S2 | ... and for --with | polars 2.0.0 | 2.1.0 3.13 | PASS |
| S3 | ... and .python-version is still found under skills/ | 3.13 | 3 13 | PASS |
| S4 | ... and a run through a ~/.claude/skills-style symlink floats too | polars 2.0.0 | 2.1.0 3.14 | PASS |
| N1 | a nested worktree without the files inherits the date and the interpreter | polars < 2 on 3.13 | 1.44.2 3.13 | PASS |
| N2 | a nested worktree with its own uv.toml uses its own | polars 2.0.0 | 2.1.0 3.13 | PASS |
| P8a | UV_NO_CONFIG=1 drops the root date for --with | polars 2.0.0 | 2.1.0 3.14 | PASS |
| P8b | UV_NO_CONFIG=1 drops the root date for a script header | polars 2.0.0 | 2.1.0 3.14 | PASS |
| P9a | uv pip compile reads the root date from the working directory | polars < 2 | polars==1.44.2 / polars-runtime-32==1.44.2 | PASS |
| P9b | uv pip compile --exclude-newer overrides it | polars 2.0.0 | polars==2.1.0 / polars-runtime-32==2.1.0 | PASS |
| P9c | uv --no-config pip compile ignores it | polars 2.0.0 | polars==2.1.0 / polars-runtime-32==2.1.0 | PASS |
| P10 | uv python list --output-format json has the fields drift reads | version, version_parts, variant, implementation | fields present | PASS |

## Comparison with the forecast

The plan forecast FAIL on P2a and P2b only, and RECORD on P3c, P7c and P7d. The run gives the same sets. P2a and P2b are the rows that expected a command-line date and `UV_EXCLUDE_NEWER` not to limit a script header. Both limit it, so both FAIL. The uv version is the same as in the draft run (0.13.1).

One difference is not a change of uv behavior. polars 2.1.0 was uploaded on 2026-10-25, after the draft run of 2026-10-21. A floating `polars` therefore resolves to 2.1.0 now, where the draft run printed 2.0.0. P3c printed `2.1.0 3.14`, and the forecast said `2.0.0 3.14`. The meaning is the same: on Python 3.14 a bare `polars` header resolves to the newest 2.x, not to 1.44.2. Rows whose label says "polars 2.0.0" test for a major version of 2 or later, so they pass on 2.1.0. P7a and P7b test the upload time of 2.0.0 (2026-10-06T11:44:04Z), which does not change.

## Step 4: `setup-uv` and the interpreter (spec R5.2)

`.github/workflows/lints.yml` pins `astral-sh/setup-uv` at `1c37ad07a6a961277cf70c0d37d6f313000f5884` (v10.3.0) and passes no inputs. In `action.yml` at that SHA, `python-version` is an optional input (`required: false`). Its description says it sets `UV_PYTHON`. The README at that SHA says that when the input is set, it overrides the Python version from `pyproject.toml`, `.python-version` and an explicitly selected `.tool-versions` file. In `src/setup-uv.ts` the action exports `UV_PYTHON` only when that input (or a `.tool-versions` file named by `version-file`) gives a version. Without them it calls `uv python find --directory <working directory>` only to report the detected version and to key its cache. It never reads `.python-version` itself. So `lints.yml` needs no change: uv reads `.python-version` on its own (row P6a).

One more fact for Task 4 and Task 15. The action reads the root `uv.toml` only for the key `required-version` (`src/version/file-parser.ts`). The new root `uv.toml` has no such key, so the action still installs the latest uv.

## Step 5: a plain file in a skills directory (spec R2.1)

`skills/uv.toml` is a file, not a skill. Five checks:

1. Repo readers. Each lists only directories that hold a `SKILL.md`: `skill_names()` in `install.py` (`path.is_dir() and (path / 'SKILL.md').is_file()`), the skills loop in `build/check_frontmatter.py` (`d.is_dir() and (d / 'SKILL.md').exists()`) and `skill_dirs()` in `build/check_provenance.py` (the same test). `build/test_runtime_support.py` uses the same test in two places. A grep for `iterdir` and `glob(` over `install.py`, `build/` and `hooks/` finds no reader of `skills/` without the `SKILL.md` test.
2. Installed skills. `~/.claude/skills` is a real directory, not a link to `skills/`. Each repo skill in it is its own symlink (for example `writing-plans -> /Users/lowell/Projects/agent-skills/skills/writing-plans`), and it holds no `uv.toml`. So no runtime sees `skills/uv.toml` through an install.
3. Claude Code 2.1.304, live. A throwaway project had `.claude/skills/demo/SKILL.md` and a plain `.claude/skills/uv.toml`. The command was the one in the plan (`claude -p --tools "" --strict-mcp-config`, with `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`). The init record listed 111 skills. Result: `demo loaded: True | a uv.toml skill: False`. The loaded `demo` skill is the positive control. The run cost about $0.048.
4. Codex. The current page is `https://learn.chatgpt.com/docs/build-skills`, the redirect target of `https://developers.openai.com/codex/skills`. The page defines a skill as a directory that holds a `SKILL.md` file, and goes on to name optional scripts and references. Confirmed, checked in the fetched page text.
5. Gemini CLI. No single sentence says that a skill is a directory with a `SKILL.md`. Two pages together say it. `docs/cli/skills.md` describes a skill as a directory that holds all its own files. `docs/cli/creating-skills.md` names `SKILL.md` as the one file a skill must have, and flags it as required in its structure listing. Both pages are in the `google-gemini/gemini-cli` repository under `docs/cli/` (published at `geminicli.com/docs/cli/`). Confirmed in substance. Neither runtime's page says what happens to a loose file beside skill directories.

## What the run changed in the spec

The run changes two items of "uv behavior that constrains the design" in `specs/package-versions.md` (amendment A1, applied in the same commit). Item 2: a command-line `--exclude-newer`, `UV_EXCLUDE_NEWER` and a `[tool.uv] exclude-newer` table in the script header each limit the header's dependencies (P2a, P2b and P2c). Item 3: with no `--python` and no `.python-version`, uv picks Python 3.14 and a bare `polars` header resolves to the newest 2.x, so the 1.44.2 result of the first probe came from a cached environment (P3a, P3b and P3c). The design still holds: the root `uv.toml` reaches script headers (P4b, P5a), `skills/uv.toml` shadows it (S1, S2, S4), and a nested worktree inherits both files (N1). Today P3c printed polars 2.1.0 where A1 item 3 says 2.0.0, because polars 2.1.0 is newer than the draft run (see "Comparison with the forecast"). The meaning of the item is unchanged.

Probes run with uv --no-cache; uv reuses a cached environment whose requirements match, whatever freeze date built it.
