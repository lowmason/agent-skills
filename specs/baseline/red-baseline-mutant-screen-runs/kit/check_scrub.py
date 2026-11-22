'''Check the identity scrub at no cost, on synthetic text built in memory.

Usage, from the repository root:
  uv run python <kit>/check_scrub.py
It builds three texts from the forms that kit_identity.py reads (each address, each local part,
each full name, each name part and $USER):
- replace: each form in three cases (as read, lower, upper) between ordinary words and marks. The
  scrub must give each its token, with the text around it unchanged, and leave no form.
- keep: each form that holds no other form, with a letter before it and with a digit after it.
  There it is part of a longer word, and the scrub must change nothing.
- ordinary: a few lines of code and report text with no form. The scrub must change nothing.
It prints only counts and PASS or FAIL, never a value, and writes no file.
'''
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_identity  # noqa: E402

ORDINARY = ('def reorder_needed(level: int, threshold: int) -> bool:\n'
            '    return level <= threshold  # stock, slug, 3KB\n'
            'Status: DONE_WITH_CONCERNS; mutants: caught 5, survived 0, invalid 0\n')


def main() -> None:
    pairs = kit_identity.forms()
    if not pairs:
        raise SystemExit('FAIL: no identity form was read')
    values = [value for value, _ in pairs]
    atomic = [v for v in values if not any(o != v and kit_identity.pattern(o).search(v) for o in values)]
    replace, want = [], []
    for value, token in pairs:
        for form in (value, value.lower(), value.upper()):
            replace.append(f'by {form}, see ({form}) and "{form}".\n')
            want.append(f'by {token}, see ({token}) and "{token}".\n')
    keep = ''.join(f'x{value} {value}9\n' for value in atomic)
    got = kit_identity.scrub(''.join(replace), pairs)
    left = sum(1 for value in values if kit_identity.pattern(value).search(got))
    checks = {
        'every form replaced by its token, the rest unchanged': got == ''.join(want),
        'no form left': left == 0,
        'a form inside a longer word kept': kit_identity.scrub(keep, pairs) == keep,
        'ordinary text unchanged': kit_identity.scrub(ORDINARY, pairs) == ORDINARY,
    }
    kinds = ', '.join(sorted({token for _, token in pairs}))
    print(f'forms: {len(pairs)} ({kinds}); replace lines: {len(replace)}; keep lines: {len(atomic)}')
    for name, ok in checks.items():
        print(f'{name}: {ok}')
    print('PASS' if all(checks.values()) else 'FAIL')
    sys.exit(0 if all(checks.values()) else 1)


if __name__ == '__main__':
    main()
