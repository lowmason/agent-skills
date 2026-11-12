'''Build plan 92's micro-test prompts.

Usage, from the repository root:
  python3 <kit>/build_prompts.py <sha> <layout> <out-dir> [<prompt> ...]
<layout> is base or new. Puts writing-skills' SKILL.md body at <sha>, whole, into every
prompt. After the conversation, each prompt holds the text of the files that cases.PROMPTS
lists for <layout>, each as a file the agent read earlier in the turn. With no prompt named,
builds every key in cases.PROMPTS that has a file list for <layout>. Skill text is read with
git show, never through ~/.claude/skills. Writes one <key>.txt per prompt and MANIFEST.txt
with the sha, the layout, the body's and each read file's sha256 and length, and each
prompt's sha256.
'''
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

SKILL = 'skills/writing-skills/SKILL.md'
SKILL_DIR = 'skills/writing-skills'
LAYOUTS = ('base', 'new')


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def body_at(sha: str) -> str:
    text = subprocess.run(['git', 'show', f'{sha}:{SKILL}'], check=True, capture_output=True,
                          text=True).stdout
    if not text.startswith('---\n'):
        raise SystemExit('SKILL.md has no frontmatter')
    end = text.index('\n---\n', 4)
    return text[end + len('\n---\n'):]


def file_at(sha: str, path: str) -> str:
    result = subprocess.run(['git', 'show', f'{sha}:{SKILL_DIR}/{path}'], capture_output=True,
                            text=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or f'git show failed for {path} at {sha}')
    return result.stdout


def main() -> None:
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    sha, layout, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    if layout not in LAYOUTS:
        raise SystemExit(f'refusing: layout {layout!r} is not base or new')
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    named = sys.argv[4:]
    for key in named:
        if key not in cases.PROMPTS:
            raise SystemExit(f'refusing: no prompt {key}')
        if layout not in cases.PROMPTS[key][1]:
            raise SystemExit(f'refusing: prompt {key} has no file list for layout {layout}')
    keys = named or [k for k, (_, layouts) in cases.PROMPTS.items() if layout in layouts]
    body = body_at(sha)
    texts = {}
    for key in keys:
        for path in cases.PROMPTS[key][1][layout]:
            if path not in texts:
                texts[path] = file_at(sha, path)
    notes = [f'sha {sha}', f'layout {layout}', f'body sha256 {sha256(body)}',
             f'body chars {len(body)}']
    notes += [f'file {path} sha256 {sha256(text)} chars {len(text)}' for path, text in texts.items()]
    out_dir.mkdir(parents=True)
    for key in keys:
        conv, layouts = cases.PROMPTS[key]
        text = cases.FRAME.format(
            body=body.strip('\n'),
            conversation=cases.CONVERSATIONS[conv].strip() + ''.join(
                '\n\n' + cases.READ.format(path=p, text=texts[p].strip('\n')) for p in layouts[layout]))
        (out_dir / f'{key}.txt').write_text(text)
        notes.append(f'{key}.txt sha256 {sha256(text)}')
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(keys)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
