# Step 3b: Explain the branch

Before the Step 4 menu, a fresh subagent writes an explainer of the branch, so that your partner can read it before
the pick. Use the values that Step 2 and Step 3 recorded. As in Step 2, run each command below as its own call, with
every value written out.

1. **Skip.** Check this first. If your partner said to skip the explainer, go to Step 4. Run none of the commands
   below, the fetch included.

2. **BASE.** Run `git fetch origin <base-branch>`, then `git merge-base origin/<base-branch> HEAD`. With no remote (the
   fetch fails because there is no `origin`), run `git merge-base <base-branch> HEAD` instead. If the fetch fails for
   any other reason, run the same merge-base on the `origin/<base-branch>` that you have. The remote-tracking base
   matters because a local base branch that fell behind would put other merged branches' commits, and their plans,
   in `BASE..HEAD`. Record the output as BASE. Then run `git rev-parse HEAD` and record HEAD.

3. **Plan branch.** Run:

   ```bash
   git diff --name-only --diff-filter=AR <BASE>..HEAD -- ':/specs/plans/completed/'
   ```

   If it prints a path, the branch is a plan branch: dispatch (item 6) with `Plan branch: yes`, and ask no question.
   The `':/'` makes the path start at the repository's top folder, whatever the current folder is. `AR` counts a
   plan that was added and a plan that was renamed into `completed/`.

4. **No plan.** If it prints nothing, ask your partner this one line and wait for the answer:
   `This branch adds no plan. Do you want an explainer of it before the menu?`
   Do not show the menu in the same message. On a yes, dispatch with `Plan branch: no`. On a no, go to Step 4.

5. **Output path.** `~/.cache/branch-explainers/<repo>/<YYYY-MM-DD>-<slug>.md`, written out in full, with the home
   folder expanded (`printf '%s\n' "$HOME"` prints it).
   - `<repo>` is the last path component of MAIN_ROOT from Step 2.
   - The date is today's (`date +%Y-%m-%d`).
   - `<slug>` is the branch name from `git branch --show-current`, with each character outside `A-Za-z0-9._-`
     replaced by `-`. On a detached HEAD the command prints nothing, and the slug is `detached-<the first 7
     characters of HEAD>`.

6. **Dispatch.** Start a fresh general-purpose subagent. Where the subagent tool takes a model, give it `opus`. Its
   prompt is this text, with each `{…}` field filled in:

   ```text
   Read {brief} and follow it to write a branch explainer.
   BASE: {base}
   HEAD: {head}
   Branch: {branch}
   Repository: {repo}
   Plan branch: {plan_branch}
   Output: {output}
   ```

   - `{brief}`: the absolute path of `references/branch-explainer-prompt.md` in this skill's folder.
   - `{base}` and `{head}`: the full shas from item 2.
   - `{branch}`: the branch name, or `detached HEAD`.
   - `{repo}`: WORKTREE_PATH from Step 2, never MAIN_ROOT.
   - `{plan_branch}`: `yes` or `no`, from item 3 or 4.
   - `{output}`: the path from item 5.

7. **Report.** Wait for the subagent. It returns the path and a word count. Give your partner one line,
   `Explainer (<N> words): <path>`. Where your runtime can show your partner a file, show it too. Then go to Step 4
   and show its menu as written.

8. **Failure.** If the subagent could not write the file, or it failed, say so in one line with its reason. Then go
   to Step 4. Do not retry it, and do not put an explainer in the conversation.

9. **No subagent tool.** Follow the brief yourself, with the same values. Then report as in item 7.

10. **Later fixes.** Step 4b's fixes do not run the explainer again. It covers HEAD as it was at Step 3b.
