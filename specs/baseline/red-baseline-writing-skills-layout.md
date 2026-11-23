# Plan 105 guard run: the writing-skills layout

> ⚠️ Quarantine this file during any micro-test of writing-skills. It names the guard cases, the file
> each case must read and the marker each case scores, so a rep that reads this file is void.

This record holds the guard run of plan 105 (`specs/plans/105-writing-skills-improvements.md`), Tasks 3,
4 and 6. The spec, `specs/writing-skills-improvements.md`, tests item 8b with "A guard run on plan 72's
`t3` cases, old layout against new". Item 8b moves three support files of writing-skills into
`references/`. The plan's D1 adds one case with tools for each moved file. So the run compares the `old`
layout with the `new` one on six cases: plan 72's no-tools cases W1–W3 and the tools cases T1–T3. Each
arm has five scored reps per case and model, on `claude-sonnet-5-5` and `claude-opus-5-5`. Each rep runs
in a fresh context.

Task 3 wrote the kit and the rules below, from Kit to Spend stop. Its commit registers them before any
probe or rep runs. No reading is added after a probe, a pilot or a scored rep is seen. Task 4 adds the
probes, the pilot and the projection to Kit and Spend stop. Task 6 fills in the two arms' shas and adds
the results and the verdict.

## Kit

The kit is `specs/baseline/red-baseline-writing-skills-layout/kit/`. It copies files from three
committed kits and edits none of them:

- plan 72's `specs/baseline/red-baseline-writing-skills-split/kit/`: the W cases and their frame;
- plan 103's `specs/baseline/red-baseline-worktree-skills-fix/kit/`: the no-tools runner, its void step
  and the identity scrub;
- plan 104's `specs/baseline/red-baseline-mutant-screen-runs/kit/`: the tools runner, its folder layout,
  its probe and its stream and path audits.

**Step 1 check.** `specs/baseline/red-baseline-worktree-skills-fix/kit/postprocess.py` is on this
branch. `claude --version` printed `2.1.323 (Claude Code)` when Task 3 ran. If Task 6 sees another
version, it runs the four probes again first.

| File | Source | Change |
|---|---|---|
| `run_json_reps.sh` | plan 103's `run_reps.sh` | The scratch folder is `~/.cache/agent-skills/scratch/plan105/json/<case>/<arm>/<model>/`, and the rep folder prefix is `/tmp/plan105-rep-`. The scratch path keeps three parts of `<out-dir>`, not two (Deviations, item 1). |
| `probe_json.sh` | plan 103's `probe.sh` | The model is the first argument, the folder prefix is `/tmp/plan105-rep-probe-`, and the probe text is this kit's `isolation_probe.txt` (Deviations, item 2). |
| `postprocess.py`, `kit_identity.py`, `check_scrub.py` | plan 103's | Unchanged, except the first lines of `postprocess.py`'s docstring. |
| `common.sh` | plan 104's | The rep root `/private/tmp/wsl105`. The tools `Read,Glob,Grep,Edit,Write`. One cap, $1.50, for both models. No venv and no role-to-model map. |
| `run_tool_reps.sh` | plan 104's `run_reps.sh` | No `.sdd` workspace, no `setup.sh`, no `@REPO@` or `@BASE@` token, no role-to-model map and no mutant-run audit. It refuses an `<out-dir>` that does not end in `<case>/<arm>/<model>`, where the arm is `MANIFEST.txt`'s. |
| `probe_tools.sh` | plan 104's `probe.sh` | This kit's models, cap and root. |
| `rep_tools.py` | plan 104's | Keeps `check-copy`, `strip` and `summarize`. `summarize` drops the workspace copies, the run files, the commit list and the mutant-run lines, and records each tool call's `is_error`. Adds `place-copy <ref>`. |
| `privacy_sweep.py`, `isolation_probe.txt` | plan 104's | Unchanged. The probe has eight numbered questions. Line 7 asks for the user's name or email, and line 8 for another Claude session. |
| `audit.py` | plan 104's `grade.py`, its stream and path audits | Adds the Grep and Glob path audit (Deviations, item 4), the read check and the VOID reasons. |
| `sheets.py` | new | Writes the blind sheets and the key, and unblinds the grades. |
| `build_prompts.py` | new | Writes the six prompts and `MANIFEST.txt`. |
| `cases.py` | plan 72's `cases.py`, for the W cases | Adds the T frame, the T cases and each case's PASS and FAIL columns. |
| `fixtures/T1/repo/` to `fixtures/T3/repo/` | new | Each T case's project (Cases). |
| `test_wsl_kit.py` | plan 103's postprocess, postprocess-shape and runner tests and plan 104's runner and audit tests, adapted, and the tests that the plan's Task 3 names | 187 tests with a stub `claude` and no model. Suite `writing-skills-layout-kit` in `build/suites.toml` runs them. |

**The arms.** `old` is `SKILL.md`'s body and the skill folder at the last commit before Task 5 (Task 5
Step 1 records it as OLD). `new` is the same at Task 5's commit (Task 5 Step 5 records it as NEW). Task 6
fills in both shas here:

- OLD: to be filled in by Task 6.
- NEW: to be filled in by Task 6.

The `pilot` arm of Task 4 is built from HEAD and is not scored.

**The steps.** Each command runs from the repository root, with `uv run python <kit>/<script>` for a
Python script.

1. `build_prompts.py <ref> <arm> <out-dir>` reads `SKILL.md`'s body at `<ref>` with `git show`. It
   writes `W1.txt` to `W3.txt`, `T1.txt` to `T3.txt` and `MANIFEST.txt`, and it refuses an `<out-dir>`
   that exists. `MANIFEST.txt` holds the full sha, the arm, the body's sha256 and length, each prompt's
   sha256, and the sha256 of each file of `git archive <sha> skills/writing-skills`.
2. `rep_tools.py place-copy <ref>` writes that archive to `/private/tmp/wsl105-skill/writing-skills/`.
   It refuses when `/private/tmp/wsl105-skill/` holds anything. After each tools batch, the caller
   empties that folder.
3. `run_json_reps.sh <prompt> <out-dir> <first> <last> <model>` runs W reps.
   `run_tool_reps.sh <prompt-dir> <case> <out-dir> <first> <last> <model>` runs T reps, one at a time.
   Each `<out-dir>` is `runs/<case>/<arm>/<model>/`.
4. `audit.py <rep-dir> ...` prints each T rep's stream audit, path audit, read check and VOID reasons.
5. `sheets.py build <runs-root> <sheet-dir> <seed>` writes the sheets and the key. A person grades the
   sheets into `grades.tsv`, in scratch. Then `sheets.py unblind <grades.tsv> <key.json>` prints the
   verdicts and the bars. It gives the guard PASS or FAIL only when all 12 cells (6 cases × 2 models)
   are there with 5 scored reps in each arm, and `incomplete` otherwise.

**No-tools reps (W1–W3).** Each rep runs this command, as plan 103's did, from its own new, empty
folder under `/tmp`, outside every repository. A rep has no tools.

```bash
env -i <HOME, USER, LOGNAME, PATH, SHELL, TMPDIR and LANG, each when set> \
  CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
  "$CLAUDE_BIN" -p --model "$MODEL" --tools "" --strict-mcp-config --setting-sources "" --disable-slash-commands \
  --no-session-persistence --output-format json --max-budget-usd 0.50
```

`postprocess.py` voids a rep or keeps it, scrubbed, without `origin`, `credential_expires_at`,
`session_id` and `uuid`. The raw JSON stays in scratch.

**Tools reps (T1–T3).** Each rep runs from `/private/tmp/wsl105/rep<N>/repo/`. That folder is the case's
fixture, committed once as the rep's BASE. Its `HOME` is `/private/tmp/wsl105/rep<N>/home/`, with
`Library/Keychains` linked to the real one so the login works, and its `TMPDIR` is
`/private/tmp/wsl105/rep<N>/tmp/`. The command, from `common.sh`:

```bash
env -i HOME="$dir/home" USER="$USER" LOGNAME="$LOGNAME" PATH=/usr/bin:/bin:/usr/sbin:/sbin SHELL="$SHELL" \
  TMPDIR="$dir/tmp" LANG="${LANG-}" CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
  "$CLAUDE_BIN" -p --model "$model" --tools Read,Glob,Grep,Edit,Write --allowedTools Read,Glob,Grep,Edit,Write \
  --strict-mcp-config --setting-sources "" --disable-slash-commands --no-session-persistence \
  --settings "$SETTINGS" --max-budget-usd 1.50 --output-format stream-json --verbose
```

`$SETTINGS` denies `Read(//Users/**)`, `Edit(//Users/**)`, `Write(//Users/**)`, `Read(~/Library/**)`,
`Edit(~/Library/**)` and `Write(~/Library/**)`, and the tools `ListAgents`, `SendMessage`,
`PushNotification` and `RemoteTrigger` by name. It sets `"syncClaudeAiSkills": false`. Before each
rep, `/private/tmp/wsl105/` must be empty, and `check-copy` must find the skill copy and the prompt as
`MANIFEST.txt` gives them. After the rep, `summarize` writes `final.diff` against BASE, new files
included, and `summary.json`, with `check-copy`'s result. A trap parks the rep folder under
`~/.cache/agent-skills/scratch/plan105/tools/<case>/<arm>/<model>/`, beside the raw stream.

**Out of every rep's reach.** The spec and the plan stay out of each rep's reach (the plan's Global Constraints, Micro-tests). A
no-tools rep has no tools. A tools rep's settings deny `Read(//Users/**)`. Its skill copy is
`git archive <ref> skills/writing-skills`, so it holds no other file of the repository. Its folder holds
only its case's fixture. The path audit voids a rep whose tool input names a path outside the allowed
roots (VOID rule).

**Grep and Glob.** This is a deviation from plan 104's audit: plan 104's audit covers Read, Edit, Write
and Bash only; these reps have Grep and Glob, so the audit also checks their path arguments. The
settings hold no Grep or Glob rule, because the repository's Claude Code guide does not document that
rule syntax. `audit.py` judges the `path` of each Grep and Glob call, joined to the rep's repository
when it is relative. It judges a Glob `pattern` that is an absolute path or that climbs with `..`: the
part up to the last `/` before the first wildcard. A `..` after a wildcard cannot be resolved, so it is
a hit too. Each `{...}` alternative, nested or comma-split, is a path of its own. An alternative that
holds `..` is a hit. An alternative that starts with `/`, `~` or `$HOME` is judged by its literal part,
so one inside the allowed roots stays clean. This is a recorded limit: a `*`, `?` or `[` only descends
from the literal part, so a `**` from the rep folder can list names under `home/Library/Keychains`, the
link to the real Keychains folder. That folder holds neither the spec nor the plan.

**Self-test.** `test_wsl_kit.py` adds 187 tests. They pass through
`uv run python build/run_suites.py writing-skills-layout-kit`. `privacy_sweep.py` over this record and
the kit gives 5 hits. Each is the pinned `//Users/**` deny pattern: in `common.sh`, in
`test_wsl_kit.py`, and on three lines of this record (Kit). The sweep's check for the home's parent
folder matches that pattern. No hit names the home or the user. These counts are for tracked files: a
`kit/__pycache__/` or `kit/.pytest_cache/` folder, when a test run leaves one, adds hits from the source
paths written into it. Git ignores both folders.
`check_scrub.py` prints PASS.

## Cases

**W1–W3**, as plan 72 states them (`specs/baseline/red-baseline-writing-skills-split.md:20-24`). The
last column is plan 72's bar. This run's bars are in Bars.

| Case | Target file | Reference | `t3` bar, per model |
|---|---|---|---|
| W1 | `skills/migration-dry-run/SKILL.md` | `references/discovery.md` | ≥ 4/5 |
| W2 | `skills/cache-invalidation/SKILL.md` | `references/flowcharts.md` | ≥ 4/5 |
| W3 | `skills/release-notes-gate/SKILL.md` | `references/bulletproofing.md` | ≥ 4/5 |

Their prompt is plan 72's `FRAME` and `CASES`, byte for byte (`cases.FRAME_W` and `cases.CASES_W`), filled
as plan 72's `build_prompts.py` fills them.

**T1–T3**, as the plan's Task 3 Step 4 states them. Each case states that the earlier steps it needs are
done, so the Iron Law does not hold the agent.

| Case | Moved file (hops in old → new) | Conversation | Target | Marker (use) |
|---|---|---|---|---|
| T1 | `testing-skills-with-subagents.md` (1 → 1) | Partner: "I want a new skill, `lockfile-refresh`, for agents that change dependencies. They bump a version in `pyproject.toml` and commit without running `uv lock`, so `uv.lock` goes stale. We'll build it with writing-skills, RED first." Then: "Write the pressure scenarios for the RED baseline, three of them, into `specs/lockfile-refresh-scenarios.md`. Don't run them yet." | `specs/lockfile-refresh-scenarios.md` | at least two scenarios end by making the tested agent choose among lettered options (A, B, C …) |
| T2 | `persuasion-principles.md` (2 → 1) | Partner: "Our `secrets-scan-gate` skill says to run `gitleaks protect --staged` before every commit. Agents skip it under pressure." `[you, tools]`: the baseline ran three pressure scenarios, 5 reps each, with the skill loaded. In 8 of 15 runs the agent committed without the scan. The rationalizations are in `specs/secrets-scan-gate-baseline.md`: "the diff only touches docs", "CI runs a scanner anyway", "I'll scan before I push". Then: "Rewrite the rule paragraph in `skills/secrets-scan-gate/SKILL.md` so it holds. Then tell me which persuasion principles your wording uses, and which ones you left out on purpose." | `skills/secrets-scan-gate/SKILL.md` | the final message names at least two of Authority, Commitment and Social Proof as used, and names Liking or Reciprocity as left out |
| T3 | `graphviz-conventions.dot` (2 → 1) | Partner: "Agents using our `http-retry-policy` skill keep retrying calls that should fail fast. I want a small decision flowchart for 'retry or fail fast' in `skills/http-retry-policy/SKILL.md`." `[you, tools]`: the baseline ran three scenarios, 5 reps each. In 10 of 15 runs the agent retried a POST that had no idempotency key. The reasons are in `specs/http-retry-policy-baseline.md`. Then: "Add the flowchart. It must show the health check `curl -sf https://status.example.invalid/health` that the agent runs first, and the warning 'Never retry a POST without an idempotency key'." | `skills/http-retry-policy/SKILL.md` | the added `dot` block draws the `curl` command as a `shape=plaintext` node, or the warning as a `shape=octagon` node |

Each case's project is `kit/fixtures/<case>/repo/`:

- T1: `pyproject.toml` and `uv.lock` of a small CLI, `tide-tables`, and `specs/`, empty but for a
  `.gitkeep`, because git keeps no empty folder.
- T2: `skills/secrets-scan-gate/SKILL.md`, a short skill whose rule paragraph is soft ("For small
  changes the scan is optional"), and `specs/secrets-scan-gate-baseline.md`, the baseline's three
  scenarios and the three rationalizations.
- T3: `skills/http-retry-policy/SKILL.md`, a short skill with a retry table and no chart, and
  `specs/http-retry-policy-baseline.md`, the baseline's three scenarios and reasons.

No fixture file and no T case text holds a marker: no lettered options in T1, no persuasion principle's
name in T2, and no `dot` block, `plaintext` or `octagon` in T3. A self-test checks this.

**The T frame.** `cases.FRAME_T` is plan 72's frame with these changes:

1. The skill block opens with `Base directory for this skill: /private/tmp/wsl105-skill/writing-skills`
   and a blank line, as Claude Code loads a skill.
2. The sentence before the skill block names that folder in place of `~/.claude/skills/writing-skills/`
   (Deviations, item 3).
3. "You have no tools in this turn." becomes "In this turn your tools are Read, Glob, Grep, Edit and
   Write, and your working directory is your partner's project."
4. The last paragraph and its two ACTION-line bullets become "It is your turn. Do the task with your
   tools, then write the message you would send to your partner."

**Domains.** No fixture and no T case repeats a worked example of writing-skills or one of plan 72's W
cases. The words of the three domains (`lockfile`, `uv lock`, `uv.lock`, `pyproject`, `tide`,
`dateutil`, `tabulate`, `gitleaks`, `secret`, `.env`, `retry`, `idempot`, `curl`, `health`, `webhook`,
`status.example`, `POST `) have no hit, case folded, in `skills/writing-skills/SKILL.md`, its four
`references/` files, its three support files, or plan 72's `cases.py`.

## Reading rule, W cases

**Reading rule for every rep of either arm.** "Reads the reference" means an ACTION line that reads or
opens the named file, as `references/<name>.md` or as `<name>.md` inside writing-skills'
references directory. Order is the order of the ACTION lines. A rep passes when such a read
comes before the first ACTION that creates or edits the target SKILL.md. A rep with no create or
edit ACTION passes when it reads the file. A rep that names the file only in its message, with
no read ACTION, fails. A rep whose header shows VOID (a tool or the advisor ran) is rerun with
the next free rep number and does not count.

The sheets write each writing-skills path as `<skill>/<basename>` (Blind grading). So a grader reads
`<skill>/<name>` in an ACTION line as the named reference, in both arms alike.

## Reading rule, T cases

A rep passes when both parts hold.

- *Read:* the tool log has a Read whose `file_path` ends in `/<moved file>` and whose tool result is
  not an error, before the first Edit or Write of the case's target. A rep with no Edit or Write of the
  target passes this part with any such Read. Glob, Grep and reads of other files do not count. A Read
  with `offset` or `limit` counts and is marked partial.
- *Use:* the blind grader marks the case's marker as present in the rep's answer.

`audit.py` reads the Read part from the raw stream, in stream order. The moved file is `cases.MOVED`, and
`ends in /<moved file>` is an exact suffix, so `old-persuasion-principles.md` and
`persuasion-principles.md.bak` do not count. The target is the case's `cases.TARGET` inside the rep's
`repo/`, in its `/tmp` and `/private/tmp` forms, with each `..` resolved. A relative `file_path` in an
Edit or a Write is joined to `repo/`, the working directory, first. The path audit joins a relative
`file_path` the same way. `audit.py` marks a Read whose tool result is an error, and such a Read does
not count. It gave the rep no content, and plan 72's rule says that "Reads the reference" means "an
ACTION line that reads or opens the named file". A failed Edit or Write of the target still counts as
the first write, because the rule orders the rep's attempts.
`sheets.py build` puts the read check in the key, and `sheets.py unblind` joins it to the grade.

## VOID rule

A W rep that `postprocess` voids (`result_index` above 0, or an `origin` that is not null). A T rep
with a V9 finding, a path outside the allowed roots, a changed skill copy, a stream line that is not
JSON, or the subtype `error_max_budget_usd`. Any rep with a kit error. A void rep does not count, and
the next rep number replaces it. A third void in one arm stops the run, and the owner hears of it.

How the kit applies it:

- **W reps.** `postprocess.py` also voids a raw JSON that is missing, empty or not an object (plan
  103's rule). A void rep gets a `rep<N>.VOID` note and no `rep<N>.json`.
- **T reps.** `audit.py`'s `void_reasons` gives each reason. V9 is plan 104's check: a peer `origin` at
  any depth of any record, or a cross-session tool (`ListAgents`, `SendMessage`, `PushNotification`,
  `RemoteTrigger`) in the init record. The allowed roots are the rep's folder and the skill copy, each
  in its `/tmp` and `/private/tmp` forms. An Edit or a Write into the skill copy, any spelling of the
  real home, and a path through `$HOME/Library` are hits too, as in plan 104's audit. A kit error is
  `summary.json`'s `kit_error`, a missing `summary.json` or a missing raw stream.
- **Added by Task 3, for the task review.** Two more reasons void a T rep. First, a second result
  record: a peer's turn adds one, as it raises `result_index` for a W rep. The plan's self-test
  `test_stream_audit_voids_a_second_result_record` asks for it. Second, a run that errors in another
  way: no result record, a subtype other than `success`, or `is_error` true. Such a run gives no answer
  to grade.
- **Added in the Task 3 review, for W reps.** A kept `rep<N>.json` whose `subtype` is not `success`, or
  whose `is_error` is true, is a run error too. `sheets.py build` skips it as void and prints the
  reason, and the next rep number replaces it. `postprocess.py` (plan 103's copy) is unchanged.
- **Check each W batch for a run error.** `sheets.py build` runs after all reps, so it is too late to
  replace a rep inside its pair or to count it toward the third-void stop. After each W batch, list
  the kept reps with this command from the repository root. A rep with a reason is void and does not
  count: run the next rep number in its place, and count it as a void. `sheets.py build` skips it.

  ```bash
  uv run python -B -c 'import sys, pathlib; sys.path.insert(0, "specs/baseline/red-baseline-writing-skills-layout/kit"); import sheets; [print(p.name, sheets.w_run_error(p)) for p in sorted(pathlib.Path(sys.argv[1]).glob("rep*.json"))]' <out-dir>
  ```

## Blind grading

Sheets name the sheet id and the case, never the arm. Before grading, diff one `new` sheet against an
`old` sheet of the same case: only the answer may differ. A read can still hint at the arm. For
example, a W2 rep of the `new` arm may name `graphviz-conventions.dot`. This record states that limit, and the W verdicts stay mechanical.

`sheets.py build` writes one sheet per scored rep, as `<id>.txt`, where `<id>` is a 6-hex id drawn from
the seed. A sheet holds the case, its PASS and FAIL columns and the answer. A W answer is the result
text. A T answer is the final message and `final.diff`. A sheet names no arm, model or rep. In the
answer, every path that ends in a writing-skills file name becomes `<skill>/<basename>`. `SKILL.md`,
`LICENSE` and `LICENSE-superpowers` change only after `writing-skills/` (Deviations, item 6). The key,
each sheet id with its case, arm, model, rep and read check, goes to `key.json` beside the sheet
folder, in scratch. `build` refuses a sheet folder inside a git repository. The key is read only after
every sheet is graded.

## Bars

Per case and model, `new` passes ≥ `old` passes − 1. The W cases also need `new` ≥ 4/5. The guard passes
when every case and model meets its bars. On a failure, stop, record, and ask the owner. Change no
pointer wording.

## Predictions (descriptive)

- W: `new` ≈ `old`.
- T1: `new` ≈ `old`, one hop in both.
- T2 and T3: `new` ≥ `old`, one hop instead of two.

T2's use part can be met from general knowledge: the principle names are well known, so a rep can name
them without reading `persuasion-principles.md`. The Read part carries T2.

Report the read and use counts apart, and the partial reads. For the T2 and T3 `old` reps, also report
whether the read went through `bulletproofing.md` or `flowcharts.md` first.

## Spend stop

Global Constraints, Spend (D2). The cap for every rep of plan 105 is $40, probes and pilots included.
Each rep's `--max-budget-usd` is $0.50 for a no-tools rep and $1.50 for a tools rep.

1. Task 4 projects the total from the pilot's costs: spend so far + 60 × $0.05 for the W reps + 30 ×
   the mean Sonnet T pilot cost + 30 × the Opus T pilot cost. A projection above $35 stops the run
   before any scored rep.
2. Task 6 runs each case and model as a pair: 5 `old` reps, then 5 `new` reps. Before each pair, the
   check is: running total + 10 × the per-rep cap ≤ $40.
3. A pair that fails the check stops the run, so no `old` arm is left without its `new` arm. The run
   reports BLOCKED with the spend table.

The total is the sum of `total_cost_usd` over every probe, pilot and rep of plan 105.

| Item | Cost (USD) | Running total (USD) |
|---|---|---|
| Start, before any probe or rep | 0.00 | 0.00 |

## Deviations

Each was made in Task 3, before any probe or rep, and the task review rules on it.

1. **`run_json_reps.sh`'s scratch path keeps three parts of `<out-dir>`.** Plan 103's runner keeps
   two. Task 6's `<out-dir>` is `runs/<case>/<arm>/<model>/`, so with two parts W1 and W2 of one arm
   and model would share a scratch folder. The overwrite guard would then refuse W2's rep1.
2. **`probe_json.sh` takes the model as an argument.** Plan 103's probe runs one fixed model, and
   Task 4 probes both models.
3. **The T frame names the skill copy's folder.** Plan 72's frame says that the skill's files sit in
   `~/.claude/skills/writing-skills/`. For a tools rep that path is inside its own empty HOME, so the
   sentence names `/private/tmp/wsl105-skill/writing-skills/` instead.
4. **The Grep and Glob path audit** (Kit, Grep and Glob).
5. **Added VOID reasons** (VOID rule, Added by Task 3 and Added in the Task 3 review). Two void a T
   rep: a second result record, and a run error. The run-error reason voids a W rep too: a kept
   `rep<N>.json` whose `subtype` is not `success`, or whose `is_error` is true.
6. **The sheets change `SKILL.md`, `LICENSE` and `LICENSE-superpowers` only after `writing-skills/`.**
   Each T2 and T3 target is a `SKILL.md` too, and these three files do not move.
7. **`build_prompts.py` takes a `pilot` arm**, which Task 4 uses, beside `old` and `new`.
8. **A Read whose tool result is an error does not count toward the Read part** (Reading rule, T
   cases). The Task 3 review ruled on it before any rep ran. A failed Edit or Write of the target still
   counts as the first write.
