# Synthesize-Mode Scenario Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify behaviourally, on a real critique and from sessions that never saw this repository, that `describe-critique-methodology`'s Synthesize mode has three properties once entered, and record the result. It presents one batched triage table before any spec text. It holds locator discipline in the spec it writes. It opens that spec with the derive-roadmap routing header and hands off without planning.

**Architecture:** Five scenario reps. Each is a fresh `claude -p` session rooted in its own scratch git repo, which holds a real pre-skill methodology description and its critique (alt-nfp-model's calibration pair). Each is driven through three scripted human turns with `--session-id` / `--resume`. The executor builds the kit, audits and grades. **The owner launches the sessions from a plain terminal.** A worktree-isolated Claude Code session refuses to launch `claude -p` with a prompt in another directory (verified 2026-10-03). A session rooted in this repository would also hand every rep this repository's context (micro-test isolation Channel 5). Grading combines a mechanical transcript-and-file checker (`grade.py`) with a manual rubric. A pilot rep is audited before the batch is spent.

**Tech Stack:** Claude Code CLI (`claude -p`, `--session-id`, `--resume`, `--output-format json`, `--permission-mode`, `--allowedTools`); bash; Python 3.13 stdlib for `grade.py`; git.

**Source:** `specs/deferred_items.md` § `18-methodology-pipeline-skills (plan #1, describe-critique-methodology) — 2026-07-26`, item "Synthesize mode has no scenario verification (spec Req 13, gate-deferred)". It was selected for a plan at the 2026-10-03 `/deferred` pass; there is no spec. Its unverified remainder is "locator discipline, the triage-table-before-spec-text ordering, and the derive-roadmap handoff." The behaviour under test is specified in `skills/describe-critique-methodology/SKILL.md` § Synthesize mode and `skills/describe-critique-methodology/references/spec-synthesis.md`.

## Global Constraints

- **Channel 5 — no rep may start inside this repository's context.** Every rep is a `claude -p` session that the owner launches from a plain terminal, with its working directory set to its own scratch repo. Never launch a rep from a Claude Code session, and never from a directory inside `~/Projects/agent-skills`. (memory `microtest-isolation-channels`, Channel 5: injected `CLAUDE.md` and `gitStatus` are inherited from the session, so no file quarantine can close it.)
- **Nothing a rep can read may contain the answer (Channel 3).** The rep repos hold only the two fixture files and a one-line README. The control directory (prompts, scripts, results, grader) lives outside every rep repo, under a neutral name.
- **No quarantine of this repository.** Sibling sessions use the main checkout, and a non-uniform quarantine is itself a tell (Channel 4). Contamination is handled by the pre-registered VOID rule below, never by moving files.
- **This plan edits no skill.** A behaviour that fails its pass bar is recorded and deferred. Fixing skill text is a writing-skills RED→GREEN cycle of its own.
- **Owner steps are explicit and batched.** The owner runs `run_pilot.sh` once (Task 2), `run_batch.sh` once (Task 3), and `run_rep.sh <n>` once per replacement rep (Task 3, only if reps are void). The executor runs everything else.
- Paths are fixed, and every script refers to them literally:
  - control directory: `~/.cache/ctl-q9/`
  - rep repos: `~/.cache/nfp-series/rep-1` … `rep-10`
- Fixture source files, copied byte for byte:
  - `/Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology.md`
  - `/Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology_review.md`
- The record goes to `specs/completed/synthesize-mode-verification-<YYYY-MM-DD>.md`, in the house record format of `specs/completed/red-baseline-derive-roadmap-2026-09-08.md` (Date / Status / Governs header, Fixture, Result, Decision, Qualitative evidence, Disposition).

## Pre-registration (fixed before any rep runs)

**The three turns.** These are the exact texts, also written to `~/.cache/ctl-q9/prompts/`:
- T1, the skill's own re-entry utterance from `SKILL.md` Describe step 4: `The critique is back — use describe-critique-methodology (synthesize mode) on specs/calibration_methodology_review.md`
- T2: `Thanks. On every needs-user-adjudication point, go with your recommendation, or with the critique's position where you gave none. Go ahead and finish the spec.`
- T3: `Approved — the spec looks good.`

**Behaviours and how each is scored** (per valid rep; pass/fail):
- **B1 — triage before spec text.** M1 (mechanical): the first assistant message carrying a markdown table with a verdict column comes before the first write to the new spec file in the transcript. This holds even when both happen in one turn, because a first-pass critique may leave no question to wait on. Manual:
  - R1: the rep states whether the critique was adjudicated or a first pass, above the table.
  - R2: the table covers every critique point in the coverage key (Task 1 Step 5).
  - R3: every needs-user-adjudication question is in the table's message, with none asked in a later message.
  
  B1 passes when M1, R1, R2 and R3 all hold.
- **B2 — locator discipline.** M3 (mechanical): before the Requirements section, the spec names both fixture files. Manual:
  - R4: a Design provenance paragraph declares a locator scheme. The critique has no C-numbers, so a declared custom scheme is the expected behaviour.
  - R5: every requirement carries at least one locator in that scheme.
  - R6: five locators sampled per rep each resolve to a real section or point of the fixture.
  - R7: no requirement without a locator, unless it is explicitly routed to brainstorming.
  
  B2 passes when M3 and R4–R7 all hold.
- **B3 — routing header and handoff.** Mechanical:
  - M2: the spec's first non-blank line after its title is the verbatim routing header from `spec-synthesis.md`, with whitespace normalised.
  - M4: no roadmap or plan file exists after T3.
  - M5: the final assistant message names derive-roadmap and recommends a fresh or new session.
  
  Manual R8: the rep stops after the handoff, never drafting a roadmap, stages or a plan in chat. B3 passes when M2, M4, M5 and R8 all hold.

**Pass bar:** each behaviour holds in at least 4 of 5 valid reps. Below that, the behaviour is a recorded failure.

**VOID rule.** A rep is void if its transcript shows it reading this plan's context or a worked synthesis of its own fixture:
- A tool input naming, or a tool result carrying, the full path of any of:
  - agent-skills `specs/deferred_items.md`
  - `specs/plans/`
  - `specs/completed/methodology-pipeline-skills.md`
  - `specs/completed/audit_9_2_26.md`
  - `specs/completed/red-baseline-*`
  - `specs/completed/synthesize-mode-*`
  - `.claude/`
  - anything under `~/Projects/alt-nfp-model`, `~/Projects/alt-nfp-stats*` or `~/Projects/archive/alt_nfp`
  - the control directory
- Or injected context (`attachment` / `system` records) carrying any Channel-5 marker: `32-synthesize-mode`, `synthesize-mode-verification`, `scenario verification`, `ctl-q9`.

Reading the skill's own files, and reading other `specs/completed/` exemplars, is required behaviour and never voids: `spec-synthesis.md` tells the rep to read two exemplars there. A bare directory listing that shows file names does not void. Reading or grepping the content of a listed VOID path does.

**Replacement:** void reps are replaced from rep-6 upward, up to 10 reps in total. With fewer than 5 valid reps after rep-10, stop: record the run as void and report.

---

### Task 1: Build the kit

**Files (all outside this repository):**
- Create: `~/.cache/ctl-q9/prompts/turn1.txt`, `turn2.txt`, `turn3.txt`
- Create: `~/.cache/ctl-q9/sessions/rep-1.id` … `rep-10.id`
- Create: `~/.cache/ctl-q9/run_rep.sh`, `run_pilot.sh`, `run_batch.sh`
- Create: `~/.cache/ctl-q9/grade.py`
- Create: `~/.cache/ctl-q9/coverage-key.md`
- Create: `~/.cache/nfp-series/rep-1` … `rep-10` (git repos)

**Interfaces:**
- Produces:
  - `run_rep.sh <n>` runs rep *n*'s three turns and writes `results/rep-<n>.turn{1,2,3}.json`, `rep-<n>.status.txt` and `rep-<n>.log.txt`.
  - `grade.py <n> …` prints one JSON object per rep, with keys `rep`, `void_hits`, `inherited_hits`, `exemplars_read`, `permission_denials`, `spec`, `write_turn`, `M1`, `M2`, `M3`, `M4`, `M5`, `bash_write_suspect`.
  - `grade.py --injected <n>` writes everything rep *n* was handed to `results/rep-<n>.injected.jsonl`, for the pilot audit to read in full.

- [ ] **Step 1: Write the three prompts**

```bash
mkdir -p ~/.cache/ctl-q9/prompts ~/.cache/ctl-q9/sessions ~/.cache/ctl-q9/results
printf '%s\n' 'The critique is back — use describe-critique-methodology (synthesize mode) on specs/calibration_methodology_review.md' > ~/.cache/ctl-q9/prompts/turn1.txt
printf '%s\n' "Thanks. On every needs-user-adjudication point, go with your recommendation, or with the critique's position where you gave none. Go ahead and finish the spec." > ~/.cache/ctl-q9/prompts/turn2.txt
printf '%s\n' 'Approved — the spec looks good.' > ~/.cache/ctl-q9/prompts/turn3.txt
```

- [ ] **Step 2: Build the ten rep repos and session ids**

Run once per `n` in 1–10, as a plain command each time. In a worktree-isolated session, loops of git commands may be refused; run them one by one.

```bash
mkdir -p ~/.cache/nfp-series/rep-1/specs
cp /Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology.md ~/.cache/nfp-series/rep-1/specs/
cp /Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology_review.md ~/.cache/nfp-series/rep-1/specs/
printf '%s\n' '# nfp-series' > ~/.cache/nfp-series/rep-1/README.md
git -C ~/.cache/nfp-series/rep-1 init -q
git -C ~/.cache/nfp-series/rep-1 add -A
GIT_AUTHOR_DATE='2026-09-22T06:02:00' GIT_COMMITTER_DATE='2026-09-22T06:02:00' git -C ~/.cache/nfp-series/rep-1 -c user.name='nfp-series' -c user.email='nfp-series@example.invalid' commit -q -m 'docs(specs): calibration methodology and its review'
uuidgen | tr 'A-Z' 'a-z' > ~/.cache/ctl-q9/sessions/rep-1.id
```

Verify, with plain commands:
```bash
ls ~/.cache/nfp-series | wc -l
ls ~/.cache/ctl-q9/sessions | wc -l
git -C ~/.cache/nfp-series/rep-10 log --oneline
```
Expected: `10`, `10`, and one commit line for rep-10. Then spot-check another rep the same way.

- [ ] **Step 3: Write the run scripts**

`~/.cache/ctl-q9/run_rep.sh`:

```bash
#!/usr/bin/env bash
# One rep: three turns of one fresh `claude -p` session rooted in the rep's repo.
# Run from a plain terminal, never from a Claude Code session.
set -euo pipefail
n="$1"
ctl="$HOME/.cache/ctl-q9"
repo="$HOME/.cache/nfp-series/rep-$n"
sid="$(cat "$ctl/sessions/rep-$n.id")"
tools='Read Glob Grep Skill Write Edit Bash(git:*) Bash(ls:*) Bash(cat:*) Bash(head:*) Bash(tail:*) Bash(grep:*) Bash(rg:*) Bash(find:*) Bash(wc:*)'
cd "$repo"
claude -p --session-id "$sid" --output-format json --permission-mode acceptEdits \
  --allowedTools "$tools" < "$ctl/prompts/turn1.txt" > "$ctl/results/rep-$n.turn1.json"
claude -p --resume "$sid" --output-format json --permission-mode acceptEdits \
  --allowedTools "$tools" < "$ctl/prompts/turn2.txt" > "$ctl/results/rep-$n.turn2.json"
claude -p --resume "$sid" --output-format json --permission-mode acceptEdits \
  --allowedTools "$tools" < "$ctl/prompts/turn3.txt" > "$ctl/results/rep-$n.turn3.json"
git -C "$repo" status --porcelain --untracked-files=all > "$ctl/results/rep-$n.status.txt"
git -C "$repo" log --oneline > "$ctl/results/rep-$n.log.txt"
echo "rep-$n done"
```

`~/.cache/ctl-q9/run_pilot.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
bash "$HOME/.cache/ctl-q9/run_rep.sh" 1
```

`~/.cache/ctl-q9/run_batch.sh`:

```bash
#!/usr/bin/env bash
# Reps 2-5 in parallel; each writes its own results.
set -euo pipefail
ctl="$HOME/.cache/ctl-q9"
for n in 2 3 4 5; do
  bash "$ctl/run_rep.sh" "$n" > "$ctl/results/rep-$n.runlog" 2>&1 &
done
wait
echo "batch done"
```

Then: `chmod +x ~/.cache/ctl-q9/*.sh`

- [ ] **Step 4: Write `grade.py`**

`~/.cache/ctl-q9/grade.py`:

```python
'''Mechanical checks for the synthesize-mode scenario reps.

Usage: python3 grade.py <rep-number> [<rep-number> ...]
Prints one JSON object per rep. Manual rubric items are scored separately.
'''
import json
import re
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
CTL = HOME / '.cache' / 'ctl-q9'
REPOS = HOME / '.cache' / 'nfp-series'
FIXTURE = {'specs/calibration_methodology.md', 'specs/calibration_methodology_review.md'}
HEADER = ('For agentic workers: REQUIRED NEXT SKILL: derive-roadmap — do not plan '
          'this spec directly and do not split it into per-subsystem plans.')
VOID_PATHS = (
    'Projects/agent-skills/specs/deferred_items.md',
    'Projects/agent-skills/specs/plans/',
    'Projects/agent-skills/specs/completed/methodology-pipeline-skills.md',
    'Projects/agent-skills/specs/completed/audit_9_2_26.md',
    'Projects/agent-skills/specs/completed/red-baseline-',
    'Projects/agent-skills/specs/completed/synthesize-mode-',
    'Projects/agent-skills/.claude/',
    'Projects/alt-nfp-model', 'Projects/alt-nfp-stats', 'Projects/archive/alt_nfp',
    '.cache/ctl-q9',
)
INHERITED = ('32-synthesize-mode', 'synthesize-mode-verification',
             'scenario verification', 'ctl-q9')
EXEMPLAR = re.compile(r'Projects/agent-skills/specs/completed/([^/\s"\']+\.md)')
TABLE_HEADER = re.compile(r'^\s*\|.*\bverdict\b.*\|\s*$', re.IGNORECASE | re.MULTILINE)
SESSION = re.compile(r'\b(fresh|new)\s+session\b', re.IGNORECASE)
WRITE_TOOLS = ('Write', 'Edit', 'MultiEdit')


def transcript(sid):
    hits = list((HOME / '.claude' / 'projects').glob(f'*/{sid}.jsonl'))
    if len(hits) != 1:
        raise SystemExit(f'expected one transcript for {sid}, found {len(hits)}')
    return [json.loads(line) for line in hits[0].read_text().splitlines() if line.strip()]


def items(record):
    content = (record.get('message') or {}).get('content')
    if isinstance(content, str):
        return [{'type': 'text', 'text': content}]
    return content or []


def result_text(item):
    content = item.get('content')
    if isinstance(content, list):
        return ' '.join(part.get('text', '') for part in content if isinstance(part, dict))
    return str(content or '')


def new_files(repo):
    out = subprocess.run(['git', '-C', str(repo), 'status', '--porcelain',
                          '--untracked-files=all'], capture_output=True, text=True,
                         check=True).stdout
    tracked = subprocess.run(['git', '-C', str(repo), 'ls-files'], capture_output=True,
                             text=True, check=True).stdout.split()
    changed = [line[3:] for line in out.splitlines()]
    return sorted(set(changed) | (set(tracked) - FIXTURE - {'README.md'}))


def header_ok(text):
    lines = text.splitlines()
    title = next((i for i, line in enumerate(lines) if line.startswith('# ')), None)
    if title is None:
        return False
    quote = []
    for line in lines[title + 1:]:
        if not line.strip() and not quote:
            continue
        if line.startswith('>'):
            quote.append(line.lstrip('> ').strip())
            continue
        break
    return ' '.join(' '.join(quote).split()) == HEADER


def provenance_ok(text):
    head = re.split(r'^#+ .*[Rr]equirement', text, maxsplit=1, flags=re.MULTILINE)[0]
    return ('calibration_methodology.md' in head
            and 'calibration_methodology_review.md' in head)


def grade(n):
    repo = REPOS / f'rep-{n}'
    sid = (CTL / 'sessions' / f'rep-{n}.id').read_text().strip()
    records = transcript(sid)
    prompts = [(CTL / 'prompts' / f'turn{t}.txt').read_text().strip() for t in (1, 2, 3)]
    turn, event = 0, 0
    first_table = first_write = write_turn = None
    void_hits, inherited_hits, exemplars, denials, bash_writes = [], [], set(), 0, []
    last_text = ''
    for record in records:
        kind = record.get('type')
        if kind in ('attachment', 'system'):
            blob = json.dumps(record)
            inherited_hits += [m for m in INHERITED if m in blob]
            continue
        for item in items(record):
            event += 1
            if kind == 'user' and item.get('type') == 'text':
                text = item.get('text', '').strip()
                if text in prompts:
                    turn = prompts.index(text) + 1
                else:
                    inherited_hits += [m for m in INHERITED if m in text]
            elif kind == 'user' and item.get('type') == 'tool_result':
                text = result_text(item)
                void_hits += [p for p in VOID_PATHS if p in text]
                if item.get('is_error') and 'permission' in text.lower():
                    denials += 1
            elif kind == 'assistant' and item.get('type') == 'text':
                last_text = item.get('text', '')
                if first_table is None and TABLE_HEADER.search(last_text):
                    first_table = event
            elif kind == 'assistant' and item.get('type') == 'tool_use':
                tool_input = json.dumps(item.get('input', {}))
                void_hits += [p for p in VOID_PATHS if p in tool_input]
                exemplars |= set(EXEMPLAR.findall(tool_input)) if item.get('name') == 'Read' else set()
                path = str(item.get('input', {}).get('file_path', ''))
                rel = path.split(f'rep-{n}/', 1)[-1] if f'rep-{n}/' in path else ''
                if (item.get('name') in WRITE_TOOLS and rel.startswith('specs/')
                        and rel.endswith('.md') and rel not in FIXTURE
                        and first_write is None):
                    first_write, write_turn = event, turn
                command = str(item.get('input', {}).get('command', ''))
                if item.get('name') == 'Bash' and 'specs/' in command and (
                        '>' in command or 'tee ' in command):
                    bash_writes.append(command[:200])
    files = new_files(repo)
    specs = [f for f in files if f.startswith('specs/') and f.endswith('.md')
             and 'roadmap' not in f and '/plans/' not in f]
    spec_text = (repo / specs[0]).read_text() if len(specs) == 1 else ''
    return {
        'rep': n,
        'void_hits': sorted(set(void_hits)),
        'inherited_hits': sorted(set(inherited_hits)),
        'exemplars_read': sorted(exemplars),
        'permission_denials': denials,
        'spec': specs,
        'write_turn': write_turn,
        'M1': first_table is not None and (first_write is None or first_table < first_write),
        'M2': bool(spec_text) and header_ok(spec_text),
        'M3': bool(spec_text) and provenance_ok(spec_text),
        'M4': not any('roadmap' in f or '/plans/' in f for f in files),
        'M5': 'derive-roadmap' in last_text and bool(SESSION.search(last_text)),
        'bash_write_suspect': bash_writes,
    }


def dump_injected(n):
    '''Write what the session was handed -- attachment/system records and every
    user text that is not a turn prompt -- for the pilot audit to read in full.'''
    sid = (CTL / 'sessions' / f'rep-{n}.id').read_text().strip()
    prompts = {(CTL / 'prompts' / f'turn{t}.txt').read_text().strip() for t in (1, 2, 3)}
    out = CTL / 'results' / f'rep-{n}.injected.jsonl'
    with out.open('w') as fh:
        for record in transcript(sid):
            if record.get('type') in ('attachment', 'system'):
                fh.write(json.dumps(record) + '\n')
            elif record.get('type') == 'user':
                for item in items(record):
                    if (item.get('type') == 'text'
                            and item.get('text', '').strip() not in prompts):
                        fh.write(json.dumps(item) + '\n')
    print(out)


if __name__ == '__main__':
    if sys.argv[1] == '--injected':
        dump_injected(int(sys.argv[2]))
    else:
        for arg in sys.argv[1:]:
            print(json.dumps(grade(int(arg))))
```

Smoke-test the transcript lookup before any rep has run:
Run: `python3 ~/.cache/ctl-q9/grade.py 1`
Expected: `expected one transcript for <uuid>, found 0`. That message shows the lookup is live and no rep has run yet.

- [ ] **Step 5: Write the coverage key and run the Channel 3 grep gate**

Read `~/.cache/nfp-series/rep-1/specs/calibration_methodology_review.md` in full. In `~/.cache/ctl-q9/coverage-key.md`, list every critique point in order, one line each with its location: each Key Findings bullet (KF1…), each Details section's distinct recommendation or claim (A1…, B1…, C1…, D1…), each numbered Recommendation (Rec 1…), and each Caveat that asks for a change. This is the reference R2 is scored against. Write it before any rep runs, and never change it afterwards.

Then the grep gate, against what reps can read:
```bash
grep -rlic 'derive-roadmap\|locator\|design provenance\|required next skill\|triage table\|synthesize mode\|describe-critique' ~/.cache/nfp-series/ | wc -l
```
Expected: `0`. A hit means a fixture file names a measured behaviour: inspect it and report before continuing.

- [ ] **Step 6: Checkpoint — hand the pilot to the owner**

Nothing is committed in this repository by this task. Report to the owner: "Kit ready. Please run `bash ~/.cache/ctl-q9/run_pilot.sh` from a plain terminal — not from any Claude Code session — and tell me when it prints `rep-1 done`."

---

### Task 2: Pilot audit (owner runs, executor audits)

**Files:**
- Read: `~/.cache/ctl-q9/results/rep-1.*`, rep-1's transcript under `~/.claude/projects/`

**Interfaces:**
- Consumes: `grade.py` (Task 1).
- Produces: a go/no-go for the batch, with the audit notes that Task 4 copies into the record.

- [ ] **Step 1: Owner runs the pilot**

The owner runs `bash ~/.cache/ctl-q9/run_pilot.sh` and reports `rep-1 done`. If it errors, collect `~/.cache/ctl-q9/results/rep-1.turn*.json` and stop: the mechanism, not the skill, failed.

- [ ] **Step 2: Grade the pilot mechanically**

Run: `python3 ~/.cache/ctl-q9/grade.py 1`
Expected, before reading any behavioural field:
- `inherited_hits` is `[]`.
- `void_hits` is `[]`.
- `permission_denials` is `0`, or every denial is on a command the rep then completed another way.

- [ ] **Step 3: Read what the pilot was handed**

Run: `python3 ~/.cache/ctl-q9/grade.py --injected 1`
Then read the file it prints (`~/.cache/ctl-q9/results/rep-1.injected.jsonl`) in full, not by grep alone. It holds every `attachment` and `system` record, plus every user text that is not one of the three turn prompts. The pilot passes the audit only if none of it mentions this plan, the deferred item, or the expected behaviours. The global `~/.claude/CLAUDE.md`, the skill listing and the rep repo's own git status are expected, and are not contamination.

- [ ] **Step 4: Decide**

- All of Steps 2–3 clean, and all three turns produced output: GO. rep-1 counts as the first rep, if it is not void.
- Inherited context names this plan or the item: NO-GO. Stop and report; Channel 5 has a path this plan did not foresee.
- Permission denials blocked the spec write or the commit: NO-GO. Report which tool was denied. Widening `tools=` in `run_rep.sh` is an owner decision, since it changes what every rep may run.
- rep-1 void under the VOID rule: GO. Record which path voided it and how; that path will recur.

Record the exemplars rep-1 opened (`exemplars_read`) in the audit notes.

- [ ] **Step 5: Checkpoint — hand the batch to the owner**

Report the audit and, on GO: "Please run `bash ~/.cache/ctl-q9/run_batch.sh` from a plain terminal and tell me when it prints `batch done`."

---

### Task 3: Batch and validity (owner runs, executor audits)

**Interfaces:**
- Consumes: `grade.py`, the VOID rule and the replacement rule (Pre-registration).
- Produces: a set of exactly 5 valid reps, or a void run.

- [ ] **Step 1: Owner runs the batch**

The owner runs `bash ~/.cache/ctl-q9/run_batch.sh` and reports `batch done`.

- [ ] **Step 2: Grade every rep and apply the VOID rule**

Run: `python3 ~/.cache/ctl-q9/grade.py 1 2 3 4 5`
A rep is void if `void_hits` or `inherited_hits` is non-empty. For each void rep, open its transcript at the first hit and confirm that it reads a VOID path or carries a marker. A false match, such as a bare listing, is not a void: record why.

- [ ] **Step 3: Replace void reps, if any**

For each void rep, ask the owner to run `bash ~/.cache/ctl-q9/run_rep.sh <k>` for the next unused *k* (6, 7, …), then grade it. Stop at rep-10. With fewer than 5 valid reps after rep-10, skip to Task 4 and record the run as void.

- [ ] **Step 4: Fix the valid set**

The first 5 valid reps by number are the scored set. Note the batching and every void, with its cause, for the record.

---

### Task 4: Score, record and commit

**Files:**
- Create: `specs/completed/synthesize-mode-verification-<YYYY-MM-DD>.md`

**Interfaces:**
- Consumes: the scored set and the audit notes (Tasks 2–3), `coverage-key.md` (Task 1).
- Produces: the record, and per behaviour a verdict that the Plan Completion Protocol acts on.

- [ ] **Step 1: Score the manual rubric for each scored rep**

For each rep, read its turn-1 output (`results/rep-<n>.turn1.json`, field `result`), its spec, and its turn-3 output. Score:
- R1: adjudication status stated above the table.
- R2: every coverage-key point appears in the table. List the missing ones.
- R3: needs-user-adjudication questions all in the table's message.
- R4: the provenance paragraph declares a scheme. Quote it.
- R5: every requirement carries a locator.
- R6: five sampled locators resolve. List them with where each resolves.
- R7: no locator-less requirement unless routed to brainstorming.
- R8: stops after the handoff.

Keep a verbatim quote for every fail.

The mechanical checks are heuristics, so check each false one by reading before it counts:
- M1 false: the table may sit under a header other than "Verdict".
- M2 or M3 false: `spec` may list more than one new file, or the file names may be written without `.md`.

Where reading shows the property holds, score it true and note why.

- [ ] **Step 2: Compute the verdicts**

Per rep, B1 = M1 ∧ R1 ∧ R2 ∧ R3; B2 = M3 ∧ R4 ∧ R5 ∧ R6 ∧ R7; B3 = M2 ∧ M4 ∧ M5 ∧ R8. A behaviour holds when it passes in ≥ 4 of the 5 scored reps.

- [ ] **Step 3: Write the record**

Create `specs/completed/synthesize-mode-verification-<YYYY-MM-DD>.md` with these sections:
- **Header**: Date, Status ("B1 held 5/5, B2 held 4/5, B3 failed 2/5", or "VOID"), and Governs ("whether describe-critique-methodology Synthesize mode's triage ordering, locator discipline and derive-roadmap handoff hold in practice").
- **Fixture**: the two source paths, their pre-skill shape (no C-numbers, foreign structure), and the coverage-key point count.
- **Pre-registration**: copied verbatim from this plan.
- **Dispatch**: the owner-run mechanism and why (Channel 5; the isolation-guard refusal), the batching, the model and effort the reps ran at (read from the transcripts' `message.model` and `effort` fields), and the pilot audit.
- **Validity**: every void with its cause, and the exemplars reps opened.
- **Result**: one table, with a row per scored rep and columns M1–M5, R1–R8, B1–B3, write turn and spec path.
- **Decision**: the three verdicts against the pass bar.
- **Qualitative evidence**: verbatim quotes for every failure, plus any notable behaviour the pass bar does not capture.
- **Disposition**: for each failed behaviour, the deferred item it becomes. Use the Deferred-item schema in `skills/writing-plans/references/deferred-backlog.md`, normally `Size: design` with `Done when:` a skill change verified by a writing-skills cycle.

- [ ] **Step 4: Commit**

```bash
git add specs/completed/synthesize-mode-verification-*.md
git commit -m "docs(specs): record the synthesize-mode scenario verification"
```

- [ ] **Step 5: Report**

Report the three verdicts, the void count and the record's path. Failed behaviours go to the Plan Completion Protocol's resolve-before-defer gate as leftovers. The protocol ticks the source item `→ done in plan 32` whatever the verdicts: its closure was that the behaviour be verified, and a recorded failure is a verification.
