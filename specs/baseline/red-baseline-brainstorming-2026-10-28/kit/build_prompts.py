'''Build plan 70's micro-test prompts.

Usage, from the repository root:
  uv run --with pyyaml python <kit>/build_prompts.py <arm> <sha> <out-dir> [<neighbor-sha>]
<arm> is control (no skill text; pass - as <sha>), skill (brainstorming's body at <sha>),
trigger (brainstorming's description at <sha>, the neighbors' at <neighbor-sha>, which
defaults to <sha>) or smoke. Skill text is read with git show, never through
~/.claude/skills. Writes one <id>.txt per prompt and MANIFEST.txt with each prompt's
sha256, and the skill text's.
'''
import hashlib
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402


def show(sha: str, path: str) -> str:
    return subprocess.run(['git', 'show', f'{sha}:{path}'], check=True, capture_output=True,
                          text=True).stdout


def split_skill(text: str) -> tuple[dict, str]:
    if not text.startswith('---\n'):
        raise SystemExit('SKILL.md has no frontmatter')
    end = text.index('\n---\n', 4)
    return yaml.safe_load(text[4:end]), text[end + len('\n---\n'):].strip('\n')


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def build(arm: str, sha: str, neighbor_sha: str) -> tuple[dict[str, str], list[str]]:
    notes = [f'arm {arm}', f'sha {sha}']
    if arm == 'smoke':
        return {'smoke': cases.SMOKE}, notes
    if arm == 'trigger':
        notes.append(f'neighbor sha {neighbor_sha}')
        lines = []
        for name in sorted(('brainstorming', *cases.NEIGHBORS)):
            fm, _ = split_skill(show(sha if name == 'brainstorming' else neighbor_sha,
                                     f'skills/{name}/SKILL.md'))
            lines.append(f"- {name}: {' '.join(str(fm['description']).split())}")
        listing = '\n'.join(lines)
        notes.append(f'listing sha256 {sha256(listing)}')
        return {key: cases.TRIGGER_FRAME.format(listing=listing, request=request)
                for key, request in cases.TRIGGER_REQUESTS.items()}, notes
    if arm not in ('control', 'skill'):
        raise SystemExit(f'unknown arm {arm!r}')
    block = ''
    if arm == 'skill':
        raw = show(sha, 'skills/brainstorming/SKILL.md')
        _, body = split_skill(raw)
        notes += [f'SKILL.md sha256 {sha256(raw)}', f'body sha256 {sha256(body)}']
    out = {}
    for key, case in cases.CASES.items():
        if arm == 'skill':
            block = cases.SKILL_BLOCK.format(how=cases.HOW_LOADED[case['how']], body=body)
        out[key] = cases.FRAME.format(skill_block=block, conversation=case['conversation'].strip())
    return out, notes


def main() -> None:
    arm, sha, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    neighbor_sha = sys.argv[4] if len(sys.argv) > 4 else sha
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    built, notes = build(arm, sha, neighbor_sha)
    out_dir.mkdir(parents=True)
    for key, text in built.items():
        (out_dir / f'{key}.txt').write_text(text)
        notes.append(f'{key}.txt sha256 {sha256(text)}')
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(built)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
