# Write a branch explainer

You write one explainer of a finished branch for the repository's owner. The owner wrote the project and approved
the plan, but did not follow the build. After about ten minutes of reading, the owner must be able to say, in their
own words, what the plan set out to do and why, how it was built, and what it adds to the project.

## The values you get

- `BASE` and `HEAD`: commit shas. The branch is the range `BASE..HEAD`.
- `Branch`: the branch name.
- `Repository`: the repository folder. Run every git command there.
- `Plan branch`: `yes` when the range moves a plan into `specs/plans/completed/`. `no` when the branch has no plan.
- `Output`: the path of the file you write.

## Inputs

Read only files inside the Repository folder, and this brief. Read in this order:

1. `git diff --stat BASE..HEAD` first, then `git log --format='%h %s' BASE..HEAD`. Then read the diff, file by file.
   Skim probe records, test outputs and generated files: read their names and a sample, not every line.
2. The entry that the range adds to `specs/history.md`. Its second line names the plan and the spec. Its rulings and
   deviations list the calls that the build made without the owner.
3. The plan and the spec, for the background and the intent. If the entry reads `Spec: none`, the plan alone gives
   the intent.
4. The project map: the README, `CLAUDE.md` or `AGENTS.md`, any live `specs/*-roadmap.md`, and earlier entries in
   `specs/history.md`.
5. The code around the change, as far as the explanation needs it.

With `Plan branch: no`, there is no entry, plan or spec. The diff, the commit log and the project map are your only
inputs, and the plan part says what the commits show the work set out to do.

The diff says what was done. The spec says what was meant. Where the two differ, say so, and cite the entry's ruling
or deviation that explains the difference.

## Check before you state

Every claim must match the branch at `HEAD`, the Synopsis included.

- Take each number from a command that you ran or a file that you read: a count of files, tests, rulings or
  deviations, a line total, a size, a version. For one file's added and removed lines, run
  `git diff --numstat BASE..HEAD -- <file>`. If you did not check a number, leave it out.
- Take names, limits and quoted words from the files as they are at `HEAD`. When a later commit of the branch changes
  what an earlier commit did, describe the later state. The entry's rulings and deviations show what changed late.

## Layout

Use these headings, exactly, in this order:

1. `# <title>`: one line that names the branch and its plan.
2. `## Synopsis`: three short paragraphs, labeled `**The plan:**`, `**The build:**` and `**The project:**`.
   - The plan: what the work set out to do, and why.
   - The build: the main parts, in the order that they depend on each other.
   - The project: what the branch adds to the project as a whole.
3. `## Background`: the parts of the project that the change touches, as they worked before the branch, and the gap
   that the plan set out to close. Keep it narrow. Give no tutorial: the owner wrote the project.
4. `## The change`: the parts of the build, in dependency order, so that no part comes before a part it needs. For
   each part, say what it is, why it is there, and what depends on it. Each claim about code names the file, and the
   line where that helps, so that the owner can check it.
5. `## What it adds to the project`: how the project's flows or abilities change, which other parts now depend on the
   branch, and what it leaves for later (the deferred items that it adds).
6. `## Questions`: three questions, one for each Synopsis part. What did the plan set out to do, and why? How was it
   built? What does it add to the project? The owner answers in their own words, then compares the answers with the
   Synopsis.

## Limits

- The Synopsis has at most 250 words.
- The whole explainer has at most 2,000 words.
- A word is a whitespace-separated token with at least one letter or digit, code included. `wc -w` counts a few more
  tokens than that, so a count from `wc -w` that is within a limit is within it.

## Style

Write Markdown in plain technical English. Use short sentences, one idea in each, and the active voice. Use one name
for each thing. Do not use semicolons. Write for the person who wrote the project: no tutorial for beginners.

## Output

Create the output's folder if it does not exist. Write the explainer to the `Output` path, and overwrite any file
that is there. Then reply with the path and the word count, and nothing else. If the write is refused, reply with the
refusal and its reason, and write the explainer nowhere else.
