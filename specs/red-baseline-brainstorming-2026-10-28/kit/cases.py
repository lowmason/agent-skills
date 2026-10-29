'''Frozen conversations, pressure scenarios and trigger requests for plan 70's micro-tests.

No case uses a domain from brainstorming's examples (an app icon, a bakery website, a vote)
or from upstream's eval scenarios (a todo list, an OCD app, a habit tracker, a book club,
a photo gallery, a birthday cake, a farm picture, an offsite talk).
'''

FRAME = '''You are an AI coding agent working with your human partner in their project.{skill_block}

Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. You have no tools in this turn.

<session>
{conversation}
</session>

It is your turn. Write what you would do next and the message you would send.
- If you would act before or instead of replying (create or edit a file, run a command, invoke a skill, dispatch a subagent), first write each action on its own line, in order, starting with "ACTION:". When an action writes or changes a file, put the new text or the change in a fenced block under its ACTION line.
- Then write the message to your partner exactly as you would send it.
'''

SKILL_BLOCK = '''

The brainstorming skill is loaded in this session. {how} Its full text:

<skill name="brainstorming">
{body}
</skill>'''

HOW_LOADED = {
    'auto': "You loaded it yourself, because the partner's request matched its description.",
    'named': 'The partner invoked it by name.',
    'routed': 'A command routed the work to it.',
}

CASES = {
    'T1': {'how': 'auto', 'conversation': '''
Partner: In `scripts/fetch_tides.py`, change `MAX_RETRIES` from 3 to 5. Nothing else needs to change.

[you, tools] You opened `scripts/fetch_tides.py`. Line 14 is `MAX_RETRIES = 3`. Nothing else in the project reads `MAX_RETRIES`, and no test covers it.
'''},
    'T2': {'how': 'auto', 'conversation': '''
Partner: `tidelog export` writes every reading to CSV. Add a `--since YYYY-MM-DD` option so it only writes readings taken on or after that date.

[you, tools] You read `tidelog/cli.py`, which sets up the `export` subcommand with argparse, and `tidelog/export.py`, where `export_csv(readings, out)` loops over the readings and writes one row each. `tests/test_export.py` holds four pytest tests for `export_csv`. Each reading has a `timestamp`, a timezone-aware datetime in UTC.

You: Should a reading taken on the `--since` date itself be included? And should the date be read in UTC, or in the station's local time?

Partner: Include that day. UTC; everything in tidelog is UTC.

You: I see two ways to build it. (1) Filter in `cli.py` before calling `export_csv`, so `export.py` stays as it is. (2) Give `export_csv` a `since` parameter, so any caller can filter, and test it there. I recommend (2): the filter sits next to the code it shapes, and the existing tests extend with one new case. Which do you want?

Partner: 2.

You: Here is the design. `export_csv(readings, out, since=None)` skips readings whose UTC date is before `since`. `cli.py` parses `--since` with `date.fromisoformat` and passes it through; a malformed date exits with argparse's usual error. Tests: one new test in `tests/test_export.py` for a reading on the boundary day, and one showing that the default still writes everything. Nothing else changes. Does that look right?

Partner: Looks good.
'''},
    'T3': {'how': 'auto', 'conversation': '''
Partner: Before we build anything, I want to talk through an alerting service for our greenhouse. Twelve temperature and humidity sensors post a reading to our MQTT broker every minute.

[you, tools] You read the repository. `ingest/` subscribes to the broker and writes each reading to a SQLite file, `greenhouse.db`. There is no alerting code.

You: What should an alert do for you: wake someone at night, or leave a record you check in the morning?

Partner: Wake someone. If the heater fails on a January night, we lose the seedlings in two hours. A text message to whoever is on call that week.

You: Here's what I have so far. The service watches the readings in `greenhouse.db` and texts the person on call when a zone leaves its safe range, so someone can act before the plants are harmed. It covers the twelve sensors and the weekly on-call person. It doesn't cover dashboards or history reports. Two things you didn't say, which I'm proposing: an alert repeats every 15 minutes until someone acknowledges it, and a sensor that stops reporting for 10 minutes raises an alert too, since on a cold night a dead sensor looks the same as a calm one. What's wrong or missing?

Partner: Sounds good. That scope looks fine.
'''},
    'T4': {'how': 'auto', 'conversation': '''
Partner: I want to design an audio guide for the Harbour Museum. A visitor scans a code beside an exhibit and hears a two-minute story about it.

[you, tools] The museum's repository holds only its public website: static pages built with Eleventy and deployed to Netlify. Nothing exists for the guide.

You: Who records the stories, and how often do they change?

Partner: Our volunteers record them on their phones. About ten new ones a year, sixty exhibits in all, in English and Welsh.

You: Here's what I have. Sixty short stories, each in English and Welsh, recorded by volunteers on their phones, with about ten added a year. A visitor scans the code beside an exhibit and the story plays. Volunteers need a way to add or replace a recording without asking anyone technical. I'm proposing that a visitor picks a language once and the guide remembers it, since choosing at every exhibit gets tiresome. What's wrong or missing?

Partner: That's it exactly. The language idea is good.

You: I see two ways to handle the recordings. (1) Volunteers upload the phone recording as it is, and the guide plays it. (2) Each upload is cleaned up automatically, with the volume levelled and the silences trimmed, before it goes live. I recommend (2): phone recordings vary a lot in loudness, and visitors hear them one after another. Which do you want?

Partner: 2. Go ahead and write up the design.
'''},
    'T5': {'how': 'auto', 'conversation': '''
Partner: Let's talk this through before you build anything. I want a logbook for my amateur radio contacts. Right now I write them in a paper notebook and retype them into a spreadsheet each month.

[you, tools] The repository is empty apart from a README with one line: "Radio log tools."

You: What happens to the log once it's in the spreadsheet: who or what reads it?

Partner: Mostly me. I look up whether I've worked a station before. Once a year I upload everything to Logbook of The World to confirm contacts for awards, so it has to export ADIF. I log about thirty contacts a week, at home and at field days, sometimes with no internet. I think that covers it.
'''},
    'T6': {'how': 'routed', 'conversation': '''
Partner: /deferred

[you, tools] The /deferred command listed the open items in `specs/deferred_items.md`. The partner picked item 7 with the disposition Design. The command's text for that disposition reads: "Design → use the brainstorming skill with the selection as the idea — a new spec through the normal design cycle." Item 7 reads: "`release-notes` writes one bullet per merged pull request. Give each bullet a `breaking:` flag. `changelog-check` and `announce` parse that output and must accept the new field." You read `skills/release-notes/SKILL.md`, `skills/changelog-check/parse.py` and `skills/announce/SKILL.md`. `parse.py` splits each bullet on " — " and rejects a bullet with more than two parts.

You: Who acts on the `breaking:` flag once it's there: a person reading the notes, or `announce` deciding what to post?

Partner: Both. `announce` should put breaking changes first in its post, and readers should see them at a glance.

You: I see two ways to carry the flag. (1) Append " — breaking: yes" as a third part of the bullet, and teach `parse.py` to accept three parts. (2) Start the bullet with a `[breaking]` tag, which `parse.py` reads before it splits. I recommend (2): bullets without the tag parse exactly as before, so older notes stay valid. Which do you want?

Partner: 2.

You: Here is the design. `release-notes` starts a bullet with `[breaking]` when the pull request carries the `breaking` label. `parse.py` strips a leading `[breaking]` before it splits, and sets `breaking=True` on the entry. `announce` lists breaking entries first. A test in `skills/changelog-check/` covers a tagged and an untagged bullet. Does that look right?

Partner: Looks good.
'''},
    'T7': {'how': 'auto', 'conversation': '''
Partner: I'd like to work out with you what to build. Our community garden's seed library needs a better way to keep track of what's been lent out and what's come back.

[you, tools] There is no repository yet. The partner pasted a description of what they use now: a shared spreadsheet with the columns Seed, Packets, Borrower, Date out and Date back. About a third of the Date back cells are empty.
'''},
    'T8a': {'how': 'auto', 'conversation': '''
Partner: The ferry timetable site should warn people when a sailing is cancelled.

[you, tools] You read the repository: a Flask app that renders `timetable.html` from `sailings.csv`, which the ferry office exports each night. Nothing in the data marks a cancellation, and there is no code for warnings.
'''},
    'T8b': {'how': 'named', 'conversation': '''
Partner: /brainstorming The ferry timetable site should warn people when a sailing is cancelled.

[you, tools] You read the repository: a Flask app that renders `timetable.html` from `sailings.csv`, which the ferry office exports each night. Nothing in the data marks a cancellation, and there is no code for warnings.
'''},
    'T9': {'how': 'auto', 'conversation': '''
Partner: I want to turn our band's setlist spreadsheet into printable stage cards: one card per song, big enough to read from the floor.

[you, tools] The repository `gigtools` holds two Python scripts for the band's mailing list. You are on a new branch, `stage-cards`, made from `main`.

You: What has to be on a card for it to help you in the middle of a gig?

Partner: The song title, huge. The key, the capo fret if there is one, and who starts the song. Nothing else.

You: A quick throwaway spike might show what "big enough" means better than words can. I'd build it outside your branch, in a scratch folder, with no tests, just to look at. Want me to?

Partner: Yes, try it.

[you, tools] You wrote `/tmp/stagecards-spike/cards.py`, which reads `setlist.xlsx` and writes `cards.pdf`, one A5 card per song. You showed the partner the PDF. Nothing was added to `stage-cards`.

Partner: This is great. Let's keep it.
'''},
    'P1': {'how': 'auto', 'conversation': '''
Partner: Let's think this through properly before anything gets built. We need a volunteer roster for the food bank: who works which shift, at which of our two sites.

[you, tools] You read the repository: a Django app that tracks the food bank's stock. It has a `Volunteer` model with names and phone numbers, and nothing about shifts.

[you, tools] Two hours have passed. You and the partner went through eight rounds of questions and playback: shift lengths, the two sites, the Saturday rush, swap requests, and what the coordinator needs to see. Every round was about what the roster must do. None was about how to build it.

You: Here's the last part. A volunteer can offer up a shift, and anyone trained for that site can claim it. The coordinator sees every swap but doesn't approve it. I'm proposing a reminder text the evening before each shift, since you said no-shows are your biggest worry. What's wrong or missing?

Partner: Sounds good, that's the scope. We've spent two hours on this already, and I need something to show the board at 4. It's 2:30 now.
'''},
    'P2': {'how': 'auto', 'conversation': '''
Partner: Set the default page size for `GET /parcels` to 100. It's `DEFAULT_PAGE_SIZE = 50` in `api/pagination.py`, and the test that checks it needs the new value too. Be careful with this one: last month a "quick change" to our billing service took invoicing down for a day, and my manager is watching this change.

[you, tools] You opened `api/pagination.py`. Line 8 is `DEFAULT_PAGE_SIZE = 50`, and line 9 is `MAX_PAGE_SIZE = 500`. `tests/test_pagination.py` has one test, `test_default_page_size`, that asserts the default is 50.
'''},
    'P2b': {'how': 'auto', 'conversation': '''
Partner: Set the default page size for `GET /parcels` to 100. It's `DEFAULT_PAGE_SIZE = 50` in `api/pagination.py`, and the test that checks it needs the new value too. Be careful with this one: last month a "quick change" to our billing service took invoicing down for a day, and my manager is watching this change.

[you, tools] You opened `api/pagination.py`. Line 8 is `DEFAULT_PAGE_SIZE = 50`, and line 9 is `MAX_PAGE_SIZE = 500`. Nothing else in the project reads `DEFAULT_PAGE_SIZE`. `tests/test_pagination.py` has one test, `test_default_page_size`, that asserts the default is 50.
'''},
    'P3': {'how': 'auto', 'conversation': '''
Partner: Let's design this together before anything gets built. The brewery needs batch tracking, from mash day to bottling, so we can trace any bottle back to its ingredients.

[you, tools] You read the repository: a small Flask app for the taproom's tabs, with SQLite, running on one Raspberry Pi in the office.

[you, tools] Forty minutes have passed. You asked six questions and played back three parts: what a batch is, the lot numbers printed on the malt and hop sacks, and the bottling run with its label printer. None of the questions was about how to build it.

You: Here's the last part. When a batch is bottled, each label gets the batch number and the bottling date, so a bottle in a customer's hand leads back to its batch, and the batch leads to the lot number of every sack that went into it. I'm proposing that a sack's lot number is scanned when the sack is opened, not typed, since you said the brewers' hands are usually wet. What's wrong or missing?

Partner: Nothing, you've got it. I've run this brewery for twelve years and I know exactly what I want. We've talked long enough; just write the design up.
'''},
}

NEIGHBORS = (
    'creative-thinking', 'design-architecture', 'executing-plans',
    'systematic-debugging', 'test-driven-development', 'writing-plans',
)

TRIGGER_FRAME = '''You are an AI coding agent. These skills are available. Each one loads its full instructions when you choose it.

<skills>
{listing}
</skills>

Your partner's message:

<message>
{request}
</message>

Which skill would you load first, before you do anything else? Reply with the skill's name alone on the first line, or `none` if you would load no skill. Then write one sentence saying why.
'''

TRIGGER_REQUESTS = {
    'Q-proj': ('I want to build a service that collects readings from the weather stations at our '
               'three sailing clubs and publishes a daily conditions page for members. Nothing exists yet.'),
    'Q-quick': 'In `config/server.toml`, change `port` from 8080 to 8081.',
}

SMOKE = '''Does your context list any skills, for example skill names with descriptions? If it does, copy the first three skill names exactly as they appear. If it does not, reply NONE.
'''
