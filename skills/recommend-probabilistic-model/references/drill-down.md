# Drill-down — handling the long tail

The `decision-map.md` router + `families/*.md` cover the common cases with no PDF access. When a
problem falls **outside** the deep families (reinforcement learning, deep generative models, exotic
kernels, nonparametric Bayes, optimization internals, causal inference, etc.), use this procedure to
navigate the books and pyprobml directly and produce a *verified* recommendation.

This is the only runtime branch that touches the PDFs, and it is the exception, not the rule. The
local PDFs are **optional**: if they are absent, fall back to pyprobml + the public book site.

## Source access (the C2 finding)

| Source | How to read it |
|--------|----------------|
| **Book 1** (`prob_ml_1-book.pdf`, 88 MB) | The Read tool works directly (pass `pages:`), or `pdftotext -f N -l M`. |
| **Book 2** (`prob_ml_book.pdf`, 144 MB) | **Read tool fails** (>100 MB text cap). Use `pdftotext -f N -l M prob_ml_book.pdf -` for text; `pdftoppm -png -f N -l M -r 120 prob_ml_book.pdf /tmp/pg` for figures/equations. |
| **Ruled out** | Splitting Book 2 with `pdfseparate`+`pdfunite` — it duplicates shared fonts/images per page and produces a file *larger* than the source (180 MB from 20 pages). Do not. |

Local PDF directory (if present): `~/Documents/Bayesian/Probabilistic Machine Learning/`.

## Procedure

1. **Classify** the problem (task type + the question), as in SKILL.md Step 1.
2. **Locate the topic in the books.** Find the section by name:
   ```bash
   PDF1="$HOME/Documents/Bayesian/Probabilistic Machine Learning/prob_ml_1-book.pdf"
   PDF2="$HOME/Documents/Bayesian/Probabilistic Machine Learning/prob_ml_book.pdf"
   # Search Book 2's table of contents (front matter) for the topic:
   pdftotext -f 5 -l 35 "$PDF2" - | grep -iE "reinforcement|policy|bandit"
   # Then read the section's body by page range (book page ≈ PDF page; widen if needed):
   pdftotext -f <p> -l <p+8> "$PDF2" -
   ```
   Murphy's books cover the standard treatment in Book 1 and the advanced/extended treatment in
   Book 2 (C3) — check both when the topic spans them.
3. **Find runnable code in pyprobml.** Notebooks are flat under `notebooks/book1/` and
   `notebooks/book2/` (master branch), with descriptive names — paths do **not** follow chapter
   numbers, so list and grep rather than construct:
   ```bash
   gh api 'repos/probml/pyprobml/git/trees/master?recursive=1' \
     | python3 -c "import sys,json;[print(t['path']) for t in json.load(sys.stdin)['tree'] if t['path'].endswith('.ipynb')]" \
     | grep -iE "reinforce|policy|bandit"
   ```
4. **Synthesize** the recommendation into the `reporting.md` template.
5. **Cite carefully and verify (C1).** Record the exact §number + title and the pyprobml path, and
   **read the cited section** to confirm it supports the claim (Gate B by hand). Append a
   *verification date* to the citation — books and notebooks drift over time.

## Worked example — reinforcement learning (route-only)

> Problem: "sequential decisions under uncertainty; reward signal; no labeled targets."
>
> 1. Classify: decision / sequential-decision task.
> 2. `pdftotext -f 5 -l 35 "$PDF2" - | grep -iE "reinforcement|decision making|bandit"` → find the
>    RL / decision-making chapter §numbers in Book 2's contents.
> 3. `… | grep -iE "reinforce|bandit|policy_gradient"` over the pyprobml listing → candidate notebooks.
> 4. Read the located sections; confirm they cover the specific sub-problem (e.g. contextual bandits
>    vs. full RL).
> 5. Write `recommendation.md`; cite `PML2 §<verified> — <title>` + the notebook; note the
>    verification date and that this routed via drill-down (no curated family file).

## If the PDFs are absent

Fall back to the public materials: the book site (`probml.github.io/pml-book`) for chapter/section
structure and the pyprobml repo (`gh api`) for notebooks. You can still produce a recommendation;
mark citations as "unverified against local source" so the user knows to confirm.
