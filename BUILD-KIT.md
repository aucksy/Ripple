# Building Ripple from scratch, one chat at a time

A kit for rebuilding Ripple on a machine where the only help available is a chat
window — Copilot with a good model, but no ability to read your files, run your
tests or edit anything itself. You do the saving and the running; the chat does
the writing.

Twelve chat windows, one file or two each, in order. Every window is a stranger
who has never met the others, which is the whole difficulty and the reason for
the contract card below.

---

## Before you start

Four things decide whether this is worth beginning.

**1. Can you run Python there, and can you install packages?**
Ripple needs a handful of things that do not come with Python, and one of them —
`sqlglot`, which reads the SQL — is not something a chat window can write for
you. Check Python first:

```
python --version
```

Then pip. Three things go wrong on a managed laptop, in this order, and each has
a fix:

- **"pip is not recognized as an internal or external command."** Nothing is
  blocked. Typing `pip` makes Windows hunt for a file it has not been told
  about. Type `python -m pip` instead, always, and it works.
- **"No module named pip."** Python was installed without it. Python carries a
  spare copy inside itself, needing no internet and no admin rights:
  `python -m ensurepip --upgrade --user`
- **Timeouts reaching pypi.org.** Your network blocks the public package site.
  Almost every large firm runs an internal mirror instead — ask whoever sits
  near you "how do you pip install here?", then point pip at it once and forget
  about it: `python -m pip config set global.index-url <their address>`

Then install, pinned to the versions these phase prompts were written against:

```
python -m pip install --user sqlglot==25.24.0 fastapi==0.115.0 uvicorn==0.30.6 pydantic==2.13.4 typing-inspection==0.4.2 python-multipart==0.0.9 extract-msg==0.48.7 httpx==0.27.2 pytest==8.3.3
```

`python-multipart` is what lets a notification file be uploaded. `extract-msg`
opens Outlook `.msg` files, which is how most notifications actually arrive.
`httpx` is only used if you later turn on the optional AI reader, and can be
left out.

`pydantic` and `typing-inspection` are not needed by name — FastAPI brings them
along by itself — but they are pinned here because of the one thing that really
does go wrong on a company mirror.

**If a single package is refused with a 403 while everything around it downloads
perfectly, the mirror is not broken.** A mirror routinely holds back a version
published in the last few days, because nothing has scanned it for security yet.
The fix is to pin that one package a few versions back and run the whole command
again: whatever asked for it almost always wants a minimum version rather than an
exact one, so an older release satisfies it just as well. That is the whole story
of `typing-inspection` above — `pydantic` asks for 0.4.2 or newer, the newest was
published the day before and was blocked, and 0.4.2 itself is ten months old and
comes straight through.

A refusal is not a rollback, either. pip downloads everything before it installs
anything, so one 403 near the end means nothing at all was installed, however much
of it you watched come down. Fix the pin and run the same command again.

If there is no mirror and no route in at all, stop and say so — the plan changes,
because `sqlglot` has to get onto the machine somehow.

**2. Will the chat take a long prompt and give back a long answer?**
Two of these files are 800 lines. Test it before you invest an evening: paste
Phase 1 and see whether you get a complete file or something that trails off
into "... rest of the implementation". If it truncates, ask it for the file in
labelled parts and paste them together.

**3. Build the core first.** The core is: read the folder, follow the column,
show the findings, write the reply. The AI email reader and the packaged Windows
program are extras. Neither is needed for the thing to be useful.

**4. Budget the time.** Twelve windows is two focused evenings if it goes well.
Phases 4 and 5 are most of the difficulty; if you only get that far you already
have the part that no other tool does.

---

## The two ways this goes wrong

**Drift.** Window 6 invents its own names for what window 4 already built, and
nothing fits together. The fix is the contract card: paste it at the top of
*every* window, every time, before the phase prompt. It is the shared memory the
chats do not have.

**Confident wrong answers.** A chat asked to build "a SQL impact analyser" will
build one that gives a clean green result whenever it fails to understand
something, because that is the obvious thing to build and it looks better in a
demo. The rules that stop it are in the contract card under **THE ONE RULE**. Do
not trim them to save space. They are the product.

---

## The build order

| # | The window builds | Roughly |
|---|---|---|
| 0 | *The contract card — not a build. Paste it at the top of every window.* | — |
| 1 | Settings, and the published-tables list | 400 lines |
| 2 | Walking the repository folder | 350 lines |
| 3 | Templated SQL and scripting blocks | 400 lines |
| 4 | Reading SQL into statements and usages | 850 lines |
| 5 | The catalogue, and following a column | 650 lines |
| 6 | Reading the notification email | 450 lines |
| 7 | Writing the summary and the reply | 250 lines |
| 8 | Progress, saved history, and the web service | 800 lines |
| 9 | The page and its styles | 550 lines |
| 10 | The screens: notification, review, repository | 600 lines |
| 11 | The screens: findings, map, summary, reply, settings | 1,000 lines |
| 12 | Starting it up, and the checklist that says it works | — |

Folder layout you are building towards. **Make these folders first**, before
window 1, and put an empty `__init__.py` in both `ripple/` and `ripple/scanner/`
— Python will not find the code without them.

```
ripple-build/
  run.py
  ripple/
    __init__.py            <- empty, but it must exist
    config.py  production.py  catalog.py  notification.py
    narrative.py  progress.py  store.py  api.py
    scanner/
      __init__.py          <- empty, but it must exist
      repo.py  templating.py  sqlread.py  lineage.py
  web/
    index.html  styles.css  app.js
  tests/
    test_production.py  test_repo.py  test_templating.py
    test_sqlread.py  test_lineage.py  test_notification.py
    test_narrative.py
  mockrepo/                <- a tiny fake pipeline to test against (Phase 12)
```

On Windows, in the folder you want the project in:

```bash
mkdir ripple-build ripple-build\ripple ripple-build\ripple\scanner ripple-build\web ripple-build\tests
type nul > ripple-build\ripple\__init__.py
type nul > ripple-build\ripple\scanner\__init__.py
```

Every phase below says where its files go, and the contract card makes the chat
repeat it back to you at the end of every reply. If a reply does not end with a
**SAVE THESE FILES** block, ask for one before you save anything — one file in
the wrong folder and the next window fails for a reason that looks like bad code.

---

# PHASE 0 — the contract card

Paste this first in every window. Then paste the phase prompt underneath it.

````text
You are helping me build a tool called Ripple, one file at a time, across
several separate chats. You cannot see the other chats, so this card is the
shared contract. Follow it exactly. Do not rename anything in it.

WHAT RIPPLE IS
An upstream data team emails us: "we are changing MARKET_CODE in
CUSTOMER_DEMOGRAPHICS on 18 September." Ripple reads our own pipeline
repository and answers: what breaks, where, and what do we tell them.
A column rarely keeps its name — MARKET_CODE becomes mc, then mkt_cd — so a
word search is useless. Ripple parses the SQL and follows the rename chain to
the tables our team publishes.

THE ONE RULE THAT OVERRIDES EVERYTHING
Never claim more than was actually read.
- If files could not be opened, or could not be parsed, the headline, the
  summary and the drafted reply must all say so. Never "no impact, proceed as
  planned" over a repository that was only partly read.
- If nothing was read at all, say "nothing was scanned", never "no impact".
- Never invent a count, a percentage, or a progress bar. Every number on
  screen is something that was actually counted. Where there is genuinely no
  total, show the count and no fraction.
- Anything the reader could not follow is listed on screen with the file and
  the line, never dropped.
- Never show a green tick unless it is genuinely earned.
When in doubt the more cautious wording wins. A tidier screen that says less
is a worse screen.

STACK
Python 3.10 or newer — assume 3.10, so put "from __future__ import annotations"
at the top of every module. FastAPI + uvicorn + pydantic for the service, and
sqlglot 25.24.0 for the SQL: write against how that version behaves.
The front end is plain HTML, CSS and JavaScript in three files — no build
step, no framework, no npm, no CDN, no TypeScript, no inline event handlers.
Tests with pytest.

FILE MAP (build order)
ripple/config.py               settings, read from environment variables
ripple/production.py           which tables the team publishes
ripple/scanner/repo.py         walking the folder, holding files, word search
ripple/scanner/templating.py   filling {{placeholders}}, dropping scripting
ripple/scanner/sqlread.py      parsing SQL into statements and usages
ripple/catalog.py              tables and columns learned from CREATE
ripple/scanner/lineage.py      following a column, producing findings
ripple/notification.py         reading a .msg / .eml / pasted email
ripple/narrative.py            writing the summary and the reply, without AI
ripple/progress.py             what the engine is doing this second
ripple/store.py                saving analyses to SQLite
ripple/api.py                  the web service
web/index.html web/styles.css web/app.js    the front end

DATA SHAPES THAT CROSS FILE BOUNDARIES — do not change these names
SourceFile  : path (repo-relative, forward slashes), abs_path, text, lang
Statement   : file, lang, line_offset, sql, target, sources (set of table
              names read), select (sqlglot Select or None), expr (sqlglot node)
ParsedRepo  : statements[], unreadable[], parsed_files (set of paths),
              opaque {path: [{line, text, sql}]}, runs_sql_from[]
Usage       : kind, column, alias, detail, certain
              kind is one of: filter, join_key, ranking, dedup_key,
              transform, aggregation, select

A finding, as JSON sent to the browser:
  {inter, from, attr, roots[], alias, logic, mode, impact, breaking,
   noLocalFix, file, lang, lines[{n, t, hit}], certain}

A scan result, as JSON sent to the browser:
  {attributes[], groups[], reached[], other[], graphs[], unreadable[],
   mentionsOnly[], heldOnline[], pathTooLong[], filesScanned, filesMatched,
   risk, stats{}}
  risk is one of: high, medium, low, none
  stats = {productionTables, tablesReached, intermediateTables,
           attributesImpacted, filesWithImpact, breakingUsages,
           couldNotRead, neverOpened}
  groups[]  = tables ON the published list, each {prod, note, rows[]}
  reached[] = tables the chain ends at that are NOT on the published list.
              These must never be thrown away: a real breaking impact shown
              as a clean result because the tables are not called _PROD is
              the exact failure this tool exists to prevent.
  other[]   = real usages in code that builds no table Ripple can name

HOUSE STYLE
- Comments explain WHY, not what. A comment restating the code is noise; a
  comment recording the mistake the line prevents is worth keeping.
- Every string shown on screen is plain English a non-engineer can act on.
  Not "ParseError at line 42" but "1 of 14 statements in this file could not
  be read — line 42 · CREATE OR REPLACE PROCEDURE ...".
- British spelling. No emoji. No exclamation marks.
- Type hints on function signatures. Dataclasses over dicts internally.
- Every table and column name in examples and tests is invented. Never use a
  real-looking internal name.

WHERE THINGS GO — the project root is the folder I run python from
  ripple-build/
    run.py
    ripple/
      __init__.py            (empty file, but it must exist)
      config.py  production.py  catalog.py  notification.py
      narrative.py  progress.py  store.py  api.py
      scanner/
        __init__.py          (empty file, but it must exist)
        repo.py  templating.py  sqlread.py  lineage.py
    web/
      index.html  styles.css  app.js
    tests/
      test_production.py  test_repo.py  test_templating.py
      test_sqlread.py  test_lineage.py  test_notification.py
      test_narrative.py
    mockrepo/                (a small fake pipeline to test against)

WHAT I WANT BACK
Complete files, ready to save. No "...rest unchanged", no placeholders, no
TODOs. If a file would be very long, say so and give it to me in clearly
labelled parts I can concatenate.

END EVERY REPLY WITH A BLOCK EXACTLY LIKE THIS, and nothing after it:

  SAVE THESE FILES
    ripple-build/ripple/config.py          <- the first code block above
    ripple-build/ripple/production.py      <- the second code block above
    ripple-build/tests/test_production.py  <- the third code block above
  FOLDERS THAT MUST EXIST FIRST
    ripple-build/ripple/   ripple-build/tests/
  EMPTY FILES TO CREATE IF THEY ARE NOT THERE YET
    ripple-build/ripple/__init__.py
  THEN RUN
    cd ripple-build
    python -m pytest tests/test_production.py -q

Paths are always relative to the project root and always use forward
slashes. Name every file you produced, in the order you produced it, and say
which code block is which. If you split one file into parts, say so and say
what order to paste them in. I am saving these by hand, so if you are vague
about the path I will put it in the wrong place and the next chat will fail.
````

---

# PHASE 1 — settings, and the published-tables list

**Saves to:** `ripple-build/ripple/config.py`, `ripple-build/ripple/production.py`,
`ripple-build/tests/test_production.py`

````text
[PASTE THE CONTRACT CARD FIRST]

Build ripple/config.py, ripple/production.py and tests/test_production.py.

--- ripple/config.py

A Settings dataclass with a module-level `settings` instance. Every field has
a default read from an environment variable, so a laptop, a demo host and a
locked-down machine differ only by environment. Fields:

  repo_path, repo_label, repo_branch
  sql_dialect          empty string means generic
  max_hops             default 4 — how many renames deep to follow a column
  code_extensions      .sql .ddl .hql .py .scala .java .sh .xml .yaml .yml
  skip_dirs            .git .venv venv node_modules __pycache__ target build dist
  max_file_bytes       2_000_000
  max_upload_bytes     25_000_000
  db_path
  production_patterns  tuple of recognised entries — what is matched against
  production_text      the raw paste, kept exactly as it arrived so the box
                       can be opened and edited again rather than handing
                       somebody back a tidied version of their own list

Environment variables: RIPPLE_REPO, RIPPLE_REPO_LABEL, RIPPLE_SQL_DIALECT,
RIPPLE_MAX_HOPS, RIPPLE_PROD_TABLES, RIPPLE_DB.

Methods: production() returning the parsed rule (cached, because it is asked
once per table visited on every hop of every scan); set_production(text);
is_production_table(name); production_rule() returning a SHORT one-line
summary — two hundred pasted names do not fit on a line, so a long list is
counted ("44 table names and 1 pattern (_PROD)") while a short one is shown
in full.

--- ripple/production.py

This is the important file. It decides which tables count as "published by
our team", which decides whether a finding counts as production impact —
which is what the headline, the risk level and the drafted reply are all
built from. Getting it wrong turns a change that really breaks three
published tables into a calm "no impact".

It must accept a PASTED LIST of real table names in whatever shape the list
arrives, because it will be copied out of Excel, Slack, Confluence or a query
result. Handle all of these with no tidying up by the user:

- one table per line; comma separated on one line; comma separated across
  several lines; semicolons; tab separated
- a paste from Excel with SEVERAL columns: work out which column holds the
  table names, and REPORT which one it took. A heading containing the word
  "table" settles it. Otherwise score each column by how many of its cells
  look like a real table name, where "real" means it also contains an
  underscore, a dot or a digit.
- a heading row on top: "Table name", "TABLE_NAME", "Name", and similar
- Slack and Confluence decoration: bullets • - * and numbering 1. 1) (1),
  backticks, ``` code fences, quotes, trailing commas and semicolons,
  markdown table pipes and ruled lines
- fully qualified prj-p-x.dataset.table, two-part dataset.table, and bare
  table, all mixed together in one paste
- different capitalisation, duplicates, blank lines, stray spaces

Classification of each entry, and this must not change existing behaviour:
  contains * or ?   -> a glob pattern, matched against the whole table name
  starts with _     -> a suffix pattern, matches the END of a table name
  anything else     -> an exact table name, matched exactly
So rules somebody set months ago (_PROD, PROD_*) go on meaning exactly what
they meant. SQL only ever gives us the last part of a name, so an exact name
is matched on its last dot-separated part, while the whole thing as pasted is
kept for showing back on screen.

BE HONEST ABOUT THE PASTE. Return, alongside the entries, a list of notes
saying what was left out and why, each already written as a sentence ready to
show on screen, with examples:
  "1 line looked like a heading row and was ignored."
  "3 duplicates removed."
  "The paste had 3 columns. Ripple read the column headed \"Table name\" and
   ignored the other 2."
  "2 lines did not look like a table name and were ignored."
  "1 pair of names is the same table to Ripple, so only the first was kept:
   SQL only ever says the last part of a table name."
Nothing may be dropped silently. And never split prose into invented table
names — "please confirm by friday" must come back as ignored, not as four
published tables Ripple would then never find.

Also provide:

  check_against_repo(rule, index, parsed) -> dict

which answers the question this whole feature exists for: WHICH OF THE
PASTED TABLES HAS RIPPLE NEVER SEEN. Three answers, and the difference sends
a person to two completely different places:
  found    the table is in the SQL that was read
  written  the name is in the repository, but nothing readable builds it
  nowhere  the name is not in this repository at all
For a name that matches nothing but IS the ending of tables that do exist,
report how many, so the screen can ask "did you mean it as a pattern?"
instead of quietly deciding. Also report, per pattern, how many tables here
it matches — a pattern matching zero tables is doing nothing at all, and
that is worth knowing before a result from it is believed.
Do the file scan for missing names in ONE pass over all files, not one pass
per name: a real repository is tens of megabytes.

An empty list must fall back to the shipped default (_PROD, _PRD,
_PUBLISHED). An empty rule would mean "no table is ever production", which
would report every repository on earth as clean.

--- tests/test_production.py

Write these tests, using only invented table names:
  a list survives however it was copied — one per line, commas on one line,
    commas across lines, semicolons, blank lines and spaces, Slack bullets,
    numbering, backticks, a code fence, quotes and trailing commas, space
    separated on one line
  an Excel column keeps its heading out of the list
  several Excel columns pick the one with the tables in it, and say which
  several columns with no heading still pick the table column
  a markdown table from Confluence reads as a list
  qualified, two-part and bare names mix in one paste
  duplicates and capitalisation are reduced and reported
  two names Ripple cannot tell apart are reported, not silently deduplicated
  a line that is not a table name is reported, never dropped silently
  prose is never split into invented table names
  every pattern still does exactly what it did before (parametrised)
  an exact name matches only that table — stg_sales_daily is NOT sales_daily
  names and patterns work side by side
  an empty box falls back rather than meaning no table is production
  the one-line form counts a long list instead of printing it
````

**Check it worked:** `python -m pytest tests/test_production.py -q` — all green. Then in a
Python prompt, paste a messy list and print the notes. If the notes are empty on
a paste that clearly had junk in it, the honesty half is missing and you should
push back in the same chat.

---

# PHASE 2 — walking the repository folder

**Saves to:** `ripple-build/ripple/scanner/repo.py`, `ripple-build/tests/test_repo.py`

````text
[PASTE THE CONTRACT CARD FIRST]

Build ripple/scanner/repo.py and tests/test_repo.py.

A RepoIndex dataclass holding every readable file in memory, built by
RepoIndex.build(root, cfg, on_progress=None). Text compresses well and only
files with a useful extension are kept, so a real repository fits easily.

Fields: files[] of SourceFile, skipped[], root, held_online[], too_long[],
in_skipped_dirs[], skipped_dir_names[].

Rules that matter, each for a reason:

1. LONG PATHS. On Windows, prefix the walk root with \\?\ (or \\?\UNC\ for a
   share) so the walk gets past the 260-character limit whether or not long
   path support is switched on. A managed laptop usually has it switched off,
   and real repository folders are 140 characters before the filename starts.
   A file that still cannot be opened and whose path is over 260 characters
   goes in too_long, not in a generic error list.

2. FILES THAT ARE NOT REALLY THERE. OneDrive Files On-Demand leaves a file in
   the listing, with its real name and size, when the contents are still in
   the cloud. Opening it asks OneDrive to fetch it, which on a machine with no
   network hangs and then fails, once per file, and there can be thousands.
   Detect it BEFORE opening, from the Windows file attributes:
     FILE_ATTRIBUTE_RECALL_ON_OPEN         0x40000
     FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS  0x400000
   Either of those means the contents are not here: record in held_online and
   do not open. FILE_ATTRIBUTE_OFFLINE (0x1000) is older and much looser —
   some backup software sets it on perfectly local files — so on its own treat
   it as suspicion only and still open the file. Also treat a read failure
   whose message contains the word "cloud" as the same thing.
   This is the most dangerous thing that can happen to a scan: half a
   repository never read comes back with a short finding list and a green
   tick, and the green tick is the only thing this tool sells.

3. SKIPPED FOLDERS. Judge the skip-dirs names against the path INSIDE the
   repository, never the whole path — a repository that happens to live under
   a folder called build or venv must not read as empty. And when a file that
   WOULD have been read is skipped because of its folder, record it in
   in_skipped_dirs and the folder name in skipped_dir_names. In most
   repositories "build" and "target" hold generated output; in a few they hold
   the pipeline, and then this is a scan of half a repository with nothing on
   screen to say so.

4. Files over max_file_bytes, and files that will not decode as UTF-8 (try
   latin-1 second), go in skipped[] with a plain-English reason.

Also in this file:

  search(names) -> Match[]        every line mentioning any of these names as
                                  a whole word, case-insensitive
  files_mentioning(names)
  get(path)
  extract_sql_blocks(f)           SQL inside triple-quoted and long single
                                  strings in .py .scala .java .sh files,
                                  returning (text, 0-based line offset) so a
                                  finding still points at a real line
  statements_for(f)               the above for program files, the whole text
                                  for .sql files
  sql_file_refs(f)                every "something.sql" string a program
                                  names, with its line. A DAG that runs the
                                  most important query in the pipeline used to
                                  look identical to an empty file.
  written_tables(f)               tables a program writes to, from
                                  saveAsTable / insertInto /
                                  createOrReplaceTempView / registerTempTable,
                                  and from destination= / destination_table= /
                                  to_gbq(. Take the last dot-separated part.
                                  Spark and BigQuery jobs run a bare SELECT
                                  and name the destination in the program, not
                                  the SQL, so without this the chain stops
                                  exactly where the interesting renames are.
  looks_like_unread_sql(f, blocks)  SQL is plainly written in this file and
                                  none could be extracted — the shape where a
                                  statement is built by adding short strings
                                  together and never exists as one thing.

Write tests/test_repo.py with a tmp_path repository covering: extensions,
skip-dirs judged inside the repository only, skipped code files being counted
and named, a too-large file reported, SQL pulled out of a Python triple-quoted
string with the right line offset, a .sql reference found, a write target
found, and whole-word search not matching a substring.
````

**Check it worked:** `python -m pytest tests/test_repo.py -q`. Then point it at a folder on
your machine and print `len(idx.files)`, `idx.skipped_dir_names`,
`len(idx.held_online)`.

---

# PHASE 3 — templated SQL and scripting blocks

**Saves to:** `ripple-build/ripple/scanner/templating.py`,
`ripple-build/tests/test_templating.py`

````text
[PASTE THE CONTRACT CARD FIRST]

Build ripple/scanner/templating.py and tests/test_templating.py.

Almost no production SQL is plain SQL, and both problems below cause the same
disaster: a repository that is almost entirely readable is reported as almost
entirely unreadable, and a scan over a repository that was never read reports
no impact.

PART ONE — placeholders.

Airflow, dbt and in-house generators wrap the parts that change:

  CREATE OR REPLACE TABLE {{tgt_project_id}}.{{stage_dataset}}.web_activity AS

A SQL parser has never met a { in that position and refuses the whole file.
Ripple is not the templating engine and does not need to be: it needs the
shape of the statement and the names in it, and the table name is sitting
right there. So replace each placeholder with an ordinary identifier made out
of its own text, giving tgt_project_id.stage_dataset.web_activity, which
parses as the three-part name it always was.

Handle: {# comments #}, {% tags %} (remove the tag, keep the SQL between),
{{ vars }} including Jinja filters {{ x | upper }}, ${ dollar } for shell and
Databricks, and { python_format } — the last one deliberately narrow, so that
a regular expression's {3} inside a string literal is left alone. For dbt,
ref('orders') and source('raw','orders') resolve to the last quoted name,
because that is a real table and taking it is the whole point of ref().

TWO RULES THIS FILE KEEPS:
  Line numbers do not move. Every replacement puts back exactly as many line
  breaks as it swallowed, so a finding still points at the real line of the
  real file, which is the only line anybody can go and look at.
  The original text is never changed. This is done to a copy on the way into
  the parser; everything shown on screen comes from the file as written.

Also provide describe(text) returning what kind of templating is in a file,
in words, for the screen: "{{ ... }} templating (Airflow, dbt or similar)".

PART TWO — scripting blocks.

Every file in a real BigQuery pipeline is wrapped in DECLARE ... BEGIN ...
END, often with a FOR loop or an IF inside. A SQL parser hands back BEGIN as
something it cannot read and, because BEGIN has no semicolon of its own,
SWALLOWS THE STATEMENT THAT FOLLOWS IT. That is the quietest possible
failure: the file parses, nothing is reported, and the first real statement
of every file has vanished.

Replace scripting keywords with an empty statement on the copy going into the
parser, keeping every line where it was:
  always scripting: BEGIN [TRANSACTION], END IF/FOR/WHILE/LOOP,
    COMMIT/ROLLBACK, EXCEPTION WHEN ... THEN, LOOP, LEAVE/ITERATE/BREAK/
    CONTINUE
  scripting only when no CASE is open: a bare END, a bare ELSE, and
    [ELSE]IF ... THEN

That last group is the trap. ELSE and END are also how an ordinary CASE
expression is written down the page:

  CASE WHEN status = 'A' THEN 'Active'
  ELSE
    'Unknown'
  END AS status_desc

Cutting those two lines puts a semicolon in the middle of a CASE and destroys
the statement they sit in — a 600-line CREATE TABLE thrown away whole, with
every table and column in it. So track CASE depth as the file is walked, and
only treat those two words as scripting when no CASE is open.

Count CASE depth on a copy of each line with STRING LITERALS AND COMMENTS
BLANKED OUT, carrying quote and comment state across lines. A keyword inside a
quoted string is not scripting, and a 600-line statement is exactly where a
stray '... END ...' turns up. Handle ' " ` ''' """ -- /* */ and #.

Three more shapes:
  RAISE USING MESSAGE = @@error.message — the last line of the exception
    handler every generated file ends with, and by a distance the commonest
    thing a parser refuses. It re-throws an error, reads no table and touches
    no column, so it is nothing to a scan — but one of them puts the file on
    the "check by hand" list, and a list padded with hundreds of files nobody
    needs to check is a list nobody reads. Consume it up to its semicolon,
    which may be several lines later.
  CREATE OR REPLACE PROCEDURE `x.y.z`(IN tbl STRING, ...) — drop the
    signature, which no parser reads, and KEEP the BEGIN ... END body, which
    is ordinary SQL worth reading.
  FOR x IN (SELECT ...) DO / WHILE ... LOOP — a loop header names a real
    table. Turn the header into "SELECT * FROM (...)" so that table is seen.
    Read the table name off the line AS WRITTEN, not off the blanked copy —
    it is usually a quoted name and blanking would leave an empty query.
    Headers written across several lines must be gathered.

unwrap_blocks(text) returns the text UNCHANGED when there is no scripting in
it, so callers can hand everything to it without asking first. Asking first
means walking every line of every file twice, which on a few thousand files
is minutes rather than seconds.

Tests: line numbers preserved through every substitution; a CASE written down
the page survives intact; a scripting END is dropped; a keyword inside a
string is not treated as scripting; BEGIN does not eat the statement after
it; a procedure body is kept; a loop header keeps its table; a multi-line
RAISE is consumed whole.
````

**Check it worked:** `python -m pytest tests/test_templating.py -q`. Then paste one of your
own real files into a Python prompt and confirm `sqlglot.parse(unwrap_blocks(fill_placeholders(text)), read="bigquery")` does not raise.

---

# PHASE 4 — reading SQL into statements and usages

**Saves to:** `ripple-build/ripple/scanner/sqlread.py`,
`ripple-build/tests/test_sqlread.py`

This is the file the whole tool rests on. Expect to spend a whole window on it.

````text
[PASTE THE CONTRACT CARD FIRST]

Build ripple/scanner/sqlread.py and tests/test_sqlread.py.

The whole value of Ripple is in this file. A word search can tell you that
MARKET_CODE appears in a file. Only parsing can tell you it appears inside a
WHERE clause compared against the literal 'US' — which is the difference
between "mentioned here" and "this breaks on the 18th".

PARSING

parse_file(f, cfg) -> (statements, problems, opaque)
parse_repo(index, cfg, on_progress) -> ParsedRepo

Parse each block with sqlglot at cfg.sql_dialect. If the whole block is
refused, SPLIT IT AND PARSE STATEMENT BY STATEMENT. sqlglot reads a file as
one piece and gives up at the first statement it cannot follow, taking every
other statement down with it — so one GRANT, one procedure call, one line in
another dialect costs the entire file. Splitting first means one bad
statement costs one statement, and the file is reported as "3 of 14 could not
be read" rather than "unreadable".

Write the splitter yourself: split on semicolons that are NOT inside quotes
or comments, returning (statement_text, 0-based start line). Handle ' " `
escapes, -- and # line comments, and /* */ blocks.

Run every block through fill_placeholders (only when needed) and then
unwrap_blocks from Phase 3, on the way into the parser ONLY.

For each parsed statement build a Statement with:
  target   from Create, Insert, MERGE, Delete and Update. MERGE matters as
           much as CREATE and INSERT: on BigQuery, Snowflake and Databricks it
           is the usual way a production table is loaded, and without it the
           chain stops one step short of the table anyone actually reads.
           DELETE and UPDATE matter for a different reason — they build
           nothing, so they look uninteresting, but a DELETE whose WHERE
           filters on the attribute being decommissioned stops working on the
           day it goes, and the table it prunes quietly fills up instead.
           If the file is a program with exactly one write target, use that.
           More than one write target: report that lineage past this job is
           not traced, and say which tables.
  sources  every table the SELECT reads, EXCLUDING names defined by WITH — a
           CTE is a name for a query, and treating one as a table invents a
           link that is not there. A DELETE or UPDATE also reads its own
           target, or nothing ever looks at its WHERE clause.

Statements sqlglot returns as a Command — a procedure call, a loop, an
EXECUTE IMMEDIATE, a scripting block — go into `opaque` keyed by file, with
line, first code line, and the SQL text. Kept, not reported: whether they
matter depends entirely on whether the name somebody is chasing turns up
inside one, which is not known here.

Report as unreadable, with plain English, a line number and the line itself:
  a file where some statements failed ("2 of 63 statements in this file could
    not be read — the other 61 were")
  a file that was read but NOT ONE statement was understood — the quietest way
    to lose a file, and the reason the wrong SQL dialect used to look like a
    clean repository
  a file that plainly contains SQL none of which could be extracted
  a program that runs a .sql file which is not in this repository — Ripple has
    never read that query, so nothing it does is covered by any scan
Add a hint when the file is a template, and when the repository is being read
as generic SQL. Collapse repeated failures in one file to a single entry with
a count: it is still one file for a person to go and check.

WHICH TABLE A COLUMN CAME FROM

In a real warehouse the same two or three key columns are in nearly every
table, so nearly every join has the same name on both sides. Matching on the
name alone reports a filter on the OTHER table's column as a usage of the one
being changed — a finding about the wrong table, in a repository where that
is the ordinary case rather than an edge one.

The statement usually says which is which, and when it does, that is a fact
about the SQL rather than a guess: a.cm13 belongs to whatever a is. Write
_belongs_to(...) returning "yes", "no" or "unknown":
  no qualifier    -> yes if the statement reads only one table, else unknown
  qualifier resolves to another table -> no
  qualifier resolves to a CTE          -> unknown (that IS the chain being
                                          followed, so not a reason to rule
                                          the usage out)
Where it says "no", drop the usage. Where it says "unknown", KEEP the usage
and set certain=False. Nothing is thrown away; the table is marked as
inferred rather than asserted.

WHAT NAME A COLUMN LEAVES UNDER

output_names(stmt, column) -> list[str]

Renames often happen inside a subquery — c.last_upd AS lut_ts buried in a
ranking, then carried out unchanged by the enclosing SELECT — so resolve from
the INNERMOST query outwards. A SELECT * means every name passes through
untouched.

A column also leaves under MORE THAN ONE name more often than it looks:

  SELECT CAST(cm13 AS STRING) AS cm13_str, cm13 FROM customer_demographics

Following only the first was a silent, expensive mistake: the next table
reads cm13, not cm13_str, so the chain stopped one step short and a change
that really does reach a published table was reported as no production
impact. Return every name, capped at 6, with the name carried through
UNCHANGED always first so it survives the cap.

Build the projection maps for a statement in ONE pass and cache them on the
statement. One scan asks the same statement about the same column many times,
and on a 600-line statement each answer means walking the whole tree again.
Measured on a real repository, this was most of the time a scan took.

HOW A COLUMN IS USED

usages_of(stmt, column, table) -> Usage[]

Look for the column in: the select list (Column -> select, anything else ->
transform with the function name), WHERE and HAVING (filter, with the literal
it is compared against as `detail`), JOIN ... ON (join_key), GROUP BY
(aggregation), window ORDER BY (ranking — where removal is silent and awful),
and MAX/MIN (dedup_key, which decides which row survives).

A DELETE or UPDATE has a WHERE clause and no SELECT at all. Requiring a SELECT
made both invisible, so "DELETE FROM stage WHERE market_code = 'US'" was
reported as no usage whatsoever.

Return the most informative reading of each kind, most consequential first:
ranking, dedup_key, filter, join_key, transform, aggregation, select. One the
SQL was explicit about beats one it was not; after that, one carrying a
detail beats one that does not.

Also: mode_of(usages) returning "Transformed" if any transform, dedup_key or
aggregation, else "Direct pull"; locate(file, column, kind, line_offset)
giving the best guess at the real 1-based line, scoring lines by whether they
also contain the keywords that kind lives near; snippet(file, line, note)
returning a few lines of real code with the important one marked.

Tests: a statement split rescues the readable statements around a bad one;
MERGE, DELETE and UPDATE are seen; CTE names are not treated as tables; a
column renamed inside a subquery is followed out; a column leaving under two
names returns both; a filter records the literal; a join on the other table's
column of the same name is not reported; where the SQL does not say, the
usage is kept with certain=False; a window ORDER BY is a ranking.
````

**Check it worked:** `python -m pytest tests/test_sqlread.py -q`. Then run it over one of
your own real folders and print how many files parsed versus how many landed in
the unreadable list. If almost everything is unreadable, the dialect is wrong or
Phase 3 is not being applied.

---

# PHASE 5 — the catalogue, and following a column

**Saves to:** `ripple-build/ripple/catalog.py`,
`ripple-build/ripple/scanner/lineage.py`, `ripple-build/tests/test_lineage.py`

````text
[PASTE THE CONTRACT CARD FIRST]

Build ripple/catalog.py, ripple/scanner/lineage.py and tests/test_lineage.py.

--- ripple/catalog.py

Rather than being handed a data dictionary, Ripple reads every CREATE it can
find and builds one. build_catalog(parsed) -> Catalog with tables
{TABLE: [columns]}, defined_in {TABLE: file}, and gaps[].
CREATE TABLE x (col type, ...) gives the columns directly. CREATE TABLE x AS
SELECT gives them from the projection. A table created without a readable
column list, or built with SELECT *, goes in gaps with a plain reason — the
real column list is not visible there and pretending otherwise is a lie.

--- ripple/scanner/lineage.py

trace(index, parsed, upstream, change_type, cfg, on_progress) -> ScanResult
where upstream is [{"table": "...", "attrs": ["...", ...]}].

Walk each attribute out from its table: find every statement that READS the
current table, ask usages_of for the current column, record a Finding, then
recurse into the statement's target under EVERY name the column leaves as,
up to cfg.max_hops, with a seen-set so a cycle cannot loop.

When the target is on the published list: record it as a production group AND
KEEP GOING. One published table feeding another is exactly how a change
spreads, and stopping at the first under-counts the number the whole tool is
judged on, while drawing a shorter chain than the real one.

When nothing further is built from a table, the chain ends there. Record it —
do not drop it. A chain ending at a table that does not happen to match the
published-table rule is still a table somebody has to look at, and dropping
those was how a real breaking impact got shown as a clean result.

A Finding carries: source table and column, target table, alias, the usage
kind and its label, mode, a plain-English impact sentence, breaking,
no_local_fix, file, lang, snippet lines, hop, certain, and `roots` — the
attributes the person actually asked about. Two renames down, the column on a
row is no longer called what they typed, and without roots the row cannot be
traced back to the question. roots must NOT be part of what makes two
findings equal: one usage can be on the path of more than one attribute.

Which changes break which usages:
  removal, rename : filter, join_key, ranking, dedup_key, transform,
                    aggregation, select
  value_change    : filter, join_key, transform
  type_change     : filter, join_key, transform
  unknown         : filter, join_key, ranking, dedup_key, transform
No local fix: ranking and dedup_key, when the change is a removal or a
rename — the replacement has to come from the upstream team.

The impact sentence is the thing a person reads and acts on, so write real
sentences, not labels. For example: a join on the raw value — "Unless both
sides change on the same day, matching rows are dropped silently — no error,
just fewer rows." A ranking — "This column is the sort order inside a ranking
that picks one row per key. Without it the choice becomes arbitrary; the
wrong record can win, and nothing is raised to tell you."

Risk: high if any finding has no local fix, medium if any breaks, low if
there are findings, none if there are none.

Order groups WORST FIRST — most impacts, then by name. On a real repository
this list is hundreds of tables long, and alphabetical order means the first
thing somebody reads is decided by the alphabet rather than by how much of it
is broken.

THE HONEST HALF. After the walk, for every file the word search matched:
  If the name is inside an opaque statement, or appears as a QUOTED STRING
  inside any statement, report it under "check by hand" with the file, the
  line and the line itself. Real pipeline code reads
    substr(decrypt_sde(get_sde_tag('cm13','triumph_demographics'), cm13),1,11)
  and both cm13s break when cm13 is renamed. Ripple reports the second,
  because it is a column. The first is a quoted string and no parser can see
  it as anything but text. Report it EVEN IN A FILE THAT ALREADY HAS
  FINDINGS, and say so explicitly — fixing the findings does not fix that
  one, the text still says the old name.
  Count how many LINES of the file name it as text, not merely whether any
  does. A real file sets one tag per column and runs to sixty of them, and a
  report naming one line sends somebody to fix one line out of sixty.
  Otherwise, if the file could not be parsed, say "mentions the name, but
  Ripple could not read it as SQL — check by hand".
  Otherwise it goes in mentionsOnly: the name appears but carries nowhere,
  which is the reassuring case and must be told apart from the others.

Per attribute, report: found, files, mentionedIn (how many files write the
name down at all — zero here is the answer to "why did it find nothing?"),
reachesProduction, endsAt, uncertain (findings where the table was inferred),
and how widely the name is used as a name (in how many of the tables Ripple
could read). A scan for a column half the warehouse shares looks identical on
screen to a scan for one only this table has, and they are not remotely the
same answer.

Also produce graphs[] for the dependency picture: per attribute, the branches
that reach a published table and the branches that end elsewhere, each a list
of {name, kind, alias, prod}. Drop any branch that is only the start of a
longer one already listed.

Tests: a chain through two renames reaches the published table; a column
leaving under two names does not lose the chain; findings are reported even
when NOTHING matches the published rule, and the risk is not "none";
correcting the rule turns them into production tables; a genuinely clean
result is still clean; a name inside a quoted string is reported even in a
file that has findings, with a count of lines; groups come back worst first.
````

**Check it worked:** `python -m pytest tests/test_lineage.py -q`. The one test to insist
on: *findings are reported even when nothing matches the published rule*. If the
chat quietly returns an empty result there, it has rebuilt the exact bug this
tool exists to prevent.

---

# PHASE 6 — reading the notification email

**Saves to:** `ripple-build/ripple/notification.py`,
`ripple-build/tests/test_notification.py`

````text
[PASTE THE CONTRACT CARD FIRST]

Build ripple/notification.py and tests/test_notification.py.

read_upload(filename, raw_bytes) -> Notification
read_pasted(text) -> Notification
extract_by_rules(notification, catalog) -> dict

A Notification holds subject, body, from_name, from_email, attachments[],
source_kind. Read three shapes:
  .eml   with the standard library email package, walking multipart, taking
         text/plain in preference to text/html, decoding whatever charset is
         declared and falling back rather than raising
  .msg   Outlook's compound file format. Do it without a third-party package:
         read the streams and pull out subject, body and sender. If the
         format defeats you, fall back to scraping readable text out of the
         bytes and SAY on screen that it was read roughly — never silently
         return an empty email.
  plain text, pasted or uploaded

extract_by_rules matches the text against the repository catalogue built in
Phase 5, so what comes out is names that actually exist in the code rather
than a guess. Return: source, changeType, changeKind (one of unknown,
removal, value_change, type_change, rename), changeDesc, subject,
effectiveDate (ISO), pocName, pocEmail, pocTeam, upstream[{table, attrs}],
warnings[], extractedBy: "rules".

Rules worth having: a table name in the text that IS in the catalogue is an
upstream table; a column name that belongs to one of those tables is one of
its attributes; a date in any common written form becomes ISO; words like
"decommission", "retire", "format change", "rename" pick the change kind.

BE HONEST. Any table named in the notification that is NOT in the connected
repository must come back as a warning: "Not found in the connected
repository: X. Scanning will still run, but expect no results for those."
Nothing is scanned until the person has confirmed the fields, so what is
extracted is a suggestion, never an answer.

Also provide an email-address extractor that pulls every address out of a
blob of text, once each, lower-cased. People do not type addresses one at a
time into a form; they paste an Outlook To line — "Priya Raman
<priya@corp.example.com>; Marcus Hale <marcus@corp.example.com>".

Tests with invented names and a fabricated .eml built in the test.
````

**Check it worked:** `python -m pytest tests/test_notification.py -q`, then feed it a real
notification you have and print what came out.

---

# PHASE 7 — writing the summary and the reply

**Saves to:** `ripple-build/ripple/narrative.py`,
`ripple-build/tests/test_narrative.py`

````text
[PASTE THE CONTRACT CARD FIRST]

Build ripple/narrative.py and tests/test_narrative.py.

summarise(scan, vals) -> {headline, narrative, bullets[], actions[],
                          writtenBy: "rules"}
draft_reply(scan, vals, summary) -> {subject, body, writtenBy: "rules"}

This is what runs when there is no AI, when a key stops working, or when
somebody decides no data may leave the network. It must be worth reading on
its own.

THE HEADLINE IS QUOTED IN MEETINGS AND THE REPLY IS SENT TO ANOTHER TEAM, so
neither may claim more than was read. Work out first how much of the
repository the answer does NOT cover: files never opened plus files that could
not be followed.

  nothing scanned at all
     -> "Nothing was scanned — there was no code to search", and a reply that
        says no answer is possible yet. Never "no impact": that is a statement
        about an empty folder wearing the clothes of a statement about a
        pipeline.
  no findings, but some files uncovered
     -> "No usage found in the N files that could be read — M others could
        not be", and a reply that says the assessment is still being
        confirmed. NEVER "no impact, proceed as planned".
  no findings, everything read
     -> "No impact — nothing in this repository consumes the attribute", and
        the confident reply. This is the only case that earns it.
  findings, and a usage with no local fix
     -> "Ranking logic has no replacement — escalate before the date"
  findings that break, and some files uncovered
     -> "N production tables at risk, and M files Ripple could not follow".
        Never "all fixable in code": the fix that has no substitute may well
        be inside one of the files nobody could follow.
  findings that break, everything read
     -> "N production tables at risk, all fixable in code"
  findings, none breaking
     -> "Labels change, but nothing breaks"

There is a further case: findings exist but NONE of them reach a table on the
published list. That is either a genuinely internal chain or a published-table
rule that does not match this repository, and only a person can tell which. So
say exactly that — "not a clean result, an unfinished one" — and the drafted
reply must say the assessment is in progress. It must never say "no impact"
while the analysis behind it is holding a list of usages.

Cap every list of table names at six or ten with "and N more". On a real
repository one key column reaches hundreds of tables, and joining them all
into a sentence produces a paragraph nobody reads, in the one place on the
screen written to be read.

Bullets and actions come from the real findings, most consequential first,
and always include the caveats: files that could not be opened go FIRST and
worded hardest, because every other number on the page is a number about the
files that WERE opened.

Tests, and these are the ones that matter:
  the summary never says "no impact" over a list of findings
  no impact is never claimed over files that could not be read — check the
    headline AND the reply body, and that "proceed as planned" is absent
  nothing scanned is never reported as no impact
  a genuinely clean result still says no impact, in both
````

**Check it worked:** `python -m pytest tests/test_narrative.py -q`. Read the four drafted
replies out loud. If any of them would embarrass you when forwarded, say so in
the same chat and have it rewritten.

---

# PHASE 8 — progress, saved history, and the web service

**Saves to:** `ripple-build/ripple/progress.py`, `ripple-build/ripple/store.py`,
`ripple-build/ripple/api.py`, and `ripple-build/run.py` at the project root

````text
[PASTE THE CONTRACT CARD FIRST]

Build ripple/progress.py, ripple/store.py and ripple/api.py.

--- ripple/progress.py

A tiny module holding what the engine is doing this second, so the page can
ask while it waits: {job, label, done, total}. reader(job) returns a callback
the scanners already expect: on_progress(done, total, label). finish() clears
it. snapshot() returns the current state.

Reading a real repository takes minutes and a scan about a minute. A spinner
and a fixed sentence for that long is indistinguishable from a program that
has hung. Show only what has actually been counted — files really read,
statements really followed. Where there is genuinely no total, because a chain
looks at as many statements as it turns out to need, report the count and NO
fraction. A fraction would need a denominator nobody knows.

--- ripple/store.py

SQLite. save(vals, scan, summary, mode, settings) -> {saved, id, reason};
listing(settings); get(id, settings); set_status(id, status, settings).
Statuses: New, In progress, Verified, Closed. Create the table on first use.
If the database cannot be written, return saved=False with a reason a person
can act on, and never crash — the screen has to be able to say "history is
not available here" rather than showing a saved analysis that was not saved.

--- ripple/api.py

FastAPI, thin on purpose: every route is a few lines calling the modules
above. Build the index once and keep it until re-read.

GET  /api/health      the shape in the contract card: repo counts including
                      heldOnline, pathTooLong, inSkippedDirs, skippedDirNames,
                      unreadable, statements, kinds[]; catalog counts;
                      sqlDialect; maxHops; production (the one-line form);
                      productionRule (the full parsed rule); limits
GET  /api/progress    progress.snapshot()
GET  /api/catalog
POST /api/reindex
GET  /api/production            the list in force, checked against the repo
POST /api/production/read       read a pasted list WITHOUT saving it, and
                                return what was made of it plus the check —
                                this is what the settings box calls as it is
                                typed into
POST /api/production            use this list from now on
POST /api/read-email  (file upload)   POST /api/read-text  (pasted)
POST /api/scan        {upstream[], changeKind} -> the scan result JSON
POST /api/summary     {scan, vals} -> {summary, reply}
POST /api/history     GET /api/history     GET /api/history/{id}
PATCH /api/history/{id}  {status}
GET  /api/file?path=  the real text of a scanned file

Refuse an upload over max_upload_bytes with a message saying what the real
ceiling is and why, not a bare 413.

Serve web/ at /static and web/index.html at /. Send Cache-Control: no-store
for the page and the script — during a demo or an edit, a cached script is
the difference between seeing a change and staring at yesterday's page. Cache
the fonts, if any, for a month.

Also write run.py at the project root: print the repository, the dialect and
the address, then start uvicorn on port 8000, with a --no-browser flag.
````

**Check it worked:**

```bash
python run.py --no-browser
```

Then in another terminal, `curl http://127.0.0.1:8000/api/health` should return
JSON with real counts in it.

---

# PHASE 9 — the page and its styles

**Saves to:** `ripple-build/web/index.html`, `ripple-build/web/styles.css`

````text
[PASTE THE CONTRACT CARD FIRST]

Build web/index.html and web/styles.css. No framework, no CDN, no build step.

LAYOUT
A fixed dark navy sidebar 288px wide: the product name, a numbered list of the
seven steps (Notification, Review fields, Repository, Impact analysis,
Dependency map, Summary, Reply), then Past analyses and Settings & checks,
then a status block pinned to the bottom showing the repository, whether the
SQL dialect is set, and a coloured dot for each.
To the right: a white header strip with the current step and a slot for a
progress line, then a scrolling area with a 1200px-wide content column.

The seven steps live in <template> elements — t-step1 to t-step7 — each
holding the static skeleton for that step with data-x="..." hooks the script
fills in. Keep the templates dumb: no text that changes, only the frame.

STYLE
A restrained corporate palette, defined as CSS variables at the top:
navy #00175A, blue #006FCF, a light background #F2F5F9, white cards with a
1px #DCE4EE border, 12px radius and a barely-there shadow. Status colours for
red, amber, green and violet, each with a background, a border and a text
tone. A monospace family for table and column names.

Components to define, because the script uses these class names:
  .card .pad .pad.lg .clip .chead      cards and their tinted header strip
  .grid2 .grid2.even .rail             two-column layouts
  .lbl .small .muted .faint .prose     type scale
  button.pri .ghost .sm .link .danger  buttons
  .pill .pill.on .pill.tab             the mode and source toggles
  .badge with .blue .red .amber .green .grey .violet, and .badge.sm
  .tag                                  the small upper-case row label
  .chip .chip.mono .chip.alias .chip.pattern .chips .scrollbox
  .note with .info .warn .good .bad     the four kinds of on-screen note
  .statgroups .stats .stats.five .stats.three .stat  the counted cards
  .groups .group .ghead .rowhead .row .detail        the findings list
  .code .code .f .code .body .code .ln .ln.hit .why  the code snippet
  .maprow .mapsrc .branches .branch .node .arrow .legend   the map
  .factrow .drop .foot .spin .big .hist

Three rules that keep it usable with real data:
  A real table name runs to forty characters and a real path to a hundred and
  sixty. Give every grid cell min-width:0 and overflow-wrap:anywhere, or one
  long name widens the grid until the page scrolls sideways and the findings
  walk off the right of the screen.
  .scrollbox is a chip container with a max height and its own scrollbar, for
  the lists that are genuinely hundreds long.
  The stat cards come in two fixed rows — five columns and three columns —
  not one row that wraps. One row wrapped six-and-one as soon as a seventh
  card appeared, which stranded the honesty numbers on a line of their own
  looking like an afterthought.
````

**Check it worked:** open the page. The sidebar and header should be there and the
content area empty. Nothing else works yet.

---

# PHASE 10 — the screens: notification, review, repository

**Saves to:** `ripple-build/web/app.js` — this window creates the file. Window 11
adds to the **end of the same file**, so do not close it off or start a second one.

````text
[PASTE THE CONTRACT CARD FIRST]

Build the first part of web/app.js — plain JavaScript, no framework, no build
step. I will paste Phase 11 underneath it, so end this part cleanly and do
not write a closing boot block yet.

STRUCTURE
A single state object S: {step, maxStep, view, mode, health, vals,
emailPreview, scan, summary, reply, savedId, manRows, man, busy, busyWhat,
openGroup, openRow, graphTab, prod}. A render() that clears the view, clones
the template for the current step and calls the function for it. Small
helpers: $, $$, el(tag, props, ...children), x(root, name) for the data-x
hooks, api(path, opts) that throws with the server's own message.

run(fn, what) wraps everything slow: sets busy, renders, starts a poll of
/api/progress twice a second, and re-renders only when the progress line
changes. Show the counted line if there is one and the fixed sentence until
there is. Never animate anything that is not really happening.

STEP 1 — the notification.
Two modes on a toggle: from email, or entered by hand.
Email mode: a drop zone that also opens a file picker, and a paste box.
Check the file size in the browser as well as on the server, and say what the
real ceiling is. Nothing is scanned until the person confirms — say so on
screen.
Manual mode: rows of upstream table + comma-separated attributes, add and
remove; and a details panel with source system, change type (a select with
the five kinds the scan actually understands), effective date (a real date
picker, plus the date written out in words underneath so a slip is visible),
what is changing, contact name, contact email, contact team.
The contact email box takes ANY number of addresses: it pulls every address
out of whatever is pasted — including a whole Outlook To line — and shows
them back as separate chips, so what was understood is obvious. It must
update itself without re-rendering the page, or the cursor jumps out of the
box on every keystroke.
Manual mode goes STRAIGHT to step 3. Being shown "check what Ripple read"
after typing it yourself is being asked to check your own typing, so the
review step is not in the wizard at all in that mode — not greyed out, not
silently skipped while the count still says 7.

STEP 2 — what Ripple read.
Warnings first. Four editable cards: source system, change type, effective
date (with a badge saying how many days are left, amber inside three weeks),
and contact with the multi-address box. Subject and description. Then the
upstream tables and attributes, editable, with a live count. Say plainly
whether the fields were found by matching the catalogue or typed by hand, and
that the scan uses exactly what is on this screen, not the email.

STEP 3 — the repository.
Left: what is connected — the folder, the label, files indexed, statements
understood, and, ONLY when they are not zero, files never opened, files that
would not parse, and files in folders Ripple skips. "Files indexed 1,770" is
the number somebody reads to decide the whole folder was covered, so when it
was not, the rows saying otherwise sit directly underneath it.
Right: what kinds of file are in the index, counted; a confirmation note with
the branch and the file count; the never-opened note if there is one, saying
the number, why, and the one thing that fixes it; the skipped-folders note if
there is one; and the catalogue counts, which arrive from a separate request —
while waiting, say what it is waiting for rather than leaving a heading with
nothing under it.
A "Run impact analysis" button, disabled when nothing is indexed, and a
"Re-read the repository" button. The hint beside them says what the scan WILL
do, in the future tense — "The scan will search X" — never something that
reads as though it is already happening.
While reading, show the counted progress line: reading takes minutes on a real
repository, and saying "a few seconds" and then taking four minutes is how a
working program gets reported as hung.
````

**Check it worked:** the wizard should walk from step 1 to step 3 and show real
counts from your folder. The scan button will not do anything yet.

---

# PHASE 11 — the screens: findings, map, summary, reply, settings

**Saves to:** the end of `ripple-build/web/app.js` — **append** it to what window
10 gave you, in the same file. Do not replace it and do not make a second script.

````text
[PASTE THE CONTRACT CARD FIRST]

Build the rest of web/app.js. It is appended to the part I already have, which
defines S, render(), el(), x(), api(), run(), and steps 1 to 3. End with the
boot block that fetches /api/health and renders.

STEP 4 — the findings. Order the page by importance, with a small heading
above each section.
  A card with what was read: the repository, and "N files read · M mention the
  names you confirmed". Real counts only.
  Under the heading "What the change reaches", five counted cards:
  production tables at risk, other tables reached, attributes impacted, files
  to change, breaking usages.
  Under the heading "What this result does not cover", up to three: to check
  by hand, never opened, in folders Ripple skips — the last two only when they
  are not zero. When all are zero, say so positively in the space beside them.
  Then, BEFORE the findings, the never-opened card if there is one. It is the
  card that decides whether every number above it can be believed, and the
  bottom of a long page is where a caveat goes to be missed.
  Then the findings: one expanding card per published table, then the tables
  the chain ends at, then usages that build no table. Each card lists rows —
  table it lands in, attribute impacted, alias used, what the code does,
  value — expanding to a plain-English impact sentence and the real lines of
  code with the matching line marked and the reason on the line itself.
  Where a row's column is no longer what the person asked about, say "from
  MARKET_CODE" underneath it.
  Draw at most 20 cards. On a real repository a key column reaches over two
  hundred tables, and two hundred collapsed cards is a page nobody scrolls to
  the end of, so the tables at the bottom are in practice hidden. Nothing is
  dropped: they are sorted worst first, and every remaining table is named
  with its count in a scrollable list underneath, saying so.
  When nothing matched the published-table rule at all, say it in a warning
  above the list, quote the rule, and point at the settings screen.
  A green tick is ONLY shown when there is genuinely nothing — no production
  table, no other table, no loose usage anywhere. If no files were read at
  all, show a red note saying nothing was scanned, and never the tick.
  Under "How to check this result": every attribute asked about and what came
  back — used in N files, or named in N files and never read from, or this
  name is not in the repository at all. Then the check-by-hand list, giving
  the file, the reason, the LINE and the line itself, so somebody can open it
  at the right place. Where the same advice applies to more than one file, say
  it once at the top rather than under every entry — printed sixty-eight times
  it stops being advice and becomes wallpaper the eye skips, taking the file
  names with it. Then the files that mention the name but carry it nowhere.

STEP 5 — the dependency map. A tab per attribute. The upstream source as a
dark card on the left, and the branches to its right, each a row of boxes
joined by arrows, with the alias shown at each step, published tables in red.
Draw at most 40 branches, longest and production-reaching first, and COUNT
THE REST OUT LOUD — every one of them is already a finding on the previous
step. A legend, and one line saying the alias is the rename a word search
would miss. The line under the title must be true of the picture underneath
it: if no branch reaches a published table, say so there.

STEP 6 — the summary. The headline with a risk badge, the narrative, the
bullets, and the change details. A right-hand rail with the deadline and days
left, a blast-radius count, and what to do. Then the check-by-hand list again,
because this is the screen people read. A save button, and when saved, say so
with the number it was saved as.

STEP 7 — the reply. Editable subject and body. The recipients as separate
chips, one per address, so a list of four is not one unreadable string hiding
a typo. Copy takes the recipients with it — copying a reply and then having to
gather the addresses again by hand is half a job. Nothing on this screen sends
anything, and nothing pretends to.

PAST ANALYSES — a table of what was saved, newest first, with an editable
status.

SETTINGS — and the published-tables control is the whole point of it.
Build it as one function used by the whole app:
  a big multi-line box, monospace, resizable, holding the list exactly as it
  was pasted — a single-line input is the wrong control for two hundred names
  as it is checked, with a 600ms pause, by POSTing to /api/production/read.
  Never re-render the page on the answer, or the cursor leaves the box.
  Underneath, in this order:
    how many table names and how many patterns were read, then every entry as
    a chip in a scrollable box, with patterns outlined differently and one
    line saying which is which
    what was left out of the paste and why, with examples
    then the important one, in red: "N of the M tables on this list are not in
    this repository", with the reason it matters — either the name is spelled
    differently here, or the table is built somewhere Ripple could not read,
    and until that is settled a clean result for those tables means nothing.
    Group them: not written anywhere in this repository, and the name is here
    but nothing readable builds it. Two different places to go and look.
    If a name matches nothing but IS the ending of tables that exist, ask
    whether it was meant as a pattern and show how to write it. Do not decide.
    Then, for each pattern, how many tables here it matches — and a warning
    when a pattern matches none, because it is doing nothing at all.
  A save button, and a line saying plainly where the list is kept and whether
  it survives a restart.
The rest of the settings screen: what is connected, and a note explaining that
this one setting decides whether "no production table is impacted" is a result
or an accident.
````

**Check it worked:** run a scan against a real folder and click through all seven
steps. Then paste a deliberately messy list into the settings box — with a typo
in it — and confirm the typo comes back named.

---

# PHASE 12 — starting it up, and the checklist

Nothing to prompt here. This is you, checking.

**Make a tiny fake pipeline to test against.** Ask any window for it:

````text
[PASTE THE CONTRACT CARD FIRST]

Write me the contents of ripple-build/mockrepo/ : a small fake pipeline, 20-25
files, using only invented table and column names. It must contain, on
purpose:
  a source table definition and a couple of tables built from it
  a column renamed twice down a chain, ending at a table called
    something_prod so the default published rule matches it
  a chain ending at a table that does NOT match the published rule
  a join on a column of the same name in two different tables
  a window ORDER BY on the column, so there is a ranking with no local fix
  a filter comparing the column to a literal
  a Python job holding SQL in a triple-quoted string
  a Python job that names a .sql file which does NOT exist in the folder
  a file with a deliberate syntax error
  a file where the column name appears only as a quoted string in a call
  a BigQuery-shaped file wrapped in BEGIN ... EXCEPTION ... RAISE ... END
  a CREATE TABLE built with SELECT *
Give me every file complete, and end with the SAVE THESE FILES block giving
the full path of each one under ripple-build/mockrepo/.
````

**Then run it:**

```bash
python run.py --no-browser
```

**The checklist. Each line is one thing to look at on screen.**

1. The repository screen shows a real file count, and if any file was never
   opened or would not parse, a row underneath saying so.
2. A scan of the renamed column reaches the published table three hops away.
3. The chain that ends somewhere not on the published list is still listed,
   under its own heading, with the rule quoted beside it.
4. The file with the syntax error is on the check-by-hand list, with its line
   number and the line itself.
5. The file where the name is only a quoted string is on that list too, and
   says how many lines of it do that.
6. The Python job naming a missing .sql file is reported as a query Ripple has
   never read.
7. Scan for a column that does not exist: the result says "this name is not in
   the repository at all", and the drafted reply says no impact **only** if
   nothing was left unread.
8. Point it at an empty folder and scan: the badge says nothing was scanned,
   and there is no green tick anywhere.
9. Paste a list of published tables with one deliberate typo: the typo comes
   back named as not in the repository.
10. Paste a two-column list copied out of a spreadsheet: it says which column
    it took and what it ignored.
11. Make every table name in the fake pipeline forty characters long: the page
    does not scroll sideways.
12. Save an analysis, reopen Past analyses, and change its status.

If 3, 5, 7, 8 or 9 fails, the honesty half has not been built and the tool will
give you a confident wrong answer on your real code. Those are the ones to go
back and insist on.

---

## When a window goes wrong

**It gives you a shorter, "simpler" version.** Reply: *"That drops the case where
X. Put it back and keep everything in the contract card."* Chats optimise for a
tidy answer; the messy cases are the product.

**It invents a name that does not match the contract.** Reply with the exact line
from the contract card. Do not accept "this is equivalent" — window 9 will not
know.

**It truncates.** Ask for the file in labelled parts, and ask it to tell you the
total line count first so you know when you have all of it.

**It writes a progress bar, a percentage, or a fake count.** Reply: *"Every number
on screen must be something that was actually counted. Where there is no total,
show the count and no fraction."*

**It quietly drops what it could not parse.** This is the big one, and it will do
it, because dropping things makes the demo look better. Reply: *"Anything the
reader could not follow is listed on screen with the file and the line, never
dropped."*
