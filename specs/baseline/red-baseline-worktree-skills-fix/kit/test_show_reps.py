'''Tests for show_reps.py: the grading sheet and the spend sum.

The brief (Task 1, Next-kit fixes): "A grading sheet names the rep id and the case, never the arm.
Before grading a treatment arm, diff one of its sheets against a control sheet of the same case: only
the rep's answer may differ." The spend stops ($3 for the control arms, $10 for the kit) read the sum
that `cost` prints. The rep JSONs here are synthetic, and their answers hold neither arm word.
'''
import json
from pathlib import Path

import pytest

import build_prompts
import show_reps

ANSWER = ('SAY: I make the worktree with git.\nRUN: git worktree add .worktrees/x -b x\n'
          'TOOL: EnterWorktree path=/work/atlas/.worktrees/x')


def write_rep(directory: Path, number: int, answer: str, cost: float = 0.01) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f'rep{number}.json').write_text(json.dumps({'result': answer, 'total_cost_usd': cost}))


def sheet(capsys, case: str, directory: Path) -> str:
    capsys.readouterr()
    show_reps.sheet(case, directory, [])
    return capsys.readouterr().out


@pytest.mark.parametrize('case', sorted(build_prompts.CASES))
def test_a_sheet_names_the_rep_and_the_case_and_never_the_arm(tmp_path, capsys, case):
    write_rep(tmp_path / f'{case}-control', 1, ANSWER)
    write_rep(tmp_path / f'{case}-treatment', 1, ANSWER)
    control = sheet(capsys, case, tmp_path / f'{case}-control')
    treatment = sheet(capsys, case, tmp_path / f'{case}-treatment')
    assert control == treatment
    assert control.startswith(f'=== case {case}, rep1 ===\n')
    assert 'control' not in control.lower() and 'treatment' not in control.lower()
    assert f'PASS: {build_prompts.CASES[case]["pass"]}\n' in control
    assert f'FAIL: {build_prompts.CASES[case]["fail"]}\n' in control
    assert f'--- answer ---\n{ANSWER}\n=== end rep1 ===' in control


def test_two_sheets_of_one_case_differ_only_in_the_answer(tmp_path, capsys):
    write_rep(tmp_path / 'noremote-control', 1, ANSWER)
    write_rep(tmp_path / 'noremote-treatment', 1, 'SAY: a different answer', cost=0.5)
    control = sheet(capsys, 'noremote', tmp_path / 'noremote-control')
    treatment = sheet(capsys, 'noremote', tmp_path / 'noremote-treatment')
    assert control != treatment
    before_c, _, rest_c = control.partition('--- answer ---\n')
    before_t, _, rest_t = treatment.partition('--- answer ---\n')
    assert before_c == before_t
    assert rest_c.partition('=== end rep1 ===')[2] == rest_t.partition('=== end rep1 ===')[2]


def test_cost_sums_every_json_below_the_folder_the_probe_and_void_reps_included(tmp_path, capsys):
    write_rep(tmp_path / 'runs' / 'noremote-control', 1, 'a', cost=0.25)
    write_rep(tmp_path / 'runs' / 'noremote-control', 2, 'b', cost=0.125)
    write_rep(tmp_path / 'runs' / 'archive-relay-control', 1, 'c', cost=0.0625)
    (tmp_path / 'probe').mkdir()
    (tmp_path / 'probe' / 'probe.json').write_text(json.dumps({'result': 'd', 'total_cost_usd': 0.5}))
    (tmp_path / 'runs' / 'noremote-control' / 'rep3.json').write_text(json.dumps({'result': 'no cost field'}))
    capsys.readouterr()
    show_reps.cost(tmp_path)
    lines = capsys.readouterr().out.splitlines()
    assert 'runs/noremote-control: $0.375' in lines
    assert 'runs/archive-relay-control: $0.062' in lines or 'runs/archive-relay-control: $0.063' in lines
    assert 'probe: $0.500' in lines
    assert lines[-1] == 'total $0.938'
