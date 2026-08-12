# Ripple

When an upstream team changes a database column, someone has to work out which
of *our* tables and jobs break. Today that means hours of searching by hand, and
it is easy to miss something.

Ripple does the searching. A human still decides.

**It is a search assistant, not an answer machine.** Everything it finds is
shown with the file and the exact lines, so it can be checked. Everything it
*could not read* is shown too — a clean "no impact" is worthless if it quietly
skipped four hundred files.

---

## Run it on your own machine

You need Python 3.11 or newer. Nothing else.

```bash
python -m venv .venv
```

Then, on Windows:

```bash
.venv\Scripts\pip install -r requirements.txt
```

and start it:

```bash
.venv\Scripts\python run.py
```

Your browser opens at `http://localhost:8000`. That is the whole setup.

On Mac or Linux the two commands are `.venv/bin/pip install -r requirements.txt`
and `.venv/bin/python run.py`.

---

## What to try first

1. Press **Enter manually**, then **Fill with an example**, then **Run impact
   analysis**. No email and no AI needed — this is the shortest path to seeing
   it work.
2. Or drag `samples/01-market-code-value-change.eml` onto the upload box.
3. On the results screen, click a row to see the real code and the exact line.
4. Try `samples/02-timestamp-decommission.eml` — that one comes out **high
   risk**, because the column is the sort order inside a ranking and has no
   local fix.
5. Try `samples/03-no-impact.eml` — nothing in the repository uses it, and
   Ripple says so, while still listing where the name appeared.

---

## What it is scanning

`mockrepo/` is a made-up data pipeline. Nothing in it is real, and no company's
code or data is present anywhere in this project.

It was built to contain the awkward cases on purpose:

| In the mock repo | Why it is there |
|---|---|
| `market_code` → `mc` → `mkt_cd` | A column renamed twice. A word search finds only the first name. |
| `WHERE cp.mc = 'US'` | A filter on a literal. After a value change it matches nothing and the table silently empties. |
| `ROW_NUMBER() ... ORDER BY last_upd` | A ranking. Remove the column and the wrong row wins, with no error raised. |
| `SUBSTR(country_code, 1, 2)` | Assumes a two-character code. Longer values are silently truncated. |
| `legacy_dynamic_build.py` | Builds SQL by gluing strings together. Ripple cannot read it — and says so. |
| `sp_refresh_market.sql` | A stored procedure. Not parsed. |
| `broken_syntax.sql` | Malformed. Reported, not skipped. |
| `vw_everything.sql` | `SELECT *`, which hides which columns flow onward. |
| `prospect_master` | An upstream table nothing consumes, so "no impact" can be demonstrated. |

To point Ripple at different code, set `RIPPLE_REPO` (see Settings below).

---

## How it works

```
  the notification            the repository
        |                           |
        v                           v
  read the fields            index every file
  (AI, or matching                  |
   the catalogue)                   v
        |                    find every mention          <- fast text search
        v                           |
   YOU CONFIRM  ------------------->|
                                    v
                            read the SQL properly        <- sqlglot
                                    |
                                    v
                            follow each rename           <- up to 4 hops
                                    |
                                    v
                    group under the production table it feeds
                                    |
                                    v
                     summary + drafted reply  (AI, or written out)
```

The AI is only ever used at the two ends — reading the email, and writing the
English. **It is never shown your source code.** The scanning is ordinary,
repeatable Python, so it gives the same answer every run.

### Why parsing matters

A word search can tell you `MARKET_CODE` appears in a file. Only parsing can
tell you it appears *inside a WHERE clause comparing it to `'US'`* — which is
the difference between "mentioned here" and "this breaks on the 18th".

Every finding is labelled with what the code actually does with the column:

| Label | Meaning |
|---|---|
| Filter | Used in a `WHERE`. A value change stops it matching. |
| Join key | Joined on. If both sides do not change together, rows vanish silently. |
| Ranking | The sort order picking one row per key. Removing it is silent and awful. |
| Dedup key | A `MAX`/`MIN` deciding which row survives. |
| Transform | Reshaped by a function — length and format assumptions live here. |
| Aggregation | Grouped on, so labels split across old and new values. |
| Select | Carried straight through. Changes, but nothing depends on it. |

Whether a usage actually *breaks* depends on the kind of change, so Ripple asks
you which it is (removal, value format, data type, rename) and applies that.

---

## Settings

All optional. Set them as environment variables before starting.

| Variable | Default | What it does |
|---|---|---|
| `RIPPLE_REPO` | `./mockrepo` | The folder to scan. Point at a real checkout. |
| `RIPPLE_REPO_LABEL` | `mockrepo` | The name shown in the interface. |
| `RIPPLE_SQL_DIALECT` | generic | `oracle`, `teradata`, `snowflake`, `hive`, `spark`, `postgres`… **Setting this correctly matters more than anything else here.** |
| `RIPPLE_MAX_HOPS` | `4` | How many renames deep to follow a column. |
| `RIPPLE_REPO_URL_TEMPLATE` | empty | Link findings to your Git host. |
| `GROQ_API_KEY` | empty | Turns the AI on. Without it everything still works. |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Which model to call. |
| `RIPPLE_DB` | `./ripple.db` | Where history is kept. |

Example, on Windows:

```bash
set RIPPLE_SQL_DIALECT=teradata && set GROQ_API_KEY=your-key-here && .venv\Scripts\python run.py
```

The **Settings & checks** screen inside Ripple shows what it is connected to and
has a *Test the key* button, so a bad key is obvious immediately rather than at
the worst moment.

---

## Turning the AI on

Ripple works with no AI at all — that is deliberate, not a limitation. With a
key it reads messier emails more reliably and writes better English.

1. Get a key from <https://console.groq.com>.
2. Set `GROQ_API_KEY` before starting.
3. Open **Settings & checks** and press *Test the key*.

**Before using this on anything real, read this.** Turning the AI on sends the
notification text and the findings — table names, system names, colleagues'
names — to Groq's servers. Being *able* to make the call is not the same as
being *allowed* to send that data. If in doubt, leave the key unset and use
manual mode; nothing is lost except some polish in the wording.

---

## Putting it online, free

The project is set up for Vercel's free tier, which gives a real HTTPS address
and redeploys every time you push.

1. Push this folder to GitHub.
2. At <https://vercel.com> choose *Add New → Project* and pick the repository.
3. Set the **Root Directory** to `Codebase`.
4. Add `GROQ_API_KEY` under *Environment Variables* if you want the AI on.
5. Deploy.

One thing to know: on Vercel the filesystem resets between requests, so **saved
history does not survive**. Everything else works. Running locally keeps history
properly.

---

## Tests

```bash
.venv\Scripts\python -m pytest tests -q
```

37 tests. Most of them exist to prove Ripple is *honest* rather than that it is
clever — that unreadable files are reported, that a clean result still says
where the name appeared, that a generic word like `STATUS` does not produce a
page of false hits.

---

## The files

```
run.py              start it locally
api/index.py        start it on Vercel (same app)
ripple/
  config.py         every setting, in one place
  api.py            the web routes - deliberately thin
  catalog.py        what tables and columns exist, learned from the code
  notification.py   reading .msg / .eml / pasted text, and pulling out fields
  ai.py             the optional AI calls, with fallbacks
  narrative.py      the summary and reply, written without AI
  store.py          history (SQLite)
  scanner/
    repo.py         walking the repository and searching it
    sqlread.py      parsing SQL and classifying how a column is used
    lineage.py      following renames, and grouping by production table
web/                the interface - plain HTML, CSS and JavaScript, no build step
mockrepo/           the synthetic pipeline being scanned
samples/            example notification emails
tests/              the test suite
```

There is no build step and no framework anywhere in `web/`. That is on purpose:
it can be opened, read and changed by anyone, including in an environment where
installing tooling is difficult.

---

## Known limits

Worth saying out loud, because a tool like this is dangerous when it looks more
certain than it is.

- **It reads one repository.** Lineage that crosses into another team's code is
  invisible to it. What you get is *your* exposure, not the whole blast radius.
- **SQL built by gluing strings together cannot be followed.** Those files are
  listed as unreadable, but they are a real hole.
- **Stored procedure bodies are not parsed.**
- **`SELECT *` hides which columns flow onward.**
- **A Spark job writing to several tables** cannot be attributed reliably, so
  lineage stops there — and says so.
- **Columns are matched by name.** Two different tables using the same column
  name can produce a finding that needs a human to dismiss.
