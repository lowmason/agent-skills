# Claude Code drift automation — Design Spec

**Status: DESIGN APPROVED (2026-10-03).** The owner reviewed the merged
spec and approved it as written, including the merge-time choices neither
session's approvals had covered: the stage order, the `build/` test
collection, the fetch gate, DIVERGES staying due, discarding failed verify
quotes, and the once-a-day notice in place of `ack`.
Two sessions designed this system in parallel from the same brief. This
session's spec (`71d2422`, "define Claude Code drift automation") and the
guide-upkeep session's (`specs/claude-code-guide-upkeep.md`, `024d430`,
"design Claude Code guide upkeep", on branch
`worktree-cc-guide-upkeep-design`) were each approved section by section. A
neutral reviewer, blind to both conversations, compared them against the
brief and recommended a merge on this spec's base: only this spec delivered
the brief's decided wiring, and the other's detection model, triage, audit
and measurements fit into it. The owner then settled the points where the
two sessions had decided differently (Decisions 10–14). This document
supersedes both. It merged to `main` at `fe072a1`. The other branch is
retired: `024d430` survives as the tag `archive/cc-guide-upkeep`, pushed to
origin. Of this spec, only R1.1's anchors exist so far, added to the guide by
the conformance plan (plan 35, `18b4a71`; see R1.1); nothing else has been
implemented.

## Purpose and scope

`specs/guides/claude-code-customization-guide.md` (the guide) is the hub for
Claude Code facts; `specs/agent-skills-portability.md` already says it governs
them.
Every file whose correctness rests on a Claude Code fact that can change
between versions cites the guide section it relies on, so when a section
drifts the signal reaches every file that cites it.

The system detects and proposes. It never commits: every edit it makes to the
guide, to its own bookkeeping, or to a citing file is left uncommitted for the
owner to review. It has five parts:

1. **The wiring**: stable section IDs in the guide, a citation with a review
   stamp in every dependent file, and a lint that keeps both honest (R1, R4,
   R5).
2. **A deterministic detector** that spends no model tokens. It hashes docs
   blocks per section group and lists the changelog releases past each
   section's stamp (R2, R3, R6, R7).
3. **A trigger**: a SessionStart hook pair that runs the detector at most once
   a day in the background and shows the owner what is due (R9).
4. **A `/cc-guide` project skill** for cheap triage, scoped re-verification of
   flagged sections, review of stale citing files, and a monthly audit (R8).
5. **Live probes** for behaviour that changes before the docs say so (R10).

It watches Claude Code only; the Codex and Gemini guides beside it in
`specs/guides/` are out of scope. Tool names use `cc_guide`, which avoids the repo's two
existing uses of "drift" (`install.py`'s dependency-drift check and
`specs/superpowers-drift-spec.md`).

## Measured baseline (2026-10-03)

"Guide-upkeep session" marks a measurement made by the other session; its
scripts were session-local (`/tmp/ccdrift-probe/`).

| Fact | Evidence |
|---|---|
| The owner moved the three customization guides from `specs/` to `specs/guides/` in `79ad04f` (renames only). Earlier commits, `91474f6` and `c33bc99` included, have the Claude Code guide at `specs/claude-code-customization-guide.md` | `git diff --stat b0ee62e 79ad04f` |
| The guide has 38 sections (9 `##`, 29 `###`). Two `###` headings read "Frontmatter reference ⚠" (Skills and Subagents) | heading scan at `c33bc99`, ignoring `#` lines inside fences |
| The guide carries 33 ⚠ markers on 32 lines, 5 of them on headings, plus the legend in its header | `grep` |
| Between the July guide (`91474f6`, verified at 2.1.219) and the refresh (`c33bc99`, 2.1.288), 32 sections changed. Six did not: the Skills intro, "The description is the router", the Rules intro (empty), "Auto memory", the Running-lean intro (empty), "Scale ceremony to task size" | per-section diff keyed by (parent `##`, heading) |
| Nothing outside `specs/` references the guide | `git grep customization-guide` |
| Drift the refresh found that nothing propagated: all 7 `agents/*.md` list `Grep, Glob` beside `Bash`; `hooks/ruff-check.sh` exits 0 whenever `stop_hook_active` is set; `hooks/README.md` lines 56, 60, 64 leave `$CLAUDE_PROJECT_DIR` unquoted | file reads |
| The July pass had five claims wrong, among them two hook semantics: PostToolUse exit 2 "blocks", and `stop_hook_active` read as "near the cap" | `9f85f08` commit message |
| 2.1.289 shipped on 2026-10-03 with four deny/ask-rule fixes and no docs-page change. At least two touch guide claims: the 2.1.287 mod-approval exception (`rules.settings`) and the advice to guard @-referenced secrets with a `Read` deny rule (`hooks.pitfalls`). No release has shipped since | `changelog.md`, refetched 2026-10-03; guide-upkeep session's refetch of the mapped pages |
| 53 of the 55 snapshot pages refetched byte-identical about 6 hours later; only the changelog and the anthropic.com HTML page changed. Four pages refetched 2 hours after the snapshot were byte-identical, preamble and signed image URLs included | guide-upkeep session; this session's `diff` |
| The docs host sends no ETag, and `Last-Modified` is the serve time, so content hashing is the only change signal | guide-upkeep session, response headers |
| `llms.txt` lives at `code.claude.com/docs/llms.txt` and lists 220 `/docs/en/` pages; `/docs/en/llms.txt` is a 404 | fetch |
| `changelog.md` wraps each release in `<Update label="2.1.x" description="date">`: 410 blocks at 2.1.288 | snapshot |
| Docs pages put indented code fences inside components (140 indented fence lines on the platform prompt-caching page, 62 on `statusline.md`), and `skills.md` nests four-backtick fences. `build/fences.py` recognizes openers only at column 0 | snapshot; `build/fences.py` |
| Broad terms flag most releases. Over 2.1.220–2.1.288, `permission` appears in 71% of releases, `hook` in 57%, `skill` in 55%, `subagent` in 50%. Identifiers are rare: `PreToolUse` 10%, `disable-model-invocation` 3%, `stop_hook_active` 0%. Replaying the refresh verifiers' keyword lists over 2.1.220–2.1.289 flagged 63–78% of releases, and identifier-only matching missed prose-only notes such as 2.1.289's mod/deny fix | changelog in the 2.1.288 snapshot; guide-upkeep session's replay |
| `env-vars.md` is 555 lines with 9 headings and 381 table rows; `settings-reference.md` is 6,408 lines with 296 headings. Each feeds several groups | snapshot |
| The refresh cost $22.05 at Sonnet 5.5 list price ($2.49–$5.26 per verifier), mostly 81.6M cache-read tokens. Its six verifiers' peak contexts (312K–394K) sum to about 2.1M, close to the brief's "about 2.2M tokens", which therefore measured context size, not spend | guide-upkeep session, from the refresh's transcripts |
| The refresh's verifier prompts are recoverable: guide line ranges, primary pages, changelog keywords, and the quote-backed A/B/C report contract | `95978d08…/subagents/` transcripts |
| Four Claude Code versions were in play on this Mac. The docs and changelog head: 2.1.289. The VS Code extension: 2.1.288. The Desktop app, which runs the owner's sessions from an undocumented bundle layout (`~/Library/Application Support/Claude/claude-code/<version>/`): 2.1.286. The PATH `claude` (`~/.local/bin/claude`): 2.1.265 from 2026-09-08 until the owner updated it to 2.1.289 at 20:17; why auto-update had stopped is unknown | `claude --version`; process trees; transcripts' `version` field; the 2026-09-08 date from the guide-upkeep session |
| Hook payloads carry no Claude Code version, no settings file configures a status line, and the variable naming the running binary (`CLAUDE_CODE_EXECPATH`) is undocumented | `hooks.md:720` (common input fields); the four settings files; `env-vars.md` |
| SessionStart hooks run in the background at launch, so the owner can type at once, but Claude's first response waits for them. `timeout` is not enforced on an `async: true` command hook. Matchers: `startup`, `resume`, `clear`, `compact`, `fork` | `hooks.md:426, 1104-1114, 3692` |
| Hook output channels: SessionStart plain stdout becomes context for Claude and is never shown in the transcript; a synchronous hook's `systemMessage` is shown to the user; an async hook's `systemMessage` and `additionalContext` reach Claude on the next turn and are not shown to the user | `hooks.md:782, 930, 1163, 3703` |
| A session started from the Dock can inherit launchd's `/usr/bin:/bin:/usr/sbin:/sbin`: system Python 3.9 and no `uv` | `hooks/README.md:136-139` |
| Block-level HTML comments in CLAUDE.md are stripped before injection; nothing says the same of skill or agent bodies | `memory.md:150` |
| No general rule covers unknown keys in agent frontmatter | `sub-agents.md:230` names two ignored fields, in one context |
| Agent frontmatter already carries full-line YAML comments (`agents/explore.md`, `agents/task-reviewer.md`); no `SKILL.md` frontmatter does | file reads |
| `sync_runtime_assets.py` keeps only `name`, `description` and `tools` from agent frontmatter and copies bodies verbatim. It, `install.py` and `check_frontmatter.py` scan only the root `skills/`, `agents/` and `commands/` | the three scripts |
| On macOS, Linux and WSL, `Glob` and `Grep` are absent for an agent that also lists `Bash`; searches run through Bash and reach hooks as Bash calls. One rule covers a subagent and a session started with `--agent` | `tools-reference.md:34-35, 292-298` |
| `build/conftest.py` excludes nothing, so `cd build && pytest` also collects test files in subdirectories | `build/conftest.py` |
| The 2.1.288 snapshot (55 pages, `check/qcheck.py`, two guide copies) is preserved at `~/.cache/agent-skills/cc-guide/2.1.288/`, with `docs/llms.txt` added from a fetch two hours later; `FETCHED.txt` records both times | `diff -r` against `/tmp/ccguide-2026-10-03/` |

## Decisions and alternatives

1. **Per-file review stamps, keyed on `changed`.** Each citation records the
   guide version its file was last reviewed against. Each section records the
   release at which its content last changed. Keying on `changed` rather than
   `checked` keeps a re-verification that changes nothing from flagging every
   citer. Git-derived staleness was rejected: an unrelated edit clears a flag
   falsely, and a review that changes nothing never clears one. Report-only
   listing was rejected: a hand edit to the guide, the path the three known
   drifts took, would reach no citer.
2. **Honest bootstrap stamps.** Pre-existing citing files are stamped
   `@2.1.219`, their true last review, so the first run flags every file that
   cites one of the 32 sections the refresh changed. That backlog is the
   review the refresh skipped. Reviewing during the citation sweep was
   rejected: the flag → review → bump loop would go unexercised, and no stamp
   is honest until the whole sweep ends. Fixing the three known drifts first
   and stamping everything `@2.1.288` was rejected: most stamps would claim
   reviews that never happened.
3. **Citations are comments, not a `metadata` key.** A YAML comment inside
   frontmatter is invisible to every parser (`yaml.safe_load`, Claude Code,
   Codex, Gemini, `sync_runtime_assets.py`), and agent frontmatter already
   carries such comments. It needs no `ALLOWED_KEYS` change and cannot collide
   with the portability spec's R1.4 `metadata` blocks. The Agent Skills
   `metadata` field suits consumer-facing data such as author and source; a
   citation is a maintainer note, and agents have no documented unknown-key
   rule.
4. **A separate manifest and baseline, read by one CLI.** Owner configuration
   (`manifest.toml`, which no tool writes) is split from tool state
   (`baseline.json`), and one CLI carries every subcommand. Rejected:
   - metadata inline in the guide: bookkeeping churns the guide's diffs, and a
     section hash would have to exclude its own metadata;
   - extending the existing gates: it splits one concern across tools and
     leans on undocumented handling of unknown agent frontmatter keys;
   - one TOML that owner and tool both edit (this spec's first draft): every
     bookkeeping write would rewrite owner-curated config.
5. **Leaf blocks, selected by the guide's own terms, in six groups.** The
   detector hashes docs blocks: each heading's own text, and each table row
   separately. Sections fall into six groups, the refresh's own verifier
   scopes, and for each group the detector selects the blocks on the group's
   pages that mention a backticked term from the group's guide text. The
   groups also scope verification: one verifier per flagged group reads the
   group's shared pages once. Rejected:
   - hashing whole `page#heading` subtrees picked by hand (this spec's first
     draft): coarse on table-heavy pages, and laborious to keep mapped;
   - page hashes plus a diff cache: a change anywhere flags every dependent
     section;
   - the changelog alone: blind to docs-only edits;
   - one verifier per flagged section (this spec's first draft): sections in
     a group share pages, which each verifier would re-read.
6. **Releases key the stamps, and a new release gates the fetch.** Stamps
   compare against published releases, never an installed binary: four
   versions coexist on this Mac. Pages are refetched only when the changelog
   head moves, so a docs edit between releases is caught at the next release,
   a day or two later.
7. **Changelog terms are hints for a triage pass, never a filter.** Broad
   terms flag most releases, and identifiers miss prose-only notes. One cheap
   Sonnet pass reads every bullet of the untriaged releases, batched weekly.
8. **Trigger: a SessionStart hook pair in this repo.** A synchronous `show`
   prints a precomputed `systemMessage`, the only hook channel shown to the
   user, at most once a day. An async `refresh` recomputes it without delaying
   the session. Rejected:
   - one synchronous hook that runs the check inline (the guide-upkeep draft):
     Claude's first response waits for SessionStart hooks, so a fetch would
     delay it;
   - printing the notice from the async hook (this spec's first draft): async
     output reaches only Claude;
   - a daily launchd job: config outside the repo, and probes would need
     `claude -p` to authenticate from launchd, which is unverified;
   - a Desktop scheduled task: time-based, so a session and a notification per
     run even when nothing moved;
   - a cloud routine: a fresh clone of `origin/main`, no cache, no local
     binaries;
   - scheduled CI: adds `.github/`, and its notification is outward-facing;
   - a status line: none is configured, and the docs say nothing of the
     Desktop app, where the owner works, rendering one;
   - manual runs only: how 58 releases passed unnoticed.
9. **The skill and its verifier are project-local**, under `.claude/`.
   `commands/` installs into every project and gets a Gemini adapter, while
   `.claude/` is invisible to `sync_runtime_assets.py`, `install.py` and
   `check_frontmatter.py`. The portability spec's decision 2 rejects
   re-listing `skills/` through an in-repo link; this is a separate, repo-local
   tool. The verifier is a subagent pinned to Sonnet with read-only tools,
   because a subagent `model:` pin holds in auto mode and a skill pin does
   not.
10. **The docs cache and all run state live outside every checkout**, in
    `~/.cache/agent-skills/cc-guide/` (the owner's call). Anthropic's text
    cannot be committed by accident, it survives worktree removal, and every
    session shares one copy. The one committed state file, `baseline.json`
    (R2.1), holds no docs text: it stores block keys only as hashes (R2.3;
    owner, plan 38 decision 9, 2026-10-05).
11. **A monthly audit** (the owner's call). Every 30 days one of the six
    groups is fully re-verified whether or not drift was flagged. This catches
    claims that were wrong when written, as the July pass's five were. It goes
    beyond re-verifying only what drifted, at about $2.50–5.30 a month.
12. **Corrections land in the working tree, uncommitted** (the owner's call).
    The owner reviews a git diff, and JUDGMENT items are never applied.
    Rejected: a proposal file that someone must transcribe (this spec's first
    draft).
13. **The tool writes its bookkeeping and never commits** (the owner's call).
    `baseline` writes `baseline.json`, the guide's stamp region and citation
    stamps; `probes` appends to `PROBES.md`. The owner still chooses
    substantive versus editorial, as a flag. Rejected: printing TOML for hand
    application (this spec's first draft), since transcribing hashes is
    error-prone.
14. **Probes v1** (the owner's call): guard liveness, agent tool set, Stop-hook
    continuation, and agent model pins. Declined: skill frontmatter pins
    (deferred item 31 stays a manual watch) and the Stop-hook block cap, which
    matters only if drift #2 is resolved toward re-checking.
15. **Probes name their binary.** `--claude <path>` is required (this spec's
    first draft): with four versions coexisting, a default would silently
    probe the wrong binary. A binary older than the latest release is refused
    unless `--allow-old` is given and recorded (the guide-upkeep draft).
16. **One staged spec, one plan per stage** (Sequencing). The detector, the
    wiring, the skill, the notice and the probes share one manifest and one set
    of section IDs; designing them together avoids a schema migration later.

## Requirements

### Layout

- `build/cc_guide/` holds the tool, its configuration and its log:
  - `cli.py`, the one CLI, run as
    `uv run --python 3.13 python build/cc_guide/cli.py <subcommand>`. It finds
    the repo from its own location, never from the working directory. Its
    subcommands, named in code font below, are `lint`, `check`, `packets`,
    `quotes`, `baseline <sub>`, `probes` and `binaries`. Each one's logic lives
    in its own module (`lint.py`, `check.py`, `baseline.py`, `quotes.py`,
    `probes.py`), on shared parsers for the guide, anchors and citations
    (`guide.py`) and for docs blocks (`blocks.py`);
  - `manifest.toml` and `baseline.json` (R2), `PROBES.md` (R10) and
    `notice.sh` (R9);
  - the tests and their hand-written fixtures (R12).
- `.claude/skills/cc-guide/` and `.claude/agents/cc-guide-verifier.md` (R8).
- `.claude/settings.json` gains the hook pair (R9).
- `~/.cache/agent-skills/cc-guide/`, never inside a checkout, holds:
  - `2.1.288/`: the bootstrap snapshot, never written;
  - `latest/docs/`: the last fetch;
  - `<release>/docs/`: the snapshots `baseline rebaseline` takes;
  - `reports/<baseline-sha12>.json` (R6.8);
  - `notice.json` and its digest, `notice-shown`, `last-check.json` and the
    `lock/` directory (R9);
  - `packets/<run>/` and `probes/<run>/`.

  Page files are named by slug, with `/` replaced by `_` and platform pages
  prefixed `platform_`, as in the 2.1.288 snapshot.

### R1 — Guide anchors and stamp region

R1.1 **Anchors.** Every `##` and `###` heading in the guide is followed, on
the next line, by `<!-- cc: <id> -->`.
- Lines inside fenced code blocks (R3.1) are never headings; `hooks.patterns`
  holds `#`-prefixed lines inside fences.
- A `##` section's text runs to its first `###`. A section with an empty body
  still gets an anchor.
- IDs are two or more dot-separated segments of `[a-z0-9-]`, with no slashes;
  they are unique, and they never change when a heading's text or ⚠ marker
  does. They contain no section numbers.
- Each section belongs to exactly one group (R2.5).
- The anchors are already in the guide. The conformance plan added them with
  exactly these IDs, in this order. Its R1.2 test
  (`test_real_guide_carries_the_drift_r11_anchors` in
  `build/test_check_conformance.py`) pins the IDs and their order, and its
  lint (`build/check_conformance.py`) requires a well-formed, unique anchor
  under every heading. Stage 1 adopts them instead of adding them
  (`specs/completed/claude-code-guide-conformance.md`, R6 D1).

| Section | ID | Group |
|---|---|---|
| 1. The organizing constraint: context | `context.overview` | overview |
| 2. Choosing the right mechanism | `mechanisms.overview` | overview |
| 3. Skills (intro) | `skills.overview` | skills |
| Where skills live | `skills.locations` | skills |
| Frontmatter reference ⚠ (Skills) | `skills.frontmatter` | skills |
| The description is the router | `skills.description` | skills |
| The listing budget ⚠ | `skills.listing-budget` | skills |
| Progressive disclosure | `skills.progressive-disclosure` | skills |
| Arguments and dynamic context | `skills.arguments` | skills |
| Iterating on skills | `skills.iterating` | skills |
| 4. Slash commands | `commands.overview` | skills |
| 5. Subagents (intro) | `subagents.overview` | subagents |
| Frontmatter reference ⚠ (Subagents) | `subagents.frontmatter` | subagents |
| Scope tools to the role | `subagents.tools` | subagents |
| Route models by role | `subagents.models` | models |
| Isolation mechanics — and when delegation pays | `subagents.isolation` | subagents |
| 6. Rules (intro; empty) | `rules.overview` | rules |
| CLAUDE.md discipline | `rules.claude-md` | rules |
| Hierarchy and loading | `rules.hierarchy` | rules |
| Rules files | `rules.rules-files` | rules |
| Auto memory | `rules.auto-memory` | rules |
| Settings precedence and permission rules | `rules.settings` | rules |
| 7. Hooks (intro) | `hooks.overview` | hooks |
| Events ⚠ | `hooks.events` | hooks |
| Exit codes and JSON control | `hooks.exit-codes` | hooks |
| Handler types ⚠ | `hooks.handlers` | hooks |
| Configuration | `hooks.configuration` | hooks |
| Patterns | `hooks.patterns` | hooks |
| Pitfalls | `hooks.pitfalls` | hooks |
| 8. Running lean (intro; empty) | `lean.overview` | overview |
| Know your numbers first | `lean.measure` | overview |
| Session hygiene | `lean.session-hygiene` | overview |
| Caching: automatic, but don't fight it | `lean.caching` | models |
| Model routing | `lean.model-routing` | models |
| MCP hygiene | `lean.mcp` | overview |
| Scale ceremony to task size | `lean.ceremony` | overview |
| Guard expensive operations | `lean.expensive-ops` | overview |
| Further reading | `reading.overview` | models |

R1.2 **Stamp region.** The header's first sentence becomes a region between
`<!-- cc-guide:stamp -->` and `<!-- /cc-guide:stamp -->`, generated by
`baseline stamp` from `baseline.json`. It names the oldest `checked` and the
oldest `audited`, for example: "Checked against the Claude Code docs and
changelog through 2.1.288 on 2026-10-03; oldest full re-verification
2026-10-03, at 2.1.288." Both dates are the days the check and the audit were
done (R2.3), so the example reads "on" (owner, plan 38, 2026-10-04).
Everything outside the markers stays owner prose,
including the July/2.1.219 history. Stage 1 converts the sentence, and the
owner reviews that edit. The region sits before the first section, so stamp
updates never touch a section's text.

### R2 — Manifest and baseline

R2.1 **Two files, split by writer.**
- `manifest.toml` is configuration. The owner edits it rarely, it is read
  with stdlib `tomllib`, and its comments record why each choice was made. No
  tool writes it.
- `baseline.json` is state. Only `baseline` writes it (R7).

R2.2 **`manifest.toml` holds:**
- the guide path, `specs/guides/claude-code-customization-guide.md`, and the
  source URLs: the docs base, `llms.txt`, the changelog, and the platform base
  `platform.claude.com/docs/en/`;
- cadences: `changelog_days = 7`, `probe_days = 7`, `audit_days = 30`;
- the six groups in a fixed order. Each lists its section IDs, which must
  match R1.1's Group column, and its pages, each marked `all` or `terms`;
- optional per-section `extra_terms` and `exclude_terms`;
- exclusions, each with its reason: `whats-new/*` duplicates the changelog;
  the anthropic.com Haiku 4.5 launch post is a historical figure and its HTML
  churns; `changelog.md` is parsed (R6.6), not hashed;
- the probe registry (R10.1), empty until Stage 5.

R2.3 **`baseline.json` holds:**
- per section: `checked` (release and date) through which its changelog
  backlog and docs blocks are resolved; `changed` (release, R2.4); `audited`
  (release and date of the last audit of its group); `text_hash` (`sha256:` of
  its normalized text, anchor line excluded, whitespace collapsed). Each date
  is the day the check or audit was done, not the release's ship date: the
  bootstrap's 2026-10-03 is the refresh's day, and 2.1.288 shipped on
  2026-10-02 (owner, plan 38, 2026-10-04);
- per group: `blocks` (page → key hash → block hash) and `snapshot` (per
  page, the release whose cached snapshot holds the baselined text). A key
  hash is R3.5 step 4's hash over a block key (R3.3, R3.4), so the committed
  file holds no docs text; `check` and `rebaseline` read a key back from its
  page's snapshot when they must name a block that has left the page (owner,
  plan 38 decision 9, 2026-10-05). A block shared by two groups is stored
  under each, so resolving it in one never hides it from the other;
- the `llms.txt` slug list from the last baseline.

R2.4 **Stamp rules.**
- Versions compare as integer tuples: `2.1.288.1` sorts after `2.1.288` and
  before `2.1.289`.
- A new `changed` must be strictly greater than every review stamp among the
  section's citers. `baseline` uses the newest known release; when that would
  not exceed the highest citer stamp, it uses that stamp with a fourth
  component added or incremented.
- When a section's text no longer matches `text_hash`, the editor records one
  of two outcomes with `baseline accept`. **Substantive:** a new `changed`
  and `text_hash`, which flags every citer. **Editorial:** a new `text_hash`
  only.

R2.5 **Seed groups.** These are the refresh's six verifier scopes, recovered
from its verifier prompts. All 39 pages are in the 2.1.288 snapshot. The
`all` and `terms` marks are initial values, to be tuned in `manifest.toml`
after the first runs.

| Group | `all` pages | `terms` pages |
|---|---|---|
| overview | context-window, costs, monitoring-usage | mcp, commands, features-overview, debug-your-config, best-practices, statusline, interactive-mode, env-vars, memory, skills |
| skills | skills | commands, plugins/components, plugins/loading, claude-directory, settings-reference, env-vars, auto-mode-config, model-config |
| subagents | sub-agents | agents, workflows, agent-teams, model-config, env-vars, tools-reference, prompt-caching, settings-reference, cli-reference |
| rules | memory, settings, permissions | settings-reference, permission-modes, claude-directory, large-codebases, env-vars |
| hooks | hooks, hooks-guide | settings-reference, env-vars |
| models | prompt-caching, model-config, fast-mode, advisor, platform about-claude/pricing, platform about-claude/models/overview | platform build-with-claude/prompt-caching, platform about-claude/model-deprecations, platform models/haiku-4-5/overview, costs, env-vars, settings-reference, commands |

R2.6 **The initial baseline** is computed by `baseline init` from the 2.1.288
snapshot in `~/.cache/agent-skills/cc-guide/2.1.288/docs/`, never from live
docs, so a docs edit published after the stamp shows up as a change rather
than being absorbed. A page later mapped but missing from the snapshot stays
unbaselined, so its selected blocks report as new. Every section starts at
`checked = audited = 2.1.288 (2026-10-03)`, with `changed` per R11.1.

### R3 — Blocks (`blocks.py`)

R3.1 **Fences.** A fence opens on a line whose first non-space characters are
three or more backticks or tildes, at any indentation. It closes only on a
line holding nothing but a run of the same character at least as long as the
opener's. This is `build/fences.py`'s closing rule, extended to the indented
openers docs pages use. The guide's section splitter (R1.1) uses the same
rule.

R3.2 **Preamble.** Strip the leading "Documentation Index" blockquote: the
`>` lines at the top of each page that point to `llms.txt`. Text after it and
before the first heading becomes the `(intro)` block.

R3.3 **Headings.** Cut at every ATX heading outside code fences. A block runs
from its heading to the next heading of any level, so a parent's block holds
only its intro text. The key is the heading path, with ancestors joined by
` › `. A repeated path gets an ordinal suffix (`#2`).

R3.4 **Tables.** Each table row inside a block, apart from the header and
separator rows, becomes its own block. Its key is the heading path, then ` › `,
then the row's first cell, with an ordinal suffix when repeated. The rest of
the text stays in the heading's block.

R3.5 **Normalize, then hash.**
1. Replace each `](target)` with `]()`. A URL that moves in a docs
   restructure is cosmetic for the guide's claims.
2. Collapse runs of whitespace and strip each line.
3. Drop empty lines.
4. Hash with SHA-256 over UTF-8 and keep the first 16 hex characters.

R3.6 **Terms.** A section's terms are the backticked spans in its guide text:
- outside fenced code;
- found by pairing every backtick first and filtering by length afterwards,
  keeping 3–60 characters. Filtering inside the regex mis-pairs around
  2-character spans such as `` `if` ``;
- minus a stoplist of generic words such as `true`, `name`, `model` and
  `paths`;
- plus the section's `extra_terms`, minus its `exclude_terms`.

Matching is case-sensitive substring matching. A group's terms are the union
of its sections' terms.

R3.7 **Selection, per group.**
- On an `all` page, every block counts.
- On a `terms` page, a block counts when its key or normalized text contains
  one of the group's terms.
- A block that is selected now but absent from the baseline is *new*: the
  guide gained a claim, for example about a new setting.
- A baselined block still on the page, its text unchanged, but no longer
  selected, because the guide dropped the term, is *deselected*. That is
  informational, and the next `baseline rebaseline` drops it. A baselined
  block whose text changed is *changed* even when it is no longer selected,
  so a docs edit that drops a block's last watched term is a finding (owner,
  plan 38 final review, 2026-10-05). Only a block key that has disappeared
  from the page is *missing*. It is named by the key its page's snapshot
  holds, or by its key hash when that snapshot is gone or no longer holds it
  (R2.3); a block named by its hash names every section of the group as a
  candidate.
- A changed, missing or new block names its **candidate sections**: the
  group's sections whose terms it contains, or every section of the group when
  none match. Triage settles attribution (R8.4).

### R4 — Citations

R4.1 **Form.** One line per citing file, `cc-guide: <id> [<id> …] @<version>`.
The version is the highest `changed` among the cited sections at the file's
last review.

| File | Placement |
|---|---|
| `SKILL.md`, `agents/*.md`, `commands/*.md`, `.claude/skills/*/SKILL.md`, `.claude/agents/*.md` | `# cc-guide: …` as a YAML comment, the last line inside the frontmatter |
| `*.sh`, `*.py` | a `# cc-guide: …` line before the first line of code. Only a shebang, comments, blank lines, a PEP 723 block (never inside it) and a Python module docstring may precede it |
| Markdown without frontmatter (CLAUDE.md, READMEs) | a block-level `<!-- cc-guide: … -->` at the top |
| TOML (`build/cc_guide/conformance.toml`) | a `# cc-guide: …` line before the first key or table, preceded only by comments and blank lines (conformance R6 D2) |

Citations never go in a skill or agent body: bodies reach Codex and Gemini
verbatim and cost tokens on every load.

R4.2 **Scope.** A file qualifies when its correctness rests on a Claude Code
fact that can change between versions; naming Claude Code is not enough.
- Known clusters: `hooks/` (the guard, its tests and README, the ruff and uv
  hooks, the probe); `agents/*.md` (tools, model, effort, and the `Explore`
  shadow); `build/check_frontmatter.py` (`CONTEXT_VALUES`, the auto-mode model
  rule, `KNOWN_AGENT_TOOLS`); `commands/*.md`; skills whose frontmatter or
  text depends on Claude Code behaviour (`effort`, `context: fork`, slash
  commands, subagent dispatch, model aliases); `install.py` (install
  locations); the root `README.md` and `CLAUDE.md`; the conformance register
  `build/cc_guide/conformance.toml` (all 38 IDs, R2.8 of the conformance spec)
  and its lint `build/check_conformance.py` (`hooks.configuration`,
  `subagents.frontmatter`, `rules.rules-files`; its R3.6). The conformance plan
  landed first, so Stage 2 adds both citation lines (conformance R6 D3).
- The plan's sweep fixes the exact list, including this system's own files.
  JSON holds no comments, so `build/cc_guide/notice.sh` carries the citation
  for the settings wiring.
- Excluded: `specs/`, `runtimes/`, `review/`.

R4.3 **Coverage gaps.** A relied-upon fact that no section covers is listed in
the plan's completion notes for the owner. The owner either extends the guide
(a new section, verified like any `/cc-guide verify` run) or leaves the fact
uncovered; the guide never grows silently. Expected first gaps: `agent_type`
in PreToolUse payloads (the guard); `claude -p` mechanics (variadic
`--allowedTools`, the stdin wait); the launchd PATH for hooks; the capitalized
`Explore` shadowing rule in `check_frontmatter.py` and `agents/explore.md`.

R4.4 **Invariants with existing machinery.** None of these changes.
- `check_frontmatter.py` never sees a YAML comment, so today's
  `ALLOWED_KEYS` and the portability spec's R1.1 key sets, R1.2 `metadata`
  shape and R1.8 `--strict` are unaffected.
- `specs/` is not installed, so a citation is not a `DEPENDENCIES` edge and
  needs no `SOFT_REFERENCES` entry. Dotted, slash-free IDs cannot match the
  dependency-drift scanner's patterns (all 38, in all three comment forms,
  were run through them with no hit); that test fails if one ever does.
- `sync_runtime_assets.py --check` stays clean: adapters keep only names,
  descriptions and tools.

R4.5 **Load check.** Claude Code already loads agent frontmatter that carries
comments (`agents/explore.md`), but no `SKILL.md` carries one, and Codex and
Gemini read skills directly. Before the sweep lands, confirm that a
`SKILL.md` whose frontmatter carries a `# cc-guide:` comment still loads in
all three runtimes, run from a directory outside any repo: Claude Code lists
and invokes it, `codex debug prompt-input` lists it, and
`gemini skills list --all` shows it `[Enabled]`.

### R5 — `lint`

An offline commit gate over the working tree (`--ref <ref>` reads a commit
instead). Exit 0 when clean; exit 1 with one line per violation.
- Every heading has exactly one well-formed anchor (R1.1). The manifest's
  groups, `baseline.json`'s sections and the anchors carry the same ID set,
  each ID in exactly one group.
- Each section's normalized text matches `text_hash`. A mismatch prints the
  `baseline accept` command for each outcome (R2.4).
- The stamp region matches `baseline.json`.
- Every citation parses, cites existing IDs, sits where R4.1 allows, and
  appears once per file. The lint scans tracked files outside R4.2's excluded
  trees for lines that begin, after indentation, with `# cc-guide:` or
  `<!-- cc-guide:`; such a line outside its placement is a violation. The
  tool's own sources keep citation-shaped test data out of line-initial
  position.
- Guide quality: every `2.1.NNN` in the guide is a changelog release label;
  every table has consistent column counts; every JSON code block parses. The
  label check reads the newest cached changelog (`latest/`, else the 2.1.288
  snapshot) and is skipped with a note when there is none.

Stale citations, whose stamp is below a cited section's `changed`, print as
`STALE <file> <ids>` on stderr and do not change the exit code. A test in the
suite runs `lint` against the repo, so the suite enforces it. CLAUDE.md's
Commands section gains the invocation, to run before committing a change to
the guide or to any file carrying a citation.

### R6 — `check`

R6.1 **Inputs.** The guide, `manifest.toml`, `baseline.json`, `PROBES.md` and
the citations come from `main`'s commit via `git show` and `git grep`, never
from whatever branch the shared checkout is on. `--ref <ref>` and
`--worktree` override; the skill uses `--worktree` (R8). `--docs <dir>` runs
offline against a local directory, for tests and for R11.4.

R6.2 **Lint first.** `check` runs `lint` against the same inputs. A failure is
due immediately (R6.7).

R6.3 **Fetch gate.** Fetch `changelog.md` and `llms.txt` on every run. When
the changelog head matches the last fetch's, fetch only mapped pages missing
from `latest/docs/`; otherwise refetch every mapped page. Compare (R6.5) and
the due rules (R6.7) always run: a guide or manifest edit changes the
selection, and a changelog batch or an audit comes due by elapsed time alone.

R6.4 **Fetch.** Parallel GETs, a 30-second timeout, one retry, and a
User-Agent that names the tool and carries no personal data. Pages are written
to `~/.cache/agent-skills/cc-guide/latest/docs/`, overwriting, with the fetch
time and changelog head recorded beside them.

R6.5 **Compare.** For each group, report its changed, missing and new blocks
as findings, each with its candidate sections (R3.7), and its deselected
blocks for information.
- A mapped page absent from `llms.txt`, or returning 404, is a **missing
  page**, which is a finding, never "unchanged". Platform pages, which
  `llms.txt` does not list, are checked by fetch status only.
- `llms.txt` slugs added or removed since the baseline are listed for
  information.

R6.6 **Changelog.** Parse the `<Update label="X" description="DATE">` blocks
and their `* ` bullets, ordering versions numerically. For each section, list
the releases after its `checked`, with every bullet; term hits are marked as
hints only.

R6.7 **Due rules.**

| Item | When it is due |
|---|---|
| A changed, missing or new block | Immediately |
| A lint failure, including a `text_hash` or stamp-region mismatch | Immediately |
| The changelog batch | Once the oldest release newer than some section's `checked` is at least `changelog_days` old |
| A probe | When it is registered but has no `PROBES.md` row, or when at least `probe_days` have passed since its last row and a release has shipped since that row's version |
| A DIVERGES probe outcome | Immediately, until a later PASS row for that probe |
| An audit | When at least `audit_days` have passed since the most recent audit of any group. It targets the group with the oldest `audited` date, ties broken in manifest order. This shared clock yields one group a month |
| Stale citations | Never; reported for information |

R6.8 **Report.** Write `~/.cache/agent-skills/cc-guide/reports/<baseline-sha12>.json`,
keyed by the baseline's hash so a worktree in the middle of a re-verify never
reads `main`'s report, and print a human-readable summary. The report records:
`generated_at`; the latest release; the hashes of the manifest, baseline and
guide; per-group findings with candidate sections; untriaged releases per
section; due probes; the due audit; lint results; errors. It also lists the
**citing files** of every candidate section, from the citation index built at
the same inputs, and the stale backlog grouped by section.

R6.9 **Exit codes**, following `check_snippets.py`, so a crash or network
failure never looks clean:
- 0: nothing is due;
- 1: at least one item is due;
- 2: an error (network, parse, an invalid manifest or baseline, an
  unresolvable anchor).

R6.10 `check` never writes inside the repo. Its writes go under
`~/.cache/agent-skills/cc-guide/` only; `--hook` also writes the notice (R9).

R6.11 **Packets.** `packets --triage | --verify <ids> | --audit <group> |
--files [<paths>] --out <dir>` writes the files the skill hands to its
verifier (R8), from the same inputs as `check --worktree`.

### R7 — `baseline`

The only writer of `baseline.json`, the guide's stamp region, and citation
stamps. Every subcommand leaves its changes uncommitted. `advance` and
`audited` can move the oldest `checked` or `audited`, which the stamp region
names, so `stamp` follows them, as R8.8 orders it; a stale region is a lint
failure. A missing page (R6.5) clears only through a `manifest.toml` edit
that drops or remaps it, since `rebaseline` keeps a missing page's entries
(owner, plan 38, 2026-10-04).
- `init`: R2.6.
- `rebaseline <group> [<block keys>]`: re-hash the group's selected blocks,
  all of them or the listed keys, from `latest/`, and snapshot those pages to
  `~/.cache/agent-skills/cc-guide/<release>/docs/`. A key is listed as
  `check` prints it, so a block `check` could name only by its key hash is
  listed by that hash (R2.3).
- `advance <ids> --to <release>`: set `checked`.
- `audited <group>`: set `audited` for the group's sections to the current
  release and date, and advance their `checked` to it.
- `accept <ids> --substantive | --editorial`: record the new `text_hash`. With
  `--substantive`, also set `changed` per R2.4.
- `stamp`: regenerate the stamp region.
- `cite <file>`: after a review, set the file's citation stamp to the highest
  `changed` among its cited sections.

### R8 — The `/cc-guide` skill and its verifier

R8.1 **Files.**
- `.claude/skills/cc-guide/SKILL.md` sets `disable-model-invocation: true`:
  typable as `/cc-guide`, absent from the listing, never auto-fired. Its body
  documents the modes, and `references/` holds the packet and report formats.
- `.claude/agents/cc-guide-verifier.md` sets `model: sonnet`,
  `tools: Read, Grep, Glob` and `omitClaudeMd: true`, with a short description
  saying that only `/cc-guide` dispatches it, since every session in this repo
  lists it. Its body holds the contract: the modes, the report formats, the
  accuracy and JUDGMENT rules, and never editing a file. Without `Bash` it
  keeps Grep and Glob on macOS and stays outside the read-only guard's remit.
- Both carry citations. `check_frontmatter.py` stays unchanged (R12.4).

R8.2 **Packets are files** (R6.11), never inlined into the dispatch prompt,
where the dispatching session would pay for them as output tokens. The
verifier reads them.

R8.3 **`quotes`** reads `file<TAB>quote` rows on stdin against a named file
set and prints `FOUND file:line` or `MISSING` per row, exiting 1 on any miss.
A quote must match within a single line, the method that found 151 of 151 in
the refresh. It succeeds the snapshot's `check/qcheck.py`.

R8.4 **`/cc-guide triage`.**
1. Run `check --worktree`, then `packets --triage`: the whole guide with line
   numbers; each changed, missing or new block's current text, with a unified
   diff against its snapshot when that is cached; and every bullet of every
   untriaged release, with term hits marked. After a long absence, split it by
   release range.
2. Dispatch one `cc-guide-verifier` in triage mode, at about $0.05–0.20 a
   weekly batch.
3. **Output.**
   - Every block gets a row:
     `item | TOUCHES / NOISE / UNSURE | section | guide line | "guide quote" | "source quote" | why`.
     A NOISE row needs no guide quote, but it needs a reason.
   - A bullet gets a row only when it is TOUCHES or UNSURE.
   - Every release gets a coverage line, `release | sections touched, or none`.
4. **Completeness, checked deterministically.** An omitted block row makes the
   block UNSURE for each of its candidate sections. A release with no coverage
   line becomes UNSURE for every section whose terms its bullets hit, or an
   owner item when they hit none. Silence never counts as NOISE.
5. `quotes` re-greps every quote, guide quotes against the guide and source
   quotes against the packet. A row whose quote fails becomes UNSURE, which is
   handled as TOUCHES: triage fails safe.
6. **Resolution, in the same run.**
   - Every section with no TOUCHES or UNSURE row is advanced to the newest
     triaged release. Its group's affected blocks are rebaselined once every
     flagged section of that group is resolved.
   - Any TOUCHES or UNSURE goes to `verify` now.
   - Deferred: nothing advances, and the next triage shows it again.

R8.5 **`/cc-guide verify [<ids>]`.**
- State the count. Above 6 verifiers, ask before dispatching, or take a
  subset.
- Dispatch one verifier per group with flagged sections. Its scope: those
  sections' guide lines, their TOUCHES and UNSURE rows, the changed blocks, and
  grep over the current snapshot (`<release>/docs/`, copied from `latest/`).
  About $0.30–1 per group.
- **Report contract**, the refresh's own format plus one verdict:
  - **A.** `L<line> | claim ≤12 words | CONFIRMED / STALE / WRONG / PARTIAL / NOT FOUND / JUDGMENT | doc:line | "verbatim quote ≤25 words" | proposed wording`.
    Proposed wording appears only for STALE, WRONG and PARTIAL; it is the
    verifier's own paraphrase, never a doc sentence. Absence of evidence alone
    is NOT FOUND, never WRONG.
  - **B.** Changelog items that change a claim in scope: version, one line,
    changelog line number.
  - **C.** At most four omissions that would change existing advice.
- **Facts versus judgment.** A claim is checkable when a doc page could
  confirm or refute it: names, defaults, numbers, behaviour, precedence,
  syntax. Recommendations get JUDGMENT and never a proposed wording. When a
  judgment rests on a mechanism, the mechanism is checked and reported as
  `JUDGMENT (mechanism STALE)` with its quote; the `opusplan` bullet resting on
  cache-read prices is an example. Lines next to a `TODO(owner)` are
  report-only.

R8.6 **`/cc-guide audit [<group>]`.** With no argument, the due group (R6.7).
The verifier checks every claim in the group's sections against all its pages
and its changelog since `checked`, under the same contract. About $2.50–5.30.

R8.7 **`/cc-guide files [<paths>]`.** With no paths, the stale backlog, in
batches under the same ask-above-6 rule.
1. Each packet holds the file and its cited sections' current text, marking
   the sections changed since its stamp.
2. One verifier per file returns rows of
   `file line | statement | section | "verbatim guide quote" | consistent / contradicts / not covered`.
3. Guide quotes are re-checked against the guide at the inputs' ref.

R8.8 **Post-processing for `verify`, `audit` and `files`**, all
deterministic:
1. `quotes` re-greps every quote. A row whose quote fails is discarded and
   listed as unverified. This is the refresh's rule, and the opposite of
   triage's escalation.
2. Surviving corrections are applied **in the working tree only**: guide
   prose for STALE, WRONG and PARTIAL rows; citing-file text for
   `contradicts` rows.
3. JUDGMENT items and `not covered` rows go to an owner's-call list and are
   never applied; a `not covered` row may also be a coverage gap (R4.3).
4. Bookkeeping, through `baseline`:
   - `accept --substantive` for each section whose prose changed, which flags
     its citers;
   - `rebaseline` for the affected blocks;
   - `advance` to the newest release the run covered: the newest triaged
     release for `verify`; for an audit, `audited` instead;
   - `cite` for each reviewed file;
   - then `stamp`.
5. Run `lint` and `build/check_conformance.py`.
6. List the citing files of every section whose `changed` moved.

Nothing is committed, and quotes appear only in session reports.

When a correction resolves a conformance gap, the same working-tree change
removes the matching `[[exception]]` from `build/cc_guide/conformance.toml`, or
narrows its `artifacts`, and step 5 then runs `check_conformance.py`. This
covers Stage 3's fixes to the three known drifts (R11.5) and any later
correction. Otherwise the register's both-ways match fails the fix as a stale
waiver (conformance R6 D5).

R8.9 **`/cc-guide probes`** runs `probes` (R10).

### R9 — Trigger (`notice.sh` and `.claude/settings.json`)

R9.1 `.claude/settings.json` gains one `SessionStart` group with matcher
`startup`, so it does not fire on resume, `/clear`, compaction or a fork,
holding two command hooks:

```json
{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/build/cc_guide/notice.sh show" },
{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/build/cc_guide/notice.sh refresh", "async": true }
```

The quoting follows the guide's own pattern; the unquoted form is drift #3.

R9.2 **`show`**, synchronous, in POSIX `sh` with no Python, network or git. It
prints `~/.cache/agent-skills/cc-guide/notice.json`, a JSON object holding one
`systemMessage` that Python escaped when writing it, unless the same notice
was already shown today. `notice-shown` holds the date and the notice's
digest, which Python writes beside the notice, so a changed notice shows again
the same day. It always exits 0 and needs only `HOME` and a minimal `PATH`: a
session started from the Dock keeps `HOME` but gets launchd's `PATH`.

R9.3 **`refresh`**, async.
- It exits 0 at once when the last successful check finished under 24 hours
  ago (`last-check.json`), or when another session holds the lock (an atomic
  `mkdir` lock, broken when older than an hour).
- Otherwise it looks for `uv` on PATH, then in `~/.local/bin` and
  `/opt/homebrew/bin`, and runs `cli.py check --hook` through
  `uv run --python 3.13` under an overall time budget, since `timeout` is not
  enforced on async hooks. It locates `cli.py` from its own directory, never
  from the hook's working directory: a relative path would repeat drift #3's
  class of bug. When `uv` is missing, it writes a fixed error notice itself.
  It exits 0.
- `check --hook` writes `notice.json` and `last-check.json` and prints
  nothing: an async hook's output would reach only Claude.

R9.4 **The notice.**
- Exit 0: the notice is empty, and `show` prints nothing.
- Exit 1: one line under 300 characters naming every due item, for example
  `cc-guide · 2 docs blocks changed (hooks.events, rules.settings) · 9 releases untriaged (oldest 8 d) · probes due 2 · audit due: hooks → /cc-guide`.
- Exit 2, no `uv`, or three failed checks in a row: an error line with the age
  of the last good check. A failure is never silent.
- The stale backlog is not part of the notice; the lint and the report carry
  it.
- Because `check --hook` reads `main` (R6.1), the notice keeps naming work the
  skill has resolved until the owner commits the bookkeeping it left in the
  working tree (Decision 13).

R9.5 It fires only in this repo (the main checkout and its worktrees) and
only in Claude Code. The settings change is persistent configuration: the
owner confirms it before it is committed.

### R10 — `probes` and `PROBES.md`

R10.1 **The registry is in `manifest.toml`.** Each probe has an ID, the
sections it backs, and optional files. Stage 5 registers the four below.

R10.2 **The v1 probes.**

| Probe | Mechanism | Asserts | Backs |
|---|---|---|---|
| `guard-liveness` | Wraps `hooks/probe-readonly-guard.sh`, which gains a `CLAUDE_BIN` override, run from a scratch git repo. Needs user settings, since the guard is installed globally | its three checks pass | files `hooks/readonly-agent-guard.py` and `hooks/README.md`; no section yet (R4.3) |
| `agent-tools` | A scratch agent with `tools: Read, Grep, Glob, Bash` and `omitClaudeMd: true`, run via `--agent`, plus a control agent without `Bash`; reads the init event's tool list. `--agent` stands in for subagent dispatch, since the docs state one rule for both (`tools-reference.md:298`) | on macOS, Linux and WSL: neither Grep nor Glob with Bash, both without. A control that lists neither is ERROR | `subagents.tools` |
| `stop-continuation` | A scratch Stop hook, registered through the scratch project's settings or `--settings` (whichever the first recorded run proves loads), logs `stop_hook_active` and blocks on its first two calls | the log reads `false, true, true`; an empty log is ERROR | `hooks.exit-codes`, `hooks.patterns` |
| `agent-model-pins` | The production path: a parent `claude -p` session in auto mode dispatches `Explore` (through `agents/explore.md` shadowing the built-in), `test-runner` and `code-reviewer` with the Agent tool | Explore and test-runner are served Haiku; code-reviewer's `effort: xhigh` holds | `subagents.frontmatter`, `subagents.models`; files `agents/explore.md`, `agents/test-runner.md`, `agents/code-reviewer.md` |

R10.3 **Binary.** `--claude <path>` is required. `binaries` lists candidates
with their versions: each `claude` on PATH with its symlink target, and the
Desktop app's bundled binaries, labelled as observed app layout, not
documented. Each run records `--version`. A result from a binary older than
the newest changelog label is refused unless `--allow-old` is given, and the
log row records the flag. The PATH CLI stalled at 2.1.265 from 2026-09-08 to
2026-10-03; the refusal catches a repeat.

R10.4 **Isolation.**
- Each run uses a fresh `mktemp -d` directory outside any repo, never the bare
  `/tmp` root. A repo cwd leaks CLAUDE.md and git status into every subagent
  (memory note `microtest-isolation-channels`, Channel 5).
- Only the setting sources a probe needs load: `user` where it tests the
  owner's installed setup (`guard-liveness`, `agent-model-pins`), `project`
  where a fixture lives in the temp directory. This repo's settings and hook
  never load.
- The permission mode is pinned through `--settings`, chosen per probe and
  recorded, with the probe's tools pre-allowed.
- `--model sonnet` at low effort, except where that would mask what the probe
  observes; `agent-model-pins` leaves the agents' own pins in force.
- A bounded `--max-turns`; `--no-session-persistence`; the prompt first, with
  stdin from `/dev/null`. `--bare` is used only where the probe's own
  mechanism survives it, since it skips hooks, skills, subagents and plugins.

R10.5 **Assertions.**
- Assert on raw `--output-format stream-json` events. Fall back to the probe
  session's transcript (`message.model`, `effort`) only for fields the stream
  lacks.
- Never assert on the model's prose.
- Record one real stream per probe before writing its assertion, as the guard
  probe did.
- Outcomes: **PASS** matches the guide. **DIVERGES** means the behaviour
  differs; it is due (R6.7) and handled like a TOUCHES row for the probe's
  sections and files. **ERROR** means the mechanism never fired or the run
  broke; it is never a pass.

R10.6 **Running and logging.** `probes` runs the due probes; `--only <id>`
and `--force` override. Each result appends a row to
`build/cc_guide/PROBES.md` (date, Claude Code version, binary path with `~`
for the home directory, probe, outcome, finding, and `--allow-old` when used),
left uncommitted. Raw streams stay under
`~/.cache/agent-skills/cc-guide/probes/`. `hooks/README.md`'s Probe log keeps
its 2026-09-03 row and gains a pointer to `PROBES.md`.

R10.7 **Cost and invocation.** About $0.05–0.30 a probe. Probes run only
manually, through `probes` or `/cc-guide probes`, never from the hook.

### R11 — Bootstrap and first run

R11.1 **`changed` derivation.** `changed = 2.1.288` for the 32 sections whose
text differs between `91474f6` and `c33bc99`, and `2.1.219` for the other 6.
Both commits are read at the guide's path then,
`specs/claude-code-customization-guide.md`. Sections align by (parent `##`,
heading), never heading text alone, so the two "Frontmatter reference ⚠"
sections stay distinct.

R11.2 **Seed manifest.** The groups' pages and marks come from R2.5; the owner
reviews `manifest.toml` before it is committed.

R11.3 **Citation sweep.** Tag every pre-existing qualifying file (R4.2)
`@2.1.219`, and record the coverage gaps (R4.3). Files this work creates are
written against the current guide, so they take the highest `changed` among
their cited sections. The load check (R4.5) runs before the sweep lands. The
conformance register and lint (R4.2) were written against the guide at 2.1.288,
so the sweep stamps them `@2.1.288`, not `@2.1.219` (conformance R6 D3).

R11.4 **First runs.**
- `check --docs ~/.cache/agent-skills/cc-guide/2.1.288/docs` reports no
  changed, missing or new blocks, which shows the baseline round-trips.
- The live run lists 2.1.289 and later as untriaged for every section, and
  reports changed blocks only where the docs actually moved.
- The stale backlog includes `agents/*.md`, `hooks/ruff-check.sh` and
  `hooks/README.md`.

R11.5 **First jobs.**
- Triage the backlog since 2.1.288. 2.1.289's deny/ask-rule notes should come
  back TOUCHES for `rules.settings` and `hooks.pitfalls`.
- The first `files` batch is the three known drifts. The reviewer starts from
  these considerations:
  - **#1, `Grep, Glob` beside `Bash` in all 7 agents.** In Claude Code on
    macOS they are inert. The Gemini adapters map them to `grep_search` and
    `glob`, which work there, so deleting them from the canonical files
    regresses Gemini. Searches already run through Bash, so the read-only
    guard must keep allowing `find` and `grep`. Agent bodies may tell agents
    to use Grep or Glob. The owner decides.
  - **#2, `hooks/ruff-check.sh`.** The guide's Pattern 3 presents both
    behaviours as valid: exit 0 whenever `stop_hook_active` is set (one attempt
    per turn, the fix never re-checked), or re-run the check and block while it
    still fails (bounded by the 8-block cap). The owner chooses, and the
    script's comment states the choice.
  - **#3, `hooks/README.md` lines 56, 60, 64.** Quote `$CLAUDE_PROJECT_DIR`
    as the guide's Pattern 1 does.
  - Fixing #1 or #3 also removes or narrows the register exception that tracks
    it, in the same change (R8.8; conformance R6 D5).

R11.6 Later `files` batches clear the rest of the backlog. It tracks itself,
through the lint's `STALE` lines and the report, so plan completion logs one
deferred item pointing at it rather than one per file.

### R12 — Tests and documentation

R12.1 **A suite in `build/cc_guide/`**, run from inside that directory:
`uv run --python 3.13 --with pytest python -m pytest -q`.
- `cd build && pytest` collects it too, so the build-directory count rises by
  the same +N. Module and test basenames therefore stay unique across
  `build/` (bare imports, no `__init__.py`), and the modules import nothing
  from `build/`, so the suite runs from either directory.
- Tests are offline. Fixtures (docs pages, `llms.txt`, a changelog) are
  hand-written, never copied docs text, and cover each edge case on purpose:
  a duplicate heading, a table under a lone `##`, a 2-character backtick
  span, indented and nested fences, and the preamble.

R12.2 **Coverage.**
- R1: anchors, IDs, groups, and section splitting, including fenced `#`
  lines and both "Frontmatter reference ⚠" sections.
- R2 and R7: version ordering with four components, and each `baseline`
  subcommand's write set.
- R3: fences, splitting, keys, normalization, terms, selection, candidate
  sections.
- R4 and R5: citation parsing in all three comment forms, stale computation,
  and every lint rule, including the stamp region, the guide-quality checks
  and citation placement.
- R6: compare, a missing page, added and removed slugs, changelog parsing and
  version order, every due rule including the shared audit clock, the fetch
  gate, and exit codes 0/1/2 with a simulated network failure.
- R8: `quotes` FOUND and MISSING; triage completeness; UNSURE on a failed
  triage quote; discard on a failed verify quote.
- R9: the notice's content for each outcome.

R12.3 **Acceptance fixtures.**
- **Replay.** Rebuild the guide at `91474f6` and `c33bc99` from git (our text,
  at its pre-move path), derive `changed` as R11.1 does, and run against fixture citers stamped
  `@2.1.219`. A file citing `subagents.tools` and a file citing
  `hooks.patterns` must be flagged; a control citing `skills.description` must
  not. Skip with a reason when the history is unavailable (a shallow clone).
- **Rows.** Editing one row of an `env-vars.md`-style fixture flags only the
  groups whose terms match it.

R12.4 **Repo tests.** `lint` passes on the repo. A `SKILL.md` carrying a
citation passes `check_frontmatter.py`. The suite checks its own `.claude/`
frontmatter: the skill sets `disable-model-invocation: true`, and the agent
sets `tools: Read, Grep, Glob`, `model: sonnet` and `omitClaudeMd: true`.
`check_frontmatter.py`, the dependency-drift test and
`sync_runtime_assets.py --check` stay unchanged.

R12.5 **`notice.sh show`** is tested under
`env -i HOME=<tmpdir> PATH=/usr/bin:/bin`, with a fixture notice under that
`HOME`. It must print the notice, print nothing on a second run the same day,
print a changed notice again, print only JSON, and always exit 0. A run that
prints nothing at all fails, so a missing notice cannot pass as a quiet day.

R12.6 **Probe assertions** are replayed against streams recorded from our own
probe runs.

R12.7 **Documentation.**
- CLAUDE.md's Commands section gains the suite's command and the `lint`,
  `check` and `probes` invocations, with no test count. Plans state the
  suite's count, and the build directory's, as +N deltas
  (owner, plan 38, 2026-10-04).
- `build/CLAUDE.md` gains a paragraph on `cc_guide/`.
- The CLAUDE.md lines a stage adds stay under the `claude-md-size` check's
  200-line limit; when they would not, the stage trims CLAUDE.md elsewhere.
  Stage 1's rewrite removed the `claude-md-size` exception, so no ceiling
  remains to raise (owner, plan 38, 2026-10-04; replaces conformance R6 D4's
  ceiling rule).
- The skill body documents its modes.

## Sequencing and execution constraints

Five stages, in order; each is one plan.

1. **Detector.** R1, R2, R3, R5 apart from its citation rules, R6 apart from
   R6.8's citing-file lists, R6.10's `--hook` and R6.11's `packets`, and every
   `baseline` subcommand but `cite`: `init`, `rebaseline`, `advance`,
   `audited`, `accept` and `stamp`, with their tests. Usable through `uv run`
   as soon as it lands. R1.1's anchors are already in the guide, so Stage 1
   adopts them (conformance R6 D1). Until Stage 3's verifier exists, the owner
   runs `rebaseline`, `advance` and `audited` by hand after a manual review,
   in R8.8's order, so Stage 1's `check` can reach exit 0 on its own. Stage 1
   opens by rewriting the root CLAUDE.md under the `claude-md-size` check's
   200-line limit, removing the register's `claude-md-size` and
   `claude-md-fast-changing-details` exceptions in the same change
   (owner, plan 38, 2026-10-04).
2. **Wiring.** R4, R5's citation rules, R6.8's citing-file lists,
   `baseline cite`, and R11.3, with their tests. It follows the detector
   because citation stamps and the lint's stale check compare against each
   section's `changed`, which the baseline holds.
3. **Act.** R8 apart from `/cc-guide probes`, R6.11's `packets`, `quotes`,
   and R11.5. Stage 1 carries R7 but `cite`, which Stage 2 adds, and
   `packets` moved here because its formats live in R8
   (owner, plan 38, 2026-10-04). Its first jobs are triaging the backlog
   since 2.1.288 and the first `files` batch.
4. **Notice.** R9, R6.10's `check --hook`, which writes R9's notice, and
   R12.5 (owner, plan 38, 2026-10-04). It comes after Stage 3, so the notice
   points at a skill that exists.
5. **Probes.** R10, R12.6 and `/cc-guide probes`. It needs only Stage 1's
   manifest and due rules, so the owner may run it earlier; `/cc-guide probes`
   then lands with Stage 3.

Each stage updates the documentation in R12.7 for what it adds.

Constraints:
- **Base.** This spec was written on `docs/cc-drift-spec`, branched from
  `main` at `b0ee62e`, and merged to `main` at `fe072a1`; that branch is gone.
- **Guide location.** The guide is at `specs/guides/` from `79ad04f` on;
  history before that has it at `specs/claude-code-customization-guide.md`
  (R11.1, R12.3).
- **Work in a worktree.** Check `git rev-parse main origin/main` first:
  `EnterWorktree` branches from `origin/main` and omits unpushed commits, and
  concurrent sessions switch and rebase the shared checkout. Stage 2's sweep
  also edits frontmatter in skills the executing session loads.
- **Portability spec coupling.** Its R1.4 adds `metadata` blocks to the 13
  superpowers skills' frontmatter, where Stage 2 adds a comment line; whichever
  branch merges second reconciles both in that merge. When a script gains a PEP
  723 header (its R3), the citation goes below the block.
  `check_frontmatter.py` is not touched.
- **JAX branch.** `codex/jax-deep-learning-skills` has merged to `main`
  (PR #20, `110bd99`), and so has `codex/recommend-causal-design`
  (`c3ff265`). No merge coordination remains: their skills that rest on
  Claude Code facts get citations in Stage 2's sweep like any other skill.
- **Plan IDs.** Check `specs/plans/` on every branch (`git ls-tree`) before
  allocating one; IDs are allocated per branch and have collided. On
  2026-10-04 no sibling branch existed and the next free ID was 38.
- **Test counts** are stated as +N deltas, never absolute totals.
- **Never commit docs text.** Caches, reports, packets and probe streams live
  under `~/.cache/agent-skills/cc-guide/`, fixtures are hand-written, and quotes
  appear only in session reports.
- **Nothing outward-facing.** Nothing commits, pushes or posts.
- **The superseded spec.** `specs/claude-code-guide-upkeep.md` (`024d430`) is
  superseded by this one. Its branch, `worktree-cc-guide-upkeep-design`, and
  its worktree are retired; the commit survives as the tag
  `archive/cc-guide-upkeep`, pushed to origin.

## Validation and acceptance

1. **Stage 1.**
   - The round trip (R11.4) reports no changed, missing or new blocks.
   - The live run lists 2.1.289 and later as untriaged and reports changed
     blocks only where docs moved. It exits 1 only when something is due.
   - The owner reviews the first live report's block selection once and tunes
     the `all` and `terms` marks.
   - The row fixture (R12.3) passes, and the lint passes on the converted
     guide.
   - The bookkeeping clears what it resolves: a fixture run with a changed
     block, untriaged releases and a due audit reaches exit 0 under
     `check --worktree` after `rebaseline`, `advance`, `audited` and `stamp`,
     run in R8.8's order. Each subcommand's write set is tested, and none
     commits (owner, plan 38, 2026-10-04).
   - The root CLAUDE.md is under 200 lines, the register's `claude-md-size`
     and `claude-md-fast-changing-details` exceptions are gone,
     `check_conformance.py` passes, and no test count remains in CLAUDE.md or
     `build/CLAUDE.md` (owner, plan 38, 2026-10-04).
2. **Stage 2.**
   - The load check (R4.5) passes in all three runtimes.
   - The replay test (R12.3) flags exactly its expected fixture files.
   - The stale backlog includes the three known drift files, and the coverage
     gaps are listed for the owner.
3. **Stage 3.**
   - Triaging the backlog since 2.1.288 produces quote-checked rows.
   - One `audit` produces the A/B/C report.
   - The first `files` batch handles the three known drifts: the owner's
     decisions on #1 and #2 are recorded, the fixes are applied, and those files
     leave the backlog.
   - The resulting diff separates fact corrections from owner's-call items,
     and nothing is committed.
4. **Stage 4.**
   - `show` prints nothing on exit 0 and a single `systemMessage` on exit 1 or
     2, and passes R12.5 in its launchd-like environment.
   - The owner sees the notice at a live session start, at most once a day.
5. **Stage 5.**
   - Each probe yields PASS or DIVERGES with recorded evidence on an
     owner-chosen binary, logged in `PROBES.md`.
   - A deliberately broken setup yields ERROR.
6. **Every existing gate passes:** `check_frontmatter.py`,
   `check_provenance.py`, `check_snippets.py skills/` (Tier 1), the
   dependency-drift test, the `build/` suite, `sync_runtime_assets.py
   --check` with no adapter change, and `check_conformance.py`
   (owner, plan 38, 2026-10-04).

## Out of scope (deferred; logged to `specs/deferred_items.md` at plan completion)

- Probes the owner declined for now: skill frontmatter pins (deferred item 31
  stays a manual watch); the Stop-hook block cap, which matters only if drift
  #2 is resolved toward re-checking; behavioural ⚠ claims the repo does not
  depend on, such as the fork-mode and `background` defaults.
- Line-level citations, and anchors for individual rows of the guide's tables.
- The Codex and Gemini customization guides in `specs/guides/`. The manifest
  is per guide, so a second guide could be added later with its own sources.
- The multi-vendor best-practices spec (retired to
  `specs/completed/agent-skills-best-practices.md` in `79ad04f`), and the
  guide's §8 `TODO(owner)`.
- Anything automatic and outward-facing (commits, PRs, issues), and CI, which
  the repo does not have.
- Widening `check_frontmatter.py` to `.claude/skills` and `.claude/agents`:
  its portability rules, such as the portability spec's R1.6 invocation parity
  with Codex, do not fit a Claude-only skill.

## Provenance and copyright

- The docs are Anthropic's copyrighted text. Copies live only in
  `~/.cache/agent-skills/cc-guide/`. The repo commits hashes, slugs, release
  labels, terms and probe outcomes. Block keys, which are docs headings and
  table first cells, are committed only as hashes from 2026-10-05; the
  history before that, `606fcc5` through `add1995`, holds them as text (R2.3;
  owner, plan 38 decision 9, 2026-10-05).
- Verifier quotes of at most 25 words appear only in session reports. Proposed
  wording is the verifier's own paraphrase, an existing rule of the refresh.
- `manifest.toml`, the scripts, the skill, the agent and the hand-written
  fixtures are original work under the repo's MIT `LICENSE`. The verifier
  contract is adapted from the 2026-10-03 refresh's own prompts, and this
  design merges two of the repo's own specs (`71d2422`, `024d430`); all of it
  is this repo's work.
- `NOTICE` is unaffected: no skill is added under `skills/`.

## Sources and verification notes

- The guide at `c33bc99` (identical at `b0ee62e`, both at
  `specs/claude-code-customization-guide.md`; moved unchanged to
  `specs/guides/` in `79ad04f`) is the hub; `91474f6` is its July version. `9f85f08`'s message records the refresh: every changed fact
  traced to a verbatim doc quote, 151 of 151 re-grepped, five July claims
  corrected.
- `specs/agent-skills-portability.md` at `b0ee62e` supplies R1.1, R1.2, R1.4,
  R1.6, R1.8 and R3 as cited above.
- `specs/claude-code-guide-upkeep.md` at `024d430` (tag
  `archive/cc-guide-upkeep`) supplies the block model,
  triage, the audit, the verifier contract, the due rules, the probe
  conventions, and the measurements marked as the guide-upkeep session's.
- Line references are to the snapshot under
  `~/.cache/agent-skills/cc-guide/2.1.288/docs/`, re-read for this merge:
  - `hooks.md:426, 3692` (`timeout` unenforced on async hooks), `720`
    (common input fields), `782, 1163` (SessionStart stdout to Claude), `930`
    (`systemMessage` shown to the user; stdout never in the transcript),
    `1104-1114` (matchers; background run; the first response waits), `3703`
    (async output to Claude only);
  - `memory.md:150`; `tools-reference.md:34-35, 292-298`; `sub-agents.md:230`;
  - `statusline.md:44` (a status line is set in user or project settings) and
    `202` (its `version` field);
  - `cli-reference.md:72, 109, 127, 128` (`--bare`,
    `--no-session-persistence`, `--setting-sources`, `--settings`);
  - `desktop-scheduled-tasks.md` (the scheduling comparison) and
    `routines.md` (environments and network access), for Decision 8.
- `changelog.md`, refetched 2026-10-03: the 2.1.289 block and no later
  release.
- `desktop.md` and `env-vars.md`, fetched 2026-10-03 at 19:44: neither
  documents `CLAUDE_CODE_EXECPATH` or a status line in the Desktop app.
- `hooks/probe-readonly-guard.sh` and `hooks/README.md` (its "Probe log", and
  lines 136-139) supply the probe mechanics and the launchd PATH this design
  reuses.
- The refresh's verifier scopes, page lists and report contract come from the
  `95978d08-e400-4983-82b5-9b30cff250d6` session's subagent transcripts.
- Memory notes: `cc-guide-refresh`, `skill-model-pins-auto-mode`,
  `microtest-isolation-channels`.
