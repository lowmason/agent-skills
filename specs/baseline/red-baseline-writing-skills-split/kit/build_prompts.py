'''Build plan 72's micro-test prompts.

Usage, from the repository root:
  python3 <kit>/build_prompts.py <sha> <out-dir> [<case> ...]
Puts writing-skills' SKILL.md body at <sha>, whole, into every prompt. With no case
named, builds every case. Skill text is read with git show, never through
~/.claude/skills. Writes one <case>.txt per prompt and MANIFEST.txt with each prompt's
sha256 and the body's.
'''
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

SKILL = 'skills/writing-skills/SKILL.md'


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def body_at(sha: str) -> str:
    text = subprocess.run(['git', 'show', f'{sha}:{SKILL}'], check=True, capture_output=True,
                          text=True).stdout
    if not text.startswith('---\n'):
        raise SystemExit('SKILL.md has no frontmatter')
    end = text.index('\n---\n', 4)
    return text[end + len('\n---\n'):]


def main() -> None:
    sha, out_dir = sys.argv[1], Path(sys.argv[2])
    keys = sys.argv[3:] or sorted(cases.CASES)
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    body = body_at(sha)
    notes = [f'sha {sha}', f'body sha256 {sha256(body)}', f'body chars {len(body)}']
    out_dir.mkdir(parents=True)
    for key in keys:
        text = cases.FRAME.format(body=body.strip('\n'), conversation=cases.CASES[key].strip())
        (out_dir / f'{key}.txt').write_text(text)
        notes.append(f'{key}.txt sha256 {sha256(text)}')
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(keys)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
