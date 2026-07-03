# Repo audit — agent-skills

**Date:** 2026-07-03 · **Requested scope:** code completeness, simplicity, documentation, skill improvement & personalization, and whether subagent-dispatching skills use the appropriate subagent.

**Method:** 75-agent audit workflow — one auditor per skill (22), seven cross-cutting reviewers (docs accuracy, provenance, cross-skill reference graph, build/ tooling with live test runs, subagent dispatch, repo hygiene, and a claude-code-guide agent for spec-limit facts), then adversarial verification of every medium/high factual finding (45 verified, **45 confirmed, 0 refuted**; 4 additional highs spot-verified by hand; 91 low-severity findings reported unverified). All test suites were run live: build/ 4/4, recommend-probabilistic-model 10/10, recommend-visualization 29/29, smoke test pass.

**Overall verdict:** the repo is in strong shape — provenance plumbing is excellent, the data-science skills are deeply personalized already, all scripts are syntactically valid, and nothing junk is tracked. But there are two genuine P0s (a broken frontmatter that silently disables a flagship skill, and a 24.8 MB provenance breach in the same skill), one environment-level surprise (10 of 22 skills aren't installed at all), and a long tail of high-value fixes.

---

## 1. Critical findings (fix first)

### 1.1 `bayesian-workflow` frontmatter is invalid YAML — the skill cannot auto-trigger

[bayesian-workflow/SKILL.md:18](../bayesian-workflow/SKILL.md) has `author: [Alexandre Andorra](https://alexandorra.github.io/)` — the unquoted markdown link breaks YAML parsing, so the entire 977-char description is dropped. **Confirmed live:** in the current session's skill registry, bayesian-workflow lists as bare "Bayesian Workflow" while every sibling shows its full description. The skill effectively triggers on its H1 title only.

**Fix (one line):** quote the value — `author: "Alexandre Andorra (https://alexandorra.github.io/)"` — verified this alone makes the frontmatter parse. Then confirm in a fresh session that the registry shows the description.

### 1.2 Three third-party paper PDFs (24.8 MB) are git-tracked, unreferenced, and unattributed

`bayesian-workflow/references/publications/` tracks Gelman et al. 2020 (arXiv non-exclusive license — no third-party redistribution right), Betancourt's *Towards a Principled Bayesian Workflow* (CC BY-NC 4.0 — requires attribution the repo doesn't provide), and Gabry et al. 2019 (Wiley/JRSS-A article). No markdown anywhere references the directory; NOTICE describes the skill as simply "MIT licensed"; README claims "Everything here is MIT." This is exactly the cite-don't-bundle failure the repo's own Murphy-books policy was designed to prevent.

**Fix:** `git rm -r bayesian-workflow/references/publications/`; the skill already cites all three papers by author-year in SKILL.md and references/visualize.md, so nothing breaks. Optionally add `references/publications.md` with links only (arXiv:2011.01808; betanalpha.github.io case study; doi:10.1111/rssa.12378 / arXiv:1709.01449). Keep local copies in `~/Documents/Bayesian/` alongside the Murphy books if you want them at hand. If the repo may ever go public, consider a history purge (24 MB of possibly-infringing blobs stays in history after `git rm`).

### 1.3 Ten of 22 skills are not installed — including two of your praised originals

`~/.claude/skills/` holds only 12 symlinks. Missing: **brainstorming, design-architecture, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, systematic-debugging, tech-debt, test-driven-development, verification-before-completion** — the entire process/discipline set plus `tech-debt` and `design-architecture` (your own originals; `bls-data-context` cross-links design-architecture, so that link is dead at runtime).

The upstream superpowers plugin is installed but **disabled** in `~/.claude/settings.json`, so there's no namespace collision — but that means the discipline vocabulary currently triggers from *nowhere in your own toolkit*, while enabled marketplace plugins (`engineering:tech-debt`, `engineering:debug`, `engineering:architecture`, `product-management:brainstorm`, `data:explore-data`, …) own that trigger space. A request like "scan for tech debt" or "write an ADR" routes to a generic plugin instead of your personalized skill.

**Fix:** decide deliberately, then act:
1. Symlink the missing skills (at minimum `tech-debt` and `design-architecture`):
   `for d in …; do ln -s ~/Projects/agent-skills/$d ~/.claude/skills/$d; done`
2. If any subset is deliberately parked, record that in CLAUDE.md so future sessions/audits stop assuming all 22 are live.
3. Review the enabled marketplace plugins that collide with your originals and disable the overlapping ones — or sharpen your descriptions to win your actual vocabulary (BLS, Polars, NumPyro).
4. Optionally: name the discipline skills in `~/.claude/CLAUDE.md`'s engineering-discipline bullets (they currently prose-mandate TDD/verification/debugging without naming the skills, so the deeper procedures never load).

### 1.4 `subagent-driven-development` ledger path contradicts its own scripts

[SKILL.md:254](../subagent-driven-development/SKILL.md) tells the controller to check `.sdd/progress.md`; the bundled scripts create `.superpowers/sdd/` ([scripts/sdd-workspace:19](../subagent-driven-development/scripts/sdd-workspace), also task-brief:7, review-package:8). A controller resuming after compaction finds no ledger and can re-dispatch completed tasks — the exact failure the section calls "the single most expensive failure observed." Also, `.sdd/` is never gitignored, making SKILL.md's "it's git-ignored scratch" claim false.

**Fix:** standardize on `.sdd/` (also finishes the de-superpowers rename): change `sdd-workspace:19` to `dir="$root/.sdd"`, update the two script header comments, and have the ledger-check step run `scripts/sdd-workspace` first so the self-ignoring directory always exists.

### 1.5 `finishing-a-development-branch` — worktree cleanup is dead code

Step 6 re-detects the environment *after* Options 1/4 have already `cd`-ed to the main root, so it always concludes "Normal repo, no worktree to clean up," orphaning the worktree and making `git branch -d` fail (reproduced in a sandbox repo). Also: Option 2 "Push and Create PR" pushes but never creates the PR (no `gh pr create`), and Step 3's `git merge-base` heuristic outputs a SHA, not a base branch.

**Fix:** record `WORKTREE_PATH` in Step 2 before any `cd` and have Step 6 consume the recorded value; add `gh pr create` to Option 2 (plus a detached-HEAD recipe: `git push origin HEAD:refs/heads/<branch>`); replace merge-base with `git symbolic-ref --short refs/remotes/origin/HEAD` (not `rev-parse --abbrev-ref`, which echoes the literal arg to stdout when the ref is unset, defeating any fallback).

### 1.6 `tech-debt/scripts/scan.sh` — two confirmed defects

1. The rg path can never find a committed `.env` file — the skill's own "do first" security signal — because `rg --files`/`rg` skip hidden files by default (scan.sh:18-19; the grep/find fallback *does* find it, so the better-equipped machine gets the worse scan; rg is installed on this machine, so this is live). Fix: `rg --files --hidden -g '!.git'`; for the "committed" predicate specifically, `git ls-files` is the more truthful source.
2. Absolute `ROOT` paths containing signal-like components (`/tmp/`, `scratch`, `_v2`, `/archive/`) flood the DELETE-candidate sections with false positives because the path regexes match the full prefix. Fix: `cd "$ROOT" && ROOT=.` after validation.

Also worth fixing while in there: the `rg 2>/dev/null || grep` fallback chaining conflates "no matches" with "tool unsupported" and silently swallows an invalid-regex error (`np.random.seed(` — unbalanced paren); pick the tool once with `command -v rg`.

### 1.7 The canonical Gate A command verifies zero citations

CLAUDE.md's documented command targets `recommend-probabilistic-model/SKILL.md` — which contains **no** PML §refs or notebook paths; all ~105 citations live in `references/*.md` and `references/families/*.md`. The canonical invocation exits 0 without checking anything (verified). Also, on a fresh clone (no gitignored `.scratch/`), `verify_citations.py` dies with a raw `FileNotFoundError` traceback instead of "run extract_structure.py first."

**Fix:** teach `verify_citations.py` to accept a directory and `rglob('*.md')`, update CLAUDE.md to `… verify_citations.py recommend-probabilistic-model/`; catch the missing-scratch case with an actionable exit message and a `pytest.skip` guard in conftest.

### 1.8 Bare-`python` usage blocks in three skills fail on this machine

`explore-data` (SKILL.md:39 + profile.py docstring), `recommend-visualization` (SKILL.md:66-68), and `design-architecture` (SKILL.md:268-269) document `python scripts/…` invocations. Verified: `which python` → not found; system `python3` is 3.9.6 without polars. Every command should use the house form with the installed-skill absolute path (skills trigger in arbitrary project cwds):

```
uv run --python 3.13 --with polars python ~/.claude/skills/explore-data/scripts/profile.py data.parquet --json profile.json
```

(design-architecture's scaffolder is stdlib-only, so `python3 ~/.claude/skills/design-architecture/scripts/new_adr.py "<title>"` suffices.)

---

## 2. The description-length question — adjudicated

Two auditors contradicted each other, so this was resolved against the docs and empirically:

- **The Agent Skills open standard** (agentskills.io) caps `description` at **1024 chars** (name at 64, lowercase+hyphens).
- **Claude Code today** enforces no 1024 hard cap; it truncates the *combined* `description` + `when_to_use` at **1536 chars** in the skill listing. No skill here uses `when_to_use`, and the longest description (develop-testing-strategy, 1358) is under 1536 — **empirically confirmed: the full 1358-char description loads untruncated in the current session.**

So the seven over-1024 descriptions (develop-testing-strategy 1358, validate-data 1257, tech-debt 1250, bls-data-context 1239, explore-data 1208, design-architecture 1175, recommend-probabilistic-model 1025) are **not broken today** — this is a portability/spec-compliance and context-budget concern, not a triggering outage. Downgrade the fleet's "HIGH" ratings accordingly, but still act on it, for three reasons: (a) the standard says 1024 and other harnesses may enforce it; (b) your own writing-skills meta-skill says "Max 1024, keep under 500 if possible"; (c) every one of these descriptions also violates the meta-skill's "triggering conditions only, never summarize content" rule — trimming the summary sentences fixes both at once. Auditors drafted ≤1024 rewrites for all seven (and for the weak short ones); they preserve every concrete trigger phrase and cut only the content-summary clauses.

**Record the adjudicated facts in writing-skills** (see §5) so the next audit doesn't re-litigate: description ≤1024 per the standard; Claude Code truncates description+when_to_use at 1536 combined; name ≤64, lowercase.

---

## 3. Subagent dispatch — your headline question

**Short answer:** every skill that dispatches subagents implies or names `general-purpose`, and that is *correct* everywhere writes or command-running are needed. The gaps are: (1) all *reviewer* roles ride over-privileged general-purpose agents constrained only by prose — the right modern answer is a custom read-only reviewer agent; (2) read-only *investigation* fan-outs should route to Explore; (3) two reviewer prompt files are orphaned dead weight; (4) several templates carry stale interactive-subagent fictions.

| Skill | What it dispatches | Named type | Verdict |
|---|---|---|---|
| subagent-driven-development | implementer, fix subagents | `general-purpose` (explicit) | **Correct** — needs Edit/Write/Bash/commit; nothing cheaper can do it |
| subagent-driven-development | task reviewer | `general-purpose` (explicit) | **Works but over-privileged** — read-only contract enforced only by prose; see custom-agent recommendation below |
| requesting-code-review | code reviewer (code-reviewer.md) | `general-purpose` (explicit) | **Correct today** — reviewer must run `git diff/log/show` and occasionally tests; Explore (search-tuned, wrong output contract) and Plan (returns implementation plans) are wrong shapes; no reviewer type exists in the registry. Same custom-agent upgrade applies. Remove the dead `haiku` alias (reviews floor at sonnet per SDO's own rule) |
| dispatching-parallel-agents | parallel investigators/fixers | `general-purpose` (explicit) | **Correct for fixes; wrong default for pure investigation** — the skill's own framing is "parallel investigations," which should route to **Explore** (read-only, cheaper, can't collide). Add a 3-line routing rule: read-only diagnosis → Explore; edits → general-purpose; design → Plan |
| writing-plans | plan-document-reviewer-prompt.md | `general-purpose` (in orphan) | **File is orphaned** — zero references, and SKILL.md:146 explicitly says self-review is "not a subagent dispatch." Delete it (or wire it in as an optional gate for >10-task plans; a document review is read-only, so a restricted agent suffices) |
| brainstorming | spec-document-reviewer-prompt.md | `general-purpose` (in orphan) | **Same orphan situation** — delete or wire in |
| executing-plans | none (routes to SDD) | n/a | Routing is stale, not the agent type: "if subagents are available" is always true in Claude Code, making this skill an unreachable redirect while SDD's own flowchart routes coupled plans back here. Re-key the choice on task coupling / plan size / user preference |
| verification-before-completion | none (governs verifying agents' claims) | n/a | Correct as far as it goes; add one caveat — read-only agents (Explore/Plan) legitimately produce no VCS diff, so "diff shows changes" verification doesn't apply; verify their reports by spot-checking cited files |
| writing-skills | pressure-test/baseline subagents | **none named** | Should say: general-purpose (the test agent must be able to *act out a violation* — edit, commit — which read-only agents can't). Also has a real contamination hole: this repo is symlinked live into `~/.claude/skills`, so a "without skill" RED baseline subagent can auto-load the very skill under test. Run RED via raw API calls or temporarily move the skill out |

**The one structural upgrade that answers the question best:** create a custom read-only reviewer agent (e.g. `~/.claude/agents/code-reviewer.md`, tools: Read, Grep, Glob, Bash; system prompt = the read-only contract + calibration + output format currently duplicated across code-reviewer.md and task-reviewer-prompt.md). Then requesting-code-review and SDD's per-task/final reviews dispatch `code-reviewer` instead of `general-purpose`: the read-only constraint becomes mechanical instead of prose, dispatch prompts shrink to task-specific inputs, and per-dispatch model choice still applies. Consider shipping it from this repo (an `agents/` directory symlinked to `~/.claude/agents/`) so provenance stays in NOTICE. Portability caveat: custom agent names are environment-specific; keep the general-purpose instructions as the documented fallback.

**Cross-template consistency bugs found while auditing dispatch (all confirmed):**
- requesting-code-review recommends `BASE_SHA=$(git rev-parse HEAD~1)` (SKILL.md:28) — the exact anti-pattern SDO forbids ("never HEAD~1", drops all but the last commit of a multi-commit task).
- SDO mandates diff-as-file handoffs (scripts/review-package) including for the final review, but code-reviewer.md — the template SDO names for that review — has no `[DIFF_FILE]` slot and tells the reviewer to run `git diff` itself.
- code-reviewer.md's "Read-Only Review" paragraph forbids mutating repo state, then suggests `git worktree add` (which mutates `.git/worktrees` and has no cleanup step).
- implementer-prompt.md tells subagents "It's always OK to pause and clarify" mid-run and SKILL.md's example shows live Q&A — one-shot subagents can't pause. The skill's own NEEDS_CONTEXT status + re-dispatch is the real mechanism; rewrite the prompt and example to use it.
- SDO's implementer dispatch never carries the plan's **Global Constraints** (no `[GLOBAL_CONSTRAINTS]` slot in implementer-prompt.md; task-brief extracts only the Task N section) while the *reviewer* template enforces them — guaranteeing review-loop churn on any constraint-bearing plan. Cleanest fix: extend `scripts/task-brief` to also extract the plan's Global Constraints section into every brief.
- SDO's model-tier table (SKILL.md:106-109) pins Sonnet 4.6 / Opus 4.6 — stale (current lineup: Haiku 4.5 / Sonnet 5 / Opus 4.8, plus the new Claude 5 tier). The aliases still work; refresh the IDs or make aliases normative with IDs as a footnote.
- dispatching-parallel-agents forbids shared-state parallelism outright; the modern Agent tool's `isolation: worktree` option (and the using-git-worktrees skill) dissolves that boundary case — worth one line each. Relatedly, SDO says "Parallel-safe (subagents don't interfere)" in Advantages while Red Flags forbids parallel implementers — reconcile.

---

## 4. Per-skill findings and suggestions

Ratings: ✅ solid as-is (polish only) · ⚠️ needs targeted fixes · ❗ has a P0 above.

### Data-science originals

**explore-data** ⚠️ — Excellent, already saturated with your domain (QCEW sentinels, panel checks); profiler smoke-tested clean. Fix: bare-python usage block (§1.8); description 1208 → adopt the drafted ≤1024 "Use when…" rewrite; make the `--json` claim true by adding `numeric_summary` and `top_categoricals` to the JSON (directly improves the recommend-visualization handoff, which currently recomputes signals "the profile JSON omits"); state which quality flags profile.py actually emits (HIGH NULL/CONSTANT/SENTINEL) vs. which are manual so a flag-free run isn't read as a clean bill of health; delete stray `scripts/__pycache__` (its cpython-312 build tag proves the un-pinned path has been used).

**validate-data** ⚠️ — All five Polars snippets verified executing on polars 1.42.1. Fix: description 1257 → drafted rewrite; **content_hash built on `hash_rows` is documented-unstable across polars releases** yet prescribed as a persistent pin — scope hash_rows to same-session parity and pin sha256-of-file-bytes + polars version instead (prevents a false FAIL on the skill's own "can't reproduce yesterday's run" trigger); drop the PyMC seeding sentence (NumPyro-only stack); single-quote the snippets; add the uv invocation hint.

**tech-debt** ❗ — scan.sh fixes in §1.6; description 1250 → drafted rewrite (also drops the unsupported "Trino" claim — zero Trino signals exist in the skill); "grep recipes below" promises runnable commands the body doesn't contain (it's a table — reword). Personalization: add `import pandas`/`import pymc` as migration-debt signals in scan.sh (the description already advertises PyMC scanning; the scanner should actually look), and a git-tracked large-data-file signal (`git ls-files | grep -E '\.(parquet|csv)$'` over ~10 MB). Cross-link develop-testing-strategy at the HARDEN "add the one pinning test" bullet and validate-data in Correctness-risk.

**design-architecture** ⚠️ — Strong and deeply personalized; scaffolder works. Fix: description 1175 → drafted rewrite; scaffolder invocation (§1.8); move the five stack-specific decision sketches (~1.2k tokens, one already duplicated in the exemplar ADR) to `references/decision-examples.md`; date the "currently solved three ways" claim (the skill's own doctrine is frozen, dated context); dedupe the anti-patterns section (immutability rule stated 4×). **Symlink it** (§1.3).

**develop-testing-strategy** ⚠️ — Excellent and already personalized. Fix: description 1358 → drafted rewrite; **reconcile the tier contradiction** — SKILL.md says shape/determinism tests are "millisecond-fast" CI-default, but the bundled scaffolds mark shape tests `@pytest.mark.slow` and leave the twice-running-MCMC determinism test unmarked (show the cached-TINY-fit fixture pattern and mark anything that samples); fix the scraper scaffold computing its expected value from the production helper it's testing (violates the skill's own anti-pattern — hand-write `date(2025, 3, 31)`); fix broken imports in copy-paste snippets (BeautifulSoup used but never imported; `pl.col` without polars); add a sibling line for test-driven-development (mirrors your global CLAUDE.md carve-out); single-quote the scaffolds.

**bls-data-context** ⚠️ — Excellent hub-and-spoke design. Fix: description 1239 → drafted rewrite; **references/oews.md is a downloader build-spec, not the program reference the hub promises** — rewrite to the sibling pattern (OEWS panel design, May reference/vintage semantics, MB3 estimation, series-ID anatomy), demoting the downloader acceptance criteria to an appendix; scrub research-session artifacts ("Primary pages provided by the user", "The live oe.release file I could access", the dead user-supplied TP66 URL note); LAUS is named as a reconciliation hazard but routed nowhere — add an out-of-scope-but-adjacent pointer; add the recommend-* skills to the "How the method skills use this" roster.

**recommend-probabilistic-model** ⚠️ — Genuinely excellent; every citation Gate-A-verified, 10/10 tests green, clean provenance. Fix: description 1025 (1 char over) → drafted 871-char rewrite that also drops the workflow summary; **four semantically mismatched notebook pointers** (GDA/NB → logreg demo, deep ensembles → bagging, SVGP → ARD demo, NB/ZIP → plain Poisson) — relocate real matches via the drill-down recipe or annotate "nearest available"; replace the opaque C1/C2/C3/C5 labels leaking from the retired spec (their referent isn't installed with the skill; keep C4 only with its inline definition, or global-rename to "handoff payload"); `../NOTICE` links break under the per-skill symlink layout — use plain text; add the uv invocation for characterize.py; drop PyMC from the GP handoff (consider tinygp for the JAX path); add recommend-visualization to reporting.md's bracketing-skills line.

**recommend-visualization** ✅ — The best-conditioned skill in the repo (913-char trigger-dense description, 29/29 tests, doc-code contract tests, verified end-to-end handoff). Fix: bare-python usage block (§1.8 — verified the uv form works end-to-end); **reconcile the Phase-0 signals story** — `top_n_coverage` and `outlier_ratio` are computed but drive nothing, and the "modality" bullet names a signal that's never computed (either wire them in with failing golden tests first, or narrow chart-selection.md's claim); scope the "recommender refuses these" list to what recommend.py actually enforces (pie>6/spaghetti/raw-scatter yes; 3D/baselines/dual-axes are Phase-2 prose); consider a "BLS charting traps" note (SA/NSA mixing, benchmark-discontinuity rules, thousands-vs-persons labels).

**bayesian-workflow** ❗ — Content is excellent and NumPyro-faithful; the wrapper is the problem. Fix: frontmatter YAML (§1.1) and PDFs (§1.2); delete `main.py` (hello-world stub) + `pyproject.toml` (empty-dep uv-init scaffolding) and the README lines describing them; README install instructions clone the *upstream* repo — rewrite for this repo's symlink reality; description → drafted "Use when…" rewrite (977 chars but summarizes content); add a 3-line siblings block (explore-data upstream; consume recommend-probabilistic-model's §6 handoff payload; validate-data downstream) — the recommender names this skill ~20 times and defines a handoff interface this skill never acknowledges; move the BlackJAX sampler block (SKILL.md:177-229) and ArviZ porting table to references/ (~2k tokens per activation); fix stale "PyMC 5/PyMC 6" comments in the ported scripts (the code branches on ArviZ versions) and the `--loo-pit` figure-name mismatch vs reporting.md's template.

### Superpowers-derived process skills

**subagent-driven-development** ❗ — The most intelligently adapted port. Fix: ledger path (§1.4); Global Constraints channel, NEEDS_CONTEXT rewrite, "same subagent fixes" contradiction, model-tier refresh (§3); task-brief awk leaks trailing plan sections into the last task's brief (verified — add a heading-level guard + test); replace the upstream `~/.config/superpowers/hooks/` example answer with a domain-native one; consider moving Example Workflow + Advantages (~25% of a 21 KB always-loaded file) to a reference; point "Finish the branch" at finishing-a-development-branch by name; densify the 85-char description (drafted rewrite available); add a line to implementer-prompt.md: "run tests with the exact commands the brief specifies" (a cheap-tier implementer guessing `pytest` from the repo root fails in your no-pyproject world and burns a re-dispatch).

**requesting-code-review** ⚠️ — Already modernized (explicit type + model tiers). Fix: **stale claim that it governs per-task SDO reviews** (SDO has its own task reviewer; this template is final-whole-branch only) — re-scope SKILL.md:15 and the Integration section; description contains no occurrence of "review"/"PR"/"diff" — adopt the drafted rewrite; HEAD~1 anti-pattern, `[DIFF_FILE]` slot, worktree cleanup, dead haiku alias (§3); unify `{CURLY}` vs `[BRACKET]` placeholder syntax between SKILL.md and the template; cross-link receiving-code-review for processing findings; swap the TypeScript example output for a Python/Polars one; add a line disambiguating from the built-in `/code-review` command.

**receiving-code-review** ⚠️ — Fix: two "your human partner's rule:" quotes are **Jesse Vincent's personal rules misattributed as your standing orders** (SKILL.md:86, 98) — restate impersonally; "explicit instruction-file violation" (line 30) cites a rule that exists in no instruction file here — either fix the parenthetical or actually add the ban to `~/.claude/CLAUDE.md`; dedupe the twice-told "Fix items 1-6" example; cross-link requesting-code-review (the two halves of the review loop currently ignore each other); replace "your human partner" (9×) with "the user".

**dispatching-parallel-agents** ⚠️ — Fix: delete the narrative back half ("Real Example from Session", "Real-World Impact — From debugging session (2025-10-03)" — the verbatim anti-pattern writing-skills bans; ~half the file is duplication; 1002 words → ~500); add the Explore/general-purpose/Plan routing rule (§3); reconcile the 2+ (description) vs 3+ (body) threshold; densify the 106-char description (drafted rewrite); replace the TypeScript test example with a BLS-native one (three parallel Explore agents profiling QCEW/CES/JOLTS extracts, one general-purpose fixer); cross-link using-git-worktrees for the same-repo boundary case.

**executing-plans** ⚠️ — Fix: the always-true subagent redirect + circular contradiction with SDO's flowchart (§3 table) — route on task coupling/user preference; description promises "review checkpoints" the body no longer has; using-git-worktrees is listed as "Required" but no step invokes it — add an explicit Step 1.0; delete the Codex/Copilot/Gemini platform list; encode your plan conventions (read from `specs/plans/<id>-<name>.md`, retire to `specs/plans/completed/` — you currently do this retirement manually); map plan checkboxes to TodoWrite explicitly.

**writing-plans** ⚠️ — Fix: delete or wire in the orphaned plan-document-reviewer-prompt.md (§3); "checkpoint at each milestone" references a concept the plan template never defines — say "after each task" or add a Milestone grouping level; restore a third execution-handoff option pointing at executing-plans (currently unreachable from any live workflow); make the plan-header's unconditional "REQUIRED SUB-SKILL: subagent-driven-development" conditional on how execution was chosen (today the saved artifact overrides a user's inline choice on later pickup); enrich the 84-char description (drafted rewrite); add a Global-Constraints boilerplate reminder to carry your stack invariants (Polars/single quotes/NumPyro/uv commands) — SDO copies Global Constraints into every brief and reviewer lens, so this is the one place stack defaults propagate to every subagent automatically; make example test commands match the uv runner.

**test-driven-development** ✅ — The healthiest port (its 79-char description is literally writing-skills' GOOD example). One real gap: **no handoff to develop-testing-strategy** despite your global CLAUDE.md carving model/data testing out to it — add one line under "When to Use". Polish: "Refactoring" under **Always** contradicts the Iron Law for pure refactors (add "(stay under existing green tests)"); two "**your human partner's correction:**" find-replace artifacts in testing-anti-patterns.md; unlabeled digraph edge creates a double-"yes" ambiguity. Caution: this is a pressure-tested discipline skill — don't trim the triple-stated rationalizations casually; the repetition may be load-bearing (Iron Law: re-test wording changes).

**systematic-debugging** ⚠️ — Fix: 91-char description omits every symptom that routes to the bundled sub-techniques (flaky tests, arbitrary sleeps, test pollution) — adopt the drafted rewrite; "see Phase 4.5" points at a phase that doesn't exist (it's Phase 4 step 5); "## your human partner's Signals…" heading is a mechanical find-replace artifact; the two root-cause-tracing flowcharts contradict each other on the untraceable case; find-polluter.sh self-describes as bisection but is a linear scan and reports "Found 1 test files" on zero matches; swap the macOS codesign example for a scrape→parse→Polars→parquet→fit boundary-logging example; generalize or delete the dated upstream session stats; name AskUserQuestion at the 3-failures human checkpoint.

**verification-before-completion** ✅ — Tight. Fix: description summarizes workflow → drafted rewrite adds violation-symptom triggers; "From 24 failure memories" / "If you lie, you'll be replaced" is unadapted upstream narrative — delete or replace with two owner-true bullets; add "marking a todo item complete" as an explicit trigger (the most common modern completion-claim vector); add the read-only-agents-leave-no-diff caveat (§3); cross-link validate-data as the data-side counterpart gate.

**using-git-worktrees** ⚠️ — Unusually harness-aware (names EnterWorktree). Fix: the submodule claim "GIT_DIR != GIT_COMMON is also true inside git submodules" is **empirically false** on git 2.51 (verified — both values are equal in a plain submodule) — delete or reword; the ignore-safety check ORs both candidate directories so it passes when the *other* one is ignored — check the chosen `$LOCATION` only; "commit the change" contradicts your commit-only-when-asked rule; description summarizes workflow → drafted rewrite; collapse the triple-stated closing sections (~1154 → ~650 words); replace pip/poetry setup lines with uv; name ExitWorktree as the finish-time counterpart and cross-link finishing-a-development-branch.

**brainstorming** ⚠️ — Well-engineered port, but carries the most upstream residue. Fix: `skills/brainstorming/visual-companion.md` path resolves nowhere (file is a sibling); `elements-of-style:writing-clearly-and-concisely` is a plugin-namespace reference to a nonexistent skill (regresses the NOTICE invariant); orphaned spec-document-reviewer-prompt.md (§3); **the companion server hotlinks a superpowers brand image from primeradiant.com with the version as a query param unless a telemetry env var is set — an upstream usage beacon** (scripts/server.cjs:106-112, 247-249); given your attribution care, either strip it (the text-only branch already exists in the code) or make it opt-in — attribution belongs in NOTICE, not runtime fetches; the `.superpowers/brainstorm/` state dir written into user projects should be renamed (e.g. `.brainstorm/`); description is second-person and workflow-summarizing → drafted rewrite; drop the "frontend-design, mcp-builder" do-not-invoke list (dropped upstream skills); map the one-question-at-a-time loop onto AskUserQuestion; cross-link design-architecture for architecture-heavy specs and note the writing-plans continuation so the specs/ chain is explicit. **Symlink it or document why parked.**

**writing-skills** ⚠️ — The meta-skill fails its own bar on the margins. Fix: 689 lines / 3,885 words vs its own <500-word/<500-line guidance — consolidate the Bulletproofing/RED-GREEN material duplicated nearly verbatim with testing-skills-with-subagents.md (keep Iron Law, Match-the-Form, SDO, checklist inline); "Max 1024 characters total" mis-states the caps (1024 is description alone; name is 64) and the template's `name: Skill-Name-With-Hyphens` violates the lowercase rule the spec enforces; **unreconciled contradiction with its own bundled reference** — SKILL.md says descriptions state ONLY when-to-use, anthropic-best-practices.md says what+when, and your best descriptions follow Anthropic's style — add an explicit precedence line (the tested failure is summarizing *workflow*; naming the domain/deliverable is fine); record the §2 adjudicated limits; stale superpowers-environment examples (getting-started, search-conversations CLI, "push to your fork") → replace with repo-native ones and the real deployment model (symlinked live — a merged edit IS deployment); render-graphs.js fails on this skill's own file (the anti-pattern ```dot fragment isn't a digraph — re-fence as ```text); the RED-baseline contamination warning (§3); thinnest description in the repo (97 chars) → drafted rewrite; add a NOTICE/provenance step to the deployment checklist (the skill governing skill creation never mentions attribution — your one provenance regression, the PDFs, is exactly what that gate would catch).

---

## 5. Documentation & provenance sync

All five CLAUDE.md commands pass as written; README lists all 22 skills. The drift (all confirmed):

1. **CLAUDE.md:15** omits `recommend-visualization` from the originals list (NOTICE has it; NOTICE was updated 2026-06-28, CLAUDE.md wasn't).
2. **README.md:90** Credits names only 6 originals — add `recommend-probabilistic-model` and `recommend-visualization`.
3. **README.md:96** "Everything here is MIT licensed" is falsified by the bundled PDFs until §1.2 lands; also add one sentence on the Murphy cite-only posture (the public README is where a licensing question lands first).
4. **LICENSE:25-27** tail predates the recommend-* skills — defer to NOTICE as the single authoritative list.
5. **CLAUDE.md Commands** omits the 29-test recommend-visualization suite (verified passing) — an agent following CLAUDE.md runs 14 of 43 tests. Also fix the Gate A command (§1.7) and the "silent + exit 0" claim (a chapter-fallback WARN prints on success).
6. **README "### Mine" heading** misattributes bayesian-workflow (an adaptation) — retitle or annotate the row.
7. Archived plans in `specs/plans/completed/` retain `superpowers:` headers — harmless, but annotate as historical so nobody replays one verbatim.
8. bayesian-workflow/README.md tells users to clone the *upstream* baygent-skills repo.

**Mechanical gates worth adding to build/** (your Gate A culture, generalized — each would have caught findings in this audit):
- `check_frontmatter.py`: YAML-parses every SKILL.md (catches §1.1's class), asserts name==dirname, name ≤64 lowercase, description ≤1024, keys ⊆ spec set, and every relative path referenced in SKILL.md exists (catches the brainstorming path).
- `check_provenance.py`: every top-level skill dir appears in NOTICE; `git ls-files` matches no `*.pdf`/`*.epub` outside an allowlist (catches §1.2).
- A Gate-B sign-off ledger (`build/gate_b_verified.txt`) so the recurring `PML2 §2.2.1.4` chapter-fallback WARN is resolvable instead of accumulating noise; five-line `build/README.md` documenting the two gates operationally.

---

## 6. Cross-skill wiring (the pipeline gaps)

The data cluster is densely and accurately interlinked. The gaps:

1. **bayesian-workflow is a dead-end hub** — recommend-probabilistic-model names it ~20 times with a dedicated handoff payload; bayesian-workflow references no repo skill at all. Add the 3-line siblings block (explore-data → [recommend-probabilistic-model §6 payload] → bayesian-workflow → validate-data).
2. **The review loop's two halves ignore each other** — one line each in requesting/receiving-code-review.
3. **The design cluster is completely unwired** — brainstorming, design-architecture, and writing-plans never mention each other, yet brainstorming writes specs to the same `specs/` location design-architecture governs. Wire brainstorm → ADR (design-architecture) → plan (writing-plans), three lines each.
4. Roster completions: bls-data-context "method skills" line + validate-data siblings should name the recommend-* skills.
5. tech-debt ↔ develop-testing-strategy / validate-data cross-links (see §4).

---

## 7. Personalization themes (recurring across auditors)

1. **The uv invocation convention is the #1 personalization gap.** Every runnable snippet in every skill should use `uv run --python 3.13 --with <deps> python ~/.claude/skills/<skill>/scripts/…` — bare `python` fails on this machine, and skills execute from arbitrary project cwds. (Fixes: explore-data, recommend-visualization, design-architecture, recommend-probabilistic-model docs, test commands in TDD/writing-plans/finishing-a-development-branch/verification-before-completion, find-polluter.sh examples.)
2. **Single quotes** — validate-data, develop-testing-strategy scaffolds, explore-data/recommend-probabilistic-model/build scripts, and the ported bayesian-workflow snippets all use double quotes against your stated style. Mechanical pass when files are next touched; note model-criticism.md imports pandas (the only library-choice conflict — swap to polars).
3. **Modern-harness naming** — AskUserQuestion for option menus and human checkpoints (finishing-a-development-branch Step 4, brainstorming's question loop, SDO's batched pre-flight, systematic-debugging's 3-failure stop, writing-plans handoff); TodoWrite mapping in executing-plans; EnterWorktree/ExitWorktree pairing; plan-mode notes in brainstorming/writing-plans.
4. **BLS-native examples over upstream leftovers** — TypeScript test files → QCEW/CES/JOLTS parallel validations (dispatching-parallel-agents); macOS codesign → pipeline boundary logging (systematic-debugging); db.ts review example → Python/Polars (code-reviewer.md); `~/.config/superpowers/hooks/` → a series_id+ref_date+vintage keying question (SDO).
5. **Global CLAUDE.md ↔ skills linkage** — your engineering-discipline bullets mandate behaviors these skills implement but don't name the skills (except develop-testing-strategy). Naming them turns accidental double-coverage into deliberate triggering — and is the cheap complement to the §1.3 symlink fix.

---

## 8. Gaps the fleet's critic flagged (worth a decision, not urgent)

1. **No pressure-test evidence exists anywhere** despite CLAUDE.md and writing-skills mandating that discipline skills be pressure-tested before deployment. Add a lightweight ledger convention (`specs/skill-test-log.md`: scenario, date, model, control-vs-skill outcome) and backfill "untested — adopted on upstream's evidence" honestly for the ports. Without it, the repo's central quality claim is unfalsifiable and the next audit re-litigates it.
2. **Missing-skill candidates** implied by your workflow: (a) scraper/ingest *construction* (politeness, retries, vintage-stamped raw capture, ingest layout — develop-testing-strategy tests them, bls-data-context documents the endpoints, nothing governs building them); (b) analysis write-up/deliverable authoring (validate-data gates the numbers; nothing governs the memo).
3. **writing-skills' naming examples cite skills that don't exist here** (using-skills, defense-in-depth, condition-based-waiting as top-level skills) — swap in real repo names so the exemplars are greppable in the collection they govern.

---

## 9. Suggested execution order

**P0 — this week (breakage & provenance):**
1. Fix bayesian-workflow frontmatter (§1.1) — one line.
2. `git rm` the three PDFs + NOTICE/README truthing (§1.2, §5.3).
3. Symlink decision for the 10 uninstalled skills; at minimum tech-debt + design-architecture (§1.3).
4. SDO ledger path unification (§1.4).
5. tech-debt scan.sh hidden-files + ROOT fixes (§1.6).
6. Gate A command + missing-scratch error (§1.7); add the recommend-visualization test line to CLAUDE.md.
7. Bare-python → uv command blocks in the three skills (§1.8).

**P1 — high-value correctness & the subagent upgrades:**
8. finishing-a-development-branch Step-6/Option-2/base-branch fixes (§1.5).
9. Custom read-only reviewer agent + template consistency fixes (HEAD~1, DIFF_FILE, NEEDS_CONTEXT, Global Constraints channel, model-tier refresh) (§3).
10. Delete/wire the two orphaned reviewer prompts; brainstorming's three upstream remnants + beacon decision.
11. The seven description trims + weak-description rewrites (drafts exist for all; per the Iron Law, micro-test discipline-skill wording changes before deploying).
12. Documentation/provenance sync (§5 items 1-8).

**P2 — wiring, trims, personalization:**
13. Cross-skill wiring (§6). 14. Token-economy trims (SDO, writing-skills, dispatching-parallel-agents, using-git-worktrees, bayesian-workflow references moves). 15. Personalization passes (§7). 16. Mechanical gates in build/ (§5). 17. Critic items (§8).

---

*Verification note: every finding in §§1, 3-6 above was either adversarially verified by an independent agent (45/45 confirmed), spot-verified by hand in this session (scan.sh rg path, brainstorming path, Gate A vacuity, ledger mismatch, symlink inventory, plugin-disabled status, live frontmatter/description behavior), or comes with file:line evidence from the auditor. The 91 low-severity items folded into §4 were reported by auditors with evidence but not independently re-verified.*

---

## Appendix A — drafted frontmatter description rewrites

Proposed replacement descriptions from the per-skill auditors. Each preserves the concrete trigger phrases and cuts content-summary clauses; all are ≤1024 chars. Per the writing-skills Iron Law, micro-test wording changes on discipline skills against the current description before deploying.

### bayesian-workflow (770 chars)

> Use when building, fitting, diagnosing, comparing, or reporting on Bayesian/probabilistic models with NumPyro (JAX) and ArviZ — consult BEFORE writing any Bayesian model code, not after. Trigger on: prior elicitation or choosing priors, MCMC/NUTS inference, convergence diagnostics (divergences, R-hat, ESS), model comparison (LOO-CV, ELPD, stacking weights), hierarchical/multilevel models, count regressions, logistic regression with uncertainty, state-space or latent time-series models, prior sensitivity analysis, calibration (PIT/LOO-PIT), presenting Bayesian results to non-technical audiences, or mentions of NumPyro, Pyro, JAX, BlackJAX, ArviZ, InferenceData, DataTree, credible intervals, HDI, posterior distributions, shrinkage, or uncertainty quantification.

### bls-data-context (936 chars)

> Use when working with U.S. Bureau of Labor Statistics employment, wage, or labor-turnover data — QCEW, CES (national or state/area SAE), JOLTS, BED/BDM, OEWS/OES, ECI, ECEC, CPS — or building pipelines over their flat files or API. Consult BEFORE interpreting a BLS series, constructing or parsing a series ID, joining two BLS sources, reconciling to an official total, or reasoning about revisions / as-of correctness. Trigger on: QCEW, CES, CES-SA, SAE, JOLTS, BED, BDM, OEWS, OES, ECI, ECEC, CPS, LAUS, NAICS / SOC codes, series_id, M01–M13, download.bls.gov/pub/time.series, vintage / benchmark / revision, place-of-work vs residence, jobs vs persons, thousands-vs-persons units, "pay period including the 12th", UI / UCFE coverage, net birth-death model, benchmarking CES to QCEW, JOLTS alignment to CES, or reconciling a payroll-provider or nowcast series to BLS. The detailed program facts that agents otherwise get subtly wrong.

### brainstorming (426 chars)

> Use when the user proposes new functionality — a feature, component, script, scraper, pipeline, analysis, or behavior change — and no approved design or spec exists yet; before writing any code, scaffolding a project, or invoking an implementation skill. Trigger on "let's build", "add a feature", "create a tool", "I have an idea", or any request that would otherwise jump straight to implementation, however simple it looks.

### design-architecture (1019 chars)

> Use when authoring or evaluating Architecture Decision Records (ADRs) for data and modeling systems — choosing between technologies (NumPyro/JAX vs PyMC, Polars vs pandas, Trino vs DuckDB, one parquet layout vs another), when a design decision spans multiple packages or repos, when reviewing a design proposal or spec for whether its trade-offs are honest, or when a past decision keeps getting re-explained or re-litigated. Trigger on: ADR, architecture decision, design record, design doc/spec review, "should we use X or Y", "document this decision", "why did we pick", trade-off analysis, alternatives considered, reversibility / blast radius, superseding a prior decision, parquet store layout and dedup/vintage policy, scraper resilience (retry/backoff/fixtures), as-of / vintage / point-in-time data modeling, multi-package workspace boundaries, inference engine choice, or determinism/seed/parity decisions — especially when the same problem is solved more than one way across repos with no recorded rationale.

### develop-testing-strategy (1023 chars)

> Use when designing a test strategy or plan for data-science code — web scrapers, Polars pipelines, or Bayesian models: a repo with zero or smoke-test-only tests, adding the first tests to an ETL/scraper/model package, a scraper that silently breaks on a site relayout, a pipeline emitting malformed parquet (wrong schema, dropped rows, exploded null rate, duplicate keys, stale data), a NumPyro/PyMC model needing more than 'it ran', parameter recovery / SBC-lite / golden-master parity / seed determinism, slow MCMC tests in CI, or as-of/vintage correctness and future leakage. Trigger on: 'how should we test this', 'what tests do we need', 'test plan', 'test strategy', 'add tests', 'this has no tests', flaky or slow suites, pytest marker design (network/slow/real_store) and CI exclusions, recorded HTML fixtures vs live sites, schema/row-count/null-rate/freshness assertions, or httpx, BeautifulSoup, lxml, Polars, parquet, NumPyro, JAX, PyMC, PRNGKey, golden master, BLS/QCEW/CES/JOLTS. Consult BEFORE writing tests.

### dispatching-parallel-agents (300 chars)

> Use when 2+ tasks are independent — no shared state, no ordering dependency — and are being worked sequentially: multiple test files failing with different root causes, several subsystems broken independently, or a batch of self-contained fixes or investigations that could run as parallel subagents.

### executing-plans (274 chars)

> Use when you have a written implementation plan to execute yourself, task by task, in the current session — e.g. a plan file from writing-plans in specs/plans/ — because tasks are tightly coupled or your human partner asked for direct execution rather than subagent dispatch

### explore-data (977 chars)

> Use when profiling a new dataset with Polars before analysis or modeling — first contact with a parquet/CSV/scrape whose shape, schema, null rates, or cardinality is unknown; when checking whether a candidate key (series_id + ref_date) is actually unique; when you suspect duplicates, sentinel codes (-1, 9999, "", "N/A", "."), constant or high-null columns, or mixed types from a raw ingest; when confirming the as-of/vintage layout on revised series (one row per series-period-vintage) before tagging or joining; when panel diagnostics are needed — coverage by period/geography/industry, balance, entry/exit; or when comparing provider microdata against QCEW/CES/JOLTS/BED. The pre-flight before bayesian-workflow, recommend-probabilistic-model, or recommend-visualization. Trigger on new microdata, "explore/profile this dataset", null/duplicate/quality checks, schema inspection, scan_parquet, .describe(), value_counts, .null_count(), n_unique, or "is this column a key?".

### finishing-a-development-branch (430 chars)

> Use when implementation on a development branch is complete and tests pass, and the work needs wrapping up — merge vs. PR vs. keep vs. discard is being decided, or a feature branch's worktree needs cleanup. Trigger on: "the feature is done", "ready to merge", "should I open a PR", "clean up this branch/worktree", deciding how to integrate a completed feature branch, or finishing work started with the using-git-worktrees skill.

### receiving-code-review (323 chars)

> Use when receiving code review feedback — from the user, a GitHub PR comment thread, a review bot, or a reviewer agent (e.g. output of the requesting-code-review skill) — before implementing any suggested change, especially when items are unclear, conflict with prior decisions, or seem technically wrong for this codebase.

### recommend-probabilistic-model (871 chars)

> Use when choosing a modeling approach for a problem and its data — "which model/method should I use", "what approach fits this dataset", "recommend a model", "is this Poisson or negative binomial", "how do I handle overdispersion / zero-inflation / panel data / many predictors". Covers regression / GLMs / counts, classification, hierarchical/multilevel, time series & state-space, Gaussian processes, dimensionality reduction & (dynamic) factor models, mixtures & clustering, and probabilistic graphical models, grounded in Kevin Murphy's Probabilistic Machine Learning (PML) books. Trigger on model selection, "which method for X", recommending an approach before fitting, or deciding between Poisson/NB/zero-inflated, pooled vs hierarchical, GP vs parametric, PCA vs factor model, HMM vs state-space. Consult BEFORE fitting a model — not for executing the fit itself.

### requesting-code-review (290 chars)

> Use when completed work needs a code review — after finishing a task or major feature, before merging a branch or opening a PR, when reviewing a commit range (BASE..HEAD) against its plan or requirements, when stuck and wanting a fresh pass on recent commits, or after fixing a complex bug.

### subagent-driven-development (774 chars)

> Use when executing an implementation plan task-by-task in the current session by dispatching subagents — a fresh implementer per task, a task-scoped spec+quality review after each, and a final whole-branch review. Trigger on: "execute this plan", "implement the plan", a plan header naming subagent-driven-development as the required sub-skill, a specs/plans/*.md handoff from writing-plans, or resuming a partially executed plan (check the progress ledger before re-dispatching anything). Covers model-tier selection per dispatch, file handoffs (task briefs, report files, review packages), fix-subagent loops, and compaction-safe progress tracking. Not for tightly coupled tasks needing one continuous context, or for execution in a separate session (use executing-plans).

### systematic-debugging (431 chars)

> Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes — including flaky or intermittent tests, race conditions or arbitrary sleeps/timeouts in tests, test pollution where state leaks between tests, errors deep in a stack trace, works-locally-but-fails-in-CI, a regression after a dependency or config change, or when previous fixes didn't stick and you're tempted to try one more quick change.

### tech-debt (906 chars)

> Use when auditing a research or data codebase for technical debt — periodic code-health triage, cleaning up before handing a project off, deciding what to refactor or delete next, building a maintenance backlog, or estimating refactor effort. Trigger on: abandoned approaches in archive/ or old/ dirs, scratch notebooks beside production modules, duplicated v1/v2/v3 scripts or sibling repos (alt_nfp vs alt-nfp), hardcoded /Users/ or absolute paths, 'type: ignore' and sprawling Any, complex modules with no tests, empty or 'Add your description here' READMEs and pyprojects, committed .env files or API keys, raise NotImplementedError / TODO / FIXME stubs, and reproducibility hazards (datetime.now() in a pipeline, magic seeds, as-of/vintage joins without guards). Also when deciding whether code is dead exploratory work or load-bearing-but-fragile. Tuned for a Polars / NumPyro / PyMC / BLS-ETL stack.

### using-git-worktrees (343 chars)

> Use when starting feature work, a bugfix, or plan execution that must not disturb the current checkout — before executing an implementation plan, when the working tree has uncommitted changes to protect, when the user asks for a worktree, isolated workspace, or branch sandbox, or when parallel agents need separate checkouts of the same repo.

### validate-data (845 chars)

> Use when QA-ing a dataset or an analysis before it is shared, published, or fed downstream — the last gate before a number leaves your laptop. Trigger on: "is this ready to publish", "sanity-check this dataset/parquet", "review my analysis", "do the numbers reconcile", "why doesn't this match the official total", validating an ETL output, pre-publish review, "I can't reproduce yesterday's run", a silent cache or fallback masking a failure, a coverage ratio that looks too clean, a decomposition whose components don't add up, unexpected nulls / duplicate keys / dtype drift in a parquet, future leakage past the as-of date on revised series (QCEW/CES/JOLTS vintages), or a claim that a result is "fine" without an independent check. Always consult before signing off on data or an analysis — these checks are the ones agents skip unprompted.

### verification-before-completion (298 chars)

> Use when about to claim work is complete, fixed, done, or passing — before committing, pushing, opening a PR, marking a task or todo complete, moving to the next task, or relaying a subagent's success report; also when tempted to say "should work now" or "looks correct", or to wrap up while tired.

### writing-plans (306 chars)

> Use when you have a spec, design doc, or requirements for a multi-step task and need an implementation plan before touching code — "write a plan", "plan this feature", "break this into tasks", a finished spec in specs/ awaiting its plan, or before handing work to subagents or a separate execution session.

### writing-skills (397 chars)

> Use when creating a new skill, editing or renaming an existing skill, or verifying a skill before deployment — including writing SKILL.md frontmatter (name/description limits), fixing a skill that fails to trigger or over-triggers, tightening a description, structuring references/ and scripts/, pressure-testing a discipline skill, or micro-testing wording changes against a no-guidance baseline.
