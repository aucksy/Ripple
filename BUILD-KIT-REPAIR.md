# Changing Ripple after it is built

You have a working Ripple. Something about it is wrong, or you want it to behave
differently. This kit tells you **which one file to put in front of Copilot** for
the thing you want to change, and **exactly what to say** so it gets the change
right the first time.

You do not need to be able to read Python. You need to be able to find a file,
copy what a chat gives you back, and run one command to check it still works.

**If you have not built Ripple yet**, this is the wrong document. Build it with
**BUILD-KIT.md** on a laptop that can install Python packages, or with
**BUILD-KIT-OFFLINE.md** on one that cannot. Come back here afterwards.

**This kit works for both builds.** Ripple's thinking lives in the same files
whether you built it on a normal laptop or on the locked-down one. Only the web
service and the start-up file are different, and where that matters it says so.

---

## The three rules. Break these and you will lose an evening.

**1. Copy the file before you change it.**
Right-click the file, Copy, then Paste in the same folder. Windows makes
`sqlread - Copy.py`. That copy is your way back. Delete it when the change has
worked for a week.

**2. One change at a time.**
Ask for one thing. Check it. Then ask for the next. Two changes in one window
and, when something breaks, you cannot tell which one did it.

**3. Run the checks before you believe it.**
Every change ends with a command. If it does not say `passed`, the change is not
done, whatever the chat told you.

---

## What Ripple is made of

Every file, what it decides, and how big it is. **You only ever open one of
these at a time.**

### The thinking — the same in both builds

| File | What it decides | Size |
|---|---|---|
| `ripple/config.py` | Every setting: which folder to scan, which SQL dialect, how many renames deep to follow, which folders to skip, the biggest file to open | 280 lines |
| `ripple/production.py` | **Which tables count as the ones your team publishes.** The most expensive setting in Ripple — a finding only counts as production impact if it ends at a table on this list | 535 lines |
| `ripple/catalog.py` | What tables and columns exist, learned by reading every `CREATE TABLE` in the repository | 93 lines |
| `ripple/scanner/repo.py` | **Which files get opened at all**, and what SQL is pulled out of a file that is not a `.sql` file — YAML, XML, shell scripts, Python | 832 lines |
| `ripple/scanner/templating.py` | Filling in `{{ }}` placeholders, and unwrapping scripting blocks so the SQL underneath can be read | 549 lines |
| `ripple/scanner/rescue.py` | BigQuery shapes the SQL parser refuses, rewritten into ones it accepts | 345 lines |
| `ripple/scanner/dialectcompat.py` | Reading the parse tree the same way whichever version of the SQL parser is installed | 98 lines |
| `ripple/scanner/sqlread.py` | **Reading SQL properly rather than matching words.** What each statement builds, what it reads, what each column leaves as, and every way a column is used | 3,573 lines |
| `ripple/scanner/lineage.py` | **Following a column through the pipeline**, and deciding what the answer means: the risk badge, what was covered, what was missed | 1,685 lines |
| `ripple/notification.py` | Reading the notification email, and the form you correct it on | 494 lines |
| `ripple/narrative.py` | **The summary and the reply letter**, written without any AI | 524 lines |
| `ripple/progress.py` | The line that says what Ripple is doing while you wait | 64 lines |
| `ripple/store.py` | Saved history of past analyses | 144 lines |
| `ripple/build_info.py` | The version number, and the build stamp on the settings screen | 197 lines |

### The screens — the same in both builds

| File | What it decides | Size |
|---|---|---|
| `web/app.js` | **Every screen.** All six steps, every card, every table, every word on them | 2,883 lines |
| `web/styles.css` | Colours, spacing, fonts | 346 lines |
| `web/index.html` | The empty page the screens are drawn into | 231 lines |

### The web service — this one is different in each build

| File | Build | What it decides |
|---|---|---|
| `ripple/api.py` | Normal laptop | Every web address the screens call, and the shape of what comes back |
| `ripple_offline/app.py` | Locked-down laptop | The same addresses, built on Python's own web server |
| `run.py` | Both | Starting it up |

### Only if you built the AI option

| File | What it decides |
|---|---|
| `ripple/ai.py` | The optional AI layer: reading the email at the front, writing the English at the back |
| `ripple/providers.py` | Which AI company a pasted key belongs to, worked out from the key itself |
| `ripple/scanner/github.py` | Reading a repository straight from GitHub instead of from a folder |

### Only in the packaged offline program

| File | What it decides |
|---|---|
| `ripple_offline/nonet.py` | The guard that stops anything reaching the internet |
| `ripple_offline/lifecycle.py` | The Close Ripple button and the automatic shutdown |
| `ripple_offline/prefs.py` | The settings file that sits beside the program |
| `ripple_offline/webbuild.py` | Building the offline screens out of the shared ones |
| `build.py` | Packaging the whole thing into a folder you can hand to somebody |

---

## "I want to change…" — which file to open

Find your row. Open that one file. Nothing else.

| What you want | The file |
|---|---|
| Which folder Ripple scans, which dialect, how deep it follows | `ripple/config.py` |
| Which table names count as published / production | `ripple/production.py` |
| A file type Ripple should open but does not — `.ipynb`, `.tf`, `.j2` | `ripple/scanner/repo.py` |
| SQL kept inside YAML, XML, a shell script or Python that is being missed | `ripple/scanner/repo.py` |
| A folder that should be skipped, or should stop being skipped | `ripple/config.py` |
| A `{{ placeholder }}` shape that is not being filled in | `ripple/scanner/templating.py` |
| A scripting block — `BEGIN`, `FOR`, `IF` — that is hiding the SQL underneath | `ripple/scanner/templating.py` |
| A statement the parser refuses and reports as unreadable | `ripple/scanner/rescue.py` |
| A rename that is not being followed | `ripple/scanner/sqlread.py` |
| A chain that stops one hop early, or does not start at all | `ripple/scanner/sqlread.py` |
| A usage that should be marked breaking and is not | `ripple/scanner/sqlread.py` |
| The risk badge being wrong | `ripple/scanner/lineage.py` |
| Something missing from "what this result does not cover" | `ripple/scanner/lineage.py` |
| A published table that should have been found, or should not have been | `ripple/scanner/lineage.py` |
| Wording in the reply letter or the summary | `ripple/narrative.py` |
| The email upload getting the tables or the date wrong | `ripple/notification.py` |
| Wording, layout or a card on any screen | `web/app.js` |
| Explaining something on screen without lengthening the page | `web/app.js` — the `why()` helper |
| Colours, spacing, anything visual | `web/styles.css` |
| A screen showing a blank where a number should be | **two files** — `ripple/scanner/lineage.py` and `web/app.js` |
| The version number on the settings screen | `ripple/build_info.py` |
| The progress line while you wait | `ripple/progress.py` |

**About that "two files" row.** A blank on screen almost always means the screen
is asking for something the engine never sent. Open `lineage.py` first and ask
whether the value is being put into the answer at all. Only go to `app.js` if it
is.

---

## The standing prompt

**Paste this first, in every window, before you say what you want.** It is what
stops Copilot rewriting half your file, inventing behaviour, or guessing at code
it has not read.

````text
You are changing one file of a working Python tool called Ripple. Ripple tells a
data team whether an upstream column change will break one of their published
tables. Its whole value is that when it says "no impact", that can be trusted.

HOW TO ANSWER ME
1. Read the file I have given you before you write anything.
2. If reading another file of mine would make your answer better or safer, ASK ME
   FOR IT BY NAME and wait. Do not guess at what is in it, and do not write code
   that depends on something you have not read. I would much rather paste a
   second file than get a confident wrong answer.
3. Tell me in plain English what you are going to change and what else it
   touches, and wait for me to say yes. I am a product manager, not a coder.
4. Then give me the COMPLETE new file, top to bottom, in one block I can copy.
   Not a patch. Not "...rest unchanged". The whole file.
5. Keep every comment that is already in the file unless the code it explains has
   gone. Those comments are the reason the tool behaves the way it does.
6. Give me one command that proves the change worked.

RULES YOU MAY NOT BREAK
* Change the least you can. If one line does it, change one line.
* Never remove something that reports a gap, a warning, or something Ripple could
  not read. Those are the whole product.
* Never make Ripple more confident than it was. If it cannot tell two things
  apart, it must follow both and say so, never pick one.
* Never invent a table, a column or a count that is not in the files being read.
* If what I am asking for would make Ripple quieter about something it does not
  know, say so and argue with me before you write it.
````

Then, underneath, in your own words: **what is wrong, and what you want instead.**

The more concrete the better. "The scan misses the table built in
`load_final.sql.j2` and I want that file read" beats "improve template support".

---

## A word about the check commands

Every card below ends with a command that proves the change worked. Those names
are the ones this kit's phases create.

**If a command says the file does not exist**, your copy names its tests something
else. Run `python -m pytest tests -q` instead. That runs everything and always
works — it is slower, and it is never wrong.

---

## The per-file cards

Each card gives you the extra sentences to add under the standing prompt for that
file. Paste the standing prompt, then the card, then say what you want.

---

### `ripple/config.py` — the settings

````text
This file holds every setting for Ripple. Nothing else in the tool may decide a
setting for itself, so a new option has to be added here first and read from here
everywhere else.

Before you change anything, tell me which other files read the setting I am
changing, and ask me for them if you need to see how they use it.

If you add a setting, it needs: a sensible default that works on a fresh machine,
and a note saying what happens if somebody sets it wrongly.
````
**Check it worked:** `python -m pytest tests -q` — a setting is read all over, so run everything.

---

### `ripple/production.py` — which tables are published

````text
This file decides which table names count as the ones my team publishes. It is the
most expensive setting in Ripple: a finding only counts as production impact if
the table it ends at is on this list. Too narrow and a real break is reported as
harmless. Too wide and every scan is full of noise.

It also reads a list somebody has pasted in - a messy paste, with bullets, heading
rows and ordinary prose mixed in - and has to say what it ignored and why.

Never make this quietly accept something it does not understand. A line it cannot
read must be reported, not dropped.
````
**Check it worked:** `python -m pytest tests/test_production.py -q`

---

### `ripple/scanner/repo.py` — which files get opened

````text
This file decides which files Ripple opens at all, and pulls SQL out of files that
are not .sql files - YAML, XML, shell scripts and Python.

Two rules here are easy to get backwards, so hold on to them:
* The list of file types Ripple does NOT report is written as a list of what is
  KNOWN not to be code - prose, images, packed data, binaries. Everything else it
  cannot open is counted and reported. That way a file type nobody thought of
  counts as a gap by default. Do not turn it round into a list of types to report.
* Pulling SQL out of a file must be anchored on something solid. Anchoring on a
  quote character means one apostrophe in a comment swallows the rest of the file.

If you add a way of finding a table name in a file, show me what your pattern does
NOT match, not only what it does. A pattern that is too loose invents tables that
do not exist, and that is worse than missing one.

This file also welds back together a statement a program wrote in pieces:

    sql  = "CREATE OR REPLACE TABLE final_published AS SELECT cm13 "
    sql += "FROM customer_demographics WHERE dt = @d"

Without that, the first piece is what gets mined - and the first piece PARSES,
because a SELECT with no FROM is valid. So nothing fails, nothing reaches the
check-by-hand list, and the scan reports no impact with complete coverage over a
job that really does rebuild the published table. Keep all four guards:
* Never weld across a comma. That is a LIST of separate queries.
* A plus-equals only joins to the variable the run before it was assigned to.
* A welded run must suppress the ordinary miner over the same characters, or
  every finding in it appears on screen twice.
* Blank triple-quoted regions before looking for pieces, to spaces of the same
  length, or a docstring welds itself onto whatever follows it.
````
**Check it worked:** `python -m pytest tests/test_repo.py -q`

---

### `ripple/scanner/templating.py` — placeholders and scripting blocks

````text
This file rewrites SQL on the way INTO the parser: it fills in {{ }} placeholders
and unwraps scripting blocks so the real SQL underneath can be read.

Two rules that everything here depends on:
* Every rewrite must keep the LINE NUMBERS exactly where they were. A finding
  points somebody at a line in their file, and if the rewriting moved the lines
  they are sent to the wrong one.
* A rewrite is done to a COPY on the way in. The file on disk is never changed and
  what the screen shows is always the real line as written.

A placeholder standing where a dataset name goes must come out as "not stated",
never as a guessed name.

Templating is also a small programming language, not only holes with names in
them. A file with an if/else in it, a set...endset block, or a placeholder alone
on its own line does not parse at all once the tags are blanked and every body
kept. So this file also RENDERS a template: it resolves the control flow, twice,
once taking every condition and once taking none.

Three things about that you must not take away:
* Both renderings are read, not the better one. Nothing in the file says which
  way it runs, and on a real warehouse 26 of 103 such files name DIFFERENT
  tables in their two branches. Picking one loses a source table in silence.
* A rendering is only ever tried on a file that ALREADY failed to parse. That is
  what stops a file that reads today from starting to read differently.
* Blanking a placeholder that stands alone on its line is tried LAST, because a
  source table written on its own line under a FROM is the same shape, and
  blanking that throws a real table away with nothing said.
````
**Check it worked:** `python -m pytest tests/test_templating.py -q`

---

### `ripple/scanner/rescue.py` — shapes the parser refuses

````text
This file rewrites BigQuery shapes the SQL parser will not accept into ones it
will. Same two rules as the templating file: it is done to a COPY on the way into
the parser, and every replacement must put back the line breaks it swallowed so
the line numbers still point at the right place.

If Ripple is reporting a statement as unreadable and you want it read, this is
where the fix goes. Do NOT work around a parse failure somewhere else in the tool.

Show me the shape before and after your rewrite, and confirm the line count is the
same.
````
**Check it worked:** `python -m pytest tests/test_sqlread.py -q` — rescued shapes are proved by the SQL-reading tests.

---

### `ripple/scanner/dialectcompat.py` — reading the parse tree safely

````text
This small file exists because the SQL parsing library renames the keys inside its
own nodes between major versions, and the renames are SILENT - the old key returns
nothing at all rather than complaining. Code that reads a renamed key keeps
running and quietly stops finding anything.

So every one of those keys is read through a helper in this file, and nothing
anywhere else in Ripple may read them directly.

If you add a helper here, add it to the test that checks every helper still
resolves against the installed version. That test is the only warning anybody gets
when the library changes underneath them.
````
**Check it worked:** `python -m pytest tests/test_parser_version.py -q`

---

### `ripple/scanner/sqlread.py` — reading the SQL

This is the biggest file in Ripple and the one everything rests on. **Expect
Copilot to ask you for other files. Give them to it.**

````text
This file reads SQL properly rather than matching words. It works out what each
statement builds, what it reads, what each column leaves the statement called, and
every way a column is used.

This file is large. Find the ONE function that decides the thing I am asking
about, change that, and leave the rest alone. Tell me which function you are
changing before you write anything.

Rules that hold this file together:
* Never read a parse-tree key directly. Every one that matters goes through the
  dialect-compatibility helper file. Ask me for that file if you need to see it.
* The table a statement writes to is left out of its own sources by node identity,
  never by comparing names. Two tables can share a short name.
* A UNION publishes EVERY branch under the FIRST branch's column names, by
  position. Merge the branches' select lists without lining the positions up and
  a column written in the second branch is followed under a name no downstream
  table can read, so the trail ends at the staging table and reports no
  production impact. Which branch somebody happened to type first then decides
  whether a real break is found. Only line them up when the branch has the same
  number of items as there are output names and no star is in the way.
* A loose name match is right for FOLLOWING a chain and catastrophic for RULING
  ONE OUT.
* When the SQL does not say which of two tables a column came from, keep the usage
  and mark it uncertain. Never drop it and never assert one of them.
* Check the shape of anything before you walk into it. The parsing library puts
  plain true/false values in some slots, and reaching into one of those takes down
  the whole file it was in.
````
**Check it worked:** `python -m pytest tests/test_sqlread.py -q`, then the whole set
with `python -m pytest tests -q`. A change in here reaches everything.

---

### `ripple/scanner/lineage.py` — following the column and judging the answer

````text
This file follows a column from the table it starts in to the tables my team
publishes, and then decides what the answer MEANS - the risk badge, what was
covered, and what was missed.

The rules here are the product, not decoration:
* Risk may never read "none" while there is a gap Ripple knows about on the thing
  being scanned. There is an "unknown" value for exactly that, and it shows on
  screen as "Not sure - needs a person".
* A confident claim may only be made where Ripple could look everywhere.
* Coverage is published as COUNTS, never a percentage. There is no honest way to
  say what share of a trail was seen.
* A caveat may never live on a different screen from the answer it qualifies.
* A published table that stops being REFRESHED is a different kind of harm from a
  column that changes, and must never be presented as the same one.

If you add anything to the answer, tell me whether the screen already knows how to
show it. If it does not, say so - I will need to change the screen file too.
````
**Check it worked:** `python -m pytest tests/test_lineage.py -q`, then the whole set
with `python -m pytest tests -q`.

---

### `ripple/narrative.py` — the summary and the reply letter

````text
This file writes the summary and the reply email with no AI at all. It runs
whenever there is no key, the key stops working, or nobody wants data leaving the
network. It must say exactly what the screens say.

The single most consequential sentence this tool writes is "Please proceed as
planned." It may only ever be written over a genuinely complete, genuinely clean
scan. Anything Ripple could not read, could not follow, could not reach, or is of
a file type it does not open means that sentence must not appear.

Every fact in the letter has to come off the scan result. Never write a number or
a table name that is not in it.
````
**Check it worked:** `python -m pytest tests/test_narrative.py -q`

---

### `ripple/notification.py` — reading the email

````text
This file reads the notification: an uploaded .eml, .msg or .txt file, or what I
type into the manual form.

Extraction never has the last word. Whatever it works out lands on a form I can
correct before anything is scanned, and anything it was unsure about has to be
visible on that form rather than silently accepted.

If a file cannot be read properly, say so on screen and point at the alternative.
Half-reading one and carrying on is the one thing this must not do.
````
**Check it worked:** `python -m pytest tests/test_notification.py -q`

---

### `web/app.js` — every screen

````text
This one file draws every screen in Ripple: all six steps, every card, every
table, every word on them.

It is large, so find the ONE function that draws the thing I am asking about and
change that. Tell me which one before you write anything.

Rules for anything on screen:
* Nothing may be shown that is not real. No invented counts, no progress bar that
  moves while nothing is happening, no link that goes nowhere, no empty coloured
  box.
* Coverage is shown as counts, never a percentage.
* A card that reports a gap may only appear when there IS one. A warning printed
  on every scan is one nobody reads.
* A reassuring message may not appear while any gap is known.
* Say the fact on the page and put the reasoning behind the information button.
  There is ONE of those, `why(fact, label, ...explanation)`, near the top of this
  file. Call it. Do not write a second one, and never use a title= tooltip: it
  cannot be opened on a touch screen, cannot be reached from a keyboard, and
  disappears while it is being read.
* Never behind that button: a count, a table name, or a warning that something
  was not read. Somebody who never presses it must still see everything Ripple
  knows it missed — they lose the reasoning, never the fact. The test that holds
  this is `Codebase/tests/test_screen_details.py`, which blanks out every
  explanation panel and then looks for each count in what is left.
* A long list is capped in the drawing, never in the analysis, and what was
  dropped is named with its count.

If the value you need is not in the scan result, STOP and tell me. Do not invent
it and do not calculate it in the screen. It has to come from the engine.

This file is shared by both builds of Ripple, so anything you change here shows up
in both.
````
**Check it worked:** `node --check web/app.js`, then the same check on the
GENERATED offline bundle — a change that breaks only that one is invisible
otherwise. Then open Ripple and LOOK at the screen you changed: read it as a
stranger and look for two things on one page that cannot both be true. That is
how the last four defects here were found, and no test would have caught any of
them.

---

### `ripple/api.py` (normal laptop) or `ripple_offline/app.py` (locked-down)

````text
This file is the web service: every address the screens call, and the exact shape
of what comes back. It is thin on purpose - each route is a few lines that call
the thinking files. All the thinking lives in those, so the same logic runs from a
test, from the command line, or from here.

IMPORTANT: there are TWO of these files, one per build, and they both feed the
SAME screen file. The health route in particular is duplicated rather than shared.
If you add something the screen reads, it has to go into BOTH or the other build
silently shows a blank where this one shows a number. Ask me for the other file
before you change this one.

Do not move any thinking into this file. If a route needs a decision made, that
decision belongs in the file that owns it.
````
**Check it worked:** start Ripple and click through the screen that uses the route.
On the locked-down build there is also `python -m pytest tests/test_api.py -q`.

---

### `ripple/build_info.py` — the version and the build stamp

````text
This file holds ONE version number. The release tag, the packaged file's name and
the line on the settings screen all read it from here. Nothing anywhere else may
write a version.

Raise it whenever behaviour changes, so that "it does not work" can be told apart
from "that was fixed, on a copy nobody installed".
````
**Check it worked:** start Ripple, open Settings & checks, and read the line. It has
to match the number you just typed.

---

## On the locked-down laptop, the check commands look different

That build has no `pytest`. Every check command in this kit translates the same
way, every time:

| This kit says | On the locked-down laptop, type |
|---|---|
| `python -m pytest tests/test_repo.py -q` | `python -m unittest tests.test_repo -v` |
| `python -m pytest tests/test_lineage.py -q` | `python -m unittest tests.test_lineage -v` |

Drop the `.py`, swap the slash for a dot, `-v` instead of `-q`. **Run it from the
project folder**, the one holding `run.py` — that is how Python finds the SQL
parser sitting beside your code. Run it from anywhere else and it fails with
"No module named sqlglot", which looks like a broken change and is not.

If your change touched more than one test file, list them one after another:
`python -m unittest tests.test_repo tests.test_lineage -v`

---

## Things you must not let Copilot take away

Ripple's worth comes from what it admits, not only from what it finds. Every one
of these is load-bearing. If a chat offers to "simplify" or "tidy" one of them,
say no.

- The question before a scan starts asking you to confirm what will be searched.
- The "check by hand" list and the count beside it.
- The "never opened" card.
- The "mentions only" list — names that appear but carry nothing.
- The per-attribute panel showing what came back for each column you asked about.
- The "table not stated" marker.
- The labels saying which words were written by AI and which by rules.
- "Trails cut short" — chains still running when Ripple hit its own limit.
- "Tables not fully readable" and "column list not visible".
- The merged-table-names card and the wildcard card.
- The COPY / CLONE / LIKE / RENAME labels that use the word the file itself uses.
- The section for published tables that stop being refreshed.
- The build stamp on the settings screen.
- The "named after their file" card and the "built from scratch in more than one
  file" card.
- The "not read because of the folder" card and the file-types-not-opened tally.
- The standing footer: "Ripple read these N files and nothing else."
- The "run as text" card and its row badge.
- The "named here, but carries it nowhere" card.
- The deliveries-out-of-the-warehouse card and its number.
- The "column not found" headline that lists the columns Ripple *did* see.
- The "how much of this Ripple could see" card.

**The test.** Before you accept a change, ask yourself: *does Ripple now say "no
impact" in a situation where it used to hedge?* If yes, and you did not
deliberately ask for that, the change is wrong however good the reason sounded.

---

## When it goes wrong

**Copilot gave me a piece of a file, not the whole thing.**
Say: *"Give me the complete file from the first line to the last, in one block. I
cannot patch it by hand."*

**It changed things I did not ask about.**
Say: *"Go back to the file I gave you and change only <the one thing>. Leave every
other line exactly as it was, including the comments."*

**It says it needs a file I do not know how to find.**
Every file in this kit's tables is under your Ripple folder. `ripple/api.py` means
the `ripple` folder, then `api.py`. `web/app.js` means the `web` folder, then
`app.js`.

**The check command failed and I do not understand the message.**
Paste the whole message back into the same chat window and say: *"This is what the
check printed. Fix the file, and give me the complete file again."* Do not start a
new window — it has lost everything it knew about your file.

**It has gone in circles three times.**
Stop. Put your backup copy back, and start a fresh window with the standing prompt
and a more concrete description of the problem. A fresh window with a good
description beats a tired one every time.

**Everything is broken and I want out.**
Delete the file you changed. Rename `<name> - Copy.py` back to `<name>.py`. Run
the check command. You are exactly where you started.

---

## Before you tell anybody it is fixed

1. The check command for that file says `passed`.
2. Run the whole set — `python -m pytest tests -q` — and it still says `passed`.
3. Open Ripple and do the thing you changed, with your own eyes, on a real
   repository.
4. If it was a screen change, look at the screen. A change that compiles has never
   proved a screen looks right.
5. Raise the version number in `ripple/build_info.py`, so the settings screen can
   tell this copy apart from the one before it.
