# Fact-checker: a handoff brief

A sender wrote a handoff brief for a fresh session, and wants it checked
before it goes out. Read the brief at [BRIEF_PATH], and the repository it
names. Change nothing: this review is read-only.

Check every claim the brief makes about the repository or the artifact it
hands off: paths, `path:line` references, section and requirement numbers,
ids, commits, and quoted phrases. Open each source and compare. A claim can be
true to the letter and still mislead; say so when it does.

Report each problem as one block, numbered from 0:

```
--- [n] wrong | misleading | missing | nit
DRAFT: <the brief's text, verbatim>
PROBLEM: <what is wrong, in one or two sentences>
SUGGEST: <replacement text>
EVIDENCE: <path:line, or the command you ran, and what it showed>
```

A `missing` finding is a fact the receiver needs and the brief omits; its
DRAFT is the passage the fact belongs in. After the blocks, list what you
checked and found correct:

```
VERIFIED OK:
- <claim> — <evidence>
```
