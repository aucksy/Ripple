# Building Ripple, one chat window at a time

**What this is.** A kit for building a working piece of software using nothing but
a chat assistant — Copilot chat on your own laptop — and about two evenings. You
do not need to know how to code. The chat writes the code; you save it into files
and type one command to check it worked. This document is every prompt you will
paste, in order, and every command you will type, in order.

**What Ripple does.** An upstream data team sends an email: *"we are changing
MARKET_CODE in CUSTOMER_DEMOGRAPHICS on 18 September."* Somebody then has to
answer: what does that break on our side, where, and what do we tell them. Today
that means searching the code for the word MARKET_CODE — and that search is close
to useless, because a column almost never keeps its name as it travels through a
pipeline. MARKET_CODE becomes `mc`, then `mkt_cd`. The search comes back empty
while the change quietly breaks three published tables. Ripple reads the SQL
properly, follows the renames from one table to the next, and reports what actually
breaks, in which file, on which line.

**Why twelve chat windows and not one.** A chat can hold only so much at once, and
Ripple is about six thousand lines. So it is built one file at a time, twelve
windows, each producing one or two finished files. The catch is that every window
is a stranger: it cannot see the other eleven and has no memory of them. That is
the whole difficulty of this approach, and the contract card further down is the
answer to it — the same page of rules pasted at the top of every window, so that
all twelve build the same product.

---

## What the chat can and cannot do

It cannot see your screen, your files or your folders. It cannot run anything, test
anything, or check whether what it just wrote works. It does not remember the other
windows. Everything it knows is what you paste into it.

So your side of the job is small and mechanical, and it is the same four moves
every time: **paste the contract card, paste the phase prompt, save the files it
gives you, run one command to check.** Nothing in this kit is harder than that.

---

## What you are actually running

Somebody will ask, and it is a fair question. Ripple has screens, so something has
to put them in front of your browser. The plain answer is that this is not a server
in the sense the word usually carries: nothing is hosted, nothing is published, and
nothing is reachable by anybody else.

- **It listens only to the laptop it is running on.** The address is 127.0.0.1,
  which is the machine talking to itself, and it is not reachable from the office
  network. A colleague who typed your machine name and the port would find nothing,
  because there is nothing there to find.
- **It runs only while the window is open.** Close the Command Prompt and it is
  gone. Nothing is installed as a Windows service and nothing starts at boot.
- **Nothing leaves the machine.** Ripple reads a folder of code you already have
  access to, works the answer out on your laptop, and shows it in your browser.
  Nothing is sent anywhere.
- **This is the ordinary shape of a desktop tool that has screens.** A Jupyter
  notebook works exactly this way. The browser is being used as the window, and
  that is the whole of it.

Two things worth saying out loud rather than being asked later: it reads the source
code of whatever repository you point it at, and it keeps one small file on your
laptop holding the analyses you chose to save. Both of those stay on the machine.

---

## Before you start — getting the machine ready

A one-off, about twenty minutes. Five steps, in order.

**Step 1 — open a Command Prompt.** Press the Windows key, type `cmd`, press
Enter. A black window opens. Everything in this kit that looks like a command gets
typed into that window, followed by Enter.

**Step 2 — check Python is there.**

```
python --version
```

It should print something like `Python 3.10.4`. Ripple needs 3.10 or newer.

- **"python is not recognized..."** — Python is installed but Windows was never
  told where it lives. Use the full path instead, quotes and all, everywhere this
  kit says `python`: `"C:\Program Files\Python310\python.exe"`
- **Nothing at all, or "not found"** — Python is not installed. That is a request
  to whoever manages your laptop.

**Step 3 — check pip.** pip is the thing that fetches ready-made pieces of code, so
that nobody has to write them again.

```
python -m pip --version
```

Three things go wrong here on a managed laptop. Every one of them looks like a
locked door and none of them is:

- **"pip is not recognized as an internal or external command."** Nothing is
  blocked. Typing `pip` on its own makes Windows hunt for a file it was never told
  about. Type `python -m pip` instead — always, everywhere — and it works.
- **"No module named pip."** Python was installed without it. Python carries a
  spare copy inside itself, needing no internet and no admin rights:
  `python -m ensurepip --upgrade --user`
- **It hangs, then times out reaching pypi.org.** The public package site is
  blocked. Almost every large firm runs its own internal copy instead. Ask whoever
  sits near you *"how do you pip install here?"*, then point pip at their address
  once and forget about it:
  `python -m pip config set global.index-url <their address>`

**Step 4 — install the pieces Ripple needs.** One command. It is long; copy the
whole line.

```
python -m pip install --user sqlglot==30.17.0 fastapi==0.115.0 uvicorn==0.30.6 pydantic==2.13.4 typing-inspection==0.4.2 python-multipart==0.0.9 extract-msg==0.48.7 httpx==0.27.2 pytest==8.3.3
```

What each one is for, so nothing on that line is a mystery:

| Piece | What it does |
|---|---|
| `sqlglot` | **Reads SQL properly.** The one piece that cannot be replaced, and the one a chat cannot write for you. It is what makes Ripple more than a word search. |
| `fastapi`, `uvicorn` | Serve the screens to your browser |
| `pydantic`, `typing-inspection` | Come along with FastAPI. Pinned here so they cannot drift |
| `python-multipart` | Lets you upload the notification email. Leave it out and that screen fails the moment the app starts |
| `extract-msg` | Opens Outlook `.msg` files, which is how most notifications actually arrive |
| `httpx` | Only used if you later switch on the optional AI reader. Safe to leave out |
| `pytest` | Runs the check at the end of each phase |

The versions are pinned on purpose. Left unpinned, the install takes whatever was
published this morning, and these phase prompts are written against how these
particular versions behave.

**If one package alone is refused with a 403** while everything around it downloads
perfectly, the mirror is not broken. A company mirror routinely holds back a
version published in the last few days, because nothing has scanned it for security
yet. Pin that one package a few versions back and run the whole command again:
whatever asked for it almost always wants a minimum version rather than an exact
one, so an older release satisfies it just as well. A refusal is not a partial
install either — pip downloads everything before it installs anything, so one
refusal near the end means nothing was installed, however much of it you watched
come down.

**Step 5 — check they all arrived.**

```
python -c "import sqlglot,fastapi,uvicorn,pydantic,multipart,extract_msg,httpx,pytest;print('all set - sqlglot',sqlglot.__version__)"
```

You want `all set - sqlglot 30.17.0`. If instead it names one thing it could not
find, install that one on its own and run this again.

---

## Making the folders

One command builds every folder. It does not matter which folder you are standing
in when you run it, because every path is written out in full.

```
mkdir C:\ripple-build\ripple\scanner C:\ripple-build\web C:\ripple-build\tests C:\ripple-build\mockrepo
```

Then two empty files. They look pointless and they are not: Python refuses to find
your code without them.

```
type nul > C:\ripple-build\ripple\__init__.py
```

```
type nul > C:\ripple-build\ripple\scanner\__init__.py
```

From here on, every command in this kit is run from that folder, so start by going
there. The `/d` matters if your Command Prompt opened on a different drive:

```
cd /d C:\ripple-build
```

**Why `C:\ripple-build` rather than Documents or Desktop.** Those two are usually
synced to OneDrive on a work laptop, and OneDrive leaves files listed on disk while
their contents are still up in the cloud. Ripple has an entire rule about detecting
that in *other* people's folders, because it makes a half-read repository look like
a clean result — you do not want your own project living in it. A short path also
keeps you clear of Windows' 260-character limit once the folders get deep.

**One note on how paths are written from here on.** The phases below say
`ripple-build/ripple/config.py` with forward slashes. That means exactly the same
place as `C:\ripple-build\ripple\config.py` — the folder you just made. The kit
writes it the short way because that is the form the chat should use, and Windows
accepts either.

This is what you are building towards. Every phase says exactly which of these
files it produces:

```
C:\ripple-build\
  run.py                   <- the one you type to start Ripple
  ripple\
    __init__.py            <- empty, but it must exist
    config.py  production.py  catalog.py  notification.py
    narrative.py  progress.py  store.py  api.py
    scanner\
      __init__.py          <- empty, but it must exist
      repo.py  templating.py  sqlread.py  lineage.py
  web\
    index.html  styles.css  app.js
  tests\
    test_production.py  test_repo.py  test_templating.py
    test_sqlread.py  test_lineage.py  test_notification.py
    test_narrative.py
  mockrepo\                <- a small fake pipeline to test against (Phase 12)
```

---

## Saving a file the chat gives you

This is the step that trips people up, and there is a trick that makes it
foolproof.

**The problem.** Notepad quietly adds `.txt` to whatever you name a file. You save
`config.py` and you actually get `config.py.txt`, which Python cannot see. Nothing
warns you. The next command fails and it looks like broken code.

**The trick: create the empty file from the command line first, then open that file
and paste into it.** The name is then already correct and Notepad cannot change it.
Two commands per file — this is the pattern for every file in the kit:

```
type nul > C:\ripple-build\ripple\config.py
```

```
notepad C:\ripple-build\ripple\config.py
```

Notepad opens, empty. Go to the chat and **use the copy button at the top of the
code block** rather than selecting it with the mouse — dragging across a long block
loses the last line more often than you would believe, and a Python file missing
its last line fails in a way that reads as the chat's fault. Paste, press Ctrl+S,
close the window. That is one file done.

**Two things not to do.** Never retype code by hand, and never tidy up the
indentation. In Python the spacing at the start of a line is not decoration — it is
what tells the language which lines belong inside which. Paste it exactly as given.

---

## Checking that a phase worked

Every phase ends with one command, run from `C:\ripple-build`. You are reading it
for one word.

```
python -m pytest tests/test_production.py -q
```

- A row of dots and then **`passed`** — green. Move on to the next phase.
- **`failed`** or **`error`** — copy the whole red block and paste it straight back
  into the same chat window with *"this is what happened when I ran it"*. That
  window still has everything it wrote in front of it and will usually fix it in
  one go. Never start a fresh window for a failure; a fresh one knows nothing.
- **`no tests ran`** — the file is not where the command is looking. Almost always
  the `.txt` problem above, or the file went into the wrong folder.

---

## The two ways this goes wrong

**Drift.** Window 6 invents its own names for what window 4 already built, and
nothing fits together. The fix is the contract card: paste it at the top of *every*
window, every time, before the phase prompt. It is the shared memory the chats do
not have.

**Confident wrong answers.** A chat asked to build "a SQL impact analyser" will
build one that gives a clean green result whenever it fails to understand
something, because that is the obvious thing to build and it looks better in a
demo. A tool that reports "no impact" when what it means is "I could not read half
of this" is worse than no tool at all, because somebody will act on it. The rules
that stop it are in the contract card under **THE ONE RULE**. Do not trim them to
save space. They are the product.

---

## The build order

Two evenings if it goes well. Phases 4, 5 and 8 are the hard ones. If you get only
as far as Phase 5, you already have the part that no other tool does.

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
| 13 | Packaging it as a program you can hand to somebody | 250 lines |

**One thing to test before you invest an evening.** Two of these files are 800
lines long. Paste Phase 1 into a window and see whether you get complete files back
or something that trails off into "... rest of the implementation". If it
truncates, ask for the file in clearly labelled parts and paste them together — and
ask it to tell you the total line count first, so you know when you have all of it.

Every phase says where its files go, and the contract card makes the chat repeat it
back to you at the end of every reply. **If a reply does not end with a SAVE THESE
FILES block, ask for one before you save anything.** One file in the wrong folder
makes the next window fail for a reason that looks like bad code.

---

# PHASE 0 — the contract card

Paste this first in every window. Then paste the phase prompt underneath it.

````text
You are helping me build a tool called Ripple, one file at a time, across
several separate chats. You cannot see the other chats, so this card is the
shared contract. Follow it exactly. Do not rename anything in it.

You also cannot see my files, run anything, or test anything. I am the only
one who finds out whether your code works, by saving it and running it, and
every round of that costs me real time. So never tell me something is tested,
verified or working -- say what you believe it does and what you are unsure
of. If you are guessing about how a library behaves, say which line you are
guessing about. A named doubt I can check in thirty seconds is worth far more
than confident prose.

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
sqlglot 30.17.0 for the SQL: write against how that version behaves.

READ THE PARSE TREE THROUGH ONE SMALL MODULE, NOT DIRECTLY. sqlglot renames the
keys inside its own nodes between major versions, and the renames that matter
are SILENT -- the old key just returns None, so the code carries on and finds
nothing. Measured on the upgrade from 25.24.0 to 30.17.0:

    Star.args["except"]        -> "except_"     SELECT * EXCEPT(col) stops
                                                being noticed, so a column
                                                dropped BY NAME is reported as
                                                carried through
    Merge.args["expressions"]  -> "whens"       every rename a MERGE makes
                                                disappears, and a MERGE is how
                                                a published table is loaded
    Select.args["from"]        -> "from_"       the check that decides which
                                                tables a SELECT * covers finds
                                                nothing
    exp.RenameTable            -> exp.AlterRename   (the only loud one)

Nothing raises. Every test goes on passing and the answers go quietly wrong.
Put those four reads behind functions in one file, and write tests that fail
LOUDLY when a key stops resolving -- against the real parser, because the gap
being guarded is exactly the one between what the code expects and what the
library returns.


The front end is plain HTML, CSS and JavaScript in three files — no build
step, no framework, no npm, no CDN, no TypeScript, no inline event handlers.
Tests with pytest.

FILE MAP (build order)
ripple/paths.py                where things live, running either way
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
  risk is one of: high, medium, low, unknown, none
  "none" is the only thing this tool sells, so it is the one word that must
  never cover a gap: see Phase 5.
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
    build.py                 (Phase 13 -- packaging)
    ripple/
      __init__.py            (empty file, but it must exist)
      paths.py  config.py  production.py  catalog.py  notification.py
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

BEFORE YOU ANSWER, CHECK YOUR OWN WORK
You are a capable model and you will be tempted to improve on this brief. The
trouble is that eleven other windows are building against it and none of them
can see what you decided. So before you reply:
- Re-read DATA SHAPES above and confirm every name that crosses a file
  boundary matches it exactly. If you genuinely needed one that is not there,
  invent it, but SAY SO in one line at the top so I can carry it to the other
  windows. A silent invention is the single most expensive thing that can
  happen here.
- Confirm every file is complete. No "...", no "rest unchanged", no TODO, no
  placeholder, no function body left as pass.
- Confirm you added nothing I did not ask for. No extra packages, no logging
  framework, no command-line options, no retry logic, no caching layer,
  no abstraction "for later". Cleverness in one window is a mismatch in the
  next.
- Confirm the tests would actually FAIL if the behaviour were missing. A test
  that passes against an empty function is worse than no test, because it
  makes a missing feature look finished.
- Confirm it runs on Python 3.10.
If something in the prompt genuinely contradicts this card, stop and ask me
instead of choosing. The question costs me a minute. A wrong guess costs me a
whole window.

WHAT I WANT BACK
Complete files, ready to save. No "...rest unchanged", no placeholders, no
TODOs, no function body left as pass.

Some of these files are 800 lines and may be longer than one reply can hold.
Before writing a long file, say how many lines you expect it to be. Then, if
it will not fit, give it in clearly labelled parts -- PART 1 OF 3 and so on --
each part ending at a sensible boundary rather than mid-function, and tell me
in what order to paste them. If a reply is cut off, do not restart the file
from the top when I ask you to continue: carry on from the last complete line
and tell me which line that was.

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

**Saves to:** `ripple-build/ripple/paths.py`, `ripple-build/ripple/config.py`,
`ripple-build/ripple/production.py`, `ripple-build/tests/test_production.py`

````text
[PASTE THE CONTRACT CARD FIRST]

Build ripple/paths.py, ripple/config.py, ripple/production.py and
tests/test_production.py.

--- ripple/paths.py

Small, and first, because everything else asks it where things are. Ripple has
to run two ways: as `python run.py` while it is being built, and later as a
packaged program with no folder of source files around it. Anything that
assumes the second case looks like the first fails silently, so the guessing is
done here, once.

  frozen()   -> bool   True when running as the packaged program. It is
                       getattr(sys, "frozen", False).
  app_dir()  -> Path   The folder a person actually sees. Packaged, the folder
                       holding the .exe: Path(sys.executable).resolve().parent.
                       From source, the project root.
  web_dir()  -> Path   Where the three front-end files are. Packaged,
                       Path(sys._MEIPASS) / "web", because the packager unpacks
                       bundled files to a folder of its own choosing and
                       _MEIPASS is where it says it put them. From source, the
                       web folder beside the code.
  data_dir() -> Path   Where the history database goes. app_dir() both ways;
                       create it if it is missing.

Nothing else in Ripple may work out a path for itself. Two rules follow, and
both exist because breaking them fails quietly rather than loudly:
  The front end is found with web_dir(), never by walking up from __file__.
  Packaged, that walk lands somewhere real but empty, so every route still
  answers and the browser shows a blank white page — which reads as broken
  code rather than as a folder that moved.
  The database is written under data_dir(), never beside the code. Packaged,
  beside-the-code is inside the program's own internals: rebuilding destroys
  every saved analysis, zipping the folder to send to somebody sends your
  saved analyses too, and a read-only location fails the save without saying
  so.

This file needs no test of its own; Phase 13 exercises it.

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
  db_path              defaults to paths.data_dir() / "ripple.db", never a
                       path worked out from this file's own location
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

**Check it worked.** From `C:\ripple-build`:

```
python -m pytest tests/test_production.py -q
```

You want `passed`. The test to insist on is the one where a messy paste — bullets,
a heading row, a line of ordinary prose — comes back with notes saying what was
ignored and why. If the chat only wrote tests for tidy lists, ask for the messy
ones. This file decides whether "no production table is impacted" is a real answer
or an accident.

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
in_skipped_dirs[], skipped_dir_names[], unknown_ext{}.

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

4. Files over max_file_bytes go in skipped[] with a plain-English reason.

5. HOW THE FILE WAS SAVED. Read the bytes and work the encoding out; do not
   just ask for UTF-8. Windows writes byte-order marks by default — Notepad,
   PowerShell's Out-File, Excel's CSV export, every Office "save as UTF-8" box
   — and a mark is invisible in every editor and lethal to a SQL parser. It
   lands on the FIRST statement of the file, which in a pipeline file is the
   one that names the source table, so the statement that matters is the one
   that is lost and the file still reports as read. Measured before this: the
   first statement failed, risk came back "none", and with two statements in
   the file the wording actively reassured — "1 of 2 statements in this file
   could not be read - the other 1 was".
     Check for a mark first: EF BB BF is utf-8-sig; FF FE 00 00 and
     00 00 FE FF are utf-32; FF FE and FE FF are utf-16.
     With no mark, look at the first 4 KB. Real text has no NUL bytes at all,
     so more than about a tenth of them being NUL means UTF-16 with no mark —
     PowerShell's ">" redirection has written UTF-16-LE by default for twenty
     years. Decide which way round from whether byte 2 is NUL.
     Then UTF-8, and latin-1 as the last fallback.
   If a NUL byte SURVIVES all that, do not index the file: put it in skipped[]
   saying it contains NUL bytes and is either not text or was saved in an
   encoding Ripple could not work out. A NUL left in the text makes the parser
   swallow the statement it sits in and say nothing — measured at
   couldNotRead 0, no warning of any kind, risk none.

6. SQL THAT IS NOT IN A .sql FILE, AND CONFIG THAT IS NOT SQL AT ALL.
   .yaml, .yml and .xml are on the read list, and handing one of them to a SQL
   parser whole can only ever fail. Two things went wrong at once:
     * An Airflow YAML holding "sql: |", an Oozie workflow.xml holding
       "<script>", and a shell script running "bq query <<EOF" each held the
       whole CREATE that builds a published table, and every one of them gave
       risk unknown and no lineage at all.
     * Every ordinary Kubernetes YAML in the repository landed on the "check by
       hand" list. Measured: twelve config files and one genuinely broken query
       gave couldNotRead 13, sorted alphabetically, with the real failure last.
       That list is the one place Ripple admits what it missed, and flooding it
       is how a real miss stops being seen.
   So: mine the SQL out (see statements_for below), and when nothing comes out
   of a markup file, say NOTHING about it — no statements, and no entry on the
   check-by-hand list. The guard on that silence is looks_like_unread_sql: a
   file with SELECT or CREATE written in it that yielded no block IS reported,
   because that is a query Ripple failed to mine rather than a config file.
   sql_file_refs also has to read markup, where the filename carries no quotes:
   "sql: queries/load_final.sql" is an ordinary Airflow shape and the
   quoted-string rule that covers .py files found nothing in it at all.

7. FILE TYPES YOU DO NOT OPEN. Count them. When a file is passed over because
   its extension is not on the read list, add one to unknown_ext[ext]. The walk
   used to have a bare "continue" with no counter, so a repository whose
   pipeline is written in .ipynb, .tf or .json files reported "indexed False,
   risk none, prod []" with NOTHING anywhere recording that a file had been
   passed over. The point is not to read them. It is that the NEXT unlisted
   extension is visible instead of silent.

Also in this file:

  search(names) -> Match[]        every line mentioning any of these names as
                                  a whole word, case-insensitive
  files_mentioning(names)
  get(path)
  extract_sql_blocks(f)           SQL inside triple-quoted and long single
                                  strings in .py .scala .java .sh files,
                                  returning (text, 0-based line offset) so a
                                  finding still points at a real line
  extract_markup_sql(f)           SQL taken out of a .yaml, .yml or .xml
                                  file, with the line each block starts on.
                                  YAML: a key whose name contains sql, query,
                                  script or statement, holding a block scalar
                                  (| or >) or a one-line value that really is a
                                  query. Take the block's own indent off, and
                                  measure from the KEY's column rather than the
                                  line's, so "- sql: |" works. XML: the text of
                                  an element whose tag contains script, query,
                                  sql, statement or command, plus any CDATA
                                  section, with the five XML escapes undone
                                  (&amp; last, or &amp;lt; decodes twice). If
                                  nothing comes out and the file's first line of
                                  code is a SQL keyword, treat the whole file as
                                  SQL.
  _heredoc_blocks(text)           SQL fed to a command through a shell heredoc:
                                  <<EOF, <<-EOF, <<'EOF', <<"EOF", ending at a
                                  line whose only content is the tag.
  statements_for(f)               extract_markup_sql for .yaml .yml .xml;
                                  extract_sql_blocks — plus heredocs, for .sh —
                                  for .py .scala .java .sh; the whole text for
                                  .sql, .sqlx, .ddl and .hql.
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

TWO MORE THINGS ABOUT MINING SQL OUT OF A FILE

  A quoted YAML value may run over several lines. Taking only the key's own line
  gave back "CREATE OR REPLACE TABLE final_published AS" with no SELECT -- half
  a statement, which parses, and was therefore counted as READ. When the value
  starts with a quote that does not close on that line, gather following lines
  until it does, and fold them into one. If the quote never closes, give back
  the first line only rather than swallowing the file.

  looks_like_unread_sql COUNTS, it does not ask "were there any blocks". An
  Airflow YAML, an Oozie workflow and a shell job normally hold several tasks of
  DIFFERENT kinds, and Ripple knows how to mine some of them. One recognised
  `sql:` block used to buy silence for the `bash_command:` beside it -- measured
  at couldNotRead 0 with the coverage card reporting no gaps, and deleting the
  recognised block from that same file put it straight back on the check-by-hand
  list. So: count the SQL-statement starts in the whole file, count them in what
  was mined, and report the file when the second number is smaller.

Write tests/test_repo.py with a tmp_path repository covering: extensions,
skip-dirs judged inside the repository only, skipped code files being counted
and named, a too-large file reported, SQL pulled out of a Python triple-quoted
string with the right line offset, a .sql reference found, a write target
found, and whole-word search not matching a substring.
````

**Check it worked.** From `C:\ripple-build`:

```
python -m pytest tests/test_repo.py -q
```

You want `passed`. You will point this at a real folder of your own in Phase 12,
where you can see the counts on screen rather than having to ask for them.

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

One placeholder must resolve to NOTHING AT ALL: a dbt directive. {{ config(
materialized='table') }} — and set, test, macro, endmacro, snapshot,
endsnapshot, do, print, log — are instructions to dbt, not values. Turned into
a bare identifier, a word lands where SQL expects a keyword and THE WHOLE FILE
stops parsing: not one table, not one column, nothing. Measured: adding a
config header to a readable dbt model took it from a full chain to 100%
unreadable, in every spelling tried. Every dbt model in the world opens with
one. Return an empty string for those, and make sure the "which words came out
of a hole" set skips the empties rather than collecting a blank name.

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

TWO WAYS THIS FILE USED TO DELETE THE ANSWER

Both measured, both silent, both producing a clean "no impact":

  IF (SELECT MAX(cm13) FROM customer_demographics) IS NOT NULL THEN
      The whole header line was replaced with an empty statement, and the query
      in the condition went with it -- so the file came back with risk none and
      every count zero. The identical guard written as ASSERT was read
      correctly, which is how this was found: where two spellings of one guard
      give opposite answers, the difference is the bug.
      Before dropping an IF, an ELSEIF or a WHILE header, look in it for the
      first balanced bracket group holding a SELECT. If there is one, replace
      the line with `SELECT * FROM <that group>;` instead of with `;`. It is a
      real read of a real table, building nothing -- which is exactly what an
      ASSERT already produces. Where there is no query in the condition, drop
      the line as before; keeping every IF would hand the parser scripting it
      cannot read.

  FOR rec IN (SELECT tbl FROM cfg_tables) DO SELECT 1; END FOR;
      A whole loop on ONE line. It matches "a loop header" and does not END with
      DO, so it was treated as a header written across several lines -- and the
      gather then looked for a line ending in DO, never found one, and returned
      "everything to the end of the file". Every line after it became an empty
      statement. No parse error, no unreadable entry, nothing on any screen: the
      trail stopped one table short and that was reported as where the chain
      ends. The same loop written across two lines gave the right answer.
      Match the one-line form first and rewrite it in place -- the bracket group
      becomes `SELECT * FROM (...)`, the body is kept, and the trailing
      `END FOR` goes. And when a gathered header never finishes, give up on THAT
      LINE, never on the rest of the file.

Tests: line numbers preserved through every substitution; a CASE written down
the page survives intact; a scripting END is dropped; a keyword inside a
string is not treated as scripting; BEGIN does not eat the statement after
it; a procedure body is kept; a loop header keeps its table; a multi-line
RAISE is consumed whole.
````

**Check it worked.** From `C:\ripple-build`:

```
python -m pytest tests/test_templating.py -q
```

You want `passed`. The test to insist on is the one where a CASE written down the
page survives intact. Without it, this file quietly destroys 600-line statements
and everything downstream reports a clean result over code nobody read.

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
  sources  every table the statement reads, EXCLUDING names defined by
           WITH — a CTE is a name for a query, and treating one as a table
           invents a link that is not there. A DELETE or UPDATE also reads its
           own target, or nothing ever looks at its WHERE clause.

           Do NOT gate this on the statement having a SELECT in it. A MERGE
           whose USING names a table, and an UPDATE ... FROM, both read a whole
           second table and have no SELECT anywhere. Gating on one meant they
           recorded no sources, were never indexed as reading anything, and no
           scan could reach them — on BigQuery that is the statement that loads
           the published table.

           A WHOLE-TABLE COPY has no SELECT in it either, and it is how a
           staging table is promoted into a published one:

             CREATE OR REPLACE TABLE published.customers COPY  stage.customers
             CREATE TABLE            published.customers CLONE stage.customers
             CREATE TABLE            published.customers LIKE  stage.customers
             ALTER TABLE stage.customers RENAME TO published.customers

           That single line is what connects everything upstream to the table
           people actually read. With no source recorded the trail died at the
           staging table and the screen said "last table in the chain — not
           matched by your production naming rule", which reads as an answer.

           A whole-table copy carries every column and writes none of them
           down, which is exactly what SELECT * means. So rewrite it, on the
           parsed copy only, into `CREATE TABLE <target> AS SELECT * FROM
           <source>` — then every piece that already follows a star works on it
           unchanged: the column is carried on, the hop is marked worked out
           rather than read, and the table is listed as one whose column list
           cannot be seen. Keep the word the file used (COPY, CLONE, LIKE,
           RENAME) on the Statement and carry it all the way to the screen. A
           row that says "Carried by SELECT *" about a file that says COPY
           sends somebody to the line to look for a statement that is not there,
           and then to doubt the finding rather than the label.

           CREATE SNAPSHOT TABLE is the same thing, but those two extra words
           make the parser give up on the whole statement. Retry it with
           "CREATE SNAPSHOT TABLE" replaced by "CREATE TABLE", and only after
           the parser has already failed, so it costs nothing on the statements
           that read normally.

           TABLE FUNCTIONS. A BigQuery TABLE FUNCTION is a table as far as
           lineage is concerned — it is named, it is read in a FROM clause, and
           every column of its body travels through it:

             CREATE OR REPLACE TABLE FUNCTION ds.recent(d STRING) AS (
               SELECT cm13 FROM customer_demographics WHERE dt = d)
             CREATE OR REPLACE TABLE published.summary AS
               SELECT cm13 FROM ds.recent('2026-01-01')

           BOTH halves are invisible to a naive reader. The definition parses as
           a function, not a table, so it publishes nothing; and the call parses
           as a function call whose table node carries NO NAME AT ALL, so it
           reads nothing. The chain breaks in the middle and the published table
           is never mentioned.

           Take the name off the function signature for the target, and off the
           call for the source. Two traps: a scalar UDF parses as the very same
           node with the very same kind, so tell them apart by their BODY — a
           table function's is a SELECT, a scalar one's is an expression, and
           getting this wrong turns every helper in the repository into a table.
           And BigQuery's own built-in table functions (EXTERNAL_QUERY, APPENDS,
           CHANGES, GAP_FILL, VECTOR_SEARCH and friends) WRAP a table rather
           than being one; the table they wrap is parsed separately and found
           anyway, so taking the wrapper's name too only invents a table nobody
           has. Keep a short list of those and skip them.

           BIGQUERY WILDCARD TABLES. Date-sharded tables are ordinary, and the
           only way to read one is a wildcard:

             SELECT cm13 FROM `prj.ds.customer_demographics_*`
             WHERE _TABLE_SUFFIX BETWEEN '20260101' AND '20260131'

           The source name recorded is `customer_demographics_*`, asterisk and
           all. Nobody has a table called that, so scanning a real shard matched
           nothing and scanning the family name matched nothing either — zero
           findings, a clean "no impact", on a change that breaks a published
           table.

           What a wildcard matches is not a guess: BigQuery only allows the star
           at the end, and it stands for every table in that dataset whose name
           starts with the part in front of it. So a wildcard covers a name when
           the name starts with that prefix. Match it in same_table AND in the
           lookup index — the index is keyed on the exact short name, so fixing
           only the comparison changes nothing.

           One deliberate addition to BigQuery's own rule: a person asked what
           breaks types the family the way they think of it — "customer_
           demographics", with no trailing separator, which BigQuery would not
           match. Match that too. It costs a row somebody can dismiss by opening
           the file; refusing it costs the clean "no impact" this tool exists to
           prevent. Do not go further than that: `ev` must never match
           `events_*`.

           Say so on the result. A finding reached through a wildcard names the
           wildcard, as the file spells it, in a card beside the findings — never
           on another screen. The dataset still rules a match out exactly as it
           does for an ordinary name.

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

A WHOLE ROW CAN BE CARRIED AS ONE VALUE, AND THAT IS A STAR TOO.

BigQuery lets a query pass an entire row around as a single value, and the
standard dbt-utils `deduplicate` macro is written exactly that way:

    SELECT unique_row.* FROM (
      SELECT ARRAY_AGG(original ORDER BY loaded_at DESC LIMIT 1)[OFFSET(0)]
               AS unique_row
      FROM customer_demographics original
      GROUP BY id)

`original` on its own — a bare name that is the table's ALIAS rather than any
column of it — is the whole row. So `unique_row.*` publishes every column the
table has, which is precisely what SELECT * means, and it has to be treated the
same way: the column is carried on, and the table built from it is listed as one
whose column list cannot be read.

Miss it and a deduplicated staging table, an ordinary thing to find in a dbt
repository, gives a clean "no impact" with no warning of any kind.

Only a BARE reference counts. `original.loaded_at` is one column, and
`STRUCT(a, b) AS s` is two named ones; treating either as a whole row would put
every column of the table on a chain the statement never touched.

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
transform with the function name), WHERE and HAVING and QUALIFY (filter, with
the literal it is compared against as `detail`), JOIN ... ON (join_key),
UNNEST in a join (transform), GROUP BY (aggregation), the statement's own
ORDER BY (ranking if there is a LIMIT under it, otherwise sort), window ORDER
BY (ranking — where removal is silent and awful), window PARTITION BY
(dedup_key), and MAX/MIN (dedup_key, which decides which row survives).

THIS LIST IS THE WHOLE GAME, AND A SHORT ONE IS THE WORST BUG THIS TOOL HAS.
A clause you do not read is a column you cannot see, and the answer that comes
back is not "unreadable" — it is "the name appears, but no lineage to a
production table", which reads as a reassurance. Every one of these was found
that way:

  QUALIFY            BigQuery and Snowflake filter on a window result, and
                     where nearly every dedup in a real pipeline is written.
                     The column often appears NOWHERE else in the statement.
  window PARTITION BY  the other half of a dedup. The ORDER BY picks the
                     winner; the PARTITION BY says what it wins against. Take
                     it away and one record survives for the whole table
                     instead of one per key, silently.
  WINDOW w AS (...)  the same dedup written as a named window clause instead
                     of inline. Writing it the other way round is not a reason
                     to miss it.
  UNNEST             FROM t, UNNEST(col) has no ON clause to look at.
  ORDER BY           writes the name down, so removing the column stops the
                     statement compiling and the table stops loading.

A DELETE or UPDATE has a WHERE clause and no SELECT at all. Requiring a SELECT
made both invisible, so "DELETE FROM stage WHERE market_code = 'US'" was
reported as no usage whatsoever.

A MERGE is worse again, and it is how a published table is normally loaded on
BigQuery, Snowflake and Databricks. When USING names a table directly there is
no SELECT anywhere in the statement, so it recorded no sources at all, was
never indexed as reading anything, and no scan could reach it however hard it
looked. Read all four parts of one:
  ON <condition>                       join_key
  WHEN ... AND <condition> THEN ...    filter — often the only place the
                                       column is named in the whole statement
  THEN UPDATE SET t.market = s.col     the column is published as `market`
  THEN INSERT (a, b) VALUES (x, y)     renames by position, like a plain INSERT
The last two are renames: follow the target's name onwards, not the source's,
or the chain walks off the end at the one statement that loads the table.

Return the most informative reading of each kind, most consequential first:
ranking, dedup_key, filter, join_key, transform, aggregation, select. One the
SQL was explicit about beats one it was not; after that, one carrying a
detail beats one that does not.

Also: mode_of(usages) returning "Transformed" if any transform, dedup_key or
aggregation, else "Direct pull"; locate(file, column, kind, line_offset)
giving the best guess at the real 1-based line, scoring lines by whether they
also contain the keywords that kind lives near; snippet(file, line, note)
returning a few lines of real code with the important one marked.

A FILE THAT IS ONE QUERY AND BUILDS NOTHING. A dbt model is a bare SELECT.
There is no CREATE, no INSERT and no MERGE, so nothing in the file names the
table it builds — dbt does, after the file. models/marts/customer_published.sql
builds customer_published. Measured before this: a three-hop dbt chain gave
productionTables 0, reachesProduction false, and the finding text "Selected
straight through into the next table" when there was no next table. EVERY dbt
repository produced zero lineage, and dbt is the commonest way a BigQuery
pipeline is written. That is the loudest possible version of this tool's worst
failure: a calm, clean, complete no-impact answer over none of the picture.

  The name is not a guess. A dbt model's name IS its file stem — that is the
  rule dbt itself runs on, and ref('customer_published') elsewhere in the
  repository resolves through exactly the same rule. Dataform (.sqlx) and every
  hand-rolled one-query-per-file runner work the same way.

  Three levels of evidence, labelled differently because they are not equally
  sure. Record which one applied on the statement, as named_by:
    "Dataform" — the file is .sqlx, or it opens with a config { } block.
    "dbt"      — the file is under models/, snapshots/ or definitions/, or it
                 calls ref(), source(), config() or this().
    "file"     — a .sql file holding exactly ONE query and no CREATE anywhere.
                 Something runs it and puts the rows somewhere; naming that
                 somewhere after the file is the convention every such runner
                 uses. Following it costs a row somebody can dismiss by opening
                 the file. Not following it costs the chain.

  Only ever name the ONE statement in the file that has no target and is a bare
  query. Two bare SELECTs in one file cannot both be the table the file is
  named after. For "dbt" and "file" also require that the whole file is that
  one query; a Dataform model may have pre_operations beside it.

  THE TRAP: check the FILE'S OWN FIRST LINE OF CODE, not the parse tree. Several
  statements that build nothing and are named after nothing are rewritten into a
  bare SELECT on the way into the parser — EXPORT DATA is the one that caught
  this — and by the time the tree exists they are indistinguishable from a dbt
  model. EXPORT DATA delivers a file to somebody outside the warehouse; naming
  its destination "a.sql" would be a table that exists nowhere. So for the "dbt"
  and "file" readings, require the file to say SELECT or WITH on its first line
  of code once comments and placeholders are taken off.

  Say it on the result. Anybody sent to that line to check will not find the
  table name written on it, and a finding somebody cannot verify is one they
  dismiss. See the namedByFile list in Phase 5.

A TEMPORARY TABLE BELONGS TO ONE FILE. A TEMP table is gone when its script
finishes, so two files that both build a "t" are not sharing a table — they
cannot be, because a static scan can never know two files ran in one session.
Temp names in real repositories are t, tmp, stg, base, deduped, so collisions
are the norm. Measured before this: two unrelated files, each building its own
"t", put BOTH of their published tables on the chain, marked the second one
breaking, and printed no warning of any kind.

  The dataset rule that keeps stage.orders apart from archive.orders cannot
  help, because a temp table has no dataset. So invent one: a scope standing for
  "inside this file", made of the file's own path with every non-alphanumeric
  character turned into an underscore, and marked with a "#" — a character no
  warehouse allows in a name. Apply it once the whole file is parsed, so a temp
  table used above the line that creates it is still caught.

  Move a name only when it has no dataset, or the _SESSION dataset BigQuery uses
  for them. ds.t is a real table that happens to share a short name with a temp
  one, and taking it would cut a genuine chain.

  same_table must treat a scoped name as ABSOLUTE: if either side carries the
  mark, the two datasets have to be identical. This is the one place the loose
  "no dataset given matches anything" rule is switched off, and it has to be —
  nothing outside that file can be reading a table that exists only inside it.
  For the same reason, when reading() is asked for a name with no dataset, drop
  any statement whose only matching source is scoped.

  Do NOT count the scope as a dataset when working out which names are
  ambiguous, or every "t" in the repository is reported as a name standing for
  more than one table. And STRIP THE MARK for display: it is your fence, not
  something anybody wrote, and a name on screen that is in no file sends
  somebody looking for a table that does not exist.

  Watch the leak one screen further along. Anything that walks ONWARDS from a
  finding — "published tables that stop being refreshed" does — must use the
  name the reader keyed, not the name shown on screen. Carry the real target on
  the finding for that purpose. Measured: fencing the chain off moved the false
  claim rather than removing it, and the unrelated published table reappeared
  under "stops being refreshed", worded as certainly as before.

INFORMATION_SCHEMA IS NOT DATA. It is BigQuery's catalogue of its own tables,
and its views are called COLUMNS, TABLES, JOBS, VIEWS, PARTITIONS — ordinary
words, and a warehouse of any size has real tables called some of them.
Measured: a real p.base.columns was reported as feeding a published table it
never touches, with a warning beside it that blamed CAPITALISATION — so the one
thing on screen pointing at the problem named the wrong cause, and following it
would not have found anything.
  If ANY dot-separated part of a qualified name is INFORMATION_SCHEMA, or the
  first part starts with "region-", it is the warehouse describing itself: never
  record it as a source, never record it as a target, never merge it with
  anything. Nothing that changes in a real table changes a COLUMN of
  INFORMATION_SCHEMA.COLUMNS — a ROW of it changes, and a row is not lineage.

PIVOT AND UNPIVOT. Both fold a column away and build differently-named ones out
of it, and both NAME the column while doing it, so the statement itself fails on
the day the column goes. Neither was read at all, and each failed in its own
direction.

  UNPIVOT was the worse of the two and the only case in the whole suite that
  hedges DOWNWARDS on a statement that hard-fails:
    CREATE OR REPLACE TABLE s1 AS SELECT * FROM customer_demographics
    UNPIVOT (val FOR metric IN (cm13, other_col));
  read as a plain SELECT *, so the answer was risk "low", breaking false, and
  the sentence "Nothing here fails on the day of the change" — printed about a
  statement whose UNPIVOT list stops being valid SQL.

  PIVOT failed the other way: the columns it builds are total_Q1 and total_Q2,
  worked out from the aggregate's alias and each IN value. Nothing derived them,
  so the trail was declared finished one hop early with the note "Last table in
  the chain", and the published table reading total_Q1 was never named.

  A PIVOT hangs off the FROM clause, not off any select list, so nothing that
  walks projections, WHERE clauses or joins can ever see it. Collect them from
  the FROM's table or subquery and from every join's, then:
    which columns it NAMES — an UNPIVOT's IN list; a PIVOT's IN list plus the
      columns inside its aggregates
    which columns it BUILDS — for a PIVOT, the output names the parser works
      out for you; for an UNPIVOT, the value column names plus the name column
      (renaming the source column changes what is written into the name column
      just as surely, so follow both)
  Map each named column to each built one as a reshape, add every named column
  to the "dropped by the star over it" set, and record a usage of its own kind —
  breaking on removal, rename and type change, but NOT on a value change, since
  an UNPIVOT folds whatever is there into rows either way. Suppress the SELECT *
  usage for a column a pivot consumes: the pivot is definitive about that one
  column, and letting the star speak as well puts "carried through untouched"
  beside "named here, and this statement fails without it". And label the row
  with the word the FILE uses — PIVOT and UNPIVOT are opposite operations.

PARTITION BY AND CLUSTER BY ON THE CREATE LINE. These sit outside the SELECT, so
nothing that walks a query can see them. Measured: a table partitioned by the
very column being decommissioned returned NO usages at all, and the whole chain
came back risk low, groups 0, couldNotRead 0. It is not a column of the table
being built, so no chain follows from it — but the name is written on the CREATE
line, so the day the column goes the statement stops compiling, the table stops
being built, and every published table underneath it quietly serves data that
has stopped being refreshed. Walk the CREATE's properties for anything whose
name mentions Partition or Cluster and record a usage. Note that PARTITION BY
cm13 with nothing round it parses as a bare IDENTIFIER, not a column, so
searching for columns alone finds nothing.

A COLUMN NAMED AFTER A PARENLESS FUNCTION. BigQuery lets CURRENT_DATE,
CURRENT_TIME, CURRENT_TIMESTAMP and CURRENT_DATETIME be written with no
brackets, so "SELECT current_date FROM customer_demographics" parses as a call
and not as a column at all. A table with a column of that name then produces the
cleanest possible zero: risk none, prod [], found 0, nameInTables 0 — Ripple did
not miss the column, it never saw one. Backticked, the very same scan is risk
medium and reaches production.
  Which of the two the writer meant cannot be known from the file: both are
  valid BigQuery and both are written exactly the same way. So FOLLOW BOTH —
  read the node back as a column — and mark every usage of that name in that
  statement as not certain. Only where the file writes the name with NO brackets
  after it; CURRENT_DATE() is unambiguously the function.

A HOLE WHERE THE COLUMN LIST GOES. A great many Airflow DAGs build SQL as
  cols = "cm13, cm14"
  sql = f"CREATE OR REPLACE TABLE ds.final_published AS SELECT {cols} FROM ..."
The placeholder is filled in before BigQuery ever sees it, so the column list
genuinely is "cm13, cm14" — but it is not in the file, and Ripple reads
"SELECT cols FROM ...". Measured: Ripple believed the published table had
exactly one column, called "cols", and answered reachesProduction False, risk
none, unreadable 0, couldNotRead 0. Identical with .format().
  A hole standing where a projection goes is a SELECT * that has not been filled
  in yet. Replace it with a star, which makes the whole existing star machinery
  work: the trail carries on, the table is listed as one whose column list is
  not visible, and every finding past it is marked worked out rather than read.
  Record on the statement that the star came from a placeholder, and use that
  everywhere the screen would otherwise say the file writes SELECT *. It does
  not, and a row that claims it does sends somebody to a line where no such
  statement is written.

A SELECT WRITTEN AS A VALUE IS NOT A SOURCE OF ROWS. When you group a
statement's SELECTs by nesting depth to work out what each column leaves as,
skip any SELECT that sits in the select list, or inside a WHERE, HAVING,
QUALIFY, GROUP BY or ORDER BY. Those are values — one number, one list to test
against — and the names inside them are their own business.
    SELECT o.k,
           (SELECT MAX(d.cm13) AS c_alias FROM customer_demographics d
            WHERE d.k = o.k) AS peak_cm
    FROM other_source o
  Measured before this: the statement's output name for cm13 came back as
  c_alias — a name that exists only inside the brackets and appears on no table
  anywhere. The real name is peak_cm, which is what the next table reads, so the
  chain went cold one hop early and reported no production impact. The mirror is
  just as bad: WHERE k IN (SELECT cm13 AS c_alias FROM ...) INVENTED a column
  called c_alias on the table being built. A subquery in FROM or JOIN, and a
  CTE, really do hand their columns to the query around them: leave those alone.
  Walk up from the nested SELECT to the enclosing one and look at which argument
  of it the chain arrived through.

SELECT * REPLACE(legacy_code AS cm13) NAMES cm13. Remove it and this statement
fails, exactly as it does with EXCEPT — and the column of that name downstream
is fed by the replacement from here on, not by this one. Ripple got the right
answer for the wrong reason: the rename was followed, but nothing said the name
was written down here, so the row read "breaking: false" about a statement that
stops compiling. Record a usage on the REPLACE target, add the replaced name to
the star's dropped set, and suppress the plain SELECT * usage for it. Label the
row REPLACE rather than EXCEPT — they are different statements and the file says
which.

_TABLE_SUFFIX. A wildcard table reads a whole family of date-sharded tables, and
the query almost always narrows that down on the very next line:
    SELECT cm13 FROM `p.ds.customer_demographics_*`
    WHERE _TABLE_SUFFIX = '20260101'
Ripple followed the wildcard and never read the line under it, so scanning
customer_demographics_19991231 — a shard from 1999 this query provably never
touches — came back risk medium, breaking true, CERTAIN true, with no hedge
anywhere. The predicate is on the same line as the wildcard, inside the snippet
Ripple prints, and the answer contradicted it.
  Work out the shard's suffix from the wildcard's own prefix, then read the
  _TABLE_SUFFIX comparisons in the WHERE: =, !=, <, <=, >, >=, IN and BETWEEN
  against string literals. Excluded means drop the finding. Anything you cannot
  evaluate — a parameter, a date calculation, a variable — sets certain=false and
  the finding STAYS; guessing at one would trade an over-confident answer for a
  missing one. Only ANDs: an OR or a NOT above the comparison means other shards
  are read too. And never narrow when the person typed the family name with the
  asterisk in it, because then no one suffix can be tested.

ONE TABLE, TWO FILES THAT BUILD IT. A CREATE OR REPLACE replaces the whole
table, so only one of them can be the definition that runs. Two of them in two
files is a fork — usually a live copy and a stale one under archive/ or dev/
that nothing schedules. Measured: the ONLY finding reported came from the
archive copy, presented with breaking true and certain true and the same wording
as any live finding, while the live definition appeared under "mentions only".
Where the real build is generated at deploy time and only the stale copy is
committed, that is a confident, clean answer about a pipeline that no longer
exists. Keep a map of short table name to the files that fully REPLACE it, and
report the ones with more than one. An INSERT or a MERGE adds to a table and
several files loading one that way is ordinary; only a CREATE forks it.

DATAFORM FILES. A .sqlx file is Google's own way of writing a BigQuery pipeline:
an ordinary SELECT with blocks on top that are JavaScript, not SQL.
    config { type: "table" }
    js { const x = 1 }
    pre_operations { DELETE FROM ... }

    SELECT cm13 FROM ${ref("customer_demographics")}
The parser refuses the whole file on the first line, so nothing at all is
learned from it. In the same place you rewrite the other shapes the parser
refuses, drop the config and js blocks whole (keeping their line breaks), and
for pre_operations and post_operations drop the brackets and KEEP the contents
as one more statement — those hold real SQL that really runs. Match braces
yourself rather than with a regular expression, because a brace inside a quoted
string closes nothing.

FOUR SHAPES THAT NAME A TABLE AND WERE INVISIBLE

Each measured as a clean answer over less than the whole picture.

  EXECUTE IMMEDIATE '<one quoted string>'
      The parser gives up and hands back a generic command, so the CREATE inside
      the string was read, understood as nothing, and produced no lineage — with
      the whole statement sitting in the file in plain sight. Parse the contents
      of the literal when the WHOLE thing after IMMEDIATE is one quoted string
      and nothing else (an INTO or a USING after it is allowed). Mark every
      statement that comes out built_as_text = "EXECUTE IMMEDIATE", carry that
      onto the finding, and say so on screen: the line it points at holds a
      string, not the CREATE the row describes, and somebody who opens it
      expecting the statement doubts the finding rather than the label.
      REFUSE, and stay unreadable, when the name is built rather than quoted:
      FORMAT(...), 'CREATE TABLE ' || env || '_mid', or a literal containing a
      "?" placeholder. In each of those the statement never exists as text
      anywhere, so there is nothing to read, and inventing the missing piece is
      the exact failure this reader exists to avoid.

  ALTER TABLE t RENAME COLUMN a TO b
      _target_of covered Create, Insert, Merge, Delete and Update and NOT Alter,
      so a repository holding its own rename migration gave target None,
      sources [] and reported no impact at all for the column the migration
      renames. That is the plainest statement of a rename the language has. Add
      Alter to _target_of, add it beside Delete and Update where the target is
      also added to sources, and read its actions:
        RenameColumn   -> usage kind "renamed", and output_names returns the
                          NEW name, so it is followed as the alias hop it is
        Drop(Column)   -> usage kind "dropped", and output_names returns []
                          — the column stops here, in this file, by name
        AlterColumn    -> usage kind "retyped", the name is written down so the
                          migration itself fails without it
      "renamed" and "retyped" break on removal and rename. "dropped" breaks
      nothing: it is not broken BY the change, it IS the change — and it is
      worth reporting for exactly that reason.

  CREATE SEARCH INDEX / VECTOR INDEX / ROW ACCESS POLICY / UNDROP TABLE
      All name a table, most name columns of it, and none carries a column
      anywhere. The parser gives up on every one, so the whole statement was
      invisible: the file landed on the check-by-hand list with nothing saying
      which table or which column it was about. Read the table and the column
      list out of them with a REGULAR EXPRESSION rather than a parser, and
      record them as "referenced here" — never as lineage, never as an edge,
      never as a hop. Reading it loosely can add a row to a list; it must never
      move a chain. A row access policy filtering on the scanned column stops
      working the day the column goes, so risk may not read "none" while one of
      these names it. UNDROP TABLE is a HARD parse error, which in sqlglot loses
      the statements either side of it — rewrite it in the rescue pass so it
      lands as a generic command, and read the table name out of that. Report a
      statement read this way ONCE: on the "named here, but nothing is carried"
      card, and NOT also as a file nobody could understand.

  EXPORT DATA OPTIONS(uri='gs://feed/partner/*.csv') AS SELECT ...
      An export builds no table, so the trail had nothing to carry the column on
      to, and the answer read "no production table is affected" — true, and
      useless. The delivery is what breaks, and whoever reads that file every
      morning is outside this repository, so no scan of it will ever find them.
      Read the uri BEFORE the rescue pass strips the OPTIONS clause, drop the
      last path segment when it holds a "*" or a "." (that is a filename
      pattern, not a place), and hang the result on the statement as export_uri.
      Match exports to statements in FILE ORDER, not by line number: the rewrite
      removes the whole "EXPORT DATA OPTIONS(...) AS", so what is left starts on
      the line after the export's own.

Tests: a statement split rescues the readable statements around a bad one;
MERGE, DELETE and UPDATE are seen; CTE names are not treated as tables; a
column renamed inside a subquery is followed out; a column leaving under two
names returns both; a filter records the literal; a join on the other table's
column of the same name is not reported; where the SQL does not say, the
usage is kept with certain=False; a window ORDER BY is a ranking.
````

**Check it worked.** From `C:\ripple-build`:

```
python -m pytest tests/test_sqlread.py -q
```

You want `passed`. Later, when you point Ripple at real code and most of it comes
back unreadable, the cause is almost never this file — it is the SQL dialect being
set wrong, or Phase 3 not being applied on the way in.

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


A TABLE THAT STOPS BEING REFRESHED IS A SECOND KIND OF IMPACT, AND MUST BE
REPORTED SEPARATELY.

A column used only in a WHERE, a JOIN or a GROUP BY never reaches the table the
statement builds. The trail for that COLUMN genuinely ends there, and saying so
is right. But the STATEMENT stops working on the day the column goes, so the
table it builds stops being rebuilt — and every published table under that one
goes on serving whatever it held yesterday. Nothing errors on the screen of
whoever reads it. The numbers are simply out of date, and stay out of date.

So: collect the tables built by any statement with a BREAKING finding on it,
follow those tables DOWNSTREAM at the level of tables rather than columns (which
column carries onwards stops mattering once the job has stopped), and report the
published ones they reach.

Three rules about how it is shown, and they matter more than the walk:

* It is a DIFFERENT question from "what breaks", so it gets its own heading, its
  own words and its own count. Folding it into the production-table number makes
  one number that means neither thing.
* Leave out any table already reported above. Saying it twice under two headings
  reads as two problems.
* Cap the walk (400 tables is plenty) and SAY SO when the cap is hit. A list cut
  short without a word reads as "there were only these".

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
no_local_fix, file, lang, snippet lines, hop, certain, the line its own
statement starts on, and `roots` — the attributes the person actually asked
about.

The line the statement starts on is part of what makes two findings the same
finding, and it has to be. One file very often builds several tables and
filters on the same source column in each of them. Keyed on file, table,
column and kind alone, the second and third statements were folded into the
first: the row shown under a published table pointed at another statement's
lines, named another statement's target, and the count of usages was quietly
short. Two renames down, the column on a
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
there are findings.

With no findings at all the answer is "none" — EXCEPT where there is a gap
Ripple knows about, and then it is "unknown", worded on screen as "Not sure —
needs a person". "No impact" is the only thing this tool sells, so it is the
one word that must never be printed over something Ripple could not look at.
"I found nothing" and "I could not look" are not the same answer, however
similar they look on screen. A gap means any of:
  a file that could not be read AND that mentions one of the names being
    followed — restricted that way because every real pipeline has some file
    the reader cannot make sense of, and a badge that says "not sure" on every
    scan ever run is one nobody reads;
  a file that could not be read and was never OPENED either, so nothing can say
    whether it mentions the name — which is exactly the problem with it;
  any file held online-only, or whose path was too long to open.
Measured before this: an EXECUTE IMMEDIATE holding a whole CREATE ... SELECT of
the scanned column printed a green "No impact" with couldNotRead 1 sitting
underneath it, and a file whose first statement was eaten by a byte-order mark
did the same. So did a whole repository read with the wrong SQL dialect, where
three files failed and nothing at all was learned.

Also carry the target table AS THE READER KEYED IT on each finding, beside the
one shown on screen. They are not always the same name — a temporary table is
fenced to the file that built it and the fence is stripped for display — and
anything that walks onwards from a finding has to use the keyed one or it looks
the table up by a name that matches every other file's temporary table.

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

FOUR MORE LISTS ON THE RESULT, each a caveat that must sit BESIDE the answer
it qualifies and never on another screen:

  namedByFile[]      {table, file, how} — tables whose name is nowhere in the
                     file that builds them, because the tool names them after
                     the file. "how" is "dbt", "Dataform" or "file". Without
                     this, somebody who opens the file to check the finding
                     will not find the table name written on it, and a finding
                     they cannot verify is one they dismiss.
  twoDefinitions[]   {table, files[]} — tables more than one file builds FROM
                     SCRATCH. Only one of those can be the definition that
                     runs, and nothing in the code says which.
  skippedInFolders[] the code files Ripple walked past because of the folder
                     they sit in, with skippedFolderNames[]. This count used to
                     reach the repository screen and nothing else, so a scan of
                     a dbt project — whose target/ folder holds the SQL that
                     actually runs — came back "risk none, prod []" with the
                     reason on a screen nobody was looking at.
  starTables[]       gains a "filledIn" field. A table whose column list is not
                     visible is not always a SELECT *: it can be a placeholder
                     the job fills in when it runs. No screen may tell somebody
                     the file says SELECT * when it does not.

SIX MORE THINGS ON THE RESULT. Every one exists because two DIFFERENT facts
were printing as the same sentence, which costs exactly as much as a missed hop.

  feeds[]            {uri, file, line, from, attrs[], breaking} — deliveries out
                     of the warehouse. Counted as feedsBroken and kept OUT of
                     productionTables: a file in a bucket is not a published
                     table, and one number covering both means neither.

  referencedHere[]   Index, policy and UNDROP DDL naming a table the chain stood
                     on or a column being followed, with the columns it names.
                     Narrow on purpose — every warehouse is full of indexes on
                     tables this scan never heard of, and listing those buries
                     the ones that matter.

  builtAsText[]      Statements the file runs as text — EXECUTE IMMEDIATE. The
                     hop is real; the line is a quoted string.

  lookupFailed       True when EVERY attribute asked about is a name Ripple
                     never met as a column on ANY table, and nothing was found.
                     "I never saw that column" and "that column goes nowhere"
                     were byte-for-byte the same answer — found 0, no findings,
                     a green tick — and they are OPPOSITE answers: the first is
                     the question never having been asked, so a typo in an
                     attribute name shipped as "no impact". Per attribute also
                     carry tableColumns: the columns Ripple DID see on that
                     table, taken from the statements that build it AND from the
                     statements that read only it (nothing in a repository ever
                     builds a source table, so its columns are only written down
                     by the queries that read it). That turns a silent wrong
                     answer into a spelling mistake somebody spots in two
                     seconds. Work it out ONLY when a lookup actually fails, and
                     only once per table: it walks every statement.

  coverage           How much of this trail Ripple could see, as COUNTS of what
                     it already worked out and used to throw away: unreadable
                     files, files never opened, tables built with SELECT *,
                     trails cut short at the hop limit, findings sitting past
                     one of those, merged names, and findings on a line that did
                     not say which table. "No impact, and I could follow every
                     step of it" and "no impact, and three tables on the way
                     were invisible to me" printed as the same three words.
                     NOT a percentage: there is no honest denominator for "how
                     much of a trail exists", and a made-up one puts a precise
                     number on a guess.

  wildcardNames[]    Only the wildcards that actually PRODUCED a finding. The
                     card says "the usages below are real", and it was being
                     printed over an empty list: a wildcard in one dataset
                     covering a shard in another matches by short name and is
                     then ruled out by same_table, so it produced nothing.
                     Each entry also carries shorthand[]: the patterns that
                     matched only because the family name was typed without the
                     separator BigQuery requires. So wildcard_match returns
                     "shard", "family", "both" or "" rather than a yes/no — a
                     shard match is a fact about the SQL and stays certain; a
                     family match is a guess about what somebody meant and sets
                     certain=False on every usage from it. Matching it at all is
                     right, because typing the name you say out loud must not
                     produce a clean "no impact"; shipping it as certain was not.

THE INFORMATION_SCHEMA HINT. A statement that looks a table up in BigQuery's own
catalogue by name — WHERE table_name = 'customer_demographics' — was reported
with the hint "which is how in-house helpers take a column or table name". That
is correct code doing exactly what it should, and the one line on screen pointing
at the problem named a cause nobody could find. Ask the parse TREE whether the
statement reads a metadata view, not the Statement's sources: a metadata view is
deliberately never recorded as a source.

"I NEVER SAW THAT COLUMN" IS A CONFIDENT CLAIM

lookupFailed says Ripple read everywhere it could and this name is not a column
anywhere. It may only be set when that is true. Measured, all three printing a
green "check your spelling" over a real gap:

* a file naming the column that could not be read;
* the whole chain sitting in a build/ folder Ripple is told to skip;
* a row access policy naming that very column, on the same screen.

So set it only when every attribute failed AND coverage is complete AND nothing
on the subject went unread AND no index or policy names the column.

Coverage counts the skipped folders too -- a folder Ripple was told to skip is
exactly as unread as a file it could not open. And risk reads "unknown" rather
than "none" when NOTHING was found and code files were skipped by folder. Only
when nothing was found: skipping build, dist and target is ordinary, and a badge
reading "not sure" on every scan of every dbt project is one nobody reads.

Also produce graphs[] for the dependency picture: per attribute, the branches
that reach a published table and the branches that end elsewhere, each a list
of {name, kind, alias, prod}. Drop any branch that is only the start of a
longer one already listed.

Tests: a chain through two renames reaches the published table; a column
leaving under two names does not lose the chain; findings are reported even
when NOTHING matches the published rule, and the risk is not "none";
correcting the rule turns them into production tables; a genuinely clean
result is still clean; a name inside a quoted string is reported even in a
file that has findings, with a count of lines; groups come back worst first;
a repository with nothing found but a file it could not read comes back
"unknown", and a clean one still comes back "none".
````

**Check it worked.** From `C:\ripple-build`:

```
python -m pytest tests/test_lineage.py -q
```

You want `passed`. The one test to insist on: *findings are reported even when
nothing matches the published-table rule, and the risk is not "none"*. If the chat
quietly returns an empty result there, it has rebuilt the exact bug this tool
exists to prevent, and no amount of green elsewhere makes up for it.

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
its attributes; MATCH NAMES IN ANY CASE, and do not require an underscore.
Matching only SHOUTED_NAMES looks reasonable and is a quiet disaster: BigQuery
names are written in lower case, real repositories have tables like
ccm_Wireless_Enroll in mixed case, and plenty of columns - cm13, pub_guid -
are one word. An email reading "we are removing cm13 from
customer_demographics ... ACCOUNT_MASTER is unaffected" produced exactly one
table to scan: ACCOUNT_MASTER, the only one the email says is fine, with no
warning of any kind. Being wide costs nothing, because a word only becomes a
table or a column once the catalogue confirms it is one - and a spare name on
the confirm screen is a tick somebody can clear, while a missing one is
invisible. Keep the narrow SHOUTED_NAME rule for one job only: listing the
names an email mentions that the repository has never heard of, which would
otherwise become every ordinary word in the message; a date in any common written form becomes ISO; words like
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

**Check it worked.** From `C:\ripple-build`:

```
python -m pytest tests/test_notification.py -q
```

You want `passed`. You will feed it a real notification email in Phase 12, on the
screen, where you can see what it made of it.

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
WHAT THE LETTER MUST NEVER SAY

"No impact. Please proceed as planned" is the most consequential sentence this
tool writes, and it was being written over every one of these. The summary and
the reply have to read the SAME facts the findings screen does:

  lookupFailed        Its own branch, before anything else. The question was not
                      answered, so the letter asks the upstream team to confirm
                      the column name. It does not report an impact either way.
  feeds[]             Name the destination. The letter used to say the data
                      feeds "tables in our own pipeline" about an EXPORT DATA
                      going to a partner's bucket.
  stopsLoading[]      When a published table stops being refreshed, the headline
                      must say so -- and must NOT say "none of them reaching a
                      table on your published list", nor send the reader off to
                      fix a production rule that matched perfectly.
  referencedHere[]    A row access policy naming the column is not "no impact".
                      It carries the column nowhere and stops working all the
                      same, so it gets its own paragraph.
  skippedInFolders[]  Counted with the files that could not be opened. A folder
                      Ripple was told to skip is exactly as unread.

  a genuinely clean result still says no impact, in both
````

**Check it worked.** From `C:\ripple-build`:

```
python -m pytest tests/test_narrative.py -q
```

You want `passed`. Then read the four drafted replies in the test file out loud.
These are the words that leave the building and get forwarded to another team, so
if any of them would embarrass you, say so in the same chat and have it
rewritten.

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

GET  /api/health      includes `build` — which build this is, so a screen can
                      say it. Nothing did, and "it does not work" has more than
                      once turned out to be "that was fixed a while ago, on a
                      copy that was never installed". Look in four places, best
                      first: a stamp file written into a packaged folder at
                      build time, the host's environment (Vercel sets
                      VERCEL_GIT_COMMIT_SHA), git, and last the dates on
                      Ripple's own files. Return where the answer came from as
                      well as the answer, and say plainly on screen when it is
                      the last one — a file date moves whenever anything is
                      touched and proves nothing about what was installed. A
                      guess dressed as a fact is worse than no line at all.
                      Also: the shape in the contract card: repo counts including
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
POST /api/read-email  (file upload — .msg, .eml or a plain text file)

There is no route that takes typed-in email text. There was one, and it went:
a box somebody pastes an email into produces a notification with no envelope —
no From, no Subject, nothing but words — so the source system and the contact
came back blank far more often than from the same email uploaded as a file. Two
ways in that behave differently is one too many. Upload the file, or use the
manual tab. The function that reads message text STAYS, because a plain .txt
upload is read with it.
POST /api/scan        {upstream[], changeKind} -> the scan result JSON
POST /api/summary     {scan, vals} -> {summary, reply}
POST /api/history     GET /api/history     GET /api/history/{id}
PATCH /api/history/{id}  {status}
GET  /api/file?path=  the real text of a scanned file

Refuse an upload over max_upload_bytes with a message saying what the real
ceiling is and why, not a bare 413.

Serve web/ at /static and web/index.html at /, finding that folder with
paths.web_dir() from Phase 1 and never by walking up from __file__ — see the
reason there. Send Cache-Control: no-store
for the page and the script — during a demo or an edit, a cached script is
the difference between seeing a change and staring at yesterday's page. Cache
the fonts, if any, for a month.

Also write run.py at the project root: print the repository, the dialect and
the address, whether it is running packaged or from source, then start uvicorn
on host 127.0.0.1, port 8000, with a --no-browser flag.

Pass uvicorn the app OBJECT -- from ripple.api import app -- and not the string
"ripple.api:app". Both work today. Only the object still works once this is
packaged in Phase 13, because a packaged program has no importable module of
that name to look up, and the string form exits immediately with "Could not
import module".

BIND TO 127.0.0.1 AND NEVER TO 0.0.0.0. The two look interchangeable and are
not. 127.0.0.1 is the machine talking to itself and cannot be reached from
outside it. 0.0.0.0 offers the whole application to everyone on the office
network, which would put an analysis of internal source code on a port any
colleague could open, with no password on it. Tutorials are full of 0.0.0.0
because they are written for containers. This is a laptop.
````

**Check it worked.** From `C:\ripple-build`:

```
python run.py --no-browser
```

It prints the folder it will read, the SQL dialect and an address, and then sits
there doing nothing. That is correct — it is waiting for a browser. **Leave it
running** and open a second Command Prompt, then:

```
curl http://127.0.0.1:8000/api/health
```

A wall of text starting with `{"ok":true` is a pass. To stop the server when you
are done, go back to the first window and hold Ctrl and press C.

---

# PHASE 9 — the page and its styles

**Saves to:** `ripple-build/web/index.html`, `ripple-build/web/styles.css`

````text
[PASTE THE CONTRACT CARD FIRST]

Build web/index.html and web/styles.css. No framework, no CDN, no build step.

This phase builds how it looks, and it is the one phase where the words below are
a specification rather than a suggestion. The colour values are exact. Use them as
given.

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
The palette is not a matter of taste. It is the design, already settled, and
it is settled already. Define exactly these CSS variables at the top
and use them everywhere -- never a colour written inline:

  --navy:#00175A; --blue:#006FCF; --blued:#005CAD; --pale:#E3F0FC;
  --line:#DCE4EE; --line2:#C7D4E4; --line3:#E7EDF5; --hair:#F0F4F9;
  --bg:#F2F5F9; --card:#fff; --tint:#FAFCFE;
  --ink:#10243E; --body:#33445E; --mute:#5C6C84; --faint:#8595AB;
  --chip:#EDF2F8; --chipink:#45566E;
  --red:#B01C2E; --redbg:#FDE8E8; --redln:#F3C4C4;
  --amber:#8A6100; --amberbg:#FFF4D9; --amberln:#EFDFAF;
  --green:#006B40; --greenbg:#E4F5EC; --greenln:#BFE5CE;
  --violet:#6D4B9E; --violetbg:#F0EAFA; --violetln:#D8C9EF;
  --codebg:#FBFCFE; --codehead:#0B1F45; --codenum:#93A3B8;
  --hit:#FFF7E1; --hitln:#F0DFAE; --hitbar:#E3A008; --hitpill:#FFF1CC;
  --shadow:0 1px 2px rgba(16,36,62,.06);

They are named for what they do, which is why there are four greys for lines:
--line is a card border, --line2 an input border, --line3 a divider inside a
card, --hair a row separator. The four ink tones run the same way, strongest
first: --ink for headings, --body for paragraphs, --mute for card labels,
--faint for field labels and hints.

Cards are white with a 1px --line border, 12px radius and --shadow. Body text
is 14px with line height 1.5. The sans family is 'Public Sans' falling back to
Segoe UI and system-ui. The monospace family, used for every table and column
name on screen, is 'IBM Plex Mono' falling back to Consolas.

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

**Check it worked.** From `C:\ripple-build`:

```
python run.py
```

Your browser opens by itself. You should see the dark navy sidebar down the left
and the header strip across the top, **in colour**, with an empty area in the
middle. Nothing else works yet, and that is expected — the screens arrive in the
next two phases. If what you get is black text on a plain white page with no
layout at all, the stylesheet did not load rather than being wrong.

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
Email mode: a drop zone that also opens a file picker. No paste box — see the
routes above for why — and beside the drop zone a short card pointing at the
manual tab, so "I have no file" has a visible answer rather than a dead end.
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
Right: what kinds of file are in the index, counted; the file types Ripple does
NOT open with a count each, from unknown_ext, so the next unlisted extension is
visible instead of silent — nothing recorded those before, and a repository whose
pipeline is written in .ipynb or .tf files looked exactly like one with no
pipeline in it; a confirmation note with the branch and the file count; the never-opened note if there is one, saying
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

**Check it worked.** Start it with `python run.py` and click through. You should be
able to walk from step 1 to step 3, and step 3 should show real counts from a real
folder. The "Run impact analysis" button will not do anything yet — that arrives in
the next phase.

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

FIVE CARDS UNDER THE FINDINGS, each one a thing Ripple could not see and each
one BESIDE the answer it qualifies. Every one of these was, at some point, a
warning that lived on another screen while a scan said "no impact":

  Tables whose column list is not readable (starTables). Say which kind each is
  — built with SELECT *, a whole table copied or renamed with COPY / CLONE /
  LIKE / RENAME, or a placeholder the job fills in at run time. Never describe a
  statement the file does not contain.
  One name standing for more than one table (mergedNames).
  Tables read through a wildcard rather than by name (wildcardNames).
  Tables built from scratch in more than one file (twoDefinitions). Say that
  only one of them can be the one that runs and that nothing in the code says
  which, so the reader checks their scheduler before acting.
  Code files not read because of the folder they are in (skippedInFolders).
  Name the folders, and say that if the pipeline really runs from one of them
  the skip list on the settings screen can be changed.
  Tables named after their file rather than by the SQL (namedByFile). Say which
  tool names them, and that opening the file will show the query and not the
  name.

AND ONE SENTENCE UNDER THE FILE COUNT, on every scan, that qualifies every other
sentence on the screen: Ripple read these N files and nothing else, so "no
impact" means "nothing in this repository", not "nothing anywhere" — a job in
another repository, a scheduled query, or a dashboard built straight on the
table is outside what it can see. That is the single commonest way to be wrong
with this tool.

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

THE AI KEY BOX. Three providers — OpenAI, Google Gemini and Groq — and ONE
box, not three. Which company issued a key is worked out from the key itself,
from its first few characters. Asking is one more thing to get wrong, and a key
sent to the wrong company comes back rejected, which reads as "your key is bad"
when it is not.

All three speak the same OpenAI-shaped POST /chat/completions, so there is one
code path and only the address, the key and the model change. Google's own
OpenAI-compatible endpoint is at
https://generativelanguage.googleapis.com/v1beta/openai — confirmed live with a
deliberately wrong key rather than taken from documentation.

Four things this must get right:

* An Anthropic key begins "sk-" exactly as an OpenAI one does. Match the
  LONGEST prefix, and keep a list of keys you recognise but cannot use so the
  screen can say "that is an Anthropic key" instead of "rejected".
* Google answers a bad key with 400 and "Please pass a valid API key", not 401.
  Read as a bad request that sends somebody to check their prompt rather than
  their key.
* DO NOT WRITE A LIST OF MODEL NAMES INTO THE CODE. It is wrong within months
  and then offers a model that no longer exists, discovered at the moment
  somebody is trying to read an email. Ask the provider — GET /models with the
  key — which proves the key and produces the real list in the same call. Keep
  a preference ORDER for choosing a default, filter out the models that cannot
  hold a conversation (embeddings, audio, images), and keep every other one:
  hiding a model somebody is paying for because you have not heard of it is the
  worse mistake.
* Not every provider accepts every optional field of an OpenAI-shaped request.
  If one refuses response_format, send the request again without it rather than
  losing the whole call — the prompt asks for JSON in words as well.

The screen reads the prefixes from the server so there is ONE list of them, and
names the provider as the key is typed, before anything is sent anywhere.

Also on the settings screen: a card saying WHICH BUILD IS RUNNING, from the
`build` block of /api/health — the version, the commit if there is one, and the
date. Underneath it, one line saying where that came from: read from the
repository, recorded when the copy was packaged, reported by the host, or — when
nothing better was found — the date of the newest file in the folder. That last
one must say out loud that it is a guess. A file date moves whenever anything is
touched and proves nothing about what anybody installed, and a guess that looks
like a fact is worse than no line.

Write this card once, as shared code, and call it from every edition's settings
screen. It exists because the copy nobody can check is exactly the one that
turns out to be months old, and putting it only on the screen you happen to be
looking at is how the half-shipped fix happens.
````

**Check it worked:** run a scan against a real folder and click through all seven
steps. Then paste a deliberately messy list into the settings box — with a typo
in it — and confirm the typo comes back named.

---

## The cards that qualify the answer

These sit BESIDE the findings, never on another screen. A caveat one click away
from the answer it qualifies is a caveat nobody reads.

* **How much of this Ripple could see** — the coverage counts, at the top of
  "how to check this result", plus a second badge next to the risk word reading
  either "whole trail seen" or "N gaps in what Ripple could see".
* **Column not found** — when lookupFailed, the headline badge reads "Column not
  found — nothing was checked" instead of a risk word, and the attribute panel
  prints back the columns Ripple DID read on that table.
* **Deliveries out of the warehouse** — the feeds, with their own stat card.
  Never folded into "production tables at risk".
* **N places name this, and carry it nowhere** — the referencedHere list, with
  the table, the columns named, and the file and line.
* **N statements are written as text and run** — the builtAsText list, and a
  "run as text" badge on every row that came out of one, because the code shown
  underneath such a row is a quoted string and looks nothing like the statement
  the row describes.
* **The wildcard card** gains a warning when any pattern matched only the family
  name without its separator: BigQuery would match nothing there, so every row
  from it is marked "table not stated".

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

**Then run everything.** First the whole test suite, from `C:\ripple-build`:

```
python -m pytest -q
```

Then start it, and this time let it open the browser, because every line of the
checklist is something to look at on screen:

```
python run.py
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

## Starting it with a double-click, before it is packaged

Once it all works you will not want to open a Command Prompt every time. Two
commands, once:

```
type nul > C:\ripple-build\start-ripple.bat
```

```
notepad C:\ripple-build\start-ripple.bat
```

Put these two lines in it, save, and close:

```
cd /d C:\ripple-build
python run.py
```

Now double-clicking **start-ripple.bat** starts Ripple and opens the browser. To
have it on your desktop, right-click it and choose *Send to → Desktop (create
shortcut)*. To stop Ripple, close the black window that opened with it.

**Why not a packaged .exe?** It can be done, and it is deliberately not in this
kit. On a managed laptop, an unsigned program you built yourself, which then opens
a network port, is close to the worst possible shape as far as endpoint security is
concerned — it tends to be quarantined, and explaining it afterwards costs more
time than it ever saved. The batch file gives you the same double-click and none of
that.

---

# PHASE 13 — packaging it as a program

**Saves to:** `C:\ripple-build\build.py` (new). Nothing else changes — Phases 1
and 8 already wrote the three things a packaged program needs.

**What you get.** A folder called `Ripple` holding `Ripple.exe` and one other
folder, about 40 MB in total. Copy that folder anywhere, double-click the program,
and Ripple starts and opens the browser — on a machine with no Python on it and
nothing installed. Packaging takes about a minute and a half each time.

**About the thousands of files in that other folder.** Open it and you will find
roughly 1,770 files. **You do not write any of them, and you never look at them
again.** They are put there by the packaging tool, every time, in about ninety
seconds. Counted on a real build:

| How many | What it is |
|---|---|
| ~923 | Python's own windowing library — it draws the "choose a folder" box and the error box |
| ~605 | a timezone database, dragged in by the Outlook-email reader |
| ~89 | the Outlook `.msg` reader |
| ~72 | the SQL parser |
| ~60 | Python itself, its standard library, and Windows DLLs |
| ~20 | Ripple's own screens |

**Not one of them is a file you typed.** Ripple's own Python — every phase in
this kit — is compiled and tucked inside the `.exe` itself, which is why you
cannot see it in there. The proof, if you want it: delete the whole output
folder and run `build.py` again. The same 1,770 files come back.

So the question "do I really have to write all that?" has a short answer: no.
You write about thirty Python files across the phases below. The packaging tool
supplies the rest, and re-supplies it every time you build.


**First, add the packaging tool.** One more install, and only on the machine that
does the building:

```
python -m pip install --user pyinstaller
```

**Why this is one short phase.** A packaged program has no folder of source files
around it, so anything that goes looking for a file has to ask where it is rather
than assume. There are three such places in Ripple and all three fail *silently* —
the program starts, looks healthy, and is wrong. They were dealt with when the
files were first written: `paths.py` in Phase 1 answers where the front end and the
database live, and `run.py` in Phase 8 hands uvicorn the app object rather than its
name. So nothing here goes back and edits anything. If any of that was skipped, go
back and fix it there rather than patching it now, or Phase 13 will appear to work
and the program will not.

````text
[PASTE THE CONTRACT CARD FIRST]

Ripple works when I run it with python run.py. Package it as a Windows program
with PyInstaller so it runs on a machine with no Python installed.

ripple/paths.py already answers where the front end and the database live when
running packaged, and run.py already passes uvicorn the app object rather than
the string "ripple.api:app". Do not change either. Do not change any other
file. I want build.py and nothing else.

--- build.py  (new, at the project root)

Run with: python build.py
It says what it is doing, runs PyInstaller, then checks the result itself.

Use exactly these arguments. Every one is here because leaving it out
produces a program that builds cleanly and then misbehaves:

  sys.executable, "-m", "PyInstaller", "run.py",
  "--name", "Ripple",
  "--noconfirm", "--clean",
  "--onedir",
  "--console",
  "--add-data", f"{WEB}{os.pathsep}web",
  "--collect-all", "sqlglot",
  "--collect-all", "extract_msg",

  --onedir, not --onefile. A one-file build unpacks itself into a temporary
    folder on every single launch, which makes it slow to start, and a
    locked-down Windows machine often refuses to run a program out of a
    temporary folder at all.
  --console for now. It leaves a plain window open beside the app showing the
    address, and showing the error if there is one. Put a line at the end of
    build.py saying that switching it to --noconsole gives a cleaner program
    once everything works, so I can find it again later.
  WEB MUST BE AN ABSOLUTE PATH. Build it as
    Path(__file__).resolve().parent / "web" and pass that. A relative "web"
    gets resolved against PyInstaller's own working folder rather than mine,
    and the build stops with "Unable to find ... web", which reads as a
    missing folder rather than a wrong path.
  --collect-all for both of those two. Each loads parts of itself by name at
    run time, which PyInstaller cannot see by reading the code. Without this
    they are silently left out and the program fails the first time it reads
    any SQL -- long after the build said it succeeded.

NAME WHAT YOU PRODUCE FOR ITS VERSION. One version number, written down in
exactly one place in the code, that the build script reads. The zip is called
Ripple-Offline-v1.1.0.zip, the release is tagged v1.1.0, and the settings screen
says Version 1.1.0 — three things that can never disagree because they are one
thing. A file called dist.zip is the same name for ever, so nobody can tell
which build they downloaded.

And do not commit it. Git keeps every version of every file for ever, which is
the exact opposite of "keep only the latest": forty builds of a 22 MB zip WERE
the whole repository, and a fresh clone paid for all forty. Write it into the
ignored dist/ folder and publish it to the releases page, keeping only the
newest one there.

Have build.py WRITE THE BUILD STAMP into the packaged folder — a small JSON
file holding the version, the commit if git can be asked, and the moment it was
packaged. Nothing inside a packaged folder can work this out for itself: an
executable has no git, and the file dates in there are the dates the files were
copied, which is true, useless, and impossible to tell apart from a real build
date. Without the stamp the settings screen falls back to that guess, and "it
does not work" goes on meaning "an old copy nobody replaced".

Then have build.py CHECK ITS OWN WORK rather than trust PyInstaller's exit
code:
  confirm dist/Ripple/Ripple.exe is really there
  confirm the build stamp is beside it and names a real date
  confirm the web folder was bundled, by finding index.html inside
    dist/Ripple/_internal/web
  print the total size of dist/Ripple in MB, and the full path to the .exe
  if PyInstaller failed, print the LAST part of its output, not a bare
    "failed" -- the real reason is usually the last three lines of a very
    long message, and the first three thousand lines are noise

Two things to guard, because both cost an evening:
  Rebuilding deletes the dist folder, and once the program has been run the
  history database is living in it. Before deleting, check for that database
  and if it exists and is not empty, say so and ask me to confirm rather than
  destroying saved analyses without a word.
  Windows will not delete a folder something is sitting in -- the last build
  still running, or a terminal whose current folder is inside it. PyInstaller
  fails there with a wall of traceback ending in WinError 32, which says none
  of that. Catch it and say it in plain words.

Python 3.10. Standard library only in build.py itself.
````

**Check it worked.** From `C:\ripple-build`:

```
python build.py
```

It takes a minute or two and ends by naming the folder it made. Then go to that
folder and double-click **Ripple.exe**. The browser should open on the same Ripple
you have been using. Walk one scan through it end to end — that is the only proof
that matters, because everything in this phase fails quietly rather than loudly.

Three things to check specifically, since these are the ones that break silently:

1. **The page is styled**, not blank and not plain text. Blank means the front end
   did not come along.
2. **Run a scan.** If it reports that it could not read any SQL, the parser was
   left out of the package.
3. **Save an analysis, close the program, open it again, and look at Past
   analyses.** Your saved analysis should still be there, and there should be a
   file next to `Ripple.exe` holding it.

**If Windows blocks it or quietly deletes it.** An unsigned program built on the
spot, which then opens a network port, is a shape that endpoint security is
designed to be suspicious of. If it is quarantined, that is not a bug in your
build, and the fix is not a setting you should go hunting for on your own — it is
a conversation with whoever runs security, who can allow it properly. Ripple runs
perfectly well as `python run.py` in the meantime.

---

## When the chat goes wrong

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

**It writes code for a newer Python than you have.** The giveaway is an error
mentioning a version, or a line the chat swears is fine. Reply: *"This is Python
3.10. Write it the 3.10 way."*

**It asks you to install something new.** Reply: *"Use only what is already
installed."* Every phase in this kit is buildable with the nine pieces from the
setup step, and an extra one is a habit rather than a need.

### The four replies worth keeping to hand

Most rounds of back-and-forth are one of these four. Paste the reply into the
same window rather than explaining it in your own words each time.

**It stopped mid-file.**
> *Continue from the last complete line. Do not start the file again from the
> top. Tell me the line you are resuming from.*

**It used a name that is not in the contract card.**
> *The card calls that X, not Y. Window 9 will be looking for X and will never
> know you renamed it. Use the card's name everywhere and give me the file
> again.*

**The tests all pass but look too easy.**
> *Would any of those tests fail if the behaviour were missing? Show me the one
> that catches it. If there is not one, add it.*

**Something failed when you ran it.** Paste the whole red block, and nothing
else except this:
> *This is what happened when I ran it. Do not guess at the cause -- tell me
> which line you think produced it and why, then give me the corrected file
> whole.*

---

## When your own machine goes wrong

These are not code problems, they are the four things that actually stop people.
Each looks like broken code and none of them is.

**"python is not recognized" or "pip is not recognized".** Windows was never told
where those live. Use `python -m pip` instead of `pip`, and if `python` itself is
not recognised, use the full path in quotes:
`"C:\Program Files\Python310\python.exe"`

**"No module named ripple", or "no tests ran".** You are standing in the wrong
folder. Every command in this kit runs from the project folder:

```
cd /d C:\ripple-build
```

**A file you definitely saved cannot be found.** It is almost certainly named
`config.py.txt` rather than `config.py`, because Notepad added the ending. This
lists what is really there, endings and all:

```
dir C:\ripple-build\ripple
```

If you see a `.txt` on the end, delete that file and save it again using the
two-command trick in *Saving a file the chat gives you* above.

**"Port 8000 is already in use".** A copy of Ripple is still running in another
Command Prompt window from earlier. Find that window and hold Ctrl and press C, or
close it.

