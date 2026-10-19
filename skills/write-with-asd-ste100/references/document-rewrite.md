# Rewrite a document

Use this procedure when a request names a file to rewrite.

1. Read the file that the request names.
2. If the file is a skill (`SKILL.md`), a subagent definition or a slash-command file, stop. A rewrite of it is a skill edit, so hand off to the writing-skills skill. If that skill is not available, say why you did not rewrite the file.
3. Choose the target.
   - Rewrite the file in place when it is not a symbolic link, git tracks it and it has no uncommitted edits. Run all three commands. The first two must succeed, and the third must print nothing.

     ```bash
     test ! -L <path>
     git ls-files --error-unmatch <path>
     git status --porcelain -- <path>
     ```

   - In every other case, outside a git repository too, write `<stem>.ste<ext>` beside the file: `setup.ste.md` beside `setup.md`. If that file exists, stop and ask.
4. Run the linter on the original, and keep its counts:

   ```bash
   python3 <this-skill-dir>/scripts/ste-lint.py --json <path>
   ```

5. Rewrite the file section by section, under the meaning rules in SKILL.md. Keep these parts unchanged: the frontmatter, fenced and inline code, URLs and link targets, quoted text and the table structure. Keep the headings too, unless the request asks to change them. The prose inside a table cell may change.
6. Run the linter on the result.
7. Reply with a short summary: the path that you wrote, the audience and rule set, the linter counts before and after, and any `Kept as-is:` notes. Never commit. In place, `git diff` shows the change and `git restore <path>` undoes it.
