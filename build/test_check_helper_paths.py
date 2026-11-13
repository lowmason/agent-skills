'''Tests for check_helper_paths.py, the commit lint that keeps every skill reference to the
six SDD and executing-plans helpers anchored at <this-skill-dir>/.'''
from check_helper_paths import check


def write_tree(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def test_both_anchor_forms_pass(tmp_path):
    write_tree(tmp_path, {
        'skills/a/SKILL.md': 'Run `<this-skill-dir>/scripts/task-brief PLAN N`.\n',
        'skills/b/references/r.md': 'Run `<this-skill-dir>/../a/scripts/review-package P B H`.\n',
    })
    assert check(tmp_path) == ([], 2)


def test_a_bare_reference_is_named_with_its_file_and_line(tmp_path):
    write_tree(tmp_path, {'skills/a/references/r.md': "Intro.\n\nRun this skill's `scripts/sdd-workspace <plan-file>`.\n"})
    assert check(tmp_path) == (['skills/a/references/r.md:3: scripts/sdd-workspace has no <this-skill-dir>/ anchor'], 1)


def test_a_sibling_path_without_the_anchor_fails(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': 'Run `../b/scripts/task-start PLAN N`.\n'})
    assert check(tmp_path) == (['skills/a/SKILL.md:1: scripts/task-start has no <this-skill-dir>/ anchor'], 1)


def test_each_reference_on_a_line_is_checked(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': 'Use `<this-skill-dir>/scripts/task-done` after `scripts/task-start`.\n'})
    assert check(tmp_path) == (['skills/a/SKILL.md:1: scripts/task-start has no <this-skill-dir>/ anchor'], 2)


def test_other_scripts_files_and_trees_are_out_of_scope(tmp_path):
    write_tree(tmp_path, {
        'skills/a/SKILL.md': 'Run `scripts/history_entry.py`, see `scripts/task-briefing`, then `<this-skill-dir>/scripts/task-brief`.\n',
        'skills/a/scripts/test_x.py': "CMD = 'scripts/task-brief'\n",
        'archive/skills/c/SKILL.md': 'Run `scripts/task-brief`.\n',
    })
    assert check(tmp_path) == ([], 1)


def test_an_unanchored_mutant_run_mention_fails(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': 'Run `scripts/mutant-run PLAN N -- cmd`.\n'})
    assert check(tmp_path) == (['skills/a/SKILL.md:1: scripts/mutant-run has no <this-skill-dir>/ anchor'], 1)


def test_no_reference_at_all_means_the_pattern_is_stale(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': 'Nothing to see.\n'})
    assert check(tmp_path) == (['no helper reference under skills/; the pattern is stale'], 0)
