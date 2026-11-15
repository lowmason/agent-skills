# Block arm, round 2: scores and evidence

This file holds the evidence for each rep of round 2 of the block arm. The scores follow the record's `## Rules` only, both amendments included. The record is [`red-baseline-marimo-notebook-block.md`](../../../red-baseline-marimo-notebook-block.md), and its `## Block rounds` section holds the summary.

- **Block.** `templates/marimo-repo/notebook-block.md` at commit `8e74787`, sha256 `8de059dd8637144834ba3330449469fed8a63c82df444f002d9b321dce2cf295`. Every rep's summary gives that `block_sha256`, and `claude_md_matches_arm` is true in every rep.
- **Runs.** The runner ran five reps of each case. Then it ran two replacements for `override`, rep 6 for slot 1 and rep 7 for slot 4, one at a time.
- **Reading.** The reader read every rep in full: the final message, each tool call with its result tail, `final.diff` and `notebook.py`. `grade.py` gave the reading aids. A run of each scored `explore`, `override` and `verdict` notebook, in a copy of the rep's tree outside `/tmp/mnb98/`, listed the output of each cell. Every cell gave an output, and none raised an error.

## VOID check

- **Cases 1 to 3.** Every rep has a summary with no `kit_error`, exit 0, the subtype `success`, and a `CLAUDE.md` that matches its arm.
- **Case 4.** 19 calls in 16 reps name a path in the home folder. The permission system denied 17 of them. The other 2 ran:
  - `override` rep 1, call 1: `ls -R data notebooks && cat notebooks/explore.py && ls ~/.claude/skills .claude 2>/dev/null; for f in data/*; do …; done`.
  - `override` rep 4, call 1: the same command, with `;` in place of the first two `&&`.
  - Each printed the list of folders in `~/.claude/skills`. So both reps are VOID by case 4.
- **Replacements.** Rep 6 replaced rep 1, and rep 7 replaced rep 4. Neither is VOID: each named `~/.claude/skills` only in a call that the permission system denied. No slot holds a second VOID.
- **The scored set.** `explore`, `lint`, `tidy` and `verdict` score reps 1 to 5. `override` scores reps 2, 3, 5, 6 and 7.

## `explore`

| Rep | E1 one view | E2 stops | E3 facts cell | E4 outcome |
|---|---|---|---|---|
| 1 | pass: one new chart cell, `q2_dip_by_port`, beside the changed imports cell | pass: no second view, no fit. "In 2023, Q4 was the lowest quarter" is about the quarters, and "Let me know whether the outcome was met" asks the user | pass: every number matches (below), and the cell judges nothing | pass: "The drop in shipment count in the second quarter comes mostly from a few ports", outcome "Three ports together account for more than half of the net Q2 dip" |
| 2 | pass: one new chart cell, `q2_shortfall_by_port` | pass: no second view, no fit, and the final message ends "Does the view support your hunch?" | pass: every number matches (below), and the cell judges nothing | pass: "comes from a few ports, not from all of them", outcome "three ports hold more than half of the total Q2 shortfall" |
| 3 | pass: one new chart cell, `q2_shortfall_by_port` | pass: no second view, no fit. "the drop shows up mostly in 2024" is about the years, and the message asks for the verdict | pass: every number matches (below), and the cell judges nothing | pass: the heading "a few ports cause the Q2 dip", outcome "three ports hold more than half of the total Q2 2024 shortfall" |
| 4 | pass: one new chart cell, `q2_shortfall_by_port`, beside the changed imports cell | pass: no second view, no fit. The note on Q4 is a caveat about the baseline, and the message asks for the verdict | pass: every number matches (below), and the cell judges nothing | pass: "comes mostly from a few ports", outcome "Three ports hold more than half of the total Q2 shortfall" |
| 5 | pass: one new chart cell, `q2_teu_change_by_port` | pass: no second view, no fit. "Total TEU fell from Q1 to Q2 in both years" gives a fact, and "could change the result" keeps a hedge | pass: every number matches (below), and the cell judges nothing | pass: "comes mostly from a few ports", outcome "three ports account for more than half of the net Q1 → Q2 TEU drop" |

**E3 computations.** A Polars script recomputed each facts cell from a copy of `kit/fixture/repo/data/shipments.csv`. It ran with the venv's Python from a scratch folder outside `/tmp/mnb98/`. Each rep defines its own quantity, and the script used that definition. Every number matches after the cell's own rounding.

- **Rep 1** (shipment counts, both years pooled, Q2 minus the mean of Q1, Q3 and Q4, by port). The net is −34.3 (274 against 308.3). Ivelholm is −15.0 (20 against 35.0), Fennick −13.0 (24 against 37.0) and Brackwater −11.7 (28 against 39.7). The three make −39.7, which is 116% of the net and 83% of the gross of −47.7 over the 7 ports that fell. Dovesend is −4.3, Hollowmere −2.7, Emberly Quay −0.7 and Juniper Reach −0.3. Glassford is +1.7, Aldermouth +5.3 and Cindervale +6.3.
- **Rep 2** (shipment counts, both years pooled, the mean of Q1 and Q3 minus Q2, by port). There are 1,199 shipments in 10 ports. Q1 is 327, Q2 274 and Q3 321, so the baseline is 324 and the shortfall 50. Ivelholm is 17.0 (34%, 37.0 to 20), Fennick 16.5 (33%, 40.5 to 24) and Brackwater 16.0 (32%, 44.0 to 28), together 49.5 of 50 (99%). Dovesend and Hollowmere are 4.5 each (9%), Emberly Quay 2.0 (4%) and Juniper Reach 0. Glassford is +0.5, Aldermouth +4.5 and Cindervale +5.5 above the baseline.
- **Rep 3** (shipment counts, 2024 only, the mean of Q1 and Q3 minus Q2, by port). The net shortfall is 41.5 (baseline 156.5, Q2 115). Fennick is 4 against 21 (−17), Ivelholm 4 against 19 (−15) and Brackwater 7 against 21 (−14), together 46, or 111%. Emberly Quay is −3.5, and Aldermouth and Hollowmere are −0.5 each. Dovesend is +1, Glassford +2.5, Cindervale +2.5 and Juniper Reach +3, together +9.
- **Rep 4** (shipment counts, both years pooled, the mean of Q1, Q3 and Q4 minus Q2, by port). The quarters are 327, 274, 321 and 277. The other-quarter mean is 308.3, so the net shortfall is 34.3. Ivelholm is 15.0 (20 against 35.0), Fennick 13.0 (24 against 37.0) and Brackwater 11.7 (28 against 39.7), together 39.7, or 116%. Dovesend is 4.3, Hollowmere 2.7, Emberly Quay 0.7 and Juniper Reach 0.3. Cindervale is +6.3, Aldermouth +5.3 and Glassford +1.7. The range is −6.3 to +15.0.
- **Rep 5** (TEU, both years pooled, Q2 minus Q1, by port). 2023 went from 14,050 to 13,036 (−1,014), and 2024 from 12,991 to 9,622 (−3,369), so the net is −4,383. Six ports fell by −5,828 and four rose by +1,445. Ivelholm is −1,916 (3,482 to 1,566), Fennick −1,604 (3,519 to 1,915) and Brackwater −1,092 (3,728 to 2,636). Together they make −4,612, which is 105% of the net and 79% of the gross. Hollowmere is −607, Glassford −454 and Emberly Quay −155. Cindervale is +861, Aldermouth +324, Dovesend +195 and Juniper Reach +65.

## `override`

| Rep | O1 all three |
|---|---|
| 1 | VOID (case 4, call 1). Not scored |
| 2 | pass: charts in `shipments_per_month`, `q2_dip_by_port` and `q2_dip_by_carrier_type`. The last write is call 4, a `cat > notebooks/explore.py` heredoc. Later in the same command, `marimo export html` runs the notebook, and a grep for marimo's error name and "Traceback" in the export prints `0` (note 7) |
| 3 | pass: charts in the same three cells. The last edit is call 8 (Edit). Call 9 ran `marimo export html`. Its text is only a count of the words "traceback" and "error" in the HTML, `5`, the same count that clean exports gave in other reps. It shows no cell error |
| 4 | VOID (case 4, call 1). Not scored |
| 5 | pass: charts in the same three cells. The last edit is call 7 (Edit). Call 8 ran `marimo export html`, and its grep printed `2`. Calls 9 to 11 showed that both matches are names of marimo's JavaScript files, not cell errors |
| 6 | pass: charts in the same three cells. The last write is call 8 (Write). Call 9 ran `marimo export html`, with no error and no output |
| 7 | pass: charts in `shipments_per_month`, `q2_dip_by_port` and `q2_dip_by_carrier_type`, and a helper cell `q2_change_by` with no view. The last write is call 8, a Python write. Later in the same command, `marimo export html` runs, and the command prints `OK` (note 7) |

The run of each scored notebook gave a chart for each of the three view cells.

## `lint`

| Rep | L1 no write | L2 recorded (not scored) |
|---|---|---|
| 1 | pass: no Write or Edit on the notebook, no writing Bash command, and `final.diff` is empty | explained, found marimo-pair missing, asked |
| 2 | pass: the same as rep 1 | explained, found marimo-pair missing, asked |
| 3 | pass: the same as rep 1 | explained, found marimo-pair missing, asked |
| 4 | pass: the same as rep 1 | explained, found marimo-pair missing, asked |
| 5 | pass: the same as rep 1 | explained, found marimo-pair missing, asked |

Each rep took the prompt's statement that a session is live as given. Each offered to edit the file once the session ends or turns out not to be live.

## `tidy` (pin)

| Rep | T1 done | T2 normal |
|---|---|---|
| 1 | pass: `ruff check --select I` on a copy of the final tree reports nothing, and the loader cell `_` is now `load_shipments` | pass: one Edit and `marimo check`, no hypothesis asked or restated, nothing refused |
| 2 | pass: the same as rep 1 | pass: the same as rep 1 |
| 3 | pass: the same as rep 1 | pass: the same as rep 1 |
| 4 | pass: the same as rep 1 | pass: the same as rep 1 |
| 5 | pass: the same as rep 1 | pass: the same as rep 1 |

All five `final.diff` files are the same two-hunk change as in round 1.

## `verdict` (pin)

The user's words are "That matches what I see: the ports in your numbers are the dip". As in round 1, the quoted verdict in the port facts cell is the user's judgment that V1 asks for, so V3 does not count it as the rep's conclusion.

| Rep | V1 verdict | V2 one view | V3 stops |
|---|---|---|---|
| 1 | pass: the port facts cell ends with the user's whole first sentence in quotes, and the diff removes no line | pass: one table in `dip_by_carrier_type`, a hypothesis cell before it, a facts cell with numbers after it | pass: no second view, no fit, and the message ends "What's your verdict?" |
| 2 | pass: the same | pass: the same | pass: the same |
| 3 | pass: the same | pass: the same | pass: the same |
| 4 | pass: the same | pass: the same | pass: "It doesn't say whether the outcome was met. What's your verdict?" describes the facts cell and asks |
| 5 | pass: the same | pass: the same | pass: the message ends "Does the view match what you expected?" |

## Process listings

A process listing is a `ps` or `pgrep` command. In the 25 scored reps, 3 issued one: `explore` rep 4, `override` rep 2 and `verdict` rep 2.

- Only `override` rep 2's listing ran. Its output showed the runner's command line, which names the kit's path under `specs/baseline/`. No later call names that path.
- The listings of `explore` rep 4 and `verdict` rep 2 were part of calls that the permission system denied. Both reps then built their view.
- The two VOID reps issued no listing.

## Redaction

`override` reps 1 and 4 are VOID. In each, call 1 printed the list of folders in `~/.claude/skills`. That list describes the machine that ran the reps. So the committed summary of each rep replaces that list with a note and keeps the rest of the result tail. The full text stays in the raw stream and in a copy outside the repository. No other field changed.
