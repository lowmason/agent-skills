'''Skip the kit tests that need Part A's code while Part A is reverted (plan 102).

Gate A failed, so Part A of plan 102 (`packets.listed_bullets` and the settle rules for listed items) was
reverted. The kit's audit fixture builder calls `packets.listed_bullets`, so a whole fixture build and every
audit-sheet test fail without it. These 16 tests skip while that function is absent. They run again when the
two revert commits are reverted. This file is not one of the 12 files in `$K/FREEZE.sha256`.
'''
import pytest

import common  # puts build/cc_guide on sys.path
import packets

NEEDS_PART_A = {
    'test_vr_fixtures.py': {
        'test_the_changed_audit_copy_lists_p11_and_p8',
        'test_a_fixture_build_never_writes_under_a_master',
        'test_the_audit_copies_leave_out_the_report_and_only_one_gains_listed',
        'test_listed_comes_from_the_packets_own_files_and_group_models',
        'test_the_readme_copy_gains_an_empty_covered_and_the_rest_are_copies',
        'test_the_build_writes_a_shasum_listing_and_prints_the_listed_count',
        'test_the_build_fails_when_p11_or_p8_is_not_listed',
        'test_the_build_refuses_when_fixtures_exist',
        'test_main_build_reads_the_masters_under_home',
        'test_no_fixture_output_names_an_arm',
    },
    'test_vr_grade.py': {
        'test_an_audit_sheet_lists_p11_and_p8_candidates_and_the_listed_counts',
        'test_an_audit_sheet_holds_the_counts_cost_duration_and_settle_lines',
        'test_an_audit_rep_settles_against_the_listed_copy_and_the_fixtures_docs',
        'test_a_sheet_takes_the_handback_when_the_agent_result_is_the_completion_notice',
    },
}
REASON = 'Part A (packets.listed_bullets) is reverted after gate A FAIL, plan 102; revert the two revert commits to run it'


def pytest_collection_modifyitems(config, items):
    if hasattr(packets, 'listed_bullets'):
        return
    skip = pytest.mark.skip(reason=REASON)
    for item in items:
        if (item.originalname or item.name) in NEEDS_PART_A.get(item.path.name, ()):
            item.add_marker(skip)
