# Codex Second-Opinion Review

A second review of the same commit range from a different model family. It runs
beside the code-reviewer subagent, not instead of it: code-reviewer checks the
work against its plan or requirements; Codex's review preset is defect-first —
it hunts bugs in the diff and never sees the plan. Two lenses, two model
families.

**You run it, as the controller.** Never ask a reviewer subagent to run Codex —
code-reviewer's contract forbids it from spawning further reviewers.

## Skip it when

- `command -v codex` prints nothing. Say "Codex CLI not installed — second
  review skipped" and continue with the other review.
- You are Codex. A second opinion from the same model family isn't one; say so
  and continue.

## Launch

1. **Clean tree.** `git status --porcelain --untracked-files=no` must print
   nothing. The preset diffs the merge base against the *working tree*, so
   uncommitted edits to tracked files would be reviewed as part of the branch.
2. **Record the HEAD under review** — `git rev-parse --short HEAD` — in the
   conversation, where a later finishing-a-development-branch run reads it to
   avoid a repeat pass. If the run keeps a progress ledger, record it there
   too, so it survives a context checkpoint.
3. **Start it in the background** (in Claude Code: Bash with
   `run_in_background`) and don't poll — you are notified when it exits. It
   takes minutes: 85 s for a ten-line commit at `xhigh` effort, far longer for
   a branch, and a foreground Bash call is cut off at 10 minutes. Write the
   values in literally; worktree-isolated sessions refuse to run a `codex`
   command assembled from shell variables:

   ```bash
   mkdir -p /tmp/codex-review
   codex exec review -c sandbox_mode=read-only --base <BASE> -o /tmp/codex-review/<short-HEAD>.md > /tmp/codex-review/<short-HEAD>.log 2>&1
   ```

   - `--base <BASE>` — Codex runs `git merge-base HEAD <BASE>` and reviews
     everything since, so give it the same BASE the code-reviewer got. A commit
     SHA or a branch name both work.
   - `-c sandbox_mode=read-only` — required. A Codex config that trusts the
     project resolves `exec review` to `workspace-write`: a reviewer that can
     edit the tree it is reviewing.
   - `-o` captures the final review message alone. The log takes stdout plus the
     stderr progress stream, which echoes every command Codex runs (134 KB for
     that ten-line commit) — never read the log whole.
   - No custom instructions: `--base` and a prompt are mutually exclusive, and
     the preset is the point. Plan conformance is code-reviewer's job.
4. **Leave the tree alone until it exits.** Codex reads the files as it goes;
   fixing code mid-review hands it a moving target.

## Read the result

- **Exit 0 and a non-empty `.md`:** Read the `.md` — that is the whole review.
- **Anything else:** report "Codex review did not complete:" with the log's
  last line (`tail -n 1` the log) and proceed on the other review. Never report
  a Codex review that did not complete.

Codex opens each finding's title with a priority tag and ends with an overall
verdict (`patch is correct` / `patch is incorrect`). Map the tags onto
code-reviewer's scale: `[P0]` → Critical, `[P1]` → Important, `[P2]`/`[P3]` →
Minor. A clean review may be a single paragraph with no tags.

## Act on it

Merge Codex's findings with code-reviewer's into one list — a defect both raise
is one finding — and work that list with the receiving-code-review skill: verify
each finding against the code before changing anything, and push back where one
is wrong. A second opinion earns no extra weight by agreeing with the first
review, and no discount by disagreeing with it.
