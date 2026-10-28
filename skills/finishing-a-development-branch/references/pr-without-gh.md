# Opening a PR without `gh`

Option 2 of finishing-a-development-branch pushes first, then opens the PR with `gh`. Where
`gh` is not installed, derive the PR URL from the remote and hand it to your partner.

On GitHub-family hosts the PR form lives at
`<web-root>/compare/<base>...<branch>?expand=1`. Derive `<web-root>` from the remote:

```bash
git remote get-url origin \
  | sed -e 's|^git@\([^:]*\):|https://\1/|' -e 's|^ssh://git@|https://|' -e 's|\.git$||'
```

Report the push, and never a PR you did not open:

```
Pushed <feature-branch> to origin. `gh` isn't installed here, so I can't open
the PR from the command line — open it in the browser:

<web-root>/compare/<base-branch>...<feature-branch>?expand=1
```
