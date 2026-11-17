'''Build the cc-guide stamp-line micro-test prompt.

Usage, from the repository root:
  python3 <kit>/build_prompts.py <sha> <out-dir>
Puts .claude/skills/cc-guide/SKILL.md's body at <sha>, whole, into the frame of cases.py, with
the frozen session after it. Skill text is read with git show. A <sha> of WORKTREE reads the
working-tree file, for a GREEN run before its commit; the body's sha256 then ties the prompt to
the committed text. Writes prompt.txt and MANIFEST.txt with the sha, the body's sha256 and length,
and the prompt's sha256.
'''
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

SKILL = '.claude/skills/cc-guide/SKILL.md'


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def body_at(sha: str) -> str:
    if sha == 'WORKTREE':
        text = Path(SKILL).read_text()
    else:
        text = subprocess.run(['git', 'show', f'{sha}:{SKILL}'], check=True, capture_output=True,
                              text=True).stdout
    if not text.startswith('---\n'):
        raise SystemExit('SKILL.md has no frontmatter')
    end = text.index('\n---\n', 4)
    return text[end + len('\n---\n'):]


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    sha, out_dir = sys.argv[1], Path(sys.argv[2])
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    body = body_at(sha)
    for name in ('release-notes', 'style-checker'):
        if name in body:
            raise SystemExit(f'refusing: the skill body names the fixture file {name}')
    text = cases.FRAME.format(body=body.strip('\n'), conversation=cases.CONVERSATION)
    out_dir.mkdir(parents=True)
    (out_dir / 'prompt.txt').write_text(text)
    notes = [f'sha {sha}', f'body sha256 {sha256(body)}', f'body chars {len(body)}',
             f'prompt.txt sha256 {sha256(text)}']
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {out_dir}/prompt.txt')


if __name__ == '__main__':
    main()
