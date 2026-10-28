# Archived skills

This folder keeps retired skills whole, so that you can restore one later. Nothing here is live:

- `install.py` installs only `skills/*/SKILL.md`, so it never installs these skills.
- The commit lints and `build/run_suites.py` do not read this folder.
- The files keep their paths as they were under `skills/`. Their text still says `skills/<name>/`, which is correct again after a restore.

| Skill | What it covered | Archived |
|---|---|---|
| [`bls-data-context`](skills/bls-data-context/) | The BLS (Bureau of Labor Statistics) employment and wage programs: QCEW, CES, SAE, JOLTS, BED, OEWS, ECI, ECEC and CPS. It has nine program references and one data-acquisition reference. | 2026-10-27 |
| [`classification-codes`](skills/classification-codes/) | NAICS, SOC and Census occupation codes, with vintage concordances under `data/` and a validated `build.py`. | 2026-10-27 |
| [`geographic-codes`](skills/geographic-codes/) | FIPS state and county codes, CBSAs, metropolitan divisions and CSAs, as interval-stamped tables under `data/`, with a validated `build.py`. | 2026-10-27 |

They were archived because they served the owner's work at BLS and Bloomberg, which has ended. Provenance stays in the root `NOTICE`, in its "Archived skills" section.

## Restore a skill

1. Move it back: `git mv archive/skills/<name> skills/<name>`.
2. In `NOTICE`, move its name from the "Archived skills" list back to the list of original works. Move the data paragraph back too if you restore a code skill.
3. Add its name back to the originals bullet in `CLAUDE.md`, and fix that bullet's count.
4. Restore its row in the root `README.md` skill table. In the Credits section, move its name from the "Archived skills" bullet back to the originals bullet. The last commit before the archive, `9905e4d`, has the old text: `git show 9905e4d:README.md`.
5. For `classification-codes` or `geographic-codes`, add its `[[suite]]` entry back to `build/suites.toml`. Get the entry from `git show 9905e4d:build/suites.toml`. For the rebuild commands, see `git show 9905e4d:CLAUDE.md`.
6. Optional: restore the pointers that other skills had to `bls-data-context`. They were in `validate-data`, `explore-data`, `develop-testing-strategy`, `design-architecture`, `recommend-probabilistic-model` and `creative-thinking`. `git diff 9905e4d -- skills/` shows them after the restore.
7. Run `build/run_commit_lints.sh`, then run `uv run python install.py claude` (or `codex`, `gemini` or `all`).

## Open work at the time of the archive

These items were open in `specs/deferred_items.md` and were removed from it when the skills were archived. Check each one again before you start it, because the sources may have changed.

- **`classification-codes`: Census industry (IND) codes** (audit-3-10-26 F5). CPS has used the 2022 Census industry classification since January 2025. Census publishes the 2017 and 2022 industry code lists with crosswalks. Decide between two options. One is to bundle `census_ind_2017` and `census_ind_2022` with a NAICS expansion, following the OCC pattern in `scripts/build.py`. The other is one sentence at the scope boundary that points to the Census page.
- **`classification-codes`: watch for NAICS 2027 and SOC 2028** (audit-3-10-26 F12). The data bundles NAICS 2022 and SOC 2018 only. A rebuild is due when one of these appears: OMB's final NAICS 2027 notice, the Census 2027 structure and 2022→2027 concordance workbooks, or the second SOC 2028 Federal Register notice. Land the count tests from the next item first.
- **Tests for both code-skill builds** (audit-3-10-26 H3). (a) `validate_naics_concordance`, `validate_soc_crosswalk` and `validate_census_occ` have no tests. (b) No test covers an offline fetch: the missing-cache error and `geographic-codes`' `fetch` are untested. (c) No test ties the counts in each SKILL.md file table to `data/` or `MANIFEST.md`.
- **`bls-data-context` cleanup** (audit-3-10-26 B4, parts 8 to 10). `references/oews.md` is still a downloader build specification, with no panel, vintage or series-ID anatomy. There is research-session residue at `qcew.md:5`, `cps.md:537-538` and `oews.md:45`. LAUS is a description trigger but has no selector row.
