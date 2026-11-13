'''Build the report-source-match micro-test prompt.

Usage, from the repository root:
  python3 <kit>/build_prompts.py <sha> <variant> <out-dir>
Puts validate-data's SKILL.md body at <sha>, whole, into the frame of cases.py, with the frozen
session of <variant> (a key of cases.VARIANTS) after it. Skill text is read with git show, never
through ~/.claude/skills. Writes prompt.txt and MANIFEST.txt with the sha, the variant, the body's
sha256 and length, and the prompt's sha256. A <sha> of WORKTREE reads the working-tree file, for a
GREEN run before its commit; the body's sha256 then ties the prompt to the committed text.
Before writing, checks that the fixture's numbers say what cases.py's docstring says they do.
'''
import csv
import hashlib
import io
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

SKILL = 'skills/validate-data/SKILL.md'


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


def rows(name: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(cases.FILES[name])))


def check_fixture() -> None:
    final, draft = rows('summary_by_district.csv'), rows('summary_by_district_draft.csv')
    for table in (final, draft):
        for r in table:
            pct = round((int(r['rides_2026q3']) / int(r['rides_2025q3']) - 1) * 100, 1)
            assert pct == float(r['pct_change']), r
    prev = sum(int(r['rides_2025q3']) for r in final)
    curr = sum(int(r['rides_2026q3']) for r in final)
    curr_draft = sum(int(r['rides_2026q3']) for r in draft)
    assert (prev, curr) == (300_000, 317_446)
    assert round((curr / prev - 1) * 100, 1) == 5.8
    assert round((curr_draft / prev - 1) * 100, 1) == 6.4
    weekly = rows('weekly.csv')
    assert sum(int(r['rides']) for r in weekly) == curr
    peak = max(weekly, key=lambda r: int(r['rides']))
    assert (peak['week'], peak['rides']) == ('31', '26900')
    for r in final:
        cell = f"| {r['district']} | {int(r['rides_2025q3']):,} | {int(r['rides_2026q3']):,} | {r['pct_change']} |"
        assert cell in cases.FILES['report.md'], cell
    stale_report = cases.STALE_FILES['report.md']
    assert 'rose 5.8%' in stale_report and 'at 12.4%' in stale_report, 'stale report keeps M1 or M2'
    assert 'draft' not in cases.STALE_FILES['make_figures.py'], 'stale make_figures.py keeps M3'
    assert 'draft' not in cases.STALE_OPENING, 'stale listing names the draft CSV'


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    sha, variant, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    if variant not in cases.VARIANTS:
        raise SystemExit(f'refusing: no variant {variant!r}')
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    check_fixture()
    body = body_at(sha)
    text = cases.FRAME.format(body=body.strip('\n'), conversation=cases.conversation(variant))
    out_dir.mkdir(parents=True)
    (out_dir / 'prompt.txt').write_text(text)
    notes = [f'sha {sha}', f'variant {variant}', f'body sha256 {sha256(body)}', f'body chars {len(body)}',
             f'prompt.txt sha256 {sha256(text)}']
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {out_dir}/prompt.txt')


if __name__ == '__main__':
    main()
