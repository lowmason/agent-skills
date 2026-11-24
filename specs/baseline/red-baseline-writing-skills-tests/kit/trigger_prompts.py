'''The eight prompts of plan 107's trigger test (Task 6), and the groups that its bars use.

Usage: uv run python trigger_prompts.py <id>   (prints one prompt; run_trigger_reps.sh calls it)

P1 to P3 should load writing-skills and test a skill that fails to trigger or over-triggers, or a reworded
rule (the testing triggers). P4 and P5 should load it too and cover creating and renaming a skill (the core
triggers). N1 to N3 are near misses: each is about skills or agent files, and none should load it.
No prompt names writing-skills or micro-testing.
'''
import sys

PROMPTS = {
    'P1': 'The `table-diff` skill never gets picked up, even when I ask it to compare two tables. Can you sort that out?',
    'P2': '`retry-budget` keeps loading on every HTTP question, even unrelated ones. Make it stop.',
    'P3': 'I reworded the core rule in `release-notes`. Before I ship it, check that the new wording actually changes what agents do.',
    'P4': 'Make a new skill that teaches agents how we load test fixtures.',
    'P5': 'Rename the `fixture-loader` skill to `loading-test-fixtures`.',
    'N1': 'Package the skills in this repo as a Claude Code plugin with a marketplace.json.',
    'N2': "Write an implementation plan for adding a timeout to `retry-budget`'s HTTP client.",
    'N3': 'Write a CLAUDE.md for this repo.',
}
SHOULD_LOAD = ('P1', 'P2', 'P3', 'P4', 'P5')
TESTING = ('P1', 'P2', 'P3')
CORE = ('P4', 'P5')
NEAR_MISS = ('N1', 'N2', 'N3')


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in PROMPTS:
        raise SystemExit(f'usage: trigger_prompts.py <{"|".join(PROMPTS)}>')
    print(PROMPTS[sys.argv[1]])


if __name__ == '__main__':
    main()
