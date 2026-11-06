# Synthesize-mode critique-point fix (fork a) — RED and GREEN on the plan 42 fixture

**Date:** 2026-11-05 · **Status:** `B1 HELD in GREEN (4 of 5 valid reps) against RED 0 of 5. Pilot, RED and GREEN cost $29.87 of the $65 cap. Skill edit fb5f940.`
**Governs:** whether defining a critique point as one distinct claim makes Synthesize mode's triage
table cover the critique's findings and evidence as well as its asks (B1, the item's Done-when).

> ⚠️ **Quarantine this file during any future micro-test of `describe-critique-methodology`.**
> It names the skill, the behaviour under test, the pass bar, the fixture's points and the
> results. Its name matches the VOID pattern `specs/completed/synthesize-mode-*`.

Source: the item "Synthesize mode never defines what a "critique point" is …" in
`specs/deferred_items.md`, section `42-synthesize-mode-verification-rerun — 2026-10-12`, and its
note `→ progress 2026-10-31 (owner ruling): fork (a)`. The run follows plan 42's record,
`specs/completed/synthesize-mode-verification-2026-10-12.md`, and changes only what is marked
below. There is no plan file and no plan id: this is one writing-skills RED→GREEN cycle (the
sender's default, not an owner ruling).

## Owner decisions

- **D1** (owner, 2026-11-05): "Maybe then 2-4 in separate sessions", answering a backlog ranking
  whose item 2 was this fix. Reading: run fork (a) to the item's Done-when in its own session.
  Home: the item's closing note.
- **D2** (owner, 2026-11-05, choosing an option): "Session, after a pilot". Reading: this session
  launches the pilot and the counted reps, after an uncounted pilot shows no user-level context,
  and stops for the owner's yes before any counted rep. Home: Dispatch, below.
- **D3** (owner, 2026-11-05, choosing an option): "Up to $65". Reading: pilot, RED and GREEN
  together at or under $65. Home: Pre-registration, below.
- **Pre-run gate** (owner, 2026-11-05, in this session): "Go ahead and". The message ended there.
  It was read as approval of the pre-registration, the pilot result and the spend estimate. No
  further text arrived before the run finished.

## Why a fresh RED

Plan 42's B1 result (0 of 5) measured skill tree `69b30fa3`. HEAD's tree at `1fbb203` is
`ad4c4749`, because commit `252d6ad` rewrote the exemplar step after plan 42. Plan 42's reps also
loaded the owner's global `CLAUDE.md`, rules and output style. So that 0 of 5 is history, and RED
ran again on HEAD's text under an isolated kit.

## Pre-registration

Frozen before any counted rep (SHA-1 `f9f8a01` of the kit's `PREREG.md`, with the scoring sheet
`r2_sheet.md` at `4494382`) and shown to the owner at the gate. Everything not listed here is plan
42's pre-registration, unchanged.

**Arms.** RED loads the skill at `1fbb203` (tree `ad4c4749`). GREEN loads the edit at `fb5f940`
(tree `edd02997`), written only after all five RED reps were scored and their scores frozen. Each
arm needs 5 valid reps, run as one parallel batch.

**Fixture and turns.** Unchanged: the two fixture files (byte-identical to plan 42's), a repo whose
single commit is `0e2c907`, and plan 42's three turn texts (byte-identical copies). Fresh repos at
`~/.cache/nfp-work/rep-<n>` and fresh session ids. Plan 42's repos (`~/.cache/nfp-notes/`) are a
VOID path.

**Behaviour scored: B1 only**, as plan 42 defines it: M1 (the triage table before the first spec
write), R1 (adjudication status stated above the table), R2 (the table covers every point of the
frozen 50-point key, `~/.cache/ctl-q9/coverage-key.md`) and R3 (every needs-user-adjudication
question in the table's message, none later). M2 to M5 are recorded from `grade.py`. B2 and B3's
manual parts are not scored (new: out of scope for this item; plan 42 held both 5 of 5).

**R2, plan 42's strict reading, written out.**
1. A point counts when a row of the triage table states its distinct claim in words. Any cell of
   the row counts, the rationale column included (calibrated on plan 42's hand-checked rep-4
   table, whose T1 rationale covered B3).
2. A row that only cites a section anchor, or names the programs involved without the claim,
   does not count.
3. A lumped "evidence" or "background" row covers none of the claims it anchors.
4. One row may cover several key points when it states each claim.
5. B7 and A9 are marginal: recorded, never counted as misses.
6. The table governs. Prose outside it and the spec do not count. R2's wording ("the table
   covers every critique point") overrides the key's header ("spec or triage table").
7. One reader (this session) scored every rep and knew the hypothesis. RED's scores were frozen
   before the edit was written. That is the only blinding.

**Pass bar:** B1 holds in at least 4 of 5 valid reps (the item's Done-when).

**VOID rule.** Plan 42's rule, plus these additions:
- **Paths:** every answer-bearing location that a content search of the home folder found before
  the pilot: `~/.cache/nfp-notes/`, `~/.cache/agent-skills/` (it holds the handoff brief),
  `~/.cache/ctl-*` (both kits and this one), `~/.cache/pondworks/`, `~/.cache/red30/`, agent-skills
  `specs/completed/deferred_items.md`, `~/.claude/projects/`, `~/.claude/file-history/`,
  `~/.claude/sessions/`, `~/.gemini/`, `~/.codex/` and `~/Library/Application Support/Claude/`.
- **Markers:** this kit's name and the five user-level sources in injected context.
- **Sibling reps:** a tool input or result naming `nfp-work/rep-<m>`, m ≠ n, voids rep n.
- **Another copy of the skill:** in GREEN, a `describe-critique-methodology/` path outside the
  plugin copy voids the rep. In RED the text is identical, so the hit is recorded only.

**Staleness rules** (the two decisions that the watch item "Synthesize mode's staleness check is a
second path to a VOID rep" asks for before a Synthesize re-run):
1. Exposure stays strict: a `Grep` result in any output mode, `files_with_matches` included, that
   carries a VOID path voids the rep (plan 36's ruling 1 and plan 42, unchanged). The staleness
   check is not pointed at an isolated copy. Instead, flag settings deny `Read` on every VOID path,
   which blocks the search at its source. Checked on Claude Code 2.1.316 before the pilot: a
   `Grep` for `nfp_series` over `~/Projects` returned no files (plan 42's voided rep-3 got 13),
   and `grep -r` and `cat` on a denied path were refused.
2. A denied call exposes nothing and does not void by itself.
3. The kit's `grade.py` (a recorded copy, `~/.cache/ctl-m4/grade.py`; plan 42's is untouched)
   checks sibling-rep directories.

**Budget (D3's home).** Pilot, RED and GREEN at or under $65. Before each launch, spend so far
plus $5.50 per rep about to start had to stay at or under $65. Void reps would be replaced one at
a time within their arm.

## Dispatch (D2's home)

This session launched every rep. Channel 5's plain-terminal rule from plan 42 does not apply,
because each rep ran with no user-level context and inherited no variable from this session:

- **Environment:** `env -i` with only `HOME`, `USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and
  `LANG`, plus `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. The
  launching session's variables (its messaging socket, session id and effort among them) never
  reach a rep.
- **Wiki variable:** `ZDOTDIR=~/.cache/zdot-r`, whose startup files source the owner's own
  `.zshenv`, `.zprofile` and `.zshrc` and then unset `LLM_WIKI_ROOT`. `~/.zshenv` has exported
  that variable since 2026-10-21, after plan 42, and zsh reads `.zshenv` for every shell, so
  `env -i` alone does not remove it. Pilot 1 ran without this fix, and its
  `printenv LLM_WIKI_ROOT` printed the wiki path.
- **Command:** `claude -p --model claude-opus-5-5 --effort xhigh --setting-sources ""
  --strict-mcp-config --plugin-dir ~/.cache/skillpack --settings <per-rep deny rules>
  --permission-mode acceptEdits --allowedTools <plan 42's list> --disallowedTools ListAgents
  SendMessage --output-format stream-json --verbose`, on each of the three turns
  (`--session-id`, then `--resume` twice).
- **Skill loading:** under `--setting-sources ""`, neither `~/.claude/skills/` nor an `--add-dir`
  folder's `.claude/skills/` loads. `--setting-sources project` with `--add-dir` loads the skill
  by its bare name, but from a cwd under the home folder it also loads `~/.claude/CLAUDE.md` and
  `~/.claude/rules/` as project files of the ancestor `~`. So the skill loads as a plugin and is
  listed as `local:describe-critique-methodology`. Every rep resolved T1's bare name to it. Only
  one arm's copy existed on disk at a time, built by `make_plugin.sh`, which checks the copy's
  tree hash against the commit.
- `ListAgents` and `SendMessage` are removed, since they reach other sessions on this Mac.

**Shared-checkout guard.** Recorded before the pilot, before each batch and after each batch. The
main checkout stayed on `main` at `1fbb203` throughout. The plugin tree was `ad4c4749` for the
pilots and RED and `edd02997` for GREEN, matching each arm's commit at every point.

**Grep gate.** Before each batch the plugin copy was grepped for the fixture's terms and the
grader's injected-context markers. HEAD's text has three hits that predate this run (`calibration
checks` in `methodology-template.md`, `nfp-model` twice in `test_check_decoupling.py`). GREEN
added none, and neither arm carries a marker.

## Pilots (uncounted, RED text, Claude Code 2.1.316)

| Check | Probe | Pilot 1 | Pilot 2 |
|---|---|---|---|
| Five user-level sources absent | all five NO | no marker in injected context | no marker in injected context |
| No MCP, advisor, `ListAgents` or `SendMessage` tool | yes | yes, every turn | yes, every turn |
| `Skill` call resolves the bare name | listed | yes | yes |
| `references/spec-synthesis.md` read from the plugin | — | yes | yes |
| `xhigh` on every assistant record; one model | — | yes (28 of 28) | yes (26 of 26) |
| `grade.py` finds the transcript; M1-M5 | — | yes; all true | yes; all true |
| `LLM_WIKI_ROOT` unset in the rep's shell | — | **no**, so the ZDOTDIR fix | yes |
| VOID, sibling, other-copy hits | — | none | none |
| Cost | $0.16 | $2.46 | $1.94 |

The probe was a separate one-turn session with the same flags and repo shape, asking seven yes/no
context questions (plan 72's `isolation_probe.txt`, extended with tool and skill lines). Each
pilot's injected context held its own environment, model, date, git status (`Git user: Lowell
Mason`, as in plan 42) and Claude Code's built-in skill and agent listings and base prompt. Every
`CLAUDE.md`, `memory` or `hook` string in it is built-in text.

## RED (tree ad4c4749, reps 3-7)

All five valid. No VOID, marker, sibling or other-copy hit. Every tool call stayed in the rep's
own repo or the plugin copy, and the wiki path appeared in no result. Denials: 2, 2, 3, 2 and 3,
each a compound `ls` of the plugin folder or a braced variable, and none blocked a read, a spec
write or a commit. No rep read an exemplar (E1 0 of 5): without the global `CLAUDE.md`, a rep is
not told where the agent-skills repo is.

| Rep | M1 | R1 | R2 | R3 | B1 | Strict misses | Rows | Cost |
|---|---|---|---|---|---|---|---|---|
| 3 | Y | Y | N | Y | fail | KF1, KF2, KF4, B3 | 24 | $2.57 |
| 4 | Y | Y | N | Y | fail | KF1, KF2, KF4, A1, B3, C3c | 22 | $2.44 |
| 5 | Y | Y | N | Y | fail | KF1, KF2, KF4, A1, B3, C3c | 21 | $2.18 |
| 6 | Y | Y | N | Y | fail | KF1, KF2, KF3a, KF4, C3c | 24 | $2.15 |
| 7 | Y | Y | N | Y | fail | KF1, KF2, KF4, A7, B3, C3c | 28 | $2.77 |

**B1: 0 of 5.** Plan 42's pattern holds without user-level context. Every rep treated the Key
Findings as evidence for other rows. Rep 3: "Key Findings 1–5 are evidence, cited under the rows
they support." Rep 4, row 22: "Evidence from other producers (KF1–5: CES, StatCan, FRB, ADP,
QuickBooks) | accept as motivation only". Rep 6, row 1: "R KF1–5: precedent (CES X/K factors, HB,
Kokic-Bell, ADP/FRB, QuickBooks) | accept (motivation only)". Rep 7 has no Key Findings row. Four
reps put "paid vs active" and "multi-establishment" on one row and dropped pay frequency, the
first clause of the same gap. Only rep 6 carries the QWI figure.

## The edit (fb5f940)

Form, per writing-skills "Match the form to the failure": RED shows a shaping failure, a wrong
unit for a row in a table the reps already build. So the edit is a positive recipe for the unit,
not a prohibition.

- `references/spec-synthesis.md`, § Critique triage table, after the table template: "A critique
  point is one distinct claim, wherever the critique makes it." Then three steps (one claim per row
  stated in words, with claims that ask for nothing as rows too; split compound points; check
  coverage against the critique's own enumeration before sending) and one worked example from a
  churn model (one paragraph, three rows).
- `SKILL.md`, Synthesize step 2: one sentence with the same rule, since `SKILL.md` always loads.

The example is from a different domain and does not copy the shape of any one fixture sentence.
No added line names a fixture point (grep gate above).

## GREEN (tree edd02997, reps 8-12)

All five valid. No VOID, marker, sibling or other-copy hit. Rep 9's staleness search ran a `Glob`
for `**/nfp_series/calibration*` over `~/.cache/nfp-work`, the parent of every rep repo. It
returned "No files found", so nothing was exposed. Denials: 2, 2, 2, 1 and 1, of the same kinds as
RED's. E1 0 of 5, as in RED.

| Rep | M1 | R1 | R2 | R3 | B1 | Strict misses | Rows | Cost |
|---|---|---|---|---|---|---|---|---|
| 8 | Y | Y | Y | Y | pass | none | 65 | $3.03 |
| 9 | Y | Y | Y | Y | pass | none | 75 | $2.74 |
| 10 | Y | Y | N | Y | fail | C3c | 68 | $2.72 |
| 11 | Y | Y | Y | Y | pass | none | 74 | $2.11 |
| 12 | Y | Y | Y | Y | pass | none | 77 | $2.58 |

**B1: 4 of 5.** Reps missing each point, RED → GREEN: KF1 5 → 0, KF2 5 → 0, KF4 5 → 0, B3 4 → 0,
C3c 4 → 1, A1 2 → 0, A7 1 → 0, KF3a 1 → 0. The tables grew from 21-28 rows to 65-77, and each Key
Finding now has rows of its own. Rep 8, row 4: "CES robust estimation sets Kokic-Bell cutoffs per
stratum and per tail; the module borrows the CES "atypical" label but not that practice". Rep 12,
row 51: "Pay-frequency composition is not handled (C3) | accept, narrowly".

**The one miss.** Rep 10's rows 44 and 45, both anchored on Details C.3 and Recommendation 9,
carry the gap's two asks (paid or active counts; multi-site records). The gap's first clause,
pay-frequency composition, has no row, and pay frequency appears nowhere in its turn-1 message.

**R3.** No GREEN rep asked a new owner question after the table. Rep 8's turn 2 lists "Choices I
made beyond the review — worth checking" and asks nothing. Plan 42 ruled the same pattern (its
rep 6) a pass: disclosed after the fact, not asked.

## Decision

| Arm | B1 | R2 | R1 | R3 | M1 |
|---|---|---|---|---|---|
| RED (HEAD text) | 0 of 5 | 0 of 5 | 5 of 5 | 5 of 5 | 5 of 5 |
| GREEN (fb5f940) | **4 of 5** | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 |

GREEN meets the Done-when bar (B1 in at least 4 of 5 valid reps), so the item closes.

**How firm the result is.**
- It meets the bar with no margin: one more miss would fail it.
- The five passes do not rest on lenient calls. Each counted point is a row that states the claim
  in words, and none of the four passing reps misses a strict point. B7 and A9 were never counted.
- The edit changed what the reps do, not only the score. RED's misses were whole classes of claim
  (Key Findings, evidence figures, a first clause). GREEN's single miss is one clause.
- One reader scored every rep and knew the hypothesis. RED was frozen first. No blind second
  reader scored GREEN.

**What the bar does not capture.** A triage table now runs to about 65-77 rows for a critique of
this size, about three times RED's, and a whole rep cost about 9% more (GREEN $2.64 a rep, RED
$2.42).
For a long critique the owner reads a much longer table.

## Kit

Outside the repo, at `~/.cache/ctl-m4/`: `run_rep.sh`, `make_repo.sh`, `make_plugin.sh`,
`make_settings.py`, the probe, `grade.py` (plan 42's with the recorded additions), `show_rep.py`,
`PREREG.md`, `r2_sheet.md`, `scores/` (one file per rep, plus a summary per arm) and `results/`.
Rep repos: `~/.cache/nfp-work/rep-0` to `rep-12`. ZDOTDIR: `~/.cache/zdot-r/`. The plugin copy at
`~/.cache/skillpack/` holds GREEN's text.
