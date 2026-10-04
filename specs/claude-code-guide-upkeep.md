# Claude Code Guide Upkeep — Design Spec

**Status: DESIGN APPROVED (2026-10-03); written spec awaiting review.**
The owner approved the scope, the architecture and five design parts in a
brainstorming pass. This document is the handoff for implementation planning.
Nothing here has been implemented. It is staged: each stage under "Sequencing"
gets its own plan, in order.

## Purpose and scope

`specs/claude-code-customization-guide.md` records Claude Code facts that
change as Claude Code releases ship, about six releases a week. Re-verifying the
whole guide on every release costs too much (the 2026-10-03 refresh: six Sonnet
verifiers, $22.05 at list price). Guide upkeep does three things:

- notices when a release or a docs edit makes part of the guide stale;
- re-verifies only those parts;
- slowly re-audits the rest, because some claims were wrong when written
  (the July pass had 5 such claims).

The name is chosen to stay clear of two existing uses of "drift":
`install.py`'s dependency-drift check and `specs/superpowers-drift-2026-09-03.md`.

Five pieces share one manifest:

1. A deterministic **detector** that spends no model tokens.
2. A **trigger**: a project SessionStart hook.
3. **Triage**: one cheap Sonnet pass that separates real changes from noise.
4. **Scoped re-verification** and a **monthly audit**, run through a
   Claude-only project skill.
5. **Live probes** for behaviour the docs may not reflect.

Nothing auto-commits. Every edit to the guide or the baseline is left
uncommitted for the owner to review.

This session owns the stamp, the source map, the detector, the trigger, scoped
re-verification and probes. A separate brainstorm owns the **guide-as-hub
wiring**: stable section anchors, citations in dependent files, and an
anchor → citing-files index. This spec consumes that work only through the
interface in R9, and no stage waits on it.

## Measured baseline (2026-10-03)

| Fact | Evidence |
|---|---|
| Claude Code 2.1.289 shipped on 2026-10-03, one release past the guide's 2.1.288 stamp. At least three of its notes touch §6/§7 claims: deny/ask rules vs mod approvals, `Read` deny rules on @-mentioned files, Bash deny rules behind an env-var prefix. No docs page changed. | `changelog.md` diff against the snapshot |
| 53 of the 55 snapshot pages refetched byte-identical about 6 h after the snapshot. The two that changed: the changelog (the 2.1.289 block) and the anthropic.com HTML news page (markup churn only). | `/tmp/ccdrift-probe/fetch_all.py`, a session-local probe script |
| The docs host sends no ETag. `Last-Modified` is the serve time and `Cache-Control` is `max-age=0`. Content hashing is the only usable change signal. | response headers for `changelog.md`, `skills.md` and `hooks.md` |
| `llms.txt` lives at `code.claude.com/docs/llms.txt` and lists 220 `/docs/en/` pages. `/docs/en/llms.txt` returns 404. | live fetch |
| `env-vars.md` is 555 lines with 9 headings and 381 table rows that begin with a backtick. `settings-reference.md` is 6,408 lines with 296 headings, about one `###` per setting. Both feed 4–5 of the 6 verifier units. | snapshot |
| Matching changelog topic keywords, as the refresh verifiers' lists did, flags 37–46 of the 59 releases from 2.1.220 to 2.1.289 for every unit. | keyword replay |
| Matching backticked identifiers flags 2–15 of the 59 releases for §2, §5, §6 and §7, but 24–38 for §1, §3, §4 and §8 (`/model` matched 36 notes, `/plugin` 37, `/mcp` 23). It misses prose-only notes such as 2.1.289's mod/deny fix. | keyword replay |
| The refresh's six verifiers cost $2.49–$5.26 each at Sonnet 5.5 list, $22.05 in total. Cache reads (81.6M tokens) dominate. Peak contexts were 312K–394K and sum to about 2.1M, close to the brief's "about 2.2M tokens", which therefore counts context size, not billed volume. | refresh transcript `95978d08…`, usage counted once per API response |
| Claude Code versions on this Mac during the brainstorm: VS Code extension 2.1.288; desktop app 2.1.286 (it bundles 2.1.284 and 2.1.286); `claude` on PATH **2.1.265** (`~/.local/bin/claude` → `versions/2.1.265`, unchanged since 2026-09-08); latest published release 2.1.289. The owner then updated the PATH CLI to 2.1.289 (launcher re-pointed 2026-10-03 20:17). Why auto-update had stopped at 2.1.265 is unknown. | transcripts' `version` field, process list, `claude --version` before and after |
| The guide carries 33 ⚠ markers on 32 lines (line 388 has two), plus the legend in its header. 5 are on headings. | `grep` |
| The refresh's verifier prompts are recoverable. Each gives guide line ranges, primary docs pages, changelog keywords and the quote-backed A/B/C report contract. | `95978d08…/subagents/*.jsonl` and `*.meta.json` |
| The 2.1.288 docs snapshot was preserved at `~/.cache/agent-skills/cc-guide/2.1.288/`. It is an identical copy of `/tmp/ccguide-2026-10-03/` (55 pages, `check/qcheck.py`, two guide copies). | `diff -r` |

## Decisions and alternatives

1. **Detect with per-block hashes (approach A).** The manifest stores a SHA-256
   for each docs block a unit depends on. A block is a heading section or a
   table row. The detector refetches, re-splits, re-hashes and compares.
   - *Rejected:* page hashes plus a local diff cache. Without the cache this
     can only report "page changed", and the shared pages would still flag
     most units.
   - *Rejected:* changelog only. It is blind to docs-only edits and never
     re-baselines.
2. **Key on published releases, never on an installed binary.** Four versions
   coexist on one machine, so "installed version" names nothing. The trigger
   decides *when* the detector runs. What it compares against is always the
   published docs and changelog.
3. **The changelog channel is mandatory and needs semantic triage.** 2.1.289
   changed behaviour with zero docs edits. Keyword filters either flag 63–78% of
   releases or miss prose-only notes. Matches are therefore hints for a cheap
   model pass and never filter anything out.
4. **Trigger: a project SessionStart hook.** It runs at most once a day, in
   the background, and reports only through `systemMessage`, which is shown to
   the user and never to the model.
   - *Rejected:* the status line. It is user-global, none is configured, and
     the owner works in the desktop app.
   - *Rejected:* a cloud routine (no personal skills, no cache), a scheduled
     desktop task (tokens per run) and scheduled CI (adds `.github/`, and its
     notification is outward-facing). All were weighed against the hook.
5. **The Claude-only command is a project skill.**
   `build/sync_runtime_assets.py` emits a Gemini adapter for every
   `commands/*.md`, with no opt-out. A skill at `.claude/skills/guide-upkeep/` is
   invisible to `sync_runtime_assets.py`, `install.py` and
   `check_frontmatter.py`, all of which scan only the root `skills/`, `agents/`
   and `commands/`. The `.claude/rules/` symlink is the precedent.
   - This does not touch `specs/agent-skills-portability.md` decision 2, which
     rejects re-listing `skills/` through an in-repo `.claude/skills` link. This
     is a separate, repo-local tool.
6. **The verifier is a project agent** (`.claude/agents/guide-verifier.md`:
   `tools: Read, Grep, Glob`, `model: sonnet`, `omitClaudeMd: true`).
   - Read-only is enforced by the tool list, not requested in a prompt.
   - The model is pinned on a subagent, where pins hold in auto mode. A skill
     `model:` pin does not hold there.
   - Not Haiku: auto mode drops Haiku skill pins, and Haiku 4.5's retirement
     window opens 2026-10-15.
7. **The docs cache lives outside every checkout**, at
   `~/.cache/agent-skills/cc-guide/`. Anthropic's text cannot be committed by
   accident, it survives worktree removal, and all sessions share one copy.
   The repo commits only hashes, slugs, release labels and terms.
8. **One staged spec**, not separate specs for detection and probes. A probe is
   a third evidence channel in the same manifest. Designing the manifest once,
   with all three channels, avoids a schema migration later.
9. **Probes run the `claude` on PATH, and the owner keeps it current.** The
   harness records the version it ran and refuses to log a result from a binary
   older than the latest release, unless given `--allow-old`.
   - *Rejected:* probing the desktop app's bundled binary, because its path is
     undocumented.
   - *Rejected:* treating 2.1.265 as an intentional pin.

## Requirements

### R1 — Manifest and baseline (`build/guide_upkeep/`)

R1.1 **Two files, split by writer.**
- `manifest.toml` is configuration. The owner edits it rarely, it is read with
  stdlib `tomllib`, and its comments record why each choice was made. No tool
  writes it.
- `baseline.json` is state. Only `baseline.py` writes it (R4.4): once at
  initialization, then only during an acknowledgement or a re-verify the owner
  approves.

R1.2 **`manifest.toml` holds:**
- the guide path and the source URLs: the docs base, `llms.txt`, the changelog,
  and the platform base `platform.claude.com/docs/en/`;
- cadences: `changelog_days = 7`, `probe_days = 7`, `audit_days = 30`;
- the units, in a fixed order (R1.4). Each unit has its anchors, its pages
  (each marked `all` or `terms`), `extra_terms`, `exclude_terms` and probes;
- exclusions, each with its reason: `whats-new/*` duplicates the changelog; the
  anthropic.com Haiku 4.5 launch post is a historical figure and its HTML
  churns; `changelog.md` is parsed rather than hashed (R3.3).

R1.3 **`baseline.json` holds, per unit:**
- `checked_through`: the release and date through which this unit's changelog
  backlog and docs blocks are resolved;
- `audited`: the release and date of the last full-unit audit;
- `blocks`: page → block key → hash. A block shared by two units is stored
  under each, so acknowledging it in one unit never hides it from the other.
- `snapshot`: per page, the release whose cached snapshot holds the baselined
  text. Pages are re-baselined at different releases, and triage diffs (R5.1)
  read from here.

It also holds the `llms.txt` slug list from the last baseline.

R1.4 **Seed units.** These come from the refresh's six verifier scopes. Anchors
are written here as heading names; R9 defines the IDs. The `all` and `terms`
marks are initial values, to be tuned in `manifest.toml` after the first runs.

| Unit | Guide regions | `all` pages | `terms` pages |
|---|---|---|---|
| `overview` | §1; §2; §8 › Know your numbers first, Session hygiene, MCP hygiene, Scale ceremony to task size, Guard expensive operations | context-window, costs, monitoring-usage | mcp, commands, features-overview, debug-your-config, best-practices, statusline, interactive-mode, env-vars, memory, skills |
| `skills` | §3; §4 | skills | commands, plugins/components, plugins/loading, claude-directory, settings-reference, env-vars, auto-mode-config, model-config |
| `subagents` | §5, except Route models by role | sub-agents | agents, workflows, agent-teams, model-config, env-vars, tools-reference, prompt-caching, settings-reference, cli-reference |
| `rules` | §6 | memory, settings, permissions | settings-reference, permission-modes, claude-directory, large-codebases, env-vars |
| `hooks` | §7 | hooks, hooks-guide | settings-reference, env-vars |
| `models` | §5 › Route models by role; §8 › Caching, Model routing; Further reading | prompt-caching, model-config, fast-mode, advisor, platform about-claude/pricing, platform about-claude/models/overview | platform build-with-claude/prompt-caching, platform about-claude/model-deprecations, platform models/haiku-4-5/overview, costs, env-vars, settings-reference, commands |

R1.5 **The initial baseline** is computed from the **2.1.288 snapshot** in the
cache, not from live docs. A docs edit published after the stamp must show up
as a change, not be absorbed. Every unit starts at
`checked_through = audited = 2.1.288 (2026-10-03)`.

### R2 — Blocks (`blocks.py`)

R2.1 **Preamble.** Strip the leading "Documentation Index" blockquote: the
`>` lines at the top of the page that point to `llms.txt`. Any text after it
and before the first heading becomes the `(intro)` block. Today that is empty
on `code.claude.com` pages, but platform pages may differ.

R2.2 **Headings.** Cut at *every* ATX heading outside code fences. A block runs
from its heading to the next heading of any level, so a parent's block is only
its intro text. The key is the heading path, with ancestors joined by ` › `. A
repeated path gets an ordinal suffix (`#2`).

R2.3 **Tables.** Each table row inside a block, excluding the header and
separator rows, becomes its own block. Its key is the heading path plus
` › ` plus the row's first cell, with an ordinal suffix if repeated. The
remaining text stays in the heading's block.

R2.4 **Normalize, then hash.**
1. Replace each `](target)` with `]()`. URL moves after a docs restructure are
   cosmetic for claims.
2. Collapse whitespace runs and strip each line.
3. Drop empty lines.
4. Hash with SHA-256 over UTF-8 and keep the first 16 hex characters.

R2.5 **Terms.** A unit's terms are the backticked spans in its guide regions:
- outside fenced code;
- found by pairing every backtick first and filtering length afterwards, to
  3–60 characters. Filtering inside the regex mis-pairs around 2-character
  spans such as `` `if` ``, a bug the keyword replay hit;
- minus a stoplist of generic words such as `true`, `name`, `model` and
  `paths`;
- plus `extra_terms`, minus `exclude_terms`.

Matching is case-sensitive substring matching.

R2.6 **Selection.**
- On an `all` page, every block counts.
- On a `terms` page, a block counts if its key or normalized text contains a
  term.
- A block that is selected now but absent from the baseline is reported as
  *new*. Example: the guide gained a claim about a new setting.
- A baselined block that is still on the page but no longer selected, because
  the guide dropped the term, is *deselected*. That is informational, and the
  next `rebaseline` drops it. Only a block key that has disappeared from the
  page is *missing*.

### R3 — Detector (`check.py`, Python 3.13, stdlib, read-only)

R3.1 **Fetch.**
- Fetch `llms.txt`, the changelog and every mapped page, with parallel GETs, a
  30 s timeout and one retry.
- Send a descriptive User-Agent that carries no personal data.
- Write the pages to `~/.cache/agent-skills/cc-guide/latest/docs/`, overwriting.
- `--docs DIR` runs offline against a local directory, for tests and for R1.5.

R3.2 **Compare.** For each unit, report its *changed*, *missing* and *new*
blocks as findings, and its *deselected* blocks for information (R2.6).
- A mapped page that is absent from `llms.txt` or returns 404 is a **missing
  page**, which is a finding, never "unchanged". Platform pages, which
  `llms.txt` does not list, are checked by fetch status only.
- `llms.txt` slugs added or removed since the baseline are listed for
  information.

R3.3 **Changelog.**
- Parse `<Update label="X" description="DATE">` blocks and their `* ` bullets.
- Order versions numerically.
- For each unit, list the releases after its `checked_through`, with every
  bullet. Term hits are marked as hints only.

R3.4 **Due rules.**

| Item | When it is due |
|---|---|
| Changed, missing or new blocks | Immediately |
| A unit's changelog batch | Once its oldest untriaged release is ≥ `changelog_days` old |
| A probe | When it is registered but has no `PROBES.md` row, or when ≥ `probe_days` have passed since its last row and a release has shipped since the version that row records (R8.5). |
| An audit | When ≥ `audit_days` have passed since the most recent audit of **any** unit. It targets the unit with the oldest `audited` date, with ties broken in manifest order. This is the shared clock that yields one unit a month. |
| A stamp mismatch or a guide-lint failure | Immediately (R4) |

R3.5 **Report.**
- Write it to `~/.cache/agent-skills/cc-guide/reports/<baseline-sha12>.json`,
  keyed by the baseline's hash so a worktree mid-re-verify never reads main's
  report.
- It records: `generated_at`, `latest_release`, the hashes of the manifest,
  baseline and guide, per-unit findings, releases per unit, probes due, audit
  due, the stamp mismatch, lint results and errors.
- It also prints a human-readable summary.

R3.6 **Exit codes.**
- **0**: nothing to act on.
- **1**: at least one item is due.
- **2**: an error, such as network, parse, an invalid manifest or baseline, or
  an unresolvable anchor.

This follows `check_snippets.py`. A crash or a network failure can never look
clean.

R3.7 `check.py` never writes inside the repo.

### R4 — Stamp and guide lint

R4.1 **The stamp is per unit**, held in `baseline.json`. The guide shows one
global line, generated inside the marked region
`<!-- upkeep:stamp -->…<!-- /upkeep:stamp -->` in the header blockquote. Its
content is the minimum `checked_through` and the oldest `audited` across
units. Example: "Checked against the Claude Code docs and changelog through
2.1.288 (2026-10-03); oldest full re-verification 2026-10-03, at 2.1.288."

Everything outside the markers stays owner prose, including the July/2.1.219
history. Stage 1 converts today's first header sentence into the marked
region, and the owner reviews that edit.

R4.2 **The detector reports a stamp mismatch** whenever the region disagrees
with `baseline.json`.

R4.3 **Guide lint** (offline, run inside `check.py`):
- every `2.1.NNN` in the guide is a changelog release label;
- every table has consistent column counts;
- every JSON code block parses.

These are the refresh's PR test plan, made automatic.

R4.4 **Baseline writer** (`baseline.py`). It is the only writer of
`baseline.json` and the stamp region. Its subcommands:
- `init`: R1.5. Lands in Stage 1.
- `rebaseline`: re-hash a unit's selected blocks, either all or listed keys,
  from `latest/`, and snapshot those pages to `<release>/docs/`.
- `advance`: set a unit's `checked_through`.
- `audited`: set `audited`, which also advances `checked_through`.
- `stamp`: regenerate the region.

All of them leave their changes uncommitted.

### R5 — Triage (`/guide-upkeep triage`)

R5.1 **Re-run the detector**, then build one packet (format in the skill's
`references/`):
- the whole guide, with line numbers;
- each changed block's current text, plus a unified diff against the page's
  baselined text (from the snapshot release named in `baseline.json`, R1.3)
  when that snapshot is in the cache;
- every bullet of each unit's untriaged releases, with term hits marked.

After a long absence, split the packet by release range.

R5.2 **Dispatch `guide-verifier` in triage mode**, with the packet inline. It
has read-only tools but needs none. This costs about $0.05–0.20 a week.

R5.3 **Output.**
- Every changed, missing or new block gets one row:
  `item | TOUCHES / NOISE / UNSURE | unit | guide line | "guide quote" | "source quote" | why`.
  A NOISE row needs no guide quote, but it needs a reason.
- Changelog bullets get a row only when they are TOUCHES or UNSURE.
- Every release in the packet gets one coverage line,
  `release | units touched, or none`.

**Completeness check (deterministic).** If the output omits a block row or a
release's coverage line, that item becomes UNSURE for every unit it could
affect. Silence never counts as NOISE.

R5.4 **`quotes.py` re-greps every quote.** It is the successor to
`qcheck.py`: input lines `file<TAB>quote` against a named file set, output
FOUND with `file:line`, or MISSING.
- Guide quotes are checked against the guide.
- Source quotes are checked against the bullet or block text.
- **A row whose quote fails becomes UNSURE.** UNSURE is handled as TOUCHES:
  triage fails safe.

R5.5 **Resolution in the same run**, with no pending queue. For each unit:
- **All rows NOISE:** the owner acknowledges. Run `rebaseline` for the affected
  blocks, then `advance` to the newest triaged release.
- **Any TOUCHES or UNSURE:** run the scoped re-verify (R6) now.
- **Deferred:** nothing advances, and the next triage shows the unit again.

### R6 — Scoped re-verification and audit

R6.1 **`.claude/agents/guide-verifier.md`** has the frontmatter in Decision 6
and a short description: dispatched only by `/guide-upkeep`. Its body holds the
contract:
- the three modes: triage, reverify, audit;
- the report formats;
- the accuracy rules, including the JUDGMENT rules;
- never edit a file.

R6.2 **Two modes.**

| Mode | Scope | Expected cost |
|---|---|---|
| `reverify <unit>` | The unit's guide lines, its TOUCHES/UNSURE rows, the changed blocks inline, and grep over the snapshot | ≈ $0.30–1 |
| `audit [<unit>]` | Every claim in the unit, all its pages, and its changelog since `checked_through` | ≈ $2.50–5.30 |

Both work against the snapshot of the current release: `<release>/docs/`,
copied from `latest/`.

R6.3 **Report contract.** This is the refresh's three-part format plus one
verdict.
- **A.** `L<line> | claim ≤12 words | CONFIRMED / STALE / WRONG / PARTIAL / NOT FOUND / JUDGMENT | doc:line | "verbatim quote ≤25 words" | proposed wording`
  - Proposed wording appears only for STALE, WRONG and PARTIAL. It is the
    verifier's own paraphrase and never a doc sentence.
  - Absence alone is NOT FOUND, never WRONG.
- **B.** Changelog items that change a claim in scope: version, one line,
  changelog line number.
- **C.** At most four omissions that would *change* existing advice.

R6.4 **Facts versus judgment.**
- A claim is *checkable* if a doc page could confirm or refute it: names,
  defaults, numbers, behaviour, precedence, syntax.
- Recommendations get **JUDGMENT**, and the verifier never proposes wording for
  them.
- When a judgment rests on a mechanism, the mechanism is checked and reported
  as `JUDGMENT (mechanism STALE)` with its quote. Example: the `opusplan`
  bullet rests on the cache-read prices.
- Lines next to a `TODO(owner)` comment are report-only.

R6.5 **Post-processing in the skill**, all deterministic:
1. `quotes.py` re-greps every A-row quote, and a row with a failing quote is
   discarded. This is the refresh rule, and it is the opposite of triage's
   escalation.
2. Surviving corrections are applied to the guide in the **working tree only**.
3. The JUDGMENT items go to the owner as a separate "owner's call" list, never
   applied.
4. Run `rebaseline`, then `advance` the unit to the newest release the run
   covered: the newest triaged release for a scoped re-verify, the current
   release for an audit. An audit also runs `audited`. Then run `stamp`.
5. Run the guide lint (R4.3).
6. List the dependents of the edited anchors (R9.3).

Nothing is committed. Quotes appear only in session reports, never in a commit.

### R7 — Trigger (`notice.py` and `.claude/settings.json`)

R7.1 **Hook entry.** `.claude/settings.json` gains a SessionStart command hook
with matcher `startup`, so it does not fire on resume, `/clear` or compaction.
It runs `python3 "$CLAUDE_PROJECT_DIR"/build/guide_upkeep/notice.py`.

R7.2 **`notice.py` is stdlib-only and 3.9-compatible.** Hooks run under the
app's PATH, where `python3` may be `/usr/bin/python3` 3.9. It always exits 0
and writes only JSON `{"systemMessage": …}` to stdout. Plain stdout would
become model context.

R7.3 **Flow.**
1. Read `reports/<baseline-sha12>.json`.
2. If the report is older than 24 h, or missing, locate `uv`: on PATH, then
   `~/.local/bin/uv`, then `/opt/homebrew/bin/uv`. Run
   `uv run --python 3.13 python build/guide_upkeep/check.py` with a timeout.
   Interactive SessionStart hooks run in the background, so this does not delay
   the session.
3. Respond by outcome:
   - **Exit 0:** print nothing.
   - **Exit 1:** print one line naming every due item, e.g.
     `guide-upkeep · 2 blocks changed (hooks, rules) · 9 releases untriaged (oldest 8 d) · probes due 3 · audit due: skills → /guide-upkeep`.
   - **Exit 2, no `uv`, or a timeout:** print an error line with the age of the
     last good check. It never stays silent.

R7.4 **One notice a day.** The same report is shown at most once a day, via
`notice-state.json` in the cache. A changed report is shown again.

### R8 — Probes (`probes.py`, `PROBES.md`)

R8.1 **The registry is in `manifest.toml`.** Each probe has an ID, the unit it
backs, and the guide anchors it supports.

| Probe | Unit | Asserts the documented behaviour |
|---|---|---|
| `guard-payload` | hooks | Wraps `hooks/probe-readonly-guard.sh`, run from a scratch git repo, and records its 3 checks. |
| `agent-model-pins` | subagents | Explore (via `agents/explore.md` shadowing the built-in) and test-runner are served Haiku. The code-reviewer `effort: xhigh` pin holds. All tested on the production path: an Agent-tool dispatch from a parent session. |
| `skill-frontmatter-pins` | skills | A fixture skill pinned to `model: haiku` keeps the session model in auto mode. A fixture `effort:` pin shows up on the skill turn's assistant lines, giving evidence for the open deferred item under `31-skill-model-pin-removal` either way. |

R8.2 **Binary.** Run `claude` from PATH (or `--claude PATH`) and record
`claude --version`. Refuse to log a result when the binary is older than the
latest published release (the newest changelog label), unless given
`--allow-old`; a result logged that way records the flag.

**Prerequisite, an owner action, met on 2026-10-03:** the PATH CLI is current
(2.1.265 → 2.1.289). It had silently stopped updating once before, so the
refusal rule is what catches a recurrence.

R8.3 **Isolation.**
- Each run happens in a fresh temp directory outside the repo. A session whose
  cwd was this repo leaks its `CLAUDE.md` and gitStatus into every subagent
  (memory note `microtest-isolation-channels`, Channel 5).
- Load `--setting-sources user`, plus `project` only where a fixture lives in
  the temp directory. This repo's settings and hook never load.
- Pin the mode under test with `--settings` (e.g.
  `{"permissions":{"defaultMode":"auto"}}`).
- Put the prompt first and redirect stdin from `< /dev/null`.

R8.4 **Assertions.**
- Assert on raw `--output-format stream-json` events. Fall back to the probe
  session's transcript (`message.model`, `effort`) only for fields the stream
  lacks.
- Never assert on the model's prose.
- Record one real stream per probe before writing its assertion, as the guard
  probe did.
- Outcomes:
  - **PASS:** matches the docs.
  - **DIVERGES:** the behaviour differs from the docs. The skill handles it
    like a TOUCHES row for the probe's unit.
  - **ERROR:** the probe could not run.

R8.5 **Log.** Append rows to `build/guide_upkeep/PROBES.md` (date · Claude Code
version · binary path · probe · outcome · finding), left uncommitted for the
owner. R3.4 parses this table.

`hooks/README.md`'s "Probe log" keeps its 2026-09-03 row and gains a pointer to
`PROBES.md` for later runs.

R8.6 **Cost and invocation.** About $0.05–0.30 per probe group. Probes run only
manually, through `probes.py` or `/guide-upkeep probes`, never from the hook.

### R9 — Wiring interface

R9.1 **Anchor IDs are opaque.** The manifest stores them, and exactly one
function resolves an ID to guide line ranges. Until the wiring spec defines
anchors, the resolver builds IDs from heading paths:
- lowercase;
- ⚠ and leading section numbers removed;
- punctuation dropped and spaces turned into hyphens;
- parent and child joined with `/`.

Examples: `skills/frontmatter-reference` and `subagents/frontmatter-reference`.
When the wiring lands, only the resolver changes, plus a one-time rename if its
IDs differ.

R9.2 **Requests to the wiring session:**
- anchor IDs must not change when a ⚠ marker is toggled, since 5 headings carry
  one today;
- they must not contain section numbers.

R9.3 **Fan-out** consumes only an index mapping anchor ID → citing file paths.
The detector report and the re-verify summary list each affected unit's
dependents. When there is no index, they say `dependents: no index`, which is
not an error. Upkeep never edits a dependent.

### R10 — Tests and documentation

R10.1 **A directory-scoped suite** in `build/guide_upkeep/`, run from inside
that directory:
`uv run --python 3.13 --with pytest python -m pytest -q`.
- Tests are offline.
- Fixtures (docs pages, `llms.txt`, the changelog) are **hand-written**: never
  copied docs text, and built to cover each edge case on purpose: a duplicate
  heading, a table under a lone `##`, a 2-character backtick span, code fences,
  and the preamble.

R10.2 **Coverage.**
- R2: splitting, keys, normalization, terms, selection.
- R3: compare, missing page, new and removed slugs, exit codes 0/1/2 (with a
  simulated network failure), changelog parsing and version order, and every
  due rule, including the shared audit clock.
- R4: the stamp mismatch and each lint rule.
- R4.4: each subcommand's write set.
- R5.4: FOUND and MISSING, and UNSURE on a failed quote.
- R8: `PROBES.md` parsing, plus probe assertions replayed against recorded
  stream fixtures (recorded from our own runs).

R10.3 **`notice.py` runs under both interpreters**:
`uv run --python 3.13 …` and `uv run --python /usr/bin/python3 …`, mirroring
`hooks/`'s dual run. Its tests check that it:
- always exits 0;
- writes only JSON to stdout;
- shows a report at most once a day;
- reports a missing `uv` or a timeout visibly.

R10.4 **The suite checks its own `.claude/` frontmatter.**
- The skill parses and sets `disable-model-invocation: true`.
- The agent has `tools: Read, Grep, Glob`, `model: sonnet` and
  `omitClaudeMd: true`.

`check_frontmatter.py` stays unchanged. Its portability rules, such as R1.6's
Codex `openai.yaml` parity for manual-only skills, do not belong on a
Claude-only skill, and leaving it alone keeps this spec off the portability
branch's file.

R10.5 **Documentation.**
- `CLAUDE.md` Commands gains the suite's command and test count (state +N
  deltas in plans), plus the `check.py` and `probes.py` invocations.
- `build/CLAUDE.md` gains a paragraph on `guide_upkeep/`.
- The skill body documents the modes.

## Sequencing and execution constraints

Stages, in order. Each is one plan. Stage 4 depends only on Stage 1.

1. **Detector**: R1–R3, R4.1–R4.3, R4.4's `init` and `stamp`, R9.1's
   resolver, and their R10 tests. That is the manifest, `blocks.py`,
   `check.py`, the stamp region and the lint. Usable through manual `uv run` as
   soon as it lands. Its first live run should list releases from 2.1.289 on as
   untriaged for every unit.
2. **Act**: R5, R6, the rest of R4.4, and R10.4. That is the skill,
   `guide-verifier` and `quotes.py`. Its first job is triaging the backlog
   since 2.1.288.
3. **Notice**: R7 and R10.3. It comes after Stage 2, so the notice points at a
   command that exists.
4. **Probes**: R8 and its R10 tests. Its prerequisite, a current PATH CLI, was
   met on 2026-10-03 (R8.2).

Each stage updates the documentation in R10.5 for what it adds.

Constraints:
- **Work in a worktree branched from `origin/main`.** Concurrent sessions
  switch and rebase the shared checkout. Check `git rev-parse main origin/main`
  first: `EnterWorktree` omits unpushed commits.
- **Before allocating a plan ID**, check `specs/plans/` on every branch
  (`git ls-tree`). IDs are allocated per branch and collided on 2026-10-03.
- **State test changes as +N deltas**, never absolute totals.
- **Never commit docs text.** Fixtures are hand-written, and quotes live only
  in session reports. `build/.scratch/` is not used.
- **Coordinate with `specs/agent-skills-portability.md`.** This spec no longer
  touches `check_frontmatter.py` (R10.4). Its decision 2 is unaffected
  (Decision 5).
- **Coordinate with the wiring brainstorm** through R9 only.

## Validation and acceptance

1. **Stage 1.**
   - `check.py --docs ~/.cache/agent-skills/cc-guide/2.1.288/docs` exits 0
     with no changed blocks, which shows the baseline round-trips.
   - The live run lists 2.1.289 or later as untriaged for every unit and
     reports changed blocks only where docs actually moved.
   - It exits 1 only if something is due: a changed block, or a batch whose
     oldest untriaged release is at least 7 days old. Otherwise it exits 0.
   - A fixture test shows that editing one `env-vars.md` row flags only the
     units whose terms match it.
2. The guide lint passes on the current guide.
3. **Stage 2.**
   - A triage of the 2.1.289+ backlog produces quote-checked rows.
   - A full `audit` of one unit produces the A/B/C report.
   - The resulting diff separates fact corrections from the owner's-call items.
   - The skill makes no commit.
4. **Stage 3.**
   - `notice.py` prints nothing on exit 0, and a single `systemMessage` on
     exit 1 or 2.
   - Both interpreter runs pass.
   - The owner sees the notice at a live session start.
5. **Stage 4.** Each probe group yields PASS or DIVERGES with recorded
   evidence on the current CLI, logged in `PROBES.md`.
6. **Every existing gate passes:**
   - `check_frontmatter.py` and `check_provenance.py`
   - `check_snippets.py skills/` (Tier 1)
   - the dependency-drift test
   - the `build/` suite
   - `sync_runtime_assets.py --check`, with no adapter change, since the new
     skill and agent live under `.claude/`

## Out of scope (deferred; logged to `specs/deferred_items.md` at plan completion)

- `specs/agent-skills-best-practices.md` (multi-vendor), and the guide's §8
  `TODO(owner)`.
- **The wiring itself:** anchors, citations, the index.
- **Editing dependent files.** Upkeep only lists them.
- **Probes for behavioural ⚠ claims** the repo does not depend on, such as the
  fork-mode and `background` defaults and the Stop-hook block cap. The owner
  declined them for now.
- **Probing the desktop app's bundled binary.**
- **The Codex counterpart guide** (`specs/codex-customization-guide.md`,
  untracked in the shared checkout and belonging to another session). The
  manifest is per guide, so a second guide could be added later.
- **Anything automatic and outward-facing**: commits, PRs, issues.

## Provenance and copyright

- **The docs are Anthropic's copyrighted text.** Copies live only in
  `~/.cache/agent-skills/cc-guide/`. The repo commits hashes, slugs, release
  labels, terms and probe outcomes.
- Verifier quotes (≤ 25 words) appear only in session reports. Proposed
  wording is the verifier's own paraphrase, an existing rule of the refresh.
- `manifest.toml`, the scripts, the skill, the agent and the hand-written
  fixtures are original work under the repo's MIT `LICENSE`.
- The verifier contract is adapted from the 2026-10-03 refresh's own prompts,
  which are this repo's work.
- `NOTICE` is unaffected: no skill is added under `skills/`.

## Sources and verification notes

- **Snapshot citations.** These line numbers are against the 2.1.288 snapshot
  in the cache:
  - `hooks.md:930`: `systemMessage` is a "Warning message shown to the user".
  - `hooks.md:1114`: SessionStart hooks run in the background in interactive
    sessions.
  - `hooks.md:1163`: SessionStart plain stdout goes to Claude's context.
  - `cli-reference.md:72,109,127,128`: `--bare`, `--no-session-persistence`,
    `--setting-sources`, `--settings`.
- **The refresh's verifier scopes, page lists and report contract** come from
  the `95978d08-e400-4983-82b5-9b30cff250d6` session's subagent transcripts
  (2026-10-03).
- **Measurements in "Measured baseline"** were taken on 2026-10-03 by this
  session, with scripts in `/tmp/ccdrift-probe/` (session-local, not
  committed):
  - the 55-page refetch;
  - the keyword replay over 2.1.220–2.1.289;
  - verifier cost, from usage counted once per API message ID and priced at the
    guide's Sonnet 5.5 list rates.
- **Memory notes:** `cc-guide-refresh`, `skill-model-pins-auto-mode`,
  `microtest-isolation-channels`.
- **The ⚠ count** is 33 markers on 32 lines, which corrects the brief's 32.
