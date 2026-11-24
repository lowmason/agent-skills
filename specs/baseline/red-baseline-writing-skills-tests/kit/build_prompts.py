'''Build plan 107's case prompts, M1, T2 and R3, and their MANIFEST.txt.

Copy of plan 105's build_prompts.py (specs/baseline/red-baseline-writing-skills-layout/kit/build_prompts.py),
with plan 107's cases and no W prompt.

Usage, from the repository root:
  uv run python <kit>/build_prompts.py <ref> <arm> <out-dir>
<arm> is old, new or pilot. The skill text is writing-skills' SKILL.md body at <ref>, read with git show
from the repository (WST_REPO, or else the one that holds this kit), never through ~/.claude/skills. A prompt
is cases.FRAME_T, with the skill copy's folder, <root>/writing-skills, as the base directory and the case's
tools (cases.TOOLS_TEXT). <root> is WST_SKILL_ROOT (default /private/tmp/wst107-skill), where
`rep_tools.py place-copy <ref>` puts the copy.

Refuses an <out-dir> that exists, an unknown arm and a ref that names no commit. Everything is read before
anything is written. Writes one <case>.txt for each case and MANIFEST.txt: `ref <full sha>`, `arm <arm>`,
`body-sha256 <hex>`, `body-chars <n>`, `skill-copy-root <root>`, one `skill-copy <rel> <sha256>
skills/<rel>@<sha>` line for each file of `git archive <sha> skills/writing-skills` (the bytes
place-copy writes), and one `prompt <name> <sha256>` line for each prompt. run_tool_reps.sh checks the
copy and the prompt against it before each rep (rep_tools.py check-copy).
'''
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402
import rep_tools  # noqa: E402

ARMS = ('old', 'new', 'pilot')
SKILL_MD = 'skills/writing-skills/SKILL.md'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def body_at(sha: str) -> str:
    '''SKILL.md's body at sha, after its frontmatter, as plan 72's build_prompts.py cuts it.'''
    shown = subprocess.run(['git', '-C', str(rep_tools.repo_root()), 'show', f'{sha}:{SKILL_MD}'],
                           capture_output=True, text=True)
    if shown.returncode != 0:
        raise SystemExit(f'refusing: no {SKILL_MD} at {sha}')
    text = shown.stdout
    if not text.startswith('---\n'):
        raise SystemExit('refusing: SKILL.md has no frontmatter')
    end = text.index('\n---\n', 4)
    return text[end + len('\n---\n'):]


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    ref, arm, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    if arm not in ARMS:
        raise SystemExit(f'refusing: arm {arm!r} is not old, new or pilot')
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    sha = rep_tools.resolve(ref)
    body = body_at(sha)
    root = rep_tools.skill_root()
    text = body.strip('\n')
    prompts = {case: cases.FRAME_T.format(base=f'{root}/writing-skills', body=text, tools=cases.TOOLS_TEXT[case],
                                          conversation=cases.CASES[case].strip())
               for case in sorted(cases.CASES)}
    files = rep_tools.archive_files(sha)
    notes = [f'ref {sha}', f'arm {arm}', f'body-sha256 {sha256(body.encode())}', f'body-chars {len(body)}',
             f'skill-copy-root {root}']
    notes += [f'skill-copy {rel} {sha256(data)} skills/{rel}@{sha}' for rel, (data, _) in sorted(files.items())]
    out_dir.mkdir(parents=True)
    for case, prompt in prompts.items():
        (out_dir / f'{case}.txt').write_text(prompt)
        notes.append(f'prompt {case}.txt {sha256(prompt.encode())}')
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(prompts)} prompts for {arm} at {sha} to {out_dir}')


if __name__ == '__main__':
    main()
