# Micro-test: the marimo notebook block and explore-data's marimo branch

This record holds the measurements for plan 98, which is Plan B of [the marimo notebook seam spec](../marimo-notebook-seam.md). Each section is one check, and the first is B0.

## B0

B0 is the spec's first check of Plan B. It asks one question. Does Codex truncate an `AGENTS.md` that is past its 32 KiB limit, or does it drop the file? The answer decides where a later task tells users to paste the notebook block.

**Run.** The check ran on 2026-11-14 with `codex-cli 0.167.2`.

**Scratch file.** The check used a new git repository under `/tmp/mnb98/b0/`. It holds one `AGENTS.md` of 49,210 bytes. Every line is 70 bytes long, and each filler line carries its own number. Eight sentinel lines mark known offsets. A sentinel line is a marker line with a unique name. The file held synthetic text only. The run opened no file from this repo. Codex adds the names and descriptions of installed skills to its prompt. Some of those skills come from this repo's public `skills/` folder, so that text went to OpenAI in the `codex exec` run.

**Instruments.** Two instruments measured the result.

1. `codex debug prompt-input 'hello'` renders the model-visible input without a model call. It exited 0. The check counted each sentinel in the output.
2. `codex exec -m gpt-6-sol -c sandbox_mode=read-only` asked the model to list every `SENTINEL-` line from its instructions. The prompt said to run no command and use no tool. It exited 0. The log shows no command, so the run is valid.

| Sentinel | Starts at byte | In the rendered input | In the read-back |
|---|---|---|---|
| A (top) | 0 | 1 | listed |
| B | 16,450 | 1 | listed |
| C | 26,670 | 1 | listed |
| D | 29,750 | 1 | listed |
| E | 31,780 | 1 | listed |
| F | 33,810 | 0 | not listed |
| G | 41,020 | 0 | not listed |
| H (end) | 49,140 | 0 | not listed |

**Cut.** The last full filler line in the rendered input is line 468. The next 8 bytes of line 469 follow it, as `filler l`. Then only the closing tag of the instruction block follows. So the cut falls at byte 32,768 of the file, in the middle of a line. That is exactly 32 KiB.

**Global file.** Yes, a global file also loaded. The cut still fell at byte 32,768 of the project file. So in this run the global file did not reduce the project file's share of the limit. The Codex guide calls the limit combined, and this run does not show the global file counting against it. The run tested one project file and one global file.

**Result.** Codex truncates an oversized `AGENTS.md` at 32 KiB and keeps everything before the cut, so the placement rule holds: a block near the top of the file loads, and text past byte 32,768 does not.
