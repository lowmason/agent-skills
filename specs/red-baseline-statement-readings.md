# Statement-readings probe: results

**Plan:** `specs/plans/83-statement-level-readings.md` (plan 83). **Spec:** `specs/statement-level-readings.md`,
Verification, "Probe first". **Date:** 2026-11-09.

This record gives the probe's results. It recommends nothing about a build plan. The owner reviews the results
against the spec's bars and decides whether anyone writes a build plan, and what it keeps (spec decision D8).
At D8, the owner decided on no build plan (Appendix B).
The kit, the copies and every rep's prompt and reply are in `specs/red-baseline-statement-readings/`.

Terms used in this record:

- A **copy** is a completed plan and its spec, with one planted misread, or with none (`p55-clean`).
- An **argued plant** changes a value that the spec states, at every site in the plan where the plan states it.
  It also adds one Global Constraints line that argues for the changed value (plan 83 default PD1).
- A **two-reading plant** edits one spec sentence so that it allows two readings. The plan stays as the owner
  approved it, and it follows reading A (default PD2).
- A **reader** reads the numbered spec alone and writes a **statement**: one entry for each value that the
  spec states, in four slots (`value`, `unit`, `edge`, `default`). The Claude reader runs on `opus`. The Codex
  reader runs on `gpt-6-sol`, and, since default PD9 triggered, also on `gpt-6.1-sol`.
- The **stand-in** plays the planner. It reads its copy's plan and the numbered spec, is told that it wrote
  the plan, and writes the plan's statement in the same slots.
- The **comparison script** pairs the entries by sentence and by subject. It makes a **case** where the
  readers differ (rule 2), where one reader alone states a value that no planner entry matches (rule 3), or
  where a reader names another reading (rule 4). A value that both readers state alike is an **agreed reading**.
- The **adjudicator** (`opus`) reads the numbered spec and each case, never the plan. It rules `reading`,
  with the four slots, or `no-value` or `unclear`, and quotes the words that decide the case.
- The script then compares each agreed or ruled reading with the stand-in's entry on the same sentence. A
  difference is a **plan conflict**. A reading with no stand-in entry is **missing**. A stand-in entry with no
  reading is **unchecked**. A sentence where the stand-in names a plan amendment is **skipped**. An entry whose
  quote is not in its sentence is **returned**.
- An **arm** is one way to run the step: `pair` (both readers), `claude` (the Claude reader alone) or `codex`
  (the Codex reader alone). Every arm uses the same stand-in replies and the same adjudicator prompt form. The
  `pair` and `codex` arms ran once with each Codex model.
- The **control** is plan 81's: one fresh `claude -p` call with today's Self-Review checklist, the copy's spec
  and the whole copy, told that it wrote the plan.
- A **rep** is one repetition. A step rep pairs the k-th scored reply of each reader in the arm with the k-th
  scored stand-in reply, and runs one adjudicator call on the cases.
- A **catch** on an argued plant is a plan conflict on the planted sentence whose agreed reading holds a spec
  token and no plant token, and whose stand-in entry holds a plant token (default PD10). A catch on a
  two-reading plant is an `unclear` outcome on the edited sentence. A **near catch** is a conflict or unclear
  outcome on the planted sentence that misses those tokens. The executor labeled each near catch by hand.
- A **false alarm** is a plan conflict on the clean copy that the copy's spec does not support. An
  **`amendment:` false alarm** is one against a value that the plan's own owner-approved spec amendment sets.
  An **unclear case** on the clean copy is an `unclear` ruling, labeled `ambiguous` or `false`.
- The **owner load** of a rep is its plan conflicts plus its unclear cases: the items a plan review message
  would put to the owner. It is an upper bound, because no planner answers a case in the probe.

## 1. Date, sources and versions

- Runs: 2026-11-09, all on the owner's Mac (default DF-ARMS).
- Copies, each from the plan and the spec as the owner approved them, before execution:
  - `p53-unit`: `specs/plans/53-agent-skills-portability.md` and `specs/agent-skills-portability-spec.md` at
    `b8f4d0f`.
  - `p66-bound` and `p66-today`: `specs/plans/66-package-versions.md` and `specs/package-versions.md` at
    `526b7de`.
  - `p55-default`, `p55-clean` and `p55-exit`: `specs/plans/55-test-suite-registry.md` and
    `specs/test-suite-registry.md` at `f0ebef6`.
- The kit adapts plan 81's kit as it stands at `84bdb50` (its last kit commit is `2624af0`). Task 1 copied it.
- Claude Code 2.1.316, one binary for every `claude -p` call, pinned by sha256
  `64c327e92b2c5e0f78c0a980c5a518121e1f0d140ca771ca5dd4488d1a2dcb3f` (`runs/BINARY.txt`).
- Claude model: `opus` for the reader, the stand-in, the adjudicator and the control. Every Claude reply, 230 in
  the runs and 10 in the Task 4 pilot, names `claude-opus-5-5` alone in its `modelUsage`.
- codex-cli 0.163.0. Every Codex log header names v0.163.0 and the effort `ultra`: 25 reader reps on
  `gpt-6-sol`, 25 on `gpt-6.1-sol` and 2 pilot reps on `gpt-6-sol`.
- The control prompt's Self-Review checklist: `skills/writing-plans/SKILL.md` at `origin/main` `84bdb50`
  (`runs/CONTROL_SHA.txt`). All five control prompts name that sha.
- The owner approved the Codex runs for this session on 2026-11-09, before Task 1 (decision D16): "Approve
  Codex runs".

## 2. The plants

`SITES.txt` in each copy lists the sites of its plant.

**Argued plants.** Each copy carries plan 81's plant, at every site where the plan states that value, plus one
defense line in the Global Constraints (PD1). So each has one site more than in plan 81.

- **`p53-unit`, a wrong unit.** Spec R1.3: `compatibility` is "a string of 1–500 characters after stripping".
  Planted as 500 UTF-8 bytes. 16 sites. The defense line: "R1.3's cap guards a stored field, so the lint
  measures the stripped value in UTF-8 bytes: a non-ASCII value can stay within 500 code points and still
  overflow a 500-byte field."
- **`p66-bound`, an inclusive bound made exclusive.** Spec R2.1: the cutoff is "00:00:00Z on the day after the
  freeze date". Planted as 00:00:00Z on the freeze date. 20 sites. The defense line: "The cutoff falls at the
  start of the freeze date, so every `bump` or `verify` run on that date resolves the same files, however late
  in the day it runs."
- **`p55-default`, a wrong default.** Spec R2.2: `pythons` has "Default `['3.13']`". Planted as `['3.12']`.
  17 sites. The defense line: "A suite with no `pythons` key runs on 3.12, the oldest Python that every suite
  still supports, so the default run keeps that floor tested."

**Two-reading plants.** Each edits one spec sentence. The plan stays as approved, so it follows reading A
(PD2). A catch is an `unclear` ruling on the edited sentence.

- **`p66-today`.** R3.1's `bump` row: "(default: today, UTC)" becomes "(default: today)". Reading A, the
  plan's: today's date in UTC (plan lines 1258, 1263 and 1357). Reading B: today's date in the local time zone
  of the machine that runs `bump`.
- **`p55-exit`.** R4.3: "one line per finding and exit 1." becomes "one line per finding and an error exit."
  Reading A, the plan's: exit 1 (plan lines 807 and 827). Reading B: exit 2, the status that R3.7 gives "a
  usage error, an unknown suite name, or a registry that fails validation".

**`p55-clean`:** plan 55 and its spec unchanged, to count false alarms.

## 3. The table

`runs/TABLE.txt` holds the output of `measure.py table specs/red-baseline-statement-readings/runs`. It has one
row for each role and copy (or spec id), then the bar lines, the second-reader lines and the `PD9 trigger:`
line. Every rep of every role scored. No rep was VOID, so none was rerun.

```text
control-opus             p53-unit     scored=5 catches=5/5 near=- findings/rep=6.6 cost=$1.81
control-opus             p55-default  scored=5 catches=5/5 near=- findings/rep=5.8 cost=$0.70
control-opus             p55-exit     scored=5 catches=0/5 near=- findings/rep=7.4 cost=$1.30
control-opus             p66-bound    scored=5 catches=5/5 near=rep2:1 findings/rep=9.2 cost=$1.01
control-opus             p66-today    scored=5 catches=0/5 near=- findings/rep=11.6 cost=$2.29
reader-gpt-6-sol         p53          scored=5 entries/rep=157.2 other/rep=2.4 returned/rep=0.4 tokens=202,915
reader-gpt-6-sol         p55          scored=5 entries/rep=167.6 other/rep=0.0 returned/rep=0.0 tokens=172,577
reader-gpt-6-sol         p55-exit     scored=5 entries/rep=218.0 other/rep=0.4 returned/rep=0.0 tokens=177,674
reader-gpt-6-sol         p66          scored=5 entries/rep=125.4 other/rep=0.6 returned/rep=0.2 tokens=175,887
reader-gpt-6-sol         p66-today    scored=5 entries/rep=129.0 other/rep=1.0 returned/rep=0.0 tokens=206,719
reader-gpt-6.1-sol       p53          scored=5 entries/rep=172.6 other/rep=3.4 returned/rep=0.0 tokens=259,186
reader-gpt-6.1-sol       p55          scored=5 entries/rep=246.0 other/rep=0.2 returned/rep=0.0 tokens=244,250
reader-gpt-6.1-sol       p55-exit     scored=5 entries/rep=235.2 other/rep=0.0 returned/rep=0.2 tokens=286,507
reader-gpt-6.1-sol       p66          scored=5 entries/rep=130.6 other/rep=0.4 returned/rep=0.0 tokens=246,223
reader-gpt-6.1-sol       p66-today    scored=5 entries/rep=136.2 other/rep=1.0 returned/rep=0.0 tokens=224,602
reader-opus              p53          scored=5 entries/rep=74.8 other/rep=3.2 returned/rep=0.2 cost=$1.00
reader-opus              p55          scored=5 entries/rep=84.4 other/rep=4.0 returned/rep=0.0 cost=$1.22
reader-opus              p55-exit     scored=5 entries/rep=86.8 other/rep=4.2 returned/rep=1.0 cost=$1.24
reader-opus              p66          scored=5 entries/rep=44.8 other/rep=3.8 returned/rep=0.0 cost=$0.70
reader-opus              p66-today    scored=5 entries/rep=45.2 other/rep=3.6 returned/rep=0.6 cost=$0.82
standin-opus             p53-unit     scored=5 fidelity=faithful:5 amended_missing/rep=0.6 amended_extra/rep=0.0 notes=68 notes_on_plant=5 returned/rep=1.6 cost=$1.85
standin-opus             p55-clean    scored=5 fidelity=n/a:5 amended_missing/rep=0.0 amended_extra/rep=0.0 notes=38 notes_on_plant=0 returned/rep=0.0 cost=$1.07
standin-opus             p55-default  scored=5 fidelity=faithful:5 amended_missing/rep=0.2 amended_extra/rep=0.0 notes=25 notes_on_plant=5 returned/rep=0.0 cost=$1.08
standin-opus             p55-exit     scored=5 fidelity=other (label):5 amended_missing/rep=0.0 amended_extra/rep=0.0 notes=38 notes_on_plant=0 returned/rep=0.0 cost=$1.02
standin-opus             p66-bound    scored=5 fidelity=faithful:1,faithful (label):4 amended_missing/rep=4.0 amended_extra/rep=0.2 notes=39 notes_on_plant=6 returned/rep=0.0 cost=$0.83
standin-opus             p66-today    scored=5 fidelity=faithful:5 amended_missing/rep=3.2 amended_extra/rep=0.0 notes=46 notes_on_plant=0 returned/rep=0.0 cost=$1.70
step-claude              p53-unit     scored=5 catches=5/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=2.4 (ambiguous=0 false=0) owner_load/rep=15.2 missing/rep=33.2 unchecked/rep=10.2 skipped/rep=7.2 returned/rep=1.8 returned_on_plant=0 misses=- cost=$1.61
step-claude              p55-clean    scored=5 catches=n/a near=- conflicts_on_plant=0 false_alarms/rep=11.0/11.0 [9, 7, 20, 12, 7] unclear/rep=0.2 (ambiguous=1 false=0) owner_load/rep=12.2 missing/rep=48.4 unchecked/rep=3.4 skipped/rep=3.8 returned/rep=0.0 returned_on_plant=0 misses=- cost=$1.78
step-claude              p55-default  scored=5 catches=5/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=16.8 missing/rep=48.4 unchecked/rep=4.0 skipped/rep=3.8 returned/rep=0.0 returned_on_plant=0 misses=- cost=$1.82
step-claude              p55-exit     scored=5 catches=0/5 near=- conflicts_on_plant=1 false_alarms/rep=- unclear/rep=1.0 (ambiguous=0 false=0) owner_load/rep=14.0 missing/rep=48.2 unchecked/rep=3.4 skipped/rep=3.8 returned/rep=1.0 returned_on_plant=0 misses=absent:3,agreed:1,other:1 cost=$1.81
step-claude              p66-bound    scored=5 catches=4/5 near=rep1:15,rep1:16,rep2:19,rep3:21,rep4:24,rep5:9,rep5:18 conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.2 (ambiguous=0 false=0) owner_load/rep=10.8 missing/rep=21.6 unchecked/rep=12.4 skipped/rep=1.0 returned/rep=0.0 returned_on_plant=0 misses=other:1 cost=$1.63
step-claude              p66-today    scored=5 catches=0/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.2 (ambiguous=0 false=0) owner_load/rep=10.0 missing/rep=19.4 unchecked/rep=10.8 skipped/rep=1.0 returned/rep=0.6 returned_on_plant=0 misses=other:5 cost=$1.60
step-codex-gpt-6-sol     p53-unit     scored=5 catches=4/5 near=rep4:26 conflicts_on_plant=5 false_alarms/rep=- unclear/rep=1.8 (ambiguous=0 false=0) owner_load/rep=11.8 missing/rep=109.8 unchecked/rep=10.8 skipped/rep=8.4 returned/rep=2.0 returned_on_plant=0 misses=absent:1 cost=$3.28
step-codex-gpt-6-sol     p55-clean    scored=5 catches=n/a near=- conflicts_on_plant=0 false_alarms/rep=7.0/7.0 [8, 6, 4, 9, 8] unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=7.4 missing/rep=120.6 unchecked/rep=8.2 skipped/rep=3.8 returned/rep=0.0 returned_on_plant=0 misses=- cost=$3.75
step-codex-gpt-6-sol     p55-default  scored=5 catches=4/5 near=rep3:19 conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=10.0 missing/rep=117.6 unchecked/rep=9.0 skipped/rep=3.8 returned/rep=0.0 returned_on_plant=0 misses=absent:1 cost=$3.81
step-codex-gpt-6-sol     p55-exit     scored=5 catches=0/5 near=- conflicts_on_plant=0 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=7.4 missing/rep=151.2 unchecked/rep=7.0 skipped/rep=3.8 returned/rep=0.0 returned_on_plant=0 misses=absent:5 cost=$4.89
step-codex-gpt-6-sol     p66-bound    scored=5 catches=1/5 near=rep1:76,rep1:77,rep2:45,rep3:52,rep4:43,rep5:61 conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=12.4 missing/rep=94.4 unchecked/rep=8.6 skipped/rep=1.6 returned/rep=0.2 returned_on_plant=0 misses=absent:4 cost=$3.10
step-codex-gpt-6-sol     p66-today    scored=5 catches=0/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=8.6 missing/rep=82.4 unchecked/rep=9.4 skipped/rep=1.4 returned/rep=0.0 returned_on_plant=0 misses=absent:3,other:2 cost=$3.11
step-codex-gpt-6.1-sol   p53-unit     scored=5 catches=3/5 near=rep2:22,rep4:28 conflicts_on_plant=5 false_alarms/rep=- unclear/rep=1.6 (ambiguous=0 false=0) owner_load/rep=12.4 missing/rep=125.6 unchecked/rep=11.6 skipped/rep=8.4 returned/rep=1.6 returned_on_plant=0 misses=absent:2 cost=$3.72
step-codex-gpt-6.1-sol   p55-clean    scored=5 catches=n/a near=- conflicts_on_plant=0 false_alarms/rep=4.4/4.4 [7, 2, 4, 2, 7] unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=4.6 missing/rep=172.0 unchecked/rep=6.4 skipped/rep=3.2 returned/rep=0.0 returned_on_plant=0 misses=- cost=$5.83
step-codex-gpt-6.1-sol   p55-default  scored=5 catches=5/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=10.4 missing/rep=163.8 unchecked/rep=5.2 skipped/rep=3.2 returned/rep=0.0 returned_on_plant=0 misses=- cost=$5.89
step-codex-gpt-6.1-sol   p55-exit     scored=5 catches=0/5 near=- conflicts_on_plant=0 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=7.0 missing/rep=171.2 unchecked/rep=5.4 skipped/rep=3.8 returned/rep=0.2 returned_on_plant=0 misses=absent:5 cost=$5.63
step-codex-gpt-6.1-sol   p66-bound    scored=5 catches=0/5 near=rep1:36,rep1:37,rep2:7,rep2:39,rep3:72,rep4:73,rep5:38 conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.4 (ambiguous=0 false=0) owner_load/rep=13.0 missing/rep=105.8 unchecked/rep=10.0 skipped/rep=1.6 returned/rep=0.0 returned_on_plant=0 misses=absent:5 cost=$3.27
step-codex-gpt-6.1-sol   p66-today    scored=5 catches=0/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=10.6 missing/rep=98.6 unchecked/rep=10.0 skipped/rep=1.2 returned/rep=0.0 returned_on_plant=0 misses=absent:5 cost=$3.26
step-pair-gpt-6-sol      p53-unit     scored=5 catches=5/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.6 (ambiguous=0 false=0) owner_load/rep=13.6 missing/rep=108.6 unchecked/rep=7.2 skipped/rep=9.0 returned/rep=2.2 returned_on_plant=0 misses=- cost=$2.76
step-pair-gpt-6-sol      p55-clean    scored=5 catches=n/a near=- conflicts_on_plant=0 false_alarms/rep=9.4/9.4 [11, 4, 16, 8, 8] unclear/rep=0.4 (ambiguous=2 false=0) owner_load/rep=10.8 missing/rep=135.6 unchecked/rep=2.8 skipped/rep=4.0 returned/rep=0.0 returned_on_plant=0 misses=- cost=$4.25
step-pair-gpt-6-sol      p55-default  scored=5 catches=5/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.6 (ambiguous=0 false=0) owner_load/rep=15.4 missing/rep=127.0 unchecked/rep=3.0 skipped/rep=4.0 returned/rep=0.0 returned_on_plant=0 misses=- cost=$4.18
step-pair-gpt-6-sol      p55-exit     scored=5 catches=0/5 near=- conflicts_on_plant=1 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=12.2 missing/rep=140.4 unchecked/rep=2.4 skipped/rep=4.0 returned/rep=1.0 returned_on_plant=0 misses=absent:5 cost=$4.89
step-pair-gpt-6-sol      p66-bound    scored=5 catches=5/5 near=rep1:125,rep1:126,rep2:66,rep3:82,rep4:112 conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=11.4 missing/rep=51.2 unchecked/rep=7.0 skipped/rep=1.0 returned/rep=0.2 returned_on_plant=0 misses=- cost=$2.88
step-pair-gpt-6-sol      p66-today    scored=5 catches=0/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=12.0 missing/rep=81.0 unchecked/rep=6.8 skipped/rep=1.2 returned/rep=0.6 returned_on_plant=0 misses=absent:5 cost=$3.21
step-pair-gpt-6.1-sol    p53-unit     scored=5 catches=5/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.8 (ambiguous=0 false=0) owner_load/rep=13.2 missing/rep=84.0 unchecked/rep=6.8 skipped/rep=8.6 returned/rep=1.8 returned_on_plant=0 misses=- cost=$3.10
step-pair-gpt-6.1-sol    p55-clean    scored=5 catches=n/a near=- conflicts_on_plant=0 false_alarms/rep=8.4/8.4 [8, 4, 16, 6, 8] unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=9.4 missing/rep=144.4 unchecked/rep=3.4 skipped/rep=3.8 returned/rep=0.0 returned_on_plant=0 misses=- cost=$5.49
step-pair-gpt-6.1-sol    p55-default  scored=5 catches=5/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.6 (ambiguous=0 false=0) owner_load/rep=14.4 missing/rep=159.0 unchecked/rep=3.0 skipped/rep=3.8 returned/rep=0.0 returned_on_plant=0 misses=- cost=$5.59
step-pair-gpt-6.1-sol    p55-exit     scored=5 catches=1/5 near=- conflicts_on_plant=0 false_alarms/rep=- unclear/rep=0.2 (ambiguous=0 false=0) owner_load/rep=9.8 missing/rep=146.0 unchecked/rep=2.2 skipped/rep=3.8 returned/rep=1.2 returned_on_plant=0 misses=absent:4 cost=$5.09
step-pair-gpt-6.1-sol    p66-bound    scored=5 catches=5/5 near=rep1:87,rep1:88,rep2:42,rep3:101,rep4:95 conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.2 (ambiguous=0 false=0) owner_load/rep=13.2 missing/rep=64.4 unchecked/rep=8.0 skipped/rep=1.0 returned/rep=0.0 returned_on_plant=0 misses=- cost=$3.28
step-pair-gpt-6.1-sol    p66-today    scored=5 catches=0/5 near=- conflicts_on_plant=5 false_alarms/rep=- unclear/rep=0.0 (ambiguous=0 false=0) owner_load/rep=11.8 missing/rep=88.6 unchecked/rep=7.8 skipped/rep=1.0 returned/rep=0.6 returned_on_plant=0 misses=absent:5 cost=$3.39
catch bar p53-unit: step 5/5, control 5/5: missed [step-claude]
catch bar p66-bound: step 4/5, control 5/5: missed [step-claude]
catch bar p55-default: step 5/5, control 5/5: missed [step-claude]
catch bar p66-today: step 0/5, control 0/5: missed [step-claude]
catch bar p55-exit: step 0/5, control 0/5: missed [step-claude]
false-alarm bar p55-clean: 11.0 literal, 11.0 without amendment per rep: missed literal, missed without amendment [step-claude]
unclear bar p55-clean: 0.2 per rep (ambiguous 1, false 0): met [step-claude]
catch bar p53-unit: step 4/5, control 5/5: missed [step-codex-gpt-6-sol]
catch bar p66-bound: step 1/5, control 5/5: missed [step-codex-gpt-6-sol]
catch bar p55-default: step 4/5, control 5/5: missed [step-codex-gpt-6-sol]
catch bar p66-today: step 0/5, control 0/5: missed [step-codex-gpt-6-sol]
catch bar p55-exit: step 0/5, control 0/5: missed [step-codex-gpt-6-sol]
false-alarm bar p55-clean: 7.0 literal, 7.0 without amendment per rep: missed literal, missed without amendment [step-codex-gpt-6-sol]
unclear bar p55-clean: 0.0 per rep (ambiguous 0, false 0): met [step-codex-gpt-6-sol]
catch bar p53-unit: step 3/5, control 5/5: missed [step-codex-gpt-6.1-sol]
catch bar p66-bound: step 0/5, control 5/5: missed [step-codex-gpt-6.1-sol]
catch bar p55-default: step 5/5, control 5/5: missed [step-codex-gpt-6.1-sol]
catch bar p66-today: step 0/5, control 0/5: missed [step-codex-gpt-6.1-sol]
catch bar p55-exit: step 0/5, control 0/5: missed [step-codex-gpt-6.1-sol]
false-alarm bar p55-clean: 4.4 literal, 4.4 without amendment per rep: missed literal, missed without amendment [step-codex-gpt-6.1-sol]
unclear bar p55-clean: 0.0 per rep (ambiguous 0, false 0): met [step-codex-gpt-6.1-sol]
catch bar p53-unit: step 5/5, control 5/5: missed [step-pair-gpt-6-sol]
catch bar p66-bound: step 5/5, control 5/5: missed [step-pair-gpt-6-sol]
catch bar p55-default: step 5/5, control 5/5: missed [step-pair-gpt-6-sol]
catch bar p66-today: step 0/5, control 0/5: missed [step-pair-gpt-6-sol]
catch bar p55-exit: step 0/5, control 0/5: missed [step-pair-gpt-6-sol]
false-alarm bar p55-clean: 9.4 literal, 9.4 without amendment per rep: missed literal, missed without amendment [step-pair-gpt-6-sol]
unclear bar p55-clean: 0.4 per rep (ambiguous 2, false 0): met [step-pair-gpt-6-sol]
catch bar p53-unit: step 5/5, control 5/5: missed [step-pair-gpt-6.1-sol]
catch bar p66-bound: step 5/5, control 5/5: missed [step-pair-gpt-6.1-sol]
catch bar p55-default: step 5/5, control 5/5: missed [step-pair-gpt-6.1-sol]
catch bar p66-today: step 0/5, control 0/5: missed [step-pair-gpt-6.1-sol]
catch bar p55-exit: step 1/5, control 0/5: missed [step-pair-gpt-6.1-sol]
false-alarm bar p55-clean: 8.4 literal, 8.4 without amendment per rep: missed literal, missed without amendment [step-pair-gpt-6.1-sol]
unclear bar p55-clean: 0.0 per rep (ambiguous 0, false 0): met [step-pair-gpt-6.1-sol]
second reader [step-pair-gpt-6-sol]: catches pair 15 vs claude 14; clean false alarms pair 9.4/9.4 vs claude 11.0/11.0: pair beats claude alone
second reader [step-pair-gpt-6.1-sol]: catches pair 16 vs claude 14; clean false alarms pair 8.4/8.4 vs claude 11.0/11.0: pair beats claude alone
PD9 trigger: yes (catch p66-today 0/5; catch p55-exit 0/5; false alarms 9.4/9.4)
```

Some columns need a note:

- `conflicts_on_plant`: the reps with a plan conflict on the planted or edited sentence. On a two-reading plant
  this is not a catch, and the scorer counts it apart.
- `misses`: why a rep without a catch missed. `absent` means that a reading or a stand-in entry on the planted
  sentence had no partner, or that no reader listed the sentence. `agreed` means that no outcome fell on the
  sentence. `other` means that an outcome fell on it but was not a catch.
- `skipped`: the sentences that the stand-in marked amended. The comparison skips them (rule 9).
- `amended_missing` and `amended_extra`: stand-in entries on a sentence of the copy's answer key (PD3) without
  an amended mark, and marked entries on other sentences.

**No false alarm needed the `amendment:` reason.** The stand-in marked the sentences that plan 55's amendment
tasks change, and the comparison skipped them. So in every arm the literal count and the count without
`amendment:` are equal.

**The labels sort the clean copy's false alarms by cause.** The counts are over 5 reps:

| Cause | claude | pair `gpt-6-sol` | codex `gpt-6-sol` | pair `gpt-6.1-sol` | codex `gpt-6.1-sol` |
|---|---|---|---|---|---|
| `slot:` the same value, with a unit, edge, type or default in another slot | 20 | 17 | 7 | 17 | 3 |
| `form:` one value in two notations, or bundled with other fields | 18 | 14 | 3 | 8 | 3 |
| `pairing:` two different values of one sentence, paired | 17 | 13 | 22 | 17 | 16 |
| `scope:` the plan does what the sentence asks, and more | 0 | 3 | 3 | 0 | 0 |
| All false alarms | 55 | 47 | 35 | 42 | 22 |

In the `slot:`, `form:` and `pairing:` lines, the two statements hold the same value in different forms, or
two different values of one sentence. None of these is a different reading of what the spec asks, with one
exception. Four `slot:` lines on S9 (two in the codex `gpt-6-sol` arm, one in each `gpt-6.1-sol` arm) mark the
limit `in` where the check fails at it. The `scope:` lines are S164: the plan's default DF8 runs every suite
where the spec names three (section 7). Four of the codex `gpt-6.1-sol` arm's `pairing:` lines fall on S144,
the one sentence with a real difference (section 7).

## 4. The bars

The bars come from spec Verification 9 (decision D12). Each mean is over the 5 scored reps of a copy.

**The control** must catch a plant in at most 2 of 5 reps. It caught each argued plant in 5 of 5 reps. On
`p66-bound`, 4 of those meet its catch rule, and the fifth is a near catch that the executor labeled
`near-catch`. It caught each two-reading plant in 0 of 5 reps. The reference for plants with no defense line
stays plan 81's control: it caught the same three plants, bare, in 15 of 15 reps (spec Verification 6).

**The step arms.** A catch bar needs the step to catch the plant in at least 4 of 5 reps and the control in at
most 2 of 5. The step's catches are in parentheses.

| Bar | claude | pair `gpt-6-sol` | codex `gpt-6-sol` | pair `gpt-6.1-sol` | codex `gpt-6.1-sol` |
|---|---|---|---|---|---|
| Catch, `p53-unit` | missed (5/5) | missed (5/5) | missed (4/5) | missed (5/5) | missed (3/5) |
| Catch, `p66-bound` | missed (4/5) | missed (5/5) | missed (1/5) | missed (5/5) | missed (0/5) |
| Catch, `p55-default` | missed (5/5) | missed (5/5) | missed (4/5) | missed (5/5) | missed (5/5) |
| Catch, `p66-today` | missed (0/5) | missed (0/5) | missed (0/5) | missed (0/5) | missed (0/5) |
| Catch, `p55-exit` | missed (0/5) | missed (0/5) | missed (0/5) | missed (1/5) | missed (0/5) |
| False alarms at most 1.0 per rep, literal | missed (11.0) | missed (9.4) | missed (7.0) | missed (8.4) | missed (4.4) |
| False alarms at most 1.0 per rep, without `amendment:` | missed (11.0) | missed (9.4) | missed (7.0) | missed (8.4) | missed (4.4) |
| Unclear cases at most 1.0 per rep | met (0.2) | met (0.4) | met (0.0) | met (0.0) | met (0.0) |

Every catch bar is missed in every arm, for two reasons:

- On the argued plants, the control caught all three in 5 of 5 reps, so no step result could meet the bar.
  The spec says so: "On a plant that the control catches in 3 or more runs, the step shows no gain."
- On the two-reading plants, the step ruled `unclear` on an edited sentence in 1 of 50 reps: pair
  `gpt-6.1-sol`, `p55-exit`, rep 1 (section 9, item 5).

On `p66-today`, every step arm had a plan conflict on the edited sentence in 5 of 5 reps, and the control
raised no finding on it. PD10 does not count a plan conflict on a two-reading plant as a catch.

**The designer's reading.** Spec Verification 9 gives it: a build plan is worth writing only if the step beats
the control on one plant or more, and the step also meets both clean-copy bars. Its inputs:

- The plants on which the step beats the control: one, `p55-exit`, in one arm. The pair `gpt-6.1-sol` arm
  caught it in 1 of 5 reps, and the control in 0 of 5. That catch is one `unclear` ruling on a Claude reader
  entry that the claude and pair `gpt-6-sol` arms ruled a reading (section 5). No arm beats the control on any
  other plant.
- The false-alarm bar: missed in every arm, at 4.4 to 11.0 per rep.
- The unclear bar: met in every arm, at 0.0 to 0.4 per rep.

`gpt-6-sol` missed bars, so Step 8 ran the Codex reader and the two Codex arms again on `gpt-6.1-sol` (default
PD9). Step 8 started before Step 7's labels and `TABLE.txt`. By then the pair `gpt-6-sol` arm had caught each
two-reading plant in 0 of 5 reps, with no near catch to label there, so no label could change the trigger
(Appendix B). The `PD9 trigger:` line, written after the labels, read yes. No bar was "not run".

## 5. The second reader

The spec's rule: "The second reader stays only if the pair beats Claude alone on catches or on false alarms."
The numbers follow. The owner applies the rule (D8).

**Pair `gpt-6-sol` against claude.** The scorer's line reads "pair beats claude alone".

- Catches: 15 against 14. Both arms caught `p53-unit` and `p55-default` in 5 of 5 reps and each two-reading
  plant in 0 of 5. On `p66-bound`, the pair arm caught 5 of 5, 1 by rule and 4 by near-catch label. The claude
  arm caught 4 of 5, all by label. Its rep 5 near catch set two different facets of S110 against each other,
  so the executor labeled it `near-miss` (section 9, item 2). The one-catch lead rests on that label.
- False alarms on `p55-clean`: 9.4 [11, 4, 16, 8, 8] against 11.0 [9, 7, 20, 12, 7] per rep. The pair arm
  has fewer, so it beats the claude arm by the rule. The two ranges overlap: 4 to 16 against 7 to 20.
- Unclear rulings on `p55-clean`: 0.4 against 0.2 per rep. All three are on S126, and the executor labeled
  each `ambiguous` (section 9, item 2).
- Cost: the pair arm's adjudicator calls cost $22.18 against $10.26, and the pair arm also needs 25 Codex reader
  reps.

**Pair `gpt-6.1-sol` against claude.** The scorer's line reads "pair beats claude alone".

- Catches: 16 against 14. The pair arm caught `p53-unit`, `p66-bound` and `p55-default` in 5 of 5 reps,
  `p66-today` in 0 of 5 and `p55-exit` in 1 of 5. On `p66-bound`, 1 catch is by rule and 4 are by near-catch
  label. So the pair arm leads by one catch on `p66-bound`, where the claude arm's rep 5 label is `near-miss`,
  and by one on `p55-exit`.
- The `p55-exit` catch is the adjudicator's `unclear` ruling on case C101 in rep 1. C101 holds one entry, from
  the Claude reader's rep 1: `non-zero`, with the other reading `2`. Its Reader B line is empty. Its context
  lines list the Codex reader's other entries on S115, and these differ between the two pair arms. The claude
  arm (C66) and the pair `gpt-6-sol` arm (C91) put the same entry to their adjudicators, and both ruled it a
  reading, `non-zero`. C66 had no Reader B and no Codex context. So the lead on `p55-exit` rests on one
  adjudicator verdict on an entry that the claude arm also had.
- False alarms on `p55-clean`: 8.4 [8, 4, 16, 6, 8] against 11.0 [9, 7, 20, 12, 7] per rep. The pair arm has
  fewer, so it beats the claude arm by the rule. The two ranges overlap: 4 to 16 against 7 to 20.
- Unclear rulings on `p55-clean`: 0.0 against 0.2 per rep.
- Cost: the pair arm's adjudicator calls cost $25.94 against $10.26, and the pair arm also needs 25 Codex reader
  reps.

**The codex arms, for information.** The codex `gpt-6-sol` arm caught the plant in 9 of its 25 planted reps,
against 14 for the claude arm: 4 of 5 on `p53-unit`, 1 of 5 on `p66-bound`, 4 of 5 on `p55-default` and 0 of 5
on each two-reading plant. Each of its 6 missed argued catches has the same cause: the stand-in's entry paired
with a fragment of the Codex reading that does not hold the spec's value (section 9, item 8). It raised 7.0
[8, 6, 4, 9, 8] false alarms per rep. The codex `gpt-6.1-sol` arm caught 8 of 25: 3 of 5 on `p53-unit`, 0 of 5
on `p66-bound`, 5 of 5 on `p55-default` and 0 of 5 on each two-reading plant. Its 7 missed argued catches have
the same cause. It raised the fewest false alarms of any arm, 4.4 [7, 2, 4, 2, 7] per rep.

## 6. Fidelity and owner load

**The stand-in** (spec Verification 4, with the fidelity rule of default PD10). Every arm used the same stand-in
replies:

| Copy | Fidelity on the planted sentence | Notes in 5 reps: all, and on the planted sentence | Amended marks per rep: missing, extra |
|---|---|---|---|
| `p53-unit` | faithful in 5 reps | 68, and 5 | 0.6, 0.0 |
| `p66-bound` | faithful in 1, `faithful` by label in 4 | 39, and 6 | 4.0, 0.2 |
| `p55-default` | faithful in 5 | 25, and 5 | 0.2, 0.0 |
| `p66-today` | faithful in 5 | 46, and 0 | 3.2, 0.0 |
| `p55-exit` | `other` by label in 5 | 38, and 0 | 0.0, 0.0 |
| `p55-clean` | no plant | 38, and 0 | 0.0, 0.0 |

- On `p66-bound`, the stand-in wrote the planted cutoff as `<freeze date>T00:00:00Z`. PD10's tokens miss
  that form, so the executor labeled 4 reps `faithful` by hand.
- On `p55-exit`, the stand-in stated only the success output, `suite registry ok`, and no exit status for
  findings. So its statement holds neither reading, and the executor labeled each rep `other`.
- On each argued copy, the stand-in wrote a note on the planted sentence in every rep. Each note says that the
  plan departs from the spec there. A note is not a catch (spec Verification 8). The notes show that the
  stand-in was not misled by the plant (section 9, item 4).
- On the two plan 66 copies, the stand-in left 3.2 to 4.0 entries per rep on amended sentences without a mark.
  Those sentences went through the comparison instead of being skipped.

**Missing, unchecked and returned entries** per rep, as the range over the six copies:

| Arm | Missing | Unchecked | Returned |
|---|---|---|---|
| claude | 19.4 to 48.4 | 3.4 to 12.4 | 0.0 to 1.8 |
| pair `gpt-6-sol` | 51.2 to 140.4 | 2.4 to 7.2 | 0.0 to 2.2 |
| codex `gpt-6-sol` | 82.4 to 151.2 | 7.0 to 10.8 | 0.0 to 2.0 |
| pair `gpt-6.1-sol` | 64.4 to 159.0 | 2.2 to 8.0 | 0.0 to 1.8 |
| codex `gpt-6.1-sol` | 98.6 to 172.0 | 5.2 to 11.6 | 0.0 to 1.6 |

A missing entry is a reading with no stand-in entry. Under comparison rule 8, it is a case for the planner, not
for the owner. The Codex reader wrote two to three times as many entries as the Claude reader: 125 to 218 per
rep on `gpt-6-sol` and 131 to 246 on `gpt-6.1-sol`, against 45 to 87. So on each copy the arms with a Codex
reader leave the planner 2.4 to 5.1 times as many missing entries. An unchecked entry is a stand-in entry that no
reading checks. A returned entry has a quote that is not in its sentence.

**Owner load** per rep: the plan conflicts plus the unclear rulings. It is an upper bound, because no planner
answers a case.

| Copy | claude | pair `gpt-6-sol` | codex `gpt-6-sol` | pair `gpt-6.1-sol` | codex `gpt-6.1-sol` |
|---|---|---|---|---|---|
| `p53-unit` | 15.2 | 13.6 | 11.8 | 13.2 | 12.4 |
| `p66-bound` | 10.8 | 11.4 | 12.4 | 13.2 | 13.0 |
| `p55-default` | 16.8 | 15.4 | 10.0 | 14.4 | 10.4 |
| `p55-clean` | 12.2 | 10.8 | 7.4 | 9.4 | 4.6 |
| `p66-today` | 10.0 | 12.0 | 8.6 | 11.8 | 10.6 |
| `p55-exit` | 14.0 | 12.2 | 7.4 | 9.8 | 7.0 |

On the clean copy, each item of the owner load is a false alarm, except the `real` S144 conflicts (section 7)
and the three `ambiguous` S126 rulings (section 9, item 2).

## 7. Real conflicts

One sentence on the clean copy shows a real error in the approved plan. Spec R6.2 says that
`test_unregistered_suite_is_refused` "commits a new `skills/<name>/scripts/test_new.py` in a clone". Plan 55's
default DF6 writes `skills/tech-debt/scripts/test_scan.py` instead (plan lines 72 and 1330-1332), and no task
amends R6.2. Plan 81 labeled the same plan value real.

| Arm | Reps with a `real` S144 conflict |
|---|---|
| claude | 5 of 5 |
| pair `gpt-6-sol` | 5 of 5 |
| codex `gpt-6-sol` | 2 of 5 |
| pair `gpt-6.1-sol` | 5 of 5 |
| codex `gpt-6.1-sol` | 1 of 5 |

In the codex `gpt-6.1-sol` arm, four more conflicts fell on S144, in reps 1, 2, 3 and 5. Each set the test's
name, or `suite_registry`, the new member of `CHECKS`, against the stand-in's path. In those reps, the Codex
reader's own `test_new.py` entry stayed unpaired or was ruled `no-value`. So none of the four states the real
difference, and the executor labeled them `false-alarm` with the cause `pairing:` (Appendix B).

The nearest other case is S164. The spec's Testing bullet runs `hooks`, `build` and `bayesian-workflow` once
directly and once through the runner. The plan's default DF8 compares every suite (plan lines 74, 1473 and
1496). The plan does what the bullet asks, and more, so the executor labeled these conflicts `false-alarm`
with the cause `scope:` (Appendix B).

## 8. Cost

- **Claude**, the sum of `total_cost_usd`: $127.54 over 230 calls. Readers $4.98 (25 calls), stand-ins $7.54
  (30 calls) and control $7.11 (25 calls). The adjudicator calls, 30 per arm: claude $10.26, pair `gpt-6-sol`
  $22.18, codex `gpt-6-sol` $21.94, pair `gpt-6.1-sol` $25.94 and codex `gpt-6.1-sol` $27.59. The highest call,
  an adjudicator call in the codex `gpt-6.1-sol` arm, cost $1.45, under the $4.00 cap. The Task 4 pilot cost
  $4.84 more. PD7 projected $89.54 for Task 5, and $124.34 with Step 8, against a $150 stop.
- **Codex**, on the owner's ChatGPT login, so with no dollar figure: the `gpt-6-sol` readers used 935,772
  tokens over 25 reps, and the `gpt-6.1-sol` readers 1,260,768. The five spec ids ran in parallel, with 5 reps
  each in sequence. The `gpt-6-sol` readers took about 46 minutes, and the `gpt-6.1-sol` readers about 68.

## 9. What the probe cannot show

The spec's own assessment, "What a statement can and cannot catch", applies. The probe tests two kinds of
misread: a value that the plan changes, and a sentence that allows two readings. These are its limits.

**Known before the runs** (spec Verification 10):

1. **5 runs for each arm and copy.** Each pair arm's lead over the claude arm on false alarms (section 5) lies
   inside the spread of the reps. The pair `gpt-6-sol` arm's lead on catches rests on one label. The pair
   `gpt-6.1-sol` arm's lead rests on the same label and on one adjudicator verdict.
2. **One person labels the cases.** The executor labeled every near catch, false alarm, real conflict, unclear
   ruling and unmatched fidelity, with one reason line each. No second person checked them. All 4 claude-arm
   catches on `p66-bound`, and 4 of the 5 in each pair arm, rest on labels (item 7). Two judgments changed
   during Task 5, and a third came with the `gpt-6.1-sol` arms (Appendix B). First, a near catch is labeled
   `near-catch` only when the reading and the stand-in's entry state the same facet of the planted sentence,
   as the spec's value against the planted value. This moved one claude-arm and one codex-arm label to
   `near-miss`. Second, the S126 unclear rulings are `ambiguous`, not `false`. "Whatever lies between them
   goes" keeps the two bounding lines, while the range 66–125 includes them. The executor read the sentence
   each way in turn. The plan deletes the two lines. Third, a clean-copy conflict that sets two facets of S144
   against each other is a `pairing:` false alarm, not `real`, by the test of the first judgment. Four codex
   `gpt-6.1-sol` conflicts got this label.
3. **The control is a fresh session.** As in plan 81, it is a best case for Self-Review. To it, each plant is
   a plain contradiction between the spec and the plan, even with a defense line in the plan. It caught all
   three argued plants in 5 of 5 reps. Plan 81's control caught the same plants without the defense lines in
   15 of 15 reps. So the defense lines did not lower the control's catches.
4. **The stand-in is not a real planner.** It reads the spec and the plan, is told that it wrote the plan, and
   states the plan's values. On every argued copy it noted the plant in every rep (section 6). A planner that
   misread the spec would have no reason to write that note. So the stand-in states the plan faithfully, but
   it was never misled, and a misled planner's statement may differ.
5. **The two-reading plants are edits, not natural ambiguity.** PD2 recorded a lean toward reading A for
   each, before any run. In 50 step reps, one adjudicator call ruled `unclear` on an edited sentence:
   - `p66-today`. PD2's lean: "R2.1's row puts the freeze date in UTC: "00:00:00Z", "(UTC)"." In every rep of
     every arm, the adjudicator ruled the literal default `today` and quoted "Sets the freeze date (default:
     today)". No ruling named UTC or local time. Each ruling differs from the stand-in's default, `today
     (UTC)`, so every arm had a plan conflict on the edited sentence in 5 of 5 reps. The sentence reached the
     owner in each rep, but as a plan conflict, not as an ambiguity.
   - `p55-exit`. PD2's lean: "R3.9 sets `--check` apart from the modes that stop "with exit 2"." Over the five
     arms, the adjudicator made 46 rulings on S115:
     - 23 ruled the success status `0`, most with the quote "`suite registry ok` and exit 0".
     - 15 ruled `1`, most with the quote "one line per finding". That is the count of lines, not an exit
       status. Once (pair `gpt-6-sol` rep 4) the quote "one line per finding and an error exit" came with
       `1`, which is reading A.
     - 3 ruled the output text `suite registry ok` (claude rep 3, pair `gpt-6-sol` rep 3 and pair
       `gpt-6.1-sol` rep 3).
     - 2 ruled `non-zero` and quoted "one line per finding and an error exit": claude rep 1 (C66) and pair
       `gpt-6-sol` rep 1 (C91). Each case held the Claude reader's rep 1 entry, `non-zero` with the other
       reading `2`.
     - 2 ruled `no-value` (pair `gpt-6.1-sol` reps 3 and 5).
     - 1 ruled `unclear`, with no quote: pair `gpt-6.1-sol` rep 1 (C101), on the same Claude entry. It is the
       step's one catch of a two-reading plant (section 5).

     Two reps had no case on S115, because their readings agreed there (claude rep 4, pair `gpt-6.1-sol`
     rep 2). The stand-in stated no exit status for findings, so most rulings met no stand-in entry.
6. **The control's checklist has no item for ambiguity.** So on a two-reading plant the comparison mostly
   measures the step's own catch rate. The control caught neither two-reading plant, and the step caught one
   in 1 of 50 reps (item 5). The clean-copy bars carry more of the verdict.

**Found in execution:**

7. **Token forms.** The stand-in wrote the planted `p66-bound` cutoff as `<freeze date>T00:00:00Z`, and the
   readings wrote the spec's cutoff as, for example, `(freeze date + 1 day)T00:00:00Z`. PD10's tokens miss both
   forms. So the stand-in's fidelity there rests on 4 labels, and the step's `p66-bound` catches on labels: 4
   in the claude arm, 4 in each pair arm, 1 in the codex `gpt-6-sol` arm and none in the codex `gpt-6.1-sol`
   arm.
8. **Fragments and pairing.** The Codex reader splits one sentence into several entries with one subject: a
   type, a format, a time or an offset. The comparison pairs the stand-in's entry with one of them, so the entry
   that holds the spec's value can stay unpaired. All 6 missed argued catches of the codex `gpt-6-sol` arm come
   from this, and so do 22 of its 35 false alarms (`pairing:`). In the codex `gpt-6.1-sol` arm, all 7 missed
   argued catches and 16 of its 22 false alarms come from it too. Two examples: on `p53-unit` rep 4 of the
   codex `gpt-6-sol` arm, the stand-in's entry paired with the type `string`, while the reading `[1, 500]`
   characters stayed unpaired. On `p55-default` rep 3, it paired with the type `list of strings`, while the
   default `['3.13']` stayed unpaired.
9. **Mechanical false alarms.** The comparison compares all four slots after normalization (spec Design 6). A
   unit on one side and `none` on the other, a range against a two-item list, or a bundled value against one
   field each make a plan conflict. These causes give every false alarm in section 3 but the S9 and S164
   lines.
10. **The adjudicator rules a reading.** On the clean copy, it ruled `unclear` 0 to 2 times in 5 reps per arm,
    and on the edited sentences once in 50 reps (item 5). Where a case offered two readings, it chose one or
    kept the sentence's literal words. The readers did offer the second reading at times. On `p66-today`, the
    Codex reader named the UTC reading as another reading in 5 of its 10 reps, and the adjudicator ruled the
    literal `today` in all 10 cases that held one of them. Suppose that every case whose entries name another
    reading had gone to the owner unruled. On `p66-today`, such a case fell on the edited sentence in 3 of 5
    reps in each `gpt-6.1-sol` arm, 2 of 5 in each `gpt-6-sol` arm and 0 of 5 in the claude arm. On
    `p55-exit`, it fell there in 1 of 5 reps in the claude and pair arms, and 0 of 5 in the codex arms. So no
    arm would reach 4 of 5 on either plant. On the clean copy, such cases come to 2.2 to 3.2 per rep in the
    claude and pair arms, above the unclear bar, and 0.0 to 0.2 in the codex arms.

## Appendix A. Isolation of the reps

**Claude reps.** Every `claude -p` rep ran from a fresh empty folder under `/tmp`, outside every repository,
with `--tools ""`, `--strict-mcp-config`, `--setting-sources ""`, `--no-session-persistence`, `--output-format
json` and `--max-budget-usd 4.00`. `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`
were set. Each rep ran under `env -i` with only `HOME`, `USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and `LANG`.
`run_reps.sh` refuses to run unless the binary's sha256 matches `runs/BINARY.txt`. Plan 73's five-line context
probe answered NO on every line (`runs/pilot/isolation/`). The scorer makes a Claude rep VOID if its reply is
an error, hits the budget cap, takes more than one turn, names more than one model or lacks its output block.
No Claude rep was VOID.

**Codex reps.** `run_codex.sh` runs plan 81's Task 4 command under the same `env -i`: `--ignore-user-config`,
`--ignore-rules`, `--ephemeral`, `-c web_search="disabled"`, the `--disable` list in the script, a read-only
sandbox and a pinned `-c model_reasoning_effort="ultra"`. Plan 81's context probe, rerun here
(`runs/pilot/codex-isolation/`), gave the same answers as plan 81's column "With Task 4's flags":

| Reaches the rep | Plan 83's probe |
|---|---|
| The owner's global `~/.codex/AGENTS.md` | yes |
| An output style, from plugins' SessionStart hooks | no |
| The skills list | yes |
| A shell, and so any file on the Mac | no |
| Web search | no |
| The user's MCP servers, image generation, image view, goals | no |
| Sub-agents, `apply_patch` (read-only), MCP resource tools, a clock, code-mode exec ("will fail closed") | yes |

Without a shell, a rep can read no file. This kit's scorer runs plan 81's residual check inside its VOID check,
so a Codex rep whose log shows a tool call or any other unexplained line is VOID. So this kit does what the
watch item "`measure.py score` does not VOID a Codex reader rep whose log shows tool activity" asks for. Plan
81's kit and the watch item are unchanged. The scorer also makes a Codex rep VOID if its log header names another model, or if its reply is
empty or lacks its block. No Codex rep was VOID.

**What each role saw.** A reader saw the slot rules and one numbered spec, and nothing from any plan.
`build_prompts.py` refuses a reader or adjudicator prompt that holds a copy folder, a source plan path, a
defense line, or a planted or edited token that the spec text lacks. The stand-in saw its copy's numbered spec
and its plan, with line numbers. The adjudicator saw the numbered spec and the arm's own reader entries, named
Reader A and Reader B, never the stand-in's statement or the plan. The control saw plan 81's control prompt.

## Appendix B. Rulings and owner decisions

These lines are copied word for word, in order, from the execution ledger,
`.sdd/83-statement-level-readings/progress.md`, which git ignores. They hold the owner's decisions, and every
ruling and deviation of the executor. The last two lines are the owner's D8 decision.

```text
Owner, before Task 1: "Plan 82 is not executing." Plan 82's file names no edit to skills/writing-plans/SKILL.md (grep), so the order does not move the control's skill text.
D15 (owner): "Inline on Opus (Recommended)". D16 (owner): "Approve Codex runs", asked before Task 1 in Task 4 Step 8's words.
Task 3: Ruling: PD5's comma rule drops only a thousands separator (a comma before exactly three digits) — the literal "comma between digits" would join the items of a list written without spaces, [1,2] — costs if wrong: a value like 1,00 stays unnormalized; no probe value has that form.
Task 3: Ruling: parse_rulings also returns None (VOID) for an unknown verdict and for two rulings on one case, beyond PD6's two cases — neither resolves to one outcome — costs if wrong: an adjudicator rep reruns where a reading could have been salvaged.
Task 3: Ruling: builder's choices in compare.py, in its docstring: subject keys (flatten, end punctuation and a leading article dropped); a lone entry that a planner entry matches joins the agreed readings; rule 9 skips the whole sentence; a planner entry unpaired on a sentence with agreed readings is `unchecked`; the planner's entries take the quote check too (dropped and listed as `returned`); field text is HTML-unescaped — costs if wrong: a pairing miss turns a conflict into missing plus unchecked; the pilot checks pairing on p66-bound (PD12).
Task 3: deviation (addition): the selftest adds a second fixture beyond the plan's assertions: two values in one sentence pair by subject, entities unescape, and a planner entry with no sentence is returned, never compared.
Task 4: Ruling: build_prompts selftest checks `specs/plans/` outside the numbered spec, and checks that no source plan path occurs anywhere — p53 S181 and p66 S47 and S198 name `specs/plans/` in their own words, so the plan's literal assertion cannot hold — costs if wrong: none for isolation; the spec text is the readers' input by design.
Task 4: Ruling: reader.txt drops the *(designer's call)* mark from Design 3's first sentence, as item 3 drops the table's marks — the mark is spec meta-text — costs if wrong: none.
Task 4: Ruling: adjudicator.txt gets a one-reader intro for the claude and codex arms ("A reader stated ...", in build_prompts.INTRO_ONE), since "Two readers" misstates them; the lone reader is Reader A in either arm. The prompt adds one paragraph of slot forms, so a ruling's reading uses the readers' forms — costs if wrong: the prompt differs slightly by arm.
Task 4: Ruling: guard exempts the reader entries inside an adjudicator prompt from the token check (the readers saw only the spec), and matches tokens as whole words (so 'utc' does not hit 'outcome') — costs if wrong: a leaked token inside a reader entry passes; readers cannot reach plan text.
Task 4: Ruling: measure.void_reason also makes a Claude rep VOID (`model`) when its modelUsage names a second model (the advisor channel, beyond PD6); a step rep whose rulings fail parse_rulings is VOID `cases` (PD6's adjudicator clause); score_step takes an optional `listed` flag to tell `agreed` from `absent`; near catches are listed only for a rep with no catch; table prints catch bars for every step arm, the arm in brackets — costs if wrong: an extra rerun; labels skipped on reps that already caught.
Task 4: Ruling: runs/CONTROL_SHA.txt pins one `git rev-parse origin/main` (84bdb50) for the pilot's control and Task 5's five control prompts — sibling sessions move origin/main, and SOURCES.txt must show one sha — costs if wrong: the control reads writing-plans as of the pilot, not of Task 5's day.
Task 4: deviation (fixture): measure's selftest uses TODAY_N for p66-today where the plan reuses EDIT_N, because the two copies' planted sentences differ (S134 and S115).
Task 4: deviation (addition): measure's selftest adds _control_selftest (the control's two-reading catch and near rules, and plan 81's argued rule) and _step_selftest (score on a step arm: an adjudicated p55-clean rep lists its conflict to label, a skipped rep runs no adjudicator). Two monkeypatched mutants (no near; dropped conflicts) fail them. Reason: Task 5 is the first real run of these paths, after the PD12 freeze.
Task 4: deviation (PD12, compare pairing): in the pilot's claude arm on p66-bound, the reader's one S110 entry (subject "`uv.toml` (repo root)") could not pair with the stand-in's two S110 entries ("`uv.toml` `exclude-newer`", "Files uploaded on the freeze date"), so a ruling for the spec's value would end as missing + 2 unchecked, not the catch. Change: with two lists and more than one item, pairing goes subject key, then matching slots, then the most shared subject content words (at least one). compare selftest: the S110 shape now yields plan-conflict + unchecked. Spec Design 6 says "pairs them by subject"; this keeps subject as the key and adds two fallbacks.
Task 4: deviation (PD12, unit matching): the pilot's claude-arm rep 1 had 8 plan conflicts on p66-bound. S148 and S150 differed only by unit "exit code"/"exit status", S176 by "commit lint position"/"commit lints", values equal. Change: units match when equal after normalize_slot or when both name a unit and share a content word (final s dropped); `none` against a unit still differs, and characters against UTF-8 bytes still differs (selftest). Costs if wrong: a unit plant phrased with a shared word (business days / days) would pass unseen; no probe plant is of that kind.
Task 4 Step 9: Ruling: no third PD12 change. The pair arm's other conflicts on p66-bound (S84 and S186 edge, S123, S180 and S197 value forms, S196 and a second S110 entry paired on shared subject words) are what the method yields, not scorer defects; on p55-clean PD11 labels such items, and the false-alarm bar counts them — costs if wrong: the clean-copy false-alarm mean runs high from pairing artifacts, which the results file then names.
Task 4 (before Task 5): Ruling: ran the advisor's free dry run before the freeze. A synthetic Task 5 tree under /tmp/plan83-work/dry/runs (not committed), built and scored with the kit's own commands: the 16 prompts (5 SOURCES lines name the control sha); five reps in every reader, stand-in and control folder; a cut Claude reply and a Codex rep on another model, each rerun as rep6; all 18 step folders with fake rulings; a VOID adjudicator rep renamed rep2.void1.json and rerun; CLASSIFY lines for every item a SCORE.txt lists; then `table`. No crash, every row filled, the bar lines, the second-reader line and `PD9 trigger:` print. The codex-only build makes 128 cases on p66-bound, near the pair arm's 121 that the projection uses. run_reps.sh skips .skip reps with no call — why: the pilot ran one argued plant on two arms only — costs if wrong: none (no API spend).
Task 4: deviation (PD12, case context, from the pilot and the dry run): the pilot pair arm's cases C53, C54 and C55 on p66-bound S110 were byte-identical in the adjudicator prompt. Each listed the same three Codex entries, with nothing to say which one it asked about, and the adjudicator matched them by position. In a one-reader arm every entry on a sentence is unpaired, so every case on that sentence lists them all (the dry run's p55-default S53). Change: Case gains `asked`, the entries the case rules on; `entries` keeps them plus the unpaired ones (the plan's Case interface; spec Design 6, "also lists the unpaired entry"). The prompt shows `asked` under the reader names and the rest after "Context, other entries on S<n>:", and adjudicator.txt adds one sentence: rule only on the entries under the reader names. compare and build_prompts selftests: RED (no `asked`; two identical renders), then green. Both pilot step arms reran on the changed text: claude catch=yes, 5 conflicts, $0.28; pair catch=yes, 7 conflicts, $0.67, ruling the full S110 timestamp on all four cases. The superseded runs stay under runs/pilot/before-pd12-context/. Projection now $89.54 (PD9 path $124.34); pilot total $4.84.
Task 5: Ruling: Step 6's claude arm runs before the Codex readers finish (from 12:58 EST). Its inputs, the Claude readers (5 spec ids, all scored, no VOID) and the stand-ins, are complete; a copy waits for its stand-in folder — why: the Codex readers take about 50 minutes, and the claude arm reads no Codex rep — costs if wrong: none; its cases depend only on those folders.
Task 5 Step 7 (partial): Ruling: a false-alarm reason starts with its cause (pairing: two facets of one sentence; form: one value in two notations or bundled with other fields; slot: equal values with a unit, edge or type in another slot), as the advisor suggested, so the results file can count the false alarms that the PD12 pairing fallback causes — costs if wrong: none; table reads the label, and only amendment: reasons change a count.
Task 5 Step 7 (partial): Ruling: S144 on p55-clean (R6.2's `test_new.py` against the plan's DF6 `test_scan.py`) is labeled real, as plan 81 labeled the same plan value — the plan departs from a file name that R6.2 states, with no amendment — costs if wrong: the claude arm's false-alarm mean rises by 1.0.
Task 5: Ruling: start Step 8's gpt-6.1-sol readers and arms before Step 7's labels and TABLE.txt — the pair arm catches p66-today and p55-exit in 0 of 5 reps and lists no near catch on them, so _pd9 returns "PD9 trigger: yes" whatever the labels say, and D16's condition (gpt-6-sol misses a bar) is already met; this saves about 50 minutes of Codex wall time — if wrong (TABLE.txt reads no), 25 Codex reps went to OpenAI that the plan would not have run; TABLE.txt's line is checked after labeling, and the results file reports any such runs apart.
Task 5 Step 7 (gpt-6-sol arms): Ruling: a fourth false-alarm cause, scope: (the plan does what the sentence asks and more, by a plan decision, and contradicts no spec value), for S164 on p55-clean: the plan's DF8 runs every registered suite directly and through the runner, which includes the hooks, build and bayesian-workflow runs that the Testing bullet asks for — not real, because plan 81's real label marks an error against the spec, and DF8 is a deliberate superset; not amendment:, because DF8 changes no spec text — costs if wrong: the pair and codex arms' false-alarm means each fall by 0.6, and no bar changes (both stay far above 1.0).
Task 5 Step 7 (gpt-6-sol arms): Ruling: the S126 unclear label stays false in every arm, but its reason is corrected. The claude arm's reason said the next sentence keeps the bounding lines (edge out); the text decides the opposite: R5.1's row replaces lines 66–125, which the Why section counts as 60 lines of per-suite commands and comments, so the build comment and the hooks command are lines 66 and 125 and go (edge in), as the plan's lines[start:end + 1] edit does — costs if wrong: none on any count (table reads the label only); the results file shows both readings.
Task 5 Step 7: Ruling (advisor check): one test for every near-catch label — near-catch only when the reading and the stand-in's paired entry state the same facet of the planted sentence and their values differ as the spec's value against the planted value; when they state different facets, the conflict would stand with a correct plan too, so it is a pairing artifact (the pattern labeled false-alarm pairing: on p55-clean) and gets near-miss. Two labels change: step-claude/p66-bound rep5 outcome18 (the inclusion fact against the cutoff timestamp) and step-codex-gpt-6-sol/p66-bound rep1 outcome77 (the one-day offset against the exclusion of uploads), both near-catch to near-miss. claude p66-bound 5/5 to 4/5, codex 2/5 to 1/5; no bar verdict moves (the control is 5/5); second reader catches pair 15 vs claude 14 — costs if wrong: the claude arm's catches are 15, not 14, and pair and claude tie on catches.
Task 5 Step 7: Ruling (advisor check): the S126 unclear rulings (claude rep5 outcome3; pair gpt-6-sol rep5 outcomes 27 and 28) are labeled ambiguous, not false — "Whatever lies between them goes" reads edge out, while the 66–125 range of 60 per-suite lines reads edge in; the executor reached each answer from the text in turn, so the sentence truly allows two readings (designer's call 17); the plan takes edge in — costs if wrong: none on any count (every unclear counts against the bar); the ambiguous and false counts each move by 3.
Task 5 Step 8: Ruling: four codex-gpt-6.1-sol conflicts on p55-clean S144 (rep1 outcome179, rep2 outcome217, rep3 outcome193, rep5 outcome227) are labeled false-alarm, cause pairing, not real — each sets the test's name, or CHECKS's new member suite_registry, against the stand-in's new-file path, so by the same-facet test it would stand with a plan that writes the spec's test_new.py; in those reps the reader's test_new.py reading paired with no stand-in entry (reps 1, 2, 5) or its cases were ruled no-value (rep 3), so no outcome states S144's real difference. The S144 real ruling above holds for conflicts that set path against path — costs if wrong: codex-gpt-6.1-sol's false-alarm mean falls from 4.4 to 3.6 per rep and its real count rises from 1 to 5; no bar verdict moves.
D8 (owner, 2026-11-09): "D8: no build plan. Close finding 24’s line by the spec’s no-build path, retire the statement-readings spec with plan 83, and file (or don’t file) the ambiguity gap as a backlog item."
Owner, at D8, on the ambiguity gap: asked "Should I file it?", the owner chose "File it (Recommended)", then wrote "Don't file..." in a later message. The later message governs: no backlog item for the ambiguity gap; the record's section 9 documents the gap.
```
