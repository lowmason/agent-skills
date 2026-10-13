---
name: cc-guide
description: >
  Use when acting on what this repo's Claude Code drift check reports about
  specs/guides/claude-code-customization-guide.md: "triage the changelog",
  "verify these guide sections", "audit a group", "review the stale citations",
  or a check summary that names releases untriaged, changed docs blocks, an
  audit due or stale citing files.
argument-hint: 'triage | verify <ids> | audit [<group>] | files [<paths>]'
disable-model-invocation: true
# cc-guide: skills.frontmatter skills.arguments subagents.isolation @2.1.296
---

# /cc-guide

Acts on what `check` reports for `specs/guides/claude-code-customization-guide.md`, the guide. Each mode builds packets, dispatches the `cc-guide-verifier` agent on them, and settles every report with a script before anything is applied. The design is `specs/claude-code-drift-automation-spec.md`, R8; `references/formats.md` holds the packet layout and the report formats.

`cli.py` below stands for `uv run --python 3.13 python build/cc_guide/cli.py`, run from the repo root.

## Ground rules

- Nothing is committed. Corrections, bookkeeping and stamps stay in the working tree for the owner to review as a diff.
- Run in a worktree on its own branch, cut from current `main`, never in the shared checkout: every mode can edit the guide, `build/cc_guide/baseline.json` and citing files. The commands read the working tree.
- Packets live under `~/.cache/agent-skills/cc-guide/packets/` and hold docs text: copy nothing from them into the repo. Quotes go only into the report to the owner.
- Never paste a packet into a dispatch prompt; name its directory, and the verifier reads it.
- State the number of verifiers before dispatching. Above 6, ask the owner first or take a subset.
- Apply only what settle lists as a correction or a contradiction, and never an owner's-call item. Edit only the guide in verify and audit, and only the reviewed file in files. Two follow-ons belong to the same fix: removing or narrowing the `[[exception]]` it resolves in `build/cc_guide/conformance.toml` (After any mode), and, for a canonical agent or command, regenerating `runtimes/` with `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py`. A fix that would reach any other file is the owner's call.
- A listed item you leave for the owner, because it needs a decision (R11.5's #1 and #2) or would reach another file, holds its section or file: run `cli.py settle <packet> --hold <section or file>`, and run the commands it prints in place of the first ones.
- In files, a contradiction that `build/cc_guide/conformance.toml` records as a `deviation` for that file, in that section, is the owner's standing decision: leave it as it is, and it holds nothing. One the register records as a `gap` is still open, so it holds the file. A deviation covers only the statement its `guide` line names; any other contradiction in the file is handled as if no entry named it.

## Pick the mode

The typed words arrive on the ARGUMENTS line: `triage`, `verify <ids>`, `audit [<group>]` or `files [<paths>]`. With none, run `cli.py check --worktree` and offer the mode its due items call for. Probes arrive with Stage 5.

## Dispatch, save, settle

Every mode handles each packet the same way:

1. Dispatch the Agent tool with subagent type `cc-guide-verifier` and the prompt `Mode: <mode>. Packet: <absolute packet directory>. Read its index.json first, then follow your contract and return only the report.` Dispatch several packets in one message, so they run in parallel.
2. Save the verifier's reply, unchanged, as `report.md` in its packet directory, with the Write tool.
3. Run `cli.py settle <packet directory>`. Exit 0: every row parsed, every quote was found, and nothing was discarded or left out. Exit 1: settle failed something safe; read its UNSURE, unverified, unparseable and left-out lines. Exit 2: a setup error to fix before going on. What settle held or discarded stands: never edit `report.md`, ask the verifier to reword a row, or read settle's code to get past it. Report it to the owner; the next run takes it up again.
4. Run the commands settle prints, in the order it prints them.

## triage

1. Run `cli.py check --worktree`. Exit 2 is an error to fix first.
2. Run `cli.py packets --triage`. "nothing to triage" ends the mode. Above 20 untriaged releases after the newest checked one, it refuses and names the `--through` of the first range of 20: build that one.
3. Dispatch one verifier, about \$0.05–0.20, then save and settle.
4. Settle's `verify:` line names the sections a TOUCHES or UNSURE row sent on. Verify them now with `cli.py packets --verify --from <triage packet directory>`, which takes those sections, or tell the owner they are deferred: they do not advance, so the next triage shows them again.
5. Settle's `owner:` lines go to the owner. Its advance stops below the oldest release one names.
6. A ranged triage's settle ends with `next range`. Once its commands have run and its verify is done or deferred, build that range the same way.

## verify <ids>

1. Run `cli.py check --worktree`, unless a triage in this run just did.
2. Run `cli.py packets --verify <ids>`. It writes one packet per group, about \$0.30–1 each.
3. Dispatch, save and settle each.
4. Apply each correction settle lists to the guide in the working tree, checking it against its quote. Then run settle's commands: `accept --substantive` only for the sections whose text you changed (lint names any you missed), then rebaseline, advance, stamp, lint and `check_conformance.py`.

## audit [<group>]

As verify, from `cli.py check --worktree` and then `cli.py packets --audit [<group>]`: no group means the due one, and packets refuses when none is due. It costs about \$2.50–5.30, and settle's commands end with `baseline audited <group>` in place of advance.

## files [<paths>]

1. Run `cli.py packets --files [<paths>]`: no paths means the stale backlog. It writes one packet per file; dispatch them in batches under the ask-above-6 rule.
2. For each, settle, then fix each contradiction it lists, in that file only, and run its commands. `baseline cite <file>` runs only for a file settle does not hold: settle again with `--hold <file>` before running anything when you leave a contradiction for the owner. Lint and `check_conformance.py` run either way. A held file stays in the backlog.
3. A not-covered row is the owner's call, and may be a coverage gap the guide could gain (spec R4.3).

## After any mode

- A correction that resolves a conformance gap removes its `[[exception]]` from `build/cc_guide/conformance.toml`, or narrows its `artifacts`, in the same change; `check_conformance.py` must pass.
- Report to the owner: the working-tree diff, split into fact corrections and owner's-call items; what settle held or left unverified; the B and C items; and lint's `STALE` lines for each section whose `changed` moved.
