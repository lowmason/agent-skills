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
than one turn, an iteration that is not a message, or more than one model). None of the 30 reps
is VOID.

The 10 Sonnet RED reps and the 10 GREEN reps were read by hand in full. The 10 Opus RED reps were
scored from their ACTION lines and from the lines that name the planted values, so the false-flag
statements below do not cover them.

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

## Limits

- **First move only.** A decision-only rep shows the agent's first move. A multi-turn Sonnet
  session that reads the draft CSV may reach the figure script one turn later. The measured gap is
  the first-move gap.
- **Sonnet only.** The gap shows on Sonnet alone. That still matters, because execution sessions
  run on Sonnet under the owner's model routing.
- **One fixture.** One fixture in one domain. How far the result generalizes is not tested.
