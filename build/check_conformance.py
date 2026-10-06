#!/usr/bin/env python3
'''Claude Code guide conformance lint.

Checks the repo's Claude Code artifacts against the register,
build/cc_guide/conformance.toml, which maps each anchored section of
specs/guides/claude-code-customization-guide.md to the artifact kinds it
governs, to mechanical checks, and to recorded exceptions. Design:
specs/completed/claude-code-guide-conformance.md.

Run: uv run --python 3.13 --with pyyaml python build/check_conformance.py
Exit 0 when clean; 1 with one `<file>: <check> (<section>): <message>` line per
violation on stdout; 2 when the guide or the register is missing or is not
valid TOML, or git cannot list the repo's files, so a broken setup never looks
clean. Field-level register problems are violations, not errors.
'''
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import NamedTuple

import yaml

from check_frontmatter import READONLY_HEADING
from fences import fenced_lines, iter_code_blocks

REPO = Path(__file__).resolve().parent.parent
REGISTER = 'build/cc_guide/conformance.toml'
# A ## or ### ATX heading. The guide's sections are exactly these (drift R1.1).
HEADING_RE = re.compile(r'^#{2,3}[ \t]')
# A well-formed anchor: two or more dot-separated [a-z0-9-] segments.
ANCHOR_RE = re.compile(r'^<!-- cc: ([a-z0-9-]+(?:\.[a-z0-9-]+)+) -->$')
# Anything meant as an anchor, well-formed or not. `cc-guide:` (drift's
# citation and stamp markers) does not match: `cc` must be followed by `:`.
ANCHOR_LIKE_RE = re.compile(r'^<!--\s*cc:')


class Section(NamedTuple):
    line: int  # 1-based line of the heading
    heading: str
    id: str | None  # None when the heading has no well-formed, unique anchor


class Violation(NamedTuple):
    file: str
    check: str
    section: str  # a section ID, several joined by ', ', or '-'
    message: str
    value: int | None = None  # the measured number, for a numeric check
    waivable: bool = True  # False when the check could not evaluate the file

    def render(self) -> str:
        return f'{self.file}: {self.check} ({self.section}): {self.message}'


def guide_sections(text: str, path: str) -> tuple[list[Section], list[Violation]]:
    '''The guide's ## and ### headings outside fenced code, each with the ID of
    the anchor on its next line, plus one violation per missing, malformed,
    stray or repeated anchor (R1.1, R3.3 rule 1).'''
    lines = text.split('\n')
    fenced = fenced_lines(text)
    sections: list[Section] = []
    out: list[Violation] = []
    under_heading: set[int] = set()
    first_line: dict[str, int] = {}
    for n, line in enumerate(lines, start=1):
        if n in fenced or not HEADING_RE.match(line):
            continue
        nxt = lines[n] if n < len(lines) else ''
        anchor = None
        m = ANCHOR_RE.match(nxt)
        if m:
            under_heading.add(n + 1)
            if m.group(1) in first_line:
                out.append(Violation(path, 'anchor', m.group(1),
                                     f'line {n + 1}: anchor repeats line {first_line[m.group(1)]}'))
            else:
                first_line[m.group(1)] = n + 1
                anchor = m.group(1)
        elif ANCHOR_LIKE_RE.match(nxt):
            under_heading.add(n + 1)
            out.append(Violation(path, 'anchor', '-', f'line {n + 1}: malformed anchor {nxt.strip()!r}'))
        else:
            out.append(Violation(path, 'anchor', '-',
                                 f'line {n}: heading {line.strip()!r} has no anchor on its next line'))
        sections.append(Section(n, line.strip(), anchor))
    for n, line in enumerate(lines, start=1):
        if n not in fenced and n not in under_heading and ANCHOR_LIKE_RE.match(line):
            out.append(Violation(path, 'anchor', '-', f'line {n}: anchor is not directly under a heading'))
    return sections, out


class SetupError(Exception):
    '''The guide or the register is missing or unreadable: exit 2, so a
    broken setup never passes as a clean run (R3.2).'''


class Kind(NamedTuple):
    globs: list[str]
    exclude: list[str]
    sections: list[str]


class Check(NamedTuple):
    id: str
    kinds: list[str]
    sections: list[str]
    enforced_by: str
    params: dict  # every key beyond CHECK_FIELDS: values taken from the guide


class Register(NamedTuple):
    kinds: dict[str, Kind]
    unmapped: dict[str, str]
    checks: list[Check]


CHECK_FIELDS = frozenset({'id', 'kind', 'sections', 'type', 'rule', 'enforced_by'})
ENFORCERS = ('check_conformance', 'check_frontmatter')


def load_register(root: Path) -> dict:
    path = root / REGISTER
    try:
        return tomllib.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        raise SetupError(f'{REGISTER}: register not found') from None
    except UnicodeDecodeError as exc:
        raise SetupError(f'{REGISTER}: not valid TOML (not UTF-8: {exc.reason})') from None
    except tomllib.TOMLDecodeError as exc:
        raise SetupError(f'{REGISTER}: not valid TOML ({exc})') from None


def load_guide(root: Path, raw: dict) -> tuple[str, str]:
    '''The guide's repo-relative path, from [guide] path, and its text.'''
    guide = raw.get('guide')
    path = guide.get('path') if isinstance(guide, dict) else None
    if not isinstance(path, str) or not path:
        raise SetupError(f'{REGISTER}: [guide] path is missing')
    try:
        return path, (root / path).read_text(encoding='utf-8')
    except OSError:
        raise SetupError(f'{path}: guide not found') from None
    except UnicodeDecodeError as exc:
        raise SetupError(f'{path}: guide is not UTF-8 ({exc.reason})') from None


def _str_list(value, nonempty: bool = True) -> bool:
    return (isinstance(value, list) and all(isinstance(v, str) and v for v in value)
            and (bool(value) or not nonempty))


def _nonempty_str(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def parse_register(raw: dict) -> tuple[Register, list[Violation]]:
    '''The register's kinds, unmapped sections and checks, keeping only the
    structurally usable entries. Each field-level problem is a violation, never
    an error (R2.3-R2.5, R3.2).'''
    out: list[Violation] = []

    def bad(message: str) -> None:
        out.append(Violation(REGISTER, 'register', '-', message))

    raw_kinds = raw.get('kinds')
    if not isinstance(raw_kinds, dict):
        bad('[kinds] must be a table of kinds')
        raw_kinds = {}
    kinds: dict[str, Kind] = {}
    for name, k in raw_kinds.items():
        if not isinstance(k, dict):
            bad(f'kinds.{name} must be a table')
            continue
        structural = []
        if not _str_list(k.get('globs')):
            structural.append('globs must be a non-empty list of strings')
        if not _str_list(k.get('exclude', []), nonempty=False):
            structural.append('exclude must be a list of strings')
        if not _str_list(k.get('sections')):
            structural.append('sections must be a non-empty list of strings')
        for problem in structural:
            bad(f'kinds.{name}: {problem}')
        if not _nonempty_str(k.get('description')):
            bad(f'kinds.{name}: description must be a non-empty string')
        if not structural:
            kinds[name] = Kind(k['globs'], k.get('exclude', []), k['sections'])

    raw_unmapped = raw.get('unmapped', {})
    if not isinstance(raw_unmapped, dict):
        bad('[unmapped] must be a table')
        raw_unmapped = {}
    unmapped = {}
    for sid, reason in raw_unmapped.items():
        if _nonempty_str(reason):
            unmapped[sid] = reason
        else:
            bad(f'[unmapped] {sid}: the reason must be a non-empty string')

    raw_checks = raw.get('check', [])
    if not isinstance(raw_checks, list):
        bad('[[check]] must be an array of tables')
        raw_checks = []
    checks: list[Check] = []
    for i, c in enumerate(raw_checks, start=1):
        if not isinstance(c, dict):
            bad(f'check #{i} must be a table')
            continue
        cid = c.get('id')
        label = f'check {cid}' if _nonempty_str(cid) else f'check #{i}'
        kind = c.get('kind')
        kind_list = [kind] if isinstance(kind, str) else kind
        structural = []
        if not _nonempty_str(cid):
            structural.append('id must be a non-empty string')
        if not _str_list(kind_list):
            structural.append('kind must name a kind, or list kinds')
        else:
            unknown = [k for k in kind_list if k not in raw_kinds]
            if unknown:
                structural.append(f'kind names no [kinds] table: {", ".join(unknown)}')
        if not _str_list(c.get('sections')):
            structural.append('sections must be a non-empty list of strings')
        if c.get('enforced_by') not in ENFORCERS:
            structural.append('enforced_by must be check_conformance or check_frontmatter')
        problems = list(structural)
        if c.get('type') not in ('fact', 'advice'):
            problems.append('type must be fact or advice')
        if not _nonempty_str(c.get('rule')):
            problems.append('rule must be a non-empty string')
        for problem in problems:
            bad(f'{label}: {problem}')
        if not structural:
            params = {k: v for k, v in c.items() if k not in CHECK_FIELDS}
            checks.append(Check(cid, kind_list, c['sections'], c['enforced_by'], params))
    return Register(kinds, unmapped, checks), out


def section_violations(reg: Register, anchors: list[str]) -> list[Violation]:
    '''Every section ID the register cites is an anchor, and every anchor is
    mapped to a kind or listed in [unmapped], never both (R2.4, R3.3 rule 1).'''
    known = set(anchors)
    out: list[Violation] = []

    def cite(where: str, ids) -> None:
        for sid in ids:
            if sid not in known:
                out.append(Violation(REGISTER, 'section-id', sid,
                                     f'{where} cites a section with no anchor in the guide'))

    for name, kind in reg.kinds.items():
        cite(f'kinds.{name}', kind.sections)
    cite('[unmapped]', reg.unmapped)
    for check in reg.checks:
        cite(f'check {check.id}', check.sections)
    mapped = {sid for kind in reg.kinds.values() for sid in kind.sections}
    for sid in anchors:
        if sid in mapped and sid in reg.unmapped:
            out.append(Violation(REGISTER, 'section-map', sid,
                                 'section is both mapped to a kind and listed in [unmapped]'))
        elif sid not in mapped and sid not in reg.unmapped:
            out.append(Violation(REGISTER, 'section-map', sid,
                                 'section is neither mapped to a kind nor listed in [unmapped]'))
    return out


class Finding(NamedTuple):
    '''One problem a check found; run_checks adds the check's ID and sections.
    waivable is False when the check could not evaluate the file, so no
    exception may hide the finding or be kept alive by it.'''
    file: str
    message: str
    value: int | None = None
    waivable: bool = True


def git_env() -> dict[str, str]:
    '''os.environ without git's repo-local variables, as install.py's git_env:
    a hook or shell may export GIT_DIR or GIT_INDEX_FILE for another repo.'''
    local = subprocess.run(['git', 'rev-parse', '--local-env-vars'],
                           capture_output=True, text=True, check=True).stdout.split()
    return {name: value for name, value in os.environ.items() if name not in local}


def kept_files(root: Path) -> list[str]:
    '''Repo-relative POSIX paths of the files git keeps under root: tracked, or
    untracked and not ignored, as install.py's kept_files lists them (R2.3).'''
    try:
        listing = subprocess.run(
            ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
            cwd=root, env=git_env(), capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SetupError(f'cannot list the files git keeps under {root} ({exc})') from None
    paths = [os.fsdecode(entry) for entry in listing.split(b'\0') if entry]
    # --cached also lists tracked files deleted from the working tree.
    return sorted(p for p in paths if (root / p).exists() or (root / p).is_symlink())


def kind_files(reg: Register, files: list[str]) -> dict[str, list[str]]:
    '''Each kind's files: those that full-match one of its globs and none of its
    excludes. full_match anchors every glob at the repo root and keeps `*`
    inside one path segment, so skills/*/SKILL.md never reaches a copy nested
    under specs/.'''
    return {
        name: [f for f in files
               if any(PurePosixPath(f).full_match(g) for g in kind.globs)
               and not any(PurePosixPath(f).full_match(e) for e in kind.exclude)]
        for name, kind in reg.kinds.items()
    }


FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.S)
# A full model ID, as the guide's subagent `model` row allows beside the aliases.
FULL_MODEL_RE = re.compile(r'claude-[a-z0-9][a-z0-9.-]*')


def frontmatter(text: str) -> dict | None:
    '''The leading YAML frontmatter as a mapping; None when absent or unparseable.'''
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    return fm if isinstance(fm, dict) else None


def tool_list(fm: dict) -> list[str] | None:
    '''An agent's tools, from a comma-separated string or a YAML list; None when unset.'''
    tools = fm.get('tools')
    if tools is None:
        return None
    items = tools if isinstance(tools, list) else str(tools).split(',')
    return [str(t).strip() for t in items if str(t).strip()]


def read_artifacts(root: Path, files: list[str], out: list[Finding]):
    '''Yield (file, text) for each file that reads as UTF-8. A dangling link or
    a file that is not UTF-8 gets an unwaivable finding in out instead.'''
    for f in files:
        try:
            yield f, (root / f).read_text(encoding='utf-8')
        except OSError as exc:
            out.append(Finding(f, f'cannot read: {exc.strerror}', waivable=False))
        except UnicodeDecodeError as exc:
            out.append(Finding(f, f'cannot read: not UTF-8 ({exc.reason})', waivable=False))


def check_agent_fields(root: Path, files: list[str], params: dict) -> list[Finding]:
    fields, models = set(params['fields']), set(params['models'])
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        fm = frontmatter(text)
        if fm is None:
            out.append(Finding(f, 'no parseable YAML frontmatter'))
            continue
        for key in fm:
            if key not in fields:
                out.append(Finding(f, f'frontmatter key {key!r} is not a documented agent field'))
        model = fm.get('model')
        if model is not None and str(model) not in models and not FULL_MODEL_RE.fullmatch(str(model)):
            out.append(Finding(f, f'model {model!r} is neither a listed alias nor a full claude- model ID'))
    return out


def check_readonly_agent_tools(root: Path, files: list[str], params: dict) -> list[Finding]:
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        if not any(line.strip() == READONLY_HEADING for line in text.splitlines()):
            continue
        fm = frontmatter(text) or {}
        tools = tool_list(fm)
        if tools is None:
            out.append(Finding(f, 'read-only agent sets no tools list, so it inherits every tool'))
        else:
            editing = [t for t in params['forbidden_tools'] if t in tools]
            if editing:
                out.append(Finding(f, f'read-only agent lists {", ".join(editing)}'))
        if 'memory' in fm:
            out.append(Finding(f, 'read-only agent sets memory, which adds Read, Write and Edit'))
    return out


def check_bash_search_tools(root: Path, files: list[str], params: dict) -> list[Finding]:
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        tools = tool_list(frontmatter(text) or {}) or []
        search = [t for t in ('Grep', 'Glob') if t in tools]
        if 'Bash' in tools and search:
            out.append(Finding(f, f'lists {" and ".join(search)} beside Bash, where both are '
                                  'absent and search runs through the shell'))
    return out


class HookCommand(NamedTuple):
    file: str
    where: str  # 'JSON block at line N: ' for Markdown, '' for a JSON file
    event: str
    command: str


def hook_commands(root: Path, files: list[str]) -> tuple[list[HookCommand], list[Finding]]:
    '''Every command hook in the hooks tree of each ```json block in the
    Markdown files and of each JSON file, plus an unwaivable finding per block
    or file that does not parse or read. Other files are skipped.'''
    found: list[HookCommand] = []
    problems: list[Finding] = []
    wiring = [f for f in files if f.endswith(('.md', '.json'))]
    for f, text in read_artifacts(root, wiring, problems):
        if f.endswith('.md'):
            docs = [(f'JSON block at line {b.line}', b.code)
                    for b in iter_code_blocks(text, ('json',))]
        else:
            docs = [('', text)]
        for label, source in docs:
            try:
                data = json.loads(source)
            except json.JSONDecodeError as exc:
                problems.append(Finding(f, f'{label or "file"} does not parse ({exc.msg})',
                                        waivable=False))
                continue
            where = f'{label}: ' if label else ''
            hooks = data.get('hooks') if isinstance(data, dict) else None
            for event, groups in (hooks.items() if isinstance(hooks, dict) else ()):
                for group in (groups if isinstance(groups, list) else ()):
                    inner = group.get('hooks') if isinstance(group, dict) else None
                    for hook in (inner if isinstance(inner, list) else ()):
                        if isinstance(hook, dict) and isinstance(hook.get('command'), str):
                            found.append(HookCommand(f, where, event, hook['command']))
    return found, problems


def _identifier_char(text: str, i: int) -> bool:
    return i < len(text) and (text[i].isalnum() or text[i] == '_')


def unquoted_var_uses(command: str, var: str) -> list[str]:
    '''The quote state, 'unquoted' or 'single-quoted', of each $var or ${var} in
    a shell command that is not inside double quotes. A single-quoted use
    never expands, so it counts too. Empty when every use is double-quoted.'''
    plain, braced = '$' + var, '${' + var + '}'
    states: list[str] = []
    quote = ''  # '', "'" or '"'
    i = 0
    while i < len(command):
        ch = command[i]
        if ch == '\\' and quote != "'":
            i += 2  # an escaped character, $ included, is literal
            continue
        if not quote and ch in '\'"':
            quote = ch
        elif ch == quote:
            quote = ''
        elif ch == '$' and (command.startswith(braced, i) or (
                command.startswith(plain, i) and not _identifier_char(command, i + len(plain)))):
            if quote != '"':
                states.append('single-quoted' if quote else 'unquoted')
        i += 1
    return states


def check_hook_dir_quoted(root: Path, files: list[str], params: dict) -> list[Finding]:
    found, out = hook_commands(root, files)
    for hook in found:
        for state in unquoted_var_uses(hook.command, 'CLAUDE_PROJECT_DIR'):
            out.append(Finding(hook.file, f'{hook.where}{hook.event} command leaves '
                                          f'$CLAUDE_PROJECT_DIR {state}'))
    return out


def check_stop_hook_guard(root: Path, files: list[str], params: dict) -> list[Finding]:
    found, _ = hook_commands(root, files)  # hook-dir-quoted reports parse failures
    scripts = {PurePosixPath(f).name: f for f in files if f.endswith(('.sh', '.py'))}
    out: list[Finding] = []
    for hook in found:
        if hook.event != 'Stop':
            continue
        try:
            words = shlex.split(hook.command)
        except ValueError:
            words = []
        script = scripts.get(PurePosixPath(words[0]).name) if words else None
        if script is None:
            out.append(Finding(hook.file, f'{hook.where}Stop command {hook.command!r} names '
                                          'no hook script in the repo'))
            continue
        for _, source in read_artifacts(root, [script], out):
            if 'stop_hook_active' not in source:
                out.append(Finding(hook.file, f'{hook.where}Stop command runs {script}, which '
                                              'never reads stop_hook_active'))
    return out


def check_claude_md_size(root: Path, files: list[str], params: dict) -> list[Finding]:
    limit = params['limit']
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        n = text.count('\n')  # what wc -l counts
        if n >= limit:
            out.append(Finding(f, f'{n} lines; the guide targets fewer than {limit}', n))
    return out


def check_rule_paths(root: Path, files: list[str], params: dict) -> list[Finding]:
    always_on = set(params['always_on'])
    out: list[Finding] = []
    readable: list[str] = []
    for f in files:
        path = root / f
        if (f.startswith('.claude/rules/') and path.is_symlink()
                and not path.resolve().is_relative_to(root.resolve())):
            out.append(Finding(f, 'link resolves outside the repo, so Claude Code treats '
                                  'it as an external import'))
        elif not path.exists():
            out.append(Finding(f, 'link target does not exist', waivable=False))
        else:
            readable.append(f)
    for f, text in read_artifacts(root, readable, out):
        paths = (frontmatter(text) or {}).get('paths')
        if f in always_on:
            if paths is not None:
                out.append(Finding(f, 'always_on lists this rule, but it sets paths'))
        elif not _str_list(paths):
            out.append(Finding(f, 'frontmatter sets no non-empty paths list, so the rule loads '
                                  'in every session'))
    return out


# Quoted phrases in a skill description: double or curly quotes, or single quotes
# that open at a word boundary, so an apostrophe inside a word never opens one.
QUOTED_PHRASE_RE = re.compile(
    r"\"[^\"\n]+\"|“[^”\n]+”|(?<!\w)'(?:[^'\n]|(?<=\w)'(?=\w))+'(?!\w)")
INLINE_CODE_RE = re.compile(r'`[^`\n]*`')
ANY_HEADING_RE = re.compile(r'#{1,6}[ \t]')
# The substitutions the guide lists that need no declaration: $ARGUMENTS, a
# positional $0, $1, ..., and a ${CLAUDE_...} session variable. A leading
# backslash escapes one. Declared argument names are added per file.
SUBSTITUTION_BASE = r'ARGUMENTS\b|\d+|\{CLAUDE_\w+\}'
INLINE_SHELL_RE = re.compile(r'!`[^`\n]+`')
SHELL_FENCE_RE = re.compile(r'^[ \t]*`{3,}!')
SKILL_PATH_RE = re.compile(r'(?:\.claude/)?skills/([^/]+)/SKILL\.md')
SKILL_DIR_RE = re.compile(r'((?:\.claude/)?skills/([^/]+))/.+')


def skill_body(text: str) -> tuple[str, int]:
    '''The text after the leading frontmatter and how many lines the
    frontmatter took, so a body line number maps to a file line number.'''
    m = FRONTMATTER_RE.match(text)
    return (text[m.end():], text[:m.end()].count('\n')) if m else (text, 0)


def description_text(fm: dict) -> str:
    '''description and when_to_use, which the guide says share one listing entry.'''
    return ' '.join(str(fm[k]) for k in ('description', 'when_to_use') if fm.get(k) is not None)


def check_compaction_window(root: Path, files: list[str], params: dict) -> list[Finding]:
    tokens, per_token = params['tokens'], params['chars_per_token']
    window = tokens * per_token
    heading = re.compile(r'\b(?:' + '|'.join(re.escape(w) for w in params['headings']) + r')\b', re.I)
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        body, first = skill_body(text)
        if len(body) <= window:
            continue
        out.append(Finding(f, f'body is about {len(body) // per_token} tokens; '
                              f'compaction re-attaches only the first {tokens}'))
        fenced = fenced_lines(body)
        offset = 0
        for n, line in enumerate(body.split('\n'), start=1):
            if offset >= window and n not in fenced and ANY_HEADING_RE.match(line) and heading.search(line):
                out.append(Finding(f, f'line {first + n}: heading {line.strip()!r} starts past the '
                                      f'first {tokens} tokens, so compaction drops it'))
            offset += len(line) + 1
    return out


def check_description_person(root: Path, files: list[str], params: dict) -> list[Finding]:
    pronoun = re.compile(r"(?<![\w'])(?:" + '|'.join(re.escape(p) for p in params['pronouns']) + r')(?!\w)',
                         re.I)
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        fm = frontmatter(text)
        if fm is None:
            continue  # check_frontmatter owns a missing or broken frontmatter
        bare = INLINE_CODE_RE.sub('', QUOTED_PHRASE_RE.sub('', description_text(fm)))
        found = sorted({m.group(0).lower() for m in pronoun.finditer(bare)})
        if found:
            out.append(Finding(f, 'description uses first- or second-person '
                                  f'{", ".join(repr(p) for p in found)} outside quoted phrases'))
    return out


def check_trigger_phrase_presence(root: Path, files: list[str], params: dict) -> list[Finding]:
    # A heuristic: it finds the two forms the repo's descriptions use, a quoted
    # phrase and a "Trigger on" list, and misses any other way to name a trigger.
    markers = [m.lower() for m in params['markers']]
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        fm = frontmatter(text)
        if fm is None:
            continue
        desc = description_text(fm)
        if not QUOTED_PHRASE_RE.search(desc) and not any(m in desc.lower() for m in markers):
            out.append(Finding(f, 'description has neither a quoted trigger phrase nor a "Trigger on" list'))
    return out


def check_substitution_hazard(root: Path, files: list[str], params: dict) -> list[Finding]:
    # Substitution and !`command` rendering are preprocessing of the whole
    # body: the guide gives no fenced-code exemption and names `\$` as the
    # only escape, so a fenced $ARGUMENTS is still a hazard.
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        body, first = skill_body(text)
        declared = (frontmatter(text) or {}).get('arguments')
        names = declared.split() if isinstance(declared, str) else [str(a) for a in declared or []]
        names = [re.escape(n.strip('[],')) + r'\b' for n in names if n.strip('[],')]
        token = re.compile(r'(?<!\\)\$(?:' + '|'.join([SUBSTITUTION_BASE, *names]) + ')')
        for n, line in enumerate(body.split('\n'), start=1):
            where = f'line {first + n}'
            for m in token.finditer(line):
                out.append(Finding(f, f'{where}: {m.group(0)!r} is substituted when the skill loads; '
                                      f'escape it as \\{m.group(0)}'))
            for m in INLINE_SHELL_RE.finditer(line):
                out.append(Finding(f, f'{where}: {m.group(0)!r} runs a shell command at render time, '
                                      'before Claude sees the body'))
            if SHELL_FENCE_RE.match(line):
                out.append(Finding(f, f'{where}: a ```! fence runs a shell command at render time, '
                                      'before Claude sees the body'))
    return out


def _matches_any(rel: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(rel, p) or fnmatch.fnmatchcase(PurePosixPath(rel).name, p)
               for p in patterns)


def _names(text: str, word: str, directory: bool = False) -> bool:
    '''Whether text mentions word as a whole file name, or as a directory
    written with its trailing slash and not as the start of a longer path.'''
    tail = r'/(?![\w.-])' if directory else r'(?![\w-])'
    return re.search(r'(?<![\w.-])' + re.escape(word) + tail, text) is not None


def check_orphan_bundled_file(root: Path, files: list[str], params: dict) -> list[Finding]:
    # A file counts as named when any other text file in its skill, tests
    # aside, mentions its file name, or the directory it sits in.
    by_skill: dict[str, list[str]] = {}
    for f in files:
        parts = PurePosixPath(f).parts
        at = parts.index('skills')
        if len(parts) > at + 2:
            by_skill.setdefault('/'.join(parts[:at + 2]), []).append('/'.join(parts[at + 2:]))
    out: list[Finding] = []
    for skill, rels in sorted(by_skill.items()):
        texts: dict[str, str] = {}
        for rel in rels:
            if _matches_any(rel, params['tests']):
                continue
            try:
                texts[rel] = (root / skill / rel).read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                pass  # a binary or dangling file names nothing
        for rel in sorted(rels):
            if _matches_any(rel, params['exempt']) or _matches_any(rel, params['tests']):
                continue
            parts = PurePosixPath(rel).parts
            dirs = ['/'.join(parts[:i]) for i in range(1, len(parts))]
            if not any(_names(text, parts[-1]) or any(_names(text, d, directory=True) for d in dirs)
                       for other, text in texts.items() if other != rel):
                out.append(Finding(f'{skill}/{rel}', f'no file in the skill names {parts[-1]}, '
                                                     'by file name or by its directory'))
    return out


def skill_names(files: list[str]) -> dict[str, str]:
    '''Each skill's directory name and the SKILL.md that holds it.'''
    out: dict[str, str] = {}
    for f in files:
        m = SKILL_PATH_RE.fullmatch(f)
        if m:
            out.setdefault(m.group(1), f)
    return out


def command_names(files: list[str]) -> dict[str, str]:
    '''Each command's filename stem and its file.'''
    return {PurePosixPath(f).stem: f for f in files
            if f.startswith('commands/') and f.endswith('.md') and f.count('/') == 1}


def check_skill_command_name_collision(root: Path, files: list[str], params: dict) -> list[Finding]:
    skills = skill_names(files)
    return [Finding(f, f'command /{name} shares its name with {skills[name]}, '
                       'and on a name collision the skill wins')
            for name, f in command_names(files).items() if name in skills]


def check_command_frontmatter_keys(root: Path, files: list[str], params: dict) -> list[Finding]:
    fields = set(params['fields'])
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        fm = frontmatter(text)
        if fm is None:
            if FRONTMATTER_RE.match(text):
                out.append(Finding(f, 'frontmatter does not parse as YAML'))
            continue  # no frontmatter is allowed: every field is optional
        for key in fm:
            if key == 'name':
                out.append(Finding(f, f'frontmatter key {key!r} is not allowed in a command: '
                                      'the filename is its name'))
            elif key == 'paths':
                out.append(Finding(f, f'frontmatter key {key!r} is not allowed in a command'))
            elif key not in fields:
                out.append(Finding(f, f'frontmatter key {key!r} is not a documented skill field'))
    return out


def check_builtin_name_shadow(root: Path, files: list[str], params: dict) -> list[Finding]:
    builtins = {b.lower() for b in params['builtins']}
    message = ('{kind} /{name} takes the name of the built-in /{name}, '
               'and a skill or command with a built-in name replaces it')
    out: list[Finding] = []
    for f in files:
        commands = command_names([f])
        names = list(commands)
        kind = 'command'
        if not commands:
            kind = 'skill'
            skill = SKILL_PATH_RE.fullmatch(f)
            names = [skill.group(1)] if skill else []
            for _, text in read_artifacts(root, [f] if skill else [], out):
                declared = (frontmatter(text) or {}).get('name')
                if isinstance(declared, str) and declared not in names:
                    names.append(declared)
        for name in names:
            if name.lower() in builtins:
                out.append(Finding(f, message.format(kind=kind, name=name)))
                break
    return out


def check_reserved_skill_name(root: Path, files: list[str], params: dict) -> list[Finding]:
    reserved = set(params['reserved'])
    dirs = {m.group(1): m.group(2) for f in files if (m := SKILL_DIR_RE.fullmatch(f))}
    return [Finding(path, f'directory name {name!r} is reserved for claude.ai skills '
                          'synced into terminal sessions')
            for path, name in sorted(dirs.items()) if name in reserved]


# Each check_conformance check: its function and the parameters the register
# must give it ('integer', or 'strings' for a list of strings).
CHECKS = {
    'claude-md-size': (check_claude_md_size, {'limit': 'integer'}),
    'rule-paths': (check_rule_paths, {'always_on': 'strings'}),
    'hook-dir-quoted': (check_hook_dir_quoted, {}),
    'stop-hook-guard': (check_stop_hook_guard, {}),
    'agent-fields': (check_agent_fields, {'fields': 'strings', 'models': 'strings'}),
    'readonly-agent-tools': (check_readonly_agent_tools, {'forbidden_tools': 'strings'}),
    'bash-search-tools': (check_bash_search_tools, {}),
    'compaction-window': (check_compaction_window, {
        'tokens': 'integer', 'chars_per_token': 'integer', 'headings': 'strings'}),
    'description-person': (check_description_person, {'pronouns': 'strings'}),
    'trigger-phrase-presence': (check_trigger_phrase_presence, {'markers': 'strings'}),
    'substitution-hazard': (check_substitution_hazard, {}),
    'orphan-bundled-file': (check_orphan_bundled_file, {'exempt': 'strings', 'tests': 'strings'}),
    'skill-command-name-collision': (check_skill_command_name_collision, {}),
    'command-frontmatter-keys': (check_command_frontmatter_keys, {'fields': 'strings'}),
    'builtin-name-shadow': (check_builtin_name_shadow, {'builtins': 'strings'}),
    'reserved-skill-name': (check_reserved_skill_name, {'reserved': 'strings'}),
}
PARAM_TYPES = {
    'integer': (lambda v: isinstance(v, int) and not isinstance(v, bool), 'an integer'),
    'strings': (lambda v: _str_list(v, nonempty=False), 'a list of strings'),
}


def _runnable(check: Check) -> bool:
    if check.enforced_by != 'check_conformance' or check.id not in CHECKS:
        return False
    return all(PARAM_TYPES[kind][0](check.params.get(name))
               for name, kind in CHECKS[check.id][1].items())


def implementation_violations(reg: Register) -> list[Violation]:
    '''Every check_conformance entry has an implementation with its parameters,
    every implementation has an entry, and check IDs are unique (R3.3 rules 2-3).'''
    out: list[Violation] = []
    ids = [c.id for c in reg.checks]
    for cid in sorted(set(ids)):
        if ids.count(cid) > 1:
            out.append(Violation(REGISTER, 'duplicate-id', '-',
                                 f'check ID {cid} appears {ids.count(cid)} times'))
    entries = set()
    for check in reg.checks:
        if check.enforced_by != 'check_conformance':
            continue
        entries.add(check.id)
        if check.id not in CHECKS:
            out.append(Violation(REGISTER, 'check-impl', ', '.join(check.sections),
                                 f'check {check.id} has no implementation in build/check_conformance.py'))
            continue
        for name, kind in CHECKS[check.id][1].items():
            valid, wanted = PARAM_TYPES[kind]
            if not valid(check.params.get(name)):
                out.append(Violation(REGISTER, 'register', '-',
                                     f'check {check.id}: parameter {name} must be {wanted}'))
    for cid in sorted(set(CHECKS) - entries):
        out.append(Violation('build/check_conformance.py', 'check-impl', '-',
                             f'implementation {cid} has no [[check]] entry'))
    return out


def run_checks(root: Path, reg: Register, kinds: dict[str, list[str]]) -> list[Violation]:
    '''Run each runnable check once over the files of its kinds.'''
    out: list[Violation] = []
    done: set[str] = set()
    for check in reg.checks:
        if check.id in done or not _runnable(check):
            continue
        done.add(check.id)
        func = CHECKS[check.id][0]
        files = sorted({f for kind in check.kinds for f in kinds.get(kind, [])})
        for found in func(root, files, check.params):
            out.append(Violation(found.file, check.id, ', '.join(check.sections),
                                 found.message, found.value, found.waivable))
    return out


class ExceptionEntry(NamedTuple):
    id: str
    check: str | None  # the waived check_conformance check, if any
    artifacts: list[str]
    reason: str
    ceiling: int | None


# Checks whose findings carry a measured value that a waiver's ceiling caps.
NUMERIC_CHECKS = frozenset({'claude-md-size'})
GLOB_CHAR_RE = re.compile(r'[*?\[]')


def parse_exceptions(raw: dict, reg: Register, anchors: list[str], files: list[str],
                     root: Path) -> tuple[list[ExceptionEntry], list[Violation]]:
    '''The register's usable exceptions, plus a violation per missing or
    inconsistent field (R2.6, R3.3 rule 3). An exception waives only when its
    id, check and artifacts are all usable.'''
    raw_exceptions = raw.get('exception', [])
    if not isinstance(raw_exceptions, list):
        return [], [Violation(REGISTER, 'register', '-', '[[exception]] must be an array of tables')]
    conformance = {c.id for c in reg.checks if c.enforced_by == 'check_conformance'}
    known = set(anchors)
    out: list[Violation] = []
    entries: list[ExceptionEntry] = []
    ids: list[str] = []
    for i, e in enumerate(raw_exceptions, start=1):
        if not isinstance(e, dict):
            out.append(Violation(REGISTER, 'exception', '-', f'exception #{i} must be a table'))
            continue
        eid = e.get('id')
        label = f'exception {eid}' if _nonempty_str(eid) else f'exception #{i}'
        problems: list[str] = []
        if _nonempty_str(eid):
            ids.append(eid)
        else:
            problems.append('id must be a non-empty string')
        etype = e.get('type')
        if etype not in ('deviation', 'gap'):
            problems.append('type must be deviation or gap')
        for field in ('guide', 'reason', 'evidence'):
            if not _nonempty_str(e.get(field)):
                problems.append(f'{field} must be a non-empty string')
        if etype == 'deviation':
            if not _nonempty_str(e.get('revisit')):
                problems.append('a deviation needs revisit')
            if 'tracked_in' in e:
                problems.append('a deviation takes no tracked_in')
        elif etype == 'gap':
            if not _nonempty_str(e.get('tracked_in')):
                problems.append('a gap needs tracked_in')
            if 'revisit' in e:
                problems.append('a gap takes no revisit')
        protects = e.get('protects', [])
        if not (_str_list(protects, nonempty=False) and set(protects) <= {'codex', 'gemini'}):
            problems.append('protects may list only codex and gemini')
        sections = e.get('sections')
        if _str_list(sections):
            for sid in sections:
                if sid not in known:
                    out.append(Violation(REGISTER, 'section-id', sid,
                                         f'{label} cites a section with no anchor in the guide'))
        else:
            problems.append('sections must be a non-empty list of strings')
        check = e.get('check')
        if check is not None and not isinstance(check, str):
            check_ok = False
            problems.append('check must name one check_conformance check')
        else:
            check_ok = check is None or check in conformance
            if not check_ok:
                problems.append(f'check {check} is not a check_conformance check')
        numeric = isinstance(check, str) and check in NUMERIC_CHECKS
        ceiling = e.get('ceiling')
        ceiling_ok = isinstance(ceiling, int) and not isinstance(ceiling, bool)
        if numeric and not ceiling_ok:
            problems.append(f'a waiver of {check} needs an integer ceiling')
        elif not numeric and ceiling is not None:
            problems.append('ceiling applies only to a numeric check '
                            f'({", ".join(sorted(NUMERIC_CHECKS))})')
        artifacts = e.get('artifacts')
        artifacts_ok = _str_list(artifacts)
        if not artifacts_ok:
            problems.append('artifacts must be a non-empty list of strings')
        elif check is not None:
            for a in artifacts:
                if GLOB_CHAR_RE.search(a):
                    problems.append(f'with check set, artifacts must be explicit paths: {a}')
                    artifacts_ok = False
                elif not ((root / a).exists() or (root / a).is_symlink()):
                    problems.append(f'artifact {a} does not exist')
                    artifacts_ok = False
        else:
            for a in artifacts:
                if not any(PurePosixPath(f).full_match(a) for f in files):
                    problems.append(f'artifact glob {a} matches no file')
                    artifacts_ok = False
        for problem in problems:
            out.append(Violation(REGISTER, 'exception', '-', f'{label}: {problem}'))
        if _nonempty_str(eid) and check_ok and artifacts_ok:
            entries.append(ExceptionEntry(eid, check, artifacts, str(e.get('reason', '')),
                                          ceiling if ceiling_ok else None))
    for eid in sorted(set(ids)):
        if ids.count(eid) > 1:
            out.append(Violation(REGISTER, 'duplicate-id', '-',
                                 f'exception ID {eid} appears {ids.count(eid)} times'))
    return entries, out


def apply_waivers(violations: list[Violation], exceptions: list[ExceptionEntry],
                  reg: Register, ran: set[str]) -> list[Violation]:
    '''Waivers match both ways, per (check, file), however many violations the
    file holds: a waived pair drops out; a waiver whose file no longer violates
    its check fails; a waived file above its ceiling fails (R3.3 rule 4).
    An unwaivable violation always stands. A waiver is never called stale on
    a file its check could not evaluate, or for a check that did not run.'''
    by_pair: dict[tuple[str, str], list[Violation]] = {}
    blocked: set[tuple[str, str]] = set()
    out: list[Violation] = []
    for v in violations:
        if v.waivable:
            by_pair.setdefault((v.check, v.file), []).append(v)
        else:
            out.append(v)
            blocked.add((v.check, v.file))
    sections = {c.id: ', '.join(c.sections) for c in reg.checks}
    waived: set[tuple[str, str]] = set()
    for exc in exceptions:
        if exc.check is None or exc.check not in ran:
            continue
        for path in exc.artifacts:
            hits = by_pair.get((exc.check, path))
            if not hits and (exc.check, path) in blocked:
                continue
            if not hits:
                out.append(Violation(
                    path, 'stale-waiver', sections[exc.check],
                    f'exception {exc.id} ({exc.reason}) waives {exc.check} here, but the file '
                    'no longer violates it: remove the entry, or this file from it'))
                continue
            waived.add((exc.check, path))
            worst = max((v.value for v in hits if v.value is not None), default=None)
            if exc.ceiling is not None and worst is not None and worst > exc.ceiling:
                out.append(Violation(path, 'ceiling', sections[exc.check],
                                     f"{worst} exceeds exception {exc.id}'s ceiling of {exc.ceiling}"))
    for pair, found in by_pair.items():
        if pair not in waived:
            out.extend(found)
    return out


def run(root: Path) -> list[str]:
    '''Every violation in the repo at root, rendered and sorted.'''
    raw = load_register(root)
    guide_path, text = load_guide(root, raw)
    files = kept_files(root)
    sections, out = guide_sections(text, guide_path)
    anchors = [s.id for s in sections if s.id]
    reg, problems = parse_register(raw)
    exceptions, exception_problems = parse_exceptions(raw, reg, anchors, files, root)
    out += problems + exception_problems
    out += section_violations(reg, anchors)
    out += implementation_violations(reg)
    kinds = kind_files(reg, files)
    ran = {c.id for c in reg.checks if _runnable(c) and all(k in kinds for k in c.kinds)}
    out += apply_waivers(run_checks(root, reg, kinds), exceptions, reg, ran)
    return sorted(v.render() for v in out)


def main(root: Path = REPO) -> int:
    try:
        lines = run(root)
    except SetupError as exc:
        print(exc, file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    return 1 if lines else 0


if __name__ == '__main__':
    sys.exit(main())
