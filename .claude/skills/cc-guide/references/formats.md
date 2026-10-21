# Packet and report formats

`cli.py packets` writes the packets and `cli.py settle` reads them back; both live in `build/cc_guide/` (`packets.py`, `settle.py`), whose tests pin these formats. The verifier's contract, `.claude/agents/cc-guide-verifier.md`, states the same report formats.

## Packets

A packet is a directory under `~/.cache/agent-skills/cc-guide/packets/`, by default `<YYYYMMDDTHHMMSS>-<mode>/`; verify and files runs hold one packet per group or file in it. `packets` refuses a directory inside any checkout, or one that is not empty, and verify and audit check it before they copy any page to the head release's snapshot. Every packet holds:

- `index.json`: `mode`, `inputs` (the working tree), `generated_at`, `head` (the changelog head the docs were fetched at), `cache` (the cache the packet was built on: settle's `cli.py` commands name it as `cli.py --cache <path> <subcommand>` when it is not the default cache), the items the verifier answers for, and `quotes`, the files each kind of quote is re-grepped in.
- `guide.md`: the guide, copied whole, so its line numbers are the guide's.

Then, by mode:

| Mode | Files | `index.json` also names |
|---|---|---|
| triage | `blocks.md` (each changed, missing or new docs block, B1, B2, ...: its current text, and its baselined text from the page's snapshot, as a diff or whole), `releases.md` (every bullet of each untriaged release, `<release>#<n>`, with term hints) | `blocks` (item, group, kind, ref, page, key hash, candidate sections, and `lines`, the lines of `blocks.md` that hold its text), `releases` (label, the sections each is untriaged for, hints, hits), `newest`, `next_through`, `groups`, `held`, `owner` |
| verify | per group: `sections.md` (the sections' guide lines and the triage rows that sent them), `blocks.md`, `changelog.md` | `group`, `sections`, `lines`, `checked` (each section's checked release), `docs` (the head release's snapshot, where the group's pages were copied), `advance_to`, `cleared` and `held` (from `--from`, and the sections a missing page holds), `blocks` |
| audit | `sections.md`, `blocks.md`, `releases.md` (the releases untriaged for the group), `changelog.md` | `group`, `sections`, `lines`, `docs`, `releases`, `held`, `blocks` |
| files | per file: `cited_<name>` (the file's copy), `sections.md` (its cited sections' text, each marked when it changed after the file's stamp) | `file`, `copy`, `stamp`, `sections`, `lines`, `changed` |

`packets --verify <ids> --from <triage>` refuses an ID the triage cleared, since the triage's own commands advance it: verify it without `--from`.

A triage range counts the untriaged releases after the newest release any section is checked through. With more than 20 of them, `packets --triage` refuses and names the `--through` of the first range of 20; `--through <release>` takes the untriaged releases up to that one, and the range's `next_through` names the next range's, the 20th untriaged release after its own. A section deferred in an earlier range shows its earlier releases again, since they stay untriaged for it, but they do not count toward the 20, so a later session never names the same first range again. Block findings ride in every range, so the first range settles them against the current docs. A missing page needs a `manifest.toml` edit, so it is an `owner` item whose sections are held.

## Reports

The verifier returns one report, saved as `report.md` in its packet. Every row is one line, its fields separated by ` | `, each quote inside double quotes, `-` for an empty field. Settle splits a row on `|`, but a quote field that opens with `"` runs to the first `"` followed by `|` or the end of the line, so a quote may hold `|` and `"`; any other field ends at the next `|`, and the last field takes the rest of the line. A leading list marker (`- `, `* `, `+ `, `1. `, `1) `) and a Markdown table's outer pipes are no part of a row, and a line without `|` is prose, never a row. Settle drops these lines without listing them, so they never move its exit to 1:
- separator rows: a line of only `|`, `-`, `:` and spaces;
- header rows, in any letter case, which are of two kinds:
  - a line whose first field is a column name no row starts with: `item`, `release`, `L<line>`, `file:line`, `file line` or `section`;
  - a line whose every field is a column name of the formats below, or one of `Line`, `Claim`, `Verdict`, `Doc`, `Quote`, `Wording` and `File`. That takes in a table's own header row and an echoed template, among them a C row whose only text is one column name (`C | statement`) and a B row shaped like the template (`B | version | one line | changelog.md:line`);
- in verify and audit, a well-formed `<section> | none` line for a section outside the packet.

Any other line holding `|` that is no row is listed as unparseable.

Triage, one row per block (at least) and per bullet that touches a section, and one coverage line per release:

    item | TOUCHES / NOISE / UNSURE | section | guide line | "guide quote" | "source quote" | why
    release | sections touched, or none

Verify and audit, parts A, B and C, and a none line for each section with no checkable claim:

    L<line> | claim ≤12 words | CONFIRMED / STALE / WRONG / PARTIAL / NOT FOUND / JUDGMENT | doc:line | "verbatim quote ≤25 words" | proposed wording
    B | version | one line | changelog.md:line
    C | omission
    section | none

Files, one row per statement that rests on a cited section, and a none line for each cited section no statement rests on:

    file:line | statement | section | "verbatim guide quote" | consistent / contradicts / not covered
    section | none

## What settle does with a report

- **Triage fails safe.** A block with no row becomes UNSURE for each of its candidate sections. A release with no coverage line becomes UNSURE for each section its bullets' terms hit, or an owner item when they hit none. A row whose quote is not found becomes UNSURE, handled as TOUCHES, and a block's row takes every candidate of its block with it; a source quote counts only within its own item's text, and a NOISE row whose source quote, or a guide quote it gives, fails sends its section and every candidate or hint on, or is an owner item when there are none. A line that does not parse still fails safe on what it names: each section it names goes to verify, and so does each candidate of a block it names (a block with no row that parses goes as one with no row); and a bullet it names falls back to its hints the same way. A line that does not parse and whose first field names a release, however it marks the label up (`**<release>**`, `<release>:`), is a coverage line: it leaves each release it names uncovered, whatever another line says about it. A release a broken row mentions only after its first field stays as its own coverage line leaves it. A row that does not parse and names no section, block or bullet sends every section in the packet to verify. An owner item stops the advance below its release. Each TOUCHES or UNSURE section goes to verify. Every other section with an untriaged release in the packet advances, unless a missing page holds it, to the range's newest release, or, when an owner item names a release, to the newest one below the oldest release an owner item names. A group's blocks are rebaselined only when none of its sections goes to verify or is held, and no row for one of its blocks sent a section of any group to verify, since another group's verify packet never carries them. `settled.json` keeps the advance target, the sections cleared, the sections held and the rows each verify section carries, for `packets --verify --from`.
- **Verify, audit and files discard.** A row whose quote is not found is discarded and listed as unverified, and so is a quote a row need not give but gives. A doc quote counts only in the `docs` snapshot's pages or the packet's `changelog.md`. A STALE, WRONG or PARTIAL row whose proposed wording is empty or `-` is discarded too. A surviving STALE, WRONG or PARTIAL row is a correction to apply, unless its line sits within a `TODO(owner)`'s reach (from the TODO through the first list item after it outside fenced code, continuation lines included, or to the end of the section when none follows) or outside the packet's sections; then it is the owner's call, with every JUDGMENT, NOT FOUND, C row and not-covered row, and one outside the packet's sections names the `/cc-guide verify` that reviews it. A B row needs a release and `changelog.md:<line>`; a B or C row that does not parse is listed as unparseable and holds nothing.
- **Holds.** A section is held, neither advanced nor audited, and no block whose candidates include it is rebaselined, nor, while that block is changed or missing, any other block on its page, when: no surviving row or none line answers for it; a discarded STALE, WRONG, PARTIAL or `JUDGMENT (mechanism STALE)` row, or an A row that does not parse, concerns it; a correction to it is left for the owner, or a `JUDGMENT (mechanism STALE)` row survives; its triage or a missing page held it; or `settle --hold` names it. An A row whose line falls in no section, before the first or past the guide's last line, holds every section in the packet; a row outside the packet's sections holds nothing, since the run neither reviews nor advances that section and its triage may have advanced it already, and a `<section> | none` line for such a section is not listed as unparseable either. A file is held, not cited, when a cited section has no surviving row or none line, a discarded `contradicts` row or a row that does not parse concerns it, a row names a section the file does not cite, `settle --hold` names it, or the file in the checkout settle runs from no longer matches the packet's copy, which the verifier read (`the file changed after its packet was built`). That comparison ignores only the citation's stamp, which `baseline cite` rewrites, so a changed list of cited sections holds the file too. Settle a files report before you fix a contradiction it lists, and run the `cite` it printed then: a settle after the fix holds the file. A hold keeps `accept`, for the text the run did change.
- **Bookkeeping**, in R8.8's order: `baseline accept --substantive` for the sections whose text changed, `rebaseline <group> <refs> --head <head>` for the resolved blocks (at the packet's `head`, so it refuses once a later fetch has moved `latest/`, rather than baseline docs the verifier never read), `advance` (verify after a triage, from `--from`) to the triage's `advance_to`, the range's newest release or, when an owner item names a release, the newest one below the oldest it names, for each section not checked past it, or `audited <group> --to <head>` (audit, at the packet's `head`, so a later fetch never moves it), `cite` (files), `stamp`; then `cli.py lint` and `build/check_conformance.py`. A ranged triage ends with the next range's `packets --triage --through` command.
