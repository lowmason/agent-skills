# Plan 105 guard run: the writing-skills layout

> ⚠️ Quarantine this file during any micro-test of writing-skills. It names the guard cases, the file
> each case must read and the marker each case scores, so a rep that reads this file is void.

This record holds the guard run of plan 105 (`specs/plans/completed/105-writing-skills-improvements.md`), Tasks 3,
4 and 6. The spec, `specs/completed/writing-skills-improvements.md`, tests item 8b with "A guard run on plan 72's
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
| `test_wsl_kit.py` | plan 103's postprocess, postprocess-shape and runner tests and plan 104's runner and audit tests, adapted, and the tests that the plan's Task 3 names | 191 tests with a stub `claude` and no model. Suite `writing-skills-layout-kit` in `build/suites.toml` runs them. |

**The arms.** `old` is `SKILL.md`'s body and the skill folder at the last commit before Task 5 (Task 5
Step 1 records it as OLD). `new` is the same at Task 5's commit (Task 5 Step 5 records it as NEW). Task 6
fills in both shas here:

- OLD: `fdc410e0b0abd745697dc1b7dffe882f72b180bf`
- NEW: `46fe35d52635268f75cadb967edd69f52bd74190`

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
link to the real Keychains folder. In the same way, a relative brace alternative under an absolute
prefix is not joined to that prefix. So `/private/tmp/wsl105/rep1/{home/Library/Keychains,x}/*` spells a
`$HOME/Library` path and is no hit. Both cases are harmless, because the Keychains link holds neither
the spec nor the plan.

**Self-test.** `test_wsl_kit.py` adds 191 tests. They pass through
`uv run python build/run_suites.py writing-skills-layout-kit`. `privacy_sweep.py` over this record and
the kit gives 5 hits. Each is the pinned `//Users/**` deny pattern: in `common.sh`, in
`test_wsl_kit.py`, and on three lines of this record (Kit). The sweep's check for the home's parent
folder matches that pattern. No hit names the home or the user. These counts are for tracked files: a
`kit/__pycache__/` or `kit/.pytest_cache/` folder, when a test run leaves one, adds hits from the source
paths written into it. Git ignores both folders.
`check_scrub.py` prints PASS.

**Sweep of the committed run output (Task 6).** `privacy_sweep.py` over `runs/` gives 4 hits of kind
`home`. All 4 are in `runs/T1/old/claude-opus-5-5/rep3`: `final.diff` lines 39, 79 and 123, and
`summary.json` line 131. The text is a path that the model invented in its T1 scenario. It holds the home's
parent folder and a three-letter segment after it. The segment is not the user's login. No email, local
part, name or user form hit. The sweep flags the home's parent folder by design. These 4 hits are
accepted. The scrubbed copies are kept as the rep wrote them, because a rewrite would change the
recorded rep evidence. The same sweep over `prompts-old/` and `prompts-new/` gives 0 hits.

### Probes and pilot (Task 4)

Task 4 ran the four probes and the pilot. `claude --version` printed `2.1.323 (Claude Code)` before and
after each of the eight batches (four probes, four pilot reps). The version did not change during the run.
The raw probe and pilot output is in `~/.cache/agent-skills/scratch/plan105/`. Nothing from it is
committed.

**Probes.** Each probe sent `isolation_probe.txt` once. `probe_json.sh` ran the no-tools command and
`probe_tools.sh` ran the tools command. All four runs ended with the subtype `success`.

| Probe | Model | Lines 1–6 and 8 | Line 7 | Cost (USD) |
|---|---|---|---|---|
| `probe_json.sh` | `claude-sonnet-5-5` | NO | YES | 0.0082029 |
| `probe_json.sh` | `claude-opus-5-5` | NO | YES | 0.0232418 |
| `probe_tools.sh` | `claude-sonnet-5-5` | NO | YES | 0.0081747 |
| `probe_tools.sh` | `claude-opus-5-5` | NO | YES | 0.0240054 |

- **Line 7 (the user's name or email) read YES in all four probes.** Each answer quoted the user's email
  address. This record does not copy the address. The open watch item "Account identity reaches the
  isolated micro-test runs" tracks this. Per the plan's Task 4 Step 1, a YES on line 7 does not stop the
  run.
- **Line 6 on Opus.** Both Opus probes answered NO and added a note. The note says that the context
  mentions some slash commands in passing, `/code-review` among them, and that it holds no skill list
  and no skill named writing-skills. The init record of both tools probes (Sonnet and Opus) lists no
  slash command and no skill. The Sonnet probes gave no such note. This record reads the line as NO.
- **Lines 1–5 and 8** read NO in every probe.

**Pilot.** The pilot arm is built from HEAD (`208800f95203f97b25be9954856aa8b5abaf1e6f`). `rep_tools.py
place-copy HEAD` placed 12 files of `skills/writing-skills` in `/private/tmp/wsl105-skill/`.
`build_prompts.py HEAD pilot <scratch>/prompts-pilot` wrote the six prompts. The body is 18,758
characters. HEAD still has the old layout, so the three support files sit in the skill folder's root.
`run_tool_reps.sh` ran each rep alone as a background command, with `<out-dir>` set to
`pilot-runs/<case>/pilot/<model>/` in scratch. `audit.py` then audited each rep.

| Case | Model | Cost (USD) | Turns | Tool calls | Wall (s) | Read of the moved file | First write of the target | Path audit | V9 | VOID | Read check |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | `claude-sonnet-5-5` | 0.1252769 | 7 | 6 | 34 | call 1 | call 5 | 0 hits | none | none | PASS |
| T2 | `claude-sonnet-5-5` | 0.0838596 | 7 | 6 | 17 | call 4 | call 6 | 0 hits | none | none | PASS |
| T3 | `claude-sonnet-5-5` | 0.0845620 | 6 | 5 | 16 | call 4 | call 5 | 0 hits | none | none | PASS |
| T1 | `claude-opus-5-5` | 0.2579898 | 6 | 5 | 52 | call 1 | call 5 | 0 hits | none | none | PASS |

Each rep ended with the subtype `success` and `is_error` false. Both T1 reps read
`testing-skills-with-subagents.md` before their first write of `specs/lockfile-refresh-scenarios.md`. The
pilot reps are not scored. Nobody graded their answers. After the pilot, `/private/tmp/wsl105-skill/` and
`/private/tmp/wsl105/` were empty.

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
Two self-tests hold the rule without reading the live skill. `test_no_t_domain_repeats_plan_72s_cases` reads plan 72's frozen `cases.py`.
`test_no_t_domain_repeats_the_skills_own_examples` holds a frozen list of the skill's example-domain
words (such as `condition-based`, `root-cause`, `flaky` and `React Router`), chosen once from
`SKILL.md`, `references/discovery.md` and `testing-skills-with-subagents.md`. No T case text or fixture
may hold one of them.

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

## Results

Task 6 ran the six cases on both arms: `old` is OLD and `new` is NEW (shas in Kit). Each of the 12 case
and model cells has 5 scored reps per arm. So 120 reps were scored, 60 W and 60 T. One more T rep was
void and did not count (VOID rule). Agent graders graded the 120 sheets blind (Blind grading). One
grader took each case and graded that case's 20 sheets, both arms and both models in one list, with no
access to the key. Sonnet graded W1 to W3 and Opus graded T1 to T3. The key was read only after the last
grade was in. Its read check joined each T rep's grade. The raw output, the sheets, the key and the
grades stay in `~/.cache/agent-skills/scratch/plan105/`. Nothing from there is committed.

In the per-rep tables, Cost is that rep's own `total_cost_usd`. The last column is the running total
after the rep's batch, from the Spend stop table. The 5 reps of one batch share that value. A deciding
line is the grader's short note. The T tables add two columns. Read is the stream's result for the Read
part. Use is the grader's result for the Use part. A T rep passes when both parts pass.

### Summary and verdict

Pass counts are the scored reps that passed, out of 5. A cell meets the bars (Bars) when `new` ≥ `old` − 1.
The W cells also need `new` ≥ 4/5.

| Case | Model | `old` | `new` | Bars | Result |
|---|---|---|---|---|---|
| W1 | `claude-sonnet-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 and `new` ≥ 4/5 | met |
| W1 | `claude-opus-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 and `new` ≥ 4/5 | met |
| W2 | `claude-sonnet-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 and `new` ≥ 4/5 | met |
| W2 | `claude-opus-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 and `new` ≥ 4/5 | met |
| W3 | `claude-sonnet-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 and `new` ≥ 4/5 | met |
| W3 | `claude-opus-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 and `new` ≥ 4/5 | met |
| T1 | `claude-sonnet-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 | met |
| T1 | `claude-opus-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 | met |
| T2 | `claude-sonnet-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 | met |
| T2 | `claude-opus-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 | met |
| T3 | `claude-sonnet-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 | met |
| T3 | `claude-opus-5-5` | 5/5 | 5/5 | `new` ≥ `old` − 1 | met |

Verdict: PASS

All 12 case and model cells meet the bars, so the guard passes.

### Per-rep results

Each table lists the `old` reps first, then the `new` reps, Sonnet before Opus.

#### W1

| Arm | Model | Rep | Verdict | Deciding line | Cost (USD) | Running total after batch (USD) |
|---|---|---|---|---|---|---|
| `old` | `claude-sonnet-5-5` | 1 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.0587715 | 0.7503254 |
| `old` | `claude-sonnet-5-5` | 2 | PASS | No create ACTION. First ACTION reads `discovery.md`. | 0.0116782 | 0.7503254 |
| `old` | `claude-sonnet-5-5` | 3 | PASS | No create ACTION. First ACTION reads `discovery.md`. | 0.0129442 | 0.7503254 |
| `old` | `claude-sonnet-5-5` | 4 | PASS | First ACTION reads `discovery.md`, before the later ACTION that creates `SKILL.md`. | 0.0265042 | 0.7503254 |
| `old` | `claude-sonnet-5-5` | 5 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.0251142 | 0.7503254 |
| `old` | `claude-opus-5-5` | 1 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.1121582 | 1.1670121 |
| `old` | `claude-opus-5-5` | 2 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.0543836 | 1.1670121 |
| `old` | `claude-opus-5-5` | 3 | PASS | No create ACTION. First ACTION reads `discovery.md`. | 0.0532716 | 1.1670121 |
| `old` | `claude-opus-5-5` | 4 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.0506236 | 1.1670121 |
| `old` | `claude-opus-5-5` | 5 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.0488156 | 1.1670121 |
| `new` | `claude-sonnet-5-5` | 1 | PASS | No create ACTION. First ACTION reads `discovery.md`. | 0.0454929 | 0.8477595 |
| `new` | `claude-sonnet-5-5` | 2 | PASS | No create ACTION. First ACTION reads `discovery.md`. | 0.0124863 | 0.8477595 |
| `new` | `claude-sonnet-5-5` | 3 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.0143303 | 0.8477595 |
| `new` | `claude-sonnet-5-5` | 4 | PASS | No create ACTION. First ACTION reads `discovery.md`. | 0.0116843 | 0.8477595 |
| `new` | `claude-sonnet-5-5` | 5 | PASS | No create ACTION. First ACTION reads `discovery.md`. | 0.0134403 | 0.8477595 |
| `new` | `claude-opus-5-5` | 1 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.1153702 | 1.4919575 |
| `new` | `claude-opus-5-5` | 2 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.0516758 | 1.4919575 |
| `new` | `claude-opus-5-5` | 3 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.0599838 | 1.4919575 |
| `new` | `claude-opus-5-5` | 4 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.0219118 | 1.4919575 |
| `new` | `claude-opus-5-5` | 5 | PASS | First ACTION reads `discovery.md`, before the ACTION that creates `SKILL.md`. | 0.0760038 | 1.4919575 |

#### W2

| Arm | Model | Rep | Verdict | Deciding line | Cost (USD) | Running total after batch (USD) |
|---|---|---|---|---|---|---|
| `old` | `claude-sonnet-5-5` | 1 | PASS | Third ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0383475 | 1.5783458 |
| `old` | `claude-sonnet-5-5` | 2 | PASS | Third ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0119247 | 1.5783458 |
| `old` | `claude-sonnet-5-5` | 3 | PASS | First ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0118947 | 1.5783458 |
| `old` | `claude-sonnet-5-5` | 4 | PASS | First ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0134947 | 1.5783458 |
| `old` | `claude-sonnet-5-5` | 5 | PASS | Third ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0107267 | 1.5783458 |
| `old` | `claude-opus-5-5` | 1 | PASS | First ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0791982 | 1.8308991 |
| `old` | `claude-opus-5-5` | 2 | PASS | First ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0212606 | 1.8308991 |
| `old` | `claude-opus-5-5` | 3 | PASS | First ACTION "Read `<skill>/flowcharts.md`"; later Edit only described as a step, not an ACTION. | 0.0219406 | 1.8308991 |
| `old` | `claude-opus-5-5` | 4 | PASS | First ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0241526 | 1.8308991 |
| `old` | `claude-opus-5-5` | 5 | PASS | First ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0248246 | 1.8308991 |
| `new` | `claude-sonnet-5-5` | 1 | PASS | First ACTION "Read `<skill>/flowcharts.md`"; no create or edit ACTION. | 0.0395415 | 1.6595225 |
| `new` | `claude-sonnet-5-5` | 2 | PASS | Third ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0117148 | 1.6595225 |
| `new` | `claude-sonnet-5-5` | 3 | PASS | Third ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0104748 | 1.6595225 |
| `new` | `claude-sonnet-5-5` | 4 | PASS | Third ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0085008 | 1.6595225 |
| `new` | `claude-sonnet-5-5` | 5 | PASS | Third ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0109448 | 1.6595225 |
| `new` | `claude-opus-5-5` | 1 | PASS | First ACTION "Read `<skill>/flowcharts.md`"; no create or edit ACTION. | 0.0808862 | 2.0186885 |
| `new` | `claude-opus-5-5` | 2 | PASS | First ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0231848 | 2.0186885 |
| `new` | `claude-opus-5-5` | 3 | PASS | First ACTION reads `<skill>/flowcharts.md`, before the later Edit ACTION on `SKILL.md`. | 0.0410928 | 2.0186885 |
| `new` | `claude-opus-5-5` | 4 | PASS | First ACTION reads `<skill>/flowcharts.md`; no create or edit ACTION. | 0.0223008 | 2.0186885 |
| `new` | `claude-opus-5-5` | 5 | PASS | First ACTION "Read `<skill>/flowcharts.md`"; no create or edit ACTION. | 0.0203248 | 2.0186885 |

#### W3

| Arm | Model | Rep | Verdict | Deciding line | Cost (USD) | Running total after batch (USD) |
|---|---|---|---|---|---|---|
| `old` | `claude-sonnet-5-5` | 1 | PASS | First ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0426975 | 2.1108272 |
| `old` | `claude-sonnet-5-5` | 2 | PASS | First ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0125273 | 2.1108272 |
| `old` | `claude-sonnet-5-5` | 3 | PASS | Third ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0119513 | 2.1108272 |
| `old` | `claude-sonnet-5-5` | 4 | PASS | Third ACTION reads `<skill>/bulletproofing.md`; no create or edit ACTION. | 0.0130513 | 2.1108272 |
| `old` | `claude-sonnet-5-5` | 5 | PASS | First ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0119113 | 2.1108272 |
| `old` | `claude-opus-5-5` | 1 | PASS | Reads `<skill>/bulletproofing.md` first, before the Edit of `SKILL.md`. | 0.0987062 | 2.4051977 |
| `old` | `claude-opus-5-5` | 2 | PASS | First ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0234258 | 2.4051977 |
| `old` | `claude-opus-5-5` | 3 | PASS | First ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0258058 | 2.4051977 |
| `old` | `claude-opus-5-5` | 4 | PASS | First ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0226378 | 2.4051977 |
| `old` | `claude-opus-5-5` | 5 | PASS | First ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0275858 | 2.4051977 |
| `new` | `claude-sonnet-5-5` | 1 | PASS | Third ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0444755 | 2.2070363 |
| `new` | `claude-sonnet-5-5` | 2 | PASS | Third ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0109814 | 2.2070363 |
| `new` | `claude-sonnet-5-5` | 3 | PASS | First ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0122314 | 2.2070363 |
| `new` | `claude-sonnet-5-5` | 4 | PASS | First ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0142734 | 2.2070363 |
| `new` | `claude-sonnet-5-5` | 5 | PASS | Third ACTION reads `<skill>/bulletproofing.md`; no edit ACTION. | 0.0142474 | 2.2070363 |
| `new` | `claude-opus-5-5` | 1 | PASS | Reads `<skill>/bulletproofing.md` first, before the Edit ACTIONs on `SKILL.md`. | 0.1034422 | 2.6768439 |
| `new` | `claude-opus-5-5` | 2 | PASS | Reads `<skill>/bulletproofing.md` first, before the Edit of `SKILL.md`. | 0.0428260 | 2.6768439 |
| `new` | `claude-opus-5-5` | 3 | PASS | Reads `<skill>/bulletproofing.md` first, before the Edit of `SKILL.md`. | 0.0423540 | 2.6768439 |
| `new` | `claude-opus-5-5` | 4 | PASS | Reads `<skill>/bulletproofing.md` first, before the Edit of `SKILL.md`. | 0.0351380 | 2.6768439 |
| `new` | `claude-opus-5-5` | 5 | PASS | Reads `<skill>/bulletproofing.md` first, before the Edit of `SKILL.md`. | 0.0478860 | 2.6768439 |

#### T1

| Arm | Model | Rep | Read | Use | Verdict | Deciding line | Cost (USD) | Running total after batch (USD) |
|---|---|---|---|---|---|---|---|---|
| `old` | `claude-sonnet-5-5` | 1 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered options (A-C or A-D). | 0.1298463 | 3.2913606 |
| `old` | `claude-sonnet-5-5` | 2 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered A/B/C options. | 0.1308793 | 3.2913606 |
| `old` | `claude-sonnet-5-5` | 3 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered A/B/C options; skill-root testing file path shown (grader hint mark: a path or file name that might show the layout). | 0.1115713 | 3.2913606 |
| `old` | `claude-sonnet-5-5` | 4 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered A/B/C options. | 0.1112836 | 3.2913606 |
| `old` | `claude-sonnet-5-5` | 5 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered options (A-C or A-D). | 0.1309362 | 3.2913606 |
| `old` | `claude-opus-5-5` | 1 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered A/B/C options. | 0.2847460 | 5.2559469 |
| `old` | `claude-opus-5-5` | 2 | PASS | PASS | PASS | 3 scenarios counted; all 3 prompts end with lettered A/B/C options. | 0.2691424 | 5.2559469 |
| `old` | `claude-opus-5-5` | 3 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered A/B/C options. | 0.2659496 | 5.2559469 |
| `old` | `claude-opus-5-5` | 4 | PASS | PASS | PASS | 3 scenarios counted; all 3 prompts end with lettered A/B/C options. | 0.2610296 | 5.2559469 |
| `old` | `claude-opus-5-5` | 5 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered options (A-C or A-D). | 0.2610324 | 5.2559469 |
| `new` | `claude-sonnet-5-5` | 1 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered options (A-C or A-D). | 0.1173420 | 3.9140469 |
| `new` | `claude-sonnet-5-5` | 2 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered A/B/C options. | 0.1285237 | 3.9140469 |
| `new` | `claude-sonnet-5-5` | 3 | PASS | PASS | PASS | 3 scenarios counted; 2 end with lettered A/B/C options; scenario 3 has none. | 0.1268786 | 3.9140469 |
| `new` | `claude-sonnet-5-5` | 4 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered A/B/C options. | 0.1198791 | 3.9140469 |
| `new` | `claude-sonnet-5-5` | 5 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered A/B/C options. | 0.1300629 | 3.9140469 |
| `new` | `claude-opus-5-5` | 1 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered A/B/C options. | 0.2924534 | 6.6667765 |
| `new` | `claude-opus-5-5` | 2 | PASS | PASS | PASS | 3 scenarios counted; all 3 prompts end with lettered A/B/C options. | 0.2843216 | 6.6667765 |
| `new` | `claude-opus-5-5` | 3 | PASS | PASS | PASS | 3 scenarios counted; 2 end with lettered A/B/C options; scenario 1 open-ended. | 0.2694804 | 6.6667765 |
| `new` | `claude-opus-5-5` | 4 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered A/B/C options. | 0.2909894 | 6.6667765 |
| `new` | `claude-opus-5-5` | 5 | PASS | PASS | PASS | 3 scenarios counted; all 3 end with lettered A/B/C options. | 0.2735848 | 6.6667765 |

#### T2

| Arm | Model | Rep | Read | Use | Verdict | Deciding line | Cost (USD) | Running total after batch (USD) |
|---|---|---|---|---|---|---|---|---|
| `old` | `claude-sonnet-5-5` | 1 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity, Social proof. Left out: Unity, Liking, Reciprocity. | 0.0896321 | 7.1045449 |
| `old` | `claude-sonnet-5-5` | 2 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity, Social proof. Left out: Liking, Reciprocity, Unity. | 0.0917168 | 7.1045449 |
| `old` | `claude-sonnet-5-5` | 3 | PASS | PASS | PASS | Used: Authority, Commitment, Social proof, Scarcity. Left out: Liking, Reciprocity, Unity (grader hint mark: a path or file name that might show the layout). | 0.0871258 | 7.1045449 |
| `old` | `claude-sonnet-5-5` | 4 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity, Social proof. Left out: Liking, Reciprocity, Unity. | 0.0823793 | 7.1045449 |
| `old` | `claude-sonnet-5-5` | 5 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity, Social proof. Left out: Liking, Reciprocity, Unity. | 0.0869144 | 7.1045449 |
| `old` | `claude-opus-5-5` | 1 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity. Left out: Social proof, Unity, Reciprocity, Liking. | 0.1810828 | 8.5017710 |
| `old` | `claude-opus-5-5` | 2 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity. Left out: Social proof, Unity, Liking, Reciprocity (grader hint mark: a path or file name that might show the layout). | 0.1846204 | 8.5017710 |
| `old` | `claude-opus-5-5` | 3 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity, Social proof. Left out: Liking, Reciprocity, Unity. | 0.2144406 | 8.5017710 |
| `old` | `claude-opus-5-5` | 4 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity, Social proof. Left out: Unity, Reciprocity, Liking. | 0.1882150 | 8.5017710 |
| `old` | `claude-opus-5-5` | 5 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity. Left out: Social proof, Unity, Liking, Reciprocity. | 0.1914702 | 8.5017710 |
| `new` | `claude-sonnet-5-5` | 1 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity, Social proof. Left out: Unity, Liking, Reciprocity. | 0.0849429 | 7.5419420 |
| `new` | `claude-sonnet-5-5` | 2 | PASS | PASS | PASS | Used: Authority, Commitment, Social proof, Scarcity. Left out: Liking, Reciprocity, Unity. | 0.0853504 | 7.5419420 |
| `new` | `claude-sonnet-5-5` | 3 | PASS | PASS | PASS | Used: Authority, Commitment, Social proof, Scarcity. Left out: Liking, Reciprocity, Unity. | 0.0902538 | 7.5419420 |
| `new` | `claude-sonnet-5-5` | 4 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity. Left out: Social proof, Unity, Liking, Reciprocity. | 0.0889354 | 7.5419420 |
| `new` | `claude-sonnet-5-5` | 5 | PASS | PASS | PASS | Used: Authority, Commitment, Social proof, Scarcity. Left out: Unity, Liking, Reciprocity. | 0.0879146 | 7.5419420 |
| `new` | `claude-opus-5-5` | 1 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity, Social proof. Left out: Liking, Reciprocity, Unity (grader hint mark: a path or file name that might show the layout). | 0.1827440 | 9.4313936 |
| `new` | `claude-opus-5-5` | 2 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity. Left out: Social proof, Unity, Liking, Reciprocity. | 0.1918804 | 9.4313936 |
| `new` | `claude-opus-5-5` | 3 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity, Social proof. Left out: Liking, Reciprocity, Unity. | 0.1841736 | 9.4313936 |
| `new` | `claude-opus-5-5` | 4 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity, Social proof. Left out: Liking, Reciprocity, Unity. | 0.1897428 | 9.4313936 |
| `new` | `claude-opus-5-5` | 5 | PASS | PASS | PASS | Used: Authority, Commitment, Scarcity, Social proof. Left out: Liking, Reciprocity, Unity. | 0.1810818 | 9.4313936 |

#### T3

| Arm | Model | Rep | Read | Use | Verdict | Deciding line | Cost (USD) | Running total after batch (USD) |
|---|---|---|---|---|---|---|---|---|
| `old` | `claude-sonnet-5-5` | 1 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.0872835 | 9.8403064 |
| `old` | `claude-sonnet-5-5` | 2 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.0817861 | 9.8403064 |
| `old` | `claude-sonnet-5-5` | 3 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.0858731 | 9.8403064 |
| `old` | `claude-sonnet-5-5` | 4 | FAIL (not counted) | n/a | VOID, not counted | Path audit: 1 hit. A Read of a mistyped path under `/private/tmp/wsl105/`, outside the rep folder and the skill copy. The rep read no `graphviz-conventions.dot`. Rep 6 replaced it. The folder is kept as the evidence for the void. | 0.0684638 | 9.8403064 |
| `old` | `claude-sonnet-5-5` | 5 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.0855063 | 9.8403064 |
| `old` | `claude-sonnet-5-5` | 6 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.0861007 | 9.9264071 |
| `old` | `claude-opus-5-5` | 1 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.2042804 | 11.3326548 |
| `old` | `claude-opus-5-5` | 2 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.1911142 | 11.3326548 |
| `old` | `claude-opus-5-5` | 3 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.2020108 | 11.3326548 |
| `old` | `claude-opus-5-5` | 4 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.1836588 | 11.3326548 |
| `old` | `claude-opus-5-5` | 5 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.1936134 | 11.3326548 |
| `new` | `claude-sonnet-5-5` | 1 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.0835459 | 10.3579772 |
| `new` | `claude-sonnet-5-5` | 2 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.0856114 | 10.3579772 |
| `new` | `claude-sonnet-5-5` | 3 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.0872965 | 10.3579772 |
| `new` | `claude-sonnet-5-5` | 4 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.0894832 | 10.3579772 |
| `new` | `claude-sonnet-5-5` | 5 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.0856331 | 10.3579772 |
| `new` | `claude-opus-5-5` | 1 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.1822860 | 12.2491906 |
| `new` | `claude-opus-5-5` | 2 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.1819582 | 12.2491906 |
| `new` | `claude-opus-5-5` | 3 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.1912640 | 12.2491906 |
| `new` | `claude-opus-5-5` | 4 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.1786014 | 12.2491906 |
| `new` | `claude-opus-5-5` | 5 | PASS | PASS | PASS | curl node shape=plaintext and warning node shape=octagon, both present | 0.1824262 | 12.2491906 |

The void rep's folder, `runs/T3/old/claude-sonnet-5-5/rep4/`, is kept as the evidence for the void. It
holds only scrubbed data.

### Descriptive counts

Predictions asks for these counts. For the T cases, the read and use counts are apart. A Read passes
when the stream shows a successful Read of the moved file before the first Edit or Write of the target
(Reading rule, T cases). A Use passes when the grader marks the case's marker as present. Each cell has
5 scored reps.

| Case | Model | Arm | Read passes | Use passes | Partial reads | Error reads |
|---|---|---|---|---|---|---|
| T1 | `claude-sonnet-5-5` | `old` | 5/5 | 5/5 | 0 | 0 |
| T1 | `claude-sonnet-5-5` | `new` | 5/5 | 5/5 | 0 | 0 |
| T1 | `claude-opus-5-5` | `old` | 5/5 | 5/5 | 0 | 0 |
| T1 | `claude-opus-5-5` | `new` | 5/5 | 5/5 | 0 | 0 |
| T2 | `claude-sonnet-5-5` | `old` | 5/5 | 5/5 | 0 | 0 |
| T2 | `claude-sonnet-5-5` | `new` | 5/5 | 5/5 | 0 | 0 |
| T2 | `claude-opus-5-5` | `old` | 5/5 | 5/5 | 0 | 0 |
| T2 | `claude-opus-5-5` | `new` | 5/5 | 5/5 | 0 | 0 |
| T3 | `claude-sonnet-5-5` | `old` | 5/5 | 5/5 | 0 | 0 |
| T3 | `claude-sonnet-5-5` | `new` | 5/5 | 5/5 | 0 | 0 |
| T3 | `claude-opus-5-5` | `old` | 5/5 | 5/5 | 0 | 0 |
| T3 | `claude-opus-5-5` | `new` | 5/5 | 5/5 | 0 | 0 |

- **Partial reads: 0.** No scored rep read the moved file with `offset` or `limit`.
- **Error reads: 0.** No scored rep had a Read of the moved file that returned an error. The void rep's
  Read of a mistyped path to `flowcharts.md` did return an error. It was not a Read of the moved file.
- **T1, hops.** Both arms use one hop. The moved file was read at call 1 in 19 of the 20 scored T1 reps
  and at call 2 in 1 rep (`old`, Sonnet).

The next table gives the order of the reads in T2 and T3. It comes from each rep's recorded tool calls in
its `summary.json`: tool names and paths only. "Intermediate file first" counts the reps with a
successful Read of `bulletproofing.md` (T2) or `flowcharts.md` (T3) before the first successful Read of the
moved file. "Moved file directly" counts the reps whose first successful Read of the moved file came with
no such Read before it. "Moved file not read" counts the reps with no successful Read of the moved file.
The void rep is not in these counts.

| Case | Model | Arm | Scored reps | Intermediate file first | Moved file directly | Moved file not read |
|---|---|---|---|---|---|---|
| T2 | `claude-sonnet-5-5` | `old` | 5 | 4 | 1 | 0 |
| T2 | `claude-sonnet-5-5` | `new` | 5 | 2 | 3 | 0 |
| T2 | `claude-opus-5-5` | `old` | 5 | 5 | 0 | 0 |
| T2 | `claude-opus-5-5` | `new` | 5 | 5 | 0 | 0 |
| T3 | `claude-sonnet-5-5` | `old` | 5 | 5 | 0 | 0 |
| T3 | `claude-sonnet-5-5` | `new` | 5 | 5 | 0 | 0 |
| T3 | `claude-opus-5-5` | `old` | 5 | 5 | 0 | 0 |
| T3 | `claude-opus-5-5` | `new` | 5 | 5 | 0 | 0 |

- **The `old` reps.** 19 of the 20 read the intermediate file first (T2: Sonnet 4 of 5, Opus 5 of 5. T3:
  Sonnet 5 of 5, Opus 5 of 5). One `old` rep (T2, Sonnet) read the moved file directly.
- **The `new` reps.** 17 of the 20 read the intermediate file first (T2: Sonnet 2 of 5, Opus 5 of 5. T3:
  Sonnet 5 of 5, Opus 5 of 5). Three `new` reps (T2, Sonnet) read the moved file directly.
- **What the order shows.** It shows what each rep read first, not why, and it gives no hop count. In
  the `new` layout, `SKILL.md` names the moved file itself. So a `new` rep that read the intermediate
  file first may still have found the moved file from that pointer.

### Reading of the result

120 of 120 scored reps passed. Every cell was `old` 5/5 and `new` 5/5, so every bar is met and the guard
passes. No case had a failing rep in either arm. So the run shows no loss from the move in these 12
cells. It cannot show a gain, because a layout that was neither better nor worse would also have scored
this way. T2's use part can be met from general knowledge (Predictions), so the Read part carries T2.
T3's use part can also be met without the read. The void T3 `old` rep 4
(`runs/T3/old/claude-sonnet-5-5/rep4/summary.json`, call 5) added a `shape=octagon` warning node and
never read `graphviz-conventions.dot`. So the Read part carries T3 too, and a later plan must not take
T3's use count as proof that the moved file was used. The blind-sheet diff check ran before grading,
for each of the six cases, and only the answer differed.

The graders were agents, not a person. Six independent agents graded the sheets, one per case. After the
grading, a mechanical scan of the sheets agreed with 118 of the 120 grades. The other two are W3 sheets
whose replies read `bulletproofing.md` and made no create or edit ACTION. There the scan's text match
was wrong, and the grader's PASS follows the Reading rule for W cases: a rep with no create or edit
ACTION passes when it reads the file. In the T1 and T2 tables, 4 notes carry the grader's hint mark
(3 of the 20 T2 notes and 1 of the 20 T1 notes). The mark means a path or a file name that might show the
layout. None of the four changed a grade.

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

Task 4 wrote the rows below. `claude --version` printed `2.1.323 (Claude Code)` at each point, and the
table shortens it to `2.1.323`. Task 6 adds its rows in the same columns. The running total sums the
exact `total_cost_usd` values.

| Item | `claude --version` before | `claude --version` after | Cost (USD) | Running total (USD) |
|---|---|---|---|---|
| Start, before any probe or rep | n/a | n/a | 0.00 | 0.00 |
| Probe, `probe_json.sh`, `claude-sonnet-5-5` | 2.1.323 | 2.1.323 | 0.0082029 | 0.0082029 |
| Probe, `probe_json.sh`, `claude-opus-5-5` | 2.1.323 | 2.1.323 | 0.0232418 | 0.0314447 |
| Probe, `probe_tools.sh`, `claude-sonnet-5-5` | 2.1.323 | 2.1.323 | 0.0081747 | 0.0396194 |
| Probe, `probe_tools.sh`, `claude-opus-5-5` | 2.1.323 | 2.1.323 | 0.0240054 | 0.0636248 |
| Pilot, T1, `claude-sonnet-5-5` | 2.1.323 | 2.1.323 | 0.1252769 | 0.1889017 |
| Pilot, T2, `claude-sonnet-5-5` | 2.1.323 | 2.1.323 | 0.0838596 | 0.2727613 |
| Pilot, T3, `claude-sonnet-5-5` | 2.1.323 | 2.1.323 | 0.0845620 | 0.3573233 |
| Pilot, T1, `claude-opus-5-5` | 2.1.323 | 2.1.323 | 0.2579898 | 0.6153131 |
| Scored batch, W1 `old`, `claude-sonnet-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.1350123 | 0.7503254 |
| Scored batch, W1 `new`, `claude-sonnet-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.0974341 | 0.8477595 |
| Scored batch, W1 `old`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.3192526 | 1.1670121 |
| Scored batch, W1 `new`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.3249454 | 1.4919575 |
| Scored batch, W2 `old`, `claude-sonnet-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.0863883 | 1.5783458 |
| Scored batch, W2 `new`, `claude-sonnet-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.0811767 | 1.6595225 |
| Scored batch, W2 `old`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.1713766 | 1.8308991 |
| Scored batch, W2 `new`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.1877894 | 2.0186885 |
| Scored batch, W3 `old`, `claude-sonnet-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.0921387 | 2.1108272 |
| Scored batch, W3 `new`, `claude-sonnet-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.0962091 | 2.2070363 |
| Scored batch, W3 `old`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.1981614 | 2.4051977 |
| Scored batch, W3 `new`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.2716462 | 2.6768439 |
| Scored batch, T1 `old`, `claude-sonnet-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.6145167 | 3.2913606 |
| Scored batch, T1 `new`, `claude-sonnet-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.6226863 | 3.9140469 |
| Scored batch, T1 `old`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 1.3419000 | 5.2559469 |
| Scored batch, T1 `new`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 1.4108296 | 6.6667765 |
| Scored batch, T2 `old`, `claude-sonnet-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.4377684 | 7.1045449 |
| Scored batch, T2 `new`, `claude-sonnet-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.4373971 | 7.5419420 |
| Scored batch, T2 `old`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.9598290 | 8.5017710 |
| Scored batch, T2 `new`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.9296226 | 9.4313936 |
| Scored batch, T3 `old`, `claude-sonnet-5-5`, reps 1-5 (rep 4 void: path audit) | 2.1.323 | 2.1.323 | 0.4089128 | 9.8403064 |
| Replacement, T3 `old`, `claude-sonnet-5-5`, rep 6 | 2.1.323 | 2.1.323 | 0.0861007 | 9.9264071 |
| Scored batch, T3 `new`, `claude-sonnet-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.4315701 | 10.3579772 |
| Scored batch, T3 `old`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.9746776 | 11.3326548 |
| Scored batch, T3 `new`, `claude-opus-5-5`, reps 1-5 | 2.1.323 | 2.1.323 | 0.9165358 | 12.2491906 |

**Final total: 12.2491906 USD.** The parts are 0.6153131 for the probes and the pilot, 2.0615308 for the W reps and
9.5723467 for the T reps. It is below the $14.29 projection and far below the $40 cap. The run used 4
probes, 4 pilot reps, 60 scored W reps and 60 scored T reps. It also used 1 void T rep (T3 `old`,
`claude-sonnet-5-5`, rep 4), whose cost is in its batch row. `claude --version` printed `2.1.323` at
all 50 version checks of Task 6's batches.

**Pair checks (Task 6).** Before each pair: running total + 10 × the per-rep cap ≤ $40. The W pairs use
the $0.50 cap of a no-tools rep, and the T pairs the $1.50 cap of a tools rep.

| Pair | Running total before (USD) | + 10 × cap (USD) | Check |
|---|---|---|---|
| W1, `claude-sonnet-5-5` | 0.6153131 | 5.6153131 | ≤ 40, pass |
| W1, `claude-opus-5-5` | 0.8477595 | 5.8477595 | ≤ 40, pass |
| W2, `claude-sonnet-5-5` | 1.4919575 | 6.4919575 | ≤ 40, pass |
| W2, `claude-opus-5-5` | 1.6595225 | 6.6595225 | ≤ 40, pass |
| W3, `claude-sonnet-5-5` | 2.0186885 | 7.0186885 | ≤ 40, pass |
| W3, `claude-opus-5-5` | 2.2070363 | 7.2070363 | ≤ 40, pass |
| T1, `claude-sonnet-5-5` (cap 1.50) | 2.6768439 | 17.6768439 | ≤ 40, pass |
| T1, `claude-opus-5-5` (cap 1.50) | 3.9140469 | 18.9140469 | ≤ 40, pass |
| T2, `claude-sonnet-5-5` (cap 1.50) | 6.6667765 | 21.6667765 | ≤ 40, pass |
| T2, `claude-opus-5-5` (cap 1.50) | 7.5419420 | 22.5419420 | ≤ 40, pass |
| T3, `claude-sonnet-5-5` (cap 1.50) | 9.4313936 | 24.4313936 | ≤ 40, pass |
| T3, `claude-opus-5-5` (cap 1.50) | 10.3579772 | 25.3579772 | ≤ 40, pass |

**Projection (Task 4, Step 3).** The pilot was one T rep per Sonnet case and one T1 rep on Opus.

| Term | Value (USD) |
|---|---|
| Spend so far (probes and pilot) | 0.6153131 |
| 60 W reps × 0.05 | 3.0000000 |
| 30 × the mean Sonnet T pilot cost, 30 × (0.1252769 + 0.0838596 + 0.0845620) / 3 = 30 × 0.0978995 | 2.9369850 |
| 30 × the Opus T pilot cost, 30 × 0.2579898 | 7.7396940 |
| **Projected total** | **14.2919921** |

The projection is $14.29. It is below the $35 stop, so the run may go on to Task 5 and the scored reps of
Task 6. The check before each pair in Task 6 still applies. The Opus term uses one rep, the T1 rep.

## Deviations

Items 1 to 8 were made in Task 3, before any probe or rep, and the task review ruled on each. Item 9
was made in Task 6, after the reps, and changes no rule.

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
9. **Grader agents graded the sheets** (Task 6, after the reps ran). The Kit and Blind grading sections
   say that a person grades the sheets. In Task 6, six grader agents did it, one for each case: 20
   sheets, with both arms and both models mixed, and no key. Sonnet graded W1 to W3 and Opus graded
   T1 to T3. A sheet shows no arm, so the blind rule holds. A mechanical scan of the sheets agreed
   with 118 of the 120 grades (Results, Reading of the result).
