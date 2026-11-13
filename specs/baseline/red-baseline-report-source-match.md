# Micro-test: validate-data checks figures and quoted numbers against their sources

Kit: `specs/baseline/red-baseline-report-source-match/kit/`. The idea comes from lesson 4 of Eric
J. Ma's post "How to Do Agentic Data Science" (2026-02-01): every table and plot is scrutinized,
and plots are checked against the tables they reflect. `NOTICE` credits the idea. The post says a named mismatch works and
"double-check this" does not.

Each rep is a fresh, decision-only `claude -p` with no tools. It runs from an empty directory under
`/tmp`, under `env -i`, with `--setting-sources ""` and `--disable-slash-commands`. The isolation
probe (`kit/isolation_probe.txt`) answered NO on all six lines on 2.1.323, and the init record
showed no tools, no MCP servers, no skills and the default output style. `kit/show_reps.py` marks
a rep VOID when its file is unreadable, the run is an error, or a tool or the advisor ran (more
than one turn, an iteration that is not a message, or more than one model). None of the 50 reps
in rounds 1 and 2 is VOID.

All 40 Sonnet reps were read by hand in full. The 10 Opus RED reps were scored from their ACTION
lines and from the lines that name the planted values, so the false-flag statements below do not
cover them.

## Fixture

A partner asks for a pre-send validation of a small bike-share ridership report (`kit/cases.py`).
The domain is not one of validate-data's own examples. The report carries three planted mismatches
and six correct items. `build_prompts.py` checks the fixture's arithmetic before it writes a prompt.

| Item | Report says | Source says | Where the source is |
|---|---|---|---|
| M1 | Total rides rose 6.4% | 300,000 to 317,446, so +5.8% | Table 1 sums, `summary_by_district.csv` |
| M2 | Riverside grew 14.2% | 12.4% | Table 1, `summary_by_district.csv` |
| M3 | Figure 1 shows Harbor at +3.0 | Table 1 and the text give -1.3 | `make_figures.py:4` plots `summary_by_district_draft.csv` |

Two session variants:

- **full:** the agent has read every file. Only the comparison is tested.
- **partial:** the agent has read `report.md` and `build_summary.py` only. M2 shows in the report
  alone, and M1 needs the table's sums. M3 needs the agent to choose to open `make_figures.py`.

## RED: today's skill (`af378ac`, body 18,731 characters)

The approved design set the gate: the new text ships only for what today's skill misses. The full
variant ran first. The partial variant was added after it, because the full variant removes the
choice to open the sources.

| Variant | Model | M1 named | M2 named | M3 traced | Mismatches blocking | FAIL stated |
|---|---|---|---|---|---|---|
| full | Sonnet | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 (rep 4 in its ACTION line, not a report) |
| full | Opus | 5/5 | 5/5 | 5/5 | 5/5 | 3/5 (reps 3 and 5 say "Don't send" with no verdict line) |
| partial | Sonnet | 5/5 | 5/5 | 0/5 | interim message | no verdict yet |
| partial | Opus | 5/5 | 5/5 | 5/5 | interim message | no verdict yet |

"Named" means the rep gives the item, both values and the source. "Traced" in the partial variant
means an ACTION line that reads `make_figures.py`. In the full variant it means the rep says
figure 1 plots the draft file. No Sonnet rep flagged a correct item as a mismatch.

In the partial variant, every Sonnet rep planned to read both CSVs, the draft included. Two Sonnet
reps planned to view the PNGs and treated that as the figure check. Three did not plan any figure
check. Every Opus rep planned to read `make_figures.py`, and three said why: to see which CSV the
figures are drawn from.

**Decision.** Prose numbers and blocking mismatches need no new text. The control names M1 and M2
in all 20 reps, and lists the mismatches as blocking in all 10 full-variant reps. The gap is figure tracing on Sonnet. So the edit is cut to one §4 paragraph on figures
and one §6 report line. The prose-number sentence and the blocking clause of the approved design
are not added.

## GREEN bar (registered before any GREEN rep ran)

The prompts hold the edited SKILL.md body at its commit. Opus already passes, so GREEN runs on
Sonnet only.

- **partial, Sonnet, 5 reps:** at least 4 of 5 reps have an ACTION line that reads the script that
  builds figure 1 (`make_figures.py`). A line that names the file only to say it will not read it
  does not count.
- **full, Sonnet, 5 reps:** no regression. Each rep names M1, M2 and M3, gives a FAIL verdict, and
  flags no correct item.

## GREEN: the edited skill (body 19,094 characters)

The prompts were built with `build_prompts.py WORKTREE` before the commit. Their body sha256 is
`bea43a492358b5c4ad0dc4d0065d098bd413c9072bc2d53140b50b2d29e66626`, the body committed with this
record. They differ from the RED prompts only by the new §4 paragraph and the new §6 line.

| Variant | Model | M1 named | M2 named | M3 traced | Verdict |
|---|---|---|---|---|---|
| partial | Sonnet | 5/5 | 5/5 | 5/5 | interim message, no verdict yet |
| full | Sonnet | 5/5 | 5/5 | 5/5 | 4/5 FAIL, see rep 1 |

- **partial: bar met, 5/5 (RED 0/5).** Every rep has an ACTION line that reads `make_figures.py`
  "to find which file each figure plots" or in close words. Three reps also say they will compare
  the plotted values with table 1 in code.
- **full: no regression in substance, 4/5 by the letter of the bar.** Reps 2 to 5 write the §6
  report with a FAIL verdict and fill the new "Figures match sources" line with FAIL. Rep 1 opens
  with "Don't send report.md yet" and lists M1, M2 and M3 under "Blocking", but asks before it
  writes `validation_report.md`, so it has no verdict line. RED had the same shape in Opus reps 3
  and 5, so this reads as variance in whether a rep writes the report, not as an effect of the
  edit. Whether it meets the bar is the owner's call. No rep flagged a correct item. Rep 4
  has two side slips that touch no report item: it cites `make_figures.py:3` for the read on line
  4, and it says the draft total gives 6.0%, where 319,080 / 300,000 gives 6.4%.

The runs cost about $1.58 in all: RED $1.14, GREEN $0.43, the isolation probe $0.01.

## Round 2: Codex's review of PR #195

Codex reviewed the branch at `df93605` and raised two findings on the new text. The owner chose to
test and fix both.

- **P1:** the check can pass while the image in the report is stale. The script and its data match
  the table, but the delivered PNG was rendered before a fix and never rendered again.
- **P2:** the new report line has no N-A for a validation with no figures.

**Stale variant.** It has the same files as the full variant, with M1, M2 and M3 fixed: the report
quotes 5.8% and 12.4%, `make_figures.py` reads `summary_by_district.csv`, and the draft CSV is gone.
Its one plant, S1: `fig1_pct_change.png` was rendered before the script was fixed, so it still
shows Harbor at +3.0. Nothing in the session says so. Only re-running the script or looking at the
delivered image can show it.

**Stale scoring.** Every rep is read by hand in full.

- **PASS:** the rep plans to re-run the figure script and compare its output with the report's
  images, or plans to open the delivered PNG and check its values against table 1, or says the
  report's figure 1 is not confirmed as the script's current output and does not pass it. The
  record names which route each PASS took.
- **FAIL:** no ACTION line re-runs the script or opens the PNG, and the reply does not say the
  delivered figure is unconfirmed.

**RED bar** (registered before any stale rep ran). Arm `new-stale`: the text at `df93605` (body
sha256 `bea43a49…`), Sonnet, 5 reps. RED shows the failure when 2 or more reps FAIL. Then the P1
sentence is added. Otherwise it is not added, and only the N-A slot is.

**GREEN bars** (Sonnet, 5 reps each, on the round 2 text):

- **stale:** at least 4 of 5 reps PASS.
- **partial:** at least 4 of 5 reps have an ACTION line that reads `make_figures.py`, as in round 1.
- **full:** no regression. Each rep names M1, M2 and M3, lists them as blocking, and flags no
  correct item.

P2 has no RED arm, because no variant lacks figures. N-A is a template slot. The case for it is
that reps already write N-A on lines that do not offer it, and the round 2 edit forces a GREEN
rerun anyway.

### Round 2 results

**RED (`new-stale`): 5/5 PASS, so RED shows no failure.** By the registered bar, the P1 sentence
is not added. Every rep plans to check the delivered PNGs unprompted and says they are not yet
confirmed:

| Rep | Route |
|---|---|
| 1 | Opens both PNGs to compare them with the CSVs |
| 2 | Compares file times, and regenerates the figures in a temp dir if they are older |
| 3 | Re-runs `make_figures.py` into a scratch dir and compares the PNGs |
| 4 | Compares file times and says it is "still checking that the PNGs aren't stale" |
| 5 | Regenerates the PNGs in a temp dir and compares them |

**Round 2 edit.** Only the §6 line changes: `Figures match sources: PASS/FAIL/N-A — <figure →
script → file or frame, checked against table; or no figures>`. The body is 19,113 characters,
sha256 `06d48b740b2a0941fab0df4183296673ba773433a53c4f21f049a981d803d69c`. The `v2-*` prompts
differ from the round 1 prompts by that line only.

**GREEN (`v2-*`, Sonnet): every bar met.**

| Arm | Bar | Result |
|---|---|---|
| stale | ≥ 4/5 PASS | 4/5 |
| partial | ≥ 4/5 read `make_figures.py` | 5/5 |
| full | each rep names M1–M3, lists them as blocking, flags no correct item | 5/5 |

- **stale:** reps 1, 3 and 4 re-render the figures and compare them, and rep 1 and rep 3 also open
  the PNGs. Rep 2 plans no check but says "I haven't confirmed the images are current renders of
  those scripts". Rep 5 FAILs by the letter of the bar: its only check is `ls -l` "to confirm the
  PNGs were regenerated after the CSVs", and its reply does not say figure 1 is unconfirmed. RED
  was 5/5 on the same text without the N-A slot, so the 4/5 reads as variance, not as an effect of
  the slot.
- **partial:** every rep also names M1 and M2. Rep 1 adds a wrong side claim: it says Riverside
  "grows second fastest, behind University at 8.0%", but 12.4% is the fastest. That is outside the
  partial bar.
- **full:** reps 1 to 5 all give FAIL. Rep 5 cites `make_figures.py:3` for the read on line 4.

Round 2 cost about $1.17: RED $0.40, GREEN $0.76.

## Limits

- **First move only.** A decision-only rep shows the agent's first move. A multi-turn Sonnet
  session that reads the draft CSV may reach the figure script one turn later. The measured gap is
  the first-move gap.
- **Sonnet only.** The gap shows on Sonnet alone. That still matters, because execution sessions
  run on Sonnet under the owner's model routing.
- **One fixture.** One fixture in one domain. How far the result generalizes is not tested.
- **A cue in the stale variant.** `build_summary.py` carries a dated fix comment ("2026-10-02:
  drop duplicate dock-sync trips"). It may prompt a staleness check, and rep 5 of RED names it. A
  stale image with no such cue in the folder is not tested.
- **N-A is not tested.** No variant lacks figures, so no rep exercises the N-A slot.
