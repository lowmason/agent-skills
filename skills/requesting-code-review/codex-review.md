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
  review skipped" and continue without it.
- You are Codex. A second opinion from the same model family isn't one; say so
  and continue.

## Launch

1. **Clean tree.** `git status --porcelain --untracked-files=normal` must
   print nothing (the flag overrides a `status.showUntrackedFiles=no`
   config that would hide new files). The preset
   diffs the merge base against the *working tree*, so an uncommitted edit
   would be reviewed as if it were on the branch — and a new file never
   `git add`-ed passes the tests locally while never reaching Codex or the
   push. Commit what is part of the work; ask your partner about anything
   else. Never `git stash` it away: every worktree of the repo shares one
   stash stack.
2. **Note the HEAD under review** — `git rev-parse --short HEAD`. It only
   becomes a record of a review once the run completes (see below).
3. **Start it in the background.** It takes minutes: 85 s for a ten-line
   commit at `xhigh` effort, far longer for a branch. In Claude Code use Bash
   with `run_in_background` and don't poll — you are notified when it exits,
   whereas a foreground call is cut off at 10 minutes. Elsewhere, use your
   platform's background mechanism and wait for the process to exit, or run
   it in the foreground with a timeout long enough for the whole branch. Write
   the values in literally; worktree-isolated sessions refuse to run a `codex`
   command assembled from shell variables:

   ```bash
   mkdir -p /tmp/codex-review
   codex exec review -c sandbox_mode=read-only --base <BASE> -o /tmp/codex-review/<short-HEAD>.md > /tmp/codex-review/<short-HEAD>.log 2>&1
   ```

   - `--base <BASE>` — Codex runs `git merge-base HEAD <BASE>` and reviews
     everything since. BASE is either the branch's merge base with its base
     branch, computed just before launch and shared with code-reviewer; or,
     for a plan executed on the base branch itself, the SHA recorded before
     its first task or the start your partner confirmed; or — in
     finishing-a-development-branch only — the SHA of an earlier
     `Codex reviewed` line, to review just the commits after it. On a feature
     branch, do not substitute a SHA noted earlier in the session for the
     merge base: a rebase onto a newer base branch silently widens that range
     to upstream commits. The base branch has no merge base to recompute, so
     its recorded start holds only while no pull or rebase has brought
     upstream commits into the range; once one has, ask your partner where
     the plan's work begins.
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
  Then write `Codex reviewed <short-HEAD>` into the conversation, and into the
  progress ledger if the run keeps one, so it survives a context checkpoint.
  The line means everything from the branch's merge base (on the base branch
  itself, from the plan's recorded or confirmed start) through that SHA has
  had a completed Codex review — true because every BASE above is one of
  those starting points or an earlier such line. It is the only record of a
  completed review; a later finishing-a-development-branch run keys on it to
  avoid a repeat pass.
- **Anything else:** report "Codex review did not complete:" with the log's
  last line (`tail -n 1` the log), and write no `Codex reviewed` line. In
  executing-plans and subagent-driven-development, proceed on code-reviewer's
  review: with no line written, finishing-a-development-branch runs Codex on
  the work before it ships — the whole branch, or on the base branch itself
  from a start your partner gives it. In finishing-a-development-branch,
  where this run is the gate, always ask your partner whether to retry or
  proceed without it — even if code-reviewer ran beside it. Never report a
  Codex review that did not complete.

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
