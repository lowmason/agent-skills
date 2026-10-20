---
name: cc-guide
description: >
  Use when acting on what this repo's Claude Code drift check reports about
  specs/guides/claude-code-customization-guide.md: "triage the changelog",
  "verify these guide sections", "audit a group", "review the stale citations",
  "run the probes", or a check summary that names releases untriaged, changed
  docs blocks, an audit due, probes due or stale citing files.
argument-hint: 'triage | verify <ids> | audit [<group>] | files [<paths>] | probes'
disable-model-invocation: true
# cc-guide: skills.frontmatter skills.arguments subagents.isolation @2.1.302
---

# /cc-guide

Acts on what `check` reports for `specs/guides/claude-code-customization-guide.md`, the guide. Each mode but `probes` builds packets, dispatches the `cc-guide-verifier` agent on them, and settles every report with a script before anything is applied. The design is `specs/claude-code-drift-automation-spec.md`, R8, and R10 for `probes`; `references/formats.md` holds the packet layout and the report formats.

`cli.py` below stands for `uv run --python 3.13 python build/cc_guide/cli.py`, run from the repo root.

## Ground rules

- Nothing is committed. Corrections, bookkeeping and stamps stay in the working tree for the owner to review as a diff.
- Run in a worktree on its own branch, cut from current `main`, never in the shared checkout: every mode can edit the guide, `build/cc_guide/baseline.json` and citing files. The commands read the working tree.
- Packets live under `~/.cache/agent-skills/cc-guide/packets/` and hold docs text: copy nothing from them into the repo. Quotes go only into the report to the owner.
- Never paste a packet into a dispatch prompt; name its directory, and the verifier reads it.
- State the number of verifiers before dispatching. Above 6, ask the owner first or take a subset.
- Apply only what settle lists as a correction or a contradiction, and never an owner's-call item. Edit only the guide in verify and audit, and only the reviewed file in files. Two follow-ons belong to the same fix: removing or narrowing the `[[exception]]` it resolves in `build/cc_guide/conformance.toml` (After any mode), and, for a canonical agent or command, regenerating `runtimes/` with `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py`. A fix that would reach any other file is the owner's call.
- A listed item you leave for the owner, because it needs a decision or would reach another file, holds its section or file: run `cli.py settle <packet> --hold <section or file>`, and run the commands it prints in place of the first ones.
- In files, a contradiction that `build/cc_guide/conformance.toml` records as a `deviation` for that file and statement is the owner's standing decision: leave it as it is, and it holds nothing. One the register records as a `gap` is still open, so it holds the file. A deviation covers only the statement its `guide` line names; any other contradiction in the file is handled as if no entry named it.

## Pick the mode

The typed words arrive on the ARGUMENTS line: `triage`, `verify <ids>`, `audit [<group>]`, `files [<paths>]` or `probes`. With none, run `cli.py check --worktree` and offer the mode its due items call for.

## Dispatch, save, settle

Every mode handles each packet the same way:

1. Dispatch the Agent tool with subagent type `cc-guide-verifier` and the prompt `Mode: <mode>. Packet: <absolute packet directory>. Read its index.json first, then follow your contract and return only the report.` Dispatch several packets in one message, so they run in parallel.
2. Save the verifier's reply, unchanged, as `report.md` in its packet directory, with the Write tool.
3. Run `cli.py settle <packet directory>`. Exit 0: every row parsed, every quote was found, and nothing was discarded or left out. Exit 1: settle failed something safe; read its UNSURE, unverified, unparseable and left-out lines. Exit 2: a setup error to fix before going on. What settle held or discarded stands: never edit `report.md`, ask the verifier to reword a row, or read settle's code to get past it. Report it to the owner; the next run takes it up again.
4. Run the commands settle prints, in the order it prints them and one at a time, never in a parallel batch: each `baseline` command rewrites `build/cc_guide/baseline.json`, so two at once can lose a write. Each `rebaseline` ends with `--head`, the packet's head. When one refuses because the latest fetch is at another release (a session start or another `check` refetched the docs), skip it, run the rest, and tell the owner: the next `check` compares those blocks again. Never drop `--head` to get past the refusal.

## triage

1. Run `cli.py check --worktree`. Exit 2 is an error to fix first.
2. Run `cli.py packets --triage`. "nothing to triage" ends the mode. Above 20 untriaged releases after the newest checked one, it refuses and names the `--through` of the first range of 20: build that one.
3. Dispatch one verifier, about \$0.05–0.20, then save and settle.
4. Settle's `verify:` line names the sections a TOUCHES or UNSURE row sent on. Verify them now with `cli.py packets --verify --from <triage packet directory>`, which takes those sections, or tell the owner they are deferred: they do not advance, so the next triage shows them again. When the TOUCHES or UNSURE rows for one block name sections of two groups (`build/cc_guide/manifest.toml` lists each group's sections), its own group's settle checks only that group (spec R8.4 step 6): verify both groups in this run, settle the other group's packet first, and if that section ends held or deferred, leave the block's ref out of its own group's `rebaseline`, keeping its `--head`, with the rest of its page if `rebaseline` then refuses the page. If that leaves no ref, skip the command: `rebaseline` with no refs takes the whole group.
5. Settle's `owner:` lines go to the owner. Its advance stops below the oldest release one names.
6. A ranged triage's settle ends with `next range`. Once its commands have run and its verify is done or deferred, build that range the same way.

## verify <ids>

1. Run `cli.py check --worktree`, unless a triage in this run just did.
2. Run `cli.py packets --verify <ids>`. It writes one packet per group, about \$0.30–1 each.
3. Dispatch, save and settle each.
4. Apply each correction settle lists to the guide in the working tree, checking it against its quote. Write a short common word unformatted: a backticked span of 3 to 60 characters that `STOP_TERMS` (`build/cc_guide/guide.py`) does not list becomes a watch term, matched as a substring of each docs block, so a backticked `none` makes every block with "nonessential" due. If such a term is needed, ask the owner for an `exclude_terms` entry in `build/cc_guide/manifest.toml`. Then run settle's commands: `accept --substantive` only for the sections whose text you changed (lint names any you missed), then rebaseline, advance, stamp, lint and `check_conformance.py`.

## audit [<group>]

As verify, from `cli.py check --worktree` and then `cli.py packets --audit [<group>]`: no group means the due one, and packets refuses when none is due, while a named group is audited even then. It costs about \$2.50–5.30. Settle's commands put `baseline audited <group> --to <head>`, at the packet's head release, where verify's put advance, and `stamp`, lint and `check_conformance.py` still follow it.

## files [<paths>]

1. Run `cli.py packets --files [<paths>]`: no paths means the stale backlog. It writes one packet per file; dispatch them in batches under the ask-above-6 rule.
2. For each, settle, then fix each contradiction it lists, in that file only, and run its commands. `baseline cite <file>` runs only for a file settle does not hold: settle again with `--hold <file>` before running anything when you leave a contradiction for the owner. Lint and `check_conformance.py` run either way. A held file stays in the backlog.
3. A not-covered row is the owner's call, and may be a coverage gap the guide could gain (spec R4.3).

## probes

Live probes check behaviour the guide states before the docs change (spec R10). Each one is a short `claude -p` run that spends tokens, so they run only in this mode or by the owner's hand, never from the session-start hook.

1. Run `cli.py binaries` and ask the owner which binary to probe. `probes` takes no default, since with several versions installed a default would probe the wrong one (spec Decision 15).
2. Check the checkout that the installed agents and guard come from. `guard-liveness` and `agent-model-pins` load user settings, so they run the files under `~/.claude/`, which link into the shared checkout and not into this worktree. Run `readlink ~/.claude/agents/explore.md`; the checkout is the folder that holds the `agents/` directory its path names, not `agents/` itself. Then run `git -C <that checkout> branch --show-current` and `git -C <that checkout> status --short -- agents hooks`. If the branch is not `main` or the status prints anything, stop and ask the owner: a row would describe other agents than the ones on `main`.
3. Run `cli.py probes --claude <path>`, which runs the due probes. `--only <ids>` names others, and `--force` runs every one. State the count first: a live probe costs about \$0.05–0.30. A binary older than the newest cached changelog release is refused; pass `--allow-old` only on the owner's word, and each row records it. Exit 2 is a setup error to fix first.
4. Each probe appends one row to `build/cc_guide/PROBES.md`, uncommitted, and keeps its raw output under `~/.cache/agent-skills/cc-guide/probes/`. `agent-model-pins` also leaves its session under `~/.claude/projects/`, since it reads effort from the transcripts. That output holds home paths and session ids: copy nothing from it into the repo.
5. A DIVERGES row is handled like a TOUCHES row: the probe's `[[probe]]` entry in `build/cc_guide/manifest.toml` names its sections and files. Run the `verify <ids>` mode on those sections and the `files [<paths>]` mode on those files. An ERROR row says nothing about the behaviour: read its raw output, then report it to the owner. DIVERGES and ERROR stay due until a later PASS.

## After any mode

- A correction that resolves a conformance gap removes its `[[exception]]` from `build/cc_guide/conformance.toml`, or narrows its `artifacts`, in the same change; `check_conformance.py` must pass.
- Report to the owner: the working-tree diff, split into fact corrections and owner's-call items; what settle held or left unverified; any `rebaseline` that refused because a later fetch moved the docs; the B and C items; and lint's `STALE` lines for each section whose `changed` moved.
