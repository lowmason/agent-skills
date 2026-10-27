'''Re-probe the uv behaviors that specs/package-versions.md relies on, on the uv of the day.

    uv run --no-project python specs/verification/66-uv-probe.py [--keep]

It builds a throwaway tree under the system temp directory, never inside this repository, and
never writes a uv.toml or .python-version into the repository: every sibling worktree under
.claude/worktrees/ would inherit them at once. It needs the network (PyPI). Output is a Markdown
table: one row for each probe, with the spec's expected result, the observed one and PASS, FAIL or RECORD.
Exit status 1 when a probe FAILs, 2 when the setup cannot run.

The probes use polars 2.0.0 (uploaded 2026-10-06) and jax 0.12.0 / 0.12.0.1 (the latter uploaded 2026-10-21),
whose upload times do not change. Design: specs/package-versions.md, Inventory ("uv behavior that constrains
the design"); plan: specs/plans/66-package-versions.md, Task 1.
'''
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

CUT = '2026-10-01T00:00:00Z'      # before polars 2.0.0
LATE = '2026-12-01T00:00:00Z'     # after it
SCRIPT = '''\
# /// script
# requires-python = '>=3.11'
# dependencies = ['polars']
# ///
import importlib.metadata as m
import sys
print(m.version('polars'), '%d.%d' % sys.version_info[:2])
'''
SCRIPT_FLOOR = SCRIPT.replace("dependencies = ['polars']", "dependencies = ['polars>=2.0']").replace(
    "print(m.version('polars'), '%d.%d' % sys.version_info[:2])", "print(m.version('polars'))")
SCRIPT_OWN_DATE = SCRIPT.replace('# ///\nimport', f'# [tool.uv]\n# exclude-newer = "{CUT}"\n# ///\nimport')
PRINT_PY = "import sys; print(sys.version_info[0], sys.version_info[1])"
PRINT_POLARS = "import importlib.metadata as m, sys; print(m.version('polars'), '%d.%d' % sys.version_info[:2])"
rows = []


def sh(args, cwd, env=None, stdin=None):
    merged = {k: v for k, v in os.environ.items() if not k.startswith('UV_')}
    merged.update(env or {})
    if args[0] == 'uv':   # uv reuses a cached environment whose requirements match, whatever the date was
        args = ['uv', '--no-cache', *args[1:]]
    done = subprocess.run(args, cwd=cwd, env=merged, input=stdin, capture_output=True, text=True)
    return done.returncode, done.stdout.strip(), done.stderr.strip()


def polars_of(out):
    return out.split()[0] if out.split() else ''


def major(version):
    return int(version.split('.')[0]) if version[:1].isdigit() else -1


def probe(pid, what, expected, args, cwd, check, env=None, stdin=None, record=False, show=None):
    code, out, err = sh(args, cwd, env, stdin)
    observed = (show(out) if show else out.replace('\n', ' / ')) if code == 0 else f'exit {code}: {err.splitlines()[-1] if err else ""}'
    ok = code == 0 and check(out)
    rows.append((pid, what, expected, observed, 'RECORD' if record else ('PASS' if ok else 'FAIL')))
    return out


def older(out):          # limited by the date: polars below 2.0.0
    return major(polars_of(out)) in range(0, 2)


def newest(out):         # not limited: polars 2.0.0 or later
    return major(polars_of(out)) >= 2


def upload_time(package, version):
    url = f'https://pypi.org/pypi/{package}/{version}/json'
    with urllib.request.urlopen(url, timeout=30) as response:
        files = json.load(response)['urls']
    return min(datetime.datetime.fromisoformat(f['upload_time_iso_8601'].replace('Z', '+00:00')) for f in files)


def build(work):
    repo = work / 'repo'
    for rel in ('build', 'skills/demo/scripts', '.claude/worktrees/wt', '.claude/worktrees/wt2', 'other'):
        (work / 'repo' / rel if rel != 'other' else work / 'other').mkdir(parents=True, exist_ok=True)
    (repo / 'uv.toml').write_text(f'exclude-newer = "{CUT}"\n')
    (repo / '.python-version').write_text('3.13\n')
    (repo / 'skills' / 'uv.toml').write_text('# no settings; this file shadows the root uv.toml\n')
    (repo / '.claude/worktrees/wt2/uv.toml').write_text(f'exclude-newer = "{LATE}"\n')
    for rel in ('build/s.py', 'skills/demo/scripts/s.py'):
        (repo / rel).write_text(SCRIPT)
    (repo / 'build/owndate.py').write_text(SCRIPT_OWN_DATE)
    (work / 'neutral.py').write_text(SCRIPT)
    (work / 'floor.py').write_text(SCRIPT_FLOOR)
    (work / 'link-build').symlink_to(repo / 'build')
    (work / 'link-skills').symlink_to(repo / 'skills')
    return repo


def run_all(work):
    repo, other = build(work), work / 'other'
    build_dir, deep = repo / 'build', repo / 'skills/demo/scripts'
    uv = ['uv', 'run']
    # 1 and 7: the cutoff on --with, and what the date compares with
    probe('P1', 'CLI --exclude-newer limits --with (jax)', 'jax 0.12.0, not 0.12.0.1',
          [*uv, '--python', '3.13', '--exclude-newer', '2026-10-20T00:00:00Z', '--with', 'jax', 'python', '-c',
           "import importlib.metadata as m; print(m.version('jax'))"], other, lambda o: o == '0.12.0')
    t = upload_time('polars', '2.0.0')
    before, after = (t - datetime.timedelta(minutes=1)), (t + datetime.timedelta(minutes=1))
    base = [*uv, '--python', '3.13', '--with', 'polars', 'python', '-c', PRINT_POLARS]
    for pid, stamp, check, expected in (('P7a', before, older, 'polars < 2 (cutoff just before the upload)'),
                                       ('P7b', after, newest, 'polars 2.0.0 (cutoff just after the upload)')):
        probe(pid, f'RFC 3339 cutoff {stamp:%Y-%m-%dT%H:%M:%SZ} is read as written', expected,
              [*uv, '--python', '3.13', '--exclude-newer', f'{stamp:%Y-%m-%dT%H:%M:%SZ}', '--with', 'polars',
               'python', '-c', PRINT_POLARS], other, check)
    for pid, zone in (('P7c', 'UTC'), ('P7d', 'Pacific/Kiritimati')):
        seen = []
        for offset in (-1, 0, 1):
            day = t.date() + datetime.timedelta(days=offset)
            _, out, _ = sh([*uv, '--python', '3.13', '--exclude-newer', day.isoformat(), '--with', 'polars',
                            'python', '-c', PRINT_POLARS], other, env={'TZ': zone})
            seen.append(f'{day}: {polars_of(out)}')
        rows.append((pid, f'bare dates around the upload date, TZ={zone} (the design uses RFC 3339, not a bare date)',
                     'record', '; '.join(seen), 'RECORD'))
    # 2: command-line and environment dates do not reach a script header; the header's own table does
    probe('P2a', 'CLI --exclude-newer does not limit a script header', 'polars 2.0.0',
          [*uv, '--exclude-newer', CUT, str(repo / 'skills/demo/scripts/s.py')], other, newest)
    probe('P2b', 'UV_EXCLUDE_NEWER does not limit a script header', 'polars 2.0.0',
          [*uv, str(repo / 'skills/demo/scripts/s.py')], other, newest, env={'UV_EXCLUDE_NEWER': CUT})
    probe('P2c', "a [tool.uv] exclude-newer in the header limits it", 'polars < 2',
          [*uv, str(build_dir / 'owndate.py')], other, older, env={'UV_NO_CONFIG': '1'})
    # 3: interpreter choice
    probe('P3a', '--python 3.13 resolves a bare polars header', 'polars 2.0.0 on 3.13',
          [*uv, '--python', '3.13', str(deep / 's.py')], other, lambda o: newest(o) and o.endswith('3.13'))
    probe('P3b', '--python 3.14 with polars>=2.0 resolves', 'polars 2.0.0 on 3.14',
          [*uv, '--python', '3.14', '--with', 'polars>=2.0', 'python', '-c', PRINT_POLARS], other,
          lambda o: newest(o) and o.endswith('3.14'))
    probe('P3c', 'no --python, no .python-version (script outside the repo): which interpreter and polars',
          'record (the spec saw 3.14 and 1.44.2)', [*uv, str(work / 'neutral.py')], other, lambda o: True, record=True)
    # 4: the root uv.toml
    probe('P4a', 'root uv.toml date reaches --with in a subdirectory', 'polars < 2',
          [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], build_dir, older)
    probe('P4b', 'root uv.toml date reaches a script header in a subdirectory', 'polars < 2',
          [*uv, 's.py'], build_dir, older)
    with_dir = work / 'constraints'
    with_dir.mkdir()
    (with_dir / 'uv.toml').write_text('constraint-dependencies = ["polars<2"]\noverride-dependencies = ["polars<2"]\n')
    probe('P4c', 'constraint- and override-dependencies in uv.toml do not affect --with', 'polars 2.0.0',
          [*uv, '--python', '3.13', '--with', 'polars', 'python', '-c', PRINT_POLARS], with_dir, newest)
    (work / 'constraint.txt').write_text('polars<2\n')
    probe('P4d', 'UV_CONSTRAINT does not affect --with', 'polars 2.0.0',
          [*uv, '--python', '3.13', '--with', 'polars', 'python', '-c', PRINT_POLARS], other, newest,
          env={'UV_CONSTRAINT': str(work / 'constraint.txt')})
    probe('P4e', 'CLI --exclude-newer overrides the uv.toml date', 'polars 2.0.0',
          [*uv, '--exclude-newer', LATE, '--with', 'polars', 'python', '-c', PRINT_POLARS], build_dir, newest)
    probe('P4f', 'UV_EXCLUDE_NEWER overrides the uv.toml date', 'polars 2.0.0',
          [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], build_dir, newest, env={'UV_EXCLUDE_NEWER': LATE})
    probe('P4g', '--with polars==1.44.2 on a script run takes over from the header polars>=2.0 (no dates)',
          'polars 1.44.2', [*uv, '--python', '3.13', '--with', 'polars==1.44.2', str(work / 'floor.py')], other,
          lambda o: o == '1.44.2')
    # 5: real path against symlink
    probe('P5a', 'a script run by its real path takes the repo uv.toml, from another directory', 'polars < 2',
          [*uv, str(build_dir / 's.py')], other, older)
    probe('P5b', 'the same script through a symlink does not', 'polars 2.0.0',
          [*uv, str(work / 'link-build' / 's.py')], other, newest)
    # 6: .python-version
    default_py = sh([*uv, '--no-project', 'python', '-c', PRINT_PY], other)[1].replace(' ', '.')
    probe('P6a', '.python-version is found from a subdirectory, also with --no-project',
          f'3.13 (the bare default here is {default_py})', [*uv, '--no-project', 'python', '-c', PRINT_PY], build_dir,
          lambda o: o == '3 13')
    probe('P6b', '--directory finds .python-version from another working directory', '3.13',
          [*uv, '--directory', str(repo), '--no-project', 'python', '-c', PRINT_PY], other, lambda o: o == '3 13')
    probe('P6c', '--directory finds the uv.toml date too', 'polars < 2',
          [*uv, '--directory', str(repo), '--with', 'polars', 'python', '-c', PRINT_POLARS], other, older)
    # the shadow file under skills/
    probe('S1', 'skills/uv.toml shadows the root date for a script header (real path)', 'polars 2.0.0',
          [*uv, 's.py'], deep, newest)
    probe('S2', '... and for --with', 'polars 2.0.0', [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], deep, newest)
    probe('S3', '... and .python-version is still found under skills/', '3.13',
          [*uv, '--no-project', 'python', '-c', PRINT_PY], deep, lambda o: o == '3 13')
    probe('S4', '... and a run through a ~/.claude/skills-style symlink floats too', 'polars 2.0.0',
          [*uv, str(work / 'link-skills/demo/scripts/s.py')], other, newest)
    # nested worktrees
    probe('N1', 'a nested worktree without the files inherits the date and the interpreter', 'polars < 2 on 3.13',
          [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], repo / '.claude/worktrees/wt',
          lambda o: older(o) and o.endswith('3.13'))
    probe('N2', 'a nested worktree with its own uv.toml uses its own', 'polars 2.0.0',
          [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], repo / '.claude/worktrees/wt2', newest)
    # what drift and bump need
    probe('P8a', 'UV_NO_CONFIG=1 drops the root date for --with', 'polars 2.0.0',
          [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], build_dir, newest, env={'UV_NO_CONFIG': '1'})
    probe('P8b', 'UV_NO_CONFIG=1 drops the root date for a script header', 'polars 2.0.0',
          [*uv, 's.py'], build_dir, newest, env={'UV_NO_CONFIG': '1'})
    compile_args = ['uv', 'pip', 'compile', '-', '--python-version', '3.13', '--no-header', '--no-annotate', '--quiet']
    pin = lambda o: next((line.split('==')[1] for line in o.splitlines() if line.startswith('polars==')), '')
    probe('P9a', 'uv pip compile reads the root date from the working directory', 'polars < 2',
          compile_args, build_dir, lambda o: major(pin(o)) in range(0, 2), stdin='polars\n')
    probe('P9b', 'uv pip compile --exclude-newer overrides it', 'polars 2.0.0',
          [*compile_args, '--exclude-newer', LATE], build_dir, lambda o: major(pin(o)) >= 2, stdin='polars\n')
    probe('P9c', 'uv --no-config pip compile ignores it', 'polars 2.0.0',
          ['uv', '--no-config', *compile_args[1:]], build_dir, lambda o: major(pin(o)) >= 2, stdin='polars\n')
    probe('P10', 'uv python list --output-format json has the fields drift reads', 'version, version_parts, variant, implementation',
          ['uv', 'python', 'list', '--only-downloads', '--output-format', 'json'], other,
          lambda o: all(k in json.loads(o)[0] for k in ('version', 'version_parts', 'variant', 'implementation')),
          show=lambda o: 'fields present')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--keep', action='store_true', help='leave the throwaway tree in place')
    args = parser.parse_args()
    if shutil.which('uv') is None:
        print('uv is not on PATH', file=sys.stderr)
        return 2
    print(f'{subprocess.run(["uv", "--version"], capture_output=True, text=True).stdout.strip()}\n')
    work = Path(tempfile.mkdtemp(prefix='vprobe-66-'))
    try:
        run_all(work)
    finally:
        if not args.keep:
            shutil.rmtree(work, ignore_errors=True)
    print('| id | probe | expected | observed | result |\n|---|---|---|---|---|')
    for row in rows:
        print('| ' + ' | '.join(cell.replace('|', '/') for cell in row) + ' |')
    return 1 if any(row[-1] == 'FAIL' for row in rows) else 0


if __name__ == '__main__':
    sys.exit(main())
