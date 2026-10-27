"""Tests for the visual companion's server.cjs — run from this directory.

cd skills/brainstorming/scripts && uv run --with pytest python -m pytest -q

server.cjs is Node, so the test drives node as a subprocess. wrapInFrame is
not exported, so a small harness compiles the module with one export line
appended. The require.main guard keeps the server from starting, and loading
the module reads its two template files but writes nothing. Skips when node
is not on PATH.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

SERVER = Path(__file__).resolve().parent / 'server.cjs'
NODE = shutil.which('node')

# Compiles server.cjs with wrapInFrame exported and prints
# wrapInFrame(argv[2]). _compile with the real filename keeps __dirname at
# this directory, so frame-template.html and helper.js still load.
HARNESS = r"""
const Module = require('module');
const fs = require('fs');
const path = require('path');
const file = process.argv[1];
const m = new Module(file, null);
m.filename = file;
m.paths = Module._nodeModulePaths(path.dirname(file));
m._compile(fs.readFileSync(file, 'utf8') + '\nmodule.exports.wrapInFrame = wrapInFrame;\n', file);
process.stdout.write(m.exports.wrapInFrame(process.argv[2]));
"""

needs_node = pytest.mark.skipif(NODE is None, reason='node is not on PATH')


def wrap_in_frame(fragment):
    result = subprocess.run(
        [NODE, '-e', HARNESS, str(SERVER), fragment], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


@needs_node
def test_wrap_in_frame_inserts_replacement_tokens_literally():
    """String.replace reads $' $` $& $$ in a replacement string as patterns,
    so a screen showing prices, shell or regex text came back with part of
    the frame, or the placeholder itself, spliced in. The token list follows
    upstream's regression test (obra/superpowers ddd35ab)."""
    tokens = ["$'", '$`', '$&', '$$', '$1', '$<name>']
    fragment = '<h2>Literal tokens</h2><pre>' + ' | '.join(tokens) + '</pre>'
    page = wrap_in_frame(fragment)
    assert fragment in page
    assert page.count('<div class="header">') == 1
    assert '<!-- CONTENT -->' not in page
