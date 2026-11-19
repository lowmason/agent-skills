#!/usr/bin/python3
'''Build each rep's extract and audit from what run_rep.sh saved (plan 100).

Usage: extract.py BATCH                 (every rep in $PHR_CTL/batches/BATCH.txt)
       extract.py --rep REP [--rep REP ...]

A fork of plan 40's $RED/tools/extract.py for per-rep homes. It writes
$PHR_CTL/results/<rep>/extract.md, which the scorer reads, and
$PHR_CTL/results/<rep>/audit.json. A rep is void (PROTOCOL.md, Audit, read by
plan 100's C10 table B) when a turn is missing, exited non-zero or reports an
error; when any tool input, in its own transcript or a subagent's, names a path
in the real home, in the rep HOME's Library folder (the Keychains link), or in
the reps directory outside the rep's HOME, or names Keychains or a
contamination fragment; when a tool input is a recursive or whole-disk search
rooted at a folder that holds the real home (guard.py's rule); or when a harness check fails (C11: the kit hash, the
init record's skills and agents, a kit_error, background tasks stopped at exit).
Permission denials, from every transcript of the rep (subagents included),
are listed for the scorer, who voids a rep whose failure traces to one.

Paths in the transcripts are the run-time ones: `~` is the HOME the rep ran
with, $PHR_ROOT/<rep>, not its parked copy. The real home is this process's
HOME, as for run_rep.sh. It reads the parked repo from $PHR_CTL/homes/<rep>/
work/<rep>. It never writes outside $PHR_CTL/results. Runs on the system
Python 3.9 with the stdlib only.
'''

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import posixpath
import re
import subprocess
import sys
from pathlib import Path

from guard import DATA_ANCESTORS, INDEXED, glob_base, search_roots, simple_commands

KIT = Path(__file__).resolve().parent
REAL = os.path.realpath(os.environ.get('HOME') or str(Path.home()))
CTL = Path(os.environ.get('PHR_CTL') or Path(REAL) / '.cache/agent-skills/handoffs/rerun100')
ROOT = os.path.realpath(os.environ.get('PHR_ROOT') or '/private/tmp/phr100')
HEADS = Path(os.environ.get('PHR_TEMPLATE_HEADS') or KIT / 'templates.tsv')
FRAGMENTS = (
    'handoffs/red', 'agent-skills/handoff-brief', 'plan40-draft', 'Projects/agent-skills',
    'specs/handoff-briefs', 'red-baseline-handoff',
)
KIT_SKILLS = (
    'brainstorming', 'writing-plans', 'executing-plans', 'subagent-driven-development',
    'finishing-a-development-branch', 'requesting-code-review', 'receiving-code-review',
    'using-git-worktrees', 'verification-before-completion', 'test-driven-development',
    'derive-roadmap', 'prepare-handoff',
)
KIT_AGENTS = ('code-reviewer', 'task-reviewer')
BACKGROUND_STOPPED = 'Background tasks still running'
PATH_TOKEN = re.compile(r'''(?:(?<![\w.~$}-])/|~|\$HOME|\$\{HOME\})[^\s'"`;|&<>(){}]*''')
DOTDOT_TOKEN = re.compile(r'''[^\s'"`;|&<>(){}=]*\.\.(?:/[^\s'"`;|&<>(){}]*)?''')
# A library path component followed anywhere later by a keychains component: Library/Keychains,
# however the text spells or splits the path (Library//Keychains, cd Library && ls Keychains).
# Unlike guard.py's, it needs Library, so that the bare word (a grep for it, say) names no path.
KEYCHAINS = re.compile(r'''(?:^|[/\s'"=])library(?=/|$|[\s'";|&)]).*(?:^|[/\s'"=])keychains(?=/|$|[\s'";|&)])''',
                       re.DOTALL)
SHELL_QUOTES = re.compile(r'''[\\'"]''')
GLOB_CHARS = re.compile(r'[*?\[]')
USER_VARS = re.compile(r'\$\{?(?:USER|LOGNAME)\}?')
FILE_KEYS = ('file_path', 'path', 'notebook_path')
DATA_VOLUME = '/System/Volumes/Data'
CAP = 800
# A tool result that reports a denial: the auto mode classifier's, or the kit guard's.
CLASSIFIER_DENIAL = 'Permission for this action was denied'
GUARD_DENIAL = 'blocked by the workspace path guard:'
HOOK_DENIAL = re.compile(r'PreToolUse:\w+ hook error: ' + re.escape(GUARD_DENIAL))


# --- audit -------------------------------------------------------------------


def spelled(path: str) -> str:
    '''One spelling for one folder (C10, Spelling): the Data-volume prefix drops,
    and /tmp becomes /private/tmp. The prefix matches in any case, as APFS does.'''
    folded = path.casefold()
    if folded == DATA_VOLUME.casefold() or folded.startswith(DATA_VOLUME.casefold() + '/'):
        path = path[len(DATA_VOLUME):] or '/'
    if path == '/tmp' or path.startswith('/tmp/'):
        path = '/private' + path
    return path


def inside(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip('/') + '/')


def expanded(token: str, cwd: str, home: str, real_home: str) -> str:
    '''The absolute, unresolved path a token names, as the rep's shell would see
    it: the HOME forms become the rep's HOME, `~user`, $USER and $LOGNAME name
    the real user, and a relative token joins cwd.'''
    for form in ('${HOME}', '$HOME', '~'):
        if token == form or token.startswith(form + '/'):
            token = home + token[len(form):]
            break
    else:
        user = posixpath.basename(real_home.rstrip('/'))
        token = USER_VARS.sub(user, token)
        if token.startswith('~'):
            token = posixpath.join(posixpath.dirname(real_home.rstrip('/')), token[1:])
    if not token.startswith('/'):
        token = posixpath.join(spelled(cwd), token)
    return token


def walked(path: str) -> list[str]:
    '''Every prefix the path passes through, resolved lexically one component at
    a time, each in its one spelling. The last is the path itself.'''
    parts: list[str] = []
    steps = []
    for part in path.split('/'):
        if part in ('', '.'):
            continue
        if part == '..':
            if parts:
                parts.pop()
        else:
            parts.append(part)
        steps.append(spelled('/' + '/'.join(parts)))
    return steps or ['/']


def glob_reaches(path: str, root: str) -> bool:
    '''Whether a glob path's leading components can match every component of
    root, so that the shell's expansion lands in it. Lexical: no disk read.'''
    if not GLOB_CHARS.search(path):
        return False
    parts, want = path.strip('/').split('/'), root.strip('/').split('/')
    return len(parts) >= len(want) and all(fnmatch.fnmatchcase(w, p) for w, p in zip(want, parts))


def classify(token: str, cwd: str, home: str, real_home: str, root: str) -> str | None:
    '''The flag for one path token, or None, by C10's table B. Comparisons fold
    case, as APFS does. The real home (any spelling, or a glob that matches it)
    voids. The rep HOME's Library folder voids, also when the path only passes
    through it, since its Keychains link leads into the real home. The rest of
    the rep's HOME is allowed. The reps directory, outside the rep's HOME,
    voids.'''
    home_f = spelled(posixpath.normpath(home)).casefold()
    real_f = spelled(posixpath.normpath(real_home)).casefold()
    root_f = spelled(posixpath.normpath(root)).casefold()
    library_f = home_f + '/library'
    steps = walked(expanded(token, cwd, home, real_home))
    final = steps[-1]
    if inside(final.casefold(), real_f):
        return f'path {final} (the real home)'
    if glob_reaches(final.casefold(), real_f):
        return f'path {final} (a glob that matches the real home)'
    if any(inside(step.casefold(), library_f) for step in steps):
        return f'path {final} (through the Library folder, which links into the real home)'
    if inside(final.casefold(), home_f):
        return None
    if inside(final.casefold(), root_f):
        return f'path {final} (the reps directory)'
    return None


def holders(real_home: str) -> set[str]:
    '''The case-folded folders that hold the real home, in their one spelling.'''
    parts = spelled(posixpath.normpath(real_home)).casefold().strip('/').split('/')
    return {'/', *DATA_ANCESTORS} | {'/' + '/'.join(parts[:n]) for n in range(1, len(parts))}


def ancestor_walks(name: str, data: dict, cwd: str, home: str, real_home: str) -> list[str]:
    '''The flags for a search rooted at a folder that holds the real home, as
    guard.py denies it: a recursive or indexed shell search (a `cd` earlier in
    the line moves its start), a Glob with `**`, or a Grep. Lexical: no disk
    read.'''
    held = holders(real_home)
    why = 'searches a folder that holds the real home'

    def where(token: str, base: str) -> str:
        return walked(expanded(token, base, home, real_home))[-1]

    found = []
    if name == 'Bash':
        command = str(data.get('command', ''))
        for words in simple_commands(command.split('\n', 1)[0] if '<<' in command else command):
            program = posixpath.basename(words[0])
            if program in ('cd', 'pushd'):
                cwd = where(next((w for w in words[1:] if not w.startswith('-')), '~'), cwd)
                continue
            roots = search_roots(words)
            if roots is None:
                continue
            if program in INDEXED:
                found.append(f'search {program} ({why}: its index covers the whole disk)')
            else:
                found += [f'search {program} {root} ({why})' for root in roots or ['.']
                          if where(glob_base(root), cwd).casefold() in held]
    elif name in ('Glob', 'Grep'):
        base = str(data.get('path') or '.')
        pattern = str(data.get('pattern', ''))
        if name == 'Glob':
            if '**' not in pattern:
                return []
            base = glob_base(pattern if pattern.startswith('/') else posixpath.join(base, pattern))
        if where(base, cwd).casefold() in held:
            found.append(f'search {name} at {base} ({why})')
    return found


def tool_uses(record: dict) -> list[tuple[str, dict]]:
    content = (record.get('message') or {}).get('content')
    if not isinstance(content, list):
        return []
    return [(c.get('name', ''), c.get('input') or {}) for c in content
            if isinstance(c, dict) and c.get('type') == 'tool_use']


def scanned(name: str, data: dict, cwd: str, home: str, real_home: str) -> list[tuple[str, str]]:
    '''The strings of one tool input that can reach a file, each with the folder
    a relative path in it starts from: a Bash command (not a heredoc's body,
    which is content), or a tool's path fields, from cwd. A Glob pattern starts
    from the Glob's path, when it has one.'''
    if name == 'Bash':
        command = str(data.get('command', ''))
        return [(command.split('\n', 1)[0] if '<<' in command else command, cwd)]
    strings = [(str(data[k]), cwd) for k in FILE_KEYS if k in data]
    if name == 'Glob' and 'pattern' in data:
        base = expanded(str(data['path']), cwd, home, real_home) if data.get('path') else cwd
        strings.append((str(data['pattern']), base))
    return strings


def flags_for(name: str, data: dict, cwd: str, home: str, real_home: str, root: str) -> list[str]:
    found = ancestor_walks(name, data, cwd, home, real_home)
    for text, base in scanned(name, data, cwd, home, real_home):
        bare = SHELL_QUOTES.sub('', text)  # the shell drops quotes, so Key""chains is Keychains
        if KEYCHAINS.search(bare.casefold()):
            found.append('names Library/Keychains, a link into the real home')
        tokens = PATH_TOKEN.findall(text) + DOTDOT_TOKEN.findall(text)
        if bare != text:
            tokens += PATH_TOKEN.findall(bare) + DOTDOT_TOKEN.findall(bare)
        if name != 'Bash' and text:
            tokens.append(text)
        for token in tokens:
            flag = classify(token, base, home, real_home, root)
            if flag is not None:
                found.append(flag)
        found += [f'fragment {frag!r}' for frag in FRAGMENTS if frag in text]
    return found


def audit_transcripts(transcripts: list[Path], repo: str, home: str, real_home: str, root: str) -> list[str]:
    flags = set()
    for transcript in transcripts:
        for line in transcript.read_text(errors='replace').splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict):
                continue
            cwd = str(record.get('cwd') or repo)
            for name, data in tool_uses(record):
                flags.update(f'{transcript.name}: {name}: {flag}'
                             for flag in flags_for(name, data, cwd, home, real_home, root))
    return sorted(flags)


def result_text(content) -> str:
    '''A tool_result's text: a string, or the text parts of a list.'''
    if isinstance(content, list):
        return '\n'.join(str(c.get('text', '')) for c in content if isinstance(c, dict))
    return str(content or '')


def is_denial(result: dict) -> bool:
    '''Whether a tool_result reports a denial, in the form the transcripts
    show: an error result that starts with the classifier's sentence, or with
    the hook error that carries the guard's reason. A result that only quotes
    the words, a grep of guard.py say, is no denial.'''
    if result.get('is_error') is not True:
        return False
    text = result_text(result.get('content')).lstrip()
    return text.startswith(CLASSIFIER_DENIAL) or HOOK_DENIAL.match(text) is not None


def records(transcript: Path) -> list[dict]:
    found = []
    for line in transcript.read_text(errors='replace').splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            found.append(record)
    return found


def collect_denials(out: Path, turns: int) -> list[dict]:
    '''Every denied tool call of the rep, once each by tool_use_id: a tool_result
    that reports a classifier or guard denial, in any transcript (the session's,
    its subagents', each turn's stream), paired with its tool_use, and each
    turn record's permission_denials. Each entry names the first transcript
    that holds it, and says whether a subagent made the call. The session
    transcripts come first, since they keep each subagent apart.'''
    project = out / 'project'
    transcripts = (sorted(project.rglob('*.jsonl')) if project.is_dir() else []) + sorted(out.glob('turn*.jsonl'))
    uses: dict[str, tuple[str, dict]] = {}
    hits: dict[str, dict] = {}
    for transcript in transcripts:
        label = str(transcript.relative_to(out))
        in_subagent = 'subagents' in transcript.relative_to(out).parts
        for record in records(transcript):
            message = record.get('message')
            content = message.get('content') if isinstance(message, dict) else None
            for c in content if isinstance(content, list) else []:
                if not isinstance(c, dict):
                    continue
                if c.get('type') == 'tool_use' and c.get('id'):
                    uses.setdefault(c['id'], (c.get('name', ''), c.get('input') or {}))
                if c.get('type') != 'tool_result' or not is_denial(c):
                    continue
                subagent = bool(in_subagent or record.get('isSidechain') or record.get('parent_tool_use_id'))
                hit = hits.setdefault(c.get('tool_use_id', ''), {'transcript': label, 'subagent': False})
                hit['subagent'] = hit['subagent'] or subagent
    denials = []
    for use_id, hit in hits.items():
        name, data = uses.get(use_id, ('', {}))
        denials.append({'tool_name': name, 'tool_use_id': use_id, 'tool_input': data, **hit})
    for n in range(1, turns + 1):
        try:
            listed = json.loads((out / f'turn{n}.json').read_text()).get('permission_denials') or []
        except (OSError, json.JSONDecodeError, AttributeError):
            continue
        for denial in listed:
            if not isinstance(denial, dict) or denial.get('tool_use_id') in hits:
                continue
            denials.append({**denial, 'transcript': f'turn{n}.json', 'subagent': False})
            if denial.get('tool_use_id'):
                hits[denial['tool_use_id']] = {}
    return denials


def turn_problems(out: Path, turns: int) -> list[str]:
    problems = []
    for n in range(1, turns + 1):
        f = out / f'turn{n}.json'
        if not f.is_file() or not f.read_text().strip():
            problems.append(f'turn {n}: no output')
            continue
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError:
            problems.append(f'turn {n}: output is not JSON')
            continue
        if data.get('is_error') or data.get('subtype') != 'success':
            problems.append(f'turn {n}: {data.get("subtype")}')
    return problems


def meta(out: Path) -> tuple[dict[str, str], list[str]]:
    '''meta.txt's key=value lines, and its other lines.'''
    keys, other = {}, []
    path = out / 'meta.txt'
    for line in (path.read_text().splitlines() if path.is_file() else []):
        key, eq, value = line.partition('=')
        if eq and re.fullmatch(r'\w+', key):
            keys[key] = value
        elif line.strip():
            other.append(line)
    return keys, other


def names(items) -> set[str]:
    '''The names in an init record's skills or agents list: strings, or objects with a name.'''
    found = set()
    for item in items if isinstance(items, list) else []:
        if isinstance(item, dict):
            item = item.get('name')
        if isinstance(item, str):
            found.add(item)
    return found


def harness_problems(out: Path, turns: int) -> list[str]:
    '''C11's checks and the wait-ceiling deviation's: the kit hash before and
    after, the runner's own failures, each init record's kit skills and agents,
    and background tasks stopped at a turn's exit.'''
    problems = []
    keys, other = meta(out)
    before, after = keys.get('kit_sha_before', ''), keys.get('kit_sha_after', '')
    if not before or not after:
        problems.append('kit hash missing from meta.txt')
    elif before != after:
        problems.append(f'kit hash changed: before {before}, after {after}')
    if 'kit_error' in keys:
        problems.append(f'kit error: {keys["kit_error"]}')
    for line in other:
        hit = re.match(r'turn (\d+) exited (\d+)', line)
        if hit:
            problems.append(f'turn {hit.group(1)}: exited {hit.group(2)}')
    for n in range(1, turns + 1):
        f = out / f'turn{n}.init.json'
        if not f.is_file():
            if n == 1:
                problems.append('turn 1: no init record')
            continue
        try:
            init = json.loads(f.read_text())
        except json.JSONDecodeError:
            problems.append(f'turn {n}: init record is not JSON')
            continue
        if not isinstance(init, dict):
            problems.append(f'turn {n}: init record is not an object')
            continue
        for field, want in (('skills', KIT_SKILLS), ('agents', KIT_AGENTS)):
            missing = sorted(set(want) - names(init.get(field)))
            if missing:
                problems.append(f'turn {n}: init {field} lack {", ".join(missing)}')
    for n in range(1, turns + 1):
        err = out / f'turn{n}.stderr'
        if err.is_file() and BACKGROUND_STOPPED in err.read_text(errors='replace'):
            problems.append(f'turn {n}: background tasks still running at exit')
    return problems


# --- extract -----------------------------------------------------------------


def git(repdir: Path, *args: str) -> str:
    done = subprocess.run(['git', '-C', str(repdir), *args], capture_output=True, text=True, check=False)
    return done.stdout if done.returncode == 0 else f'(git {" ".join(args)} failed: {done.stderr.strip()})\n'


def capped(text: str, limit: int = CAP) -> str:
    lines = text.splitlines()
    if len(lines) <= limit:
        return text if text.endswith('\n') or not text else text + '\n'
    return '\n'.join(lines[:limit]) + f'\n[... {len(lines) - limit} more lines cut]\n'


def tool_line(name: str, data: dict) -> str:
    if name in ('Write', 'Edit', 'MultiEdit', 'NotebookEdit'):
        target = data.get('file_path') or data.get('notebook_path', '')
        size = len(str(data.get('content', data.get('new_string', ''))))
        return f'{name}: {target} ({size} chars)'
    if name in ('Agent', 'Task'):
        prompt = ' '.join(str(data.get('prompt', '')).split())[:300]
        return f'{name}: {data.get("subagent_type", "")}: {data.get("description", "")} | {prompt}'
    if name == 'Skill':
        return f'Skill: {data.get("skill", "")} {data.get("args", "")}'.rstrip()
    text = data.get('command', '') if name == 'Bash' else json.dumps(data, ensure_ascii=False)
    return f'{name}: {" ".join(str(text).split())[:300]}'


def transcript_lines(transcript: Path, prompts: list[str]) -> list[str]:
    lines = []
    for raw in transcript.read_text(errors='replace').splitlines():
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        content = (record.get('message') or {}).get('content')
        if record.get('type') == 'user' and isinstance(content, str):
            for n, prompt in enumerate(prompts, start=1):
                if prompt and content.strip().startswith(prompt.strip()[:60]):
                    lines.append(f'--- turn {n} prompt ---')
        lines += [tool_line(name, data) for name, data in tool_uses(record)]
    return lines


def file_text(path: Path, limit: int = 400) -> str:
    try:
        return capped(path.read_text(errors='replace'), limit)
    except OSError as e:
        return f'(unreadable: {e})\n'


def repo_section(repdir: Path, start: str) -> list[str]:
    starts = dict(pair.split('=', 1) for pair in start.split(',') if pair)
    base = starts.get('main', '')
    parts = ['## Repo at the end\n',
             '### Branches\n', git(repdir, 'for-each-ref', '--format=%(refname:short) %(objectname:short)', 'refs/heads'),
             '### Uncommitted\n', git(repdir, 'status', '--porcelain=v1', '--untracked-files=all') or '(clean)\n',
             '### New commits\n', git(repdir, 'log', '--all', '--format=%h %cs%d %s', '--not', *starts.values()) or '(none)\n']
    for branch in git(repdir, 'for-each-ref', '--format=%(refname:short)', 'refs/heads').split():
        frm = starts.get(branch, base)
        parts += [f'### {branch}: changes since {frm}\n', git(repdir, 'diff', '--stat', '-M', frm, branch),
                  capped(git(repdir, 'diff', '-M', frm, branch, '--', 'specs/'))]
    parts += ['### Uncommitted changes under specs/\n', capped(git(repdir, 'diff', 'HEAD', '--', 'specs/')) or '(none)\n']
    for rel in git(repdir, 'ls-files', '--others', '--exclude-standard').split() + git(
            repdir, 'ls-files', '--others', '--ignored', '--exclude-standard', '--', '.handoff').split():
        if rel.endswith('.md'):
            parts += [f'### Untracked: {rel}\n', file_text(repdir / rel)]
    return parts


def template_start(template: str) -> str:
    '''The repo section's start refs: main at the template's expected HEAD.'''
    rows = [line.split('\t') for line in HEADS.read_text().splitlines()[1:] if line.strip()] if HEADS.is_file() else []
    head = next((row[1] for row in rows if len(row) > 1 and row[0] == template), '')
    return f'main={head}' if head else ''


def registry_row(rep: str) -> list[str]:
    rows = [line.split('\t') for line in (CTL / 'registry.tsv').read_text().splitlines()[1:]]
    row = next((r for r in rows if r[0] == rep), None)
    if row is None or len(row) < 6:
        raise SystemExit(f'extract.py: {rep} has no full row in {CTL / "registry.tsv"}')
    return row


def build(rep: str) -> dict:
    _, arm, phase, template, kit, prompts = registry_row(rep)[:6]
    out = CTL / 'results' / rep
    home = posixpath.join(ROOT, rep)  # the HOME the rep ran with; the transcripts name it
    repo = posixpath.join(home, 'work', rep)
    repdir = CTL / 'homes' / rep / 'work' / rep  # the parked repo
    turns = prompts.split(',')
    transcripts = sorted((out / 'project').rglob('*.jsonl')) if (out / 'project').is_dir() else []
    problems = turn_problems(out, len(turns)) + harness_problems(out, len(turns))
    if not transcripts:
        problems.append('no transcript copied')
    flags = audit_transcripts(transcripts, repo, home, REAL, ROOT)
    denials, cost = collect_denials(out, len(turns)), 0.0
    for n in range(1, len(turns) + 1):
        try:
            data = json.loads((out / f'turn{n}.json').read_text())
        except (OSError, json.JSONDecodeError):
            continue
        cost += data.get('total_cost_usd') or 0.0
    audit = {'rep': rep, 'arm': arm, 'phase': phase, 'valid': not problems and not flags,
             'problems': problems, 'flags': flags, 'denials': denials, 'cost_usd': round(cost, 4)}
    (out / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n')

    prompt_texts = [(out / f'turn{n}.prompt.txt').read_text() if (out / f'turn{n}.prompt.txt').exists() else ''
                    for n in range(1, len(turns) + 1)]
    parts = [f'# {rep} — {arm} ({phase}; template {template}, kit {kit})\n\n',
             (out / 'meta.txt').read_text() if (out / 'meta.txt').exists() else '', '\n## Audit\n',
             f'- verdict: {"valid" if audit["valid"] else "VOID"}\n',
             f'- problems: {"; ".join(problems) or "none"}\n',
             f'- flags: {"; ".join(flags) or "none"}\n',
             f'- permission denials: {json.dumps(denials) if denials else "none"}\n',
             f'- cost: ${audit["cost_usd"]}\n']
    for n, prompt in enumerate(prompt_texts, start=1):
        result = ''
        try:
            result = json.loads((out / f'turn{n}.json').read_text()).get('result', '')
        except (OSError, json.JSONDecodeError):
            result = '(no result)'
        git_state = (out / f'turn{n}.git.txt').read_text() if (out / f'turn{n}.git.txt').exists() else ''
        parts += [f'\n## Turn {n}\n\n### Prompt\n\n{prompt}\n### Final message\n\n{result}\n\n',
                  f'### Repo after turn {n}\n\n{git_state}\n']
    parts.append('\n## Tool calls, in order\n\n')
    for transcript in transcripts:
        parts.append(f'### {transcript.relative_to(out / "project")}\n')
        parts += [f'- {line}\n' for line in transcript_lines(transcript, prompt_texts)]
    parts.append('\n')
    if repdir.is_dir():
        parts += repo_section(repdir, template_start(template))
    for root, label in ((out / 'handoffs', 'Brief directory'), (out / 'project' / 'memory', 'Memory')):
        if root.is_dir():
            for f in sorted(p for p in root.rglob('*') if p.is_file()):
                parts += [f'\n## {label}: {f.relative_to(root)}\n\n', file_text(f)]
    (out / 'extract.md').write_text(''.join(parts))
    return audit


def main() -> int:
    parser = argparse.ArgumentParser(description='Build rep extracts and audits.')
    parser.add_argument('batch', nargs='?')
    parser.add_argument('--rep', action='append', default=[])
    args = parser.parse_args()
    reps = list(args.rep)
    if args.batch:
        reps += [r for r in (CTL / 'batches' / f'{args.batch}.txt').read_text().split() if not r.startswith('#')]
    if not reps:
        parser.error('give a batch or --rep')
    for rep in reps:
        if not (CTL / 'results' / rep).is_dir():
            print(f'{rep}: no results yet')
            continue
        audit = build(rep)
        verdict = 'valid' if audit['valid'] else f'VOID: {"; ".join(audit["problems"] + audit["flags"])}'
        print(f'{rep} {audit["arm"]}: {verdict} (${audit["cost_usd"]}, {len(audit["denials"])} denial(s))')
    return 0


if __name__ == '__main__':
    sys.exit(main())
