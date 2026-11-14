# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
'''Plan 94's branch explainer probe kit: fixtures, prompts, word counts, the rep audit and the scores.

Run from the repository root:
  uv run specs/baseline/red-baseline-branch-explainer/kit/kit.py <command> [args]
Commands: selftest; fixture <name> <dest>; writer-prompt <arm> <name> <rep-dir>;
audit <stream> <rep-dir> <out-prefix>; reader-prompt <arm> <explainer>;
adjudicator-prompt <arm> <name> <explainer> <reader-json>; result-ok <json>; score <arm-dir>.
'''
import functools
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURES = {
    'p80': {'plan': '80-development-history-record', 'head': '325330a57ddff8196b40c253e016c05ebe0cd151',
            'base': '4d69454f51a548e242e5e830275303e0c7c09b74', 'branch': 'claude/plan-80-execution-636c1e',
            'commits': 21, 'held_out': False},
    'p90': {'plan': '90-readonly-guard-command-starts', 'head': 'd51bf645509b6a96db2673b9b423696363fce70c',
            'base': '84efc992b77a84d113bb15294b236e22c5349346', 'branch': 'claude/quirky-golick-44b138',
            'commits': 24, 'held_out': False},
    'p92': {'plan': '92-writing-skills-guide-rewrite', 'head': '0b6d34f43d11adb5bce772e19073fd07241fa978',
            'base': 'e382493700ea5bc7b44aa5048886a85a157f8dfd', 'branch': 'claude/compassionate-jennings-98ff45',
            'commits': 15, 'held_out': False},
    'p84': {'plan': '84-spec-derived-acceptance-tests', 'head': '4cae5b24491392c64854ce7d31eaa2318befaa26',
            'base': '650e13c4722a83684a33b219a26f74cb1ffe0fdc', 'branch': 'claude/musing-dhawan-59a2d0',
            'commits': 16, 'held_out': True},
}
WRITER_TOOLS = frozenset({'Bash', 'Read', 'Write', 'Grep', 'Glob'})
MODEL = 'claude-opus-5-5'
SYNOPSIS_LIMIT = 250
EXPLAINER_LIMIT = 2000
REPS = 3
HOLD = 2

CONTROL_REQUEST = ('Explain the change in `{base}..HEAD` of this repository to me, its owner, before I merge it. '
                   'Write it to `{path}`.')

DISPATCH = '''Read {brief} and follow it to write a branch explainer.
BASE: {base}
HEAD: {head}
Branch: {branch}
Repository: {repo}
Plan branch: {plan_branch}
Output: {output}'''

READER = '''Below is a document that explains one branch of a code repository to the repository's owner. Read it. Then, from what the document says, write a synopsis of the branch in your own words: three labeled parts, at most 250 words in all.

The plan: what the work set out to do, and why.
The build: how it was built: the main parts, in the order they depend on each other.
The project: what the branch adds to the project as a whole.

Reply with the three parts only.

<document>
{explainer}
</document>'''

ADJUDICATOR = '''You score one explainer of a code branch, and a synopsis that a reader wrote after reading only that explainer. You have no tools. Everything you need is below.

<spec>
{spec}
</spec>
<plan>
{plan}
</plan>
<history_entry>
{entry}
</history_entry>
<diff_stat>
{stat}
</diff_stat>
<diff note="Probe records under specs/baseline/ and specs/red-baseline-*/, and the plan and spec files, are left out of this diff. diff_stat lists every changed file.">
{diff}
</diff>
<explainer>
{explainer}
</explainer>
<synopsis>
{synopsis}
</synopsis>

Score four bars. A bar passes only when every part of it holds.

B1 Plan. The synopsis's first part states the plan's goal and the reason for it, and both agree with the spec.
B2 Build. The synopsis's second part names the main parts of the build in an order that fits their dependencies: no part comes before a part it needs. It also states at least two facts that come from the diff and that the spec does not state, such as a file, a function, a command, a check, a count or a behavior.
B3 Project. The synopsis's third part names at least one way the branch changes the project beyond the files it touches: a part of the project that now depends on the branch, or a step of a workflow that now runs differently. A list of changed files does not count.
B4 Accuracy. The explainer, every section of it, makes no claim about what the branch's code or text does that the diff contradicts. A claim that the diff does not cover is not a contradiction.{b4_extra}

Reply in exactly this form, and nothing else:
B1: PASS or FAIL
Why: <one or two sentences that quote the synopsis>
B2: PASS or FAIL
Why: <the order you checked, and the two diff facts, each with the file it comes from>
B3: PASS or FAIL
Why: <one or two sentences that quote the synopsis>
B4: PASS or FAIL
Contradicted: none, or one line per claim: "<quoted claim>" against <file>: <what the diff shows>'''

TREATMENT_B4 = (" The explainer's own Synopsis section counts too: each of its three parts must agree with the spec and "
                'the diff, and a part that does not is a claim for the list.')

WRITE_CHECK = ('Write the single word ok to the file {path}. Then reply DONE, or reply REFUSED with the reason if the '
               'write was refused.')

KIT = Path(__file__).resolve().parent
PROBE_FILE = KIT / 'isolation_probe_tools.txt'
SYNOPSIS_NAMES = {'control': ('synopsis', 'summary', 'tl;dr'), 'treatment': ('synopsis',)}
BARS = ('B1', 'B2', 'B3', 'B4')
ALL_BARS = (*BARS, 'B5')
SYSTEM_PREFIXES = ('/usr/', '/bin/', '/opt/', '/Library/', '/System/')
ALLOWED_PATHS = ('/dev/null',)
TEXT_ONLY_FIELDS = {'Write': ('content',)}  # text written, not a path read or run
SNIPPET_CHARS = 30
NO_SPEC = '(none: the history entry reads Spec: none)'

HEADING_RE = re.compile(r'^(#{1,6})(?:\s+(.*?))?\s*$')
FENCE_RE = re.compile(r'^\s{0,3}(```|~~~)')
WORD_RE = re.compile(r'[^\W_]')
ABS_PATH_RE = re.compile(r'''(?:^|(?<=[\s'"=(<>|;&]))/[^\s'"`;|&<>()]*''')
HOME_PATH_RE = re.compile(r'''(?:^|(?<=[\s'"=(]))(?:~[A-Za-z0-9._-]*|\$HOME|\$\{HOME\})(?=[/\s'"]|$)''')
PARENT_RE = re.compile(r'''(?:^|(?<=[\s/='"]))\.\.(?=[/\s'"]|$)''')
ADJ_LINE_RE = re.compile(r'^(B[1-4]):\s*(PASS|FAIL)$')
ENTRY_PATHS_RE = re.compile(r'^Plan: `?([^\s`]+)`?\s+·\s+Spec: `?([^\s`]+)`?')
TREATMENT_DIR_RE = re.compile(r'treatment-r\d+')
AUDIT_FILE_RE = re.compile(r'rep(\d+)\.audit\.json')


def count_words(text: str) -> int:
    '''Whitespace-separated tokens that hold at least one letter or digit, code included (C7).'''
    return sum(1 for token in text.split() if WORD_RE.search(token))


def heading_lines(lines: list[str]) -> list[tuple[int, int, str]]:
    '''(line index, level, name) of each Markdown heading outside a code fence; the name drops the #s,
    the spaces and a trailing colon, in lowercase.'''
    found = []
    fence = None
    for index, line in enumerate(lines):
        opener = FENCE_RE.match(line)
        if opener:
            if fence is None:
                fence = opener.group(1)
            elif opener.group(1) == fence:
                fence = None
            continue
        heading = HEADING_RE.match(line) if fence is None else None
        if heading:
            name = (heading.group(2) or '').strip().removesuffix(':').strip().lower()
            found.append((index, len(heading.group(1)), name))
    return found


def check_arm(arm: str) -> None:
    if arm not in SYNOPSIS_NAMES:
        raise ValueError(f'arm must be control or treatment, not {arm}')


def synopsis_span(text: str, arm: str) -> tuple[int, int] | None:
    '''Half-open line range of the synopsis section, from its heading to the next heading of the same or a
    higher level; the treatment's is `## Synopsis`, a control's the first Synopsis, Summary or TL;DR.'''
    check_arm(arm)
    lines = text.splitlines()
    headings = heading_lines(lines)
    for position, (index, level, name) in enumerate(headings):
        if name in SYNOPSIS_NAMES[arm]:
            end = next((later for later, later_level, _ in headings[position + 1:] if later_level <= level),
                       len(lines))
            return index, end
    return None


def reader_view(text: str, arm: str) -> str:
    '''What the reader sees: a treatment explainer without its Synopsis section; a control explainer whole.'''
    check_arm(arm)
    span = synopsis_span(text, arm) if arm == 'treatment' else None
    if span is None:
        return text
    lines = text.splitlines(keepends=True)
    return ''.join(lines[:span[0]] + lines[span[1]:])


def length_bar(text: str, arm: str) -> dict:
    '''B5: the explainer within EXPLAINER_LIMIT words and its synopsis, if any, within SYNOPSIS_LIMIT.
    A treatment explainer with no `## Synopsis` fails; a control with none is judged on its length only.'''
    span = synopsis_span(text, arm)
    words = count_words(text)
    synopsis = None if span is None else count_words('\n'.join(text.splitlines()[span[0] + 1:span[1]]))
    if span is None and arm == 'treatment':
        holds = False
    else:
        holds = words <= EXPLAINER_LIMIT and (synopsis is None or synopsis <= SYNOPSIS_LIMIT)
    return {'explainer': words, 'synopsis': synopsis, 'B5': holds}


def parse_adjudication(text: str) -> dict[str, bool] | None:
    '''B1 to B4 from an adjudicator's reply; None unless each bar has exactly one `Bk: PASS|FAIL` line.'''
    found = {}
    for line in text.splitlines():
        verdict = ADJ_LINE_RE.match(line.strip())
        if verdict:
            if verdict.group(1) in found:
                return None
            found[verdict.group(1)] = verdict.group(2) == 'PASS'
    if set(found) != set(BARS):
        return None
    return {bar: found[bar] for bar in BARS}


def arm_of(arm_dir: Path) -> str:
    '''`control` for a control folder; `treatment` for `heldout` or `treatment-r<k>`.'''
    name = arm_dir.name
    if name == 'control':
        return 'control'
    if name == 'heldout' or TREATMENT_DIR_RE.fullmatch(name):
        return 'treatment'
    raise ValueError(f'not an arm folder: {name}')


@functools.cache
def repo_root() -> str:
    '''`git rev-parse --show-toplevel` of the working directory.'''
    return run(['git', 'rev-parse', '--show-toplevel']).strip()


def run(command: list[str], cwd: str | None = None) -> str:
    '''stdout of a command; exits 2 with its stderr when it fails.'''
    done = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if done.returncode != 0:
        print(f'failed ({done.returncode}): {" ".join(command)}\n{done.stderr.strip()}', file=sys.stderr)
        sys.exit(2)
    return done.stdout


def git(*args: str) -> str:
    '''A git command in this repository, from its top folder.'''
    return run(['git', '--no-pager', *args], cwd=repo_root())


def history_entry(base: str, head: str, plan: str) -> str:
    '''The section that `base..head` adds to specs/history.md whose header starts `## <plan>`.'''
    added, in_hunk = [], False
    for line in git('diff', '--no-color', '--no-ext-diff', '-U0', f'{base}..{head}', '--',
                    'specs/history.md').splitlines():
        if line.startswith('@@'):
            in_hunk = True
        elif in_hunk and line.startswith('+'):
            added.append(line[1:])
    start = next((index for index, line in enumerate(added) if line.startswith(f'## {plan}')), None)
    if start is None:
        print(f'no history entry for {plan} in {base[:7]}..{head[:7]}', file=sys.stderr)
        sys.exit(2)
    end = next((index for index in range(start + 1, len(added)) if added[index].startswith('## ')), len(added))
    return '\n'.join(added[start:end]).rstrip('\n') + '\n'


def entry_paths(entry: str) -> tuple[str, str | None]:
    '''The plan path and the spec path (None for `Spec: none`) from an entry's `Plan:` line.'''
    for line in entry.splitlines():
        paths = ENTRY_PATHS_RE.match(line)
        if paths:
            return paths.group(1), None if paths.group(2) == 'none' else paths.group(2)
    print('no `Plan: … · Spec: …` line in the history entry', file=sys.stderr)
    sys.exit(2)


def adjudicator_diff(base: str, head: str, plan: str, spec: str | None) -> tuple[str, str]:
    '''The full `--stat=200`, and the diff without probe records and the plan and spec files (C5).'''
    stat = git('diff', '--no-color', '--no-ext-diff', '--stat=200', f'{base}..{head}')
    left_out = [f'specs/plans/{Path(plan).name}', f'specs/plans/completed/{Path(plan).name}']
    if spec is not None:
        left_out += [f'specs/{Path(spec).name}', f'specs/completed/{Path(spec).name}']
    pathspecs = [':/', ':(exclude,glob)specs/baseline/**', ':(exclude,glob)specs/red-baseline-*/**',
                 *(f':(exclude){path}' for path in left_out)]
    diff = git('diff', '--no-color', '--no-ext-diff', f'{base}..{head}', '--', *pathspecs)
    return stat, diff


def result_problem(path: Path) -> str | None:
    '''None for a `claude -p --output-format json` file that succeeded with a reply; else a short reason.'''
    if not path.is_file():
        return 'no file'
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return 'not JSON'
    if not isinstance(data, dict):
        return 'not JSON'
    if data.get('subtype') != 'success':
        return f'subtype {data.get("subtype")}'
    if data.get('is_error') is not False:
        return 'is_error'
    reply = data.get('result')
    if not isinstance(reply, str) or not reply.strip():
        return 'empty result'
    return None


def stream_records(stream: Path) -> tuple[dict, list[dict], dict | None]:
    '''The init record, the assistant records and the last result record of a stream-json file.'''
    init, assistants, result = {}, [], None
    for line in stream.read_text().splitlines() if stream.is_file() else []:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get('type') == 'system' and record.get('subtype') == 'init':
            init = record
        elif record.get('type') == 'assistant':
            assistants.append(record)
        elif record.get('type') == 'result':
            result = record
    return init, assistants, result


def strings_in(value, key: str = '') -> list[tuple[str, str]]:
    '''(field name, text) of every string inside a tool input.'''
    if isinstance(value, str):
        return [(key, value)]
    if isinstance(value, dict):
        return [found for name, item in value.items() for found in strings_in(item, name)]
    if isinstance(value, list):
        return [found for item in value for found in strings_in(item, key)]
    return []


def path_hits(tool: str, tool_input: dict, roots: tuple[str, ...]) -> list[str]:
    '''Each absolute path outside the rep, home-folder path and `..` component that a tool input names.'''
    hits = []
    for field, text in strings_in(tool_input):
        if field in TEXT_ONLY_FIELDS.get(tool, ()):
            continue
        for match in ABS_PATH_RE.finditer(text):
            path = match.group(0)
            inside = any(path == root or path.startswith(root + '/') for root in roots)
            if not (inside or path in ALLOWED_PATHS or path.startswith(SYSTEM_PREFIXES)):
                hits.append(path)
        hits += [match.group(0) for match in HOME_PATH_RE.finditer(text)]
        hits += [text[max(0, match.start() - SNIPPET_CHARS):match.end() + SNIPPET_CHARS]
                 for match in PARENT_RE.finditer(text)]
    return list(dict.fromkeys(hits))


def audit_hits(stream: Path, rep_dir: Path) -> dict:
    '''Tools, models, outcome and outside-the-rep inputs of one writer stream, with the C7 void reasons.'''
    init, assistants, result = stream_records(stream)
    roots = (str(rep_dir), os.path.realpath(rep_dir))
    tools, models, outside = set(init.get('tools') or []), set(), []
    if init.get('model'):
        models.add(init['model'])
    for record in assistants:
        message = record.get('message') or {}
        if message.get('model'):
            models.add(message['model'])
        for part in message.get('content') or []:
            if not isinstance(part, dict) or part.get('type') != 'tool_use':
                continue
            tools.add(part.get('name'))
            hits = path_hits(part.get('name'), part.get('input') or {}, roots)
            if hits:
                outside.append({'tool': part.get('name'), 'input': part.get('input'), 'hits': hits})
    reasons = []
    if result is None:
        reasons.append('no result record')
    else:
        if result.get('subtype') != 'success':
            reasons.append(f'subtype {result.get("subtype")}')
        if result.get('is_error'):
            reasons.append('is_error')
    reasons += [f'tool {name} outside the writer list' for name in sorted(tools - WRITER_TOOLS)]
    reasons += [f'model {model}' for model in sorted(models - {MODEL})]
    explainer = rep_dir / 'out' / 'explainer.md'
    if not explainer.is_file() or not explainer.read_text().strip():
        reasons.append('no explainer file')
    result = result or {}
    return {'tools': sorted(tools), 'models': sorted(models), 'subtype': result.get('subtype'),
            'cost': result.get('total_cost_usd'), 'permission_denials': result.get('permission_denials'),
            'outside': outside, 'void_reasons': reasons}


def selftest() -> None:
    '''Assert the kit's pure functions and its git readers on fixed inputs; print `selftest passed`.'''
    assert count_words('Hello, world! -- `x.py:12` | ## |') == 3
    t = '# T\n\n## Synopsis\n\n**The plan:** a\n\n### Sub\nb\n\n## Background\nc\n'
    assert reader_view(t, 'treatment') == '# T\n\n## Background\nc\n'
    assert reader_view(t, 'control') == t
    c = '# T\n## Summary:\nx y\n## Body\nz\n'
    assert length_bar(c, 'control') == {'explainer': 6, 'synopsis': 2, 'B5': True}
    assert reader_view(c, 'control') == c
    assert synopsis_span(c, 'treatment') is None
    assert length_bar(c, 'treatment')['B5'] is False
    assert length_bar('# T\n' + 'w ' * 10, 'control') == {'explainer': 11, 'synopsis': None, 'B5': True}
    assert length_bar('## Synopsis\n' + 'w ' * 251 + '\n## B\n', 'treatment')['B5'] is False
    assert length_bar('w ' * 2001, 'control')['B5'] is False
    fenced = '# T\n\n## Synopsis\n\n```bash\n# not a heading\n```\nx\n\n## Background\nc\n'
    assert synopsis_span(fenced, 'treatment') == (2, 9)
    good = 'B1: PASS\nWhy: x\nB2: FAIL\nWhy: y\nB3: PASS\nWhy: z\nB4: PASS\nContradicted: none\n'
    assert parse_adjudication(good) == {'B1': True, 'B2': False, 'B3': True, 'B4': True}
    assert parse_adjudication(good.replace('B3: PASS', 'B3: PASS or FAIL')) is None
    assert parse_adjudication(good.replace('B3: PASS\n', '')) is None
    assert arm_of(Path('x/control')) == 'control'
    assert arm_of(Path('x/treatment-r12')) == 'treatment' and arm_of(Path('x/heldout')) == 'treatment'
    for bad in ('pilot', 'treatment', 'treatment-r', 'heldout2'):
        try:
            arm_of(Path('x') / bad)
        except ValueError:
            pass
        else:
            raise AssertionError(bad)
    f = FIXTURES['p90']
    entry = history_entry(f['base'], f['head'], f['plan'])
    assert entry.startswith('## 90-readonly-guard-command-starts')
    plan, spec = entry_paths(entry)
    assert plan == 'specs/plans/completed/90-readonly-guard-command-starts.md'
    assert spec == 'specs/completed/readonly-guard-command-starts.md'
    stat, diff = adjudicator_diff(f['base'], f['head'], plan, spec)
    assert 'specs/plans/completed/90-readonly-guard-command-starts.md' in stat
    assert '+++ b/specs/plans/completed/90-' not in diff and '+++ b/hooks/' in diff
    f = FIXTURES['p80']
    assert history_entry(f['base'], f['head'], f['plan']).startswith('## 80-development-history-record')
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        (folder / 'ok.json').write_text('{"is_error": false, "subtype": "success", "result": "x"}')
        (folder / 'empty.json').write_text('')
        (folder / 'budget.json').write_text('{"is_error": true, "subtype": "error_max_budget_usd", "result": ""}')
        assert result_problem(folder / 'ok.json') is None
        assert result_problem(folder / 'empty.json') == 'not JSON'
        assert result_problem(folder / 'budget.json') is not None
        assert result_problem(folder / 'missing.json') == 'no file'
    rep_dir = Path('/tmp/plan94-rep-abc')
    inside = {'file_path': '/tmp/plan94-rep-abc/repo/README.md'}
    projects = {'file_path': '/Users/x/Projects/agent-skills/specs/branch-explainer.md'}
    home = {'command': 'cat ~/notes.md'}
    real = {'file_path': os.path.realpath(rep_dir) + '/repo/x.md'}
    parent = {'command': 'cat ../../notes.md'}
    stat_range = {'command': 'git diff --stat main..HEAD'}
    log_range = {'command': 'git log --oneline 4be1c9a..HEAD'}

    def use(name: str, tool_input: dict) -> dict:
        return {'type': 'tool_use', 'id': name, 'name': name, 'input': tool_input}

    first = {'type': 'assistant', 'message': {'content': [
        use('Read', inside), use('Read', projects), use('Bash', home), use('Read', real), use('Bash', parent),
        use('Bash', stat_range), use('Bash', log_range)]}}
    second = {'type': 'assistant', 'message': {'content': [use('WebFetch', {'url': 'https://example.com/x'})]}}
    records = [{'type': 'system', 'subtype': 'init', 'tools': ['Bash', 'Read']}, first,
               {'type': 'result', 'subtype': 'success'}]
    with tempfile.TemporaryDirectory() as tmp:
        stream = Path(tmp) / 'rep1.jsonl'
        stream.write_text('\n'.join(json.dumps(r) for r in records) + '\n')
        hits = audit_hits(stream, rep_dir)
        flagged = [o['input'] for o in hits['outside']]
        assert projects in flagged and home in flagged and inside not in flagged
        assert real not in flagged and parent in flagged
        assert stat_range not in flagged and log_range not in flagged
        assert 'no explainer file' in hits['void_reasons']
        stream.write_text('\n'.join(json.dumps(r) for r in [*records[:2], second, records[2]]) + '\n')
        assert any('WebFetch' in reason for reason in audit_hits(stream, rep_dir)['void_reasons'])
    print('selftest passed')


def fixture(name: str, dest: str) -> None:
    '''Build <dest>/repo: only the head's history, `main` at BASE, a detached HEAD at the head (C2).'''
    spec = FIXTURES[name]
    repo = Path(dest) / 'repo'
    run(['git', 'init', '-q', '-b', 'main', str(repo)])
    in_repo = ['git', '-C', str(repo)]
    run([*in_repo, 'fetch', '-q', '--no-tags', repo_root(), spec['head']])
    run([*in_repo, 'update-ref', 'refs/heads/main', spec['base']])
    run([*in_repo, 'checkout', '-q', '--detach', spec['head']])
    (repo / '.git' / 'FETCH_HEAD').unlink(missing_ok=True)
    count = int(run([*in_repo, 'rev-list', '--count', 'main..HEAD']).strip())
    refs = run([*in_repo, 'for-each-ref', '--format=%(refname)']).split()
    if count != spec['commits'] or refs != ['refs/heads/main']:
        print(f'fixture {name}: {count} commits in main..HEAD (want {spec["commits"]}), refs {refs}',
              file=sys.stderr)
        sys.exit(2)
    print(repo)


def writer_prompt(arm: str, name: str, rep_dir: str) -> None:
    '''The writer's prompt for one rep folder.'''
    spec, rep = FIXTURES[name], Path(rep_dir)
    output = str(rep / 'out' / 'explainer.md')
    if arm == 'control':
        text = CONTROL_REQUEST.format(base=spec['base'], path=output)
    elif arm == 'treatment':
        text = DISPATCH.format(brief=rep / 'brief' / 'branch-explainer-prompt.md', base=spec['base'],
                               head=spec['head'], branch=spec['branch'], repo=rep / 'repo', plan_branch='yes',
                               output=output)
    elif arm == 'probe':
        text = PROBE_FILE.read_text()
    elif arm == 'permcheck':
        text = WRITE_CHECK.format(path=rep / 'out' / 'check.txt')
    else:
        sys.exit(f'unknown writer arm: {arm}')
    print(text.rstrip('\n'))


def audit(stream: str, rep_dir: str, out_prefix: str) -> None:
    '''Write <out-prefix>.audit.json and <out-prefix>.result.json; print the void reasons.'''
    hits = audit_hits(Path(stream), Path(rep_dir))
    init, _, result = stream_records(Path(stream))
    result = result or {}
    digest = hashlib.sha256(Path(stream).read_bytes()).hexdigest() if Path(stream).is_file() else None
    summary = {'tools': init.get('tools'), 'model': init.get('model'), 'version': init.get('claude_code_version'),
               'cost': result.get('total_cost_usd'), 'turns': result.get('num_turns'),
               'subtype': result.get('subtype'), 'permission_denials': result.get('permission_denials'),
               'stream_sha256': digest, 'model_usage': sorted(result.get('modelUsage') or {}),
               'result': result.get('result')}
    Path(f'{out_prefix}.audit.json').write_text(json.dumps(hits, indent=2) + '\n')
    Path(f'{out_prefix}.result.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('void: ' + ('; '.join(hits['void_reasons']) or 'none'))
    print(f'outside hits: {len(hits["outside"])}, cost: {summary["cost"]}, turns: {summary["turns"]}')


def reader_prompt(arm: str, explainer: str) -> None:
    print(READER.format(explainer=reader_view(Path(explainer).read_text(), arm).rstrip('\n')))


def adjudicator_prompt(arm: str, name: str, explainer: str, reader_json: str) -> None:
    '''The adjudicator's prompt: the fixture's spec, plan, entry, stat and diff, then the explainer and synopsis.'''
    check_arm(arm)
    spec = FIXTURES[name]
    entry = history_entry(spec['base'], spec['head'], spec['plan'])
    plan_path, spec_path = entry_paths(entry)
    stat, diff = adjudicator_diff(spec['base'], spec['head'], plan_path, spec_path)
    spec_text = NO_SPEC if spec_path is None else git('show', f'{spec["head"]}:{spec_path}')
    synopsis = json.loads(Path(reader_json).read_text())['result']
    print(ADJUDICATOR.format(spec=spec_text.rstrip('\n'), plan=git('show', f'{spec["head"]}:{plan_path}').rstrip('\n'),
                             entry=entry.rstrip('\n'), stat=stat.rstrip('\n'), diff=diff.rstrip('\n'),
                             explainer=Path(explainer).read_text().rstrip('\n'), synopsis=synopsis.strip(),
                             b4_extra=TREATMENT_B4 if arm == 'treatment' else ''))


def result_ok(path: str) -> None:
    problem = result_problem(Path(path))
    if problem is not None:
        print(problem)
        sys.exit(1)


def is_void(fixture_dir: Path, rep: int) -> bool:
    '''A rep with a `.VOID` file from the executor, or with a void reason in its audit (C7).'''
    if (fixture_dir / f'rep{rep}.VOID').exists():
        return True
    return bool(json.loads((fixture_dir / f'rep{rep}.audit.json').read_text())['void_reasons'])


def score(arm_dir: str) -> None:
    '''Score each fixture's first REPS reps that are not VOID; a bar holds in HOLD of REPS.'''
    folder = Path(arm_dir)
    try:
        arm = arm_of(folder)
    except ValueError as error:
        print(error)
        sys.exit(2)
    rows, errors = [], []
    fixture_dirs = sorted(path for path in folder.iterdir() if path.is_dir() and path.name in FIXTURES)
    if not fixture_dirs:
        errors.append(f'no fixture folders in {folder}')
    for fixture_dir in fixture_dirs:
        reps = sorted(int(found.group(1)) for path in fixture_dir.iterdir()
                      if (found := AUDIT_FILE_RE.fullmatch(path.name)))
        scored = [rep for rep in reps if not is_void(fixture_dir, rep)][:REPS]
        if len(scored) < REPS:
            errors.append(f'{fixture_dir.name}: {len(scored)} scored reps, {REPS} needed')
        for rep in scored:
            adjudication = fixture_dir / 'adj' / f'rep{rep}.json'
            problem = result_problem(adjudication)
            if problem is not None:
                errors.append(f'{fixture_dir.name} rep{rep}: adj/rep{rep}.json: {problem}')
                continue
            bars = parse_adjudication(json.loads(adjudication.read_text())['result'])
            if bars is None:
                errors.append(f'{fixture_dir.name} rep{rep}: adj/rep{rep}.json does not parse')
                continue
            length = length_bar((fixture_dir / f'rep{rep}.md').read_text(), arm)
            rows.append((fixture_dir, rep, {**bars, 'B5': length['B5']}, length))
    if errors:
        print('\n'.join(errors))
        sys.exit(2)
    for fixture_dir, rep, bars, length in rows:
        (fixture_dir / f'rep{rep}.score.json').write_text(
            json.dumps({'rep': rep, 'arm': arm, 'bars': bars, 'length': length}, indent=2) + '\n')
    for fixture_dir in fixture_dirs:
        mine = [(rep, bars) for directory, rep, bars, _ in rows if directory == fixture_dir]
        print(f'{fixture_dir.name} ({arm}), scored reps {" ".join(str(rep) for rep, _ in mine)}')
        for bar in ALL_BARS:
            passes = sum(bars[bar] for _, bars in mine)
            print(f'  {bar}: {passes}/{len(mine)} {"holds" if passes >= HOLD else "fails"}')
        print(f'  all five bars at once: {sum(all(bars.values()) for _, bars in mine)}/{len(mine)}')


COMMANDS = {'selftest': selftest, 'fixture': fixture, 'writer-prompt': writer_prompt, 'audit': audit,
            'reader-prompt': reader_prompt, 'adjudicator-prompt': adjudicator_prompt, 'result-ok': result_ok,
            'score': score}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit(f'usage: kit.py <{"|".join(COMMANDS)}> [args]')
    COMMANDS[sys.argv[1]](*sys.argv[2:])


if __name__ == '__main__':
    main()
