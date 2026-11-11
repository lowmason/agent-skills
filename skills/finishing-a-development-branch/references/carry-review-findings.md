# Carrying review findings

Step 4b of the skill sends you here when you left a finding or a Declined to judge line unfixed.

**If you left any finding or Declined to judge line unfixed,** ask your partner
which of them to carry, and offer to record each one they carry in
`specs/deferred_items.md`. On their yes:

- Append one item per carried finding, in the **Deferred-item schema** of
  [deferred-backlog.md](../../writing-plans/references/deferred-backlog.md): the file paths, the
  finding and why it is carried, what fixing it would take, a `Size:`, and a
  `Done when:` or `Revisit if:`. Write each as an unticked `- [ ]` line at
  column 0, which `deferred_stats.py` counts. A finding with no closure condition is not
  deferrable: tell your partner, and fix or drop it.
- Put the items under a new section at the end of the file,
  `## <name> Step 4b review — <YYYY-MM-DD>`, with an em dash, so the backlog
  stats can date it. `<name>` is the executed plan's file name without `.md`,
  or the branch name when no plan ran. If the file is missing, create it with
  a single `# Deferred items` title line first.
- Commit the edit on the branch before the work leaves it: before Option 1 leaves
  the worktree or your partner merges, and before the push (Option 2; Option 1
  on a detached HEAD), so the record ships with the work. The commit changes only `specs/`,
  so a `Codex reviewed <sha>` line stays current: do not re-run the review for
  it.

Record only the findings your partner carries.
