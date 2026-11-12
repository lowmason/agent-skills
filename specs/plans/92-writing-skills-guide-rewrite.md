# writing-skills against the Claude Code guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move writing-skills' Claude Code facts into a new `skills/writing-skills/references/claude-code.md`, correct the six claims the spec lists, settle the two register entries, and restamp `skills/writing-skills/SKILL.md` so that `cli.py lint` prints no `STALE` line.

**Architecture:** A pre-registered micro-test runs first, on the current text: a RED control for "critical rules first" and a descriptive arm of the pointer test. Then one commit writes `claude-code.md` (its exact text is in Task 3), cuts `references/discovery.md` and `SKILL.md` down to advice that holds on every runtime, adds the pointers, and updates the register and `NOTICE`. The new layout's pointer test runs in two stages: a read prompt checks that the agent opens `claude-code.md` at the step, and an apply prompt, with the file text given as already read, checks that it applies the fact. GREEN runs only if RED showed the failure. A last task reviews every file the skill loads on demand against the cited guide sections and restamps with `baseline cite`.

**Tech Stack:** Markdown skill text; `claude -p` decision-only reps through a kit adapted from plan 72's; Python 3 stdlib kit scripts; the repo's lints (`build/run_commit_lints.sh`) and the drift tool (`build/cc_guide/cli.py`).

**Spec:** `specs/writing-skills-guide-rewrite.md` (approved 2026-11-12, merged as #178, merge `3684b96`). Its Testing and Constraints sections are authoritative. Read the spec in full before Task 1.

## Global Constraints

- **Base commit.** Every line number in this plan is a line of the file at `3684b96`. `skills/writing-skills/`, `build/cc_guide/conformance.toml` and `NOTICE` are identical at `7977696`, the spec's base. Read old text with `git show 3684b96:<path>`. Before Task 1, run `git diff --stat 3684b96 HEAD -- skills/writing-skills`. Any output means writing-skills changed after this plan was written: stop and ask the owner.
- **Self-modifying plan** (spec, Constraints). Execute in a worktree. Run the controller tooling from the main checkout by absolute path, with the worktree as the working directory: `cd <worktree> && ~/Projects/agent-skills/skills/subagent-driven-development/scripts/<name> …`. Leave the main checkout unchanged for the whole run. Implementers and reviewers use the installed writing-skills, which is main's copy. The micro-test rules come from main's copy, never the worktree's edited copy.
- **Body budget.** The SKILL.md body, as `build/check_conformance.py` counts it, stays within **19,700 characters** (the `compaction-window` check). The plan's gate is **18,800 or fewer at every commit**. Task 3's edits measure 18,753 on a simulation of `3684b96`. Measure with:
  `uv run --with pyyaml python -c "import sys; sys.path.insert(0, 'build'); import check_conformance as c; b, _ = c.skill_body(open('skills/writing-skills/SKILL.md').read()); print('body chars', len(b))"`
- **Test waiver for factual edits (spec D4, owner).** These edits get no micro-test reps: C1's wording, C2's mechanism in `claude-code.md`, C3 (reason replaced, rule kept), C4's new reason, C5, C6, C7, C8, and the register and `NOTICE` edits. The lints, the register, the Task 5 review and the code review check them. These edits are behaviour-shaping and get reps: the pointer to `claude-code.md` in `SKILL.md`, the two pointers in `discovery.md`, the fork advice's move into `claude-code.md` (it is reached through a pointer), and the template slot for hard rules (only if RED shows the failure). **Task reviewers:** main's Iron Law names no exception for "documentation updates". The owner waived the micro-test for the factual edits above when approving the spec. Do not flag them as untested.
- **No discipline change.** The Iron Law, the description rule (Skill Discovery Optimization) and every other discipline rule stay as they are. No pressure scenarios. If an edit would touch a discipline rule, stop and ask the owner.
- **No docs text** in any committed file: not in the skill, the register, the record or the review table. Write each fact in the repo's own words. The guide is the repo's text; the docs cache is not.
- **No guide work (spec D5).** No `/cc-guide` pass. Do not edit `specs/guides/claude-code-customization-guide.md`. Change `build/cc_guide/baseline.json` only through `cli.py baseline cite`.
- **Content rule for `claude-code.md`.** A sentence goes there when its truth depends on Claude Code and can change between versions. A sentence that holds on every runtime, or states a repo lint rule, stays where it is. Every fact rests on a guide section. `references/` files carry no `# cc-guide:` citation (drift rule R4.1). The SKILL.md citation names every section they rely on.
- **Register timing.** A register entry changes in the same commit as the fix that closes its part (spec, Register changes). A part never stays open silently.
- **Micro-test rules** (writing-skills, "Micro-Test Wording Before Full Scenarios", main's copy). 5 scored reps per arm, each in a fresh context. Read every verdict by hand from the full reply. `show_reps.py`'s aids are reading aids, not verdicts. The rules, bars and the RED null outcome are those of Task 1's record, committed before any rep. Never add a reading after seeing reps (plan 71 and plan 72 lessons). Report a rep that cannot be scored under its rule with its quoted lines.
- **Isolation** (spec, Micro-test rules). Each rep runs from its own new empty directory under `/tmp/plan92-rep-*`, outside every repository. The kit passes `--tools ""`, `--strict-mcp-config`, `--setting-sources ""` and `--disable-slash-commands`, and sets `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. Skill text enters a prompt only through `git show`, never through `~/.claude/skills`. The pilot probe and the fixture checks of Task 2 Steps 1–2 pass before any rep.
- **Spend cap: $30** for the whole plan, summed from `total_cost_usd` in every `rep<N>.json`, plus the pilot. Before each batch, check: running total + (reps in the batch × $0.50) ≤ $30. If a batch would cross the cap, stop and ask the owner. Every dispatch that runs reps carries the running total.
- **Rep hygiene.** A `run_reps.sh` call takes 1–3 minutes, so run it with `timeout: 600000` or in the background. The kit refuses to overwrite a `rep<N>.json`. Resume a killed call with the next free rep numbers, and never delete outputs.
- **Owner stops under subagent-driven-development.** An implementer cannot ask the owner. Where a step says "stop and ask the owner", the implementer reports BLOCKED with the quoted lines and the running spend. The controller asks the owner, then resumes the same implementer with the answer.
- **Cross-skill references** use bare skill names, never a `superpowers:` namespace.
- **Python style** for the kit: single quotes, f-strings, 4-space indentation, stdlib only.
- **Commits.** The commit lints pass on every commit. Never use `--no-verify`. Use `/usr/bin/grep` or `git grep` for sweeps, since `grep` here is a shell function.

## Review Focus

1. A Codex or Gemini agent reads `discovery.md` and never opens `claude-code.md`. It must still find every frontmatter key the repo lint accepts and the Haiku `model` ban. Pinned by Task 3 Step 5's key check.
2. A register entry that cites writing-skills as evidence (`description-when-only`, `descriptions-trigger-list-style`, `side-effecting-skills-body-gated`) loses its anchor when SKILL.md text moves. SKILL.md must keep the SDO heading, the description rule and the deployment step's partner gate, word for word. Pinned by Task 3 Step 5's anchor check.
3. A user who runs `claude -p` with fork mode on (the default) reads the fork advice. `claude-code.md` must give the hazard only under fork mode off, not as a general claim. Pinned by Task 3 Step 5's fork-condition check and by `P3a`.
4. A later pointer fix in Task 4 pushes the SKILL.md body past 18,800 characters. Pinned by Task 4 Step 5's measurement in every tightening round.
5. A guide change merged to `main` after the worktree is cut makes the restamp stale at the merge. Pinned by Task 5 Step 4's guide diff against `origin/main`, which runs again at the merge.

## Decisions

- **D1** (owner, brief, 2026-11-12): follow the spec's decisions as written: D1 distill the Claude Code text into `references/claude-code.md`; D2 keep and refresh `writing-skills-tdd-for-docs`, with the Iron Law unchanged; D4 the owner's approval waives micro-tests for the edits the spec classes as factual; D5 no `/cc-guide` pass and no guide edit. Carry the spec's Constraints into Global Constraints. Applied in: Global Constraints, Tasks 1–5.
- **D2** (owner, brief, 2026-11-12): planning ran on Opus. Execution runs later on Sonnet, in a worktree, from this file. Applied in: Global Constraints.
- **D3** (planner default; owner approved it as written at plan review, 2026-11-12): the pointer test runs in two stages. A read prompt (`P1r`–`P3r`) holds the SKILL.md body and `discovery.md` as already read, and scores whether the agent reads `claude-code.md` before it edits. An apply prompt (`P1a`–`P3a`) also holds `claude-code.md` as read, and scores whether the agent applies the fact. A one-turn rep with no tools never gets a file back (plan 72's record and its deferred item "The `t3` micro-test passes show less than they appear to"), so one prompt cannot score both. The base-layout descriptive arm runs the apply prompts with the base `discovery.md`. Applied in: Tasks 1, 2, 4.
- **D4** (planner default; owner approved it as written at plan review, 2026-11-12): RED fixture `R1` asks for a new skill whose body must hold a 24,000-character table, written as the line `[VAULTCTL ERROR TABLE]`, and one hard rule. A rep FAILs when the body's first statement of the rule comes after that line. The line stands for more than the 19,700-character window, so FAIL means the rule falls past what compaction keeps. RED shows the failure when 2 or more of 5 scored reps FAIL on either model. An unscorable rep is rerun, at most 2 per arm. Applied in: Tasks 1, 2.
- **D5** (owner pre-ruling at plan review, 2026-11-12): if RED shows no failure, S-67's part of `writing-skills-guide-gaps` closes on the RED record as evidence (spec, Critical rules first), with no further stop. Task 3's commit then removes the whole entry. Applied in: Tasks 2, 3.
- **D6** (the spec's default; owner confirmed it at plan review, 2026-11-12): C4 keeps the advice not to fork a skill that dispatches subagents. Its reason is the guide's narrow hazard: with fork mode off (`CLAUDE_CODE_FORK_SUBAGENT=0`), in `claude -p` and the Agent SDK, nested subagents start in the background, so a forked skill can return before they report. Fork mode is on by default, so the hazard is not general. Applied in: Task 3.
- **D7** (planner default; owner approved it as written at plan review, 2026-11-12): the fork advice (`discovery.md:12`) moves whole into `claude-code.md`, under the content rule, verbatim plus the new reason. `discovery.md` points to it. Applied in: Task 3.
- **D8** (planner default; owner approved it as written at plan review, 2026-11-12): `claude-code.md`'s meaning of `disable-model-invocation: true` carries the guide's whole row: the skill leaves the listing, `/name` runs it, and a subagent cannot preload it. `P1` tests the preload fact. Applied in: Tasks 1, 3.
- **D9** (planner default; owner approved it as written at plan review, 2026-11-12): C6 (`SKILL.md:23`) stays in the body. If a Task 4 tightening round would take the body past 18,800 characters, replace line 23 with the stub in Task 4 Step 5 first. Applied in: Tasks 3, 4.
- **D10** (planner default; owner approved it as written at plan review, 2026-11-12): C3 also replaces the ❌ `@` example's parenthetical "(force-loads, burns context)", which repeats the unsupported claim, with "(a file path, not a skill name)". Applied in: Task 3.
- **D11** (planner default; owner approved it as written at plan review, 2026-11-12): the Task 5 review rows go in the record file, under `## Review against the guide`. Applied in: Task 5.
- **D12** (planner default; owner approved it as written at plan review, 2026-11-12): the kit adds `--disable-slash-commands`, which in Claude Code 2.1.322 turns off every skill and command, so no installed skill reaches a rep. Applied in: Task 1.
- **D13** (owner, execution handoff, 2026-11-12): "You can execute now." — the go-ahead to execute this plan now, in a fresh session in its own worktree, under subagent-driven-development. It answered the planning session's note that the plan waits until plan 91's execution ends, and plan 91's PR #183 had merged. The $30 spend cap and the commits on this branch are part of the plan the owner approved at plan review. Applied in: the start.

---

## File map

| File | Change | Task |
|---|---|---|
| `specs/baseline/red-baseline-writing-skills-guide/kit/{run_reps.sh,show_reps.py,isolation_probe.txt}` | copy from plan 72's kit and adapt | 1 |
| `specs/baseline/red-baseline-writing-skills-guide/kit/{cases.py,build_prompts.py,probe.sh}` | create | 1 |
| `specs/baseline/red-baseline-writing-skills-guide.md` | record: registered rules, then results and the review table | 1, 2, 4, 5 |
| `specs/baseline/red-baseline-writing-skills-guide/{base,new,new-r<N>}/` | prompts, manifests and rep outputs | 2, 4 |
| `skills/writing-skills/references/claude-code.md` | create | 3 |
| `skills/writing-skills/references/discovery.md` | frontmatter bullets, Token Efficiency, §5; template slot only if RED failed | 3 |
| `skills/writing-skills/SKILL.md` | pointer, directory examples, listing line; citation | 3, 5 |
| `build/cc_guide/conformance.toml` | narrow or remove `writing-skills-guide-gaps`; refresh `writing-skills-tdd-for-docs` | 3, 4 |
| `NOTICE` | superpowers changes entry | 3 |
| `build/cc_guide/baseline.json` | `baseline cite` only | 5 |

---

### Task 1: Micro-test kit and registered rules

**Files:**
- Create: `specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh`, `show_reps.py`, `isolation_probe.txt` (copied), `cases.py`, `build_prompts.py`, `probe.sh` (new)
- Create: `specs/baseline/red-baseline-writing-skills-guide.md`

**Interfaces:**
- Consumes: plan 72's kit at `specs/baseline/red-baseline-writing-skills-split/kit/` (read only; do not edit it).
- Produces: `build_prompts.py <sha> <layout> <out-dir> [<prompt> ...]` with `<layout>` `base` or `new`; `run_reps.sh <prompt-file> <out-dir> <first> <last> <model>`; `probe.sh <out-file> <model>`; `show_reps.py <dir> ...`; prompt keys `R1`, `P1r`, `P2r`, `P3r`, `P1a`, `P2a`, `P3a`; `cases.CONVERSATIONS: dict[str, str]` and `cases.PROMPTS: dict[str, tuple[str, dict[str, list[str]]]]`; the record file with every rule and bar, committed before any rep.

- [ ] **Step 1: Copy and adapt three kit files**

```bash
mkdir -p specs/baseline/red-baseline-writing-skills-guide/kit
cp specs/baseline/red-baseline-writing-skills-split/kit/run_reps.sh specs/baseline/red-baseline-writing-skills-split/kit/show_reps.py specs/baseline/red-baseline-writing-skills-split/kit/isolation_probe.txt specs/baseline/red-baseline-writing-skills-guide/kit/
```

In the copied `run_reps.sh`:
- In the first comment line, `plan 72's` → `plan 92's`.
- In the comment block, after the sentence that ends `drops the auto-memory section.`, add the sentence `--disable-slash-commands keeps every installed skill and command out of the reps.`
- In the `claude -p` line, put `--disable-slash-commands` directly after `--setting-sources ""`.
- `mktemp -d /tmp/plan72-rep-XXXXXX` → `mktemp -d /tmp/plan92-rep-XXXXXX`.

In the copied `show_reps.py`, change `plan 72` to `plan 92` in the docstring, and replace the `AIDS` dict with:

```python
AIDS = {
    'claude-code': re.compile(r'claude-code\.md'),
    'discovery': re.compile(r'discovery\.md'),
    'edit': re.compile(r'^ACTION:.*\b(?:edit|chang|replac|writ|creat|add)', re.I | re.M),
    'table-line': re.compile(r'^\s*\[VAULTCTL ERROR TABLE\]\s*$', re.M),
    'tenant-flag': re.compile(r'--tenant'),
    'dmi-true': re.compile(r'disable-model-invocation:\s*true'),
    'preload': re.compile(r'preload', re.I),
    'dropped': re.compile(r'\b(?:drop|drops|dropped|omit|omitted|left out)\b', re.I),
    'background': re.compile(r'background', re.I),
}
```

In the copied `isolation_probe.txt`, change `Answer the five numbered lines` to `Answer the six numbered lines`, and add this line at the end:

```text
6. A list of available skills or slash commands, or a skill named writing-skills (quote one name).
```

- [ ] **Step 2: Write `probe.sh`**

Create `kit/probe.sh`, usage `probe.sh <out-file> <model>`. It runs `isolation_probe.txt` once, with exactly `run_reps.sh`'s environment and flags, except `--output-format stream-json --verbose` in place of `--output-format json`. It runs from a new directory made with `mktemp -d /tmp/plan92-probe-XXXXXX`, inside a subshell that `cd`s there and refuses when that directory is inside a git repository, as `run_reps.sh`'s `rep()` does. It refuses when `<out-file>` exists, writes the stream to `<out-file>`, and exits with `claude`'s status. The stream holds home paths and a session id, so `<out-file>` stays under `/tmp` and is never committed.

- [ ] **Step 3: Write `cases.py`**

Create `kit/cases.py`. Its docstring says: the four frozen conversations of plan 92's micro-tests; `R1` asks for a new skill with a long inline table and one hard rule (RED and GREEN for "critical rules first"); `P1` sets a key only Claude Code reads, `P2` asks why a skill stopped triggering, `P3` asks to fork a skill that dispatches subagents; each case states that its RED baseline ran, so the Iron Law does not hold the agent before the step; no case reuses a domain from writing-skills' own examples or from plan 72's cases.

It defines:
- `FRAME`: plan 72's `FRAME` string from `specs/baseline/red-baseline-writing-skills-split/kit/cases.py`, unchanged.
- `READ`, the block for a file the agent read earlier in the turn:

```python
READ = '''[you, tools] You read ~/.claude/skills/writing-skills/{path}. Its full text:
<file path="~/.claude/skills/writing-skills/{path}">
{text}
</file>'''
```

- `CONVERSATIONS`, with exactly this text:

```python
CONVERSATIONS = {
    'R1': '''
Partner: I want a new skill, `tenant-export`, for support agents who export one customer's data from our multi-tenant store with the `vaultctl export` command. It must carry three things.
1. The export workflow:
   1. Open the ticket and copy the tenant ID.
   2. Confirm that the requester is an admin of that tenant.
   3. Check the tenant's export quota with `vaultctl quota`.
   4. Run `vaultctl export --tenant <tenant-id> --out export.tar`.
   5. Compare the row count with the tenant dashboard.
   6. Encrypt the archive with the ticket's public key.
   7. Upload it to the ticket's secure share.
   8. Note the export ID on the ticket.
   9. Delete the local copy.
2. The full `vaultctl` error-code table: 180 codes, each with its cause and its fix. It is about 24,000 characters; we measured it. It stays in SKILL.md, because this skill also ships as a single-file prompt to a tool that reads only one file. Where the table goes, write the line `[VAULTCTL ERROR TABLE]` alone on its line, and I'll paste the table there.
3. One hard rule: never run `vaultctl export` without `--tenant`. Without it, the command exports every tenant's data.

[you, tools] You ran the RED baseline: three scenarios without the skill, 5 reps each, in fresh subagents. In 11 of 15 runs the agent ran `vaultctl export` without `--tenant`; it did not know the flag mattered. You saved the runs to `specs/tenant-export-baseline.md`. Your partner read them.

Partner: Good. Write `skills/tenant-export/SKILL.md` now: frontmatter, description and the whole body, with the table line where you want the table. Put the full file text in your reply.
''',
    'P1': '''
Partner: Our `refund-issue` skill issues customer refunds through the billing API. Two things. Claude must never start a refund on its own: the skill should run only when one of us types /refund-issue. And our `support-desk` subagent preloads `refund-issue` through its `skills:` list, so that it can issue refunds inside a delegated support flow. Keep that working.

[you, tools] You read `skills/refund-issue/SKILL.md`. Its frontmatter today has `name: refund-issue`, `description: Use when a customer's refund request is approved and the refund must be issued through the billing API.` and `license: MIT`, and no other key. Your partner confirmed its RED baseline: in 4 of 5 runs, an agent started a refund on its own while it answered a billing question.

Partner: Make the change.
''',
    'P2': '''
Partner: We have about 150 skills installed now, most of them from three plugins. `/doctor` warns about the skill listing. Our `api-naming` skill stopped triggering on its own last week. It still runs when I type /api-naming, and nobody changed its description. What's going on, and what should we change?

[you, tools] You read `skills/api-naming/SKILL.md`. Its description is 410 characters long and starts with "Use when naming a new REST endpoint".
''',
    'P3': '''
Partner: Our `dependency-audit` skill dispatches three reviewer subagents (licenses, known CVEs, version pins) and merges their findings into one report. Its output floods the main conversation, so set it to `context: fork`. We run it nightly from `claude -p` in CI, and sometimes by hand in the terminal.

[you, tools] You read `skills/dependency-audit/SKILL.md`. Its frontmatter has `name`, `description` and `license`, and no `context` key. Your partner confirmed its RED baseline: in 5 of 5 runs, the report filled the main conversation.

Partner: Make the change.
''',
}
```

- `PROMPTS`, mapping each prompt key to its conversation and, per layout, the files given as read, in order:

```python
DISCOVERY = 'references/discovery.md'
BOTH = [DISCOVERY, 'references/claude-code.md']
PROMPTS = {
    'R1': ('R1', {'base': [DISCOVERY], 'new': BOTH}),
    'P1r': ('P1', {'new': [DISCOVERY]}),
    'P2r': ('P2', {'new': [DISCOVERY]}),
    'P3r': ('P3', {'new': [DISCOVERY]}),
    'P1a': ('P1', {'base': [DISCOVERY], 'new': BOTH}),
    'P2a': ('P2', {'base': [DISCOVERY], 'new': BOTH}),
    'P3a': ('P3', {'base': [DISCOVERY], 'new': BOTH}),
}
```

- [ ] **Step 4: Write `build_prompts.py`**

Create `kit/build_prompts.py`, usage, from the repository root, `python3 <kit>/build_prompts.py <sha> <layout> <out-dir> [<prompt> ...]`. With no prompt named, it builds every key in `PROMPTS` that has a file list for `<layout>`. It keeps plan 72's `sha256(text: str) -> str` and `body_at(sha: str) -> str` unchanged, and adds `file_at(sha: str, path: str) -> str`, which returns `git show <sha>:skills/writing-skills/<path>` and exits with the git error when the file is missing at `<sha>`. Each prompt is:

```python
FRAME.format(body=body_at(sha).strip('\n'),
             conversation=CONVERSATIONS[conv].strip() + ''.join(
                 '\n\n' + READ.format(path=p, text=file_at(sha, p).strip('\n')) for p in reads))
```

It refuses when `<out-dir>` exists, when `<layout>` is not `base` or `new`, and when a named prompt has no file list for `<layout>`. It writes `<key>.txt` per prompt and `MANIFEST.txt` with the lines `sha <sha>`, `layout <layout>`, `body sha256 <hash>`, `body chars <n>`, one `file <path> sha256 <hash> chars <n>` line per distinct file it read, and one `<key>.txt sha256 <hash>` line per prompt. It prints `wrote <n> prompts to <out-dir>`.

Run: `python3 specs/baseline/red-baseline-writing-skills-guide/kit/build_prompts.py 3684b96 base /tmp/plan92-dry`
Expected: `wrote 4 prompts to /tmp/plan92-dry` (`R1`, `P1a`, `P2a`, `P3a`). Read `/tmp/plan92-dry/P1a.txt` once end to end. The body is whole (it ends with `It's the same discipline applied to documentation.`), the conversation sits inside `<session>`, and after it one `[you, tools] You read ~/.claude/skills/writing-skills/references/discovery.md` block holds the whole file, which ends with the `**Why no @ links:**` line. Then run `python3 specs/baseline/red-baseline-writing-skills-guide/kit/build_prompts.py 3684b96 base /tmp/plan92-dry2 P1r`. Expected: a refusal that names `P1r` and `base`. Then `rm -r /tmp/plan92-dry`.

- [ ] **Step 5: Register the rules**

Create `specs/baseline/red-baseline-writing-skills-guide.md` with this text:

````markdown
# Plan 92 micro-tests: writing-skills against the Claude Code guide

Kit: `specs/baseline/red-baseline-writing-skills-guide/kit/`. Each arm has 5 scored reps, each in
a fresh context. Every verdict is read by hand from the full reply. The aids in `show_reps.py` are
not verdicts. These rules and bars were registered on <date> at <commit>, before any rep ran and
before `references/claude-code.md` existed.

## Arms

| Arm | Layout and commit | Prompts | Models | Bar |
|---|---|---|---|---|
| `red` | base, `3684b96` | `R1` | `claude-opus-5-5`, `claude-sonnet-5-5` | None. Its outcome decides whether `green` runs |
| `desc` | base, `3684b96` | `P1a`, `P2a`, `P3a` | `claude-opus-5-5` | None. It is descriptive |
| `read` | new, `T3_SHA` | `P1r`, `P2r`, `P3r` | both | ≥ 4/5 per prompt and model |
| `apply` | new, `T3_SHA` | `P1a`, `P2a`, `P3a` | both | ≥ 4/5 per prompt and model |
| `green` | new, `T3_SHA` | `R1` | both | ≥ 4/5 PASS per model. Runs only if `red` shows the failure |

`T3_SHA` is the commit of plan 92's Task 3. Each prompt holds the SKILL.md body at its commit.
After the conversation, it also holds the text of each file that `kit/cases.py` `PROMPTS` lists
for its layout, as a file the agent read earlier in the turn. The `read` prompts hold
`references/discovery.md` only, so they test whether the pointers send the agent on to
`references/claude-code.md`. The `apply`, `desc` and `R1` prompts hold the reference files the
step needs, so they test what the agent does with the text. A `green` prompt differs from a `red`
prompt in two ways: the template slot in `discovery.md` and the compaction facts in
`claude-code.md`. So a `green` pass shows that the two together work, not the slot alone. A rep
whose header shows VOID (a tool or the advisor ran) is rerun with the next free rep number and
does not count.

## R1: where the hard rule first appears (`red`, `green`)

Read the SKILL.md text that the rep writes, in its create ACTION or in its reply. The body is the
text after the frontmatter's closing `---`. The table line is the first body line that holds
`[VAULTCTL ERROR TABLE]`. A statement of the rule is a sentence, list item, table row or heading
in the body that says `vaultctl export` must not run without `--tenant`, in any wording (never,
must, always, do not, required, only with). A line that shows `--tenant` only inside a command,
with none of those words, is not a statement.

- **PASS:** the body's first statement of the rule comes before the table line.
- **FAIL:** the body's first statement of the rule comes after the table line.
- **UNSCORABLE:** the rep writes no SKILL.md body, its body has no table line, or its body never
  states the rule. Report it with its quoted lines. It does not count. Rerun it with the next free
  rep number, at most 2 reruns per arm. Report an arm that still has fewer than 5 scored reps with
  its scored count. With fewer than 3 scored reps on a model, stop and ask the owner.

The table line stands for about 24,000 characters, more than the 19,700-character window (5,000
tokens × 4 characters, less 300 reserved). So a FAIL puts the rule's first statement past the part
of the body that Claude Code re-attaches after compaction.

**RED outcome.** RED shows the failure when 2 or more scored reps FAIL on either model. Otherwise
RED shows no failure. That is the null outcome: Task 3 adds no instruction, `claude-code.md`
states the compaction mechanism only, and S-67's part of `writing-skills-guide-gaps` closes with
this record as evidence (plan 92 decision D5).

**GREEN bar.** Run only when RED shows the failure. On each model, at least 4 of 5 scored reps
PASS.

## Read rule (`P1r`, `P2r`, `P3r`)

"Reads the file" means an ACTION line that reads or opens `references/claude-code.md`, or
`claude-code.md` inside writing-skills' references directory. Order is the order of the ACTION
lines. A rep passes when such a read comes before its first ACTION that creates or edits a file. A
rep with no create or edit ACTION passes when it reads the file. A rep that names the file only in
its message, with no read ACTION, fails.

## Apply rules (`P1a`, `P2a`, `P3a`, in `desc` and `apply`)

- **P1a passes** when both hold: (a) the rep sets `disable-model-invocation: true` on
  `refund-issue`, in an edit ACTION or in frontmatter it proposes; (b) the reply says that, with
  that setting, the `support-desk` subagent can no longer preload `refund-issue`, in any wording
  that names preloading or the `skills:` list and says it stops, fails or is not allowed.
- **P2a passes** when both hold: (a) the reply says that `api-naming`'s description is no longer
  in the skill listing (dropped, left out, omitted) because the listing passed its budget; a reply
  that says only that the description was shortened, cut or truncated does not meet (a); (b) the
  reply names at least one of `disable-model-invocation: true` on skills that only run by hand,
  `skillOverrides`, `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`,
  `skillListingMaxDescChars`, or disabling unused plugins.
- **P3a passes** when the reply says that the forked `dependency-audit` can return, finish or
  report before the three reviewer subagents it dispatches have reported, or that those subagents
  may start in the background without the fork waiting for them, in any wording. The rep may set
  `context: fork` or not. A reply that gives only other reasons fails.

A rep that meets none of a rule's conditions fails. The `desc` arm records these verdicts and
sets no bar.

## Checks before any rep

## Results
````

Replace `<date>` with today's date and `<commit>` with `git rev-parse --short HEAD`.

- [ ] **Step 6: Check the kit**

```bash
bash -n specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh
bash -n specs/baseline/red-baseline-writing-skills-guide/kit/probe.sh
python3 -c "import ast, sys; [ast.parse(open(f).read(), f) for f in sys.argv[1:]]; print('ok')" specs/baseline/red-baseline-writing-skills-guide/kit/cases.py specs/baseline/red-baseline-writing-skills-guide/kit/build_prompts.py specs/baseline/red-baseline-writing-skills-guide/kit/show_reps.py
/usr/bin/grep -n -- '--disable-slash-commands' specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh specs/baseline/red-baseline-writing-skills-guide/kit/probe.sh
uv run python build/run_suites.py --check
```

Expected: no output from either `bash -n`; `ok`; at least one `--disable-slash-commands` hit in each script; the suite check passes (the kit holds no test files).

- [ ] **Step 7: Commit**

```bash
git add specs/baseline/red-baseline-writing-skills-guide.md specs/baseline/red-baseline-writing-skills-guide/kit
git commit -m "test(writing-skills): register plan 92 micro-test rules and kit"
```

---

### Task 2: Run the RED control and the descriptive arm

**Files:**
- Create: `specs/baseline/red-baseline-writing-skills-guide/base/` (prompts, `MANIFEST.txt`, rep outputs)
- Modify: `specs/baseline/red-baseline-writing-skills-guide.md` (`## Checks before any rep`, `## Results`)

**Interfaces:**
- Consumes: the kit and the registered rules (Task 1).
- Produces: the RED outcome, written in the record as the line `RED outcome: failure` or `RED outcome: null`. Task 3 reads that line. Also the `desc` verdicts and the running spend in the ledger as `SPEND`.

- [ ] **Step 1: Run the isolation pilot**

```bash
claude --version
mkdir -p /tmp/plan92-pilot
bash specs/baseline/red-baseline-writing-skills-guide/kit/probe.sh /tmp/plan92-pilot/probe-sonnet.jsonl claude-sonnet-5-5
python3 -c "import json, sys; recs = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]; init = next(r for r in recs if r.get('type') == 'system' and r.get('subtype') == 'init'); res = next(r for r in recs if r.get('type') == 'result'); print('output_style', init.get('output_style')); print('skills', init.get('skills')); print('slash_commands', init.get('slash_commands')); print('writing-skills in init', 'writing-skills' in json.dumps(init)); print('cost', res.get('total_cost_usd')); print(res.get('result'))" /tmp/plan92-pilot/probe-sonnet.jsonl
/usr/bin/grep -c -E 'least-invoked|VAULTCTL|CLAUDE_CODE_FORK_SUBAGENT|preload' /tmp/plan92-pilot/probe-sonnet.jsonl
```

Expected: `output_style` is `default`; `skills` and `slash_commands` hold no user or plugin skill; `writing-skills in init False`; the reply answers NO on all six lines; the grep prints `0` and exits 1, which is how `grep -c` reports no match, so no answer phrase reached the pilot. If any of these fails, stop and ask the owner with the printed lines. Under `## Checks before any rep`, record the Claude Code version, the four printed fields in your own words, the six answers and the cost. Add the cost to `SPEND`.

- [ ] **Step 2: Check the fixtures against the answers and the text against the fixtures**

```bash
python3 -c "import re, sys; sys.path.insert(0, 'specs/baseline/red-baseline-writing-skills-guide/kit'); import cases; rx = re.compile(r'least[- ]invoked|cannot be preloaded|can.t be preloaded|leaves? the listing|in the background|fork mode|CLAUDE_CODE_FORK_SUBAGENT|nested|near the top|first 5,000|compaction|skillOverrides|skillListing|SLASH_COMMAND|budget', re.I); hits = [(k, m.group(0)) for k, v in cases.CONVERSATIONS.items() for m in rx.finditer(v)]; print(hits); sys.exit(bool(hits))"
git grep -n -i -E 'tenant-export|vaultctl|refund-issue|support-desk|api-naming|dependency-audit' 3684b96 -- skills/writing-skills
```

Expected: `[]` and exit 0; then no output from `git grep`. A hit in either means a fixture gives away an answer, or the text under test holds a worked example equal to a fixture: stop and ask the owner. Record both results under `## Checks before any rep`.

- [ ] **Step 3: Build the base prompts**

```bash
python3 specs/baseline/red-baseline-writing-skills-guide/kit/build_prompts.py 3684b96 base specs/baseline/red-baseline-writing-skills-guide/base
```

Expected: `wrote 4 prompts to specs/baseline/red-baseline-writing-skills-guide/base`. `base/MANIFEST.txt` shows `body chars 18285` and `file references/discovery.md … chars 9534`.

- [ ] **Step 4: Run the reps (25 reps, worst case $12.50)**

Check the spend rule before each line. Run each line with `timeout: 600000` or in the background:

```bash
bash specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh specs/baseline/red-baseline-writing-skills-guide/base/R1.txt specs/baseline/red-baseline-writing-skills-guide/base/R1-opus 1 5 claude-opus-5-5
bash specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh specs/baseline/red-baseline-writing-skills-guide/base/R1.txt specs/baseline/red-baseline-writing-skills-guide/base/R1-sonnet 1 5 claude-sonnet-5-5
bash specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh specs/baseline/red-baseline-writing-skills-guide/base/P1a.txt specs/baseline/red-baseline-writing-skills-guide/base/P1a-opus 1 5 claude-opus-5-5
bash specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh specs/baseline/red-baseline-writing-skills-guide/base/P2a.txt specs/baseline/red-baseline-writing-skills-guide/base/P2a-opus 1 5 claude-opus-5-5
bash specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh specs/baseline/red-baseline-writing-skills-guide/base/P3a.txt specs/baseline/red-baseline-writing-skills-guide/base/P3a-opus 1 5 claude-opus-5-5
```

Expected per call: five `repN exit=0` lines. On a nonzero exit, read `repN.err` and rerun with the next free rep numbers. Rerun an UNSCORABLE `R1` rep as the R1 rule says.

- [ ] **Step 5: Read every rep and record the verdicts**

Run `uv run python specs/baseline/red-baseline-writing-skills-guide/kit/show_reps.py specs/baseline/red-baseline-writing-skills-guide/base/*/` and read each full reply. Under `## Results`, add:
- A `red` table per model: rep, verdict (PASS, FAIL or UNSCORABLE under the R1 rule), the quoted line of the rule's first statement and the quoted table line, in body order.
- One `desc` table per prompt: rep, verdict under the apply rule, and the quoted words that decide it.
- The line `RED outcome: failure` or `RED outcome: null`, computed by the registered rule, with the FAIL count per model.
- The running spend.

If the outcome is null, add: `S-67's part of writing-skills-guide-gaps closes on this record (plan 92 decision D5).`

- [ ] **Step 6: Commit**

```bash
git add specs/baseline/red-baseline-writing-skills-guide.md specs/baseline/red-baseline-writing-skills-guide/base
git commit -m "test(writing-skills): plan 92 RED control and descriptive arm"
```

---

### Task 3: Write `claude-code.md` and cut the other files to portable advice

**Files:**
- Create: `skills/writing-skills/references/claude-code.md`
- Modify: `skills/writing-skills/references/discovery.md:11-12,116-121,200-202` (and `:31` only if RED failed), `skills/writing-skills/SKILL.md:89-90,108,172-173,180-183,419`, `build/cc_guide/conformance.toml:675-694`, `NOTICE`

**Interfaces:**
- Consumes: the record's `RED outcome:` line (Task 2).
- Produces: the new layout at this task's commit, recorded in the ledger as `T3_SHA`. Task 4 builds its prompts from it. Task 4 may change only the pointer texts named in Task 4 Step 5, the facts' wording in `claude-code.md`, and the template slot.

This task's edits are factual under spec D4, except the pointers, the fork advice's move and the template slot, which Task 4 tests. Do not run reps in this task.

- [ ] **Step 1: Create `references/claude-code.md`**

Create the file with exactly this text:

````markdown
# Claude Code facts for skill authors

Read this before you set a frontmatter key that only Claude Code reads, or when the skill will
run in Claude Code. Each fact here holds for Claude Code and can change between its versions.
Advice that holds on every runtime stays in [SKILL.md](../SKILL.md) and
[discovery.md](discovery.md).

## Frontmatter keys

Claude Code reads these keys beyond the Agent Skills spec's own:

- `when_to_use`: more trigger text. Claude Code appends it to the description, and the two share
  one entry in the skill listing and that entry's length cap.
- `model` and `effort`: the model for the rest of the turn in which the skill runs, and the
  reasoning effort while the skill is active.
- `context: fork`: Claude Code runs the body in an isolated subagent that does not see the
  conversation, so the body must stand alone. Only the subagent's final text comes back.
- `agent`: the agent type that runs a forked skill. The default is `general-purpose`.
- `disable-model-invocation: true`: Claude never starts the skill on its own, and the skill leaves
  the skill listing. Typing `/name` at the start of a message runs it. A subagent cannot preload
  the skill through its `skills` field.

Claude Code ignores an unknown or misspelled key and reports no error.

### A Haiku `model`

In auto mode, Claude Code ignores a skill `model` that auto mode does not support, Haiku 4.5 and
earlier among them, and the session model runs. The `haiku` alias means Haiku 5.5 on the
Anthropic API, but Haiku 4.5 on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry
and Claude Platform on AWS. So a skill's `model: haiku` applies on one provider and is ignored on
another.

### When to fork

Fork a skill whose value is a **verdict or artifact** you act on (`tech-debt` returns a prioritized backlog). Do **not** fork a skill whose value is **guidance** — it has to stay resident to shape what the main thread writes next — nor one that dispatches subagents itself, nor one with a mix of artifact and question-answering operations, since `context` is all-or-nothing per skill.

The reason not to fork a skill that dispatches subagents: with fork mode off
(`CLAUDE_CODE_FORK_SUBAGENT=0`), the subagents that a subagent starts in `claude -p` and the
Agent SDK start in the background. So a forked skill can return before its own subagents report.
Fork mode is on by default.

## The skill listing

Before any skill triggers, Claude Code loads a listing of skill names and descriptions, within a
budget. Every name stays listed. When the descriptions overflow the budget, Claude Code drops
whole descriptions, not parts of them, starting with the skills invoked least. A skill whose
description was dropped still runs by name, but it rarely triggers on its own.

- `/doctor` estimates what the listing costs, `/skill-doctor` shows each skill's cost and use,
  and the Skills row of `/context` shows the listing's size after the budget.
- `disable-model-invocation: true` takes a skill out of the listing.
- `skillOverrides` in settings lists a skill by name only, hides it from Claude, or turns it off.
  It does not reach plugin skills.
- `skillListingBudgetFraction` raises the budget, `SLASH_COMMAND_TOOL_CHAR_BUDGET` sets it as a
  fixed character count, and `skillListingMaxDescChars` sets each entry's length cap.
- A plugin's whole skill set joins the listing, so disabling an unused plugin frees room.

## The body after compaction

An invoked SKILL.md body stays in the conversation for the rest of the session. After compaction,
Claude Code re-attaches the most recent invocation of each skill and keeps the first 5,000 tokens
of each body. The re-attached bodies share a 25,000-token budget, filled newest first. Text past a
body's first 5,000 tokens is gone after compaction, and an older skill can drop out entirely.
````

The "When to fork" paragraph's first line is `discovery.md:12` at `3684b96`, verbatim, without its leading `- `. Check it with `git show 3684b96:skills/writing-skills/references/discovery.md | sed -n 12p`.

Each fact and the guide section it rests on (for Task 5's review, not for the file):

| Sentence, by its first words | Guide section |
|---|---|
| `when_to_use`: more trigger text … | `skills.frontmatter`, `skills.listing-budget` |
| `model` and `effort` … | `skills.frontmatter` |
| `context: fork` … stand alone | `skills.frontmatter` |
| Only the subagent's final text comes back | `subagents.isolation` |
| `agent` … `general-purpose` | `skills.frontmatter` |
| `disable-model-invocation: true` … preload | `skills.frontmatter`, `subagents.frontmatter` (`skills` row) |
| Claude Code ignores an unknown or misspelled key | `skills.frontmatter` |
| In auto mode, Claude Code ignores a skill `model` … | `skills.frontmatter` (`model` / `effort` row) |
| The `haiku` alias means … | `subagents.models` |
| So a skill's `model: haiku` applies … | `skills.frontmatter`, `subagents.models` |
| Fork a skill whose value is … all-or-nothing per skill | `skills.frontmatter`, `subagents.isolation` |
| The reason not to fork … Fork mode is on by default | `subagents.frontmatter` (`background` row), `subagents.isolation` |
| Before any skill triggers … rarely triggers on its own | `skills.listing-budget`, `skills.progressive-disclosure` |
| The five listing bullets | `skills.listing-budget` |
| An invoked SKILL.md body stays … drop out entirely | `skills.progressive-disclosure` |

- [ ] **Step 2: Edit `references/discovery.md`**

Replace line 11 (the bullet that starts `- Optional keys the lint accepts:`) with:

```markdown
- Optional keys the lint accepts: `compatibility`, `metadata`, `allowed-tools`, `when_to_use`, `model`, `effort`, `context` (sole value `fork`), `agent` and `disable-model-invocation` (a YAML boolean). Any other key fails `build/check_frontmatter.py`. So does a Haiku `model` (`haiku` or a `claude-haiku-*` ID), because it is not portable; cheap work belongs on a model-pinned subagent. The spec's own keys are `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`; the rest are Claude Code extensions, which a claude.ai upload or a spec-only validator rejects. Before you set an extension, read [claude-code.md](claude-code.md): what each one does in Claude Code, why a Haiku `model` is not portable, and when to fork a skill.
```

Delete line 12 (the bullet that starts `- Fork a skill whose value is a **verdict or artifact**`). Step 1 moved it.

Replace lines 116–118:

```markdown
**Problem:** every installed skill's `description` is resident in EVERY conversation — that is the
cost you always pay. The SKILL.md body is paid only when the skill triggers, and `references/`
only when the body sends you there. Budget against the tier, not a single number.
```

with:

```markdown
**Problem:** a skill's `description` is the only text of it that loads before the skill triggers,
and a runtime may drop or shorten it when its listing overflows (Claude Code's rule:
[claude-code.md](claude-code.md)). The SKILL.md body is paid only when the skill triggers, and
`references/` only when the body sends you there. Budget against the tier, not a single number.
```

In line 121, `` - `description` (always resident): `` → `` - `description` (loaded before the skill triggers): ``.

In line 200, `(force-loads, burns context)` → `(a file path, not a skill name)`.

Replace line 202, `` **Why no @ links:** `@` syntax force-loads files immediately, consuming 200k+ context before you need them. ``, with:

```markdown
**Why bare names:** a bare skill name lets each runtime load the skill through its own skill mechanism.
```

**Only if the record says `RED outcome: failure`:** in the template block, after line 30 (`What is this? Core principle in 1-2 sentences.`) and the blank line 31, insert these three lines, so that `## When to Use` follows them:

```markdown
## Hard Rules (REQUIRED when the skill has a never/always rule)
Each never/always rule in one line, before any table, long example or reference

```

- [ ] **Step 3: Edit `SKILL.md`**

After line 108 (`rules and the body template.`), add a blank line and:

```markdown
Before you set a frontmatter key only Claude Code reads, or when the skill
will run in Claude Code, also read
[references/claude-code.md](references/claude-code.md): what those keys do,
when to fork, how its listing drops descriptions and what survives compaction.
```

Replace lines 89–90 with:

```text
    SKILL.md              # Main reference (required)
    references/           # Depth, loaded on demand (only if needed)
    scripts/              # Executable tools (only if needed)
```

Replace lines 172–173 with:

```text
  SKILL.md            # Overview + patterns
  scripts/example.ts  # Working helpers to adapt
```

Replace lines 180–183 with:

```text
  SKILL.md                  # Overview + workflows
  references/pptxgenjs.md   # 600 lines API reference
  references/ooxml.md       # 500 lines XML structure
  scripts/                  # Executable tools
```

In line 419, `(the always-loaded list of skill names and descriptions)` → `(the skill names and descriptions loaded before any skill triggers; an overfull listing can lose descriptions)`.

Leave the `# cc-guide:` line (`:14`) and line 23 unchanged. Task 5 sets the citation.

- [ ] **Step 4: Update the register and `NOTICE`**

In `build/cc_guide/conformance.toml`:

- **If `RED outcome: null`:** replace the comment line `# writing-skills' departures from the guide go to its rewrite.` with `# writing-skills tests skill text first, even an edit the guide's TDD row lets skip (plan 92).`, so that it heads `writing-skills-tdd-for-docs`. Delete the whole `writing-skills-guide-gaps` block, from `[[exception]]` through its `tracked_in` line, and the blank line after it. All three parts close in this commit: S-58 through C1, S-107 through C3, and S-67 through D5.
- **If `RED outcome: failure`:** keep the comment line and replace the `writing-skills-guide-gaps` block's `sections`, `guide`, `reason` and `evidence` lines with:

```toml
sections = ['skills.progressive-disclosure']
guide = 'A SKILL.md body has its critical rules near the top.'
reason = "Plan 92's RED run showed agents stating a hard rule past a long block. writing-skills' body template gained a Hard Rules slot, and the entry leaves when plan 92's GREEN run passes."
evidence = 'Audit rows S-67 and S-68; owner gate 2026-10-04. The listing-budget (S-58) and @-loading (S-107) parts closed in plan 92 (2026-11-12). Body length (S-02) left on 2026-10-29.'
```

- **Either way:** in the `writing-skills-tdd-for-docs` block, keep `id`, `type`, `sections`, `artifacts` and `guide`, and replace `reason`, `evidence` and `revisit` with:

```toml
reason = "The guide keeps TDD for behaviour changes, and skill wording changes agent behaviour, so the departure is narrow. writing-skills' Iron Law also covers an edit that changes no instruction (a typo, a link, a verbatim move), which the guide's TDD row would let skip the test. In practice the owner waives the micro-test for such edits case by case (commit 7bb8810)."
evidence = 'Audit row S-97; owner gate 2026-10-04; owner decisions D2 and D4 of the writing-skills guide-rewrite spec, 2026-11-12 (plan 92).'
revisit = "When the guide's TDD row names agent-facing text such as skills or prompts, or when writing-skills' Iron Law changes."
```

In `NOTICE`, add this entry as the last entry of the superpowers changes list, directly before the blank line that comes before the indented skill list (`    brainstorming/`):

```text
  - Plan 92 (2026-11-12) checked writing-skills against this repository's
    Claude Code guide. A new file, references/claude-code.md, holds the
    skill's Claude Code facts in this repository's own words: what the
    frontmatter keys that only Claude Code reads do, why a Haiku `model`
    is not portable, when to fork a skill, how Claude Code's listing drops
    descriptions, and what of a body survives compaction. The fork advice
    moved there from references/discovery.md with a reason that the guide
    supports. discovery.md and SKILL.md keep the advice that holds on
    every runtime and point to the new file. Also corrected: a description
    is no longer said to load in every conversation, the reason given
    against `@` links is now a portability reason, and the directory
    examples show references/ and scripts/. The new file departs from
    upstream v7.0.1's references/ map, which plan 72 followed. No
    upstream text was taken.
```

**Only if `RED outcome: failure`:** after `examples show references/ and scripts/.`, add the sentence `discovery.md's body template also gained a Hard Rules slot after Overview, from this repository's own micro-test (specs/baseline/red-baseline-writing-skills-guide.md).` and re-wrap the entry at 74 columns with the same 4-space indent.

- [ ] **Step 5: Run the focused checks**

```bash
uv run --with pyyaml python -c "import sys; sys.path.insert(0, 'build'); import check_conformance as c; b, _ = c.skill_body(open('skills/writing-skills/SKILL.md').read()); print('body chars', len(b))"
uv run --with pyyaml python -c "import sys; sys.path.insert(0, 'build'); import check_frontmatter as f; t = open('skills/writing-skills/references/discovery.md').read(); missing = [k for k in sorted(f.SPEC_KEYS | f.HOST_KEYS) if f'\`{k}\`' not in t]; print('missing', missing, 'haiku ban', 'claude-haiku-*' in t); sys.exit(bool(missing) or 'claude-haiku-*' not in t)"
git grep -n -F -e '## Skill Discovery Optimization (SDO)' -e '**CRITICAL: Description = When to Use, NOT What the Skill Does**' -e "Push to a fork only when your human partner says to" -- skills/writing-skills/SKILL.md
git grep -n -F -e 'CLAUDE_CODE_FORK_SUBAGENT=0' -e 'Fork mode is on by default.' -- skills/writing-skills/references/claude-code.md
git grep -n -i -E 'tenant-export|vaultctl|refund-issue|support-desk|api-naming|dependency-audit|force-loads|200k|always resident|resident in EVERY' -- skills/writing-skills
git grep -n -E '^#|<!--' -- skills/writing-skills/references/claude-code.md
```

Expected:
- `body chars 18753`, give or take a few characters. It must be 18,800 or fewer.
- `missing [] haiku ban True` and exit 0 (Review Focus 1).
- Three hits in `SKILL.md`, one per anchor (Review Focus 2).
- Two hits in `claude-code.md` (Review Focus 3).
- No output from the fixture-and-old-claim sweep.
- The `^#` sweep lists only the file's Markdown headings (`# Claude Code facts …`, `## …`, `### …`) and no `# cc-guide:` or `<!--` line.

- [ ] **Step 6: Run the lints**

```bash
uv run python build/check_links.py
uv run --with pyyaml python build/check_frontmatter.py
uv run python build/check_provenance.py
uv run --with pyyaml python build/check_conformance.py
uv run python build/check_snippets.py skills/
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
uv run python build/cc_guide/cli.py lint
bash build/run_commit_lints.sh
```

Expected: `231 relative link(s) checked, 0 broken` (226 at `3684b96`, plus one link in `SKILL.md`, two in `discovery.md` and two in `claude-code.md`; a different base count means `skills/` changed since `3684b96`, so report it); the frontmatter, provenance, conformance and Tier 1 snippet checks pass; the dependency test passes; `cli.py lint` passes and still prints the one `STALE skills/writing-skills/SKILL.md …` line, which Task 5 clears; the runner ends `commit lints passed`.

- [ ] **Step 7: Commit**

```bash
git add skills/writing-skills build/cc_guide/conformance.toml NOTICE
git commit -m "refactor(writing-skills): distill Claude Code facts into references/claude-code.md" -m "SKILL.md and discovery.md keep the advice that holds on every runtime and point to the new file. Corrects the listing claim, the @-link reason, the fork advice's reason, the Haiku model facts and the directory examples (plan 92, spec specs/writing-skills-guide-rewrite.md). Refreshes writing-skills-tdd-for-docs, and closes or narrows writing-skills-guide-gaps."
```

Record this commit's short SHA in the ledger as `T3_SHA`.

---

### Task 4: Run the new-layout arms and settle the last register part

**Files:**
- Create: `specs/baseline/red-baseline-writing-skills-guide/new/` and, for a tightening round, `new-r<N>/`
- Modify: `specs/baseline/red-baseline-writing-skills-guide.md` (`## Results`)
- Modify only on a missed bar: the pointer texts, the facts' wording in `claude-code.md`, the template slot (Step 5)
- Modify on the GREEN result: `build/cc_guide/conformance.toml` (Step 6)

**Interfaces:**
- Consumes: `T3_SHA` (Task 3); `SPEND`; the kit and rules (Task 1); the `RED outcome:` line (Task 2).
- Produces: verdict tables for `read`, `apply` and (if run) `green`; the final state of `writing-skills-guide-gaps`.

- [ ] **Step 1: Check the new text against the fixtures, then build the prompts**

```bash
git grep -n -i -E 'tenant-export|vaultctl|refund-issue|support-desk|api-naming|dependency-audit' <T3_SHA> -- skills/writing-skills
python3 specs/baseline/red-baseline-writing-skills-guide/kit/build_prompts.py <T3_SHA> new specs/baseline/red-baseline-writing-skills-guide/new
```

Expected: no output from `git grep`; then `wrote 7 prompts to …/new`. `new/MANIFEST.txt` shows `body chars` near 18,753 and a `file references/claude-code.md` line. If `RED outcome: null`, `new/R1.txt` is built but not run.

- [ ] **Step 2: Run the `read` and `apply` arms (60 reps; each batch of 5 needs $2.50 of headroom under the cap)**

Check the spend rule before each line. Run each line with `timeout: 600000` or in the background:

```bash
for p in P1r P2r P3r P1a P2a P3a; do
  bash specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh specs/baseline/red-baseline-writing-skills-guide/new/$p.txt specs/baseline/red-baseline-writing-skills-guide/new/$p-opus 1 5 claude-opus-5-5
  bash specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh specs/baseline/red-baseline-writing-skills-guide/new/$p.txt specs/baseline/red-baseline-writing-skills-guide/new/$p-sonnet 1 5 claude-sonnet-5-5
done
```

Run the loop one prompt at a time if the spend rule needs a check between batches.

- [ ] **Step 3: Run the `green` arm, only if `RED outcome: failure` (10 reps)**

```bash
bash specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh specs/baseline/red-baseline-writing-skills-guide/new/R1.txt specs/baseline/red-baseline-writing-skills-guide/new/R1-opus 1 5 claude-opus-5-5
bash specs/baseline/red-baseline-writing-skills-guide/kit/run_reps.sh specs/baseline/red-baseline-writing-skills-guide/new/R1.txt specs/baseline/red-baseline-writing-skills-guide/new/R1-sonnet 1 5 claude-sonnet-5-5
```

- [ ] **Step 4: Read every rep and record the verdicts**

Run `uv run python specs/baseline/red-baseline-writing-skills-guide/kit/show_reps.py specs/baseline/red-baseline-writing-skills-guide/new/*/` and read each full reply. Under `## Results`, add:
- One table per prompt and model for `read`: rep, verdict under the read rule, and the ACTION line that decides it. Say how many passes come from the no-edit clause.
- One table per prompt and model for `apply`: rep, verdict under the apply rule, and the quoted words that decide it.
- If run, one `green` table per model, in the same form as `red`.
- A summary table of every bar: prompt, model, score, bar, met or missed. Then two sentences that compare `apply` on Opus with `desc`, and say that the comparison is descriptive.
- The running spend.

- [ ] **Step 5: Tighten on a missed bar (at most two rounds per prompt)**

For each prompt and model that misses its bar:
- `read` miss: tighten the pointer that sends the agent on. That is the `SKILL.md` paragraph added in Task 3 Step 3, or the `discovery.md` sentence that starts `Before you set an extension, read`, or the `(Claude Code's rule: …)` pointer in Token Efficiency. Change only pointer text.
- `apply` miss: tighten the wording of the fact the rule scores, in `claude-code.md`. Add no instruction.
- `green` miss: tighten the template slot's wording in `discovery.md`.

After each tightening, re-run the body measurement of Task 3 Step 5 (it must stay 18,800 or fewer) and `uv run python build/check_links.py`. If a `SKILL.md` pointer change would pass 18,800, first replace `SKILL.md` line 23 with the line below, and add `Claude Code reads personal skills from \`~/.claude/skills/\`.` as the first sentence under `## Frontmatter keys`' heading in `claude-code.md`, as its own paragraph (D9):

```markdown
**Personal skills live in your runtime's skills directory.** Codex, Copilot CLI, and Gemini CLI also recognize `~/.agents/skills/` as a cross-runtime alias. Claude Code's directory is in [references/claude-code.md](references/claude-code.md).
```

Commit each round with `git commit -m "fix(writing-skills): tighten <what> for plan 92 <prompt>"`. Rebuild only the missed prompt, with `build_prompts.py <new-sha> new specs/baseline/red-baseline-writing-skills-guide/new-r<N> <prompt>`. Rerun 5 reps on each model that missed, and record them as in Step 4. Prompts that passed keep their verdicts on the earlier text; say so in the record. After two rounds with a bar still missed, stop and ask the owner with the reps' quoted lines and the running spend.

- [ ] **Step 6: Settle `writing-skills-guide-gaps`**

- **`RED outcome: null`:** Task 3 removed the entry. Nothing to do.
- **GREEN met its bar on both models:** replace the comment line `# writing-skills' departures from the guide go to its rewrite.` with `# writing-skills tests skill text first, even an edit the guide's TDD row lets skip (plan 92).`, and delete the narrowed `writing-skills-guide-gaps` block, from `[[exception]]` through its `tracked_in` line, and the blank line after it. This commit closes S-67's part.
- **GREEN still misses after two rounds:** stop and ask the owner whether the slot stays. Then point the entry's `tracked_in` at a new backlog item that Task 5's completion notes name. The part stays open, and the entry says so.

- [ ] **Step 7: Run the checks and commit**

```bash
uv run --with pyyaml python build/check_conformance.py
bash build/run_commit_lints.sh
git add specs/baseline/red-baseline-writing-skills-guide.md specs/baseline/red-baseline-writing-skills-guide build/cc_guide/conformance.toml
git commit -m "test(writing-skills): plan 92 new-layout micro-test results"
```

Expected: the conformance check passes; the runner ends `commit lints passed`.

---

### Task 5: Review against the guide and restamp

**Files:**
- Modify: `specs/baseline/red-baseline-writing-skills-guide.md` (`## Review against the guide`)
- Modify: `skills/writing-skills/SKILL.md:14` (citation), and any file a contradicted row fixes
- Modify: `build/cc_guide/baseline.json` (through `baseline cite` only)

**Interfaces:**
- Consumes: the final skill text (Tasks 3–4); Task 3 Step 1's fact-to-section table.
- Produces: the review table; the restamped citation; `cli.py lint` with no `STALE` line.

- [ ] **Step 1: Review every file the skill loads on demand**

The review covers `SKILL.md` and every Markdown file it loads on demand (drift rule R4.1): `references/claude-code.md`, `references/discovery.md`, `references/flowcharts.md`, `references/bulletproofing.md`, `testing-skills-with-subagents.md`, `persuasion-principles.md` and `examples/CLAUDE_MD_TESTING.md`. Read each against the guide sections `skills.locations`, `skills.frontmatter`, `skills.description`, `skills.listing-budget`, `skills.progressive-disclosure`, `subagents.frontmatter`, `subagents.models` and `subagents.isolation` in `specs/guides/claude-code-customization-guide.md`.

Add `## Review against the guide` to the record, before `## Results`, with one row per statement whose truth depends on Claude Code:

```markdown
| # | File:line | Statement, in the repo's words | Guide section | Verdict | Note |
|---|---|---|---|---|---|
```

The verdict is `covered`, `contradicted` or `not covered`. Start from Task 3 Step 1's table. Write each statement and note in your own words; quote no docs text. A file with no Claude Code statement gets one row that says so. `examples/CLAUDE_MD_TESTING.md`'s `~/.claude/skills/` lines are statements under `skills.locations`.

- [ ] **Step 2: Fix every contradicted row**

Fix each `contradicted` row in the skill text, as a factual edit under D4. Add no instruction; if a fix needs one, stop and ask the owner. Re-run Task 3 Step 5's body measurement and Step 6's lints. List each `not covered` row for the owner. The owner rules on each at the plan's completion gate.

- [ ] **Step 3: Set the citation**

In `SKILL.md`, replace line 14 with the sections that at least one `covered` row relies on, in this order, dropping any that no row uses:

```text
# cc-guide: skills.locations skills.frontmatter skills.description skills.listing-budget skills.progressive-disclosure subagents.frontmatter subagents.models subagents.isolation @2.1.219
```

Leave the `@2.1.219` stamp as it is. Step 5 restamps it.

- [ ] **Step 4: Check the guide on `origin/main`**

```bash
git fetch origin
git diff "$(git merge-base HEAD origin/main)" origin/main -- specs/guides/claude-code-customization-guide.md
```

Expected: no output. If the diff touches a section the citation names, merge `origin/main` into this branch with a true merge, re-review that section's rows, and fix any new contradiction before Step 5. Record what changed under the review table.

- [ ] **Step 5: Restamp and run every check**

```bash
uv run python build/cc_guide/cli.py baseline cite skills/writing-skills/SKILL.md
uv run python build/cc_guide/cli.py lint
uv run --with pyyaml python build/check_conformance.py
bash build/run_commit_lints.sh
```

Expected: `baseline cite` restamps the citation and records each section's `text_hash`; `cli.py lint` passes and prints no `STALE` line; the conformance check passes; the runner ends `commit lints passed`.

- [ ] **Step 6: Commit**

```bash
git add skills/writing-skills/SKILL.md build/cc_guide/baseline.json specs/baseline/red-baseline-writing-skills-guide.md
git commit -m "docs(writing-skills): review against the guide and restamp its citation"
```

Add any skill file a contradicted row fixed to the same commit.

---

## Done when

- **L4182:** `writing-skills-guide-gaps` is gone from the register, or narrowed to S-67 with a new backlog item (Task 4 Step 6). `writing-skills-tdd-for-docs` carries the refreshed reason, evidence and revisit. `build/check_conformance.py` passes. The `@` reason sentence is gone, and the bare-name rule stays with its portability reason. The directory examples show `references/` and `scripts/`. The citation names `subagents.models`. The fork advice has a guide-backed reason, or the owner ruled to drop it.
- **L1681:** `SKILL.md` and its on-demand files are reviewed and restamped with `baseline cite`, and `cli.py lint` prints no `STALE` line on this branch at the merge. Re-run Task 5 Step 4 and `cli.py lint` right before the merge.
- **L1158:** `references/claude-code.md` exists and holds the Claude Code facts, and `SKILL.md` and `discovery.md` point to it.
- The record holds every arm's verdicts and the review table. `NOTICE` records the change.
- Every `read` and `apply` bar is met, and `green`'s if it ran, or the owner has ruled on the one that is not.

## Completion notes

For the Plan Completion Protocol (writing-plans):

- **Gate questions for the owner:** every `not covered` row from Task 5; and whether the `apply` arm earns a progress note on the deferred item "The `t3` micro-test passes show less than they appear to".
- **Tick** the three items with `→ done <date> (plan 92)`: "A distilled `references/` file for writing-skills", "Review the 41 files the drift sweep stamped stale" and "Split and rewrite writing-skills against the guide".
- **New items** (spec, Not in this spec):
  - The guide omits a docs fact: Claude Code attaches the files that `@` paths name in a local skill's body, but not in a skill synced from claude.ai. `/cc-guide` upkeep can add it to `skills.progressive-disclosure`, and writing-skills could then state the Claude Code reason again.
  - `build/cc_guide/packets.py` `files()` copies only the citing file into a `/cc-guide files` packet, so it leaves out the on-demand files that R4.1 says a SKILL.md citation covers.
  - The new backlog item for S-67, if Task 4 Step 6 needed one.
- **Retire** the spec with the plan: no other live plan implements it.
