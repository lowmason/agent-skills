# Scraper test scaffolds (httpx / BeautifulSoup / lxml)

Copy-paste starting points for testing BLS-style scrapers. The organizing idea: the **parser
is a pure function of an HTML string**, so it can be tested with recorded fixtures and never
touches the network. Only one marked test and a marked canary ever fetch.

## 0. Architecture prerequisite — split fetch from parse

If `scrape_schedule()` both fetches and parses, you cannot test the parse hermetically. Refactor
so a pure parser takes bytes/text:

```python
# bls_stats/release_dates/scraper.py
def fetch_schedule_html(client: httpx.Client, url: str) -> str:
    return client.get(url).raise_for_status().text

def parse_schedule(html: str, program: str) -> pl.DataFrame:
    """Pure: HTML string -> rows. No I/O. This is what the unit tests target."""
    soup = BeautifulSoup(html, "lxml")
    ...

def scrape_schedule(client, url, program):       # thin orchestrator, covered by the canary
    return parse_schedule(fetch_schedule_html(client, url), program)
```

## 1. Recorded HTML fixtures

Download a real page once and commit it. Never re-fetch inside a test.

```
tests/
  fixtures/
    ces/empsit_schedule.html        # real saved page
    jolts/jolts_schedule.html
    qcew/qcew_schedule.html
conftest.py
test_scraper.py
```

```python
# conftest.py
from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"

@pytest.fixture
def html():
    """Load a recorded page: html("ces", "empsit_schedule")."""
    def _load(source: str, name: str) -> str:
        return (FIXTURES / source / f"{name}.html").read_text(encoding="utf-8")
    return _load
```

Refresh fixtures deliberately (when the canary fires), with a one-liner kept out of the test path:

```python
# scripts/refresh_fixtures.py  — run by hand, not in CI
import httpx, pathlib
PAGES = {"ces/empsit_schedule": "https://www.bls.gov/schedule/news_release/empsit.htm"}
for stem, url in PAGES.items():
    p = pathlib.Path("tests/fixtures") / f"{stem}.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(httpx.get(url, timeout=30).raise_for_status().text, encoding="utf-8")
```

## 2. Parse edge cases — parametrized, tiny, inline

The highest-value scraper tests target the small pure helpers with inline snippets. Cover the
period-name variants BLS pages actually contain.

```python
import pytest
from datetime import date
from bls_stats.release_dates.scraper import _parse_ref_date, _last_business_day

@pytest.mark.parametrize("program, title, expected", [
    # month names, monthly programs
    ("ces",  "THE EMPLOYMENT SITUATION - MARCH 2026",               date(2026, 3, 12)),
    ("sae",  "STATE EMPLOYMENT AND UNEMPLOYMENT - JANUARY 2025",     date(2025, 1, 12)),
    # JOLTS keys off last business day of the reference month
    ("jolts","JOB OPENINGS AND LABOR TURNOVER - MARCH 2025",         _last_business_day(2025, 3)),
    # quarter names, quarterly programs
    ("qcew", "QUARTERLY CENSUS - First Quarter 2025",                date(2025, 3, 12)),
    ("bed",  "BUSINESS EMPLOYMENT DYNAMICS - Fourth Quarter 2024",   date(2024, 12, 12)),
    # no period present -> None, not a crash
    ("ces",  "No period here",                                       None),
])
def test_parse_ref_date(program, title, expected):
    assert _parse_ref_date(program, title) == expected


@pytest.mark.parametrize("year, month, expected", [
    (2025, 1, date(2025, 1, 31)),   # ends Friday
    (2025, 5, date(2025, 5, 30)),   # ends Saturday -> rollback
    (2025, 8, date(2025, 8, 29)),   # ends Sunday   -> rollback
    (2025, 4, date(2025, 4, 30)),   # ends Wednesday
])
def test_last_business_day(year, month, expected):
    assert _last_business_day(year, month) == expected
```

Layout-variant test driven by a fixture (one program reads differently from another):

```python
def test_parse_schedule_extracts_all_rows(html):
    df = parse_schedule(html("ces", "empsit_schedule"), program="ces")
    assert df.height > 0
    assert df.columns == ["program", "title", "ref_period", "release_date", "embargo"]
    # a value the recorded page is known to contain — the parse contract, not the live site
    assert df.filter(pl.col("title").str.contains("MARCH 2026")).height == 1
```

## 3. Mock the fetch layer (when you must test the orchestrator hermetically)

Use `httpx.MockTransport` to exercise `scrape_schedule` without a network, feeding it a recorded
fixture as the response body. This is mocking the *boundary* only; the real parser still runs.

```python
import httpx

def test_scrape_schedule_orchestration(html):
    body = html("ces", "empsit_schedule")
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("empsit.htm")
        return httpx.Response(200, text=body)
    client = httpx.Client(transport=httpx.MockTransport(handler))
    df = scrape_schedule(client, "https://www.bls.gov/schedule/news_release/empsit.htm", "ces")
    assert df.height > 0
```

Also test the unhappy paths the live site will eventually produce:

```python
def test_scrape_raises_on_500():
    client = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500)))
    with pytest.raises(httpx.HTTPStatusError):
        fetch_schedule_html(client, "https://www.bls.gov/x")
```

## 4. The live canary — `@pytest.mark.network`, scheduled, NOT in PR CI

Recorded fixtures cannot detect that the site changed. The canary fetches live and asserts the
*anchors the parser depends on still exist*. When it fails, refresh the fixtures.

```python
import os
import httpx
import pytest

@pytest.mark.network
def test_ces_schedule_layout_canary():
    """Fires when BLS relayouts the CES schedule page. Run on a schedule, not per-push."""
    url = "https://www.bls.gov/schedule/news_release/empsit.htm"
    html = httpx.get(url, timeout=30).raise_for_status().text
    soup = BeautifulSoup(html, "lxml")
    # the structural anchors parse_schedule() relies on:
    table = soup.find("table", id="release-schedule")     # the id the parser selects
    assert table is not None, "CES schedule table id changed — refresh fixtures + parser"
    rows = table.find_all("tr")
    assert len(rows) > 5, "row structure changed — investigate before trusting the scraper"
    # parser still produces plausible output against the live page
    df = parse_schedule(html, program="ces")
    assert df.height > 0
```

CI runs `pytest -m "not network"`. A nightly job runs `pytest -m network` and alerts on failure.
