'''Build plan 93's reviewer micro-test packages R1, R2 and R3.

Usage, from the repository root:
  uv run python <kit>/build_packages.py <out-dir>

A package is the seven files a task reviewer reads for one task: the brief, the implementer's
report, the controller's test run, the review package (the diff), the spec excerpts, the mutants
file and the controller's mutant run. Each package is made the way a real run makes it, with this
worktree's scripts (skills/subagent-driven-development/scripts/):

1. A new git repository under /tmp, outside every other repository, holds F3's fixture
   (../impl-kit/fixtures/F3/repo/). Its first commit is the base.
2. task-brief writes the brief from plan.md, Task 1. The excerpts file is F3's spec.md.
3. As the implementer: the plan test fails (RED), a correct count_words makes it pass (GREEN), and
   both go into commit 1. The tests for each input shape go into commit 2. The patches and the
   mutants file go into the workspace. mutant-run runs. For R3, mutant 4 survives that run. Its
   patch is renamed .withdrawn, its Withdrawn line is added, and mutant-run runs again.
4. The implementer's report, written from the runs' real output.
5. As the controller: test-run on the brief's focused command and the documented suite, then
   mutant-run on the focused command, then review-package from the base to HEAD.

Each commit has a fixed author, committer and date, so a rebuild makes the same shas. The seven
files are copied into <out-dir>/R<n>/ with the scratch repository's path written as /work/notes
(cases.REPO). <out-dir>/MANIFEST.txt gives each file's sha256, the base and head of each package,
and the sha256 of each script used. The scratch repositories stay under /tmp for a hand check,
and the script prints their paths.

Refuses an existing <out-dir>. Stops when a step does not give the result the package needs: a
script's exit status, a mutant's verdict, a test count. Stops when a copied file still names the
scratch path, /Users/, $HOME, $TMPDIR or the OS user name.
'''
import getpass
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = ROOT / 'skills/subagent-driven-development/scripts'
SCRIPT_NAMES = ('sdd-repo', 'sdd-workspace', 'task-brief', 'test-run', 'mutant-run', 'review-package')
F3 = Path(__file__).resolve().parents[1] / 'impl-kit/fixtures/F3'
DATES = ('2026-11-02T09:00:00+0000', '2026-11-02T09:20:00+0000', '2026-11-02T09:40:00+0000')

CODE = '''def count_words(text: str) -> int:
    total = 0
    for line in text.split('\\n'):
        if line.lstrip().startswith('#'):
            continue
        total += len(line.split())
    return total
'''
COMMENT_CHECK = "        if line.lstrip().startswith('#'):\n            continue\n"

# Each wrong version is CODE with one edit, as (old, new).
EDITS = {
    'single-spaces': ('len(line.split())', "len(line.split(' '))"),
    'no-skip': (COMMENT_CHECK, ''),
    'hash-anywhere': ("if line.lstrip().startswith('#'):", "if '#' in line:"),
    'return-0': ('def count_words(text: str) -> int:\n', 'def count_words(text: str) -> int:\n    return 0\n'),
    'spaces-only': ("line.lstrip().startswith('#')", "line.lstrip(' ').startswith('#')"),
}

PLAN_TEST = r'''from wordcount import count_words


def test_count_words_skips_comment_lines():
    assert count_words('# note\nhello world\n') == 2
'''
TAB_TEST = 'test_count_words_skips_a_comment_after_a_tab_or_other_blank'
# NEL, LS and PS are whitespace to str.split() and line ends to str.splitlines(). NBSP and
# IDEOGRAPHIC_SPACE are whitespace to str.split().
NEL, LS, PS = '\x85', chr(0x2028), chr(0x2029)
NBSP, IDEOGRAPHIC_SPACE = '\xa0', chr(0x3000)
# The tests that commit 2 adds, in file order, as {name: ((input, expected), ...)}. Each input is
# written into the test file with repr(), so every escape stays visible.
ADDED_TESTS = {
    'test_count_words_skips_a_comment_after_spaces': (('   # note\nhello\n', 1),),
    TAB_TEST: (('\t# note\nhello\n', 1), ('\x0c\x0b# note\nhello\n', 1),
               (f'\r\x1c\x1d\x1e{NEL}{LS}{PS}{NBSP}{IDEOGRAPHIC_SPACE}# note\nhello\n', 1)),
    'test_count_words_skips_a_comment_with_no_blank_after_the_hash': (('#note here\nhello\n', 1), ('#\nhello\n', 1)),
    'test_count_words_skips_a_comment_on_the_last_line': (('hello\n# last note', 1),),
    'test_count_words_skips_several_comment_lines': (('# one\n# two\nhello\n', 1), ('# only\n# comments\n', 0)),
    'test_count_words_skips_a_comment_line_that_ends_with_crlf': (('# note\r\nhello\r\n', 1),),
    'test_count_words_skips_a_whole_comment_line_past_other_whitespace': (
        (f'# a\x0bb\x0cc\rd{NEL}e{LS}f\nhello\n', 1),),
    'test_count_words_counts_a_hash_after_a_word': (('hello # world\n', 3),),
    'test_count_words_counts_a_hash_after_other_whitespace_in_a_line': (
        ('hello\x0c# world\n', 3), ('hello\r# world\n', 3), (f'hello{LS}# world\n', 3)),
    'test_count_words_splits_on_any_run_of_whitespace': (('one  two\tthree \t four\n\nfive\r\nsix\n', 6),
                                                         ('well-known a,b end.\n', 3), ('hello  world', 2)),
    'test_count_words_splits_on_other_whitespace_inside_a_line': (
        ('a\x0bb\x0cc\rd\n', 4),
        (f'a\x1cb\x1dc\x1ed{NEL}e{LS}f{PS}g{NBSP}h{IDEOGRAPHIC_SPACE}i\n', 9)),
    'test_count_words_ignores_whitespace_at_the_ends': (('  one two  \n', 2), (f'{IDEOGRAPHIC_SPACE}one two{NEL}\n', 2),
                                                        ('', 0), (' \t\n', 0)),
}

R7 = 'specs/wordcount.md:7'
R8 = 'specs/wordcount.md:8'
# The Inputs table, as (rule, shape, test). R3 leaves out the rows whose test is TAB_TEST.
INPUTS = (
    (R7, '`#` at column 0', 'test_count_words_skips_comment_lines'),
    (R7, 'spaces before `#`', 'test_count_words_skips_a_comment_after_spaces'),
    (R7, 'a tab before `#`', TAB_TEST),
    (R7, 'other whitespace before `#`: a form feed, a vertical tab, a lone `\\r`, `\\x1c` to `\\x1e`, '
         '`\\x85`, `\\u2028`, `\\u2029`, the no-break space `\\u00a0`, the ideographic space `\\u3000`', TAB_TEST),
    (R7, 'no blank after `#`', 'test_count_words_skips_a_comment_with_no_blank_after_the_hash'),
    (R7, 'a line that is only `#`', 'test_count_words_skips_a_comment_with_no_blank_after_the_hash'),
    (R7, 'a comment on the last line, with no newline after it', 'test_count_words_skips_a_comment_on_the_last_line'),
    (R7, 'several comment lines in a row, and text that is only comments', 'test_count_words_skips_several_comment_lines'),
    (R7, 'a comment line that ends with `\\r\\n`', 'test_count_words_skips_a_comment_line_that_ends_with_crlf'),
    (R7, 'other whitespace inside a comment line (a vertical tab, a form feed, a lone `\\r`, `\\x85`, `\\u2028`): '
         'only a newline ends the line', 'test_count_words_skips_a_whole_comment_line_past_other_whitespace'),
    (R7, '`#` after a word, so not the first non-blank character', 'test_count_words_counts_a_hash_after_a_word'),
    (R7, '`#` after a word and a form feed, a lone `\\r` or `\\u2028` in the same line',
     'test_count_words_counts_a_hash_after_other_whitespace_in_a_line'),
    (R8, 'one space', 'test_count_words_skips_comment_lines'),
    (R8, 'a run of spaces', 'test_count_words_splits_on_any_run_of_whitespace'),
    (R8, 'a tab', 'test_count_words_splits_on_any_run_of_whitespace'),
    (R8, 'a run of spaces and tabs', 'test_count_words_splits_on_any_run_of_whitespace'),
    (R8, 'a newline', 'test_count_words_splits_on_any_run_of_whitespace'),
    (R8, 'a blank line, so two newlines in a row', 'test_count_words_splits_on_any_run_of_whitespace'),
    (R8, 'a carriage return before a newline', 'test_count_words_splits_on_any_run_of_whitespace'),
    (R8, 'a last line that holds words, with no newline after it', 'test_count_words_splits_on_any_run_of_whitespace'),
    (R8, 'punctuation with no whitespace (`well-known`, `a,b`): it never separates words',
     'test_count_words_splits_on_any_run_of_whitespace'),
    (R8, 'a vertical tab, a form feed or a lone `\\r` between words: each separates words and never ends a line',
     'test_count_words_splits_on_other_whitespace_inside_a_line'),
    (R8, 'other Unicode whitespace between words (`\\x1c` to `\\x1e`, `\\x85`, `\\u2028`, `\\u2029`, '
         'the no-break space `\\u00a0`, the ideographic space `\\u3000`)',
     'test_count_words_splits_on_other_whitespace_inside_a_line'),
    (R8, 'whitespace at the start and end of a line, Unicode whitespace too (`\\u3000`, `\\x85`)',
     'test_count_words_ignores_whitespace_at_the_ends'),
    (R8, 'empty text, and whitespace only', 'test_count_words_ignores_whitespace_at_the_ends'),
)
WHITESPACE_TESTS = ('test_count_words_splits_on_any_run_of_whitespace',
                    'test_count_words_splits_on_other_whitespace_inside_a_line',
                    'test_count_words_ignores_whitespace_at_the_ends')
COMMENT_TESTS = ('test_count_words_skips_comment_lines', 'test_count_words_skips_a_comment_after_spaces', TAB_TEST,
                 'test_count_words_skips_a_comment_with_no_blank_after_the_hash',
                 'test_count_words_skips_a_comment_on_the_last_line', 'test_count_words_skips_several_comment_lines',
                 'test_count_words_skips_a_comment_line_that_ends_with_crlf',
                 'test_count_words_skips_a_whole_comment_line_past_other_whitespace')
HASH_TESTS = ('test_count_words_counts_a_hash_after_a_word', 'test_count_words_counts_a_hash_after_other_whitespace_in_a_line')

# Each mutant as (number, edit, targets, the wrong version in one line). A target list leaves out
# a test the package does not have.
R1_MUTANTS = (
    (1, 'single-spaces', (R8, *WHITESPACE_TESTS), 'splits each line on single spaces, not on any run of whitespace'),
    (2, 'no-skip', (R7, *COMMENT_TESTS), 'comment lines are not skipped, so their words count'),
    (3, 'hash-anywhere', (R7, *HASH_TESTS), 'a line with `#` anywhere in it is skipped as a comment'),
)
R2_MUTANT_1 = (1, 'return-0', WHITESPACE_TESTS, 'returns 0 at the top of `count_words`')
R3_MUTANT_4 = (4, 'spaces-only', (R7, 'test_count_words_skips_a_comment_after_spaces'),
               'strips only spaces before the `#` check, so a tab before `#` is kept')
R3_WITHDRAWN = 'Withdrawn: 4 — equivalent, no behavior changes'

PACKAGES = {
    'R1': {'tab_test': True, 'mutants': R1_MUTANTS, 'withdraw': None},
    'R2': {'tab_test': True, 'mutants': (R2_MUTANT_1, *R1_MUTANTS[1:]), 'withdraw': None},
    'R3': {'tab_test': False, 'mutants': (*R1_MUTANTS, R3_MUTANT_4), 'withdraw': 4},
}

REPORT = '''# Task 1 report

## What I implemented

`count_words(text: str) -> int` in `wordcount.py`. It splits the text into lines at each newline, skips each line whose first non-blank character is `#`, and counts the words of every other line with `str.split()`. So any run of whitespace separates two words, and only a newline ends a line.

## What I tested

- `{focused}`: {focused_last}
- `{suite}`: {suite_last}

The plan's test is unchanged. I added {added} tests in a second commit. Together they cover each input shape of the two rules that the plan's test does not use, and the Inputs table in the mutants file lists each shape and its test.

## TDD Evidence

- RED: `{focused}`

  ```
{red}
  ```

  The failure was expected: `count_words` did not exist yet.

- GREEN: `{focused}`

  ```
{green}
  ```

## Mutants

{mutants}

## Files changed

- wordcount.py
- tests/test_wordcount.py

## Self-review findings

None.

## Issues or concerns

None.
'''


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(('GIT_', 'PYTEST', 'PYTHON', 'VIRTUAL_ENV', 'UV_'))}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def run(cmd: list[str], cwd: Path, expect: int | None = 0, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env or clean_env())
    if expect is not None and done.returncode != expect:
        raise SystemExit(f'{" ".join(cmd)} exited {done.returncode}, not {expect}:\n{done.stdout}{done.stderr}')
    return done


def git(repo: Path, *args: str, date: str | None = None) -> str:
    env = clean_env()
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    return run(['git', '-C', str(repo), *args], repo, env=env).stdout.strip()


def script(name: str, repo: Path, *args: str, expect: int | None = 0) -> subprocess.CompletedProcess:
    return run([str(SCRIPTS / name), *args], repo, expect=expect)


def tests_text(tab_test: bool) -> str:
    parts = [PLAN_TEST]
    for name, body in ADDED_TESTS.items():
        if name == TAB_TEST and not tab_test:
            continue
        asserts = ''.join(f'    assert count_words({text!r}) == {expected}\n' for text, expected in body)
        parts.append(f'\n\ndef {name}():\n{asserts}')
    return ''.join(parts)


def mutants_text(spec: dict) -> str:
    rows = [f'| {rule} | {shape} | {test} |' for rule, shape, test in INPUTS if spec['tab_test'] or test != TAB_TEST]
    lines = ['# Task 1 mutants', '', '## Inputs', '', '| Rule | Shape | Test |', '|---|---|---|', *rows, '', '## Mutants', '']
    for number, _, targets, wrong in spec['mutants']:
        kept = [t for t in targets if spec['tab_test'] or t != TAB_TEST]
        lines.append(f'Mutant {number}: {", ".join(kept)} — {wrong} — task-1-mutant-{number}.patch')
    if spec['withdraw']:
        lines.append(R3_WITHDRAWN)
    return '\n'.join(lines) + '\n'


def last_line(text: str) -> str:
    return text.strip().splitlines()[-1].strip()


def indent(text: str) -> str:
    return '\n'.join(f'  {line}' if line else '' for line in text.strip('\n').splitlines())


def result_line(out: str) -> str:
    line = next(l for l in out.splitlines() if l.startswith('result: '))
    return line[len('result: '):]


def run_path(out: str) -> Path:
    return Path(out.strip().splitlines()[-1].split('run: ', 1)[1])


def build(name: str, spec: dict, scratch: Path) -> tuple[Path, Path, str, str, list[Path]]:
    repo = scratch / 'notes'
    shutil.copytree(F3 / 'repo', repo)
    git(repo, 'init', '-q', '-b', 'main')
    git(repo, 'config', 'user.name', 'Developer')
    git(repo, 'config', 'user.email', 'developer@example.invalid')
    git(repo, 'config', 'commit.gpgsign', 'false')
    git(repo, 'add', '-A')
    git(repo, 'commit', '-q', '-m', 'Start the project', date=DATES[0])
    base = git(repo, 'rev-parse', 'HEAD')
    workspace = Path(script('sdd-workspace', repo, cases.PLAN_FILE).stdout.strip())
    script('task-brief', repo, cases.PLAN_FILE, '1')
    if (workspace / 'task-1-brief.md').read_bytes() != (F3 / 'brief.md').read_bytes():
        raise SystemExit(f'{name}: task-brief output differs from F3 brief.md')
    shutil.copyfile(F3 / 'spec.md', workspace / 'task-1-spec.md')
    focused = cases.FOCUSED_COMMAND.split()

    # The implementer: RED, GREEN and commit 1; the input shapes and commit 2.
    (repo / 'tests').mkdir()
    (repo / 'tests/test_wordcount.py').write_text(PLAN_TEST)
    red = run(focused, repo, expect=2)
    if "cannot import name 'count_words'" not in red.stdout:
        raise SystemExit(f'{name}: RED is not the expected ImportError:\n{red.stdout}')
    (repo / 'wordcount.py').write_text(CODE)
    green = run(focused, repo)
    git(repo, 'add', 'wordcount.py', 'tests/test_wordcount.py')
    git(repo, 'commit', '-q', '-m', 'Add count_words', date=DATES[1])
    (repo / 'tests/test_wordcount.py').write_text(tests_text(spec['tab_test']))
    git(repo, 'add', 'tests/test_wordcount.py')
    git(repo, 'commit', '-q', '-m', 'Test each input shape of the two rules', date=DATES[2])
    head = git(repo, 'rev-parse', 'HEAD')

    for number, edit, _, _ in spec['mutants']:
        old, new = EDITS[edit]
        if CODE.count(old) != 1:
            raise SystemExit(f'{name}: edit {edit} does not match the code once')
        (repo / 'wordcount.py').write_text(CODE.replace(old, new))
        patch = run(['git', '-C', str(repo), 'diff', '--', 'wordcount.py'], repo).stdout
        if not patch.strip():
            raise SystemExit(f'{name}: mutant {number} made an empty patch')
        (workspace / f'task-1-mutant-{number}.patch').write_text(patch)
        git(repo, 'checkout', '--', 'wordcount.py')
    (workspace / 'task-1-mutants.md').write_text(mutants_text({**spec, 'withdraw': None}))
    impl_runs = [script('mutant-run', repo, cases.PLAN_FILE, '1', '--', *focused, expect=None)]
    if spec['withdraw']:
        number = spec['withdraw']
        verdict = f'mutant {number}: SURVIVED'
        if impl_runs[0].returncode != 1 or verdict not in impl_runs[0].stdout:
            raise SystemExit(f'{name}: mutant {number} did not survive:\n{impl_runs[0].stdout}')
        patch = workspace / f'task-1-mutant-{number}.patch'
        patch.rename(patch.with_name(patch.name + '.withdrawn'))
        (workspace / 'task-1-mutants.md').write_text(mutants_text(spec))
        impl_runs.append(script('mutant-run', repo, cases.PLAN_FILE, '1', '--', *focused, expect=None))
    if impl_runs[-1].returncode != 0:
        raise SystemExit(f'{name}: the implementer\'s last mutant run exited {impl_runs[-1].returncode}')

    # The report, from the real output.
    suite_out = run(cases.SUITE_COMMAND.split(), repo)
    focused_out = run(focused, repo)
    if len(impl_runs) == 1:
        mutants = f'`{run_path(impl_runs[0].stdout)}`: {result_line(impl_runs[0].stdout)}.'
    else:
        first, second = impl_runs
        mutants = (f'Run 1, `{run_path(first.stdout)}`: {result_line(first.stdout)}. Mutant {spec["withdraw"]} survived. '
                   f'It is equivalent, so I withdrew it: the mutants file has its `Withdrawn:` line, and its patch is '
                   f'renamed `task-1-mutant-{spec["withdraw"]}.patch.withdrawn`.\n\n'
                   f'Run 2, `{run_path(second.stdout)}`: {result_line(second.stdout)}.')
    added = sum(1 for test in ADDED_TESTS if spec['tab_test'] or test != TAB_TEST)
    report = REPORT.format(focused=cases.FOCUSED_COMMAND, suite=cases.SUITE_COMMAND,
                           focused_last=last_line(focused_out.stdout), suite_last=last_line(suite_out.stdout),
                           added=added, red=indent('\n'.join(red.stdout.strip().splitlines()[-6:])),
                           green=indent(green.stdout), mutants=mutants)
    (workspace / 'task-1-report.md').write_text(report)

    # The controller: test-run, mutant-run, review-package.
    combined = f'({cases.FOCUSED_COMMAND}) && ({cases.SUITE_COMMAND})'
    test_run = run_path(script('test-run', repo, cases.PLAN_FILE, '1', '--', 'sh', '-c', combined).stdout)
    mutant_run = run_path(script('mutant-run', repo, cases.PLAN_FILE, '1', '--', *focused).stdout)
    wrote = script('review-package', repo, cases.PLAN_FILE, base, head).stdout
    diff = Path(re.match(r'wrote (.+\.diff): ', wrote).group(1))
    files = [workspace / 'task-1-brief.md', workspace / 'task-1-report.md', test_run, diff,
             workspace / 'task-1-spec.md', workspace / 'task-1-mutants.md', mutant_run]
    return repo, workspace, base, head, files


def check_copy(name: str, text: str, scratch: Path) -> None:
    home = str(Path.home())
    tmpdir = os.environ.get('TMPDIR', '').rstrip('/')
    banned = [str(scratch), str(scratch.resolve()), '/Users/', home, getpass.getuser(), '/private/var', '/var/folders']
    if tmpdir:
        banned.append(tmpdir)
    hits = sorted({b for b in banned if b and b in text})
    if hits:
        raise SystemExit(f'{name}: a copied file still names {hits}')


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    out_dir = Path(sys.argv[1])
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    missing = [n for n in SCRIPT_NAMES if not os.access(SCRIPTS / n, os.X_OK)]
    if missing:
        raise SystemExit(f'refusing: no executable {missing} in {SCRIPTS}')
    notes = [f'script {n} sha256 {sha256((SCRIPTS / n).read_bytes())}' for n in SCRIPT_NAMES]
    built = {}
    for name, spec in PACKAGES.items():
        scratch = Path(tempfile.mkdtemp(prefix='mt-review-build-', dir='/tmp')).resolve()
        if run(['git', 'rev-parse', '--show-toplevel'], scratch, expect=None).returncode == 0:
            raise SystemExit(f'refusing: {scratch} is inside a git repository')
        repo, workspace, base, head, files = build(name, spec, scratch)
        copies = {}
        for path in files:
            text = path.read_text().replace(str(repo), cases.REPO).replace(str(repo).replace('/private/tmp/', '/tmp/', 1), cases.REPO)
            check_copy(name, text, scratch)
            copies[path.name] = text
        if len(copies) != 7:
            raise SystemExit(f'{name}: {len(copies)} files, not 7')
        built[name] = (copies, base, head, repo)
    for name, (copies, base, head, repo) in built.items():
        target = out_dir / name
        target.mkdir(parents=True)
        notes.append(f'{name} base {base} head {head}')
        for file_name, text in copies.items():
            (target / file_name).write_text(text)
            notes.append(f'{name}/{file_name} sha256 {sha256(text.encode())}')
    manifest = '\n'.join(notes) + '\n'
    check_copy('MANIFEST.txt', manifest, Path('/tmp/mt-review-build-'))
    (out_dir / 'MANIFEST.txt').write_text(manifest)
    print(f'wrote {len(built)} packages to {out_dir}')
    for name, (_, _, _, repo) in built.items():
        print(f'{name} scratch repository: {repo}')


if __name__ == '__main__':
    main()
