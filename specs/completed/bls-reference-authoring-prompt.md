# Authoring prompt for `bls-data-context/references/<program>.md`

A reusable deep-research prompt for producing one new BLS program reference, matching the
converged style of `references/bed.md` and `references/qcew.md`. Written for Claude Chat's
Research mode or ChatGPT deep research.

## How to use it

1. **Prep the attachments.** In a browser, open
   `https://download.bls.gov/pub/time.series/<prefix>/` and download **every file except the
   `.data.*` files**: the `<prefix>.txt` documentation, the `<prefix>.series` metadata file (a
   `head -50` is enough), and all of the small mapping files - `.period`, `.dataclass`,
   `.dataelement`, `.industry`, `.state`, `.area`, `.sizeclass`, `.ratelevel`, `.periodicity`,
   `.seasonal`, `.ownership`, `.unitanalysis`, `.footnote`, and whatever else the directory holds.
   They are a few KB each. Attach all of them. Do not skip this - see below.
2. **Fill the parameter block**, paste the prompt, run it.
3. **Integrate locally** (in Claude Code) using the follow-up checklist at the end. The prompt
   deliberately produces only the reference file; the surrounding edits are local work.

## Why the flat-file section is attachment-only

The failure mode that survives review is a *fabricated lookup table*. A hallucinated
`sizeclass_code` table looks exactly like a real one - plausible codes, plausible labels, correct
formatting - and nothing downstream catches it until an agent writes a filter that silently
matches zero rows. Methodology prose fails loudly (it reads as vague); code tables fail silently.

Everything in `bed.md` lines 261-447 is mechanically derivable from the LABSTAT directory
listing. Note the division of labor in those files: `<prefix>.txt` gives field layouts and
positions, while the code-to-label mappings each live in their own small file (`bd.sizeclass`,
`bd.dataclass`, `bd.footnote`, ...). Attaching only `<prefix>.txt` yields a section 14 that is a
wall of `UNVERIFIED` stubs, which defeats the point of splitting the file by source.

## Parameter block

Fill these before pasting. Worked example uses LAUS, the obvious next gap (it appears in the
`bls-data-context` trigger list with no reference file).

| Placeholder | Meaning | LAUS example |
|---|---|---|
| `{{PROGRAM}}` | Full program name + abbreviations | `Local Area Unemployment Statistics (LAUS)` |
| `{{PREFIX}}` | LABSTAT flat-file prefix | `la` |
| `{{HOM}}` | Handbook of Methods chapter root | `https://www.bls.gov/opub/hom/laus/` |
| `{{HOME}}` | Program home page | `https://www.bls.gov/lau/` |
| `{{NEIGHBORS}}` | Confusable programs/concepts to disambiguate | `LAUS vs CPS state model estimates; LAUS vs CES/SAE (residence vs workplace); LAUS unemployment rate vs national U-3; LAUS vs QCEW` |
| `{{SIBLINGS}}` | References already written | `QCEW, CES national, CES state & area (SAE), JOLTS, BED, OEWS, ECI, ECEC, CPS` |

---

## The prompt

````text
You are producing a single reference document about one U.S. Bureau of Labor Statistics
statistical program.

The document is not for human readers. It will be loaded verbatim into the context window of a
small, fast LLM agent that has no prior knowledge of this program and no ability to browse. That
agent uses it to interpret series, construct and parse series IDs, write ingestion code, and judge
whether a comparison between two data sources is legitimate. Optimize entirely for that reader:
literal, dense, table-first, unambiguous. Every fact must be usable without inference. Assume the
reader will follow any instruction you write, exactly, without checking it.

PROGRAM: {{PROGRAM}}
LABSTAT FLAT-FILE PREFIX: {{PREFIX}}
HANDBOOK OF METHODS CHAPTER: {{HOM}}
PROGRAM HOME PAGE: {{HOME}}
CONFUSABLE NEIGHBORS TO DISAMBIGUATE: {{NEIGHBORS}}
SIBLING REFERENCES THAT ALREADY EXIST (assume the reader may have read none of them): {{SIBLINGS}}

## Sources

- Official BLS sources only for methodology: the Handbook of Methods chapter (its concepts, data
  sources, design, calculation, presentation, and more-information pages), the program home page,
  technical notes attached to the news release, the program FAQ, data-access and file-layout
  pages, and BLS-published documentation files.
- Non-BLS sources (FRED, Wikipedia, news, vendor docs, blogs) may be used only to locate an
  official BLS page. Never cite them as the authority for a fact.
- Cite the specific URL for every nontrivial claim, at the end of the section that makes it.
- If two official BLS pages disagree, say so explicitly and give both values with both URLs.
  Do not silently pick one.
- Paraphrase in your own words throughout. Do not reproduce BLS page text verbatim beyond short
  definitional phrases, and do not use block quotes.
- Carry over BLS's own hedging. If BLS says "generally", "approximately", or "about", keep it.
  Never sharpen an approximation into a precise figure.

## The flat-file section is transcription, not research

The section on the public flat-file system must be built ONLY from the attached LABSTAT files -
the `{{PREFIX}}.txt` documentation, the `{{PREFIX}}.series` sample, and the mapping files. Do not
research it. Do not infer code values from another BLS program, from series titles, from the
program's web tables, or from what would be sensible.

If the attachments do not cover a table you were asked to produce, emit the heading followed by
exactly:

    UNVERIFIED - not covered by the attached LABSTAT files; confirm against the raw directory.

and move on. An honest gap is useful. An invented code table is worse than no table at all,
because it fails silently: a filter built on a wrong code matches zero rows instead of raising.

If this program's primary bulk-access channel is not the LABSTAT time series (some programs
publish chiefly as XLSX or CSV downloads), cover that channel in this section instead, with the
same transcription rule applied to whichever documentation was attached.

## Three accuracy clauses

These come from errors found in earlier documents of this kind. Apply them everywhere.

1. NAME BOTH SIDES OF EVERY RATIO. Any percentage, share, coverage figure, or "X% of Y" must
   state its numerator and its denominator explicitly, in the same sentence. "Covers about 97%"
   is a defect. "Covers about 97% of employment that is in scope for program Z" is correct. Where
   a program has more than one coverage denominator, treat them as separate facts in separate
   sentences and say plainly that they must not be conflated.

2. MARK EVERY LIST EXHAUSTIVE OR ILLUSTRATIVE. For any list of exclusions, exceptions,
   categories, products, or geographies, say which it is: "the excluded groups are:" versus
   "excluded groups include, among others:". Never leave the reader to guess whether a list is
   complete.

3. SCOPE EVERY CONVENTION TO THIS PROGRAM. Do not state a BLS-wide rule. State what THIS program
   does, and name the datatype it applies to when it varies within the program. Conventions that
   look universal across BLS are frequently not.

   Apply clause 3 to period codes with particular care, since this is where it has failed before.
   State exactly which period codes this program's files emit, per datatype
   (`M01`-`M12` monthly, `M13` monthly annual average, `Q01`-`Q04` quarterly, `Q05` quarterly
   annual average, `A01` annual-only, or something else). State explicitly which of those codes
   this program does NOT emit. State what happens when a filter assumes the wrong family: it
   matches zero rows and silently empties the frame rather than raising. Source this from the
   attached `{{PREFIX}}.period` file and the begin/end periods in the `{{PREFIX}}.series` sample,
   not from what other BLS programs do.

## Output format

One markdown file, nothing else. Start at `# {{PROGRAM}}`. No YAML frontmatter. No preamble, no
closing summary, no offers of further help.

Use `##` headings in exactly the order below. The numbering is ordering only - the headings
themselves carry no numbers. Write `## Source hierarchy`, not `## 1. Source hierarchy`. If the
program has no analogue for a section, keep the heading and write one line saying so, rather than
dropping it silently.

1. Source hierarchy - every official URL consulted, grouped as Handbook of Methods / operational
   program pages / flat-file and data-access documentation. Close with a line stating that
   release dates, latest available periods, sample sizes, and current benchmark details are
   time-sensitive and must be re-checked live rather than trusted from this file.
2. Naming conventions - every abbreviation BLS itself uses for this program (formal program name,
   web-navigation name, flat-file database abbreviation, series-ID prefix), plus each confusable
   neighbor from the list above and the one-line rule that separates it.
3. One-sentence mental model - a single bolded sentence capturing what the program does.
4. Agent rules of thumb - 8 to 12 numbered imperatives, each independently actionable and each a
   standalone sentence that still makes sense read in isolation. This is the read-this-first block
   that front-loads the traps before the methodology; put the highest-consequence mistakes here.
5. What {{PROGRAM}} measures - the published concepts and data types.
6. Unit of observation - establishment, firm, person, household, job, or occupation; whether
   counts are jobs or persons; place of work or place of residence. Be explicit even if obvious.
7. Scope and coverage - the universe, what is in, what is out (apply clause 2), geographic
   coverage and its limits, and the handling of Puerto Rico / Virgin Islands / territories.
8. {{PROGRAM}} versus nearby BLS programs - one `###` subsection per neighbor. For each: what
   differs in concept, scope, unit, timing, and geography; whether a reconciliation between them
   is expected to close; and if not, why not.
9. Data sources and collection - where the input data comes from, who reports, collection modes,
   response rates, and any administrative-record dependencies.
10. Estimation methodology - sample design or census construction, weighting, any models,
    imputation, benchmarking, and aggregation. Give formulas as fenced `text` blocks using
    snake_case identifiers, e.g. `net_change = gross_gains - gross_losses`.
11. Seasonal adjustment - method used, direct versus indirect, concurrent versus annual
    re-estimation, which series are adjusted, and what revises as a result.
12. Rates and derived measures - every published rate or derived statistic, each with its exact
    denominator (apply clause 1). Formulas in fenced `text` blocks.
13. Revisions, vintages, and reliability - the revision schedule, the benchmark process, exactly
    which time window each revision touches for seasonally adjusted and not seasonally adjusted
    data, published error measures, and whether sampling error applies at all.
14. Release timing and availability - cadence, lag after the reference period, the start of the
    published history, and the full list of data products.
15. Public flat-file system - TRANSCRIPTION ONLY, from the attachments. Include: a table of files
    in the directory with a purpose for each; a table of the data-file columns; a table of the
    series-file columns; a positional series-ID anatomy table with columns
    "Positions | Component | Example | Meaning" built around one real example series ID; and one
    lookup-code table per dimension, giving every code value and its literal meaning.
16. Agent workflow for data retrieval - a numbered decision procedure, from clarifying the
    concept through selecting series to running identity and sanity checks on the result.
17. Polars-oriented ingestion notes - dtypes, which columns must stay strings to preserve leading
    zeros, delimiter behavior of the raw files, lazy scanning, and a suggested normalized table
    layout (observations table, series table, lookup tables, derived calendar table).
18. Common analytical pitfalls - one `###` per pitfall, with the heading naming the mistake
    ("Treating openings as births"), then two to four sentences on why it is wrong and what to do.
19. Good language for reports - a "Use:" list and an "Avoid:" list of literal phrasings a report
    writer should and should not use about this program's numbers.
20. Quick examples of series-selection logic - four to six concrete analytical tasks, each
    answered as the exact set of dimension filters that select the right series.
21. Recommended metadata to store with derived datasets - for reproducibility.
22. Minimal checklist before publishing an answer - the pre-flight an agent runs before returning
    a {{PROGRAM}}-based number.
23. Glossary - every program-specific term and acronym used above, defined.

## Style

- Tables wherever the content is tabular. Reserve prose for genuinely narrative methodology.
- Bold the term being defined, not whole sentences.
- Backtick every code value, file name, column name, and identifier. Write codes literally with
  their leading zeros (`00`, `000000`), never as bare integers.
- Prefix imperative warnings inside prose with `Agent caution:` or `Agent rule:`.
- ASCII hyphens. No emoji, no horizontal rules, no decorative formatting.
- The file must be self-contained. Do not reference other documents, and do not write "as
  discussed above" or "see the section on X" - restate the fact.
- Depth over brevity. Comparable references run 450-1000 lines. Do not compress to save space,
  and do not pad with generic statistical background.

## Process

- Do not ask clarifying questions. If something is ambiguous, choose the reading that best serves
  a data-engineering agent, state the assumption inline in one italic line, and continue.
- If a fact cannot be confirmed in an official BLS source, either omit it or prefix it with
  `UNVERIFIED:`. Never present an inferred value as a documented one.
- Finish with a final `## Verification status` section listing: (a) claims you could not confirm
  in an official source, (b) pages you could not access, (c) every `UNVERIFIED` marker you left
  and where, and (d) any table in the flat-file section you could not fill from the attachments.
  This section is scaffolding for the human reviewer and will be deleted before the file is
  committed; keep it last and keep it complete.
````

---

## Tool-specific notes

- **Claude Research** - attach the LABSTAT files before sending. It honors the "do not ask
  clarifying questions" line. Output tends to land in one long message; ask for it as an artifact
  if you want a clean copy target.
- **ChatGPT deep research** - it will normally open a clarification turn regardless of the
  instruction. Answer it with "proceed exactly as specified in the prompt" rather than adding new
  requirements, or the added text will outrank the section skeleton. It also has a stronger pull
  toward essay prose and toward adding a title block and a concluding summary; the "no preamble,
  no closing summary" line is doing real work there.
- **On truncation** - `ecec.md` is 979 lines / 58KB, at or past what either tool reliably emits in
  one response. If the output cuts off, ask for the remaining sections as a follow-up message in
  the same conversation. Do not re-run the research.
- Either tool may hedge the flat-file section into vagueness if the attachments are missing. If
  that section comes back without concrete code tables, the attachments did not get through -
  re-request that section alone rather than accepting it.

## Local follow-up after the file lands

The prompt produces the reference file only. Integrating it is local work:

1. Strip the `## Verification status` section, after working through each item in it.
2. Spot-check every code table in the flat-file section against the raw mapping files and a real
   query.
3. Add rows to `skills/bls-data-context/SKILL.md`: the program-selector table, the revision-pattern
   table, and the reference-files table at the bottom.
4. Add a cross-program-reconciliation bullet if the new program reconciles against an existing one.
5. Fold any new period-code or coverage facts into SKILL.md's flat-file-conventions paragraph, and
   check the sibling references for passages the new facts contradict.
6. Confirm `NOTICE` still describes the skill correctly (these references are listed as Lowell's
   originals, MIT - which is why the prompt requires paraphrase rather than verbatim BLS text).
7. Run the lints:
   `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
   `uv run --python 3.13 python build/check_provenance.py`
