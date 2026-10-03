'''Execute explicitly marked, self-contained JAX CPU examples without a preamble.'''
import argparse
import math
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from fences import iter_code_blocks


@dataclass(frozen=True)
class Example:
    path: Path
    line: int
    identifier: str
    code: str


def collect_examples(paths: list[Path]) -> tuple[list[Example], list[str]]:
    examples: list[Example] = []
    errors: list[str] = []
    identifiers: set[str] = set()
    visited: set[Path] = set()
    for scope in paths:
        if not scope.exists():
            errors.append(f'{scope}: missing scope')
            continue
        if scope.is_dir():
            files = sorted(scope.rglob('*.md'))
        elif scope.suffix == '.md':
            files = [scope]
        else:
            errors.append(f'{scope}: expected a Markdown file or directory')
            continue
        selected = 0
        for path in files:
            blocks = iter_code_blocks(path.read_text())
            for block in blocks:
                parts = block.info.split()
                marker = parts[0] if parts else ''
                location = f'{path}:{block.line}'
                if marker in {'norun', 'noparse'}:
                    if len(parts) < 2:
                        errors.append(f'{location}: exemption needs a reason')
                    continue
                if marker != 'cpu-example' or len(parts) != 2:
                    errors.append(f'{location}: needs an explicit execution marker and id/reason')
                    continue
                selected += 1
                if path.resolve() in visited:
                    continue
                identifier = parts[1]
                if identifier in identifiers:
                    errors.append(f'{location}: duplicate example id {identifier}')
                    continue
                identifiers.add(identifier)
                examples.append(Example(path.resolve(), block.line, identifier, block.code))
            visited.add(path.resolve())
        if selected == 0:
            errors.append(f'{scope}: zero CPU examples')
    return examples, errors


def run_example(example: Example, timeout: float) -> tuple[bool, str]:
    location = f'{example.path}:{example.line} [{example.identifier}]'
    env = os.environ.copy()
    env['JAX_PLATFORMS'] = 'cpu'
    with tempfile.TemporaryDirectory(prefix='jax-example-') as directory:
        script = Path(directory) / 'example.py'
        script.write_text(example.code)
        try:
            result = subprocess.run(
                [sys.executable, str(script)], cwd=directory, env=env,
                text=True, capture_output=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired as error:
            output = error.stdout or b''
            stderr = error.stderr or b''
            if isinstance(output, bytes):
                output = output.decode(errors='replace')
            if isinstance(stderr, bytes):
                stderr = stderr.decode(errors='replace')
            return False, f'{location}: timed out after {timeout}s\n{output}{stderr}'
    if result.returncode != 0:
        return False, f'{location}: exit {result.returncode}\n{result.stdout}{result.stderr}'
    return True, f'{location}: PASS'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--timeout', type=float, default=300)
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error('--timeout must be finite and positive')
    examples, errors = collect_examples(args.paths)
    if errors:
        for error in errors:
            print(error)
        print(f'Selected {len(examples)} CPU examples; executed 0 (scope errors).')
        return 1
    passed = 0
    for example in examples:
        success, detail = run_example(example, args.timeout)
        print(detail)
        passed += success
    print(f'Selected/executed {len(examples)} CPU examples; passed {passed}.')
    return int(passed != len(examples))


if __name__ == '__main__':
    raise SystemExit(main())
