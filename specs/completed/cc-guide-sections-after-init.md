# Guide sections created after `baseline init` — Design Spec

**Status:** COMPLETE (2026-11-15), implemented by plan 99 (`specs/plans/completed/99-cc-guide-sections-after-init.md`).
It was APPROVED on 2026-11-15. The owner approved this file, its designer's calls included, the same day. The
question was "Do you approve the spec, with its designer's calls?", and the owner answered "Approve it".

The design came from a brainstorming session on 2026-11-15. It is the Design pick of the 2026-11-14 `/deferred`
pass: the item "Sections created after `baseline init` (plan 38, T7-m3)" in `specs/deferred_items.md`,
§ 38-claude-code-drift-automation — 2026-10-05. The owner settled four decisions (D1 to D4). Text marked
*(designer's call)* is the designer's choice, and "Designer's calls" lists each one. Line numbers and counts are
as of `a9c0d18`, the commit this design read.

The work amends two retired specs: the drift spec, `specs/completed/claude-code-drift-automation-spec.md`, and
the conformance spec, `specs/completed/claude-code-guide-conformance.md`. "Spec amendments" gives the changes.
The plan applies them. This file names a requirement of the drift spec as "drift R7", and one of the conformance
spec as "conformance R1.2".

> **For agentic workers:** plan from this file with the writing-plans skill. It yields one plan.

## Intent

The drift detector (`build/cc_guide/`) keeps the Claude Code customization guide
(`specs/guides/claude-code-customization-guide.md`) equal to the docs. Its state file, `baseline.json`, holds one
entry for each guide section. Each entry has four values (drift R2.3):

- `checked`: the release through which the section's changelog backlog and docs blocks are resolved.
- `changed`: the release of the section's last substantive change. A citing file stamped below it is STALE.
- `audited`: the release and date of the last full re-verification of the section's group.
- `text_hash`: a hash of the section's normalized text.

Only `baseline init` creates section entries, and only `init` derives them from git history. So the set of
sections is frozen at the bootstrap of 2026-10-03. The guide must be able to grow and shrink. This work gives the
drift contract a way for a section to enter and leave `baseline.json`. It also cuts the history tests loose from
the working-tree guide.

**Why now.** This is the oldest open backlog item. Its section date is 2026-10-05, so on 2026-11-20 it passes
the 45-day horizon. From then on, finishing-a-development-branch's Step 1b gate blocks every merge and PR until a
`/deferred` pass changes the item's state or the owner carries it once.

## Current state (recon, 2026-11-15)

1. **No subcommand admits a new section.** `known()` (`build/cc_guide/baseline.py:97`) refuses an ID that
   `baseline.json` lacks, so `accept`, `advance` and `audited` refuse it. `cite` refuses it too (line 340).
   `lint` reports `section <id>: missing from baseline.json` (`lint.py:31`, `id_set_problems`) and names no
   command.
2. **`init --force` refuses a new section as well.** `derive_changed` (`baseline.py:34`) maps each section of
   the working-tree guide to the refresh guide (`c33bc99`) by (parent `##`, heading). It raises on a heading
   the refresh lacks. A new section has no match. A heading edit, which drift R1.1 allows, also has no match.
   Both cases were reproduced on 2026-11-15:
   `R11.1: section hooks.pitfalls ('### Pitfalls to avoid') is not in the c33bc99 guide`.
3. **`init --force` would also destroy state.** All 38 sections have `checked` at 2.1.323, and 25 have
   `changed` at 2.1.323. `init` resets `checked` and `audited` to 2.1.288 and `changed` to the R11.1 values. It
   writes `cited` as `{}`, and it rebuilds every group's blocks and `snapshot` pointers from the 2.1.288
   snapshot. So it clears the STALE flags of files stamped since the bootstrap and loses every review record.
4. **A removed section is stuck the same way.** `lint` reports `section <id>: missing from the guide and
   manifest.toml`. No subcommand removes a section entry, and drift R2.1 forbids a hand edit.
5. **Two history tests read the working-tree guide.** In `build/cc_guide/test_baseline.py`,
   `test_r11_derivation_from_the_real_history` (line 88) and
   `test_the_replay_flags_the_citers_of_drifted_sections_and_not_the_control` (line 97) pass the working-tree
   guide as `derive_changed`'s third input. The first reads it without `encoding='utf-8'`. A heading edit fails
   both.
6. **A third test pins the 38 IDs on the working-tree guide.**
   `test_real_guide_carries_the_drift_r11_anchors` (`build/test_check_conformance.py:86`) asserts 38 headings
   and the exact R1.1 ID list (`R11_IDS`, line 24). It also reads without `encoding='utf-8'`. A new section or
   a removed one fails it.
7. **Commit `18b4a71` is a stable history reference.** It is plan 35's commit "anchor Claude Code artifacts to
   the customization guide", and drift R1.1 names it. It is on `main`'s first-parent line. The guide there, at
   `specs/guides/claude-code-customization-guide.md`, has the 38 anchors. Its `##` and `###` headings are
   identical to the refresh's at `c33bc99` (diffed 2026-11-15). The current guide's headings are still
   identical too, so all three tests pass today.
8. **`check` already handles the blocks.** A new section's backticked terms select new blocks, which `check`
   reports as `new`. A removed section's terms leave blocks that `check` reports as `deselected`
   (informational, `check.py:181`). `rebaseline` settles both. `check` and `packets` iterate
   `baseline.json`'s sections and skip a manifest section it lacks (`check.py:289`).
9. **CI runs only the commit lints** (`.github/workflows/lints.yml`). The history tests run in local full
   clones, where `history()` (`test_baseline.py:64`) skips a commit the clone lacks.
10. **`dump_baseline`** (`state.py:364`) keeps insertion order. `parse_baseline` refuses an empty `sections`.

## Owner decisions

- **D1 (2026-11-15): a new section's `audited` copies its group's oldest `audited`.** The question was "How
  should a new section's `audited` date start?" The owner answered "Inherit group's date". The alternative was
  the creation release and date. It was rejected because the stamp region would then suggest a verifier pass
  that never happened.
- **D2 (2026-11-15): two named subcommands, `baseline add` and `baseline drop`.** The owner answered "A + H1" to
  "Which approach should the spec take?" (see Approaches).
- **D3 (2026-11-15): the guide at `18b4a71` replaces the working-tree guide as the history reference.** The same
  answer (H1).
- **D4 (2026-11-15): a new section's `checked` copies its group's oldest `checked`, and `add` takes no `--to`.**
  The question was "What `checked` should a new section start with?" The owner answered "Group's oldest". The
  builder check found that the draft's rule, the newest cached release, had two side effects.
  `packets.triage` counts its untriaged releases from the highest `checked` of any section (`packets.py:215`),
  so a new section at the newest release removed triage's 20-release split. And on a machine whose cache is
  older than the other sections' `checked`, it lowered the stamp region. A copy has neither effect. An author
  who checked the section through a later release records that with `advance`. The rejected alternatives were
  the highest `checked` in the file, which claims a check the author may not have done, and the draft's rule.

## Goals, non-goals and anti-goals

**Goals.**
- G1. A section created after `init` enters `baseline.json` through one R7 subcommand. No other section's
  state changes.
- G2. A section removed from the guide and the manifest leaves `baseline.json` through one R7 subcommand.
- G3. A heading edit breaks neither `init` nor any test. No test reads the working-tree guide to learn the
  bootstrap's sections.
- G4. `lint` names the command that clears an ID-set violation, where one command does.

**Non-goals.**
- No `rename` subcommand. Drift R1.1 says an ID never changes. A deliberate rename is `drop` and then `add`.
  The old ID's citers then fail `lint` until they are edited and cited again.
- No change for a section that moves to another group in `manifest.toml`. No stored value names a section's
  group, so `lint` passes, and the section keeps its `audited`.
- No `baseline.json` format change. `format` stays 3.
- `init` stays. It is still the from-scratch rebuild, and it keeps R11.1's values for the 38 bootstrap sections.
- `add` and `drop` do not touch any group's `blocks` or `snapshot`. `check` and `rebaseline` do that, as today.
- No section is added or dropped in the live guide by this work.

**Anti-goals.** The work fails, even if it runs, when any of these is true:
- Adding or dropping a section changes another section's values or any group's blocks.
- `add` writes a `checked` or `audited` value that claims a check or an audit that did not happen (D1, D4).
- The history reference is a commit that a merge style can lose, such as a SHA made on the fix branch.
- The fix needs a hand edit of `baseline.json` (drift R2.1).

## Approaches

**How a section enters or leaves `baseline.json`:**

| Approach | How | Trade-off |
|---|---|---|
| **A. Named subcommands (picked, D2)** | `baseline add <ids>` and `baseline drop <ids>`. `lint` prints each command. | One more verb each way. It matches R7's style (`accept` and `advance` take IDs), and nothing changes that the editor did not name. |
| B. One reconcile subcommand | `baseline sections`, no arguments: adds what the guide and manifest have, drops what only `baseline.json` has. | Less to type. But the editor never names what changes, and a drop deletes `cited` records unasked. |
| C. Stretch existing verbs | `accept --substantive` creates a missing entry. | No new verb for adding. But removal still has none, and `accept` stops meaning only "record a text change". |

**Which history reference replaces the working-tree guide:**

| Approach | How | Trade-off |
|---|---|---|
| **H1. The guide at `18b4a71` (picked, D3)** | It becomes `derive_changed`'s third input, the map from heading to ID. | The smallest change. R11.1 keeps its method. `init` still reads three commits from git. |
| H2. Freeze R11.1's result as data | A constant holds the six IDs at 2.1.219. A test proves it from git. | `init` needs no git history. But the repo holds two records of one fact, and `init` changes more. |

## Design

### S1. `baseline add <ids>`

`add` creates a `baseline.json` entry for each named section. It refuses, with a `cc-guide:` line, exit 2 and
nothing written, when:
- An ID is not an anchor in the guide, or not a section of a group in `manifest.toml`.
- An ID is already in `baseline.json`.
- There is no cached changelog. `changed` needs the newest cached release.
- A citation does not parse. `changed` reads the citers' stamps, so `add` applies the rule of a substantive
  `accept` (`cli.py:348`).

Each new entry takes these values:
- `text_hash`: the section's current text, hashed as drift R2.3 says.
- `checked`: a copy of the oldest `checked` among the group's sections that `baseline.json` already has (D4).
  "Oldest" uses the stamp region's order for `checked`: by release, then by date.
- `changed`: `next_changed(<newest cached release>, <review stamps of the files that cite the ID>)`, drift R2.4's
  rule. Usually no file cites the ID yet, because `cite` refuses an ID that `baseline.json` lacks. Then
  `changed` is the newest cached release. A citation written by hand before `add` is flagged STALE, because its
  review came before the section's entry *(designer's call)*.
- `audited`: a copy of the oldest `audited` among the group's sections that `baseline.json` already has (D1).
  "Oldest" uses the stamp region's order for `audited`: by date, then by release (`guide.render_stamp`).

When the group has no such section, as for a new group, both copies come from the oldest value in the whole
file *(designer's call)*. All IDs of one run read the file as it was before the run.

`add` writes `baseline.json` only. It rebuilds the `sections` map in the guide's heading order, so the file
reads as `init` would write it *(designer's call)*. `checked` and `audited` are copies of values the file
already holds, so `add` cannot move the stamp region, and no `stamp` run follows it.

The flow for a new section is:
1. Write the section in the guide, with its anchor (drift R1.1).
2. Add its ID to one group in `manifest.toml`.
3. Run `baseline add <id>`. If you checked the section against a later release than its group's oldest
   `checked`, run `baseline advance <id> --to <release>`, then `baseline stamp`.
4. Run `check`. It reports the blocks that the section's terms now select as `new`. Review them, then run
   `rebaseline`.
5. Run `cli.py lint` and `check_conformance.py`.

### S2. `baseline drop <ids>`

`drop` removes the named sections' entries. It refuses, with a `cc-guide:` line, exit 2 and nothing written,
when:
- An ID is still an anchor in the guide, or still a section in `manifest.toml`.
- An ID is not in `baseline.json`.
- The run would leave `sections` empty (`parse_baseline` refuses that).

It removes each ID's `sections` entry and the ID from every file's map in `cited`. A file whose map becomes
empty leaves `cited` *(designer's call)*. It writes `baseline.json` only. It does not edit citing files. `lint`
already reports each one (`<path>: cites <id>, which is not a guide section`). The editor fixes each citation
and runs `cite`. A dropped section can hold the oldest `checked` or `audited`, so `stamp` follows `drop`. The
next `check` reports the blocks that only the dropped section's terms selected as `deselected`. A full
`rebaseline` of the group drops them (drift R7).

`manifest.toml` cannot hold a group with no sections. So when `drop` removes a group's last section, the group
has already left the manifest. `drop` leaves that group's `groups` entry in place *(designer's call)*. Only
`rehash` reads a stored group that the manifest lacks, and it handles one already (`baseline.py:307`).

### S3. `lint` names the command

`id_set_problems` (`lint.py:31`) adds a command to two of its messages. The message ends with the command in
backticks, built from the `CLI` constant, as `hash_problems` prints `baseline accept`:
- An ID in the guide and `manifest.toml` but not `baseline.json`: the command is `<CLI> baseline add <id>`.
- An ID only in `baseline.json`: the command is `<CLI> baseline drop <id>`.

Every other combination needs a guide or manifest edit first, so its message stays as it is.

### S4. The history reference

- `baseline.py` gains a constant beside `JULY` and `REFRESH`, for example
  `ANCHORED = ('18b4a71', 'specs/guides/claude-code-customization-guide.md')`. Its comment says what the commit
  is: plan 35's, the first with anchors, with headings identical to the refresh's. The path differs from
  `OLD_GUIDE_PATH` because `79ad04f` moved the guide before `18b4a71`.
- `derive_changed` keeps its signature. Its docstring says the third input is the guide at `ANCHORED`. Its
  result keys the 38 bootstrap IDs. The refusal of a section that the refresh lacks stays, as a guard on the
  `ANCHORED` constant.
- `init` (`cli.py:311`) passes the guide at `ANCHORED` as the third input. For each section of the
  working-tree guide, `changed` is the derived value when the ID has one, and `init`'s `--release` otherwise.
  `init` baselines every section's text at `--release`, so a section with no derived value has no earlier
  release to keep *(designer's call)*.
  `init` no longer refuses a heading edit or a section created after the bootstrap. The `git_show` error names
  the reference it lacks, as today.

### S5. Tests that stop reading the working tree

- `test_baseline.py`: `history()` takes the path with the ref. `test_r11_derivation_from_the_real_history` and
  the replay test pass the guide at `ANCHORED` as the third input. Neither reads the working tree, so the
  missing `encoding='utf-8'` goes with the read. Their assertions stay as they are.
- `build/test_check_conformance.py`: `test_real_guide_carries_the_drift_r11_anchors` reads the guide at
  `18b4a71` from git and skips, with a reason, when the clone lacks the commit, as `history()` does. Its three
  assertions stay. Its docstring says it pins the bootstrap record. The working tree's anchors stay covered by
  two commit lints: `check_conformance.py` (well-formed, unique anchors) and `cli.py lint` (one ID set in the
  guide, the manifest and `baseline.json`).

## Testing

Each behaviour gets a failing test before its code (test-driven-development). The tests are offline, use the
suite's fixtures (`cc_fixtures.py`), and never use the live guide or `baseline.json`.

- `add`: the four values, including D1's and D4's copies, the whole-file fallback for a new group, and
  `next_changed` above a hand-written citer stamp. Each refusal. Heading order in `sections`. No other section's values and no
  group's blocks change.
- `drop`: the removed entry and `cited` IDs, an emptied `cited` map leaving, each refusal, and no other change.
- Write sets (drift R12.2, `test_cli.py`): `add` and `drop` write `baseline.json` only.
- `lint`: the two new messages, and an unchanged message for the other combinations.
- `init`: on a fixture guide with an edited heading and an extra section, `init` succeeds. The bootstrap
  sections keep their derived `changed`, and the extra section takes `--release`.
- The history tests and the conformance test pass with the working-tree guide's headings edited. A test can
  show this by monkeypatching the path they would have read, or by reading their source. The builder picks the
  form.
- The suites `cc_guide` and `build` pass (`build/run_suites.py`). The commit lints pass
  (`build/run_commit_lints.sh`).

## Spec amendments

The plan applies these to the two retired specs, with a dated note under each spec's status line that names this
file.

**Drift spec.**
- **R1.1.** After "Each section belongs to exactly one group (R2.5).", add: "The table records the 38 sections
  at the bootstrap. `manifest.toml` lists the live sections. A section created later takes an anchor, an ID in
  one group, and `baseline add` (R7). A removed one leaves through `baseline drop`."
- **R2.6.** Add: "A section created after `init` enters through `baseline add` (R7)."
- **R5.** After the ID-set bullet's sentence, add: "When the guide and the manifest have an ID that
  `baseline.json` lacks, the message prints the `baseline add` command. When only `baseline.json` has it, the
  message prints the `baseline drop` command."
- **R7.** The sentence "`advance` and `audited` can move the oldest `checked` or `audited` ..." becomes
  "`advance`, `audited` and `drop` can move ...". Two bullets go after `init`:
  - "`add <ids>`: create each named section's entry, for a section created after `init`. The ID must be an
    anchor in the guide and in one `manifest.toml` group, and not yet in `baseline.json`. `text_hash` is the
    section's text, and `changed` follows R2.4. `checked` and `audited` copy the oldest of each among the
    group's sections, in the stamp region's order, or the oldest in the file when the group has none. So `add`
    claims no check or audit, and never moves the stamp region. `advance` records a later check (owner,
    2026-11-15). It touches no blocks: `check` reports what the section's terms select as `new`, and
    `rebaseline` settles it."
  - "`drop <ids>`: remove each named section's entry, and the ID from every file in `cited`, once the guide and
    `manifest.toml` no longer have it. It touches no blocks and no citing file."

  And two sentences close the `init` bullet: "`init --force` is not the way to add or drop a section. It resets
  every section's `checked`, `changed` and `audited` to the bootstrap and empties `cited`."
- **R11.1.** Add: "The guide at `18b4a71` (plan 35, the first with anchors, headings identical to `c33bc99`'s)
  maps each aligned section to its ID. So a later heading edit changes nothing. `init` gives a section without
  a derived value its `--release`."
- **R12.2.** The R2-and-R7 bullet adds "and `add` and `drop`".
- **R12.3.** The replay bullet's first sentence becomes "Rebuild the guide at `91474f6` and `c33bc99` from git
  (our text, at its pre-move path), map their sections to IDs through the guide at `18b4a71`, derive `changed`
  as R11.1 does, and ...". Add: "No history test reads the working-tree guide."

**Conformance spec.**
- **R1.2.** "A test parses the real guide" becomes "A test parses the guide at `18b4a71`, the commit that added
  the anchors". Add: "The working tree's anchors are the lint's to check (R3.3), and drift R5's."

**Repo docs.**
- `build/cc_guide/cli.py`: the module docstring and `--help` list `add` and `drop`.
- `build/CLAUDE.md`: the `cc_guide/` paragraph gains one or two sentences on `add` and `drop` in the flow.
  `build/CLAUDE.md` is a Claude Code artifact, so `check_conformance.py` runs before the commit.

## Constraints

- Only `baseline` writes `baseline.json` (drift R2.1). Every subcommand leaves its changes uncommitted (R7).
- `build/cc_guide/` imports nothing from `build/`, and its tests are offline, with bare imports and basenames
  unique across `build/` (drift R12.1).
- The repo's Python style (`rules/clean-code-python.md`): single quotes, f-strings, 4-space indentation.
- No live section changes. The guide, `manifest.toml` and `baseline.json` stay as they are. Tests use fixtures.
- Prose in the specs and `build/CLAUDE.md` follows the plain technical English rule
  (`rules/write-with-asd-ste100.md`).
- Provenance: the drift detector is the owner's original code (MIT, `LICENSE`). This work brings in no outside
  text or code, so `NOTICE` does not change.

## Done when

- The backlog item's own condition: drift R7 says how a section created after `init` enters `baseline.json`,
  and the history test no longer depends on the working-tree guide's headings.
- S1 to S5 are built, with the tests in Testing. Both suites and the commit lints pass.
- The spec amendments are applied.
- The plan's completion ticks the backlog item `→ done`.

## Designer's calls

The owner's approval of this file approves these.

1. Removal (`drop`, G2, S2) is in scope. The owner was told it would be and did not object, but did not rule on
   it explicitly.
2. `add`'s `changed` uses the newest cached release, drift R2.4's rule. So `changed` can be above the copied
   `checked`, as it is today between a substantive `accept` and the `advance` after it.
3. A citation written before `add` is flagged STALE, through `next_changed`.
4. A group with no section in `baseline.json` copies the oldest `checked` and `audited` in the whole file.
5. `add` rebuilds `sections` in the guide's heading order.
6. A file whose `cited` map `drop` empties leaves `cited`.
7. `init` gives a section without a derived value its `--release`.
8. The conformance test reads `18b4a71`, not the working tree, and the commit lints keep the working tree
   covered.
9. `drop` leaves the `groups` entry of a group that has left the manifest. That case is out of scope.

## Left to the builder

- Where the `18b4a71` constant lives so that `build/test_check_conformance.py` can use it. That file may import
  `baseline` through the path `check_conformance.py` already uses, or restate the SHA with a comment.
- The exact refusal and `lint` message wording, within S1 to S3.
- How the `init` test gets git history: a fixture repo with three commits, or a test of `baseline.init` with a
  `changed` map computed from fixture texts.
- Whether `add` shares code with a substantive `accept` for reading citer stamps.

## Not in this spec

- A `rename` subcommand, a reconcile subcommand, or a change for group moves.
- Retiring `init`.
- A `baseline.json` format change.
- Adding, removing or renaming a section in the live guide.
- Removing the `groups` entry of a group that has left `manifest.toml` (S2). The entry costs only space. The
  plan's completion logs it as a deferred item.
