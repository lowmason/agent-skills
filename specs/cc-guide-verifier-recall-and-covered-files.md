# cc-guide verifier recall and covered files — Design Spec

**Status:** DRAFT, for the owner's review. The design came from a brainstorming session on 2026-11-17 for lane D1
of that day's `/deferred` triage. D1 is the owner's ruling from that pass. D2 and D4 are the owner's answers in the
brainstorming session. Text marked *(designer's call)* is the designer's choice.

This spec changes two kinds of `/cc-guide` packet and what the `cc-guide-verifier` agent answers from them. An
audit packet gets a numbered list of the changelog bullets that name the group's terms, and the verifier must answer
each one. A files packet for a skill gets a copy of each Markdown file that the skill's citation covers, and the
files rule gets a component scope. A micro-test gates the audit change and the files change separately.

## Backlog items

Each item is in `specs/deferred_items.md`, found by its first words.

| # | Item (first words) | Section | Ages out |
|---|---|---|---|
| I1 | "Make a files packet show the verifier the Markdown that a `SKILL.md` citation covers" | `cc-guide-files-2.1.326-backlog (…) — 2026-11-17` | 2027-01-02 |
| I2 | "`build/cc_guide/packets.py` `files()` copies only the citing file" | `92-writing-skills-guide-rewrite — 2026-11-12` | 2026-12-28 |
| I3 | "The audit verifier writes no B row for the changelog entries behind P11" | `45-claude-code-drift-automation — 2026-10-14` | 2026-11-29 |
| I4 | "The audit verifier's omission recall was 3 of 7 known positives" | `44-claude-code-drift-automation — 2026-10-13` | 2026-11-28 |
| I5 | "The files rule has no precision fixture outside its own fixtures' domain" | `45-claude-code-drift-automation — 2026-10-14` | 2026-11-29 |
| I6 | "The files rule must take its reference case from the component the file describes" | `45-claude-code-drift-automation — 2026-10-14` | 2026-11-29 |

P1 to P14 below are the labels of plan 45's ground-truth key
(`specs/plans/completed/45-claude-code-drift-automation.md:117-130`). P11 is `deniedModels` beside
`availableModels` (guide line 429). P8 is a top-level `effortLevel` that no longer counts for Opus 5.5 (guide line
426).

## Motivation

| Fact | Evidence |
|---|---|
| The audit of group `models` on 2026-10-13 missed P11 and P8. P11's changelog entry is in release 2.1.283, at `changelog.md:1288` of that audit packet. P8's is in 2.1.280, at `:1702`. | Packet `~/.cache/agent-skills/cc-guide/packets/20261013T113847-audit/`; plan 45's key, lines 124 and 127 |
| Both releases are older than the group's `audited` release, 2.1.288. `baseline init` wrote that release on 2026-10-03 without an audit. The packet's `releases.md` was empty (`index.json` `releases: []`). The contract tells an audit to check "the releases in `releases.md`" and to write one B row per changelog item in scope, over a 10,497-line `changelog.md`. No list ever named the two bullets. | `git show 5bd78a7:build/cc_guide/baseline.json`; `.claude/agents/cc-guide-verifier.md:45-57` |
| Plan 45 tried a contract-only change (`0b76543`). P11 was hit in 0 of 2 valid changed reps and 0 of 2 control reps, and the owner reverted the change. In 3 of those 4 reps, the `deniedModels` text was in the verifier's own context. | `specs/completed/verifier-recall-verification-2026-10-14.md`, Result; I4's `plan 45 transcripts` note |
| Measured on that packet with the repo's own term rules (`group_terms` in `build/cc_guide/state.py`, `STOP_TERMS` in `build/cc_guide/guide.py`): about 205 changelog bullets hold a backticked span that is exactly one of the group's terms (204 by a line scan, 206 by the repo's bullet parser). P11 is listed through `availableModels`, and P8 through `/effort`. 81 of them also name a span that the guide never names: P11 is among them, P8 is not, because P8 changes behaviour and names nothing new. 1,288 bullets hold a group term as a substring, which is triage's hint rule. | Scratch measurement and the builder check, 2026-11-17 |
| On today's manifest and changelog, the same rule lists about 299 bullets for `models`, 382 for `overview` and 406 for `skills`. The list grows as the changelog grows. | Builder check, 2026-11-17 |
| `files()` copies only the citing file. Spec R4.1 says that a `SKILL.md` citation covers the Markdown files the skill loads on demand, in `references/` or beside it. 15 citing skills have such files, counted without `README.md` and `scripts/`: from 1 file (`executing-plans` and two others) to 19 files and about 206 KB (`bayesian-workflow`). | `build/cc_guide/packets.py:365-402`; `specs/completed/claude-code-drift-automation-spec.md:541-545` |
| Settle discards a files row whose file is not `index['file']`, and `same_file` compares only that file with the checkout. The skill lets a files fix edit only the reviewed file. | `build/cc_guide/settle.py:565-637`; `.claude/skills/cc-guide/SKILL.md`, Ground rules |
| Plan 45's changed files rule left 8 UNSUPPORTED `contradicts` rows on the readme packet, against 0 for the control. Three were on `hooks/README.md:89`, where the rule applied Claude Code's permission-matcher splitting to the repo's own hook. Settle prints each `contradicts` row as an edit to apply. | Plan 45's record, Result and Disposition |
| Plan 45's kit (`~/.cache/agent-skills/scratch/plan45/`) and its held 2.1.296 binary are gone. The audit packet, the readme packet `20261013T121854-files/hooks__README.md` and the docs snapshot `~/.cache/agent-skills/cc-guide/2.1.296/docs/` remain. The snapshot holds no `changelog.md`; the audit packet holds the 2.1.296 changelog. The audit packet's `guide.md` is byte-identical to the guide at `5bd78a7`. | Checked 2026-11-17 |

## Goals

- **G1.** The audit verifier answers every changelog bullet that names one of its group's terms. Settle holds an
  audit that leaves one unanswered. (I3, I4)
- **G2.** A files packet for a skill holds a copy of each Markdown file that the skill's citation covers. The
  verifier reviews them, and settle accepts rows on them and checks them against the checkout. (I1, I2)
- **G3.** The files rule takes its reference case from the component that a statement describes. (I6)
- **G4.** A micro-test measures each contract change against today's contract, on the fixtures the backlog names
  and on one new precision fixture outside the hooks domain. (I3 to I6)

## Non-goals

- No change to triage or verify mode.
- No window on the listed bullets, such as the releases since the group's last real audit. Every audit lists the
  matching bullets of the whole changelog. *(designer's call: the owner took the whole-changelog cost with D2. The
  builder check found 300 to 400 bullets per group today, not the 200 the owner was told. In tokens that is small
  beside an audit's docs pages, and a window needs a new `baseline.json` field, since the `audited` release that
  `baseline init` wrote marks no real audit. Revisit if the list's length lowers the answers' quality.)*
- No lint change. A covered file still carries no citation of its own, and an edit to it does not make the skill
  STALE.
- No change to the A rows' verdicts, or to the C rows.
- No guide edit. A later `/cc-guide` run applies what the new rows find.

## Anti-goals

- A contract rule that names `availableModels`, `deniedModels`, `effortLevel` or any other fixture fact. That
  leaks the fixture into the arm, as plan 45's term gate warned.
- Settle applying a B row or a listed-bullet answer as an edit. B rows stay items for the owner.
- A files change that raises false `contradicts` rows, since settle prints each one as an edit to apply.
- One gate for both contract sections. In plan 45, the failed audit gate also reverted the files fixes, which had
  passed.

## Decisions

- **D1** (owner, 2026-11-17, `/deferred` ruling on I1 and I2): the packet copies each on-demand Markdown file, as
  it copies the cited file, so settle checks against fixed bytes. I1 and I2 close together.
- **D2** (owner, 2026-11-17, brainstorming): listed bullets for the audit. See Approaches.
- **D3** *(designer's call)*: one spec, one plan and one kit for I1 to I6. The audit section and the files section of
  the contract each land or revert on their own gate.
- **D4** (owner, 2026-11-17, brainstorming, after the builder check): the fresh `/cc-guide files` pass that I1 needs
  runs in its own session after this plan merges, not in the plan. The pass edits stamps and maybe text in
  machinery skills, so it runs alone under the machinery rule, and the plan stays a domain stream.

## Approaches

For I3 and I4, three ways were considered:

| Approach | What it does | Trade-off | Outcome |
|---|---|---|---|
| Listed bullets | The audit packet lists every changelog bullet that names a group term (about 205 for `models` at 2.1.296, and 300 to 400 per group on today's changelog). Each is marked with the names it carries that the guide lacks. The verifier answers each one, and settle holds the audit when one goes unanswered. | Reaches P11 and P8. Each monthly audit reads 300 to 400 more lines, about 20,000 input tokens, and writes as many short answers. Needs settle and contract changes. | **Picked (D2)** |
| Narrow list | Lists only the 81 bullets that name a span the guide lacks. | Cheaper, but P8 is not listed, so I3 cannot close. | Dropped |
| Contract wording only | A "family" rule: account for each sibling setting of a guide line. | No packet change, but plan 45's wording change hit P11 in 0 of 2 reps. | Dropped |

For I1 and I2, the owner ruled on the copy (D1). The alternative, naming the files for the verifier to read in the
checkout, lost because settle could not check the files against fixed bytes. I5 and I6 fix their own shape in their
done-whens.

## Design

### Part A: listed bullets in an audit packet (I3, I4)

- **A1.** `packets.audit()` writes `listed.md` and an index key `listed`. A listed bullet is a bullet of any
  release in the packet's `changelog.md` that holds a backticked span equal to one of the group's terms: the union
  of `group_terms` over the group's sections. Each entry holds:
  - `item`: `<release>#<n>`, where n is the bullet's place among its release's bullets, as triage numbers them;
  - `line`: the bullet's line in the packet's `changelog.md`;
  - `sections`: the group's sections whose terms the bullet names;
  - `lacks`: the bullet's backticked spans of 3 to 60 characters, not in `STOP_TERMS`, that are not a backticked
    span anywhere in the guide.
- **A2.** `listed.md` gives each item one line: its ID, `changelog.md:<line>`, its sections, `names the guide
  lacks: …` when `lacks` is not empty, and the bullet's text. Items keep the changelog's order, newest first.
- **A3.** The contract's audit section adds a rule: give each listed item a B row whose `changelog.md:line` is the
  item's line when the bullet changes a claim in scope, and otherwise the line `<item> | none`. The rule is
  generic and names no setting.
- **A4.** Settle, audit mode only: a B row on an item's line, or its none line, answers the item. An unanswered
  item holds the sections in its `sections` that are in the packet's scope, so settle prints no `baseline
  audited`. Settle prints the counts answered by a B row, answered none and unanswered, with the unanswered IDs. A
  none line for an ID that is not listed is unparseable, as today. *(designer's call: an item holds only its own
  sections.)*
- **A5.** The B row's form does not change. The `<item> | none` line reuses the none-line form. The contract,
  `.claude/skills/cc-guide/references/formats.md` and `report_grammar.py` stay in step, as
  `test_skill_files.py`'s format test checks.
- **A6.** The skill's audit section and `formats.md` describe `listed.md` and its cost.
- **A7.** `releases.md` does not change. A bullet in both files is one item, and a B row on its line answers both.
  *(designer's call)*
- **A8.** A function that computes the list from a changelog text, the group's terms and a guide text is public, so
  the kit can apply it to the 2026-10-13 packet (D4).

### Part B: covered files in a files packet (I1, I2)

- **B1.** A citing file that is a skill's `SKILL.md`, under `skills/` or `.claude/skills/`, covers every `.md` file
  in its skill folder and its subfolders, except `SKILL.md`, any `README.md` and anything under `scripts/`.
  *(designer's call, from R4.1's "in `references/` or beside it"; a README is for people and is not loaded on
  demand.)*
- **B2.** `packets.files()` copies each covered file into the packet as `covered/<path within the skill folder>`,
  and the index gains `covered: {<repo path>: <copy path>}`. Any other citing file gets `covered: {}`.
- **B3.** The contract's files section: rows cover the statements in the cited file and in each covered file, and a
  row names the file it is in by its repo path. The none-line rule stays one per cited section, across all the
  files.
- **B4.** Settle, files mode: a row's file may be `index['file']` or a key of `covered`. A contradiction names the
  file to fix. `same_file` compares every copy with its file in the checkout. A difference, or a covered file
  added to or removed from the skill since the packet was built, holds the citing file. `baseline cite` still
  names only the citing file. *(designer's call: an added or removed file holds.)*
- **B5.** The skill's ground rules let a files fix edit the reviewed file or a file that its citation covers.
- **B6.** Tests in `build/cc_guide/`:
  - a files packet for a fixture skill holds exactly its covered copies (a `references/` file, a file beside
    `SKILL.md`, a nested file) and leaves out `README.md` and a `scripts/` Markdown file; the index names them;
  - settle accepts a row on a covered file, discards a row on a file that is neither cited nor covered, and holds
    the citing file when a covered file has changed.
- **B7.** One packet per skill, whatever its size. The largest adds about 206 KB. The ask-above-6 rule still caps
  the verifiers in one batch. *(designer's call)*

### Part C: component scope in the files rule (I6)

- **C1.** The files section gains one rule: compare a statement with what the guide says about the component the
  statement describes. A repo's own script, hook or agent is not Claude Code, so a guide fact about how Claude Code
  behaves contradicts a statement only when the statement describes that behaviour. The wording is the builder's,
  and it names no fixture fact.
- **C2.** `test_skill_files.py` pins the rule by a key phrase, as its TODO and none-line tests do.

### Part D: the micro-test (I3 to I6)

- **D1. Kit.** A new kit, built under the writing-skills micro-test procedure. It reuses plan 45's design where it
  still applies: its Pre-registration and settled defaults DF2 to DF21, as D5 changes them. Two aims pull apart, and
  the kit settles them so *(designer's call)*:
  - Fidelity. The verifier runs as in production: the arm's agent file, its `model` pin, the owner's current
    default effort, and the advisor tool if production verifiers have it. Before any counted rep, a pilot rep is
    compared with a production `/cc-guide` dispatch, as plan 45's pilot was.
  - Isolation. Each rep runs in its own scratch folder under the system temp directory, which holds copies of its
    packet and of the docs snapshot, so no rep needs a read under the home folder. The kit denies home-folder
    reads. The main session that dispatches the verifier gets no Bash tool, or a probe rep shows that a Bash read
    of the home folder is denied.

  The master packets, the snapshot and the collected raw output stay under `~/.cache/agent-skills/`, since they
  hold docs text. Kit scripts may be committed. The record carries counts, labels, line pointers and paths only, as
  plan 45's record does.
- **D2. Next-kit fixes.** The kit closes the three open next-kit items in `specs/deferred_items.md`:
  - "Parallel micro-test reps share the scratch folder": each rep gets its own scratch folder, and a no-model test
    shows that two reps cannot see each other's files;
  - "The next micro-test kit still copies `credential_expires_at`": the rep-file writer drops the field, and a
    no-model test proves it;
  - "The deny rule `Read(~/**)` does not stop every Bash read": the kit closes the gap and a probe rep shows a
    `for`-loop `ls ~/…` denied, or the owner records that the gap stays.

  It also sets `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` above the audit timeout, since the 10-minute default voided
  all four of plan 45's first gate reps.
- **D3. Arms.** Control: `.claude/agents/cc-guide-verifier.md` at this spec's base commit. Changed: the same file
  with Parts A, B and C. Each packet exercises its own mode's section, so one changed arm serves both gates.
- **D4. Fixtures.**
  - *Audit (gate A).* The changed arm reads a copy of `20261013T113847-audit` with `listed.md` and `listed` added,
    computed by A8 from that packet's own `changelog.md` and `guide.md` and the group's terms under `5bd78a7`'s
    `build/cc_guide/manifest.toml`. The control arm reads the packet unchanged. *(designer's call)* Both arms read
    the 2.1.296 docs snapshot.
  - *Readme (gate F).* `20261013T121854-files/hooks__README.md`, both arms. It has no covered files.
  - *Precision (gate F).* A new files packet for a citing skill whose citation names no `hooks.*` or
    `permissions.*` section and whose covered files state Claude Code facts. It is built once at a pinned commit
    and cache and frozen in the kit, with a precision key fixed before any rep runs: which statements, if any,
    truly contradict their section. *(designer's call: `skills/writing-skills/SKILL.md`, whose
    `references/claude-code.md` states Claude Code facts throughout; `skills/executing-plans/SKILL.md` if its key
    is cheaper to build.)*
- **D5. Gate A** (the audit section lands or reverts):
  - In a valid changed rep, P11 is met by a B row on P11's line or by a correction that names `deniedModels`, and
    P8 is met by a B row on P8's line.
  - PASS needs P11 met in at least 4 of 5 valid changed reps and P8 met in at least 4 of 5. *(designer's call: I3's
    done-when, read as needing both entries.)*
  - This replaces plan 45's DF10 for P11: a B row on P11's line counts, as I3's done-when allows. A correction
    counts only when it is rated SUPPORTED against the docs, as under DF10. *(designer's call)*
  - Control, after DF2: the control arm meets P11 in at most 1 of its valid reps. At 2, the fixture no longer
    separates the arms, and the gate stops UNSETTLED for the owner. *(designer's call)*
  - Precision, DF7: the changed arm's kept UNSUPPORTED corrections are at most the control's plus 3, and no changed
    rep has more than 2.
  - Retention, DF8: for each of P1 to P6, P9, P13 and P14, the changed arm's hits are at least the control's minus 1.
  - Reported, not gated: B rows per rep and unanswered listed items per rep.
- **D6. Gate F** (the files section lands or reverts):
  - Readme: no valid changed rep keeps a `contradicts` row on `hooks/README.md:89`, and no changed rep has more than
    2 UNSUPPORTED `contradicts` rows (I6's done-when). *(designer's call: this is a guard. Today's contract keeps
    no false row on this packet, so a pass shows that C1 does no harm, not that it cures plan 45's failure. I6's
    done-when asks for a fixed negative control, and the rule that caused the failure is not coming back, so the
    kit adds no arm to provoke it.)*
  - Precision fixture: UNSUPPORTED `contradicts` rows per rep in both arms (I5's done-when), and no changed rep above
    2. *(designer's call: the same ceiling as the readme.)*
  - Reach: in at least 2 of 3 valid changed reps on the precision fixture, a row names a covered file. *(designer's
    call)*
  - Part B's contract text and Part C share the files section and one arm. If gate F fails, the owner rules at the
    gate whether to revert Part C alone and rerun, or revert both.
- **D7. Budget.** About $50 to $70 at plan 45's per-rep costs: an audit rep cost $2.95 to $3.51 and a files rep
  $0.24 to $1.20, before the longer list. D1's choices can change that basis: the advisor was about $1 of each
  plan 45 audit rep. The plan estimates again after the pilot. The owner approves a ceiling before any rep runs.
- **D8. Binary.** The plan pins one held copy of the current Claude Code for every rep, as plan 45 did.

### Part E: landing and closing

- **E1.** Part A lands as a unit, its code with its contract text: with the old contract, its settle rule would
  hold every audit. If gate A fails, Part A reverts whole.
- **E2.** Part B's packet and settle code may land even if gate F fails, since the old contract ignores the copies.
  Its contract text follows gate F.
- **E3.** Not in the plan (D4). After the plan merges with gate F passed, a session of its own runs `/cc-guide
  files` on each citing skill whose covered files state Claude Code facts (I1's done-when). That session lists the
  skills by a search, keeps the ask-above-6 rule and runs alone under the machinery rule. The plan's completion
  report names this pass as the next step.
- **E4.** The plan's completion protocol closes each item on its own done-when: I3 on gate A; I4 on gate A's P11
  clause; I5 on gate F's precision counts; I6 on C2 and gate F's readme clause. Each next-kit item in D2 closes when
  its done-when is met. I1 and I2 close together (D1), so both stay open with a `→ progress` note that names E3's
  pass, though Part B and its tests meet I2's own done-when. Both close when that pass is done.

## Constraints

- The repo is public. Packets, reports and docs text stay in the cache. The spec, plan and record carry counts,
  labels and pointers only.
- `.claude/agents/cc-guide-verifier.md` and `.claude/skills/cc-guide/` are project-local, so `runtimes/` needs no
  regeneration. Their `# cc-guide:` citations follow the usual lint, and `check_conformance.py` must pass.
- `build/cc_guide/conformance.toml` and `build/cc_guide/baseline.json` are hot spots that other lanes also edit.
  This work should not need either, except a `baseline cite` that an edit to a citing file calls for.
- This is a domain lane. It edits no execution machinery. `skills/writing-skills/` and `skills/executing-plans/` are
  read only, as fixtures.

## Left to the builder

- The exact contract wording for A3, B3 and C1, within the rules above, and the key phrases the tests pin.
- Where the covered-file helper lives, and the copy layout's details.
- Rep counts per arm within the ceiling, VOID rules, the grading scripts and how the precision key is built.
- Where the record goes, under the repo's conventions in `CLAUDE.md`.
