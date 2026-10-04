# Claude Code drift automation — Design Spec

**Status: DESIGN APPROVED (2026-10-03); written spec awaiting review.**
The owner approved five design sections, and the decisions recorded below, in
a brainstorming pass. This document is the handoff for implementation
planning. Nothing here
has been implemented. A peer session ("Drift automation for Claude Code
guide", worktree branch `worktree-cc-guide-upkeep-design`) was designing the
same system at the same time. By the owner's choice the two designs were kept
independent, and reconciling them is the owner's call.

## Purpose and scope

`specs/claude-code-customization-guide.md` (the guide) is the hub for Claude
Code facts; `specs/agent-skills-portability.md` already says it governs them.
Every file whose correctness rests on a Claude Code fact that can change
between versions cites the guide section it relies on. When a section
drifts, the signal reaches every file that cites it.

The system detects and proposes. It never edits: changes to the guide or to
any citing file stay human-reviewed. It has four parts:

1. **Anchors, a manifest, and citations.** Stable section IDs in the guide; a
   committed manifest of each section's doc sources, changelog keywords,
   stamps, and hashes; one citation line per citing file (R1, R2).
2. **A deterministic lint and detector**, `build/cc_drift.py`, stdlib only
   (R3, R4).
3. **Live probes** for behaviour that drifts before the docs say so (R5).
4. **A trigger and a verify step.** A SessionStart hook pair that notices a
   new release, and a manual `/cc-verify` skill that re-verifies only what
   drifted (R6, R7).

It watches Claude Code only; the Codex and Gemini guides that landed in
`b0ee62e` are out of scope.

## Measured baseline (2026-10-03)

| Fact | Evidence |
|---|---|
| The guide has 38 sections (9 `##`, 29 `###`). Two `###` headings read "Frontmatter reference ⚠" (Skills and Subagents) | heading scan at `c33bc99`, ignoring `#` lines inside fences |
| Between the July guide (`91474f6`, verified at 2.1.219) and the refresh (`c33bc99`, 2.1.288), 32 sections changed. Six did not: the Skills intro, "The description is the router", the Rules intro (empty), "Auto memory", the Running-lean intro (empty), "Scale ceremony to task size" | per-section diff keyed by (parent `##`, heading) |
| Nothing outside `specs/` references the guide | `grep -rn customization-guide` |
| Drift the refresh found that nothing propagated: all 7 `agents/*.md` list `Grep, Glob` beside `Bash`; `hooks/ruff-check.sh` exits 0 whenever `stop_hook_active` is set; `hooks/README.md` lines 56, 60, 64 leave `$CLAUDE_PROJECT_DIR` unquoted | file reads |
| The July pass had five claims wrong, among them two hook semantics: PostToolUse exit 2 "blocks", and `stop_hook_active` read as "near the cap" | `9f85f08` commit message |
| Three versions are in play. The docs and changelog head is 2.1.288. The Desktop app's bundled binary (`~/Library/Application Support/Claude/claude-code/2.1.286/…`) runs the owner's sessions. The terminal `claude` (`~/.local/bin/claude` → `versions/2.1.265`) is what `claude -p` reaches | `changelog.md`; this session's process tree; `claude --version` |
| Hook payloads carry no Claude Code version; no settings file configures a status line; the variable naming the running binary (`CLAUDE_CODE_EXECPATH`) is undocumented | `hooks.md` common input fields; the four settings files; `env-vars.md` |
| A session started from the Dock can inherit launchd's `/usr/bin:/bin:/usr/sbin:/sbin`: system Python 3.9, no `uv` | `hooks/README.md:136-139` |
| Block-level HTML comments in CLAUDE.md are stripped before injection. Nothing says the same of skill or agent bodies | `memory.md:150` |
| No general rule covers unknown keys in agent frontmatter | `sub-agents.md:230` names two ignored fields, in one context |
| `sync_runtime_assets.py` keeps only `name`, `description`, and `tools` from agent frontmatter and copies bodies verbatim into the Codex and Gemini adapters | `build/sync_runtime_assets.py` |
| On macOS, Linux, and WSL, `Glob` and `Grep` are absent for an agent that also lists `Bash`; searches run through Bash and reach hooks as Bash calls | `tools-reference.md:34-35, 292-298` |
| `changelog.md` wraps each release in `<Update label="2.1.x" description="date">`; 410 blocks at 2.1.288 | snapshot |
| The docs index is `code.claude.com/docs/llms.txt`; `/docs/en/llms.txt` returns 404 | fetch |
| Four pages re-fetched two hours after the snapshot were byte-identical to it, doc-index preamble and signed image URLs included | `diff` against the snapshot |
| SessionStart hooks run in the background at launch, but Claude's first response waits for them. An `async: true` command hook delivers its output on the next turn and has no enforced timeout. Matchers: `startup`, `resume`, `clear`, `compact`, `fork` | `hooks.md`: SessionStart; Run hooks in the background |
| The refresh's docs snapshot (54 Markdown pages, one HTML page, `qcheck.py`) is preserved, gitignored, at `build/.scratch/cc-docs/2026-10-03/`, with `llms.txt` added from a later fetch; `FETCHED.txt` records both times | byte-identical copy of `/tmp/ccguide-2026-10-03/` |

## Decisions and alternatives

1. **Per-file review stamps, keyed on `changed`.** Each citation records the
   guide version its file was last reviewed against; each section records the
   release at which its content last changed. Keying on `changed` rather than
   `checked` keeps a re-verification that changes nothing from flagging every
   citer. Git-derived staleness was rejected: an unrelated edit clears a flag
   falsely, and a review that changes nothing never clears one. Report-only
   listing was rejected: a hand edit to the guide, the path the three known
   drifts took, would reach no citer.
2. **Honest bootstrap stamps.** Pre-existing citing files are stamped
   `@2.1.219`, their true last review, so the first run flags every file that
   cites one of the
   32 sections the refresh changed. That backlog is the review the refresh
   skipped. Reviewing during the citation sweep was rejected: the
   flag → review → bump loop would go unexercised until real drift arrived,
   and no stamp is honest until the whole sweep ends. Fixing the three known
   drifts first and stamping everything `@2.1.288` was rejected: most stamps
   would claim reviews that never happened.
3. **A separate manifest plus one CLI.** Metadata inline in the guide was
   rejected: bookkeeping churns the guide's diffs, and a section hash would
   have to exclude its own metadata. Extending the existing gates was
   rejected: it splits one concern across tools and leans on undocumented
   handling of unknown agent frontmatter keys.
4. **Citations are comments, not a `metadata` key.** A YAML comment inside
   frontmatter is invisible to every parser (`yaml.safe_load`, Claude Code,
   Codex, Gemini, `sync_runtime_assets.py`). It needs no `ALLOWED_KEYS`
   change and cannot collide with the portability spec's R1.4 `metadata`
   blocks. The Agent Skills `metadata` field suits consumer-facing data
   (author, source); a citation is a maintainer note, and agents have no
   documented unknown-key rule.
5. **Version-gated detection.** Nothing runs unless a version moved: the
   changelog head gates the docs and changelog scan, and the probed binary's
   version gates each probe. Docs edited between releases are caught at the
   next release's run, a day or two later at the current release rate.
6. **Trigger: a SessionStart hook pair in this repo.** Rejected: a daily
   launchd job (config outside the repo; probes would need `claude -p` to
   authenticate from launchd, unverified); a Desktop scheduled task
   (time-based, so a session and a notification per run even when nothing
   moved); a cloud routine (a fresh clone of `origin/main`, no docs cache, no
   local binaries, network allowlist unverified); a status-line nudge (none
   configured, and the docs say nothing of the Desktop app rendering one);
   manual runs only (how 58 releases passed unnoticed).
7. **Probes v1: guard liveness, agent tool set, Stop-hook continuation.** An
   effort-pin probe was offered and not chosen; deferred item 31 stays a
   manual watch.
8. **The tool never writes a committed file.** It writes gitignored caches,
   state, and reports, and prints manifest and citation changes for a human
   to apply.
9. **`probe --claude <path>` is required.** With three versions in play, a
   default would silently probe the wrong binary.
10. **The verify step is project-local** (`.claude/skills/`,
    `.claude/agents/`). `commands/` installs into every project and gets a
    Gemini adapter.

## Requirements

### R1 — Guide anchors and manifest

R1.1 **Anchors.** Every `##` and `###` heading in the guide is followed, on
the next line, by `<!-- cc: <id> -->`.
- Lines inside fenced code blocks are never headings; `hooks.patterns` holds
  `#`-prefixed lines inside fences.
- A `##` section's text runs to its first `###`. A section with an empty body
  still gets an anchor.
- IDs are two or more dot-separated segments of `[a-z0-9-]`, with no slashes;
  they are unique and never change when a heading's text does.

| Section | ID |
|---|---|
| 1. The organizing constraint: context | `context.overview` |
| 2. Choosing the right mechanism | `mechanisms.overview` |
| 3. Skills (intro) | `skills.overview` |
| Where skills live | `skills.locations` |
| Frontmatter reference ⚠ (Skills) | `skills.frontmatter` |
| The description is the router | `skills.description` |
| The listing budget ⚠ | `skills.listing-budget` |
| Progressive disclosure | `skills.progressive-disclosure` |
| Arguments and dynamic context | `skills.arguments` |
| Iterating on skills | `skills.iterating` |
| 4. Slash commands | `commands.overview` |
| 5. Subagents (intro) | `subagents.overview` |
| Frontmatter reference ⚠ (Subagents) | `subagents.frontmatter` |
| Scope tools to the role | `subagents.tools` |
| Route models by role | `subagents.models` |
| Isolation mechanics — and when delegation pays | `subagents.isolation` |
| 6. Rules (intro; empty) | `rules.overview` |
| CLAUDE.md discipline | `rules.claude-md` |
| Hierarchy and loading | `rules.hierarchy` |
| Rules files | `rules.rules-files` |
| Auto memory | `rules.auto-memory` |
| Settings precedence and permission rules | `rules.settings` |
| 7. Hooks (intro) | `hooks.overview` |
| Events ⚠ | `hooks.events` |
| Exit codes and JSON control | `hooks.exit-codes` |
| Handler types ⚠ | `hooks.handlers` |
| Configuration | `hooks.configuration` |
| Patterns | `hooks.patterns` |
| Pitfalls | `hooks.pitfalls` |
| 8. Running lean (intro; empty) | `lean.overview` |
| Know your numbers first | `lean.measure` |
| Session hygiene | `lean.session-hygiene` |
| Caching: automatic, but don't fight it | `lean.caching` |
| Model routing | `lean.model-routing` |
| MCP hygiene | `lean.mcp` |
| Scale ceremony to task size | `lean.ceremony` |
| Guard expensive operations | `lean.expensive-ops` |
| Further reading | `reading.overview` |

R1.2 **Header stamp.** The guide's version line carries
`<!-- cc-verified-through: X -->`. X is the oldest `checked` across
sections, and the line's visible prose names the same version, so the header
never overclaims after a partial re-verification.

R1.3 **Manifest, `build/cc_guide.toml`.** Committed; it holds only our own
data.
- `[meta]`: `guide` (the path), `docs_base`
  (`https://code.claude.com/docs/en/`), `baseline` (the cache directory the
  hashes came from, initially `2026-10-03`), and `watch` (broad watch terms,
  R4.4).
- `[sections.'<id>']`, one per anchor:
  - `pages`: source entries `page.md` or `page.md#heading-slug`; a full URL
    for another host (pricing lives on `platform.claude.com`); `[]` for a
    pure-advice section, which docs drift then never flags.
  - `keywords`: changelog terms, matched as case-insensitive substrings;
    `[]` is allowed.
  - `checked`: the release through which the section was last verified or
    cleared.
  - `changed`: the release at which its content last changed.
  - `text_hash`: `sha256:` of the section's normalized text (anchor line
    excluded, whitespace collapsed).
  - `source_hashes`: one `sha256:` per `pages` entry, of the normalized
    source subtree (R4.3).
- `[probes.'<name>']`: `backs` (section IDs), optional `files`, and `turns`,
  a cost hint (R5).

R1.4 **Stamp rules.**
- Versions compare as integer tuples: `2.1.288.1` sorts after `2.1.288` and
  before `2.1.289`.
- A new `changed` must be strictly greater than every review stamp among the
  section's citers. The tool proposes the newest known release; when that
  would not exceed the highest citer stamp, it proposes that stamp with a
  fourth component added or incremented.
- When a section's text no longer matches `text_hash`, the editor records one
  of two outcomes. **Substantive:** a new `changed` and `text_hash`, which
  flags every citer. **Editorial:** a new `text_hash` only.

### R2 — Citations

R2.1 **Form.** One line per citing file, `cc-guide: <id> [<id> …] @<version>`.
The version is the highest `changed` among the cited sections at the file's
last review.

| File | Placement |
|---|---|
| `SKILL.md`, `agents/*.md`, `commands/*.md`, `.claude/skills/*/SKILL.md`, `.claude/agents/*.md` | `# cc-guide: …` as a YAML comment, the last line inside the frontmatter |
| `*.sh`, `*.py` | a `# cc-guide: …` line before the first line of code. Only a shebang, comments, blank lines, a PEP 723 block (never inside it), and a Python module docstring may precede it |
| Markdown without frontmatter (CLAUDE.md, READMEs) | a block-level `<!-- cc-guide: … -->` at the top |

Citations never go in a skill or agent body: bodies reach Codex and Gemini
verbatim and cost tokens on every load.

R2.2 **Scope.** A file qualifies when its correctness rests on a Claude Code
fact that can change between versions; naming Claude Code is not enough.
- Known clusters: `hooks/` (the guard, its tests and README, the ruff and uv
  hooks, the probe); `agents/*.md` (tools, model, effort);
  `build/check_frontmatter.py` (`CONTEXT_VALUES`, the auto-mode model rule,
  `KNOWN_AGENT_TOOLS`); `commands/*.md`; skills whose frontmatter or text
  depends on Claude Code behaviour (`effort`, `context: fork`, slash
  commands, subagent dispatch, model aliases); `install.py` (install
  locations); the root `README.md` and `CLAUDE.md`.
- The plan's sweep fixes the exact list, including this system's own files.
  JSON holds no comments, so `build/cc_drift_hook.sh` carries the citation
  for the settings wiring.
- Excluded: `specs/`, `runtimes/`, `build/.scratch/`, `review/`.

R2.3 **Coverage gaps.** A relied-upon fact that no section covers is listed
in the plan's completion notes for the owner. The owner either extends the
guide (a new section, verified like any Mode 1 run) or leaves the fact
uncovered; the guide never grows silently. Expected first gaps: `agent_type`
in PreToolUse payloads (the guard); `claude -p` mechanics (variadic
`--allowedTools`, the stdin wait); the launchd PATH for hooks; the
capitalized `Explore` shadowing rule in `check_frontmatter.py`.

R2.4 **Invariants with existing machinery.** None of these changes.
- `check_frontmatter.py` never sees a YAML comment, so today's
  `ALLOWED_KEYS` and the portability spec's R1.1 key sets, R1.2 `metadata`
  shape, and R1.8 `--strict` are unaffected.
- `specs/` is not installed, so a citation is not a `DEPENDENCIES` edge and
  needs no `SOFT_REFERENCES` entry. Dotted, slash-free IDs cannot match the
  dependency-drift scanner's patterns; that test fails if one ever does.
- `sync_runtime_assets.py --check` stays clean: adapters keep only names,
  descriptions, and tools.

### R3 — `cc_drift.py lint`

An offline commit gate over the working tree. Exit 0 when clean; exit 1 with
one line per violation.
- Every heading has exactly one well-formed anchor (R1.1), and the manifest
  and the guide carry the same ID set.
- Each section's normalized text matches `text_hash`. A mismatch prints both
  outcomes (R1.4) with the exact TOML lines to apply.
- The header marker equals the oldest `checked` (R1.2).
- Every citation parses, cites existing IDs, sits where R2.1 allows, and
  appears once per file. The lint scans tracked files outside R2.2's
  excluded trees for lines that begin, after indentation, with
  `# cc-guide:` or `<!-- cc-guide:`; such a line outside its placement is a
  violation. The tool's own sources keep citation-shaped test data out of
  line-initial position.

Stale citations, whose stamp is below a cited section's `changed`, print as
`STALE <file> <ids>` on stderr and do not change the exit code. A `build/`
test runs `lint` against the repo, enforcing it the way the dependency-drift
test is enforced. CLAUDE.md's Commands section gains the invocation, to run
before committing a change to the guide or to any file carrying a citation.

### R4 — `cc_drift.py check` and its outputs

R4.1 **Inputs.** The guide, manifest, and citations come from `main`'s
commit via `git show` and `git grep`, never from whatever branch the shared
checkout is on. `--ref <ref>` and `--worktree` override.

R4.2 **Version gate.** Fetch `changelog.md`. If its head release and the
manifest's hash both match `state.json`, exit 0. Otherwise run R4.3–R4.5
and record the new head.

R4.3 **Source scan.** Fetch each cited page once, plus `llms.txt`. Cut each
`page#heading` entry to that heading's subtree (up to the next heading of the
same or higher level), strip the doc-index preamble (the leading blockquote
every page opens with, pointing at `llms.txt`), collapse whitespace, and
hash.
- A hash that differs from `source_hashes` is drift, reported with a unified
  diff against the baseline cache, or "no baseline cached" when that
  directory is absent (a fresh clone).
- A missing heading is drift.
- Pages added to or removed from `llms.txt` since the baseline go to triage.

R4.4 **Changelog scan.** Parse the `<Update label=… description=…>` blocks.
- For each section, a bullet is a hit when it comes from a release after the
  section's `checked` and contains one of its keywords.
- A bullet from a new release that matches a `[meta] watch` term but no
  section is listed as **unclaimed**, for triage; this is how a keyword gap
  surfaces.
- Other bullets are counted, not listed.

R4.5 **Outputs.**
- `report.md`, `state.json`, and `nudge.txt` live under
  `build/.scratch/cc-drift/` in the main checkout, resolved through
  `git rev-parse --git-common-dir` so every worktree shares them.
- Fetched pages go to `build/.scratch/cc-docs/<fetch-timestamp>/` with a
  `FETCHED.txt` (time, changelog head). The baseline directory is never
  written after bootstrap; only the baseline and the latest fetch are kept.
- The report lists, in order: drifted sections, each with its hits, its
  diffs, and the files citing it; unclaimed bullets; added and removed
  pages; probe failures (R5); the stale backlog, grouped by section.

R4.6 **Exit codes.** 0 when no section drifted (the stale backlog does not
count); 1 when at least one did; 2 on error.

R4.7 **Network.** stdlib `urllib` with a per-request timeout and an overall
budget, and a User-Agent that names the tool and carries no personal data.

R4.8 **Other subcommands.**
- `ack`: marks the current findings seen; the nudge stays silent until the
  findings change.
- `report [--sections <ids>] [--stale [<paths>]] --packets <dir>`: writes
  the per-section or per-file packets R7 consumes.
- `quotes [--docs <cache-dir> | --guide]`: reads `<source>\t<quote>` rows and
  prints `FOUND <source>:<line>` or `MISSING`, exiting 1 on any miss. A quote
  must match within a single line, the method that found 151 of 151 in the
  refresh.
- `bootstrap` (R8.1).

R4.9 **Clearing a false positive** means advancing that section's `checked`;
`check` prints the exact TOML line.

### R5 — Probes

R5.1 `cc_drift.py probe --claude <path> [--only <name>] [--force]
[--extended]`. `--claude` is required. `cc_drift.py binaries` lists
candidates with their versions: each `claude` on PATH with its symlink
target, and the Desktop app's bundled binaries, labelled as observed app
layout rather than documented.

R5.2 **Records.** Each run appends one line to
`build/.scratch/cc-drift/probes.jsonl`: time, probe, binary path,
`--version`, platform, the model the stream's init event reports, result
(`pass`, `fail`, or `error`), and detail. A probe whose last `pass` ran on
the same version is skipped unless `--force` is given.

R5.3 **Results.** `fail` means the behaviour differs from the guide. It is
drift: the probe's `backs` sections and `files` enter the report and the
nudge. `probe` writes its failures into `state.json`, `report.md`, and
`nudge.txt` itself, since R4.2's gate means a `check` may not rebuild the
report until the next release. `error` (exit 2) means the mechanism never
fired or the run broke; it is never a pass.

R5.4 **Isolation.** Each probe uses:
- a fresh `mktemp -d` directory outside any repo, never the bare `/tmp` root;
- the prompt first, with stdin from `/dev/null`;
- `--output-format stream-json --verbose`;
- assertions on the raw stream or on files its own hooks write, never on the
  model's prose;
- `--model sonnet` at low effort (through whichever flag or setting the
  probed binary supports), a bounded `--max-turns`, and an explicit
  permission mode with the probe's tools pre-allowed, so auto mode's
  classifier never runs;
- no MCP servers, plugins, or user settings beyond what it needs.

Scratch assets are generated into that directory at run time.

R5.5 **The v1 probes.**

| Probe | Mechanism | Pass | Backs | Cost |
|---|---|---|---|---|
| `guard-liveness` | runs `hooks/probe-readonly-guard.sh`, which gains a `CLAUDE_BIN` override (it hardcodes `claude` today). It is the one probe that needs user settings, since the guard is installed globally | the script's three checks pass | files `hooks/readonly-agent-guard.py`, `hooks/README.md`; no guide section yet (R2.3) | 3 short runs |
| `agent-tools` | a scratch agent with `tools: Read, Grep, Glob, Bash` and `omitClaudeMd: true`, run via `--agent`, plus a control agent without `Bash`. `--agent` stands in for subagent dispatch; the docs state one rule for both (`tools-reference.md:298`) | on macOS, Linux, and WSL the init event lists neither Grep nor Glob for the first agent and both for the control. A control that lists neither is `error` | `subagents.tools` | 2 single-turn runs |
| `stop-continuation` | a scratch Stop hook, registered through the scratch project's settings or `--settings` (whichever the first run proves loads), logs `stop_hook_active` and blocks on its first two calls | the log reads `false, true, true`. An empty log is `error`. `--extended` blocks on every call and records where the cap ends the loop (8 per the docs) | `hooks.exit-codes`, `hooks.patterns` | ~3 turns (~9 extended) |

### R6 — Trigger

R6.1 `.claude/settings.json` gains one `SessionStart` group with matcher
`startup` and two command hooks:

```json
{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/build/cc_drift_hook.sh nudge" },
{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/build/cc_drift_hook.sh check", "async": true }
```

The quoting follows the guide's own pattern; the unquoted form is drift #3.

R6.2 **`nudge`** is POSIX `sh` and synchronous. It finds the shared state
directory through `git rev-parse --git-common-dir` and prints `nudge.txt`'s
line when one is pending. No Python, no network, exit 0. It works under
`env -i PATH=/usr/bin:/bin`.

R6.3 **`check`** runs async.
- It exits 0 at once when the last successful check finished under 24 hours
  ago, or when another session holds the lock (an atomic `mkdir` lock; a lock
  older than an hour is broken).
- Otherwise it looks for `uv` on PATH, then in `~/.local/bin` and
  `/opt/homebrew/bin`, runs
  `uv run --python 3.13 python build/cc_drift.py check --hook` under an
  overall time budget, and exits 0.
- In `--hook` mode, `check` prints the nudge line only when findings are new,
  which delivers it to the current session on its next turn; `nudge.txt`
  carries it into later sessions.
- When `uv` is missing, or three checks in a row fail, `nudge.txt` reads
  `drift check failing: <reason>; run it by hand`.

R6.4 **The nudge line** names the release range, the count and first IDs of
the drifted sections, the unclaimed count, probe failures, the version the
probes last passed on, and the report path. It is one line under 300
characters and mentions only findings not yet acknowledged.

R6.5 The settings change is persistent configuration: the owner confirms it
before it is committed.

### R7 — The verify skill

R7.1 `.claude/skills/cc-verify/SKILL.md` sets `disable-model-invocation:
true`: typable as `/cc-verify`, absent from the listing, never auto-fired.
Its verifier is `.claude/agents/cc-verifier.md` with `model: sonnet`,
`tools: Read, Grep, Glob`, and `omitClaudeMd: true`. Without `Bash` the
verifier keeps Grep and Glob on macOS and stays outside the read-only
guard's remit. Both files carry citations. `check_frontmatter.py` does not
scan `.claude/`, and this spec does not widen it.

R7.2 **Mode 1: `/cc-verify [<ids>…]`** (docs → guide). With no IDs it takes
the drifted sections from the latest report.
1. `report --sections … --packets <dir>` writes one packet per section.
2. State the section count. Above 6 verifiers, ask before dispatching, or
   take a subset. Dispatch one `cc-verifier` per section, in parallel.
3. Each verifier returns rows of `guide line | claim | verdict (holds /
   changed / unsupported / new) | page#heading | verbatim quote | page
   line`. Every verdict except `new` carries an exact quote from the cached
   source; `changed` and `new` rows carry proposed guide prose.
4. `quotes --docs` re-checks every quote. A missing quote goes back to its
   verifier once; if it is still missing, the row is dropped and listed as
   unverified.
5. Write `build/.scratch/cc-drift/proposals/<timestamp>-sections.md`. Per
   section it holds the exact old → new guide text; the manifest lines to
   change (`checked` to the head release, `changed` only if the prose
   changes, the new `source_hashes`, the post-edit `text_hash`); and the
   files the `changed` bump will flag. Stop.

R7.3 **Mode 2: `/cc-verify --files [<paths>…]`** (guide → citing files).
With no paths it takes the stale backlog, in batches under the same
ask-above-6 rule.
1. `report --stale … --packets <dir>` writes, per file, the file and its
   cited sections' current text, marking the sections changed since its
   stamp.
2. One verifier per file returns rows of `file line | statement | section |
   verbatim guide quote | verdict (consistent / contradicts / not
   covered)`.
3. `quotes --guide` re-checks the quotes against the guide at `main`.
4. The proposal holds edits for the `contradicts` rows and the file's new
   stamp. `not covered` rows go to triage (R2.3). Stop.

R7.4 Both modes stop at a proposal. The owner reviews it; applying may
happen in the same session; `lint` runs; the owner commits. The skill never
commits, pushes, or edits the guide on its own.

### R8 — Bootstrap and first run

R8.1 **Manifest bootstrap.** `cc_drift.py bootstrap` prints a draft
manifest.
- `text_hash` comes from the anchored guide, and `checked = '2.1.288'` for
  every section: the header claims a full re-verification at 2.1.288.
- `changed = '2.1.288'` for the 32 sections whose text differs between
  `91474f6` and `c33bc99`, and `'2.1.219'` for the other 6. Sections align by
  (parent `##`, heading), never by heading text alone, so the two
  "Frontmatter reference ⚠" sections stay distinct.
- `source_hashes` come from `build/.scratch/cc-docs/2026-10-03/`, the snapshot
  the refresh actually read. A cited page or heading missing from it leaves
  its section unbaselined, and the first Mode 1 run verifies that section.
- `pages` and `keywords` are judgment work, drafted per section and reviewed
  by the owner. The refresh's verifier rows were not saved, so they cannot
  seed them.

The owner reviews the whole draft before it is committed.

R8.2 **Citation sweep.** Tag every pre-existing qualifying file (R2.2)
`@2.1.219` and record the coverage gaps (R2.3). Files this plan creates are
written against the current guide, so they take the highest `changed` among
their cited sections.

R8.3 **First run.** `lint` and `check` run against the real repo and docs.
The stale backlog must include `agents/*.md`, `hooks/ruff-check.sh`, and
`hooks/README.md`.

R8.4 **First Mode 2 batch: the three known drifts.** The reviewer starts
from these considerations.
- **#1, `Grep, Glob` beside `Bash` in all 7 agents.** In Claude Code on macOS
  they are inert. The Gemini adapters map them to `grep_search` and `glob`,
  which work there, so deleting them from the canonical files regresses
  Gemini. Searches already run through Bash, so the read-only guard must
  keep allowing `find` and `grep`. Agent bodies may tell agents to use Grep
  or Glob. The owner decides.
- **#2, `hooks/ruff-check.sh`.** The guide's Pattern 3 presents both
  behaviours as valid: exit 0 whenever `stop_hook_active` is set (one attempt
  per turn, the fix never re-checked), or re-run the check and block while
  it still fails (bounded by the 8-block cap). The owner chooses, and the
  script's comment states the chosen semantics.
- **#3, `hooks/README.md` lines 56, 60, 64.** Quote `$CLAUDE_PROJECT_DIR` as
  the guide's Pattern 1 does.

R8.5 Later Mode 2 batches clear the rest of the backlog. It tracks itself
(the lint's `STALE` lines and the report), so plan completion logs one
deferred item pointing at it rather than one per file.

### R9 — Tests

R9.1 `build/test_cc_drift.py` is directory-scoped, uses stdlib plus pytest,
and enters CLAUDE.md as a +N delta. Its units cover: anchor and ID rules;
section splitting, including fenced `#` lines and both "Frontmatter
reference ⚠" sections; normalization and hashing; version ordering,
four-component stamps included; citation parsing in all three comment
forms; `<Update>` parsing; keyword versus watch-term classification;
heading-subtree extraction; stale computation; and the nudge text.

R9.2 Fixtures are original synthetic text, never copied from Anthropic's
docs.

R9.3 **Replay acceptance test.** Rebuild the guide at `91474f6` and
`c33bc99` from git (our text), derive `changed` as R8.1 does, and run against
fixture citers stamped `@2.1.219`. A file citing `subagents.tools` and a
file citing `hooks.patterns` must be flagged; a control citing
`skills.description` must not. Skip with a reason when the history is
unavailable (a shallow clone).

R9.4 A repo test runs `lint` on the real repo. A test proves that a
`SKILL.md` carrying a citation passes `check_frontmatter.py`. The
dependency-drift test and `sync_runtime_assets.py --check` stay unchanged.

R9.5 `cc_drift_hook.sh nudge` is tested under `env -i PATH=/usr/bin:/bin`.

R9.6 The probes' stream parsers are tested against stream-json recorded from
our own probe runs. Each probe's first live run must agree with the 2.1.288
docs before its results are trusted, and a deliberately broken setup must
yield `error`, not `pass`.

## Sequencing and execution constraints

Four stages. A ships alone; B, C, and D each need A; C and D are
independent of each other.

- **A — core.** Anchors, the manifest bootstrap, `lint`, the citation sweep,
  `check`, `report`, `ack`, `quotes`, the tests, the CLAUDE.md commands, and
  the `.gitignore` comment describing the new `build/.scratch/` contents.
- **B — verify.** The skill (both modes), the verifier agent, and the first
  Mode 2 batch (R8.4).
- **C — probes.** `probe`, `binaries`, the three probes, `CLAUDE_BIN` in the
  guard probe, and a first recorded run.
- **D — trigger.** `cc_drift_hook.sh` and the settings entries (R6.5).

Constraints:
- **Base.** This spec sits on `docs/cc-drift-spec`, branched from `main` at
  `b0ee62e`, which carries both the refreshed guide (`c33bc99`) and the
  portability spec. Integrating it is the owner's call.
- **Work in a worktree.** Stage A's sweep edits frontmatter in skills the
  executing session loads, and `~/.claude/skills` resolves to the main
  checkout.
- **Portability spec coupling.** Its R1.4 adds `metadata` blocks to the 13
  superpowers skills' frontmatter, where this sweep adds a comment line;
  whichever branch merges second reconciles both in that merge. When a script
  gains a PEP 723 header (its R3), the citation goes below the block.
- **JAX branch.** Skills from `codex/jax-deep-learning-skills` that rest on
  Claude Code facts get citations in whichever merge comes second.
- **Plan id.** Check `specs/plans/` on every branch (`git ls-tree`) before
  allocating one; ids 32 to 34 are taken on sibling branches.
- **Test counts** are +N deltas against each suite, never absolute totals.
- **Copyright.** Caches, reports, packets, proposals, and probe streams that
  hold Anthropic text stay under `build/.scratch/`. Commits carry only our
  values: hashes, versions, slugs, keywords, IDs. Before each commit, confirm
  nothing under `build/.scratch/` is staged; `git check-ignore` needs a file
  path or a trailing slash there.
- **Nothing outward-facing.** The tool and the skill never commit, push, or
  post.

## Validation and acceptance

1. Every gate in CLAUDE.md's Commands passes, plus `cc_drift.py lint` and
   the new tests. `sync_runtime_assets.py --check` and the dependency-drift
   test pass unchanged.
2. The replay test (R9.3) flags exactly its expected fixture files.
3. The first live `check` writes a report, and its unclaimed list has been
   reviewed once to tune keywords.
4. The stale backlog includes the three known drift files. The first Mode 2
   batch produced proposals for them, the owner's decisions on #1 and #2 are
   recorded, the fixes are applied, and those files leave the backlog.
5. Each probe has run once on an owner-chosen binary and agreed with the
   2.1.288 docs, or the disagreement is investigated and recorded. A broken
   setup yielded `error`.
6. The hook pair works: `nudge` under a launchd-like PATH, `check` writing
   state, and a session started with new findings pending shows exactly one
   nudge line.
7. The coverage gaps are listed for the owner.
8. Nothing under `build/.scratch/` is committed.

## Out of scope (deferred; logged to `specs/deferred_items.md` at plan completion)

- An effort-pin probe; deferred item 31 stays a manual watch.
- Line-level citations, and anchors for individual rows of the guide's
  tables.
- The Codex and Gemini customization guides (`b0ee62e`). The anchor and
  manifest design extends to them, but their sources need their own fetchers
  and gates.
- `specs/agent-skills-best-practices.md`: multi-vendor, and the owner ruled it
  out of the refresh.
- Auto-applying proposals, and CI (the repo has none).
- Widening `check_frontmatter.py` to `.claude/skills` and `.claude/agents`.
- Updating the terminal CLI from 2.1.265, an owner action noted because it is
  the binary `claude -p` reaches by default.
- Reconciling this design with the peer session's.

## Sources and verification notes

- The guide at `c33bc99` (identical at `b0ee62e`) is the hub; `91474f6` is
  its July version. `9f85f08`'s commit message records the refresh: every
  changed fact traced to a verbatim doc quote, 151 of 151 re-grepped, five
  July claims corrected.
- `specs/agent-skills-portability.md` at `b0ee62e` supplies R1.1, R1.2, R1.4,
  R1.8, and R3 as cited above.
- Line references are to the docs snapshot under
  `build/.scratch/cc-docs/2026-10-03/docs/`: `memory.md:150`,
  `tools-reference.md:34-35, 292-298`, `sub-agents.md:230`,
  `statusline.md:202` (the status line's `version` field), and the named
  sections of `hooks.md`, `desktop-scheduled-tasks.md` (the scheduling
  comparison), and `routines.md` (environments and network access).
- `desktop.md` and `env-vars.md`, fetched 2026-10-03 at 19:44: neither
  documents `CLAUDE_CODE_EXECPATH` or a status line in the Desktop app.
  `desktop.md` is not in the snapshot.
- `hooks/probe-readonly-guard.sh` and `hooks/README.md` ("Probe log" and
  lines 136-139) supply the probe mechanics and the launchd PATH this design
  reuses.
- The manual refresh's cost, six Sonnet verifiers at about 320–415K tokens
  each and about 2.2M in total, comes from the owner's brief for this
  design.
