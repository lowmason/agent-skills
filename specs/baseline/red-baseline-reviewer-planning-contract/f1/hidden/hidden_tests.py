'''Plan 73 F1 hidden acceptance tests. No agent in an F1 run sees this file.'''
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(os.environ['F1_REPO'])


def run(*files: Path, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(REPO / 'tally.py'), *map(str, files)],
                          capture_output=True, text=True, cwd=cwd)


def test_refund_in_parentheses_counts_negative(tmp_path):
    f = tmp_path / 'a.csv'
    f.write_text('date,description,amount\n2026-03-02,Hotel,80.00\n2026-03-09,Hotel refund,(80.00)\n'
                 '2026-03-10,Lunch,12.25\n')
    result = run(f, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ['2026-03 12.25']


def test_export_with_byte_order_mark_is_read(tmp_path):
    f = tmp_path / 'bom.csv'
    f.write_bytes('﻿date,description,amount\n2026-04-01,Taxi,15.00\n'.encode())
    result = run(f, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ['2026-04 15.00']


def test_missing_file_is_a_clean_error(tmp_path):
    good = tmp_path / 'good.csv'
    good.write_text('date,description,amount\n2026-05-01,Bus,2.00\n')
    result = run(good, tmp_path / 'card-9.csv', cwd=tmp_path)
    assert 'card-9.csv' in result.stderr
    assert 'Traceback' not in result.stderr
