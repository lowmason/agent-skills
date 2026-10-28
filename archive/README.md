# Archived skills

This folder keeps retired skills whole, so that you can restore one later. Nothing here is live:

- `install.py` installs only `skills/*/SKILL.md`, so it never installs these skills.
- No suite runs their tests, and the skill lints skip them. `build/run_suites.py --check` skips this folder. Only repo-wide scans, such as the binary-asset check, still cover it.
- The files keep their paths as they were under `skills/`. Their text still says `skills/<name>/`, which is correct again after a restore.

| Skill | What it covered | Archived |
|---|---|---|
| [`bls-data-context`](skills/bls-data-context/) | The BLS (Bureau of Labor Statistics) employment and wage programs: QCEW, CES, SAE, JOLTS, BED, OEWS, ECI, ECEC and CPS. It has nine program references and one data-acquisition reference. | 2026-10-27 |
| [`classification-codes`](skills/classification-codes/) | NAICS, SOC and Census occupation codes, with vintage concordances under `data/` and a validated `build.py`. | 2026-10-27 |
| [`geographic-codes`](skills/geographic-codes/) | FIPS state and county codes, CBSAs, metropolitan divisions and CSAs, as interval-stamped tables under `data/`, with a validated `build.py`. | 2026-10-27 |

They were archived because they served the owner's work at BLS and Bloomberg, which has ended. Provenance stays in the root `NOTICE`, in its "Archived skills" section.

## After archiving

The installer made links to these skills in `~/.claude/skills/` and `~/.agents/skills/`. When `main` has the move, those links point to nothing, and `install.py` does not remove them. Remove them by hand:

```bash
rm ~/.claude/skills/{bls-data-context,classification-codes,geographic-codes} ~/.agents/skills/{bls-data-context,classification-codes,geographic-codes}
```

## Restore a skill

The archive commit is the commit that added this file. Its parent has the text from before the archive. Set both first, from the repository root:

```bash
A=$(git log --diff-filter=A --format=%h -- archive/README.md | tail -1)
git show --stat "$A"
```

`git show "$A^:<path>"` prints a file as it was before the archive. `git show "$A" -- <path>` prints what the archive changed in it.

1. Move the skill back: `git mv archive/skills/<name> skills/<name>`.
2. `NOTICE`:
   - Move its name from the "Archived skills" list to the list under "original works by Lowell Mason, MIT licensed:".
   - For a code skill, move its part of the data paragraph back after the deep-learning paragraph. That paragraph names both code skills, so split it if you restore only one.
   - Fix "All three" in the "Archived skills" section, or remove the section when it is empty. Also fix the sentence near the top of the file that points to the section.
   - For `bls-data-context`, remove the writing-skills line from the superpowers change list ("names bayesian-workflow and deep-learning") if you also restore step 6's writing-skills example.
3. `CLAUDE.md`:
   - Add the name back to the "Lowell's originals" bullet, and fix its count.
   - For a code skill, add its rebuild commands back to the Commands block (`git show "$A^:CLAUDE.md"`).
   - Reword the `test_build.py` collision sentence in the Commands section, which now names "the two archived code skills". Do the same in `skills/explore-data/scripts/test_profile.py`.
   - Fix the `archive/skills/` sentence in "What this repo is" if the folder becomes empty.
4. `README.md` (compare with `git show "$A^:README.md"`):
   - Restore the skill's row in the skill table.
   - Restore its name in the stack caveat near the top ("Three skills are specific to US federal statistics").
   - In Credits, move its name from the "Archived skills" bullet back to the originals bullet. For a code skill, restore the "Public-domain data" bullet. In License, restore the "Bundled U.S. Government data" wording.
   - Add "bundled `data/` tables" back to the sentence about what a skill directory holds.
   - Fix "three retired originals", or remove the bullet and the `archive/` line in Layout when the folder becomes empty.
5. For a code skill, add its `[[suite]]` entry back to `build/suites.toml` (`git show "$A^:build/suites.toml"`). `geographic-codes` needs `fastexcel`, which is still pinned in `build/versions.toml`.
6. For `bls-data-context`, restore the pointers that other skills had to it if you want them. `git show "$A" -- skills/` shows each one. They were in `creative-thinking/SKILL.md`, `design-architecture/references/decision-examples.md`, `develop-testing-strategy/SKILL.md`, `explore-data/SKILL.md`, `recommend-probabilistic-model/SKILL.md` and `references/external-data-and-priors.md`, `validate-data/SKILL.md` and `writing-skills/SKILL.md`.
7. The archived skills name each other in their text. A skill restored alone points at siblings that are still archived. Restore them together, or edit those handoffs.
8. Search for text that the archive made untrue: `git grep -n -e 'archive/skills' -e 'archived' -- README.md NOTICE CLAUDE.md build skills specs/deferred_items.md`.
9. Run `build/run_commit_lints.sh`. The lints do not prove that steps 2 to 4 are done: `check_provenance.py` accepts a name in either NOTICE list. Check by eye that the name is in the originals list in both `NOTICE` and `CLAUDE.md`.
10. Install: `uv run python install.py claude` (or `codex`, `gemini` or `all`).

## Open work at the time of the archive

These items were open in `specs/deferred_items.md` and were removed from it when the skills were archived. The full item text, with line anchors, is in `git show "$A^:specs/deferred_items.md"`. Check each item again before you start it, because the sources may have changed.

- **`classification-codes`: Census industry (IND) codes** (audit-3-10-26 F5). CPS has used the 2022 Census industry classification since January 2025. Census publishes the 2017 and 2022 industry code lists with crosswalks (<https://www.census.gov/topics/employment/industry-occupation/guidance/code-lists.html>). Choose one of two paths:
  - Bundle the codes. Add `census_ind_2017` and `census_ind_2022` with a NAICS expansion, following the OCC pattern in `scripts/build.py`. This is plan-sized. Adding "IND" to the description needs a writing-skills micro-test.
  - Leave them out. Add one sentence at the scope boundary that points to the Census page. This is a quick fix.
- **`classification-codes`: watch for NAICS 2027 and SOC 2028** (audit-3-10-26 F12). The data bundles NAICS 2022 and SOC 2018 only. A rebuild is due when one of these appears: OMB's final NAICS 2027 notice, the Census 2027 structure and 2022→2027 concordance workbooks, or the second SOC 2028 Federal Register notice. Land the count tests from the next item first.
- **Tests for both code-skill builds** (audit-3-10-26 H3). (a) `validate_naics_concordance`, `validate_soc_crosswalk` and `validate_census_occ` have no tests. (b) No test covers an offline fetch: the missing-cache error and `geographic-codes`' `fetch` are untested. (c) No test ties the counts in each SKILL.md file table to `data/` or `MANIFEST.md`.
- **`bls-data-context` cleanup** (audit-3-10-26 B4, parts 8 to 10). `references/oews.md` is still a downloader build specification, with no panel, vintage or series-ID anatomy. There is research-session residue at `qcew.md:5`, `cps.md:547` and `oews.md:45`. LAUS is a description trigger but has no selector row.
