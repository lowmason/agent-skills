'''The nine prompts of plan 111's trigger test (Task 3 Step 2), the groups that its PASS rule uses, and the probe.

Usage: uv run python trigger_prompts.py <id>   (prints one prompt; run_trigger_reps.sh calls it)

P1 to P5 should load classification-codes. P1 and P2 ask about Census industry (IND) codes, which only the
`new` description names. P3 to P5 ask about NAICS, SOC and Census occupation (OCC) codes. N1 to N4 are near
misses: N1 is a geographic-codes task, N2 and N3 are bls-data-context tasks, and N4 is a Polars task.
The id `probe` prints isolation_probe.txt as it is, so the isolation probe runs as a trigger rep does. It is
not in PROMPTS, so triggers.py tally refuses a `probe` folder in a runs root.
'''
import sys
from pathlib import Path

PROMPTS = {
    'P1': ('Our CPS extract has an IND column with values like 7860 and 0770. What industries are those, and which '
           'NAICS codes do they cover?'),
    'P2': ('I need to join ACS PUMS records coded with 2017 Census industry codes to QCEW data keyed by NAICS. How do I '
           'map one to the other?'),
    'P3': 'What is the 2022 NAICS title for 541511, and did that code change from 2017?',
    'P4': 'Map these SOC 2010 codes to SOC 2018: 15-1132 and 15-1133.',
    'P5': 'Our ACS file has OCCP 1021. Which occupation is that?',
    'N1': 'Which counties are in the Austin-Round Rock CBSA?',
    'N2': 'How does the CES birth-death model feed into the monthly payroll estimate?',
    'N3': 'How do I compute an unemployment rate from CPS microdata with the PWSSWGT weight?',
    'N4': 'Write a Polars function that drops duplicate rows keyed on series_id and ref_date.',
}
SHOULD_LOAD = ('P1', 'P2', 'P3', 'P4', 'P5')
IND = ('P1', 'P2')
NEAR_MISS = ('N1', 'N2', 'N3', 'N4')
PROBE = 'probe'
PROBE_FILE = Path(__file__).resolve().parent / 'isolation_probe.txt'


def main() -> None:
    if len(sys.argv) != 2 or (sys.argv[1] not in PROMPTS and sys.argv[1] != PROBE):
        raise SystemExit(f'usage: trigger_prompts.py <{"|".join(PROMPTS)}|{PROBE}>')
    if sys.argv[1] == PROBE:
        sys.stdout.write(PROBE_FILE.read_text())
        return
    print(PROMPTS[sys.argv[1]])


if __name__ == '__main__':
    main()
