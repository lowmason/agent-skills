#!/bin/bash
# Build one plan 73 F1 scratch repository: the fixture, plus the skills and agents at <sha> as
# project files, with skills/writing-plans replaced by <writing-plans-dir>.
# Usage, from the repository root: make_scratch.sh <writing-plans-dir> <sha> <dest>
set -eu
ARM="$(cd "$1" && pwd)"
SHA="$2"
DEST="$3"
F1="$(cd "$(dirname "$0")" && pwd)"
[ -e "$DEST" ] && { echo "refusing: $DEST exists"; exit 2; }
mkdir -p "$DEST"
DEST="$(cd "$DEST" && pwd)"
if (cd "$DEST" && git rev-parse --show-toplevel > /dev/null 2>&1); then
  echo "refusing: $DEST is inside a git repository"; exit 2
fi
mkdir -p "$DEST/.claude/agents" "$DEST/specs"
for s in subagent-driven-development requesting-code-review receiving-code-review test-driven-development \
         verification-before-completion executing-plans finishing-a-development-branch using-git-worktrees \
         systematic-debugging; do
  git archive "$SHA" "skills/$s" | tar -x -C "$DEST/.claude"
done
cp -R "$ARM" "$DEST/.claude/skills/writing-plans"
for a in code-reviewer task-reviewer; do git show "$SHA:agents/$a.md" > "$DEST/.claude/agents/$a.md"; done
cp "$F1/fixture/expense-tally.md" "$DEST/specs/expense-tally.md"
cp "$F1/fixture/CLAUDE.md" "$DEST/CLAUDE.md"
git -C "$DEST" init -q -b main
git -C "$DEST" add -A
git -C "$DEST" -c user.name='Plan 73 F1' -c user.email='f1@example.invalid' commit -q -m 'Scratch repository for plan 73 F1'
echo "built $DEST"
