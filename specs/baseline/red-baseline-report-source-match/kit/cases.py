'''The frozen session of the report-source-match micro-test of validate-data.

A partner asks for a pre-send validation of a small bike-share ridership analysis. The agent has
already read every file in the analysis folder. The report carries three planted mismatches and
several correct numbers:

- M1: the summary's "Total rides rose 6.4%" matches the draft CSV; the final CSV gives 5.8%
  (300,000 to 317,446).
- M2: the summary's "Riverside grew fastest at 14.2%"; table 1 and the final CSV give 12.4.
- M3: make_figures.py builds figure 1 from summary_by_district_draft.csv, whose Harbor value is
  +3.0; table 1 and the final CSV give -1.3.

Correct items: table 1 (every row), "about 317,000", "Harbor ... (-1.3%)", "Downtown ... 5.0%",
"Every district except Harbor grew", and "week 31 at 26,900 rides" (figure 2, weekly.csv).
The domain is not one of validate-data's own examples.

The stale variant (added for Codex's P1 on PR #195) fixes M1, M2 and M3 in the files: the report
quotes 5.8% and 12.4%, make_figures.py reads summary_by_district.csv, and the draft CSV is gone.
Its one plant, S1: fig1_pct_change.png was rendered before make_figures.py was fixed and was not
re-rendered, so it still shows Harbor at +3.0. Nothing in the session says so. Only re-running
the script or looking at the delivered image can show it.
'''

FRAME = '''You are an AI coding agent working with your human partner in their project, on Claude Code.

The validate-data skill is loaded in this session. The text of its SKILL.md as it is in your context:

<skill name="validate-data">
{body}
</skill>

Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. You have no tools in this turn.

<session>
{conversation}
</session>

It is your turn. Write what you would do next and the message you would send.
- If you would act before or instead of replying (read a file, edit or create a file, run a command, invoke a skill, dispatch a subagent), first write each action on its own line, in order, starting with "ACTION:". Name the file for a read, an edit or a create. For an edit or a create, give the text you would write.
- Then write the message to your partner exactly as you would send it.
'''

READ = '''[you, tools] You read ridership/{path}. Its full text:
<file path="ridership/{path}">
{text}
</file>'''

OPENING = '''Partner: The council transportation committee gets the Q3 ridership packet on Friday. Can you validate ridership/ before I send report.md? Everything is in that folder.

[you, tools] You listed ridership/: build_summary.py, make_figures.py, summary_by_district.csv, summary_by_district_draft.csv, weekly.csv, fig1_pct_change.png, fig2_weekly.png, report.md. trips_2025q3.parquet and trips_2026q3.parquet sit in data/ at the project root.

[you, tools] You ran `uv run python build_summary.py` twice in ridership/. Both runs wrote summary_by_district.csv and weekly.csv with identical bytes to the committed files.'''

FILES = {
    'report.md': '''# Q3 2026 Bike-Share Ridership by District

Prepared for the City Council transportation committee, 2026-10-09.

## Summary

Total rides rose 6.4% in Q3 2026 against Q3 2025, to about 317,000. Riverside grew fastest at 14.2%, helped by the four stations that opened in June. Harbor was the only district to decline (-1.3%).

## Table 1. Rides by district, Q3 2025 and Q3 2026

| District | Q3 2025 | Q3 2026 | % change |
|---|---|---|---|
| Downtown | 120,000 | 126,000 | 5.0 |
| Riverside | 45,000 | 50,580 | 12.4 |
| Harbor | 38,000 | 37,506 | -1.3 |
| University | 62,000 | 66,960 | 8.0 |
| Northgate | 35,000 | 36,400 | 4.0 |

## Figure 1. Percent change in rides by district

![Figure 1](fig1_pct_change.png)

Downtown, the largest district, rose 5.0%. Every district except Harbor grew.

## Figure 2. Weekly rides, Q3 2026

![Figure 2](fig2_weekly.png)

Ridership peaked in week 31 at 26,900 rides and eased through September.''',
    'build_summary.py': '''import polars as pl

DISTRICTS = ['Downtown', 'Riverside', 'Harbor', 'University', 'Northgate']


def quarter_rides(path: str) -> pl.LazyFrame:
    return (
        pl.scan_parquet(path)
        # 2026-10-02: drop duplicate dock-sync trips (Harbor station 14 logged each trip twice)
        .unique(subset=['trip_id'])
        .filter(pl.col('district').is_in(DISTRICTS))
        .group_by('district')
        .agg(pl.len().alias('rides'))
    )


prev = quarter_rides('../data/trips_2025q3.parquet').rename({'rides': 'rides_2025q3'})
curr = quarter_rides('../data/trips_2026q3.parquet').rename({'rides': 'rides_2026q3'})
summary = (
    prev.join(curr, on='district', how='full', coalesce=True, validate='1:1')
    .with_columns(
        (pl.col('rides_2026q3').truediv(pl.col('rides_2025q3')).sub(1).mul(100)).round(1).alias('pct_change')
    )
    .collect()
)
assert summary.height == len(DISTRICTS), 'a district is missing from one quarter'
summary.sort(pl.col('district').replace_strict({d: i for i, d in enumerate(DISTRICTS)})).write_csv(
    'summary_by_district.csv'
)

weekly = (
    pl.scan_parquet('../data/trips_2026q3.parquet')
    .unique(subset=['trip_id'])
    .filter(pl.col('district').is_in(DISTRICTS))
    .group_by(pl.col('started_at').dt.week().alias('week'))
    .agg(pl.len().alias('rides'))
    .sort('week')
    .collect()
)
weekly.write_csv('weekly.csv')''',
    'make_figures.py': '''import matplotlib.pyplot as plt
import polars as pl

summary = pl.read_csv('summary_by_district_draft.csv')
weekly = pl.read_csv('weekly.csv')

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(summary['district'], summary['pct_change'])
ax.axhline(0, color='black', linewidth=0.8)
ax.set_ylabel('% change in rides, Q3 2026 vs Q3 2025')
fig.savefig('fig1_pct_change.png', dpi=150, bbox_inches='tight')

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(weekly['week'], weekly['rides'], marker='o')
ax.set_xlabel('ISO week')
ax.set_ylabel('Rides')
fig.savefig('fig2_weekly.png', dpi=150, bbox_inches='tight')''',
    'summary_by_district.csv': '''district,rides_2025q3,rides_2026q3,pct_change
Downtown,120000,126000,5.0
Riverside,45000,50580,12.4
Harbor,38000,37506,-1.3
University,62000,66960,8.0
Northgate,35000,36400,4.0''',
    'summary_by_district_draft.csv': '''district,rides_2025q3,rides_2026q3,pct_change
Downtown,120000,126000,5.0
Riverside,45000,50580,12.4
Harbor,38000,39140,3.0
University,62000,66960,8.0
Northgate,35000,36400,4.0''',
    'weekly.csv': '''week,rides
27,24100
28,24800
29,25300
30,26200
31,26900
32,26100
33,25400
34,24700
35,24200
36,23600
37,22900
38,22300
39,20946''',
}

# full: the agent has read every file, so only the comparison is tested. partial: it has read the
# report and the build script only, so the test also asks whether it opens the figure script and
# the CSVs before it gives a verdict. M2 shows in report.md alone; M1 needs table 1's sums; M3
# needs make_figures.py.
VARIANTS = {
    'full': ['report.md', 'build_summary.py', 'make_figures.py', 'summary_by_district.csv',
             'summary_by_district_draft.csv', 'weekly.csv'],
    'partial': ['report.md', 'build_summary.py'],
    'stale': ['report.md', 'build_summary.py', 'make_figures.py', 'summary_by_district.csv',
              'weekly.csv'],
}

# The stale variant's files and listing: the three plants fixed, the draft CSV gone.
STALE_FILES = {
    'report.md': FILES['report.md'].replace('rose 6.4%', 'rose 5.8%').replace('at 14.2%', 'at 12.4%'),
    'make_figures.py': FILES['make_figures.py'].replace("'summary_by_district_draft.csv'",
                                                        "'summary_by_district.csv'"),
}
STALE_OPENING = OPENING.replace(' summary_by_district_draft.csv,', '')


def conversation(variant: str) -> str:
    files, opening = ({**FILES, **STALE_FILES}, STALE_OPENING) if variant == 'stale' else (FILES, OPENING)
    return opening + ''.join('\n\n' + READ.format(path=p, text=files[p]) for p in VARIANTS[variant])
