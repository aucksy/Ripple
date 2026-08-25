# Run Ripple here — on a machine where nothing installs

**What this is.** Every file of Ripple, handed over whole. Same as
`RUN-RIPPLE-HERE.md`, with one difference that changes everything: this one is
for a machine where `pip install` does not work.

**Try the other file first.** Run this:

````
python -m pip install sqlglot==30.17.0
````

If that succeeds, close this file and use `RUN-RIPPLE-HERE.md`. It is shorter,
it needs nothing copied, and it gives you the whole product including the AI
email reader. Only carry on here if pip genuinely cannot reach anything.

---

## What is different here, and what it costs

This build reaches the network nowhere. Three things follow:

* **The web service is Python's own `http.server`**, not FastAPI, because FastAPI
  is an install. Same addresses, same JSON, same screens.
* **There is no AI email reader and no "download a repository" button.** Both
  need a network. The screens here do not have them — not greyed out, not
  broken: absent.
* **There is a settings screen the other build does not have**, for choosing the
  folder and the SQL dialect on screen rather than in environment variables.

Everything else is the same Ripple, and the answers are the same answers.

---

## The one thing that must be copied

`sqlglot` is the SQL parser — 183 files, 2.7 MB. It is what makes Ripple more
than a word search, no chat can write it, and pasted through a chat window it is
about seventy-five pastes. **It has to arrive as files**, in a folder called
`sqlglot` sitting beside `run.py`.

`BUILD-KIT-OFFLINE.md` has a whole section on getting it there — an internal
company mirror, the source zip from GitHub, a copy from a colleague's machine.
Read Phase 0 of that file first. Nothing below works without it.

---

## Read this before you start

**No Python file builds the screens.** Every screen, every card and every word
lives in `web/app.js`, which is JavaScript. `web/styles.css` holds the colours.
Python only serves those files and hands them the numbers.

**Fonts are not included here.** The other kit carries them as text. This one
does not, so the screens use whatever Segoe UI and Consolas the machine has:
same layout, same colours, same spacing, slightly different letterforms.

---

## First: the empty files

Before anything else, create these. They are empty — nothing goes in them — and
there is no paste for them below for that reason.

````
    ripple/__init__.py
    ripple/scanner/__init__.py
````

In a Command Prompt, from the folder you are building in:

````
type nul > ripple\__init__.py
type nul > ripple\scanner\__init__.py
````

Nothing is printed and nothing happens on screen. That is correct.

**Do not skip them because everything works without them.** It does. That is
exactly what makes them worth the two commands.

Leave them out and Python still imports Ripple perfectly happily — as a
"namespace package", which is a package assembled out of EVERY folder called
`ripple` it can find, merged together. Measured: with the empty file, `ripple`
is one folder and a decoy folder elsewhere on the path cannot get in. Without
it, `ripple` spans two folders and a module from the decoy imports as though it
were Ripple's own.

Nothing errors. Nothing warns. On a laptop that has ever had another copy of
Ripple, or a folder called `ripple` belonging to something else, the answer on
screen comes partly from code that is not in the folder you are looking at —
which is the one failure this whole tool exists to make impossible.

---


## What you are pasting

| File | What it decides | Lines | Pieces |
|---|---|---|---|
| `ripple/__init__.py` | the engine | 0 | empty file |
| `ripple/build_info.py` | the engine | 197 | 1 |
| `ripple/catalog.py` | the engine | 93 | 1 |
| `ripple/config.py` | the engine | 314 | 1 |
| `ripple/narrative.py` | the engine | 528 | 1 |
| `ripple/notification.py` | the engine | 494 | 1 |
| `ripple/production.py` | the engine | 535 | 1 |
| `ripple/progress.py` | the engine | 64 | 1 |
| `ripple/providers.py` | the engine | 142 | 1 |
| `ripple/store.py` | the engine | 144 | 1 |
| `ripple/scanner/__init__.py` | reading the repository and following the column | 0 | empty file |
| `ripple/scanner/dialectcompat.py` | reading the repository and following the column | 138 | 1 |
| `ripple/scanner/lineage.py` | reading the repository and following the column | 1,726 | 3 |
| `ripple/scanner/repo.py` | reading the repository and following the column | 964 | 2 |
| `ripple/scanner/rescue.py` | reading the repository and following the column | 345 | 1 |
| `ripple/scanner/sqlread.py` | reading the repository and following the column | 3,720 | 5 |
| `ripple/scanner/templating.py` | reading the repository and following the column | 681 | 1 |
| `ripple_offline/folderpick.py` | the wrapper | 51 | 1 |
| `ripple_offline/lifecycle.py` | the wrapper | 167 | 1 |
| `ripple_offline/nonet.py` | the wrapper | 122 | 1 |
| `ripple_offline/paths.py` | the wrapper | 52 | 1 |
| `ripple_offline/prefs.py` | the wrapper | 297 | 1 |
| `ripple_offline/synced.py` | the wrapper | 89 | 1 |
| `ripple_offline/__init__.py` | written for this build, not copied | 16 | 1 |
| `ripple_offline/engine.py` | written for this build, not copied | 88 | 1 |
| `ripple_offline/app.py` | written for this build, not copied | 511 | 1 |
| `ripple_offline/webserver.py` | written for this build, not copied | 287 | 1 |
| `run.py` | written for this build, not copied | 172 | 1 |
| `tests/test_smoke.py` | written for this build, not copied | 178 | 1 |
| `web/index.html` | the empty page the screens are drawn into | 206 | 1 |
| `web/styles.css` | every colour, size and spacing rule | 396 | 1 |
| `web/app.js` | every screen, every card, every word | 3,250 | 5 |

**15,967 lines in 25 pastes.** Do them in the order below.
Where a file is split, the pieces MUST go one after another into the SAME file —
piece 2 goes on the end of piece 1, never into a new file.

---

## How to say it to the chat

Paste this once, at the top, before the first piece:

````text
I am going to paste some files in pieces. Each piece says which file it belongs
to and whether it starts that file or continues it.

Write them out exactly as given. Do not reformat, do not re-indent, do not
"improve" anything, do not add or remove comments, do not change quote marks,
and do not shorten anything with a comment saying the rest is unchanged. If a
piece looks like it was cut off mid-way, that is correct -- the next piece
continues it.

If you cannot write the whole piece, say so and stop. Do not summarise it.
````

That last line matters. A chat asked for a long file will sometimes write half
of it and put `# ... rest unchanged ...` in the middle, which produces a file
that looks finished and is not. The check at the bottom catches it.

---


## The pieces

## Paste 1 of 25 — 3 files

### ripple/build_info.py

Create the file `ripple/build_info.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Which build of Ripple is this one?

Nothing on any screen said. "It does not work" has more than once turned out to
be "that was fixed a while ago, on a copy that was never installed", and there
was no way at all to tell those two apart without reading the code.

So: one line, on the settings screen and in ``/api/health``, saying which build
is running.

Where the answer came from matters as much as the answer, and the two are never
allowed to look the same. A commit hash read out of git is a fact. The date of
the newest file in the folder is a guess -- it moves when anything is touched,
and it says nothing about whether that change was ever installed anywhere. So
each is labelled for what it is, and a guess always says so out loud.

Four places to look, best first:

* a stamp file written into the packaged folder at build time -- the only thing
  that can tell one copy of the executable from another, because an executable
  has no git and no source dates worth reading;
* the host's own environment, which is how Vercel says which commit it deployed;
* git, when Ripple is being run from the repository it lives in;
* the dates on its own files, which is a guess, and says so.
"""
from __future__ import annotations

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# The one version number, and the only place it is written down. The build
# script reads it from here to name what it produces, so the filename, the
# release tag and the line on the settings screen can never disagree.
#
# Bump it whenever behaviour changes. Three parts: break.feature.fix.
VERSION = "1.8.1"

# Written into the packaged folder by the offline build script. Kept as a
# constant because two files have to agree on the name.
STAMP_FILE = "BUILD-STAMP.json"

_PKG = Path(__file__).resolve().parent          # .../Codebase/ripple
_ROOT = _PKG.parent                             # .../Codebase

_cached: dict | None = None


def _places_to_look() -> list[Path]:
    """Folders a stamp file could be sitting in."""
    out = [_PKG, _ROOT]
    if getattr(sys, "frozen", False):
        out.append(Path(sys.executable).resolve().parent)
        bundled = getattr(sys, "_MEIPASS", "")
        if bundled:
            out.append(Path(bundled))
    return out


def _from_stamp_file() -> dict | None:
    for folder in _places_to_look():
        f = folder / STAMP_FILE
        try:
            if not f.is_file():
                continue
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict) and data.get("built"):
            return {
                "commit": str(data.get("commit") or ""),
                "built": str(data["built"]),
                "from": "build",
            }
    return None


def _from_env() -> dict | None:
    """How a host says which commit it deployed. Vercel sets the first of these."""
    sha = os.environ.get("VERCEL_GIT_COMMIT_SHA") or os.environ.get("RIPPLE_BUILD_COMMIT")
    if not sha:
        return None
    return {
        "commit": sha[:7],
        "built": os.environ.get("RIPPLE_BUILD_DATE", ""),
        "from": "host",
    }


def _from_git() -> dict | None:
    """The commit this working copy is actually on."""
    if not any((p / ".git").exists() for p in (_ROOT, _ROOT.parent)):
        return None
    try:
        done = subprocess.run(
            ["git", "log", "-1", "--format=%h|%cI"],
            cwd=str(_ROOT), capture_output=True, text=True, timeout=5,
        )
    except Exception:
        return None
    if done.returncode != 0 or "|" not in done.stdout:
        return None
    commit, when = done.stdout.strip().split("|", 1)
    commit = commit.strip()
    # A commit hash is only the truth about this copy if nothing has been edited
    # since. Left unmarked, a build made from a working copy with changes in it
    # claims to be the commit it is not, which is the exact confusion this whole
    # file exists to remove.
    if _has_edits():
        commit += "+edits"
    return {"commit": commit, "built": when.strip(), "from": "git"}


def _has_edits() -> bool:
    """Has anything been changed since that commit?"""
    try:
        done = subprocess.run(["git", "status", "--porcelain"],
                              cwd=str(_ROOT), capture_output=True, text=True, timeout=5)
    except Exception:
        return False
    return done.returncode == 0 and bool(done.stdout.strip())


def _from_file_dates() -> dict:
    """The newest of Ripple's own files. A guess, and labelled as one."""
    newest = 0.0
    folders = [(_PKG, "*.py"), (_ROOT / "web", "*")]
    for folder, pattern in folders:
        if not folder.is_dir():
            continue
        for f in folder.rglob(pattern):
            if "__pycache__" in f.parts or not f.is_file():
                continue
            try:
                newest = max(newest, f.stat().st_mtime)
            except OSError:
                continue
    when = datetime.fromtimestamp(newest).isoformat(timespec="seconds") if newest else ""
    return {"commit": "", "built": when, "from": "files"}


def _day(iso: str) -> str:
    """A date somebody can read, out of whatever shape the stamp is in."""
    if not iso:
        return ""
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%d %b %Y")
    except ValueError:
        return iso[:10]


def _label(info: dict) -> str:
    """The one line the screen shows. Says plainly when it is a guess."""
    bits = [f"Version {info['version']}"]
    if info["commit"]:
        bits.append(info["commit"])
    day = _day(info["built"])
    if info["from"] == "files":
        bits.append(f"newest file {day}" if day else "no build date")
        bits.append("no build record — this is a guess")
    elif day:
        bits.append(f"built {day}")
    return " · ".join(bits)


def build_info() -> dict:
    """Which build this is. Worked out once and kept -- it cannot change while
    the program is running, and ``/api/health`` is asked on every screen."""
    global _cached
    if _cached is None:
        found = _from_stamp_file() or _from_env() or _from_git() or _from_file_dates()
        info = {"version": VERSION, **found}
        info["label"] = _label(info)
        _cached = info
    return dict(_cached)


def write_stamp(folder: Path, commit: str = "", built: str = "") -> Path:
    """Record which build this is, into a folder being packaged.

    Called by the offline build script. Without it the executable falls back to
    file dates, which in a packaged folder are the dates the files were copied
    -- true, useless, and indistinguishable from a real build date.
    """
    if not built:
        built = datetime.now().astimezone().isoformat(timespec="seconds")
    if not commit:
        found = _from_git()
        commit = found["commit"] if found else ""
    out = folder / STAMP_FILE
    out.write_text(
        json.dumps({"version": VERSION, "commit": commit, "built": built}, indent=2),
        encoding="utf-8",
    )
    return out
````

### ripple/catalog.py

Create the file `ripple/catalog.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""What tables and columns exist, learned from the repository itself.

This is the "mock database" for the demo: rather than being handed a data
dictionary, Ripple reads every CREATE TABLE it can find and builds one. The
same code works against a real repository -- and whatever it cannot read shows
up as a gap rather than silently shrinking the catalogue.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from sqlglot import exp

from .scanner.sqlread import ParsedRepo, short_name


@dataclass
class Catalog:
    tables: dict[str, list[str]] = field(default_factory=dict)   # TABLE -> [COLUMN, ...]
    defined_in: dict[str, str] = field(default_factory=dict)     # TABLE -> file
    gaps: list[dict] = field(default_factory=list)

    def has_table(self, name: str) -> bool:
        return (name or "").upper() in self.tables

    def columns(self, table: str) -> list[str]:
        return self.tables.get((table or "").upper(), [])

    def has_column(self, table: str, column: str) -> bool:
        return (column or "").upper() in {c.upper() for c in self.columns(table)}

    def to_dict(self) -> dict:
        return {
            "tables": self.tables,
            "definedIn": self.defined_in,
            "gaps": self.gaps,
            "tableCount": len(self.tables),
            "columnCount": sum(len(v) for v in self.tables.values()),
        }


def build_catalog(parsed: ParsedRepo) -> Catalog:
    cat = Catalog()
    for stmt in parsed.statements:
        expr = stmt.expr
        if not isinstance(expr, exp.Create):
            continue
        schema = expr.this
        # CREATE TABLE x (col type, ...) -- an explicit column list
        if isinstance(schema, exp.Schema):
            table = schema.this.name if isinstance(schema.this, exp.Table) else None
            cols: list[str] = []
            for d in schema.expressions:
                if isinstance(d, exp.ColumnDef):
                    cols.append(d.this.name)
            if table and cols:
                cat.tables[table.upper()] = cols
                cat.defined_in[table.upper()] = stmt.file
                continue
            if table:
                cat.gaps.append(
                    {"table": table, "file": stmt.file,
                     "reason": "created without a readable column list"}
                )
                continue
        # CREATE TABLE x AS SELECT ... -- columns come from the query
        #
        # Keyed on the table's own name, without the dataset. What asks this
        # catalogue anything is the notification, and a notification names a
        # table the way a person writes one down.
        target = short_name(stmt.target) if stmt.target else None
        if target and stmt.select is not None:
            cols = []
            for e in stmt.select.expressions:
                if isinstance(e, exp.Star):
                    cols = []
                    # Not a dead end. A scan follows the column straight through
                    # a star and marks the steps past it as inferred; this note
                    # says what the catalogue is missing, not what the scan is.
                    cat.gaps.append(
                        {"table": target, "file": stmt.file,
                         "reason": "built with SELECT * - a scan follows your column through it, "
                                   "but the column names it publishes are not written down"}
                    )
                    break
                if isinstance(e, exp.Alias):
                    cols.append(e.alias)
                elif isinstance(e, exp.Column):
                    cols.append(e.name)
            if cols:
                cat.tables.setdefault(target.upper(), cols)
                cat.defined_in.setdefault(target.upper(), stmt.file)
    return cat
````

### ripple/config.py

Create the file `ripple/config.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Settings for a Ripple installation.

Everything that would differ between a laptop, a demo host and a real corporate
network lives here, so nothing has to be hunted for in code.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from . import providers
from .production import (           # noqa: F401  (re-exported for older callers)
    DEFAULT_PRODUCTION,
    DEFAULT_TEXT as DEFAULT_PRODUCTION_TEXT,
    ProductionRule,
    parse as parse_production_text,
    parse_production_rule,
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Which tables are the ones this team publishes -- the tables a finding has to
# reach before anybody outside the team notices. Every organisation names them
# differently, and getting this wrong is the most expensive mistake Ripple can
# make: a change that really breaks three tables is reported as "no impact"
# purely because the tables are not called _PROD. So it is a setting, it is on
# screen, and findings that reach nothing on this list are still shown.
#
# Two shapes are accepted, side by side. A pasted list of the real table names
# is read as written -- that is the answer rather than a guess about it. A
# pattern is still a pattern, unchanged: a word beginning with an underscore
# matches the end of a table name (_PROD, _UMDL, _PUBLISHED), and one with a *
# is matched in full, so PROD_* works too and * on its own means every table.
# See ripple/production.py for how a paste is read.

# Which model Ripple asks, when a key has been given.
#
# There is no list of model names in this file any more. A hand-typed list is
# wrong within months, and then it tells somebody a model exists that does not
# -- which they discover at the moment they are trying to read an email. The
# list is fetched from whichever provider issued the key, which produces the
# real names and proves the key in the same call. See ripple/providers.py.
#
# The job is narrow: pull table and attribute names out of a forwarded, badly
# quoted email and return strict JSON, then write a few careful sentences from
# findings that are already worked out. That rewards instruction-following
# rather than breadth, so the preference order in providers.py leans towards
# the larger models, and any model the provider offers can still be chosen.


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default).strip()


def _env_any(names: tuple[str, ...], default: str = "") -> str:
    """First of several environment variables that is actually set."""
    for n in names:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return default


def _serverless() -> bool:
    return bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))


def _default_db() -> str:
    if os.environ.get("RIPPLE_DB"):
        return os.environ["RIPPLE_DB"].strip()
    return "/tmp/ripple.db" if _serverless() else str(BASE_DIR / "ripple.db")


@dataclass
class Settings:
    # ── is this a serverless host? ─────────────────────────────────────────
    # Vercel, Lambda and friends impose limits a laptop does not: the disk is
    # read-only apart from /tmp, the machine is thrown away between requests,
    # a request body cannot exceed about 4.5 MB, and a request is killed at
    # 60 seconds. Several defaults below change because of that, so the app
    # says what it will really do instead of promising laptop behaviour.
    serverless: bool = field(default_factory=_serverless)

    # ── where the code comes from ──────────────────────────────────────────
    # "folder" reads a directory on this machine. "github" pulls a repository
    # over the network with an access token. Either can be chosen on screen.
    repo_source: str = field(default_factory=lambda: _env("RIPPLE_REPO_SOURCE", "folder"))

    # ── which repository is scanned (folder mode) ──────────────────────────
    repo_path: Path = field(
        default_factory=lambda: Path(_env("RIPPLE_REPO", str(BASE_DIR / "mockrepo")))
    )
    repo_label: str = field(default_factory=lambda: _env("RIPPLE_REPO_LABEL", "mockrepo"))
    repo_branch: str = field(default_factory=lambda: _env("RIPPLE_REPO_BRANCH", "main"))

    # ── GitHub mode ────────────────────────────────────────────────────────
    # The token is a secret. It is only ever sent to GitHub as a header; it is
    # never logged, never saved to disk, and never returned by any route.
    github_repo: str = field(default_factory=lambda: _env("RIPPLE_GITHUB_REPO", ""))
    github_branch: str = field(default_factory=lambda: _env("RIPPLE_GITHUB_BRANCH", ""))
    github_token: str = field(
        default_factory=lambda: _env_any(("RIPPLE_GITHUB_TOKEN", "GITHUB_TOKEN"))
    )
    github_api: str = field(default_factory=lambda: _env("RIPPLE_GITHUB_API", "https://api.github.com"))
    github_timeout: float = field(default_factory=lambda: float(_env("RIPPLE_GITHUB_TIMEOUT", "30")))
    # How much compressed repository Ripple will pull in one go. Lower on a
    # serverless host, where the whole request is killed at 60 seconds: a clear
    # "that repository is too big for this host" beats a blank timeout.
    max_repo_bytes: int = field(
        default_factory=lambda: int(
            _env("RIPPLE_MAX_REPO_BYTES", "25000000" if _serverless() else "60000000")
        )
    )

    # Link template so a finding can jump to the real file. {path} and {line}
    # are filled in. Point this at your own Git host when you get there.
    repo_url_template: str = field(
        default_factory=lambda: _env("RIPPLE_REPO_URL_TEMPLATE", "")
    )

    # ── how the SQL is read ────────────────────────────────────────────────
    # One of: oracle, teradata, snowflake, hive, spark, postgres, mysql, tsql,
    # duckdb, bigquery, redshift, databricks, presto, trino, sqlite, "" (generic).
    sql_dialect: str = field(default_factory=lambda: _env("RIPPLE_SQL_DIALECT", ""))

    # How many renames deep to follow a column.
    #
    # This was 4, and 4 was measured to be wrong for the pipeline Ripple was
    # built for. That pipeline runs source -> foundation -> tmp -> run_datetime
    # -> union -> stage -> entity -> published, which is eight hops before a
    # published table is reached at all, and further again to the reports built
    # on top of it. On a generated repository of that exact shape, a limit of 4
    # found NO production tables; 8 found all of them; 10 finished every trail
    # with nothing left cut short. The cost of the change was 0.21s to 0.32s on
    # that repository -- a scan is dominated by looking up statements, not by
    # how deep it goes.
    #
    # A limit that is too low does not fail loudly. It reports "the chain ends
    # here and does not reach production", which is a sentence about this
    # number wearing the clothes of a sentence about the warehouse.
    #
    # ZERO means follow the trail until the CODE runs out, and that is now the
    # default. Ten was still a wall, just a further-off one, and the screen's
    # offer to follow twice as far did not get past it either: measured on a
    # 36-hop chain, ten renames cut the trail short, twenty cut it short, and
    # twenty-five -- the deepest the screen would offer -- cut it short as well.
    # There was no number a person could choose that produced an answer, and
    # every attempt cost another whole scan to be told the same thing.
    #
    # This is safe because the walk already carries a set of every
    # (table, column) it has been through, so a ring of tables closes on itself
    # whatever this is set to. The counter was a second guard that could only
    # ever truncate a real answer. Measured on a real BigQuery warehouse of
    # 7,304 files: following to the end costs 10.6s against 10.5s at ten hops,
    # for the same tables plus the ones that were past the limit.
    #
    # A limit somebody sets on purpose is still obeyed, and a trail stopped by
    # it is still reported as stopped rather than as a chain that ended.
    max_hops: int = field(default_factory=lambda: int(_env("RIPPLE_MAX_HOPS", "0")))

    # Which tables count as the ones this team publishes. See the note at the
    # top of this file for why this is a setting and not a constant.
    #
    # Two fields, and both matter. ``production_patterns`` is what is matched
    # against: every entry Ripple recognised, whether a real table name or a
    # pattern. ``production_text`` is what was actually pasted, kept exactly as
    # it arrived so the box can be opened and edited again rather than being
    # handed back a tidied-up version of somebody's list.
    #
    # There is no default any more, and that is deliberate. Whoever deploys a
    # hosted copy can still set RIPPLE_PROD_TABLES; on a copy where nobody has,
    # this is empty, and empty means NOT GIVEN rather than "nothing is
    # published". See set_production and has_production.
    production_patterns: tuple[str, ...] = field(
        default_factory=lambda: parse_production_rule(_env("RIPPLE_PROD_TABLES", ""))
    )
    production_text: str = field(
        default_factory=lambda: _env("RIPPLE_PROD_TABLES", "")
    )

    # File types worth reading at all.
    #
    # ``.sqlx`` is Dataform -- Google's own tool for building BigQuery pipelines,
    # and the one most likely to be in a BigQuery repository after dbt. A .sqlx
    # file is an ordinary SELECT with a ``config { }`` block on top, and it was
    # not opened, not counted and not mentioned: `indexed False, risk none,
    # prod []`, with nothing anywhere recording that the file existed.
    code_extensions: tuple[str, ...] = (
        ".sql", ".sqlx", ".ddl", ".hql", ".py", ".scala", ".java", ".sh",
        ".xml", ".yaml", ".yml",
    )
    # Never walk into these.
    skip_dirs: tuple[str, ...] = (
        ".git", ".venv", "venv", "node_modules", "__pycache__", "target", "build", "dist",
    )
    max_file_bytes: int = 2_000_000

    # The biggest email file that can be uploaded. A serverless host refuses a
    # request body over roughly 4.5 MB before Ripple ever sees it, so the limit
    # on screen has to be the real one, not a friendlier invented one.
    max_upload_bytes: int = field(
        default_factory=lambda: int(
            _env("RIPPLE_MAX_UPLOAD_BYTES", "4000000" if _serverless() else "25000000")
        )
    )

    # ── AI (entirely optional) ─────────────────────────────────────────────
    # One key, whoever issued it. Which provider it belongs to is worked out
    # from the key itself rather than asked for -- see ripple/providers.py.
    #
    # The old GROQ_* names are still read, because they are set on a running
    # host and silently ignoring them would turn the AI off without a word.
    ai_key: str = field(default_factory=lambda: _env_any(
        ("RIPPLE_AI_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
         "GOOGLE_API_KEY", "GROQ_API_KEY")))
    # Empty means "whichever the provider recommends", worked out on connect
    # from the list it actually returns.
    ai_model: str = field(default_factory=lambda: _env_any(("RIPPLE_AI_MODEL", "GROQ_MODEL")))
    # Only for a proxy or a provider Ripple does not know. Left empty, the
    # address comes from whichever provider issued the key.
    ai_base_url: str = field(default_factory=lambda: _env_any(
        ("RIPPLE_AI_BASE_URL", "GROQ_BASE_URL")))
    # How long to wait for the model. Writing the summary makes two calls one
    # after the other, so on a serverless host both have to finish inside the
    # 60-second cap -- otherwise the page dies with no explanation instead of
    # falling back to the written-without-AI version.
    ai_timeout: float = field(
        default_factory=lambda: float(_env("RIPPLE_AI_TIMEOUT", "20" if _serverless() else "45"))
    )

    # ── storage ────────────────────────────────────────────────────────────
    # Serverless hosts give you a read-only filesystem apart from /tmp, and even
    # that is wiped between runs -- so on Vercel, history is per-session only.
    db_path: Path = field(default_factory=lambda: Path(_default_db()))

    def ai_available(self) -> bool:
        return bool(self.ai_key)

    def ai_provider(self) -> dict | None:
        """The company that issued this key, worked out from the key itself."""
        return providers.detect(self.ai_key)

    def ai_endpoint(self) -> str:
        """Where to send the request. An explicit setting always wins."""
        if self.ai_base_url:
            return self.ai_base_url.rstrip("/")
        found = self.ai_provider()
        return found["base_url"] if found else ""

    # ── the published-table rule ───────────────────────────────────────────
    def production(self) -> ProductionRule:
        """The rule, read. Rebuilt only when the entries themselves change.

        Asked once per table visited on every hop of every scan, and a real
        list is hundreds of names long, so the answer is worked out once and
        kept rather than re-parsed each time.
        """
        entries = tuple(self.production_patterns)
        cached = getattr(self, "_production_cache", None)
        if cached is None or cached[0] != entries:
            rule = ProductionRule(text=self.production_text,
                                  entries=parse_production_text(
                                      "\n".join(entries)).entries)
            object.__setattr__(self, "_production_cache", (entries, rule))
            return rule
        return cached[1]

    def set_production(self, text: str) -> ProductionRule:
        """Take a pasted list, in whatever shape it arrived. Returns what was read.

        An empty box stays empty. It used to fall back to the shipped default --
        _PROD, _PRD, _PUBLISHED -- and that is the most expensive thing this
        tool ever did: on a warehouse that names its published tables anything
        else, the default matches NOTHING, and matching nothing does not read as
        "I do not know which tables are yours". It reads as "no production table
        is affected", in green, over a change that breaks all of them.

        Empty now means NOT GIVEN, which is a different thing from "nothing is
        published" and is treated as one everywhere: see has_production, which
        every entry point checks before it will scan.
        """
        rule = parse_production_text(text or "")
        self.production_text = "" if rule.is_empty() else str(text or "")
        self.production_patterns = tuple(e.given for e in rule.entries)
        object.__setattr__(self, "_production_cache",
                           (self.production_patterns, rule))
        return rule

    def has_production(self) -> bool:
        """Has anybody said which tables this team publishes?

        The one setting Ripple cannot work out for itself, and the one that
        decides whether the answer says "production impact" at all. Nothing may
        be scanned until it has been given -- an answer computed against a list
        nobody chose is worth less than no answer, because it looks the same as
        a real one.
        """
        return bool(self.production_patterns)

    def is_production_table(self, table: str) -> bool:
        return self.production().matches(table)

    def production_rule(self) -> str:
        """The rule as one short line, for a status row rather than a screen.

        Two hundred pasted table names do not fit on a line, and pretending
        otherwise produces a row of dots that says nothing. A long list is
        counted instead; a short one is still shown in full.
        """
        return self.production().one_line()


settings = Settings()
````

## Paste 2 of 25

### ripple/narrative.py

Create the file `ripple/narrative.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Writing the summary and the reply without any AI.

This is what runs when there is no key, when the key stops working, or when
someone decides no data may leave the network. It is plainer than the AI
version, but it says exactly the same things -- the facts come from the scan
either way.
"""
from __future__ import annotations

from datetime import date


def _plural(n: int, one: str, many: str | None = None) -> str:
    return f"{n} {one}" if n == 1 else f"{n} {many or one + 's'}"


def days_until(iso: str) -> int | None:
    if not iso:
        return None
    try:
        y, m, d = (int(x) for x in iso.split("-"))
        return (date(y, m, d) - date.today()).days
    except (ValueError, TypeError):
        return None


def _names(items: list[str], limit: int = 6) -> str:
    """A readable list of table names, however many there really are.

    On a real repository one key column reaches hundreds of tables. Joining
    them all into a sentence produces a paragraph nobody reads, in the one place
    on the screen written to be read -- and the count, which is the fact that
    matters, disappears into the middle of it.
    """
    if len(items) <= limit:
        return ", ".join(items)
    return ", ".join(items[:limit]) + f" and {len(items) - limit} more"


def _unique(groups: list[dict]) -> list[dict]:
    """Rows across groups, listed once. A finding upstream of two tables appears
    in both groups; counting it twice makes the actions read like a stutter."""
    rows, seen = [], set()
    for g in groups:
        for r in g["rows"]:
            k = (r.get("file"), r.get("attr"), r.get("alias"), r.get("logic"))
            if k not in seen:
                seen.add(k)
                rows.append(r)
    return rows


def summarise(scan: dict, vals: dict) -> dict:
    stats = scan.get("stats", {})
    groups = scan.get("groups", [])
    # Chains that end somewhere that is not on the production list, and usages
    # in code that builds no table at all. Both are real usages of the
    # attribute, and saying "no impact" while holding them would be a lie the
    # person then forwards to the upstream team in writing.
    reached = scan.get("reached", [])
    other = scan.get("other", [])
    unreadable = scan.get("unreadable", [])
    prod_names = [g["prod"] for g in groups]
    rows = _unique(groups)
    elsewhere = _unique(reached) + other
    breaking = [r for r in rows if r.get("breaking")]
    no_fix = [r for r in rows if r.get("noLocalFix")]
    attrs = ", ".join(
        a for u in vals.get("upstream", []) for a in u.get("attrs", [])
    ) or "the changed attributes"
    when = vals.get("effectiveLabel") or "the effective date"

    # How much of the repository this answer does NOT cover. A headline is a
    # sentence somebody quotes in a meeting and pastes into a reply, so it must
    # never claim more than was read: "no impact" over four hundred files that
    # were never opened is the exact answer this tool exists to stop anybody
    # giving, and so is "all fixable in code" over a list of files nobody could
    # follow -- the fix that is missing may well be in one of them.
    files_scanned = scan.get("filesScanned", 0)
    never_opened = stats.get("neverOpened", 0)
    # Two more ways this answer covers less than the whole picture, and both used
    # to be silent. A trail Ripple stopped following at its hop limit, and a
    # table built with SELECT * whose column list is nowhere in the code. Either
    # one makes "no impact" a sentence about how far Ripple looked rather than
    # about the pipeline -- and this is the paragraph that gets forwarded.
    cut_short = scan.get("cutShort", [])
    star_tables = scan.get("starTables", [])
    # Facts this letter used to be written without, every one of them measured
    # as a letter that said the opposite of the screen it was written from.
    feeds = scan.get("feeds", [])
    stops = scan.get("stopsLoading", [])
    referenced = [r for r in scan.get("referencedHere", []) if r.get("namesColumns")]
    lookup_failed = bool(scan.get("lookupFailed"))
    # Code files walked past because of the folder they sit in. Measured: the
    # whole chain from the source table to the published one sat in build/, and
    # this file wrote "Please proceed as planned".
    skipped = len(scan.get("skippedInFolders", []))
    folder_names = scan.get("skippedFolderNames", [])
    # A whole file type Ripple does not open is exactly as unread as a folder it
    # was told to skip. Measured: the middle hop of the chain sat in a notebook,
    # and this letter said "Please proceed as planned" over it.
    unopened_types = scan.get("fileTypesUnopened", [])
    unopened = sum(t.get("count", 0) for t in unopened_types)
    blind = never_opened + len(unreadable) + len(cut_short) + skipped + unopened

    def _blind_phrase() -> str:
        bits = []
        if never_opened:
            bits.append(f"{_plural(never_opened, 'file')} could not be opened at all")
        if unreadable:
            bits.append(f"{_plural(len(unreadable), 'file')} could not be followed")
        if skipped:
            bits.append(f"{_plural(skipped, 'code file')} "
                        f"{'sits' if skipped == 1 else 'sit'} in a folder Ripple is told to "
                        f"skip ({_names(folder_names)}) and "
                        f"{'was' if skipped == 1 else 'were'} never read")
        if unopened:
            bits.append(f"{_plural(unopened, 'file')} "
                        f"{'is' if unopened == 1 else 'are'} of a type Ripple does not open "
                        f"({_names([t.get('ext', '') for t in unopened_types])})")
        if cut_short:
            bits.append(f"{_plural(len(cut_short), 'trail')} was stopped at "
                        f"{scan.get('maxHops', 4)} renames deep and was still going"
                        if len(cut_short) == 1 else
                        f"{len(cut_short)} trails were stopped at "
                        f"{scan.get('maxHops', 4)} renames deep and were still going")
        return " and ".join(bits)

    def _inferred_phrase() -> str:
        if not star_tables:
            return ""
        return (f" {_plural(len(star_tables), 'table')} on the way "
                f"{'is' if len(star_tables) == 1 else 'are'} built with SELECT *, so the column "
                f"list could not be read and the steps past "
                f"{'it' if len(star_tables) == 1 else 'them'} are worked out rather than read.")

    if not groups and elsewhere:
        # Found, and consumed -- but nothing it feeds is on the list of tables
        # this team publishes. That is either a genuinely internal chain or a
        # production naming rule that does not match this repository, and only
        # a person can tell which. So the wording says exactly that.
        # A chain that Ripple stopped following has not ended, so it must not be
        # described with the word "end". That sentence used to be printed on the
        # screen where somebody decides whether to worry, about a chain that was
        # still going when the hop limit stopped the walk.
        cut_names = [c["table"] for c in cut_short]
        end_names = [g["prod"] for g in reached if not g.get("cut")]
        # Two things Ripple DID name, one line earlier on the same screen, while
        # this paragraph said "none of them reaching a table on your published
        # list" and sent the reader off to fix a rule that had worked perfectly.
        stop_names = [s["prod"] for s in stops]
        feed_names = [f["uri"] for f in feeds if f.get("uri")]
        if stop_names:
            headline = (f"{_plural(len(stop_names), 'published table')} "
                        f"{'stops' if len(stop_names) == 1 else 'stop'} being refreshed")
        elif feed_names:
            headline = (f"{_plural(len(feed_names), 'delivery')} out of the warehouse "
                        f"{'breaks' if len(feed_names) == 1 else 'break'}")
        else:
            headline = (f"{_plural(len(elsewhere), 'usage')} found - none of them reaching "
                        f"a table on your published list")
        narrative = (
            f"{attrs} is used in {_plural(len({r.get('file') for r in elsewhere}), 'file')} "
            f"of the {scan.get('filesScanned', 0)} scanned. "
            + (f"Those chains end at {_names(end_names)}. " if end_names else "")
            + (f"Ripple stopped following {_names(cut_names)} at "
               f"{scan.get('maxHops', 4)} renames deep - "
               f"{'that trail was' if len(cut_names) == 1 else 'those trails were'} still going, "
               f"so nothing past that point has been looked at. " if cut_names else "")
            + (f"{_names(stop_names)} "
               f"{'is on your published list and stops' if len(stop_names) == 1 else 'are on your published list and stop'}"
               f" being refreshed: no column of "
               f"{'it' if len(stop_names) == 1 else 'them'} changes, the job that fills "
               f"{'it' if len(stop_names) == 1 else 'them'} stops running. " if stop_names else "")
            + (f"The data also leaves the warehouse: {_names(feed_names)} is written by one of "
               f"these statements, and whoever reads that file is outside this repository. "
               if feed_names else "")
            + ("" if stop_names or feed_names else
               "None of those names match the rule Ripple has been given for a table this "
               "team publishes, so this is not a clean result - it is an unfinished one. "
               "Check the rule on the settings screen before replying.")
            + _inferred_phrase()
        )
        bullets = [f"{r['inter']} - {r['logic'].lower()} on {r['alias']}" for r in elsewhere[:4]]
        if stop_names:
            bullets.insert(0, f"{_names(stop_names)} stops being refreshed on the day of the "
                              f"change. Nothing fails on screen; the numbers go stale.")
        if feed_names:
            bullets.insert(0, f"The delivery at {_names(feed_names)} carries this attribute out "
                              f"of the warehouse. Whoever reads it has to be told.")
        if not stop_names and not feed_names:
            bullets.append("Nothing here matched the production naming rule, so Ripple cannot say "
                           "whether these tables are ones anybody outside the team reads.")
        if cut_names:
            bullets.append(f"{_plural(len(cut_names), 'trail')} was cut short by the hop limit "
                           f"rather than by the code. Run the scan again, deeper, before "
                           f"treating this as the whole answer.")
        actions = ([f"Follow the trails Ripple stopped at - they were still going at "
                    f"{scan.get('maxHops', 4)} renames deep."] if cut_names else [])
        if feed_names:
            actions.append(f"Tell whoever reads {_names(feed_names)} - they are outside this "
                           f"repository and no scan of it will find them.")
        if stop_names:
            actions.append(f"Fix the job that fills {_names(stop_names)} before the date, or it "
                           f"quietly serves yesterday's data.")
        if not stop_names and not feed_names:
            actions.append("Check the production table rule on the settings screen against how "
                           "your tables are really named, then run the scan again.")
        actions.append("Until then, treat the tables listed above as impacted.")
    elif not files_scanned:
        # Nothing was read at all. "No impact" here is a statement about an
        # empty folder dressed up as a statement about a pipeline.
        headline = "Nothing was scanned - there was no code to search"
        narrative = (
            f"Ripple read no files at all, so it has looked for {attrs} in nothing. This is not "
            f"a result about your pipeline; it is a result about an empty repository. Choose the "
            f"folder holding the code on the settings screen and run the scan again."
        )
        bullets = ["No file was read, so nothing can be said about the change either way."]
        actions = [
            "Point Ripple at the folder holding the code, on the settings screen.",
            "Run the scan again once files have been read.",
        ]
    elif lookup_failed:
        # Not "no impact". Ripple never met this name as a column on any table
        # it read, so it has not answered the question -- and this paragraph is
        # the one that gets pasted into a reply. Measured: a mistyped attribute
        # produced "No impact - nothing in this repository consumes the
        # attribute" and a letter reading "Please proceed as planned."
        known = [c for a in scan.get("attributes", []) for c in a.get("tableColumns", [])]
        table = (scan.get("attributes") or [{}])[0].get("table", "that table")
        headline = f"{attrs} was not found - nothing has been checked"
        narrative = (
            f"Ripple read {_plural(files_scanned, 'file')} and never met a column called "
            f"{attrs} on {table}, or on anything else in this repository. That is not the same "
            f"as the change being safe: the question has not been answered. Check the spelling "
            f"before replying."
            + (f" The columns Ripple did read on {table} are {_names(known, 12)}."
               if known else
               f" Ripple has no column list for {table} either, because nothing in this "
               f"repository writes one down.")
        )
        bullets = [
            f"No answer either way about {attrs} - the name was not found as a column.",
            (f"What Ripple did read on {table}: {_names(known, 12)}." if known else
             f"Nothing in this repository states the columns of {table}."),
        ]
        actions = [
            f"Check the spelling of {attrs} against the list above, then run the scan again.",
            "Do not reply to the upstream team on the strength of this scan.",
        ]
    elif not groups:
        if referenced:
            # Nothing carries the column anywhere, and something names it
            # outright and stops working without it. That is not "no impact".
            headline = (f"No lineage, but {_plural(len(referenced), 'statement')} "
                        f"{'names' if len(referenced) == 1 else 'name'} {attrs} directly")
        elif blind:
            headline = (f"No usage found in the {_plural(files_scanned, 'file')} that could be "
                        f"read - {_plural(blind, 'other file')} could not be")
        else:
            headline = "No impact - nothing in this repository consumes the attribute"
        narrative = (
            f"The scan read {_plural(files_scanned, 'file')} looking for {attrs}, and found no "
            f"path from it to any production table this team publishes."
            + (f" {_plural(len(referenced), 'statement')} does name it and carries it nowhere: "
               f"{_names([r['kind'] + ' on ' + r['table'] for r in referenced])}. "
               f"{'That stops' if len(referenced) == 1 else 'Those stop'} working on the day "
               f"the column changes." if referenced else "")
            + (f" It is not a clean result for the whole repository: {_blind_phrase()}, "
               f"so nothing in those is covered either way." if blind else "")
            + _inferred_phrase()
        )
        bullets = [
            f"No production table depends on {attrs}.",
            f"{_plural(scan.get('filesMatched', 0), 'file')} mentioned the name, none of them in a way that carries it downstream.",
        ]
        if referenced:
            bullets.insert(0, f"{_plural(len(referenced), 'statement')} names {attrs} without "
                              f"carrying it anywhere - "
                              f"{_names([r['kind'] + ' on ' + r['table'] for r in referenced])}.")
        actions = (["Read the files below by hand before replying - this result does not cover them."]
                   if blind else [])
        if referenced:
            actions.append(f"Update the "
                           f"{_names([r['kind'] for r in referenced])} that names {attrs}.")
        actions += [
            "Reply to the upstream team confirming no impact." if not blind and not referenced
            else "Reply only once those have been checked.",
            "Re-run the scan if this repository takes on the table later.",
        ]
    else:
        if no_fix:
            headline = "Ranking logic has no replacement - escalate before the date"
        elif breaking and blind:
            # "All fixable in code" is a promise about the whole repository. The
            # fix that has no substitute may well be inside one of the files
            # nobody could follow, and that is not a promise to make on a
            # headline somebody forwards.
            headline = (f"{_plural(len(prod_names), 'production table')} at risk, and "
                        f"{_plural(blind, 'file')} Ripple could not follow")
        elif breaking:
            headline = f"{_plural(len(prod_names), 'production table')} at risk, all fixable in code"
        elif blind:
            headline = (f"Labels change - and {_plural(blind, 'file')} could not be checked")
        else:
            headline = "Labels change, but nothing breaks"
        narrative = (
            f"{attrs} changes on {when}. "
            f"{_plural(len(rows), 'pipeline object')} consume it across "
            f"{_plural(stats.get('filesWithImpact', 0), 'file')}, feeding "
            f"{_names(prod_names)}. "
            + (
                f"{_plural(len(breaking), 'of those usages breaks', 'of those usages break')} outright."
                if breaking
                else "None of those usages break outright - the values simply change shape."
            )
        )
        bullets = []
        for r in breaking[:4]:
            bullets.append(f"{r['inter']} - {r['logic'].lower()} on {r['alias']} - {r['impact']}")
        if no_fix:
            bullets.append(
                "At least one usage has no local fix: a replacement must come from the upstream team."
            )
        if not bullets:
            bullets.append("Every usage carries the value through unchanged; only labels move.")
        actions = []
        for r in breaking[:4]:
            actions.append(f"Fix the {r['logic'].lower()} on {r['alias']} in {r['file']}.")
        if no_fix:
            actions.insert(0, "Ask the upstream team for a replacement attribute - this one has no substitute.")
        actions.append("Re-run the scan once the fixes are in, and confirm the findings clear.")

    if unreadable:
        bullets.append(
            f"{_plural(len(unreadable), 'file')} could not be followed and must be checked by hand."
        )
        actions.append(
            f"Read the {_plural(len(unreadable), 'file')} in the 'check by hand' list yourself - "
            f"Ripple could not read them, or found the name somewhere it cannot follow."
        )

    # Files that were never opened go first among the caveats and are worded
    # harder, because every other number on the page is a number about the files
    # that WERE opened. Left unsaid, this reads as an answer about the whole
    # repository when it is an answer about part of one.
    if never_opened:
        bullets.insert(0, (
            f"{_plural(never_opened, 'file')} in this repository could not even be opened, so "
            f"nothing in them was read - this result covers the rest."
        ))
        actions.insert(0, (
            f"Make the {_plural(never_opened, 'file')} that could not be opened available on this "
            f"machine and read the repository again before trusting this result."
        ))

    return {
        "headline": headline,
        "narrative": narrative,
        "bullets": bullets[:6],
        "actions": actions[:6],
        "writtenBy": "rules",
    }


def draft_reply(scan: dict, vals: dict, summary: dict) -> dict:
    groups = scan.get("groups", [])
    reached = scan.get("reached", [])
    other = scan.get("other", [])
    # The same rows the summary counted. A finding upstream of two published
    # tables appears in both groups, so counting them raw made the letter say
    # "9 pipeline objects" one click after the summary said 8 -- two numbers for
    # the same thing, and the wrong one is the one that leaves the building.
    rows = _unique(groups)
    elsewhere = _unique(reached) + other
    no_fix = [r for r in rows if r.get("noLocalFix")]
    poc = vals.get("pocName") or "there"
    first = poc.split()[0] if poc and poc != "there" else "there"
    attrs = ", ".join(a for u in vals.get("upstream", []) for a in u.get("attrs", []))
    subject_base = vals.get("subject") or f"{attrs} change"

    if not groups and elsewhere:
        # This draft is a letter somebody sends. It must never say "no impact"
        # while the analysis behind it is holding a list of usages.
        end_names = _names([g["prod"] for g in reached], 10) or "tables in our own pipeline"
        # Two things Ripple named that this letter used to leave out entirely,
        # while telling the reader the data feeds "tables in our own pipeline".
        stops = scan.get("stopsLoading", [])
        feeds = [f["uri"] for f in scan.get("feeds", []) if f.get("uri")]
        subject = f"RE: {subject_base} - assessment in progress"
        lines = [
            f"Hi {first},", "",
            "We have run our impact analysis and are still confirming the result.", "",
            f"{attrs} is used in {_plural(len({r.get('file') for r in elsewhere}), 'file')} "
            f"in our repository, feeding {end_names}.",
        ]
        if stops:
            lines += ["", f"One thing is already confirmed: "
                          f"{_names([s['prod'] for s in stops], 10)} stops being refreshed on "
                          f"the day of the change. No column of it changes - the job that fills "
                          f"it stops running, so it quietly serves stale data."]
        if feeds:
            lines += ["", f"This data also leaves the warehouse. {_names(feeds, 10)} is written "
                          f"from one of these statements and read by somebody outside our "
                          f"repository, so we are tracing who consumes it."]
        if not stops:
            lines += ["", "We are confirming which of those tables are published outside our "
                          "team before we can tell you whether this is impacting."]
        lines += ["", "We will come back to you with a firm answer before the effective date.",
                  "", "Thanks,", "Data Engineering"]
        body = "\n".join(lines)
    elif not scan.get("filesScanned", 0):
        # There was nothing to read. A letter saying "no impact" here is a
        # letter about an empty folder, sent to somebody who will act on it.
        subject = f"RE: {subject_base} - assessment not yet run"
        body = (
            f"Hi {first},\n\n"
            f"We are not able to give you an answer yet. Our impact analysis read no files at "
            f"all, so nothing has actually been checked.\n\n"
            f"We will come back to you with a firm answer before the effective date.\n\n"
            f"Thanks,\nData Engineering"
        )
    elif scan.get("lookupFailed"):
        # The question was never answered. Ripple never met this name as a
        # column anywhere it read, so there is nothing to report either way --
        # and this letter used to say "No impact... Please proceed as planned."
        subject = f"RE: {subject_base} - we need to check the attribute name"
        body = (
            f"Hi {first},\n\n"
            f"We cannot answer this one yet.\n\n"
            f"Our repository scan could not find a column called {attrs} anywhere in our code, "
            f"so nothing has actually been checked against it. That is most likely a difference "
            f"in how the attribute is named on our side.\n\n"
            f"Could you confirm the exact column name? We will re-run the analysis and come back "
            f"to you with a firm answer before the effective date.\n\n"
            f"Thanks,\nData Engineering"
        )
    elif not groups:
        # "No impact, proceed as planned" is the single most consequential
        # sentence this tool writes. It is only ever sent when the whole
        # repository really was read -- and a trail Ripple stopped following at
        # its own hop limit is not the whole repository having been read, any
        # more than a folder Ripple was told to skip is.
        referenced = [r for r in scan.get("referencedHere", []) if r.get("namesColumns")]
        # A folder Ripple was told to skip is exactly as unread as a file it
        # could not open, and this letter used to count neither.
        blind = (scan.get("stats", {}).get("neverOpened", 0)
                 + len(scan.get("unreadable", []))
                 + len(scan.get("cutShort", []))
                 + len(scan.get("skippedInFolders", []))
                 # ... and a file type Ripple does not open at all is neither
                 # read nor followed nor reached. See fileTypesUnopened.
                 + sum(t.get("count", 0) for t in scan.get("fileTypesUnopened", [])))
        if blind or referenced:
            subject = f"RE: {subject_base} - no impact found so far"
            lines = [
                f"Hi {first},", "",
                "We have run our impact analysis and are still confirming the result.", "",
                f"No usage of {attrs} was found in the "
                f"{_plural(scan.get('filesScanned', 0), 'file')} we were able to read, and no "
                f"production table traces back to it.",
            ]
            if blind:
                lines += ["", f"{_plural(blind, 'further file')} could not be read, followed or "
                              f"reached automatically and "
                              f"{'is' if blind == 1 else 'are'} being checked by hand, so we are "
                              f"not confirming no impact yet."]
            if referenced:
                # Read, understood, and carrying the column nowhere -- so it is
                # not on any chain, and it stops working all the same.
                lines += ["", f"Separately, {_plural(len(referenced), 'statement')} in our "
                              f"repository names {attrs} without carrying it into another table "
                              f"- {_names([r['kind'] + ' on ' + r['table'] for r in referenced])}. "
                              f"{'That has' if len(referenced) == 1 else 'Those have'} to be "
                              f"updated on our side before the date."]
            lines += ["", "We will come back to you with a firm answer before the effective "
                          "date.", "", "Thanks,", "Data Engineering"]
            body = "\n".join(lines)
        else:
            subject = f"RE: {subject_base} - no impact"
            body = (
                f"Hi {first},\n\n"
                f"We have completed our impact analysis.\n\n"
                f"No impact. Our repository scan found no usage of {attrs} in any SQL, Spark job, "
                f"view or ETL script, and no production table traces back to it.\n\n"
                f"No action required from our side. Please proceed as planned.\n\n"
                f"Thanks,\nData Engineering"
            )
    else:
        # Capped like every other list of table names here: this is a letter
        # somebody sends, and a paragraph of two hundred names is not read.
        prod = _names([g["prod"] for g in groups], 10)
        lines = [f"Hi {first},", "", "We have completed our impact analysis.", ""]
        lines.append(
            f"Impact confirmed. {attrs} is consumed by {_plural(len(rows), 'pipeline object')} "
            f"feeding {_plural(len(groups), 'production table')}: {prod}."
        )
        lines.append("")
        lines.append("What we will do before the effective date:")
        for a in summary.get("actions", [])[:4]:
            lines.append(f"  - {a}")
        if no_fix:
            lines += [
                "",
                "One ask of your team: at least one of these usages orders or deduplicates on the "
                "attribute, and has no local substitute. Can you confirm a replacement attribute, "
                "or retain this one, before the effective date?",
            ]
        unreadable = scan.get("unreadable", [])
        if unreadable:
            lines += [
                "",
                f"For transparency: {_plural(len(unreadable), 'file')} in our repository could not be "
                f"read automatically and are being checked by hand, so this assessment may still grow.",
            ]
        never_opened = scan.get("stats", {}).get("neverOpened", 0)
        if never_opened:
            lines += [
                "",
                f"Also for transparency: {_plural(never_opened, 'file')} could not be opened at all "
                f"on the machine this was run on, so this assessment does not cover them.",
            ]
        lines += ["", "Thanks,", "Data Engineering"]
        subject = f"RE: {subject_base} - impact confirmed"
        body = "\n".join(lines)

    return {"subject": subject, "body": body, "writtenBy": "rules"}
````

## Paste 3 of 25

### ripple/notification.py

Create the file `ripple/notification.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Reading the impact notification.

Two ways in, and both end at the same editable form:

* upload a saved Outlook message, or paste the text
* type the tables and attributes yourself (manual mode)

Extraction never has the last word. Whatever comes out of here is shown to a
human to correct before a single file is scanned.
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from datetime import date, datetime

from .catalog import Catalog

# A SHOUTED_NAME. Narrow on purpose, and kept that way for the two jobs where
# being narrow is right: telling a table name apart from a person's team, and
# listing the names an email mentioned that this repository has never heard of.
IDENT = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")
# Anything that could be a name at all, in whatever case it happens to be
# written. Matching only SHOUTED_NAMES was a quiet disaster: BigQuery names are
# written in lower case, his own repository has ccm_Wireless_Enroll in mixed
# case, and a great many columns -- cm13, pub_guid -- are one word with no
# underscore in them at all.
#
# An email reading "we are removing cm13 from customer_demographics ...
# ACCOUNT_MASTER is unaffected" produced exactly one table to scan:
# ACCOUNT_MASTER. The only one the email says is fine, with no warning of any
# kind, and a clean confident result at the end of it.
#
# Being wide costs nothing here, because a token only becomes a table or a
# column once the catalogue built from the repository confirms that it is one.
# A spare name on the confirm screen is a tick somebody can clear; a missing
# one is invisible.
NAME_TOKEN = re.compile(r"\b[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)*\b")

DATE_PATTERNS = [
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "%Y-%m-%d"),
    (re.compile(r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b", re.I), None),
    (re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s*(\d{4})?\b", re.I), None),
]
MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}

CHANGE_HINTS = [
    (("decommission", "removed", "removal", "dropped", "retire", "sunset"), "removal", "Attribute decommission"),
    (("renamed", "rename"), "rename", "Attribute rename"),
    (("format", "value", "iso", "full country"), "value_change", "Value format change"),
    (("data type", "datatype", "length", "precision", "varchar", "widened"), "type_change", "Data type change"),
]

EMAIL_ADDR = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


@dataclass
class Notification:
    subject: str = ""
    body: str = ""
    from_name: str = ""
    from_email: str = ""
    attachments: list[str] = field(default_factory=list)
    source_kind: str = "paste"          # msg | eml | paste | manual
    warnings: list[str] = field(default_factory=list)

    def text(self) -> str:
        return f"{self.subject}\n\n{self.body}"


# ── getting the words out of the file ──────────────────────────────────────
def read_eml(raw: bytes) -> Notification:
    from email import policy
    from email.parser import BytesParser

    msg = BytesParser(policy=policy.default).parsebytes(raw)
    n = Notification(source_kind="eml")
    n.subject = str(msg.get("subject") or "")
    sender = str(msg.get("from") or "")
    m = re.match(r"\s*\"?([^\"<]*)\"?\s*<?([^>]*)>?", sender)
    if m:
        n.from_name = m.group(1).strip()
        n.from_email = m.group(2).strip()
    body_parts: list[str] = []
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition") or "")
            if "attachment" in disp:
                n.attachments.append(part.get_filename() or "attachment")
                continue
            if ctype == "text/plain":
                body_parts.append(part.get_content())
            elif ctype == "text/html" and not body_parts:
                body_parts.append(strip_html(part.get_content()))
    else:
        content = msg.get_content()
        body_parts.append(
            strip_html(content) if msg.get_content_type() == "text/html" else content
        )
    n.body = "\n".join(p for p in body_parts if p).strip()
    if not n.body:
        n.warnings.append("The email had no readable text body - paste the text instead.")
    return enrich(n)


def read_msg(raw: bytes) -> Notification:
    try:
        import extract_msg
    except ImportError:  # pragma: no cover
        n = Notification(source_kind="msg")
        n.warnings.append("Outlook .msg support is not installed - paste the text instead.")
        return n
    n = Notification(source_kind="msg")
    try:
        m = extract_msg.Message(io.BytesIO(raw))
        n.subject = m.subject or ""
        n.from_name = (m.sender or "").split("<")[0].strip().strip('"')
        em = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", m.sender or "")
        n.from_email = em.group(0) if em else ""
        n.body = (m.body or "").strip()
        if not n.body and getattr(m, "htmlBody", None):
            html = m.htmlBody
            n.body = strip_html(html.decode("utf-8", "ignore") if isinstance(html, bytes) else html)
        n.attachments = [a.longFilename or a.shortFilename or "attachment"
                         for a in (m.attachments or [])]
    except Exception as exc:
        n.warnings.append(f"Could not open the Outlook file ({type(exc).__name__}) - paste the text instead.")
    if not n.body and not n.warnings:
        n.warnings.append("The Outlook file had no readable text body - paste the text instead.")
    return enrich(n)


def strip_html(html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html or "")
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", text)
    text = re.sub(r"(?i)</t[dh]>", "\t", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


# ── headers and sign-offs that live inside the text itself ─────────────────
# A saved .msg or .eml carries real headers, so the sender and the subject are
# handed to us. Pasted text carries none: everything the reader needs is in the
# words themselves. That used to leave the source system and the contact blank
# on the one path that has no AI to cover for it, so the same facts are read
# out of the text here -- for pasted text and for uploads alike, because a
# forwarded email hides the original sender in its body too.

HEADER_KEYS = ("from", "sent", "date", "to", "cc", "bcc", "subject", "reply-to", "importance")
HEADER_LINE = re.compile(r"^\s*(" + "|".join(HEADER_KEYS) + r")\s*:\s*(.*)$", re.I)
# Anything header-shaped, used only to decide how far a block reaches. Someone
# who opens a saved .eml in Notepad and pastes the lot brings Content-Type and
# MIME-Version with them, and left in the body one of those becomes Ripple's
# description of the change.
ANY_HEADER = re.compile(r"^\s*[A-Za-z][A-Za-z0-9-]{1,40}\s*:\s")
# "-----Original Message-----", or the row of underscores Outlook draws above a
# forwarded block. Worth removing with the block, or it is left floating.
FORWARD_RULE = re.compile(r"^\s*(?:[-_=*]{5,}|-{2,}\s*original message\s*-{2,}|-{2,}\s*forwarded message\s*-{2,})\s*$", re.I)
# Gmail and most phones write the attribution as one line instead of a block.
# The name is the part after the last comma, so it may not contain one itself --
# otherwise the whole date swallows it ("Mon, 3 Aug 2026 at 09:14, Priya Raman").
WROTE_LINE = re.compile(r"^\s*On\b.{0,80}?,\s*(?P<who>[^<>,]{2,60}?)\s*(?:<(?P<email>[^>]+)>)?\s*wrote:\s*$", re.I)

# How people end these notices. The name comes after the closing, not before.
SIGNOFF_OPENERS = re.compile(
    r"^\s*(regards|kind regards|best regards|best wishes|best|thanks|thank you|many thanks|"
    r"cheers|sincerely|yours|warm regards|br)\s*[,.!]*\s*$", re.I)
# Words that describe what a team does rather than which system it owns, so
# "C360 Data Governance" yields "C360" and "Data Governance" yields nothing.
TEAM_TAIL_WORDS = {
    "data", "governance", "office", "team", "platform", "engineering", "operations",
    "ops", "group", "dept", "department", "services", "service", "support", "delivery",
    "programme", "program", "function", "domain", "coe",
}
# Bracketed subject tags that are a priority flag, not a system name.
SUBJECT_TAG_STOPWORDS = {
    "action required", "action", "notice", "fyi", "eom", "external", "urgent",
    "reminder", "info", "important", "confidential", "internal", "update", "alert",
}


def split_pasted_headers(body: str) -> tuple[dict[str, str], str]:
    """Lift an Outlook-style header block out of text and hand back both halves.

    Only a run of header lines anchored on a ``From:`` line counts, so a
    sentence that merely begins "To: " is left alone. Every block found is
    removed -- a twice-forwarded email has several -- but the values reported
    are the first block's, which is the one at the top of what was pasted.
    """
    lines = (body or "").splitlines()
    found: dict[str, str] = {}
    keep: list[str] = []
    i = 0
    while i < len(lines):
        m = WROTE_LINE.match(lines[i])
        if m:
            found.setdefault("from", (m.group("who") or "").strip()
                             + (f" <{m.group('email')}>" if m.group("email") else ""))
            i += 1
            continue
        head = HEADER_LINE.match(lines[i])
        if not (head and head.group(1).lower() == "from"):
            keep.append(lines[i])
            i += 1
            continue
        # A real block: this From: line plus the header lines packed around it.
        # A block reaches as far as header-shaped lines go, but only the ones
        # worth reading are read -- the rest are noise to be taken out of the way.
        start = i
        while start > 0 and keep and ANY_HEADER.match(keep[-1]):
            keep.pop()
            start -= 1
        end = i
        block: list[str] = []
        while end < len(lines) and ANY_HEADER.match(lines[end]):
            block.append(lines[end])
            end += 1
        for line in block:
            hm = HEADER_LINE.match(line)
            if hm:
                found.setdefault(hm.group(1).lower(), hm.group(2).strip())
        # the rule Outlook draws above the block goes with it
        while keep and (not keep[-1].strip() or FORWARD_RULE.match(keep[-1])):
            if FORWARD_RULE.match(keep[-1]):
                keep.pop()
                break
            keep.pop()
        i = end
    return found, "\n".join(keep).strip()


def parse_sender(value: str) -> tuple[str, str]:
    """A name and an address out of one ``From:`` value, in any of its shapes."""
    raw = (value or "").strip()
    if not raw:
        return "", ""
    email = ""
    m = EMAIL_ADDR.search(raw)
    if m:
        email = m.group(0)
    # strip the address itself, however it was wrapped, and any mailto: label
    name = re.sub(r"<[^>]*>|\[mailto:[^\]]*\]|\(mailto:[^)]*\)", " ", raw, flags=re.I)
    name = name.replace(email, " ").strip().strip('",;').strip()
    if name.lower().startswith("mailto:"):
        name = ""
    # "priya.raman@corp.example.com" alone -> make a readable name from it
    if not name and email:
        name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
    return name, email


def _is_person(line: str) -> bool:
    words = line.split()
    if not (1 < len(words) <= 4) or len(line) > 45:
        return False
    # A tab means a table cell, not a person -- an HTML table flattens to tabs.
    if any(c in line for c in "@:_/\\|\t") or any(c.isdigit() for c in line):
        return False
    if line.rstrip().endswith((".", "?", "!")):
        return False
    return all(w[0].isupper() or (len(w) <= 3 and w.islower()) for w in words if w)


def _is_team(line: str) -> bool:
    """A team line has to say what the team does, not merely look tidy.

    Without that, the second name in a sign-off, or any short capitalised line,
    becomes somebody's "team". Requiring one of the words teams are actually
    named after means an unrecognised shape leaves the field blank instead.
    """
    words = line.split()
    if not (0 < len(words) <= 6) or len(line) > 60:
        return False
    if any(c in line for c in "@:|\t") or line.rstrip().endswith((".", "?", "!")):
        return False
    if IDENT.search(line):                 # a table name is not a team name
        return False
    return any(w.strip(",.").lower() in TEAM_TAIL_WORDS for w in words)


def signature(body: str) -> dict[str, str]:
    """The name, team and address a notice is signed off with.

    Read from the bottom up, because that is where a sign-off is: reading down
    from the top, the first tidy-looking line of the message body wins instead.
    Only the tail is considered, and only lines that plainly read as a person
    and a team are accepted. Nothing here guesses -- an unrecognised shape
    leaves the field blank for someone to fill in, rather than filling it in
    wrongly.
    """
    out = {"name": "", "team": "", "email": ""}
    tail = [ln.strip() for ln in (body or "").splitlines() if ln.strip()][-8:]
    if not tail:
        return out
    pending_team, pending_at = "", -1
    for i in range(len(tail) - 1, -1, -1):
        clean = tail[i].lstrip("-–—•* ").strip()
        if not clean or SIGNOFF_OPENERS.match(clean):
            continue
        # "Priya Raman, C360 Data Governance" -- both on one line
        if "," in clean:
            left, right = (p.strip() for p in clean.split(",", 1))
            if _is_person(left) and _is_team(right):
                out["name"], out["team"] = left, right
                break
        if _is_team(clean):
            pending_team, pending_at = clean, i
            continue
        if _is_person(clean):
            out["name"] = clean
            if pending_at == i + 1:        # the team sits directly beneath it
                out["team"] = pending_team
            break
    for line in tail:
        m = EMAIL_ADDR.search(line)
        if m:
            out["email"] = m.group(0)
            break
    return out


def source_system(team: str, subject: str) -> str:
    """Which upstream system this came from -- never who typed the email.

    It used to be the sender's first name, so a notice from Priya Raman was
    filed under "Priya". The system is named by the team that owns it, or by a
    tag on the subject line when that tag is a system code rather than a
    priority flag.
    """
    words = (team or "").split()
    while words and words[-1].strip(",.").lower() in TEAM_TAIL_WORDS:
        words.pop()
    if words:
        return " ".join(words).strip(",.-")
    m = re.match(r"\s*[\[(]([^\])]{1,20})[\])]", subject or "")
    if m:
        tag = m.group(1).strip()
        if tag.lower() not in SUBJECT_TAG_STOPWORDS and (tag.isupper() or any(c.isdigit() for c in tag)):
            return tag
    return ""


def enrich(n: Notification) -> Notification:
    """Fill in whatever the envelope did not carry, from the text itself."""
    found, body = split_pasted_headers(n.body)
    n.body = body or n.body
    if found.get("subject") and not n.subject:
        n.subject = found["subject"]
    if found.get("from"):
        name, email = parse_sender(found["from"])
        if not n.from_name:
            n.from_name = name
        if not n.from_email:
            n.from_email = email
    if not (n.from_name and n.from_email):
        sig = signature(n.body)
        n.from_name = n.from_name or sig["name"]
        n.from_email = n.from_email or sig["email"]
    return n


def read_pasted(text: str) -> Notification:
    """Text someone pasted in, read as carefully as an uploaded file is."""
    return enrich(Notification(body=(text or "").strip(), source_kind="paste"))


def read_upload(filename: str, raw: bytes) -> Notification:
    name = (filename or "").lower()
    if name.endswith(".msg"):
        return read_msg(raw)
    if name.endswith(".eml"):
        return read_eml(raw)
    try:
        return read_pasted(raw.decode("utf-8"))
    except UnicodeDecodeError:
        n = Notification(source_kind="paste")
        n.warnings.append("That file is not a .msg, .eml or plain text file.")
        return n


# ── turning the words into fields, with no AI involved ─────────────────────
def parse_date(text: str) -> str:
    for pat, fmt in DATE_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        try:
            if fmt:
                return datetime.strptime(m.group(0), fmt).date().isoformat()
            groups = [g for g in m.groups() if g]
            if groups[0].isdigit():                     # 18 September 2026
                day, mon, year = int(groups[0]), MONTHS[groups[1][:3].lower()], int(groups[2])
            else:                                       # September 18, 2026
                mon = MONTHS[groups[0][:3].lower()]
                day = int(groups[1])
                year = int(groups[2]) if len(groups) > 2 and groups[2] else date.today().year
            return date(year, mon, day).isoformat()
        except (ValueError, KeyError, IndexError):
            continue
    return ""


def classify_change(text: str) -> tuple[str, str]:
    low = (text or "").lower()
    for words, kind, label in CHANGE_HINTS:
        if any(w in low for w in words):
            return kind, label
    return "unknown", "Not specified"


def extract_by_rules(n: Notification, cat: Catalog) -> dict:
    """Pull fields out using the catalogue - the fallback when there is no AI.

    Columns are only accepted once their own table has matched. Without that
    rule, generic words like STATUS or AMOUNT produce a page of false hits.
    """
    n = enrich(n)                      # however this arrived, read its own text too
    text = n.text()
    idents = [m.group(0) for m in NAME_TOKEN.finditer(text)]
    seen_tables: list[str] = []
    for tok in idents:
        if cat.has_table(tok) and tok.upper() not in [t.upper() for t in seen_tables]:
            seen_tables.append(tok)

    upstream = []
    for t in seen_tables:
        attrs = [tok for tok in idents if cat.has_column(t, tok)]
        deduped: list[str] = []
        for a in attrs:
            if a.upper() not in [x.upper() for x in deduped]:
                deduped.append(a)
        upstream.append({"table": t, "attrs": deduped})

    kind, label = classify_change(text)
    warnings = list(n.warnings)
    # Only SHOUTED_NAMES are worth complaining about. Every ordinary word in the
    # email is now checked against the catalogue above, and listing all of them
    # back as "not in your repository" would bury the one line that matters.
    shouted = [m.group(0) for m in IDENT.finditer(text)]
    unknown = [tok for tok in dict.fromkeys(shouted)
               if not cat.has_table(tok) and not any(cat.has_column(t, tok) for t in seen_tables)]
    if unknown:
        warnings.append(
            "These names were mentioned but are not in the connected repository: "
            + ", ".join(unknown[:8])
        )
    if not upstream:
        warnings.append(
            "No table from the connected repository was recognised. Add the table and "
            "attributes by hand before scanning."
        )

    sig = signature(n.body)
    return {
        "source": source_system(sig["team"], n.subject) or "Unknown",
        "changeType": label,
        "changeKind": kind,
        "changeDesc": first_sentence(n.body),
        "subject": n.subject,
        "effectiveDate": parse_date(text),
        "pocName": n.from_name or sig["name"],
        "pocEmail": n.from_email or sig["email"],
        "pocTeam": sig["team"],
        "upstream": upstream,
        "warnings": warnings,
        "extractedBy": "rules",
    }


# Header names that are plumbing rather than words a person wrote. Kept narrow
# on purpose: "Impact: this breaks the nightly load" is a real first sentence,
# and a rule that skipped every line with a colon in it would throw that away.
PLUMBING_HEADERS = re.compile(
    r"^\s*(content-type|content-transfer-encoding|content-disposition|content-language|"
    r"mime-version|message-id|received|return-path|delivered-to|authentication-results|"
    r"dkim-signature|thread-topic|thread-index|accept-language|x-[a-z0-9-]+)\s*:", re.I)


def first_sentence(body: str, limit: int = 240) -> str:
    clean = re.sub(r"\s+", " ", (body or "")).strip()
    for line in (body or "").splitlines():
        line = line.strip()
        if PLUMBING_HEADERS.match(line):
            continue
        if len(line) > 40 and not line.lower().startswith(("hi ", "hello", "team", "dear")):
            clean = line
            break
    return clean[:limit]
````

## Paste 4 of 25 — 4 files

### ripple/production.py

Create the file `ripple/production.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Which tables are the ones this team publishes.

This is the single most expensive setting in Ripple. A finding only counts as
production impact if the table it ends at is on this list, so getting it wrong
turns a change that really breaks three published tables into a calm "no
production impact" -- the exact answer this tool exists to stop anybody giving.

It used to take patterns only: a word like ``_PROD`` matching the end of a table
name, or ``PROD_*`` with a wildcard. That is a guess about a naming convention
dressed up as a rule. So this module also takes the answer directly: paste the
real list of published tables and Ripple uses it as written.

The paste arrives from wherever the list happens to live -- an Excel column, a
Slack message, a Confluence page, the output of a query -- so it is read
tolerantly. Nothing is thrown away quietly: everything the reader declined to
use comes back as a note saying what it was and why, because a silently misread
list here is worse than no list at all.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from fnmatch import fnmatch

# What Ripple assumes when nobody has said. Every one of these begins with an
# underscore, which is what marks it as a pattern rather than a table name.
DEFAULT_PRODUCTION = ("_PROD", "_PRD", "_PUBLISHED")
DEFAULT_TEXT = ", ".join(DEFAULT_PRODUCTION)

# ── how a line is tidied before anything is read out of it ─────────────────
# A bullet only counts as a bullet when a space follows it. Without that rule
# "*_PROD" would lose its wildcard and "PROD_*" would be fine while "*" alone
# -- which means "treat every table as published" -- would vanish entirely.
_BULLET = re.compile(r"^(?:[-–—•‣·◦*+>]\s+|\(?\d+[.)]\s+|\[\d+\]\s+)")
_FENCE = re.compile(r"^`{3,}|^~{3,}")
_SEPARATOR = re.compile(r"^[\s|:+-]*-[\s|:+-]*$")
_QUOTES = "\"'`‘’“”"

# A table name, as written anywhere it might be written: bare, dataset-qualified,
# or fully qualified with a project id (which on BigQuery may contain hyphens).
_PART = r"[A-Za-z_][A-Za-z0-9_$#-]*"
_TABLE_NAME = re.compile(rf"^{_PART}(?:\.{_PART}){{0,3}}$")

# Column headings a list of tables tends to arrive under. Matched only against
# the first row, so a table genuinely called "source" is only ever at risk if it
# is the very first line -- and even then the note says it was dropped.
_HEADINGS = {
    "table", "tables", "table name", "table names", "tablename", "name", "names",
    "full name", "full table name", "fully qualified name", "fully qualified table name",
    "qualified name", "target table", "output table", "published table", "prod table",
    "production table", "downstream table", "dataset", "datasets", "schema", "project",
    "database", "db", "owner", "team", "layer", "type", "description", "comment",
    "comments", "status", "notes", "id", "index", "no", "s no", "sr no", "sl no",
    "row", "environment", "env", "frequency", "sla", "domain", "source", "#",
}


@dataclass(frozen=True)
class Entry:
    """One thing read out of the paste, and what Ripple will do with it."""

    given: str          # as written, once decoration was stripped
    kind: str           # "name" | "endswith" | "glob"
    key: str            # what is actually matched, upper case

    @property
    def is_pattern(self) -> bool:
        return self.kind != "name"

    def to_dict(self) -> dict:
        return {"given": self.given, "kind": self.kind, "key": self.key,
                "isPattern": self.is_pattern}


def _classify(text: str) -> Entry | None:
    """A tidied cell, as an entry -- or None if it is not one.

    Three shapes, and the order matters. Both pattern shapes are exactly what
    they were before this module existed, so a rule somebody set months ago goes
    on meaning what it meant: a wildcard is matched against the whole name, and
    a word beginning with an underscore matches the end of one.
    """
    if "*" in text or "?" in text:
        return Entry(given=text, kind="glob", key=text.upper())
    if text.startswith("_"):
        return Entry(given=text, kind="endswith", key=text.upper())
    if _TABLE_NAME.match(text):
        # Ripple only ever learns the last part of a table name from SQL, so
        # that is what an exact name is compared against. The whole thing is
        # kept for showing back, because that is what was pasted.
        return Entry(given=text, kind="name", key=text.rsplit(".", 1)[-1].upper())
    return None


# ── reading the paste ──────────────────────────────────────────────────────
def _strip_decoration(line: str) -> str:
    """A line with Slack, Confluence and Markdown ornament taken off it."""
    out = line.strip()
    for _ in range(3):                     # "- - foo" happens; "- - - foo" does not
        stripped = _BULLET.sub("", out).strip()
        if stripped == out:
            break
        out = stripped
    return out


def _strip_cell(cell: str) -> str:
    """One value, with quotes, backticks and trailing punctuation taken off.

    Stripping never empties a value. A line of nothing but punctuation is left
    as it was so it comes back as something that was ignored, with a reason,
    rather than disappearing as if it had been a blank line.
    """
    out = original = cell.strip()
    for _ in range(4):
        before = out
        out = re.sub(r"[,;.]+$", "", out).strip()
        if len(out) >= 2 and out[0] in _QUOTES and out[-1] in _QUOTES:
            out = out[1:-1].strip()
        out = out.strip(_QUOTES).strip()
        if out == before:
            break
    return out or original


def _is_heading(cell: str) -> bool:
    norm = re.sub(r"[\s_\-]+", " ", cell.strip().strip(":.").lower()).strip()
    return norm in _HEADINGS


def _looks_like_a_name(cell: str) -> bool:
    return bool(_TABLE_NAME.match(cell)) or "*" in cell or "?" in cell


def _looks_like_a_table(cell: str) -> bool:
    """The stricter test: a name that could only be a table, not a word.

    Used where guessing wrong invents an entry rather than declining one --
    splitting a line on spaces, and choosing which column of a grid to read.
    "please confirm by friday" is four words that all pass the loose test, and
    reading them as four published tables would be the worst kind of quiet
    mistake: four tables Ripple would then never find anywhere.
    """
    if not _looks_like_a_name(cell):
        return False
    return "_" in cell or "." in cell or any(ch.isdigit() for ch in cell)


def _split_cells(line: str, delimiter: str | None) -> list[str]:
    if delimiter == "\t":
        return line.split("\t")
    if delimiter == "|":
        return line.split("|")
    parts = re.split(r"[,;]", line)
    out: list[str] = []
    for p in parts:
        p = p.strip()
        # A list pasted out of Slack can be space separated. Only split on
        # spaces when every piece is a name on its own -- otherwise "Table name"
        # would arrive as two entries instead of being spotted as a heading.
        pieces = p.split()
        if len(pieces) > 1 and all(_looks_like_a_table(_strip_cell(x)) for x in pieces):
            out.extend(pieces)
        else:
            out.append(p)
    return out


def _delimiter_of(lines: list[str]) -> str | None:
    """Tab or pipe means columns. Commas are a list unless a heading says otherwise."""
    if any("\t" in ln for ln in lines):
        return "\t"
    if any(len([c for c in ln.split("|") if c.strip()]) >= 2 for ln in lines):
        return "|"
    return None


def _pick_column(rows: list[list[str]], heading: list[str] | None) -> tuple[int, dict | None]:
    """Which column of a pasted grid holds the table names, and how it was decided.

    A heading with the word "table" in it settles the question outright. Failing
    that the column with the most values that look like table names wins. Either
    way the answer is handed back so the screen can say which column it took --
    a grid read down the wrong column is a silent, total misread.
    """
    width = max((len(r) for r in rows), default=0)
    if width <= 1:
        return 0, None
    # Columns that are empty everywhere are an artefact of splitting a Markdown
    # row on its pipes, not columns anybody pasted. Counting them would say
    # "the paste had 4 columns" about a two-column table.
    filled = [i for i in range(width)
              if any(i < len(r) and r[i].strip() for r in rows)]
    used = len(filled)

    def place(i: int) -> int:
        return (filled.index(i) + 1) if i in filled else i + 1

    if heading:
        for i, h in enumerate(heading[:width]):
            norm = re.sub(r"[\s_\-]+", " ", h.strip().strip(":.").lower()).strip()
            if "table" in norm and "count" not in norm:
                return i, {"index": i, "position": place(i), "heading": h.strip(),
                           "by": "heading", "columns": used}
    scores: list[tuple[int, int]] = []
    for i in range(width):
        score = 0
        for r in rows:
            cell = _strip_cell(r[i]) if i < len(r) else ""
            if not cell:
                continue
            if _looks_like_a_table(cell):
                score += 3
            elif _looks_like_a_name(cell):
                score += 1
        scores.append((score, -i))
    best = max(range(width), key=lambda i: scores[i])
    head = heading[best].strip() if heading and best < len(heading) else ""
    return best, {"index": best, "position": place(best), "heading": head,
                  "by": "content", "columns": used}


def parse(text: str) -> "ProductionRule":
    """Read a pasted list, however it arrived, and say what was made of it."""
    raw = str(text or "")
    notes: list[dict] = []
    fenced = 0
    lines: list[str] = []
    for line in raw.splitlines():
        if _FENCE.match(line.strip()):
            fenced += 1
            continue
        lines.append(line)
    if fenced:
        notes.append({"kind": "fence", "count": fenced, "examples": [],
                      "text": f"{fenced} code-fence line{'' if fenced == 1 else 's'} "
                              f"(```) ignored."})

    tidied = [_strip_decoration(ln) for ln in lines]
    kept: list[str] = []
    separators = 0
    for ln in tidied:
        if not ln:
            continue
        if _SEPARATOR.match(ln):
            separators += 1
            continue
        kept.append(ln)
    if separators:
        notes.append({"kind": "separator", "count": separators, "examples": [],
                      "text": f"{separators} ruled line{'' if separators == 1 else 's'} "
                              f"from a table border ignored."})

    delimiter = _delimiter_of(kept)
    rows = [_split_cells(ln, delimiter) for ln in kept]
    rows = [[c for c in r] for r in rows if any(c.strip() for c in r)]

    # A heading row, if the first row is one. Checked before anything is read as
    # a name so that "TABLE_NAME" at the top of an Excel paste is not offered as
    # a table called TABLE_NAME.
    heading: list[str] | None = None
    if rows:
        first = [_strip_cell(c) for c in rows[0] if c.strip()]
        if first and any(_is_heading(c) for c in first) and not all(
            _looks_like_a_name(c) and not _is_heading(c) for c in first
        ):
            heading = [_strip_cell(c) for c in rows[0]]
            notes.append({"kind": "heading", "count": 1,
                          "examples": [" · ".join(first)[:120]],
                          "text": "1 line looked like a heading row and was ignored."})
            rows = rows[1:]

    column: dict | None = None
    cells: list[str] = []
    if delimiter and rows:
        index, column = _pick_column(rows, heading)
        for r in rows:
            cells.append(_strip_cell(r[index]) if index < len(r) else "")
        if column and column["columns"] > 1:
            dropped = column["columns"] - 1
            where = (f'the column headed "{column["heading"]}"' if column.get("heading")
                     else f"column {column.get('position', column['index'] + 1)}")
            notes.append({
                "kind": "column", "count": dropped, "examples": [],
                "text": f"The paste had {column['columns']} columns. Ripple read {where} "
                        f"and ignored the other {dropped}.",
            })
    else:
        for r in rows:
            cells.extend(_strip_cell(c) for c in r)

    entries: list[Entry] = []
    seen: dict[str, Entry] = {}
    duplicates: list[str] = []
    same_table: list[str] = []
    rejected: list[str] = []
    headings_inline = 0
    for cell in cells:
        if not cell:
            continue
        if _is_heading(cell) and not _TABLE_NAME.match(cell):
            headings_inline += 1
            continue
        entry = _classify(cell)
        if entry is None:
            rejected.append(cell[:80])
            continue
        marker = f"{entry.kind}:{entry.key}"
        if marker in seen:
            kept = seen[marker]
            # The same name twice is a duplicate. Two *different* names that
            # Ripple cannot tell apart is a different thing entirely, and it has
            # to be said rather than quietly counted as a duplicate: SQL only
            # ever tells Ripple the last part of a table name.
            if cell.upper() == kept.given.upper():
                duplicates.append(cell)
            else:
                same_table.append(f"{kept.given} and {cell}")
            continue
        seen[marker] = entry
        entries.append(entry)

    if headings_inline:
        notes.append({"kind": "heading", "count": headings_inline, "examples": [],
                      "text": f"{headings_inline} more line{'' if headings_inline == 1 else 's'} "
                              f"looked like a heading and {'was' if headings_inline == 1 else 'were'} ignored."})
    if duplicates:
        notes.append({"kind": "duplicate", "count": len(duplicates),
                      "examples": duplicates[:6],
                      "text": f"{len(duplicates)} duplicate"
                              f"{'' if len(duplicates) == 1 else 's'} removed."})
    if rejected:
        notes.append({"kind": "rejected", "count": len(rejected), "examples": rejected[:6],
                      "text": f"{len(rejected)} line{'' if len(rejected) == 1 else 's'} did not "
                              f"look like a table name and {'was' if len(rejected) == 1 else 'were'} "
                              f"ignored."})

    if same_table:
        notes.append({
            "kind": "sameTable", "count": len(same_table), "examples": same_table[:6],
            "text": f"{len(same_table)} pair{'' if len(same_table) == 1 else 's'} of names "
                    f"{'is' if len(same_table) == 1 else 'are'} the same table to Ripple, so "
                    f"only the first of each was kept. SQL only "
                    f"ever says the last part of a table name, which means two datasets holding "
                    f"a table of the same name cannot be told apart.",
        })

    return ProductionRule(text=raw, entries=tuple(entries), notes=tuple(notes), column=column)


# Kept under its old name: the old rule was "a comma separated list of patterns",
# and everything that called it still gets exactly that.
def parse_production_rule(text: str) -> tuple[str, ...]:
    return tuple(e.given for e in parse(text).entries)


@dataclass
class ProductionRule:
    """A pasted list, read. Immutable in practice -- rebuilt when the text changes."""

    text: str = ""
    entries: tuple[Entry, ...] = ()
    notes: tuple[dict, ...] = ()
    column: dict | None = None
    _names: frozenset = field(default=frozenset(), repr=False, compare=False)
    _globs: tuple = field(default=(), repr=False, compare=False)
    _suffixes: tuple = field(default=(), repr=False, compare=False)

    def __post_init__(self) -> None:
        # Exact names are a set lookup, because a real list is hundreds long and
        # this is asked once per table visited on every hop of every scan.
        object.__setattr__(self, "_names",
                           frozenset(e.key for e in self.entries if e.kind == "name"))
        object.__setattr__(self, "_globs",
                           tuple(e.key for e in self.entries if e.kind == "glob"))
        object.__setattr__(self, "_suffixes",
                           tuple(e.key for e in self.entries if e.kind == "endswith"))

    # ── matching ───────────────────────────────────────────────────────────
    def matches(self, table: str) -> bool:
        name = (table or "").strip()
        if not name:
            return False
        bare = name.rsplit(".", 1)[-1].upper()
        if bare in self._names:
            return True
        for pattern in self._globs:
            if fnmatch(bare, pattern):
                return True
        for pattern in self._suffixes:
            if bare.endswith(pattern):
                return True
        return False

    # ── what it is made of ─────────────────────────────────────────────────
    @property
    def names(self) -> tuple[Entry, ...]:
        return tuple(e for e in self.entries if e.kind == "name")

    @property
    def patterns(self) -> tuple[Entry, ...]:
        return tuple(e for e in self.entries if e.is_pattern)

    def is_empty(self) -> bool:
        return not self.entries

    def one_line(self) -> str:
        """The rule as one short line, for a status row rather than a screen.

        A list of two hundred table names does not fit on a line and pretending
        otherwise produces a row of dots. So a long list is counted instead.
        """
        names, patterns = self.names, self.patterns
        if not self.entries:
            return "not set"
        if len(self.entries) <= 4:
            return ", ".join(e.given for e in self.entries)
        bits = []
        if names:
            bits.append(f"{len(names)} table name{'' if len(names) == 1 else 's'}")
        if patterns:
            bits.append(f"{len(patterns)} pattern{'' if len(patterns) == 1 else 's'} "
                        f"({', '.join(e.given for e in patterns[:3])}"
                        f"{'…' if len(patterns) > 3 else ''})")
        return " and ".join(bits)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "entries": [e.to_dict() for e in self.entries],
            "names": [e.given for e in self.names],
            "patterns": [e.given for e in self.patterns],
            "nameCount": len(self.names),
            "patternCount": len(self.patterns),
            "notes": [dict(n) for n in self.notes],
            "column": self.column,
            "oneLine": self.one_line(),
        }


EMPTY = ProductionRule()


# ── checking the list against the repository that was actually read ────────
def check_against_repo(rule: ProductionRule, index, parsed) -> dict:
    """Which of these tables Ripple has actually seen, and which it has not.

    This is the point of taking a pasted list at all. If fifty tables are pasted
    and Ripple only ever sees forty-four of them, the other six are either
    misspelled or built somewhere it could not read -- and both of those have to
    be known *before* a result from this list is believed, not after.

    Three answers, and the difference between them matters:

    * **found** -- the table is in the SQL Ripple read.
    * **written down** -- the name is in the repository, but not in any statement
      Ripple could turn into a table. Something builds it out of reach.
    * **nowhere** -- the name is not in this repository at all. A typo, a table
      from another repository, or one that is created by a tool.
    """
    known = _table_names(parsed)
    names = rule.names
    found: list[dict] = []
    unseen: list[Entry] = []
    for e in names:
        if e.key in known:
            found.append({"given": e.given, "key": e.key, "state": "found"})
        else:
            unseen.append(e)

    # One pass over the files for everything that was not in the parsed SQL,
    # rather than one pass per name: a real repository is tens of megabytes.
    mentions: dict[str, int] = {}
    if unseen and index is not None and getattr(index, "files", None):
        wanted = {e.key: 0 for e in unseen}
        pattern = index._pattern([e.key for e in unseen])
        for f in index.files:
            hits = {m.upper() for m in pattern.findall(f.text)}
            for hit in hits:
                if hit in wanted:
                    wanted[hit] += 1
        mentions = wanted

    missing: list[dict] = []
    for e in unseen:
        seen_in = mentions.get(e.key, 0)
        # A name nobody uses as a table may still be a naming convention that
        # was meant as a pattern. Said out loud rather than guessed at, because
        # silently re-reading it as a pattern is how a rule stops meaning what
        # it says.
        ends_with = sum(1 for t in known if t.endswith(e.key) and t != e.key)
        missing.append({
            "given": e.given, "key": e.key,
            "state": "written" if seen_in else "nowhere",
            "files": seen_in,
            "endsWith": ends_with,
        })

    pattern_hits: list[dict] = []
    for e in rule.patterns:
        hit = sorted(t for t in known
                     if (fnmatch(t, e.key) if e.kind == "glob" else t.endswith(e.key)))
        pattern_hits.append({"given": e.given, "kind": e.kind, "matches": len(hit),
                             "examples": hit[:6]})

    return {
        "checked": bool(known),
        "tablesKnown": len(known),
        "found": found,
        "missing": missing,
        "patterns": pattern_hits,
        "foundCount": len(found),
        "missingCount": len(missing),
    }


def _table_names(parsed) -> set[str]:
    """Every table name in the SQL Ripple understood: written or read."""
    if parsed is None:
        return set()
    cached = getattr(parsed, "_table_names_cache", None)
    if cached is not None and cached[0] == len(parsed.statements):
        return cached[1]
    names: set[str] = set()
    for s in parsed.statements:
        if s.target:
            names.add(s.target.rsplit(".", 1)[-1].upper())
        for src in s.sources:
            if src:
                names.add(src.rsplit(".", 1)[-1].upper())
    try:
        parsed._table_names_cache = (len(parsed.statements), names)
    except Exception:      # pragma: no cover - a stand-in object in a test
        pass
    return names
````

### ripple/progress.py

Create the file `ripple/progress.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""What Ripple is doing right now, so a screen can say so while it waits.

On a repository the size of the one this was built for -- a couple of thousand
files, single statements six hundred lines long -- reading takes minutes and a
scan takes about a minute. A screen that says nothing for that long looks
broken, and the honest answer to "is it still going?" is a number that is
actually going up.

Two rules this file keeps, and they are the whole reason it is this small:

* Every number here is counted, never estimated. ``done`` is files that have
  really been read. Nothing is smoothed, nothing is extrapolated, and nothing
  moves on a timer.
* ``total`` is zero when there genuinely is no total. Following a chain looks at
  as many statements as it turns out to need, so there is no denominator, and
  inventing one to fill a progress bar would be inventing the one number on the
  screen nobody could check.
"""
from __future__ import annotations

_state: dict = {"job": "", "label": "", "done": 0, "total": 0}


def start(job: str, label: str = "") -> None:
    _replace({"job": job, "label": label, "done": 0, "total": 0})


def step(done: int, total: int, label: str = "") -> None:
    _replace({"job": _state.get("job", ""), "label": label or _state.get("label", ""),
              "done": done, "total": total})


def finish() -> None:
    _replace({"job": "", "label": "", "done": 0, "total": 0})


def snapshot() -> dict:
    """What to show. A copy, so a read cannot catch a half-written update."""
    now = _state
    return {
        "job": now.get("job", ""),
        "label": now.get("label", ""),
        "done": now.get("done", 0),
        # Zero means "not known", and the screen says so rather than drawing a bar.
        "total": now.get("total", 0),
    }


def _replace(new: dict) -> None:
    # Swapped whole rather than edited in place: another request can be reading
    # this at any moment, and half of one update and half of the next would put
    # a number on screen that was never true.
    global _state
    _state = new


def reader(job: str):
    """A callback to hand to the engine, and the job name it reports under."""
    start(job)

    def on_progress(done: int, total: int, label: str = "") -> None:
        step(done, total, label)

    return on_progress
````

### ripple/providers.py

Create the file `ripple/providers.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Which AI provider a key belongs to, worked out from the key itself.

One box on the screen, not three. Somebody pasting a key should not have to
tell Ripple which company issued it: the key says so in its first few
characters, and asking is one more thing to get wrong on a screen whose whole
job is to be checkable.

All three providers speak the same OpenAI-shaped ``/chat/completions``, so
there is one code path and only the address, the key and the model change.
Google's is its own OpenAI-compatible endpoint, which was confirmed live rather
than taken from documentation.

The model list is NOT written down here. A hand-typed list of model names is
wrong within months and then tells somebody a model exists that does not. It is
fetched from the provider with the key they just pasted, which proves the key
and produces the real list in the same call. The names below are only an
ORDER OF PREFERENCE applied to whatever comes back -- if none of them is in the
list, the first usable model is used and the screen says which.
"""
from __future__ import annotations

PROVIDERS: tuple[dict, ...] = (
    {
        "id": "openai",
        "label": "OpenAI",
        # Longest first: a project key starts with the legacy prefix too.
        "prefixes": ("sk-proj-", "sk-svcacct-", "sk-admin-", "sk-"),
        "base_url": "https://api.openai.com/v1",
        "where": "platform.openai.com/api-keys",
        "prefer": ("gpt-5", "gpt-4.1", "gpt-4o", "gpt-4o-mini", "gpt-4.1-mini"),
    },
    {
        "id": "gemini",
        "label": "Google Gemini",
        "prefixes": ("AIza",),
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "where": "aistudio.google.com/apikey",
        "prefer": ("gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash",
                   "gemini-1.5-pro", "gemini-1.5-flash"),
    },
    {
        "id": "groq",
        "label": "Groq",
        "prefixes": ("gsk_",),
        "base_url": "https://api.groq.com/openai/v1",
        "where": "console.groq.com",
        "prefer": ("openai/gpt-oss-120b", "llama-3.3-70b-versatile",
                   "openai/gpt-oss-20b", "llama-3.1-8b-instant"),
    },
)

# Keys Ripple can recognise but cannot use.
#
# Naming the company beats "that key was rejected", which sends somebody to
# check a key that is perfectly good. It also stops an Anthropic key being read
# as an OpenAI one: both begin "sk-", and without this the longer prefix would
# be tested against the shorter one and lose.
KNOWN_BUT_UNSUPPORTED: tuple[dict, ...] = (
    {"prefixes": ("sk-ant-",), "label": "Anthropic"},
    {"prefixes": ("hf_",), "label": "Hugging Face"},
    {"prefixes": ("xai-",), "label": "xAI"},
    {"prefixes": ("sk-or-",), "label": "OpenRouter"},
    {"prefixes": ("r8_",), "label": "Replicate"},
    {"prefixes": ("ghp_", "github_pat_"), "label": "GitHub"},
)

# Model ids that are not chat models. A provider's list is mostly these -- audio,
# images, embeddings, moderation - and offering one produces a baffling failure
# at the moment somebody is trying to read an email.
_NOT_CHAT = (
    "embed", "embedding", "whisper", "tts", "audio", "speech", "transcribe",
    "dall-e", "image", "imagen", "vision-only", "moderation", "rerank",
    "guard", "safety", "veo", "video", "clip", "distil-whisper", "playai",
    "aqa", "learnlm", "gemma",
)


def detect(key: str) -> dict | None:
    """The provider that issued this key, or None if it is not one we can use."""
    key = (key or "").strip()
    if not key:
        return None
    for unsupported in KNOWN_BUT_UNSUPPORTED:
        if key.startswith(unsupported["prefixes"]):
            return None
    best: dict | None = None
    longest = -1
    for provider in PROVIDERS:
        for prefix in provider["prefixes"]:
            if key.startswith(prefix) and len(prefix) > longest:
                best, longest = provider, len(prefix)
    return best


def name_of_unsupported(key: str) -> str:
    """The company whose key this is, when Ripple cannot use it. '' otherwise."""
    key = (key or "").strip()
    for unsupported in KNOWN_BUT_UNSUPPORTED:
        if key.startswith(unsupported["prefixes"]):
            return unsupported["label"]
    return ""


def by_id(provider_id: str) -> dict | None:
    for provider in PROVIDERS:
        if provider["id"] == provider_id:
            return provider
    return None


def is_chat_model(model_id: str) -> bool:
    """Could this model hold a conversation and return JSON?

    Deliberately a denylist rather than an allowlist. A new chat model appearing
    and being hidden is the worse mistake: it looks like the provider is broken.
    """
    low = (model_id or "").lower()
    if not low:
        return False
    return not any(word in low for word in _NOT_CHAT)


def rank_models(provider: dict | None, models: list[str]) -> list[str]:
    """The provider's own list, with the ones we would choose first at the top.

    Everything the provider returned is kept. Ripple has no business hiding a
    model somebody is paying for because it has not heard of it.
    """
    usable = [m for m in models if is_chat_model(m)]
    prefer = list((provider or {}).get("prefer", ()))

    def rank(model_id: str) -> tuple:
        low = model_id.lower()
        for i, wanted in enumerate(prefer):
            if low == wanted.lower():
                return (0, i, low)
        for i, wanted in enumerate(prefer):
            if low.startswith(wanted.lower()):
                return (1, i, low)
        return (2, 0, low)

    return sorted(usable, key=rank)
````

### ripple/store.py

Create the file `ripple/store.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""History of past notifications, so nothing gets lost between people.

A single SQLite file. On a serverless host the filesystem is read-only apart
from /tmp, so the path is configurable and a failure to write is reported
rather than crashing the request.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings, settings as default_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at   TEXT NOT NULL,
  subject      TEXT,
  source       TEXT,
  change_type  TEXT,
  effective    TEXT,
  risk         TEXT,
  status       TEXT NOT NULL DEFAULT 'New',
  mode         TEXT,
  vals_json    TEXT,
  scan_json    TEXT,
  summary_json TEXT
);
"""

STATUSES = ("New", "In progress", "Verified", "Closed")


def _connect(cfg: Settings) -> sqlite3.Connection:
    path = Path(cfg.db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # A longer wait than the default five seconds, for one specific reason: this
    # file usually sits in a folder OneDrive is syncing, and OneDrive holds a
    # file open while it uploads it. Five seconds is short enough to lose a
    # saved analysis to a routine upload; fifteen rides it out. If the lock is
    # real rather than passing, the caller still gets a plain refusal.
    con = sqlite3.connect(path, timeout=15)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


KEPT_NOTE = (
    "Saved on the machine that handled this request. This copy of Ripple runs on a "
    "serverless host, which throws that machine away and starts a fresh one, so this "
    "entry can disappear at any time -- often within minutes. Treat the list of past "
    "analyses as a scratchpad here, not a record. Copy anything you need to keep."
)


def save(vals: dict, scan: dict, summary: dict, mode: str,
         cfg: Settings | None = None) -> dict:
    cfg = cfg or default_settings
    try:
        con = _connect(cfg)
    except (sqlite3.Error, OSError) as exc:
        return {"saved": False, "reason": f"history is unavailable here ({exc})"}
    try:
        with con:
            cur = con.execute(
                """INSERT INTO analyses
                   (created_at, subject, source, change_type, effective, risk, status,
                    mode, vals_json, scan_json, summary_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    vals.get("subject", ""),
                    vals.get("source", ""),
                    vals.get("changeType", ""),
                    vals.get("effectiveDate", ""),
                    scan.get("risk", "none"),
                    "New",
                    mode,
                    json.dumps(vals),
                    json.dumps(scan),
                    json.dumps(summary),
                ),
            )
        out = {"saved": True, "id": cur.lastrowid}
        if cfg.serverless:
            out["note"] = KEPT_NOTE
        return out
    finally:
        con.close()


def listing(cfg: Settings | None = None, limit: int = 50) -> list[dict]:
    cfg = cfg or default_settings
    try:
        con = _connect(cfg)
    except (sqlite3.Error, OSError):
        return []
    try:
        rows = con.execute(
            """SELECT id, created_at, subject, source, change_type, effective, risk, status, mode
               FROM analyses ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()


def get(analysis_id: int, cfg: Settings | None = None) -> dict | None:
    cfg = cfg or default_settings
    try:
        con = _connect(cfg)
    except (sqlite3.Error, OSError):
        return None
    try:
        r = con.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        if not r:
            return None
        d = dict(r)
        for k in ("vals_json", "scan_json", "summary_json"):
            d[k] = json.loads(d[k]) if d.get(k) else None
        return d
    finally:
        con.close()


def set_status(analysis_id: int, status: str, cfg: Settings | None = None) -> bool:
    if status not in STATUSES:
        return False
    cfg = cfg or default_settings
    try:
        con = _connect(cfg)
    except (sqlite3.Error, OSError):
        return False
    try:
        with con:
            cur = con.execute(
                "UPDATE analyses SET status = ? WHERE id = ?", (status, analysis_id)
            )
        return cur.rowcount > 0
    finally:
        con.close()
````

## Paste 5 of 25

### ripple/scanner/dialectcompat.py

Create the file `ripple/scanner/dialectcompat.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Reading the parse tree the same way whichever sqlglot is installed.

sqlglot renames the keys inside its own nodes between major versions, and three
of the renames that matter here are SILENT: the old key simply returns None, so
the code carries on and finds nothing. Two of the three switch off things this
tool exists to do --

* ``Star.args["except"]`` became ``except_``. Read the old key and
  ``SELECT * EXCEPT(col)`` stops being noticed, so a column that is dropped by
  name is reported as carried through.
* ``Merge.args["expressions"]`` became ``whens`` (wrapped in a ``Whens`` node).
  Read the old key and every rename a MERGE makes disappears -- and a MERGE is
  how a published table is normally loaded.

-- and the third, ``Select.args["from"]`` becoming ``from_``, quietly empties
the check that decides which tables a ``SELECT *`` covers.

None of that raises. The tests would go on passing on the version that is
installed today and the answers would go quietly wrong on any newer one. So
every one of those keys is read through a function here, and there is a test
that fails loudly if a key stops resolving at all.
"""
from __future__ import annotations

from sqlglot import exp

# ALTER TABLE a RENAME TO b. The one rename that is loud -- the class simply
# stops existing -- but it belongs with the rest.
RENAME_NODE = getattr(exp, "AlterRename", None) or getattr(exp, "RenameTable")


def from_of(select: exp.Select):
    """The FROM clause of a SELECT."""
    return select.args.get("from") or select.args.get("from_")


def star_except(star: exp.Star) -> list:
    """The columns named in ``SELECT * EXCEPT(a, b)``."""
    return list(star.args.get("except") or star.args.get("except_") or [])


def star_replace(star: exp.Star) -> list:
    """The columns swapped by ``SELECT * REPLACE(x AS a)``."""
    return list(star.args.get("replace") or star.args.get("replace_") or [])


def is_unpivot(pivot: exp.Expression) -> bool:
    """PIVOT turns rows into columns; UNPIVOT turns columns into rows."""
    return bool(pivot.args.get("unpivot"))


def pivot_fields(pivot: exp.Expression) -> list:
    """The ``FOR x IN (...)`` parts of a PIVOT or UNPIVOT.

    Where the names live. For an UNPIVOT the IN list IS the column list being
    folded away, so reading the wrong key means a statement that hard-fails on
    the day the column goes is reported as carrying it through untouched.
    """
    fields = pivot.args.get("fields")
    if fields is None:
        fields = pivot.args.get("field")
    if fields is None:
        return []
    return list(fields) if isinstance(fields, list) else [fields]


def pivot_columns(pivot: exp.Expression) -> list[str]:
    """The output column names a PIVOT produces -- ``total_Q1``, ``total_Q2``.

    sqlglot works these out itself, which is worth having: the rule involves the
    aggregate's alias, whether it has one, and each IN value. Empty means it did
    not, and the caller must not pretend it knows the names.
    """
    return [c.name if hasattr(c, "name") else str(c)
            for c in (pivot.args.get("columns") or [])]


def is_temporary(stmt: exp.Expression | None) -> bool:
    """Was this CREATE written as TEMP or TEMPORARY?

    A temporary table lives inside one script and is gone when it ends, so two
    files that both call one ``t`` are not sharing a table. Read the wrong key
    and they get merged, which invents a chain to a published table nobody
    touched -- and the finding on it looks exactly like a real one.
    """
    props = getattr(stmt, "args", {}).get("properties") if stmt is not None else None
    node = getattr(exp, "TemporaryProperty", None)
    if props is None or node is None:
        return False
    return any(isinstance(p, node) for p in props.expressions)


def merge_whens(merge: exp.Expression) -> list:
    """Every WHEN branch of a MERGE, whichever shape it arrives in."""
    whens = merge.args.get("whens")
    if whens is not None:
        return list(getattr(whens, "expressions", whens) or [])
    return list(merge.args.get("expressions") or [])


# ── set operations: UNION, INTERSECT, EXCEPT ───────────────────────────────
# sqlglot 25 had only ``exp.Union`` and made INTERSECT and EXCEPT subclasses of
# it. sqlglot 30 introduced ``exp.SetOperation`` as the shared parent. Naming
# either one directly is the same trap as the renamed keys above: on the other
# version the ``find_all`` matches nothing, every branch of every union goes
# unnoticed, and no test fails.
SET_OPERATION = getattr(exp, "SetOperation", None) or exp.Union


def set_branches(node: exp.Expression) -> list[exp.Expression]:
    """The branches of a set operation, in the order they are written.

    A three-way union is nested to the left -- ``Union(Union(a, b), c)`` -- so
    the branches have to be flattened, not read off two keys. Written in the
    file's order because SQL takes the output column names from the FIRST
    branch, and a list in any other order silently renames the wrong one.
    """
    if not isinstance(node, SET_OPERATION):
        return []
    left, right = node.this, node.args.get("expression")
    branches = set_branches(left) if isinstance(left, SET_OPERATION) else [left]
    if right is not None:
        branches += (set_branches(right) if isinstance(right, SET_OPERATION)
                     else [right])
    return [b for b in branches if b is not None]


def output_names(query: exp.Expression) -> list[str]:
    """The names a query publishes its columns under, in order.

    sqlglot works this out itself and gets a union right -- the names come from
    the leftmost branch. Empty means it could not, and the caller must not
    pretend to know them.
    """
    try:
        return list(query.named_selects or [])
    except Exception:                                   # noqa: BLE001
        return []
````

## Paste 6 of 25

### ripple/scanner/lineage.py — piece 1 of 3

Create the file `ripple/scanner/lineage.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Following a column through the pipeline, and saying what it means.

A column rarely keeps its name. MARKET_CODE becomes mc, then mkt_cd, and the
thing that finally breaks is three files away from the one the notification
named. This module walks that chain and groups what it finds under the
production table each chain ends at -- because that is the thing an engineer
actually has to defend.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, replace

from sqlglot import exp

from ..config import Settings, settings as default_settings
from .dialectcompat import merge_whens
from .repo import RepoIndex, unopened_code_types
from .sqlread import (
    ParsedRepo,
    Usage,
    canonical,
    dataset_of,
    is_wildcard,
    reads_metadata,
    same_table,
    wildcard_match,
    mode_of,
    locate,
    output_names,
    short_name,
    snippet,
    suffix_verdict,
    usages_of,
)

# What a given kind of change does to a given kind of usage.
#
# "star" is in none of them, and that is deliberate. A SELECT * does not fail
# when a column disappears -- it quietly builds a narrower table, and the thing
# that breaks is whatever reads the missing column further down. Calling the
# star hop itself breaking would put a red badge on the one row in the chain
# that carries on working.
#
# "pivoted" is in every set but value_change, for the same reason "excluded" is:
# the column is NAMED in the statement, so removing or renaming it stops the SQL
# compiling. A change to its VALUES does not -- an UNPIVOT folds whatever is
# there into rows either way. Reading the type wrong can still break it, because
# every column an UNPIVOT folds together has to share one.
#
# "renamed" and "retyped" are an ALTER TABLE naming the column outright, so they
# fail the same way "select" does. "dropped" is in none of them: an ALTER TABLE
# ... DROP COLUMN of the very column being decommissioned is not broken by the
# change, it IS the change -- and it is worth reporting for exactly that reason.
BREAKS = {
    "removal":      {"filter", "join_key", "ranking", "dedup_key", "transform", "aggregation",
                     "sort", "excluded", "pivoted", "layout", "select", "renamed", "retyped"},
    "rename":       {"filter", "join_key", "ranking", "dedup_key", "transform", "aggregation",
                     "sort", "excluded", "pivoted", "layout", "select", "renamed", "retyped"},
    "value_change": {"filter", "join_key", "transform"},
    "type_change":  {"filter", "join_key", "transform", "pivoted", "layout", "retyped"},
    "unknown":      {"filter", "join_key", "ranking", "dedup_key", "transform", "sort",
                     "pivoted", "layout", "renamed", "retyped"},
}
# Usages with no local fix: the replacement has to come from the upstream team.
NO_LOCAL_FIX = {"ranking", "dedup_key"}


def _impact_sentence(u: Usage, change_type: str, target: str | None,
                     copied_by: str = "", feed: str = "") -> str:
    tgt = feed and f"the delivery at {feed}" or target or "the next table"
    # An EXPORT DATA writes a file to a bucket. There is no published table to
    # gain or lose a column, which is exactly why the answer used to read "no
    # production table is affected" -- true, and no use to anybody: the file
    # somebody else's job reads every morning changes shape or stops arriving.
    if feed and u.kind not in ("filter", "join_key"):
        return (f"This column is written into the file delivered to {feed}. No table in this "
                f"warehouse gains or loses anything - the delivery does, and whoever reads it "
                f"is outside this repository. Tell them before the change ships.")
    lit = f" '{u.detail}'" if u.kind == "filter" and u.detail else ""
    if u.kind == "star":
        # A whole-table COPY does exactly what a SELECT * does, and is followed
        # the same way -- but saying "SELECT *" about a file that says COPY
        # sends somebody to the line to look for a statement that is not there.
        how = (f"This statement copies the whole table with {copied_by}" if copied_by
               else "This statement takes every column with SELECT *")
        return (f"{how}, so the column is carried into "
                f"{tgt} without ever being named. Nothing here fails on the day of the change - "
                f"{tgt} is simply built without the column, and whatever reads it further down is "
                f"what breaks. Ripple cannot see {tgt}'s column list, so everything past this "
                f"point is worked out rather than read.")
    if u.kind == "excluded":
        if u.detail == "REPLACE":
            return (f"This statement puts another value in this column's place by name - "
                    f"SELECT * REPLACE. The column of that name in {tgt} is fed by the "
                    f"replacement from here on, not by this one, so the trail stops here - and "
                    f"the name is written down, so removing or renaming it makes this statement "
                    f"itself fail.")
        return (f"This statement takes every column EXCEPT this one by name. The column never "
                f"reaches {tgt}, so the trail stops here - but the name is written down, so "
                f"removing or renaming it makes this statement itself fail.")
    if u.kind == "renamed":
        return (f"This file renames the column, in {tgt} itself, to "
                f"{u.detail or u.alias}. Everything downstream of {tgt} reads the new name "
                f"from here on, which is why the trail carries on under it - and the old name "
                f"is written on this line, so the migration has to change with it.")
    if u.kind == "dropped":
        return (f"This file already drops the column from {tgt}, by name. The trail stops here: "
                f"nothing built from {tgt} after this statement runs has the column at all. "
                f"Check whether this migration has already run.")
    if u.kind == "retyped":
        return (f"This file changes the column on {tgt} itself. The name is written on this "
                f"line, so removing or renaming it stops the migration running - and a change "
                f"of type here meets whatever type change you are making.")
    if u.kind == "layout":
        how = u.detail or "PARTITION BY"
        return (f"{tgt} is laid out by this column ({how}). Nothing published gains or loses a "
                f"column when it goes -- but the name is written on the CREATE line, so the "
                f"statement stops compiling, {tgt} stops being built, and everything below it "
                f"quietly serves data that has stopped being refreshed.")
    if u.kind == "pivoted":
        if u.detail == "UNPIVOT":
            return (f"This column is named in an UNPIVOT list. Its values are folded into rows "
                    f"under a new column name, so the column itself does not reach {tgt} - but "
                    f"the name is written down here, so removing or renaming it makes this "
                    f"statement fail outright and {tgt} stops loading.")
        return (f"This column is fed into a PIVOT, which turns its values into columns of "
                f"{tgt} under names worked out from each value. The name is written down here, "
                f"so removing or renaming it makes this statement fail outright.")
    if u.kind == "filter":
        if change_type in ("removal", "rename"):
            return (f"Used in a filter here. Once the column is gone this query fails outright, "
                    f"and {tgt} stops loading.")
        return (f"The code filters on a literal value{lit}. After the change that comparison "
                f"stops matching, so {tgt} quietly loads no rows.")
    if u.kind == "join_key":
        if change_type in ("removal", "rename"):
            return f"Joined on this column. Removing it breaks the join and {tgt} fails to build."
        return ("Joined on the raw value. Unless both sides change on the same day, matching rows "
                "are dropped silently - no error, just fewer rows.")
    if u.kind == "ranking":
        return ("This column is the sort order inside a ranking that picks one row per key. "
                "Without it the choice becomes arbitrary - the wrong record can win, and nothing "
                "is raised to tell you.")
    if u.kind == "dedup_key":
        if u.detail == "PARTITION BY":
            return ("This column is the key the ranking is worked out within - one row is kept "
                    "for each value of it. Take the column away and every row falls into a "
                    f"single group, so {tgt} keeps one record for the whole table instead of "
                    "one per key. Nothing fails on the day; the table is simply wrong.")
        return (f"{u.detail or 'An aggregate'} on this column decides which row survives. "
                f"Without it {tgt} can publish stale records with no error.")
    if u.kind == "sort":
        return (f"The rows are sorted by this column on the way into {tgt}. The name is "
                f"written down here, so removing or renaming it stops this statement running "
                f"at all, and {tgt} stops loading.")
    if u.kind == "transform":
        fn = f" ({u.detail})" if u.detail else ""
        return (f"The value is reshaped here{fn}. A change in its format or length produces wrong "
                f"output that flows straight into {tgt}.")
    if u.kind == "aggregation":
        return ("Grouped on this column, so the group labels move with it. Old and new values will "
                "split the history in two unless the table is rebuilt.")
    return (f"Selected straight through into {tgt}. Nothing here depends on the value, but the "
            f"published column changes with it.")


@dataclass
class Finding:
    source_table: str
    source_column: str
    target_table: str | None
    alias: str | None
    logic: str
    kind: str
    mode: str
    impact: str
    breaking: bool
    no_local_fix: bool
    file: str
    lang: str
    lines: list[dict]
    hop: int
    # The attribute the person actually asked about, which two hops down the
    # chain is no longer the column name on this row. A row saying "mc" is
    # unattributable on a scan of three attributes -- and it is the row somebody
    # has to act on. Not part of what makes two findings the same finding: one
    # usage can be on the path of more than one attribute.
    roots: list[str] = field(default_factory=list, compare=False)
    # Whether the statement said which table this column came from. False means
    # the usage is real and on that line, but the same column name is in more
    # than one table the statement reads and the SQL did not say whose it is.
    # Shown, never dropped -- and never asserted either.
    certain: bool = True
    # This hop is carried by a SELECT *, so the table it builds has no column
    # list Ripple can read. The hop is real; everything past it is inferred.
    via_star: bool = False
    # "" when the file really does say SELECT *; otherwise the word it used to
    # copy a whole table instead - COPY, CLONE, LIKE or RENAME. Carried this far
    # so no screen ever tells somebody the file says SELECT * when it does not.
    copied_by: str = ""
    # "" for a statement written as SQL in the file. Otherwise the words the
    # file used to run it as text -- EXECUTE IMMEDIATE. The statement is read
    # exactly as it will run, so this finding is real; but the line it points at
    # holds a quoted string, and a row that does not say so sends somebody to
    # look for a CREATE that is not written there.
    built_as_text: str = ""
    # "" for an ordinary statement. Otherwise where this EXPORT DATA delivers
    # to. The row sits under "builds no table", which is true of it and does not
    # tell the whole story: Ripple knows exactly where this one goes.
    feed_uri: str = ""
    # How many SELECT * hops are behind this finding, counting this one. Zero
    # means every step to here was written down in the SQL.
    inferred_hops: int = 0
    # The line the statement this finding lives in starts on. Part of what makes
    # two findings the same finding, and the reason is worth writing down: one
    # file very often builds several tables, and the same column of the same
    # source table is filtered on in each of them. Without this the second and
    # third statements were folded into the first, so the row shown under a
    # published table pointed at another statement's lines and named another
    # statement's target -- and the count of usages was quietly short.
    at: int = 0
    # The target table as the reader keyed it, which is not always what goes on
    # screen: a temporary table is fenced to the file that built it, and the
    # fence is stripped for display. Anything that walks ONWARDS from a finding
    # has to use this, or it looks the table up by a name that matches every
    # other file's temporary table of the same name -- which is the merge this
    # fence exists to stop, leaking back in one screen further along.
    target_key: str = field(default="", compare=False)

    def key(self) -> tuple:
        return (self.file, self.at, self.source_table, self.source_column, self.kind)


@dataclass
class ScanResult:
    attributes: list[dict] = field(default_factory=list)
    groups: list[dict] = field(default_factory=list)
    # Chains that end somewhere Ripple has not been told is a table this team
    # publishes. These used to be thrown away, which meant a real, breaking
    # impact could be shown as a clean result purely because the tables are not
    # named _PROD. They are reported, and labelled for what they are.
    reached: list[dict] = field(default_factory=list)
    # Usages in code that builds no table Ripple can name -- a bare SELECT, a
    # view it could not follow. Still real usages of the attribute.
    other: list[dict] = field(default_factory=list)
    graphs: list[dict] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    unreadable: list[dict] = field(default_factory=list)
    # How many of those unreadable files actually mention one of the names being
    # followed. The coverage line used to say "N files mention these names and
    # could not be read" about every file in the repository the parser choked
    # on, which on a clean scan printed "3 files mention these names" directly
    # above a row saying the attribute was named in one file and nowhere else.
    # Those two cannot both be true.
    unreadable_on_topic: int = 0
    mentions_only: list[dict] = field(default_factory=list)
    # Files that were never opened at all, which is a different and worse thing
    # than a file that was read and not understood. A scan over a repository
    # half of which was never opened produces a short finding list and a green
    # tick, and that green tick is the only thing this tool sells.
    held_online: list[str] = field(default_factory=list)
    too_long: list[str] = field(default_factory=list)
    # Tables the chain went through that are built with SELECT *. Their column
    # list is nowhere in the SQL, so every hop past one of them is worked out
    # rather than read. This belongs on the scan result and nowhere else: the
    # repository screen has listed these tables for months, and nothing joined
    # it up to the answer, so a scan said "no impact" while the warning sat on
    # a screen nobody was looking at.
    star_tables: list[dict] = field(default_factory=list)
    # Trails Ripple stopped following because the hop limit was reached, not
    # because the code ran out. Without this the setting gets reported as a fact
    # about the warehouse: "the chain ends at t4, it does not reach production".
    cut_short: list[dict] = field(default_factory=list)
    # Table names this repository uses in more than one dataset, where the SQL
    # being followed did not say which one it meant. Ripple treats them as one
    # table -- losing the chain is the worse mistake -- and says so here, so a
    # finding under one of these names is read as being about either.
    merged_names: list[dict] = field(default_factory=list)
    # Wildcard table names the chain was followed through -- ``events_*``. The
    # SQL never named the table being scanned; it named a whole family of
    # date-sharded tables, and this one falls inside it. The finding is real and
    # the statement really does read this table, but "which shard" is a question
    # the file does not answer, and the person acting on it has to know that.
    wildcard_names: list[dict] = field(default_factory=list)
    # Tables on the trail whose name is nowhere in the file that builds them. A
    # dbt model is a bare SELECT with no CREATE: the table it loads is named
    # after the file, by dbt, at run time. Ripple follows that rule -- without it
    # a dbt repository produced no lineage at all -- and then says so here,
    # because somebody sent to that line to check will not find the table
    # written on it, and a finding they cannot verify is one they will dismiss.
    named_by_file: list[dict] = field(default_factory=list)
    # Statements on the trail that the file runs as text -- EXECUTE IMMEDIATE
    # holding a whole CREATE in a quoted string. Ripple reads the string, so the
    # hop is followed rather than lost; the line it points at is a string, and
    # this card is what says so beside the answer instead of on another screen.
    built_as_text: list[dict] = field(default_factory=list)
    # Files Ripple would have read but did not, because they sit in a folder it
    # is told to skip -- build, dist, target, venv. The count reached the
    # repository screen and nothing else, so a scan of a dbt project (whose
    # target/ folder holds the SQL that actually runs) came back `risk none,
    # prod []` with the reason on a screen nobody was looking at.
    # Tables on the trail that more than one file builds from scratch. Only one
    # of those definitions can be the one that runs, and nothing in the files
    # says which -- so both are followed and both are named. See rebuilt_in.
    two_definitions: list[dict] = field(default_factory=list)
    skipped_in_folders: list[str] = field(default_factory=list)
    skipped_folder_names: list[str] = field(default_factory=list)
    # File types Ripple does not open at all, and how many of each are in the
    # repository: {".ipynb": 12, ".tf": 3}. The repository screen has always
    # listed these. The ANSWER never did -- so a middle hop written in a
    # notebook, or in Terraform, or in a file with no extension at all, produced
    # "the name appears, but no lineage to a production table" with nothing
    # anywhere beside it saying a file had been passed over. Measured on a
    # notebook holding the one statement that built the published table.
    # A caveat may never live on a different screen from the answer it
    # qualifies, so it is carried here and counted as a gap in coverage.
    file_types_unopened: dict = field(default_factory=dict)
    # Published tables that are not built FROM this column, but that stop being
    # refreshed because the statement feeding them stops running on the day of
    # the change. A different kind of impact from the findings above, and it
    # must never be presented as the same one.
    stops_loading: list[dict] = field(default_factory=list)
    # DDL that names a table on the trail, or one of the columns being followed,
    # and carries no column anywhere: a search index, a vector index, a row
    # access policy, an UNDROP. Never lineage -- a dependency somebody has to go
    # and change. Before this the whole statement was invisible: the parser gave
    # up on it, the file landed on the "check by hand" list, and nothing said
    # which table or which column it was about.
    referenced_here: list[dict] = field(default_factory=list)
    # Deliveries out of the warehouse -- EXPORT DATA writing a file to a bucket
    # somebody else's job picks up. An export builds no table, so the trail had
    # nothing to carry the column on to, and the answer read "no production
    # table is affected": true, and useless. The delivery that breaks belongs to
    # another team, and until now it was named on no screen at all.
    feeds: list[dict] = field(default_factory=list)
    # True when the walk that found them hit its own ceiling. A cap nobody is
    # told about reads as "there were only these".
    stops_loading_capped: bool = False
    # Every attribute asked about turned out to be a name Ripple never saw as a
    # column anywhere, and nothing was found. That is not "no impact" -- it is
    # the question not having been answered, and printed as a green tick it is
    # the most convincing wrong answer this tool can give.
    lookup_failed: bool = False
    max_hops: int = 0
    files_scanned: int = 0
    files_matched: int = 0
    risk: str = "none"

    def to_dict(self) -> dict:
        return {
            "attributes": self.attributes,
            "groups": self.groups,
            "reached": self.reached,
            "other": self.other,
            "graphs": self.graphs,
            "unreadable": self.unreadable,
            "mentionsOnly": self.mentions_only,
            "heldOnline": self.held_online,
            "pathTooLong": self.too_long,
            "starTables": self.star_tables,
            "cutShort": self.cut_short,
            "mergedNames": self.merged_names,
            "wildcardNames": self.wildcard_names,
            "namedByFile": self.named_by_file,
            "builtAsText": self.built_as_text,
            "twoDefinitions": self.two_definitions,
            "skippedInFolders": self.skipped_in_folders,
            "skippedFolderNames": self.skipped_folder_names,
            "fileTypesUnopened": [{"ext": k, "count": n} for k, n
                                  in sorted(self.file_types_unopened.items(),
                                            key=lambda kv: (-kv[1], kv[0]))],
            "stopsLoading": self.stops_loading,
            "referencedHere": self.referenced_here,
            "feeds": self.feeds,
            "stopsLoadingCapped": self.stops_loading_capped,
            "maxHops": self.max_hops,
            "filesScanned": self.files_scanned,
            "filesMatched": self.files_matched,
            "risk": self.risk,
            "lookupFailed": self.lookup_failed,
            "coverage": self.coverage(),
            "stats": self.stats(),
        }

    def coverage(self) -> dict:
        """How much of this trail Ripple could actually see.

        "No impact, and I could follow every step of it" and "no impact, and
        three tables on the way were invisible to me" printed identically: one
        three-word badge, computed from nothing but whether a finding was
        breaking. Everything below was already counted and then thrown away.

        Deliberately counts, not a percentage. There is no honest denominator
        for "how much of a trail exists" -- a made-up one would put a precise
        number on a guess, which is the one thing this tool may not do. The
        files ratio IS real, because both halves are files Ripple listed.
        """
        # Each line is written twice, for one and for more than one. Printed
        # plural-only these read "1 findings are on a line" and "1 trails were
        # still going", which is the sort of thing that makes a careful tool
        # look careless on the exact screen where care is what it is selling.
        on_topic = min(self.unreadable_on_topic, len(self.unreadable))
        gaps = [
            (len(self.unreadable),
             "file could not be read" + (
                 f", and it mentions these names" if on_topic else ""),
             "files could not be read" + (
                 f", and {on_topic} of them mention these names" if on_topic else "")),
            (len(self.held_online) + len(self.too_long),
             "file was never opened at all",
             "files were never opened at all"),
            # Written for somebody reading a scan for the first time. "On the
            # trail", "hop limit" and "worked out rather than read" are Ripple's
            # own vocabulary, and this is the list a person reads to decide
            # whether to believe the answer above it.
            (len(self.star_tables),
             "table the column passes through takes every column at once, so your "
             "code never lists what its columns are called",
             "tables the column passes through take every column at once, so your "
             "code never lists what their columns are called"),
            (len(self.cut_short),
             "trail was still going when Ripple stopped following it",
             "trails were still going when Ripple stopped following them"),
            (len([f for f in self.findings if f.inferred_hops]),
             "finding comes after one of those tables, so Ripple worked the column "
             "name out rather than reading it",
             "findings come after one of those tables, so Ripple worked the column "
             "names out rather than reading them"),
            (len(self.merged_names),
             "name here stands for more than one table, and the SQL does not say which",
             "names here stand for more than one table, and the SQL does not say which"),
            (len([f for f in self.findings if not f.certain]),
             "finding is on a line that did not say which table the column came from",
             "findings are on a line that did not say which table the column came from"),
            (len(self.skipped_in_folders),
             "code file was walked past because of the folder it sits in",
             "code files were walked past because of the folder they sit in"),
            (sum(self.file_types_unopened.values()),
             "file is of a type Ripple does not open, so anything written in "
             "it was never read",
             "files are of a type Ripple does not open, so anything written in "
             "them was never read"),
        ]
        found = [{"count": n, "what": one if n == 1 else many}
                 for n, one, many in gaps if n]
        return {
            "complete": not found,
            "gaps": found,
            # Both halves are files Ripple listed, so this ratio is a fact.
            "filesMatched": self.files_matched,
            "filesUnread": len(self.unreadable),
        }

    def stats(self) -> dict:
        inter = {f.source_table for f in self.findings if f.hop > 0}
        inter |= {f.target_table for f in self.findings if f.target_table}
        prod = {g["prod"] for g in self.groups}
        inter = {t for t in inter if t and t not in prod}
        return {
            "productionTables": len(self.groups),
            "tablesReached": len(self.reached),
            "intermediateTables": len(inter),
            # Counted over the attributes that were actually confirmed, not over
            # every column name a finding touches -- a column renamed twice on
            # the way down is one attribute, and the card says "of those you
            # confirmed", so it has to be true of that number.
            "attributesImpacted": len([a for a in self.attributes if a.get("found")]),
            "filesWithImpact": len({f.file for f in self.findings}),
            "breakingUsages": len([f for f in self.findings if f.breaking]),
            "couldNotRead": len(self.unreadable),
            "neverOpened": len(self.held_online) + len(self.too_long),
            # Tables on the trail whose column list is not written down, and
            # findings that sit on the far side of one. Both counts, because
            # "3 tables Ripple could not see inside" and "40 findings that
            # depend on them" are different sizes of the same problem.
            "tablesNotVisible": len(self.star_tables),
            "inferredFindings": len([f for f in self.findings if f.inferred_hops]),
            "trailsCutShort": len(self.cut_short),
            # Not added to productionTables: nothing about these tables'
            # columns changes, and one number covering two different kinds of
            # impact is a number that means neither.
            "productionStopsLoading": len(self.stops_loading),
            # Kept out of productionTables for the same reason: a file delivered
            # to a bucket is not a published table, and one number covering two
            # different kinds of impact is a number that means neither.
            "feedsBroken": len([f for f in self.feeds if f["breaking"]]),
        }


def _kind_of_node(name: str, cfg: Settings) -> str:
    if cfg.is_production_table(name):
        return "Prod"
    up = name.upper()
    if up.startswith("TEMP") or "_TEMP" in up:
        return "Temp"
    if up.endswith("_ODL") or "_ODL" in up:
        return "ODL"
    return "ETL"


def trace(
    index: RepoIndex,
    parsed: ParsedRepo,
    upstream: list[dict],
    change_type: str = "unknown",
    cfg: Settings | None = None,
    on_progress=None,
) -> ScanResult:
    """upstream is [{"table": "CUSTOMER_DEMOGRAPHICS", "attrs": ["MARKET_CODE"]}].

    ``on_progress(done, total, label)`` is called as the chain is followed. It
    is deliberately given no total: how many statements a scan will look at
    depends on what it finds as it goes, and a fraction of a number nobody knows
    is a made-up fraction. The count of what has actually been looked at is a
    real thing to show.
    """
    cfg = cfg or default_settings
    res = ScanResult()
    res.max_hops = cfg.max_hops
    res.files_scanned = len(index.files)
    res.unreadable = list(parsed.unreadable)
    res.held_online = list(index.held_online)
    res.too_long = list(index.too_long)
    # Beside the answer, not on another screen. See ScanResult.skipped_in_folders.
    res.skipped_in_folders = list(index.in_skipped_dirs)
    res.skipped_folder_names = list(index.skipped_dir_names)
    # Already counted while the repository was indexed. Carried onto the ANSWER
    # rather than left on the repository screen. See file_types_unopened.
    res.file_types_unopened = unopened_code_types(index.unknown_ext)
    breaks = BREAKS.get(change_type, BREAKS["unknown"])

    # Searched on the table's own name, not on the whole thing somebody typed.
    # "prj.raw_dataset.customer_demographics" appears in the files as a name with
    # placeholders where the project and dataset are, so looking for it in full
    # matches nothing at all -- and "0 files mention this" is the most convincing
    # possible way to say "no impact".
    all_names: list[str] = []
    for u in upstream:
        all_names.append(short_name(u["table"]))
        all_names.extend(u.get("attrs") or [])
        # A date-sharded table is never written by its own name. The file says
        # ``customer_demographics_*``, so searching the text for the shard finds
        # nothing -- and then every honesty list built off that search is empty
        # too, including the one that says "the name is in this file as text".
        all_names.extend(parsed.wildcards_covering(u["table"]))
    matched_files = {m.file for m in index.search(all_names)}
    res.files_matched = len(matched_files)
    attr_names = [a for u in upstream for a in (u.get("attrs") or [])]
    shared, table_count = _tables_carrying(parsed, attr_names)

    graphs: list[dict] = []
    findings_by_key: dict[tuple, Finding] = {}
    looked = [0]                       # statements examined, for the progress line
    # production table -> ordered findings that lead to it
    prod_groups: dict[str, list[Finding]] = {}
    # the same, for chains that end at a table nothing further is built from
    end_groups: dict[str, list[Finding]] = {}
    # tables whose column list is not written down, and where that was found
    star_seen: dict[str, dict] = {}
    cut_seen: dict[tuple, dict] = {}
    merged_seen: dict[str, dict] = {}
    wild_seen: dict[str, dict] = {}
    # Tables a wildcard genuinely produced a finding for. The card says "the
    # usages below are real"; without this it was printed over an empty list.
    wild_confirmed: set[str] = set()
    # tables whose name came from the file path, not from the statement
    file_named_seen: dict[str, dict] = {}
    # tables more than one file builds from scratch
    forked_seen: dict[str, dict] = {}
    # statements the file runs as text -- EXECUTE IMMEDIATE
    text_sql_seen: dict[tuple, dict] = {}
    # deliveries out of the warehouse -- EXPORT DATA
    feed_seen: dict[tuple, dict] = {}
    # Every table the chain actually stood on. Used at the end to look through
    # the statements Ripple could not understand for one that names any of
    # them -- see _opaque_on_the_trail.
    visited: set[str] = set()

    def note_if_wildcard(name: str) -> None:
        """Say when this table was only reached through a wildcard name.

        The SQL did not name this table. It named ``customer_demographics_*``,
        a whole family of date-sharded tables, and the one being scanned falls
        inside it. The usage is real -- that query reads this table on any day
        its suffix is in range -- but the file cannot say which shard, and a
        finding that does not admit that reads as more precise than it is.

        Nothing is said when the person typed the wildcard themselves. They
        already know; a warning on every scan is a warning nobody reads.

        Recorded here, and only PUT ON THE SCREEN if a finding actually came out
        of one of these patterns. The card says "the usages below are real", and
        it was being printed over an empty list: a wildcard in one dataset and a
        shard in another are not the same table -- ``same_table`` rules on the
        dataset and this does not -- so the pattern covered the name, produced
        nothing, and the card contradicted the answer it sat under.
        """
        if is_wildcard(name):
            return
        key = short_name(name).upper()
        if key in wild_seen:
            return
        found = parsed.wildcards_covering_how(name)
        if found:
            wild_seen[key] = {
                "table": short_name(name),
                "patterns": [p for p, _ in found],
                # The family name typed without the separator BigQuery requires.
                # A guess about what somebody meant, and it gets its own line.
                "shorthand": [p for p, how in found if how == "family"],
            }

    def note_if_merged(name: str, matched: list, hop: int) -> None:
        """Say when following this name really did pull in more than one table.

        Reported because it happened, not because it might have. Two tables of
        the same name in two named datasets are kept apart, and nothing is said;
        what gets reported is a match that only held because one side said
        nothing -- ``archive_dataset.cust_stage`` matched by a bare
        ``cust_stage`` somewhere else.

        Ripple always follows those, because missing a chain is far worse than
        showing a row somebody can dismiss by opening the file. What it must not
        do is stay quiet, or the finding reads as a fact about one table when it
        may be about the other.

        Capitals are the same problem wearing a different hat: BigQuery treats
        ccm_Wireless_Enroll and ccm_wireless_enroll as two different tables, and
        Ripple matches them as one.
        """
        key = short_name(name).upper()
        if key in merged_seen:
            return
        spellings = parsed.spellings_for(name)
        if len(spellings) > 1:
            merged_seen[key] = {
                "table": short_name(name), "reason": "capitals",
                "spellings": spellings, "datasets": parsed.datasets_for(name),
            }
            return
        def record() -> None:
            merged_seen[key] = {
                "table": short_name(name), "reason": "dataset",
                "spellings": spellings, "datasets": parsed.datasets_for(name),
            }

        if hop == 0:
            # The first name came from a person, not from the code. Somebody
            # typing "customer_demographics" without its dataset is not an
            # ambiguity in the warehouse, and flagging it would put a warning on
            # every scan ever run. It only matters if the repository really does
            # have that name in more than one dataset.
            if len(parsed.datasets_for(name)) > 1:
                record()
            return
        here = dataset_of(name).upper()
        for stmt in matched:
            for src in stmt.sources:
                if same_table(src, name) and dataset_of(src).upper() != here:
                    record()
                    return

    def show(name: str) -> str:
        """A table name as it should appear on screen. Dataset-qualified only
        where this repository uses the same short name in two datasets."""
        return parsed.display(name)

    for up in upstream:
        # What was typed is what gets shown; what gets followed is the table it
        # names. A project id in front of it is dropped, so a name typed in full
        # still finds the same table the SQL writes with a placeholder there.
        typed = up["table"]
        table = canonical(typed)
        # Only worked out when a lookup actually fails, and then only once for
        # the whole table. It walks every statement in the repository and opens
        # every column of the ones that read this table -- cheap on a scan that
        # needs it, minutes across a repository the size of his on every scan
        # that does not.
````

## Paste 7 of 25

### ripple/scanner/lineage.py — piece 2 of 3

Add this to the END of `ripple/scanner/lineage.py`, straight after what is already there. Do not start a new file. Do not re-type anything above.

````python
        columns_cache: list[list[str]] = []

        def columns_here() -> list[str]:
            if not columns_cache:
                columns_cache.append(_columns_on(parsed, table)[:MAX_COLUMNS_SHOWN])
            return columns_cache[0]
        for attr in up.get("attrs") or []:
            branches: list[list[dict]] = []
            end_branches: list[list[dict]] = []
            attr_findings: list[Finding] = []
            attr_cut: list[dict] = []

            def walk(cur_table: str, cur_col: str, hop: int, path: list[dict],
                     chain: list[Finding], seen: set, inferred: int) -> tuple[bool, bool]:
                """Follow the column onwards.

                Returns (anything recorded, the hop limit stopped us). The second
                half is the whole point: without it a trail Ripple gave up on
                looks exactly like a trail that genuinely ended, and the screen
                where somebody decides whether to worry reports a setting as a
                fact about their warehouse.
                """
                # Zero means "until the code runs out" -- see Settings.max_hops.
                # The `seen` set below is what actually guarantees this ends.
                if cfg.max_hops and hop >= cfg.max_hops:
                    entry = cut_seen.setdefault(
                        (cur_table.upper(), cur_col.upper()),
                        {"table": show(cur_table), "attr": cur_col, "hop": hop, "roots": []},
                    )
                    if attr not in entry["roots"]:
                        entry["roots"].append(attr)
                    if entry not in attr_cut:
                        attr_cut.append(entry)
                    return False, True
                key = (cur_table.upper(), cur_col.upper())
                if key in seen:
                    return False, False
                seen = seen | {key}
                recorded = False
                truncated = False
                matched = parsed.reading(cur_table)
                visited.add(short_name(cur_table).upper())
                note_if_merged(cur_table, matched, hop)
                note_if_wildcard(cur_table)

                for stmt in matched:
                    looked[0] += 1
                    if on_progress is not None and looked[0] % 200 == 0:
                        on_progress(looked[0], 0,
                                    f"Following {cur_col} — {len(findings_by_key)} usages so far")
                    us = usages_of(stmt, cur_col, cur_table)
                    if not us:
                        continue
                    # This statement reads a whole family of date-sharded
                    # tables, and the line under the wildcard says which. See
                    # suffix_verdict: a shard the query provably never touches
                    # used to come back breaking and certain.
                    reads = suffix_verdict(stmt, cur_table)
                    if reads == "excluded":
                        continue
                    if reads == "maybe":
                        us = [replace(u, certain=False) for u in us]
                    # How this statement got here. A statement that names the
                    # table outright is a fact; one reached only through
                    # ``customer_demographics_*`` matching plain
                    # ``customer_demographics`` is a guess about what somebody
                    # meant -- BigQuery requires the separator and would match
                    # nothing. Ripple follows it anyway, because a clean "no
                    # impact" for somebody typing the family name they say out
                    # loud is the worse mistake; shipping it as certain is the
                    # part that was wrong.
                    how = _how_this_statement_reads(stmt, cur_table)
                    if how == "family":
                        us = [replace(u, certain=False) for u in us]
                    if how:
                        wild_confirmed.add(short_name(cur_table).upper())
                    primary = us[0]
                    src = index.get(stmt.file)
                    if src is None:
                        continue
                    hit = locate(src, cur_col, primary.kind, stmt.line_offset, stmt.line_end)
                    note = {
                        "filter": "Filter - stops matching after the change",
                        "join_key": "Join key - verify both sides change together",
                        "ranking": "Ranking order - breaks silently if removed",
                        "dedup_key": "Decides which row survives",
                        "transform": "Value is reshaped here",
                        "aggregation": "Group label changes with the value",
                        "sort": "Sort order - the statement stops running if this goes",
                        "excluded": ("Named in REPLACE - swapped here, and breaks here"
                                     if primary.detail == "REPLACE"
                                     else "Named in EXCEPT - dropped here, and breaks here"),
                        "pivoted": f"Named in {primary.detail or 'PIVOT'} - reshaped here, "
                                   "and breaks here",
                        "layout": f"{primary.detail or 'PARTITION BY'} - this table stops "
                                  "being built without it",
                        "renamed": f"Renamed here to {primary.detail or primary.alias}",
                        "dropped": "Dropped from the table here, by name",
                        "retyped": "Changed on the table itself here",
                        "star": "SELECT * - carried on without being named",
                        "select": f"Carried forward as {primary.alias or cur_col}",
                    }.get(primary.kind, "Used here")

                    carried_by_star = any(u.via_star for u in us)
                    # A whole-table COPY, CLONE, LIKE or RENAME is followed as
                    # the SELECT * it is, but those two words are nowhere in the
                    # file. A row that says "Carried by SELECT *" sends somebody
                    # to the line to look for a statement that is not there --
                    # and then to doubt the finding rather than the label.
                    logic = primary.label
                    # The file does not say SELECT * -- it says {cols}, and the
                    # column list arrives when the job runs. A row that claims
                    # the file says SELECT * sends somebody to a line where no
                    # such statement is written.
                    if stmt.star_note and primary.kind == "star":
                        logic = "Carried by a placeholder"
                        note = stmt.star_note
                    # PIVOT and UNPIVOT are opposite operations, and the file
                    # says which one. A row labelled PIVOT beside a line reading
                    # UNPIVOT is describing a statement that is not there.
                    if primary.kind == "pivoted" and primary.detail:
                        logic = f"Named in {primary.detail}"
                    # EXCEPT drops the column; REPLACE puts another value in its
                    # place. Both name it and both break here, but they are not
                    # the same statement and the file says which.
                    if primary.kind == "excluded" and primary.detail == "REPLACE":
                        logic = "Named in REPLACE"
                    if stmt.whole_copy and primary.kind == "star":
                        logic = f"Carried by {stmt.whole_copy}"
                        note = (f"{stmt.whole_copy} of the whole table - every column "
                                "carried on, none of them named")
                    f = Finding(
                        source_table=show(cur_table),
                        source_column=cur_col,
                        target_table=show(stmt.target) if stmt.target else None,
                        alias=primary.alias or cur_col,
                        logic=logic,
                        kind=primary.kind,
                        mode=mode_of(us),
                        impact=_impact_sentence(primary, change_type,
                                                show(stmt.target) if stmt.target else None,
                                                stmt.whole_copy, stmt.export_uri),
                        breaking=primary.kind in breaks,
                        no_local_fix=primary.kind in NO_LOCAL_FIX
                        and change_type in ("removal", "rename"),
                        file=stmt.file,
                        lang=src.lang,
                        lines=snippet(src, hit, note),
                        hop=hop,
                        certain=primary.certain,
                        via_star=carried_by_star,
                        copied_by=stmt.whole_copy,
                        built_as_text=stmt.built_as_text,
                        feed_uri=stmt.export_uri,
                        inferred_hops=inferred + (1 if carried_by_star else 0),
                        at=stmt.line_offset,
                        target_key=stmt.target or "",
                    )
                    findings_by_key.setdefault(f.key(), f)
                    f = findings_by_key[f.key()]
                    if attr not in f.roots:
                        f.roots.append(attr)
                    if f not in attr_findings:
                        attr_findings.append(f)
                    new_chain = chain + [f]

                    tgt = stmt.target
                    # An EXPORT DATA delivers a file to somebody outside the
                    # warehouse. It builds no table, so the trail has nothing to
                    # carry the column on to -- and every screen therefore said
                    # "no production table is affected", which is true and
                    # useless. The delivery breaks; it is named here.
                    if stmt.export_uri:
                        entry = feed_seen.setdefault(stmt.export_uri, {
                            "uri": stmt.export_uri, "file": stmt.file,
                            "line": stmt.line_offset + 1, "from": show(cur_table),
                            "attrs": [], "breaking": False})
                        if attr not in entry["attrs"]:
                            entry["attrs"].append(attr)
                        entry["breaking"] = entry["breaking"] or f.breaking
                        recorded = True
                    if not tgt:
                        continue
                    shown = show(tgt)
                    node = {
                        "name": shown,
                        "kind": _kind_of_node(short_name(tgt), cfg),
                        "alias": primary.alias or cur_col,
                    }
                    # The statement builds a table it never names -- a dbt model
                    # or any other one-query file. The hop is real and the name
                    # is the tool's own rule, not a guess, but it is not written
                    # on the line, so it is said out loud beside the answer.
                    # More than one file builds this table from scratch, and
                    # only one of them can be the definition that runs. See
                    # ParsedRepo.rebuilt_in.
                    forks = parsed.rebuilt_in(tgt)
                    if forks:
                        node["twoDefinitions"] = True
                        forked_seen.setdefault(shown, {"table": shown, "files": forks})
                    # The file does not hold this statement as SQL. It holds a
                    # quoted string, and runs it. Ripple reads the string, so
                    # the hop is real -- but nobody sent to that line will find
                    # the CREATE this row describes written there.
                    if stmt.built_as_text:
                        node["builtAsText"] = True
                        text_sql_seen.setdefault(
                            (stmt.file, stmt.line_offset),
                            {"table": shown, "file": stmt.file,
                             "line": stmt.line_offset + 1, "how": stmt.built_as_text})
                    if stmt.named_by:
                        node["namedByFile"] = True
                        file_named_seen.setdefault(shown, {
                            "table": shown, "file": stmt.file, "how": stmt.named_by})
                    if carried_by_star:
                        # This table is built with SELECT *, so its column list
                        # is nowhere in the repository. The hop is real and the
                        # ones past it are worked out, and both facts travel with
                        # the result rather than living on another screen.
                        node["inferred"] = True
                        node["how"] = stmt.whole_copy
                        entry = star_seen.setdefault(shown, {
                            "table": shown, "file": stmt.file, "from": show(cur_table),
                            "attr": cur_col, "roots": [],
                            # A whole-table COPY, CLONE, LIKE or RENAME is
                            # followed as the SELECT * it is, but the file does
                            # not say SELECT * -- and a card describing a
                            # statement that is not in the file is worse than
                            # no card. Which word was written travels with it.
                            "how": stmt.whole_copy,
                            # Not a star in the file at all, but a hole where
                            # the column list goes. See Statement.star_note.
                            "filledIn": stmt.star_note,
                        })
                        if attr not in entry["roots"]:
                            entry["roots"].append(attr)
                    # SELECT * EXCEPT(col) drops the column by name. It does not
                    # reach this table, so there is nothing to follow onwards --
                    # but the statement is still broken by the change, which is
                    # why the finding above was kept.
                    if primary.kind == "excluded":
                        branch = path + [node]
                        if branch not in end_branches:
                            end_branches.append(branch)
                        _collect(end_groups, shown, new_chain)
                        recorded = True
                        continue
                    # A column can leave a statement under more than one name --
                    # reshaped into one column and passed through unchanged as
                    # another, in the same SELECT. Following only one of them
                    # stopped the chain one table short of the published table
                    # that reads the other, and reported no production impact.
                    onwards = output_names(stmt, cur_col)
                    onward_inferred = inferred + (1 if carried_by_star else 0)
                    if cfg.is_production_table(short_name(tgt)):
                        node["prod"] = True
                        branch = path + [node]
                        if branch not in branches:
                            branches.append(branch)
                        _collect(prod_groups, shown, new_chain)
                        recorded = True
                        # And keep going. One published table feeding another is
                        # exactly how a change spreads, and stopping at the first
                        # one under-counts the number this whole tool is judged
                        # on -- while showing a shorter chain than the real one.
                        for onward in onwards:
                            _, hit_cap = walk(tgt, onward, hop + 1, path + [node],
                                              new_chain, seen, onward_inferred)
                            truncated = truncated or hit_cap
                        continue
                    # Every onward name is followed. This used to be an any(),
                    # which stops at the first one that finds something -- so a
                    # column leaving under two names had its second name dropped
                    # exactly when the first name found something, which is most
                    # of the time.
                    results = [walk(tgt, onward, hop + 1, path + [node], new_chain,
                                    seen, onward_inferred)
                               for onward in onwards]
                    truncated = truncated or any(cap for _, cap in results)
                    if any(done for done, _ in results):
                        recorded = True
                    else:
                        # Nothing further is built from this table, so the trail
                        # ends here -- unless the hop limit is what stopped us,
                        # in which case the trail does not end here at all and
                        # the node says so.
                        if any(cap for _, cap in results):
                            node["cut"] = True
                        branch = path + [node]
                        if branch not in end_branches:
                            end_branches.append(branch)
                        _collect(end_groups, shown, new_chain)
                        recorded = True
                return recorded, truncated

            walk(table, attr, 0, [], [], set(), 0)

            # A chain that carries on past a published table is drawn once, at
            # its full length. The shorter version of it is the same chain with
            # the end cut off, and drawing both reads as two findings.
            branches = _longest_only(branches)
            end_branches = _longest_only(end_branches)

            res.findings.extend([f for f in attr_findings if f not in res.findings])
            # "I never saw that column" and "that column goes nowhere" were the
            # same answer, byte for byte: found 0, no findings, a green tick.
            # They are opposite answers -- one answers the question, the other
            # is the question never having been asked. Split on whether the name
            # ever turned up as a column on any table in the repository.
            lookup_failed = not attr_findings and not shared.get(attr.upper(), 0)
            if branches or end_branches:
                graphs.append({"attr": attr, "table": typed,
                               "branches": branches, "endBranches": end_branches})
            res.attributes.append(
                {
                    "table": typed,
                    "attr": attr,
                    "found": len(attr_findings),
                    "files": len({f.file for f in attr_findings}),
                    # How many files so much as write the name down. Zero here
                    # is the answer to "why did it find nothing?" -- the name is
                    # not in this repository at all.
                    "mentionedIn": len({m.file for m in index.search([attr])}),
                    "reachesProduction": bool(branches),
                    # Only the branches that genuinely ran out of code. A branch
                    # Ripple stopped following has not ended, and putting it here
                    # is what turned a setting into a claim about the warehouse.
                    "endsAt": sorted({b[-1]["name"] for b in end_branches
                                      if not b[-1].get("cut")}),
                    "cutShortAt": sorted({c["table"] for c in attr_cut}),
                    # Hops on this attribute's trail where the column list was
                    # not written down, and findings that sit past one of them.
                    "notVisible": sorted({f.target_table for f in attr_findings
                                          if f.via_star and f.target_table}),
                    "inferred": len([f for f in attr_findings if f.inferred_hops]),
                    # How widely this column name is used as a name. A scan for
                    # a name half the warehouse shares is a different kind of
                    # answer from a scan for a name only one table has, and the
                    # screen has no way to say so without these two numbers.
                    "nameInTables": shared.get(attr.upper(), 0),
                    "tablesRead": table_count,
                    # "I never saw that column" and "that column goes nowhere"
                    # were byte-for-byte the same answer: found 0, no findings,
                    # a green tick. They are opposite answers. The first is a
                    # question Ripple did not manage to ask; the second is an
                    # answer to it. Split on whether the name turned up as a
                    # column on ANY table in the repository.
                    "lookupFailed": lookup_failed,
                    # The columns Ripple did read on the table asked about, so a
                    # typo corrects itself on the spot rather than shipping as
                    # "no impact". Empty means Ripple has no column list for
                    # this table at all, which is a different answer again.
                    "tableColumns": columns_here() if lookup_failed else [],
                    # Findings on lines where the SQL did not say which table
                    # the column came from. Real usages; the table is inferred.
                    "uncertain": len([f for f in attr_findings if not f.certain]),
                }
            )

    res.graphs = graphs
    # Most impacts first, then by name. On a real repository this is hundreds of
    # tables long, and alphabetical order puts whichever table happens to start
    # with an "a" at the top of the page -- so the one thing somebody reads
    # first is decided by the alphabet rather than by how much of it is broken.
    def _worst_first(groups: dict[str, list[Finding]]) -> list[tuple[str, list[Finding]]]:
        return sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0].upper()))

    res.groups = [
        {
            "prod": prod,
            "note": f"Published by this team - {_kind_of_node(prod, cfg).lower()} table",
            "rows": [_finding_row(f) for f in fs],
        }
        for prod, fs in _worst_first(prod_groups)
    ]
    placed = {f.key() for fs in prod_groups.values() for f in fs}
    cut_tables = {c["table"] for c in cut_seen.values()}
    res.reached = [
        {
            "prod": table,
            "note": ("Ripple stopped following here - the hop limit was reached, so this is "
                     f"not where the chain ends" if table in cut_tables else
                     "Last table in the chain - not matched by your production naming rule"),
            "cut": table in cut_tables,
            "rows": [_finding_row(f) for f in fs],
        }
        for table, fs in _worst_first(end_groups)
    ]
    res.star_tables = sorted(star_seen.values(), key=lambda s: s["table"].upper())
    res.cut_short = sorted(cut_seen.values(), key=lambda c: c["table"].upper())
    res.merged_names = sorted(merged_seen.values(), key=lambda m: m["table"].upper())
    # Only the wildcards that actually produced a finding. See note_if_wildcard:
    # this card says "the usages below are real", and a wildcard in one dataset
    # covering a shard in another produces none, so the card was contradicting
    # the empty answer it sat under.
    res.wildcard_names = sorted(
        (w for k, w in wild_seen.items() if k in wild_confirmed),
        key=lambda w: w["table"].upper())
    res.named_by_file = sorted(file_named_seen.values(), key=lambda m: m["table"].upper())
    res.two_definitions = sorted(forked_seen.values(), key=lambda m: m["table"].upper())
    res.built_as_text = sorted(text_sql_seen.values(),
                               key=lambda m: (m["file"], m["line"]))
    res.feeds = sorted(feed_seen.values(), key=lambda m: m["uri"])
    placed |= {f.key() for fs in end_groups.values() for f in fs}
    res.other = [_finding_row(f) for f in res.findings if f.key() not in placed]

    # Honesty: anything the search matched but the reader could not turn into a
    # finding is surfaced, never quietly dropped. Which of the three things it
    # is matters enormously -- "the name is written down here and nothing reads
    # it" is reassuring, and "the name is inside a call I cannot follow" is the
    # opposite, and they used to be told apart by nothing at all.
    # DDL that names a table the chain stood on, or one of the columns being
    # followed, and carries no column anywhere. A row access policy filtering on
    # market_code stops working on the day market_code goes, and no lineage
    # anywhere would ever have said so. Worked out here, before the honesty
    # lists below, because a file already accounted for by this belongs on this
    # card and on no other -- counted twice it is the same statement reported as
    # two separate problems.
    res.referenced_here = _references_on_topic(parsed, visited, all_names)
    accounted_for = {r["file"] for r in res.referenced_here}

    impacted_files = {f.file for f in res.findings}
    already = {u.get("file"): u for u in res.unreadable}

    # A file that produced findings used to be skipped entirely here, on the
    # reasonable-sounding grounds that it is already covered. It is not.
    #
    # Real code in this pipeline reads:
    #
    #     substr(decrypt_sde(get_sde_tag('cm13', 'triumph_demographics'), cm13), 1, 11)
    #
    # Both cm13s on that line break when cm13 is renamed. Ripple reports the
    # second one, because it is a column. The first is a quoted string, so no
    # parser can see it as anything but text -- and because the file was
    # "already covered", nothing was said about it at all. Somebody fixes the
    # column, ships, and the helper carries on asking for a name that has gone.
    for path in sorted(matched_files & impacted_files):
        hidden = _named_out_of_reach(index, parsed, path, all_names)
        if not hidden:
            continue
        hidden["reason"] = ("this file has findings above, and the name is ALSO written as "
                            "text in it - " + hidden["reason"])
        hidden["hint"] = (hidden.get("hint", "") + " Fixing the findings above does not fix "
                          "this one: the text still says the old name.").strip()
        res.unreadable.append(hidden)

    for path in sorted(matched_files - impacted_files):
        hidden = _named_out_of_reach(index, parsed, path, all_names)
        if hidden and path in already:
            # Already known to be unreadable, but now there is something better
            # to say about it: not just "this file was a problem" but "the name
            # you are chasing is on line 212 of it".
            entry = already[path]
            entry["hint"] = (entry.get("hint", "") + " " + hidden["hint"]).strip()
            entry.update({k: hidden[k] for k in ("reason", "line", "snippet")})
        elif hidden:
            res.unreadable.append(hidden)
        elif path in already:
            continue
        elif path in accounted_for:
            # An index, a policy or an UNDROP naming this very column. It is on
            # the "named here, but nothing is carried" card with the table and
            # the columns spelled out -- which is more than either of the two
            # lines below could say about it.
            continue
        elif path not in parsed.parsed_files:
            res.unreadable.append(
                {
                    "file": path,
                    "reason": "mentions the name, but Ripple could not read it as SQL - check by hand",
                }
            )
        else:
            res.mentions_only.append(
                {"file": path, "reason": "name appears, but no lineage to a production table"}
            )

    # A published table that stops being REFRESHED, rather than one whose
    # column changes. See _stops_loading -- a column used only to filter or
    # join never reaches the table the statement builds, so the trail for it
    # ends there, but the statement stops running and the table stops loading.
    broken: dict[str, str] = {}
    for f in res.findings:
        if f.breaking and f.target_table:
            # Keyed on what goes on screen, walked on from what the reader
            # keyed. For a temporary table those are two different names -- see
            # Finding.target_key.
            broken.setdefault(short_name(f.target_table).upper(),
                              f.target_key or f.target_table)
    res.stops_loading, res.stops_loading_capped = _stops_loading(
        parsed, cfg, broken,
        {short_name(g["prod"]).upper() for g in res.groups}, show)

    # A statement Ripple could not understand that names a table the chain
    # actually stood on. This is the quietest hole left in the reader: the file
    # parses, the readable statements produce findings, and the one statement
    # that carries the chain onwards -- a procedure call, SQL built as text,
    # a shape the parser gave up on -- is simply absent. The result reads as
    # complete because nothing on it says otherwise.
    #
    # Deliberately narrow. Every real pipeline is full of DECLAREs and CALLs
    # that carry no lineage at all, and reporting those would bury the list this
    # is trying to protect. Only a statement naming a table on THIS trail counts.
    for entry in _opaque_on_the_trail(index, parsed, visited,
                                      {u.get("file") for u in res.unreadable}):
        res.unreadable.append(entry)

    # Worst first. This list is the one place Ripple admits what it missed, and
    # it is only useful for as long as somebody reads to the bottom of it.
    # Alphabetical order decides what they read first by the first letter of a
    # filename -- measured: twelve config files above the one genuinely broken
    # query, because the query's file happened to start with a z.
    res.unreadable.sort(key=lambda u: (-_sql_likeness(u, index, matched_files),
                                       u.get("file", "")))

    # A gap Ripple knows about, on the subject of this scan. See _risk_of.
    # Restricted to files that mention one of the names being followed, because
    # every real pipeline has some file the reader cannot make sense of, and a
    # badge that says "not sure" on every scan ever run is one nobody reads. A
    # file that was never OPENED is not restricted that way -- nothing can say
    # whether it mentions the name, which is exactly the problem with it.
    opened = {f.path for f in index.files}
    res.unreadable_on_topic = len([u for u in res.unreadable
                                   if u.get("file") in matched_files])
    unread_on_topic = (any(u.get("file") in matched_files for u in res.unreadable)
                       or any(u.get("file") not in opened for u in res.unreadable)
                       or bool(res.held_online) or bool(res.too_long)
                       # Code files walked past because of the folder they sit
                       # in, on a scan that found NOTHING. Measured: the whole
                       # chain from the source table to the published one sat
                       # in build/, and the answer was a green "no impact" with
                       # a letter saying "please proceed as planned".
                       # Only when nothing was found: skipping build, dist and
                       # target is ordinary, and a badge that reads "not sure"
                       # on every scan of every dbt project is one nobody reads.
                       # Where the chain WAS found, the card naming the skipped
                       # folder is the right size of warning.
                       or (not res.findings and bool(res.skipped_in_folders)))
    # Every attribute asked about is a name Ripple never met as a column. The
    # scan did not come back clean -- it came back without having asked the
    # question, and those two have to look different on screen. See
    # ScanResult.lookup_failed.
    #
    # "I never saw that column" is a CONFIDENT claim, and it may only be made
    # where Ripple could look everywhere. Measured, all three as a green
    # "check your spelling" over a real gap: a file naming the column that could
    # not be read; the whole chain sitting in a skipped build/ folder; and a row
    # access policy that names the column outright, on the very screen saying
    # the name was never met.
    res.lookup_failed = (
        bool(res.attributes)
        and all(a["lookupFailed"] for a in res.attributes)
        and res.coverage()["complete"]
        and not unread_on_topic
        and not _names_a_scanned_column(res)
    )
    res.risk = _risk_of(res, unread_on_topic)
    return res


def _names_a_scanned_column(res: ScanResult) -> bool:
    """Does any index or policy name one of the columns being followed?

    Nothing here is lineage, so it produces no finding -- but a row access
    policy filtering on the column stops working on the day the column goes,
    and "No impact" over that is the one sentence this tool may not print.
    """
    return any(r.get("namesColumns") for r in res.referenced_here)


# How many tables the downstream walk will look at before it stops. Reached
# only by a table half the warehouse is built from; the number exists so a
# pathological repository cannot turn one scan into a very long one.
MAX_DOWNSTREAM = 400


def _stops_loading(parsed: ParsedRepo, cfg: Settings, broken: dict[str, str],
                   already: set[str], show) -> tuple[list[dict], bool]:
    """Published tables that stop being refreshed because a job stops running.

    A column used only in a WHERE, a JOIN or a GROUP BY never reaches the table
    the statement builds, so the trail for that COLUMN genuinely ends there --
    and Ripple said so, and stopped. But the statement itself stops working on
    the day the column goes, so the table it builds stops being rebuilt, and
    everything below it is served from data that is no longer being updated.

    That is a real impact on a published table, and it was invisible. It is
    also a DIFFERENT KIND of impact from the findings above -- nothing about
    those tables' columns changes -- so it is reported separately and in its
    own words. Folding the two together would be worse than not reporting it.

    Followed at the level of tables, not columns: which column carries onwards
    does not matter once the job feeding them has stopped.
    """
    if not broken:
        return [], False
    out: dict[str, dict] = {}
    seen = set(broken)
    frontier = [(table, [show(table)]) for table in broken.values()]
    capped = False
    # Zero means "until the code runs out". `seen` grows every round and is
    # never cleared, so this walk ends when the frontier does -- or at
    # MAX_DOWNSTREAM below, which IS reported.
    rounds = cfg.max_hops if cfg.max_hops else len(parsed.statements) + 1
    for _ in range(max(1, rounds)):
        if not frontier:
            break
        nxt: list[tuple[str, list[str]]] = []
        for table, path in frontier:
            for stmt in parsed.reading(table):
                target = stmt.target
                if not target:
                    continue
                key = short_name(target).upper()
                if key in seen:
                    continue
                if len(seen) >= MAX_DOWNSTREAM:
                    capped = True
                    continue
                seen.add(key)
                step = path + [show(target)]
                if cfg.is_production_table(short_name(target)) and key not in already:
                    out[key] = {"prod": show(target), "because": path[0], "via": step}
                nxt.append((target, step))
        frontier = nxt
    return sorted(out.values(), key=lambda r: r["prod"].upper()), capped


def _how_this_statement_reads(stmt, table: str) -> str:
    """"" if the statement names this table outright, else how it reached it.

    "shard" or "family" -- see wildcard_match. Only asked of statements that
    already produced a usage, so the cost is per finding rather than per file.
    """
    if stmt.reads_from(short_name(table)):
        return ""
    best = ""
    for src in stmt.sources:
        how = wildcard_match(src, table)
        if how == "family":
            best = "family"
        elif how and not best:
            best = "shard"
    return best


def _references_on_topic(parsed: ParsedRepo, visited: set[str],
                         all_names: list[str]) -> list[dict]:
    """Index, policy and UNDROP DDL that names something this scan is about.

    Deliberately narrow, for the same reason _opaque_on_the_trail is. A real
    warehouse has indexes on tables nobody in this scan has heard of, and
    listing those would bury the ones that matter. A statement counts when it
    names a table the chain actually stood on, or one of the columns being
    followed.
    """
    wanted = {n.upper() for n in all_names if n}
    out: list[dict] = []
    for ref in parsed.references:
        table = short_name(ref["table"]).upper()
        columns = [c for c in ref["columns"] if c.upper() in wanted]
        if table not in visited and table not in wanted and not columns:
            continue
        out.append({**ref, "namesColumns": columns})
    return sorted(out, key=lambda r: (r["file"], r["line"]))


def _opaque_on_the_trail(index: RepoIndex, parsed: ParsedRepo, visited: set[str],
                         already: set) -> list[dict]:
````

## Paste 8 of 25

### ripple/scanner/lineage.py — piece 3 of 3

Add this to the END of `ripple/scanner/lineage.py`, straight after what is already there. Do not start a new file. Do not re-type anything above.

````python
    """Statements Ripple could not read that name a table the chain reached."""
    if not visited or not parsed.opaque:
        return []
    out: list[dict] = []
    pattern = index._pattern(sorted(visited))
    for path, records in sorted(parsed.opaque.items()):
        if path in already:
            continue
        for record in records:
            # An index, a policy or an UNDROP. The parser gave up on it, but
            # Ripple read the table and the columns out of it and reports them
            # under "named here, but nothing is carried". Listing it as a
            # statement nobody could understand as well would count one thing
            # twice, on the list that has to stay short enough to read.
            if record.get("refKind"):
                continue
            text = record.get("sql") or record.get("text") or ""
            match = pattern.search(text)
            if not match:
                continue
            out.append({
                "file": path,
                "reason": (f"a statement here names {match.group(1)}, which is on this "
                           "trail, and Ripple could not understand it"),
                "line": record.get("line", 0),
                "snippet": record.get("text", "")[:200],
                "hint": ("The chain may carry on inside that statement. Everything above "
                         "is what Ripple could follow; this one has to be read by a "
                         "person."),
            })
            break                                  # one entry per file, not per line
    return out


def _named_out_of_reach(
    index: RepoIndex, parsed: ParsedRepo, path: str, names: list[str]
) -> dict | None:
    """Is the name here in a place structural reading cannot follow?

    Two shapes, both everywhere in real pipeline code, and both invisible to a
    parser however good it is:

    * The name is inside a statement the reader could take in but not make sense
      of -- a procedure call, a loop, an EXECUTE IMMEDIATE, SQL assembled as
      text and run later.
    * The name is a quoted string rather than a column: an in-house helper like
      ``get_tag('home_phone_no', 'customer_demographics')`` names the column and
      the table as text, and no amount of parsing turns that back into lineage.

    Either way the attribute really is referenced in this file. Filing it under
    "mentions the name but carries it nowhere" reads as a reassurance, and it is
    the one place a person genuinely has to go and look.
    """
    pattern = index._pattern(names)
    src = index.get(path)

    for record in parsed.opaque.get(path, []):
        # Read after all -- see the note in _opaque_on_the_trail.
        if record.get("refKind"):
            continue
        match = pattern.search(record.get("sql") or record.get("text") or "")
        if match:
            line, text, places = _line_naming(src, match.group(1))
            return {
                "file": path,
                "reason": "the name is used in a statement Ripple cannot follow",
                "line": line,
                "snippet": text,
                "places": places,
                "hint": "A procedure call, a loop, or SQL built as text and run later. "
                        "Ripple can see the name in it but not what it does with it, so "
                        "this one has to be read by a person.",
            }

    for stmt in parsed.statements_in(path):
        if stmt.expr is None:
            continue
        for literal in stmt.expr.find_all(exp.Literal):
            if not literal.is_string:
                continue
            match = pattern.search(str(literal.this))
            if not match:
                continue
            line, text, places = _line_naming(src, match.group(1))
            # How many lines of the file do this, not merely whether any does.
            # A real file sets one tag per column and runs to sixty of them; a
            # report naming one line reads as one thing to check, and sends
            # somebody to fix one line out of sixty.
            where = f" - on {places} lines of this file" if places > 1 else ""
            # Name what actually happened. This statement reads BigQuery's own
            # catalogue and looks the table up by its name as text -- which is
            # correct code, doing exactly what it should. Told instead that the
            # name is "how in-house helpers take a column or table name", the
            # one line on screen pointing at the problem named the wrong cause,
            # and following it would have found no such helper anywhere.
            # Asked of the tree, not of stmt.sources: a metadata view is
            # deliberately never recorded as a source -- it carries no column of
            # anybody's table -- so the one place the fact survives is the
            # statement itself.
            if reads_metadata(stmt.expr):
                return {
                    "file": path,
                    "reason": (f'this statement looks "{match.group(1)}" up in BigQuery\'s own '
                               f"catalogue, by name{where}"),
                    "line": line,
                    "snippet": text,
                    "places": places,
                    "hint": ("INFORMATION_SCHEMA describes the warehouse, so the table name is "
                             "a value here rather than a table being read. Nothing about the "
                             "lineage of the table changes -- but this query stops finding it "
                             "the day the name changes, and no rename of a column or table "
                             "updates a string. Change it by hand."),
                }
            return {
                "file": path,
                "reason": f'the name appears as text inside a call - "{match.group(1)}"{where}',
                "line": line,
                "snippet": text,
                "places": places,
                "hint": "Written as a quoted string rather than used as a column, which is "
                        "how in-house helpers take a column or table name. Ripple cannot "
                        "follow what the helper does with it.",
            }
    return None


def _line_naming(src, name: str) -> tuple[int, str, int]:
    """Where this name is written as text, that line, and how many such lines.

    Quoted occurrences win: that is the one being reported, and it is the line
    somebody has to open the file at. The count matters as much as the line --
    one file can name the same column on sixty lines in a row.
    """
    if src is None:
        return 1, "", 0
    quoted = re.compile(r"['\"]" + re.escape(name) + r"['\"]", re.IGNORECASE)
    plain = re.compile(r"\b" + re.escape(name) + r"\b", re.IGNORECASE)
    first = fallback = None
    places = 0
    for number, line in enumerate(src.lines, start=1):
        if quoted.search(line):
            places += 1
            if first is None:
                first = (number, line.strip()[:140])
        elif fallback is None and plain.search(line):
            fallback = (number, line.strip()[:140])
    if first is not None:
        return first[0], first[1], places
    if fallback is not None:
        return fallback[0], fallback[1], 1
    return 1, "", 0


def _longest_only(branches: list[list[dict]]) -> list[list[dict]]:
    """Drop any branch that is just the start of a longer one already listed."""
    return [b for b in branches
            if not any(other is not b and len(other) > len(b) and other[:len(b)] == b
                       for other in branches)]


def _collect(groups: dict[str, list[Finding]], table: str, chain: list[Finding]) -> None:
    bucket = groups.setdefault(table, [])
    for f in chain:
        if f not in bucket:
            bucket.append(f)


# How many of a table's own column names to print back when a lookup fails.
# Enough to spot a typo in, short enough to read on one line of a card.
MAX_COLUMNS_SHOWN = 40


def _columns_on(parsed: ParsedRepo, table: str) -> list[str]:
    """Every column name Ripple has seen on this table, in the order it met them.

    Two ways of seeing one, and both count. A statement that BUILDS the table
    writes its column list down. A statement that READS ONLY this table
    attributes every column in it to this table and nothing else -- which is
    where a source table's columns are written down, because nothing in the
    repository builds a source table at all.

    Empty means one of two very different things, and the card that prints this
    has to say which: nothing here builds or reads the table under that name, or
    everything that touches it does so with a SELECT *.
    """
    wanted = short_name(table).upper()
    out: list[str] = []
    seen: set[str] = set()

    def add(name: str) -> None:
        key = (name or "").upper()
        if name and key not in seen:
            seen.add(key)
            out.append(name)

    for stmt in parsed.statements:
        if stmt.target and short_name(stmt.target).upper() == wanted:
            for name in _stated_columns(stmt):
                add(name)
            continue
        # Only when this table is the one thing the statement reads. With two
        # tables in the FROM, a bare column name genuinely does not say whose it
        # is -- and putting a guess on this card is how somebody comes to scan
        # for a column that is on the other table.
        if len(stmt.sources) == 1 and stmt.reads_from(wanted) and stmt.expr is not None:
            for col in stmt.expr.find_all(exp.Column):
                add(col.name)
    return out


def _stated_columns(stmt) -> list[str]:
    """The column names this statement writes down for the table it builds."""
    schema = stmt.expr.this if isinstance(stmt.expr, exp.Create) else None
    if isinstance(schema, exp.Schema):
        return [d.this.name for d in schema.expressions if isinstance(d, exp.ColumnDef)]
    columns: list[str] = []
    if isinstance(stmt.expr, exp.Merge):
        for when in merge_whens(stmt.expr):
            then = when.args.get("then")
            if isinstance(then, exp.Update):
                columns += [e.this.name for e in then.args.get("expressions") or []
                            if isinstance(e, exp.EQ) and isinstance(e.this, exp.Column)]
            elif isinstance(then, exp.Insert) and isinstance(then.this, exp.Tuple):
                columns += [c.name for c in then.this.expressions if getattr(c, "name", "")]
        return columns
    if stmt.select is not None:
        for e in stmt.select.expressions:
            if isinstance(e, exp.Alias):
                columns.append(e.alias)
            elif isinstance(e, exp.Column):
                columns.append(e.name)
    return columns


def _tables_carrying(parsed: ParsedRepo, names: list[str]) -> tuple[dict[str, int], int]:
    """How many tables have a column of each of these names, and how many tables
    there are altogether.

    In this warehouse cm13, cm11 and pub_guid are columns in nearly every table,
    and market_code is in a handful. Those two scans look identical on screen and
    are not remotely the same thing: one of them is following a name that half
    the repository happens to share. Counting it is what lets the screen say so
    instead of leaving somebody to work it out from the length of the list.
    """
    wanted = {n.upper() for n in names if n}
    carrying: dict[str, set[str]] = {n: set() for n in wanted}
    all_tables: set[str] = set()
    for stmt in parsed.statements:
        if not stmt.target:
            continue
        target = stmt.target.upper()
        all_tables.add(target)
        columns: list[str] = []
        schema = stmt.expr.this if isinstance(stmt.expr, exp.Create) else None
        if isinstance(stmt.expr, exp.Merge):
            # A MERGE writes the published table's own column names on the left
            # of every SET and in every INSERT list. Without reading them a
            # MERGE-loaded table looked like a table with no columns at all, so
            # a column name half the warehouse shares was counted as rare -- and
            # "only one table has this name" is read as a reason to relax.
            for when in merge_whens(stmt.expr):
                then = when.args.get("then")
                if isinstance(then, exp.Update):
                    columns += [e.this.name for e in then.args.get("expressions") or []
                                if isinstance(e, exp.EQ) and isinstance(e.this, exp.Column)]
                elif isinstance(then, exp.Insert) and isinstance(then.this, exp.Tuple):
                    columns += [c.name for c in then.this.expressions if getattr(c, "name", "")]
        elif isinstance(schema, exp.Schema):
            columns = [d.this.name for d in schema.expressions if isinstance(d, exp.ColumnDef)]
        elif stmt.select is not None:
            for e in stmt.select.expressions:
                if isinstance(e, exp.Alias):
                    columns.append(e.alias)
                elif isinstance(e, exp.Column):
                    columns.append(e.name)
        for c in columns:
            key = (c or "").upper()
            if key in carrying:
                carrying[key].add(target)
    return {k: len(v) for k, v in carrying.items()}, len(all_tables)


def _finding_row(f: Finding) -> dict:
    return {
        "inter": f.target_table or f.source_table,
        "from": f.source_table,
        "attr": f.source_column,
        # Which of the attributes on the notification this row belongs to. Two
        # renames down, the column on this row is not called what the person
        # typed, and without this the row cannot be traced back to the question.
        "roots": list(f.roots),
        "alias": f.alias,
        "logic": f.logic,
        "mode": f.mode,
        "impact": f.impact,
        "breaking": f.breaking,
        "noLocalFix": f.no_local_fix,
        "file": f.file,
        "lang": f.lang,
        "lines": f.lines,
        "certain": f.certain,
        "viaStar": f.via_star,
        "copiedBy": f.copied_by,
        "builtAsText": f.built_as_text,
        "feed": f.feed_uri,
        "inferredHops": f.inferred_hops,
    }


# Files whose whole job is to hold SQL. One of these on the "check by hand"
# list is a query nobody read; a .yaml on the same list is usually a config
# file that happens to have the word SELECT in a comment.
_SQL_FIRST_EXTS = (".sql", ".sqlx", ".ddl", ".hql")
_SQL_WORDS = re.compile(
    r"\b(SELECT|INSERT\s+INTO|CREATE\s+TABLE|CREATE\s+OR\s+REPLACE|MERGE\s+INTO"
    r"|UPDATE|EXECUTE\s+IMMEDIATE)\b",
    re.IGNORECASE,
)


def _sql_likeness(entry: dict, index: RepoIndex, matched_files: set[str]) -> int:
    """How much a file on the 'check by hand' list is worth checking.

    Three things, in order. Whether it mentions the name being scanned settles
    it on its own -- that is a hole in THIS answer rather than in the reader.
    Then whether the file is a SQL file at all. Then whether SQL is written in
    it anywhere.
    """
    path = entry.get("file", "")
    score = 0
    if path in matched_files:
        score += 4
    if path.lower().endswith(_SQL_FIRST_EXTS):
        score += 2
    src = index.get(path)
    if src is not None and _SQL_WORDS.search(src.text):
        score += 1
    elif src is None:
        # Never opened at all -- nothing can say what is in it, which is the
        # whole problem with it.
        score += 1
    return score


def _risk_of(res: ScanResult, unread_on_topic: bool = False) -> str:
    """The badge at the top of the answer.

    "No impact" is the only thing this tool sells, so it is the one word that
    must never be printed over a gap. A file that mentions the very name being
    scanned and could not be read, or a file that was never opened at all, is a
    gap -- Ripple does not know what is in it, and "I found nothing" and "I could
    not look" are not the same answer however similar they look on screen.

    Measured before this: an EXECUTE IMMEDIATE holding a whole CREATE ... SELECT
    of the scanned column printed a green "No impact" with couldNotRead 1 sitting
    underneath it, and a file whose first statement was eaten by a byte-order
    mark did the same.
    """
    if not res.findings:
        if unread_on_topic:
            return "unknown"
        # No lineage anywhere, but something in the repository names this very
        # column and stops working without it -- a row access policy filtering
        # on it, a search index built over it. See _names_a_scanned_column.
        if _names_a_scanned_column(res):
            return "low"
        # Nothing found, and a whole file type in this repository was never
        # opened. The middle hop of a chain lives in a notebook often enough
        # that "no impact" here is a claim Ripple has not earned. It did not
        # look everywhere, so it says so. See file_types_unopened.
        if res.file_types_unopened:
            return "unknown"
        return "none"
    if any(f.no_local_fix for f in res.findings):
        return "high"
    if any(f.breaking for f in res.findings):
        return "medium"
    return "low"
````

## Paste 9 of 25

### ripple/scanner/repo.py — piece 1 of 2

Create the file `ripple/scanner/repo.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Reading the repository and finding candidate files.

Step one of a scan is deliberately dumb and fast: find every file that so much
as mentions the name. Understanding what the mention *means* happens later.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from ..config import Settings, settings as default_settings

# Which files carry SQL inside string literals rather than being SQL themselves.
EMBEDDED_SQL_EXTS = {".py", ".scala", ".java", ".sh"}

# Which files carry SQL inside markup rather than being SQL themselves. An
# Airflow YAML holds it under ``sql: |``; an Oozie workflow.xml holds it in a
# ``<script>`` element. Both were being handed to the SQL parser whole, which is
# never going to work -- so every one of them landed on the "check by hand" list
# instead. Measured: twelve ordinary Kubernetes YAML files and one genuinely
# broken .sql gave couldNotRead 13, sorted alphabetically, with the real failure
# last. That list is the one place Ripple admits what it missed, and burying it
# under config files nobody wrote SQL in is how a real miss stops being seen.
MARKUP_SQL_EXTS = {".yaml", ".yml", ".xml"}

# File types that plainly do not hold pipeline SQL. Every OTHER type Ripple does
# not open is carried onto the scan answer as a gap, because an extension nobody
# thought of -- .ipynb, .tf, .j2, or no extension at all -- is exactly how the
# middle hop of a chain goes missing without a word being said about it.
#
# The list is written this way round on purpose. A new file type Ripple has
# never seen counts as a gap by default; only what is KNOWN to be prose, an
# image, packed data or a binary is passed over in silence. The opposite way
# round, every unheard-of extension would be silently harmless, which is the
# failure this exists to stop.
#
# The repository screen still lists EVERY skipped extension, this one included.
# What this decides is only whether the ANSWER carries the warning -- and a
# warning printed over every scan, because every repository has a README, is one
# nobody reads.
NOT_CODE_EXTS = frozenset({
    # prose and documents
    ".md", ".markdown", ".rst", ".txt", ".adoc", ".pdf", ".doc", ".docx", ".odt",
    ".rtf", ".tex",
    # images
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp", ".tif",
    ".tiff", ".psd",
    # styling, fonts and browser build output
    ".css", ".scss", ".sass", ".less", ".woff", ".woff2", ".ttf", ".eot",
    ".otf", ".map",
    # packed data -- rows, not the code that makes them
    ".csv", ".tsv", ".parquet", ".avro", ".orc", ".xlsx", ".xls", ".pb",
    # archives and binaries
    ".zip", ".gz", ".tgz", ".tar", ".bz2", ".xz", ".7z", ".rar", ".jar", ".war",
    ".whl", ".egg", ".so", ".dll", ".dylib", ".exe", ".bin", ".pyc", ".pyo",
    ".class", ".o", ".a", ".lib", ".pdb",
    # media
    ".mp3", ".mp4", ".mov", ".avi", ".wav", ".webm", ".flac", ".ogg",
    # locks, logs and housekeeping
    ".lock", ".log", ".bak", ".swp", ".ds_store",
})


# A query kept as a template is named for what it IS and then for how it is
# filled in: load_final.sql.j2. Python calls that file's suffix ".j2", so it was
# never opened -- and the "runs the SQL in X, which is not in this repository"
# warning could not fire either, because that only matches names ending ".sql".
# A double miss, which is exactly what made it silent: no file read, no gap
# reported, and a published table that traced back to nothing.
#
# Only these outer suffixes count, and only over an inner SQL one. Reading
# anything at all past a .sql would take load_final.sql.bak with it, and a
# backup file read as a live one turns into "this table is built in two files".
TEMPLATE_SUFFIXES = frozenset({
    ".j2", ".jinja", ".jinja2", ".tmpl", ".template", ".tpl",
    ".mustache", ".hbs", ".erb",
})
_TEMPLATABLE = frozenset({".sql", ".sqlx", ".ddl", ".hql"})


def effective_ext(path) -> str:
    """The extension that decides how this file is read. See TEMPLATE_SUFFIXES."""
    suffixes = [s.lower() for s in path.suffixes]
    if (len(suffixes) >= 2 and suffixes[-1] in TEMPLATE_SUFFIXES
            and suffixes[-2] in _TEMPLATABLE):
        return suffixes[-2]
    return path.suffix.lower()


def unopened_code_types(unknown_ext: dict) -> dict:
    """The unopened file types that could plausibly hold SQL. See NOT_CODE_EXTS."""
    return {ext: n for ext, n in unknown_ext.items()
            if ext.lower() not in NOT_CODE_EXTS}

# ── files that are not really on this machine ──────────────────────────────
# OneDrive's Files On-Demand leaves a file in the folder listing, with its real
# name and its real size, when the contents are still in the cloud. It looks
# exactly like a file. Opening it asks OneDrive to fetch it, which needs the
# network -- and Ripple Offline is for a machine that has none.
#
# This is the most dangerous thing that can happen to a scan. A repository half
# of which was never read comes back with a short finding list and a green tick,
# and the whole point of this tool is that the green tick can be trusted. So
# these are found before anything is opened, counted, and said out loud.
FILE_ATTRIBUTE_OFFLINE = 0x1000
FILE_ATTRIBUTE_RECALL_ON_OPEN = 0x40000
FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x400000

# The two recall flags are set by the cloud provider itself and mean one thing
# only: the contents are not here. OFFLINE is older and much looser -- some
# backup software sets it on files that are perfectly local -- so on its own it
# is treated as a suspicion, and the file is still opened. Refusing to read a
# repository because a backup tool touched a flag would be its own disaster.
_DEFINITELY_ONLINE_ONLY = FILE_ATTRIBUTE_RECALL_ON_OPEN | FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS

ONLINE_ONLY_REASON = "not really on this machine - OneDrive is holding it online-only"

# Windows still refuses a path over 260 characters unless long path support has
# been switched on, and on a managed office laptop it usually has not been. His
# real folders are about 140 characters before the filename even starts, so this
# is not a theoretical limit. Prefixing the root with \\?\ opts this walk out of
# the limit whatever the machine is set to.
_LONG_PATH_LIMIT = 260


def _walk_root(root: Path) -> Path:
    """The same folder, in the form Windows will walk past 260 characters."""
    if os.name != "nt":
        return root
    text = str(root)
    if text.startswith("\\\\?\\"):
        return root
    absolute = os.path.abspath(text)
    if absolute.startswith("\\\\"):                 # \\server\share\...
        return Path("\\\\?\\UNC\\" + absolute[2:])
    return Path("\\\\?\\" + absolute)


def online_only(p: Path) -> int:
    """Which placeholder flags this file carries, or 0 for an ordinary file."""
    if os.name != "nt":
        return 0
    try:
        attrs = p.stat().st_file_attributes            # type: ignore[attr-defined]
    except (OSError, AttributeError):
        return 0
    return attrs & (_DEFINITELY_ONLINE_ONLY | FILE_ATTRIBUTE_OFFLINE)


# ── the first three bytes of a file ────────────────────────────────────────
# A byte-order mark is invisible in every editor and lethal to a SQL parser. It
# arrives on the front of the FIRST statement, which in a pipeline file is the
# one that names the source table -- so the statement that matters is the one
# that is lost, and the file still reports as read.
#
# Measured before this: the first statement failed, `risk` came back `none`, and
# with two statements in the file the wording actively reassured -- "1 of 2
# statements in this file could not be read - the other 1 was". Windows writes
# these by default: Notepad, PowerShell's `Out-File`, Excel's CSV export, and
# every "save as UTF-8" box in Office.
#
# UTF-16 is the same problem one step worse. PowerShell's `>` redirection has
# written UTF-16-LE by default for twenty years, and read as UTF-8 the file
# comes back as text with a NUL between every letter, which parses as nothing at
# all and says so about the whole file rather than about one statement.
_BOMS = (
    (b"\xef\xbb\xbf", "utf-8-sig"),
    (b"\xff\xfe\x00\x00", "utf-32"),
    (b"\x00\x00\xfe\xff", "utf-32"),
    (b"\xff\xfe", "utf-16"),
    (b"\xfe\xff", "utf-16"),
)
# How much of the head to look at when there is no mark to go by, and how much
# of it has to be NUL before UTF-16 is the better guess. Real text has none.
_SNIFF_BYTES = 4096
_NUL_SHARE = 0.10


def _decoded(raw: bytes) -> str:
    """The file as text, whichever way Windows happened to write it.

    Raises UnicodeDecodeError like ``read_text`` does, so the caller's existing
    fallback still runs.
    """
    for mark, encoding in _BOMS:
        if raw.startswith(mark):
            return raw.decode(encoding)
    head = raw[:_SNIFF_BYTES]
    if head.count(0) > len(head) * _NUL_SHARE:
        # No mark, but full of NULs. Which end the NULs sit on says which way
        # round it is; guessing wrong here only costs the same failure as now.
        try:
            return raw.decode("utf-16-le" if raw[1:2] == b"\x00" else "utf-16-be")
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8")


def _looks_like_a_cloud_error(exc: BaseException) -> bool:
    """Did this read fail because the file was still in the cloud?

    Matched on the words Windows itself uses rather than on error numbers, so a
    number remembered wrongly cannot turn a real problem into a reassuring one.
    """
    return "cloud" in str(exc).lower()

LANG_BY_EXT = {
    ".sql": "SQL",
    ".sqlx": "Dataform SQL",
    ".ddl": "SQL",
    ".hql": "Hive SQL",
    # "Python", not "Spark SQL": a .py file here might be a Spark job, a
    # BigQuery job or neither, and guessing wrong is visible on screen.
    ".py": "Python",
    ".scala": "Scala",
    ".java": "Java",
    ".sh": "Shell",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
}


@dataclass
class SourceFile:
    path: str            # repo-relative, forward slashes
    abs_path: Path
    text: str
    lang: str

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()


@dataclass
class Match:
    file: str
    line_no: int
    line: str
    name: str


@dataclass
class RepoIndex:
    """Every readable file in the repository, held in memory.

    The mock repository is tiny. A real one is bigger but still small compared
    with the memory on any server -- text compresses extremely well and we only
    keep files with an extension we can do something with.
    """

    files: list[SourceFile] = field(default_factory=list)
    skipped: list[dict] = field(default_factory=list)
    root: Path | None = None
    # Files OneDrive is keeping in the cloud, which is a different thing from a
    # file that would not parse and needs saying differently.
    held_online: list[str] = field(default_factory=list)
    # Files whose path went past what Windows will open on this machine.
    too_long: list[str] = field(default_factory=list)
    # Files Ripple never looked at because of the folder they sit in: build,
    # dist, target, venv and the rest. Those names mean "generated output" in
    # most repositories and "our SQL" in a few, and when they mean the second
    # thing an entire folder of code is missing from every answer with nothing
    # on screen to say so. Counted, and said.
    in_skipped_dirs: list[str] = field(default_factory=list)
    # Files whose extension is not on the read list, counted by extension. This
    # is the only place an unlisted file type is recorded at all: the walk had a
    # bare ``continue`` with no counter, so a repository whose pipeline lives in
    # .sqlx, .ipynb or .tf files reported `indexed False, risk none, prod []`
    # with NOTHING anywhere saying a file had been passed over. The point is not
    # to read them -- it is that the NEXT unlisted extension is visible instead
    # of silent.
    unknown_ext: dict = field(default_factory=dict)
    skipped_dir_names: list[str] = field(default_factory=list)

    @classmethod
    def build(cls, root: Path | str, cfg: Settings | None = None,
              on_progress=None) -> "RepoIndex":
        """Read the repository. ``on_progress(done, total, label)`` is called as
        it goes, with real counts -- a repository this size takes minutes, and a
        screen that says nothing for four of them looks broken."""
        cfg = cfg or default_settings
        root = Path(root)
        idx = cls(root=root)
        if not root.exists():
            idx.skipped.append({"file": str(root), "reason": "repository folder not found"})
            return idx

        walk = _walk_root(root)
        candidates = [p for p in sorted(walk.rglob("*")) if p.is_file()]
        total = len(candidates)
        for seen, p in enumerate(candidates, start=1):
            if on_progress is not None and (seen % 25 == 0 or seen == total):
                on_progress(seen, total, "Reading the files")
            # Judged on the path *inside* the repository, never the whole path.
            # Otherwise a repository that merely happens to live under a folder
            # called build, dist, target or venv has every one of its files
            # skipped, and the scan comes back clean because it read nothing.
            relative = p.relative_to(walk)
            ext = effective_ext(p)
            hit = next((part for part in relative.parts if part in cfg.skip_dirs), "")
            if hit:
                # Only worth mentioning when it is a file Ripple would otherwise
                # have read. A folder of compiled output holds thousands of
                # files nobody wants counted.
                if ext in cfg.code_extensions:
                    idx.in_skipped_dirs.append(relative.as_posix())
                    if hit not in idx.skipped_dir_names:
                        idx.skipped_dir_names.append(hit)
                continue
            if ext not in cfg.code_extensions:
                # Counted, not read. See RepoIndex.unknown_ext.
                if ext:
                    idx.unknown_ext[ext] = idx.unknown_ext.get(ext, 0) + 1
                continue
            rel = relative.as_posix()

            # Held in the cloud: do not open it. Opening asks OneDrive to fetch
            # it, which on a machine with no network hangs and then fails, once
            # per file -- and there can be thousands.
            # Counted here and nowhere else. A file that was never opened is not
            # a file to "check by hand" -- there is nothing on this machine to
            # open. Listing it in both places counts two problems where there is
            # one, and tells somebody to go and read a file that is not there.
            flags = online_only(p)
            if flags & _DEFINITELY_ONLINE_ONLY:
                idx.held_online.append(rel)
                continue

            try:
                size = p.stat().st_size
                if size > cfg.max_file_bytes:
                    idx.skipped.append(
                        {"file": rel, "reason": f"file is {size // 1024} KB - too large to read"}
                    )
                    continue
                text = _decoded(p.read_bytes())
            except UnicodeDecodeError:
                try:
                    text = p.read_text(encoding="latin-1")
                except Exception as exc:  # pragma: no cover - defensive
                    idx.skipped.append({"file": rel, "reason": f"could not decode ({exc})"})
                    continue
            except Exception as exc:
                # A read that fails on a file already flagged OFFLINE, or that
                # fails with Windows' own cloud wording, is the same problem as
                # above -- said in the same words rather than as an error code
                # nobody can act on.
                if flags or _looks_like_a_cloud_error(exc):
                    idx.held_online.append(rel)
                elif len(str(p)) > _LONG_PATH_LIMIT:
                    idx.too_long.append(rel)
                else:
                    idx.skipped.append({"file": rel, "reason": f"could not open ({exc})"})
                continue
            # A NUL that survived decoding. The parser swallows the statement it
            # sits in and says nothing at all -- measured: couldNotRead 0, no
            # warning of any kind, risk none. Either this is a mis-decoded file
            # the sniff above did not catch, or it is not text; both are worth
            # saying out loud rather than half-reading.
            if "\x00" in text:
                idx.skipped.append({
                    "file": rel,
                    "reason": "contains NUL bytes - it is not plain text, or it was "
                              "saved in an encoding Ripple could not work out",
                    "hint": "Open it and save it as UTF-8. Nothing in it has been read.",
                })
                continue
            idx.files.append(
                SourceFile(path=rel, abs_path=p, text=text, lang=LANG_BY_EXT.get(ext, "Text"))
            )
        return idx

    # ── searching ──────────────────────────────────────────────────────────
    @staticmethod
    def _pattern(names: list[str]) -> re.Pattern:
        parts = sorted({re.escape(n) for n in names if n}, key=len, reverse=True)
        if not parts:
            return re.compile(r"(?!x)x")  # matches nothing
        return re.compile(r"\b(" + "|".join(parts) + r")\b", re.IGNORECASE)

    def search(self, names: list[str]) -> list[Match]:
        """Every line mentioning any of these names, as whole words."""
        pat = self._pattern(names)
        out: list[Match] = []
        for f in self.files:
            if not pat.search(f.text):
                continue
            for i, line in enumerate(f.lines, start=1):
                m = pat.search(line)
                if m:
                    out.append(Match(file=f.path, line_no=i, line=line.rstrip(), name=m.group(1)))
        return out

    def files_mentioning(self, names: list[str]) -> list[SourceFile]:
        pat = self._pattern(names)
        return [f for f in self.files if pat.search(f.text)]

    def get(self, path: str) -> SourceFile | None:
        for f in self.files:
            if f.path == path:
                return f
        return None


# ── pulling SQL out of programs that build it as text ──────────────────────
_TRIPLE = re.compile(r'("""|\'\'\')(?P<body>.*?)\1', re.DOTALL)
_SINGLE = re.compile(r'"(?P<body>[^"\n]{40,})"|\'(?P<body2>[^\'\n]{40,})\'')
# Which blocks of text inside a program, a YAML file or a shell script are worth
# handing to the SQL parser.
#
# Every word here used to need a SELECT in it somewhere, so a statement that has
# none was mined by nothing: a DELETE that clears a published table before a
# reload, a TRUNCATE, a CREATE FUNCTION. The file was not read, and it went onto
# the "check by hand" list saying there was SQL in it that could not be taken
# out -- which named neither the table nor the column. Measured on a real
# BigQuery warehouse: 24 such blocks in 9 files, 18 of them a DELETE against a
# table that same repository publishes.
#
# Written tightly on purpose, and this is the whole difficulty of the list. It
# is matched against ordinary prose -- docstrings, comments, log messages -- and
# a loose CREATE ... TABLE takes "this helper will create the destination table"
# with it. Measured: three docstrings in one repository became statements, each
# one a table on screen that does not exist anywhere. So only real SQL modifiers
# may sit between CREATE and its noun, never "the", "a" or "your".
_LOOKS_SQL = re.compile(
    r"""\b(
          SELECT
        | INSERT\s+(?:INTO|OVERWRITE)
        | MERGE\s+INTO
        | UPDATE
        | DELETE\s+FROM
        | TRUNCATE\s+TABLE
        | CREATE\s+OR\s+REPLACE
        | CREATE\s+(?:TEMP\s+|TEMPORARY\s+|MATERIALIZED\s+|EXTERNAL\s+|SNAPSHOT\s+)?
          (?:TABLE|VIEW|FUNCTION)
      )\b""",
    re.IGNORECASE | re.VERBOSE,
)


# ── SQL a program builds out of several strings ───────────────────────────
# One statement, written as pieces, is the ordinary way a program that has to
# fill something in writes SQL::
#
#     sql  = "CREATE OR REPLACE TABLE final_published AS SELECT cm13 "
#     sql += "FROM customer_demographics WHERE dt = @d"
#
# Every miner below looks for a whole statement inside ONE pair of quotes, so
# what it found here was the first half. And the first half PARSES -- BigQuery
# is happy with a SELECT that has no FROM -- so nothing failed, nothing landed
# on the check-by-hand list, and the scan came back `risk none, prod [],
# coverage complete` over a job that really does rebuild the published table
# out of that column. A green tick, with "I could see all of it" printed beside
# it. That is the worst answer this tool is capable of giving.
#
# The pieces are welded back together on the way in. Only where the join is
# plainly one string -- whitespace, a +, a line continuation, or the same
# variable += -- and never across a comma, so a LIST of separate queries is
# left as the separate queries it is.
#
# Every character position is kept: the quotes and the joining text are replaced
# by spaces and newlines of exactly the same length, never removed. A finding
# still points at the line the statement starts on, which is the only line
# anybody can go and look at.
_STR_PREFIX = r"[fFrRbBuU]{0,2}"
# One quoted piece, on one line. Its own line, deliberately: the miner below
# joins pieces itself, and a quote allowed to run over a line break is how one
# apostrophe in a comment swallows the rest of a file.
_PIECE = re.compile(r"""(?P<q>['"])(?P<body>[^'"\n]*)(?P=q)""")
# What may sit BETWEEN two pieces for them to still be one string: whitespace, a
# line continuation, a +, or the same variable being added to. Never a comma --
# that is a LIST of separate queries, and welding those together would invent a
# statement that is in no file.
_WELD_GAP = re.compile(
    r"""^[ \t]*(?:\\\r?\n[ \t]*)?\+?[ \t]*(?:\r?\n[ \t]*)?"""
    r"""(?:(?P<name>\w+)[ \t]*\+=[ \t]*)?""" + _STR_PREFIX + r"""$""")
_ASSIGNED = re.compile(
    r"""(?P<name>\w+)[ \t]*\+?=[ \t]*""" + _STR_PREFIX + r"""['"]""")


def welded_blocks(text: str) -> tuple[list[tuple[str, int]], list[tuple[int, int]]]:
    """One statement written as several strings, joined back into one.

    Gives back the joined blocks AND the character spans they were built from.
    The spans matter: the first piece of a welded run is a quoted string in its
    own right, so the ordinary miner finds it too, and a statement read once
    whole and once in half puts every finding in it on screen twice.

    Only runs of TWO OR MORE pieces are welded. A lone string is already found
    by the ordinary miners and is left to them.

    The line offset is the line the FIRST piece starts on, which is the line of
    the file somebody opens to check the finding.
    """
    out: list[tuple[str, int]] = []
    spans: list[tuple[int, int]] = []
    # A triple-quoted block is three quote characters in a row, so the piece
    # scanner reads its fence as two empty pieces and welds the whole docstring
    # onto whatever follows it. Blanked to spaces first -- same length, so every
    # offset below is still an offset into the real file. What is inside them is
    # already mined by _TRIPLE.
    scan = _TRIPLE.sub(lambda m: " " * (m.end() - m.start()), text)
    pieces = list(_PIECE.finditer(scan))
    used = 0
    while used < len(pieces):
        run = [pieces[used]]
        at = used + 1
        while at < len(pieces):
            gap = scan[run[-1].end():pieces[at].start()]
            m = _WELD_GAP.match(gap)
            if m is None:
                break
            if m.group("name"):
                # "sql += ..." only joins to the variable the run was assigned
                # to. Two variables holding two queries must stay two queries.
                before = _ASSIGNED.findall(scan[:run[0].end()])
                owner = before[-1] if before else None
                if owner is not None and owner != m.group("name"):
                    break
            run.append(pieces[at])
            at += 1
        if len(run) > 1:
            body = "".join(p.group("body") for p in run)
            if _LOOKS_SQL.search(body):
                out.append((body, scan[:run[0].start("body")].count("\n")))
                spans.append((run[0].start(), run[-1].end()))
        used = at if at > used else used + 1
    return out, spans


def extract_sql_blocks(f: SourceFile) -> list[tuple[str, int]]:
    """Return (sql_text, line_offset) for SQL found inside a program file.

    line_offset is the 0-based line number in the file where the block starts,
    so findings can still point at a real line in the real file.
    """
    blocks: list[tuple[str, int]] = []
    # One statement written as several strings, joined back into one. See
    # welded_blocks -- without it the miners take the first piece, that piece
    # parses on its own, and the scan reports complete coverage over half a
    # statement.
    welded, welded_spans = welded_blocks(f.text)
    blocks.extend(welded)
    text = f.text

    def already_welded(at: int) -> bool:
        return any(lo <= at < hi for lo, hi in welded_spans)

    for m in _TRIPLE.finditer(text):
        body = m.group("body")
        if _LOOKS_SQL.search(body):
            offset = text[: m.start("body")].count("\n")
            blocks.append((body, offset))
    for m in _SINGLE.finditer(text):
        body = m.group("body") or m.group("body2") or ""
        if _LOOKS_SQL.search(body):
            start = m.start("body") if m.group("body") else m.start("body2")
            # This piece was already read as part of a whole statement above.
            # Reading it again puts every finding in it on screen twice.
            if already_welded(start):
                continue
            offset = text[:start].count("\n")
            blocks.append((body, offset))
    return blocks


# ── SQL kept inside markup and inside a shell script ───────────────────────
# Three shapes, all of them ordinary, none of them readable as SQL as they
# stand. Every one of these measured `risk unknown, prod []` before this: the
# statement that builds the published table was sitting in the file in plain
# sight and no scan could reach it.
#
#     Airflow YAML     sql: |            <- a block scalar
#     Oozie XML        <script>...       <- element text, often in CDATA
#     a shell job      bq query <<EOF    <- a heredoc
#
# The line each block starts on is carried out with it, so a finding still
# points at the real line of the real file.

# ``sql:``, ``query:``, ``script:`` and the handful of names that mean the same
# thing. Matched loosely at both ends because real files write ``sql_query:``,
# ``hive_script:`` and ``bql:`` -- but anchored on the whole key so that
# ``sql_conn_id:`` (a connection name, not a query) does not match.
_YAML_SQL_KEY = re.compile(
    r"^(?P<lead>[ \t]*(?:-[ \t]+)*)"
    r"(?P<key>[\"']?[A-Za-z0-9_.\-]*(?:sql|query|script|statement)[A-Za-z0-9_.\-]*[\"']?)"
    r"[ \t]*:[ \t]*(?P<rest>.*)$",
    re.IGNORECASE,
)
# ``|``, ``>``, ``|-``, ``>+``, ``|2`` -- YAML's ways of saying "the value is
# the indented block below".
_YAML_BLOCK_MARK = re.compile(r"^[|>][-+]?\d*[ \t]*$")


def _yaml_quoted_value(lines: list[str], at: int, rest: str) -> tuple[str, int]:
    """A value written on the key's line, and the last line it occupies.

    A quoted YAML scalar may run over several lines and is folded back into one
    when it is read. Stopping at the first line handed the parser half a
    statement -- and a half-statement that still parses is counted as read,
    which is worse than not reading it at all.
    """
    quote = rest[:1]
    if quote not in ("'", '"'):
        return rest.strip("\"'"), at
    if rest.count(quote) >= 2:
        return rest[1:rest.rfind(quote)], at
    parts = [rest[1:]]
    for j in range(at + 1, len(lines)):
        line = lines[j]
        end = line.find(quote)
        if end >= 0:
            parts.append(line[:end])
            return " ".join(p.strip() for p in parts), j
        parts.append(line)
    # The quote never closes. Give back the first line only, exactly as before,
    # rather than swallowing the rest of the file.
    return rest.strip("\"'"), at


def _yaml_blocks(text: str) -> list[tuple[str, int]]:
    """SQL held under a ``sql:``-ish key in a YAML file."""
    out: list[tuple[str, int]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = _YAML_SQL_KEY.match(lines[i])
        if not m:
            i += 1
            continue
        # The key's own column, not the line's indent -- a list item writes
        # "  - sql: |" and the block under it is indented past the "sql", not
        # past the dash.
        col = len(m.group("lead"))
        rest = m.group("rest").strip()
        if not _YAML_BLOCK_MARK.match(rest):
            # A value on the key's own line. YAML lets a quoted one run over
            # several lines, and taking only the first gave back
            # "CREATE OR REPLACE TABLE final_published AS" with no SELECT --
            # half a statement, handed to the parser, and counted as read.
            body, i = _yaml_quoted_value(lines, i, rest)
            if _LOOKS_SQL.search(body):
                out.append((body, i))
            i += 1
            continue
        body_lines: list[str] = []
        j = i + 1
        while j < len(lines):
            line = lines[j]
            if line.strip() and len(line) - len(line.lstrip()) <= col:
                break                       # dedented back out of the block
            body_lines.append(line)
            j += 1
        # Strip the block's own indent, and no more. Taking the first line's
        # indent off every line is what YAML itself does.
        pad = min((len(b) - len(b.lstrip()) for b in body_lines if b.strip()), default=0)
        body = "\n".join(b[pad:] if len(b) >= pad else b for b in body_lines)
        if _LOOKS_SQL.search(body):
            out.append((body, i + 1))
        i = j
    return out


# An element whose contents are a query. Oozie writes <script>, Hadoop tooling
# writes <query> and <command>, and several write it inside a CDATA section so
# that the SQL's own < and > do not have to be escaped.
_XML_SQL_ELEMENT = re.compile(
    r"<\s*(?P<tag>[A-Za-z0-9_.:\-]*(?:script|query|sql|statement|command)[A-Za-z0-9_.:\-]*)"
    r"(?:\s[^>]*)?>(?P<body>.*?)</\s*(?P=tag)\s*>",
    re.IGNORECASE | re.DOTALL,
)
_CDATA = re.compile(r"<!\[CDATA\[(?P<body>.*?)\]\]>", re.DOTALL)
_XML_ENTITIES = (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
                 ("&apos;", "'"), ("&#10;", "\n"), ("&amp;", "&"))


def _unescape_xml(text: str) -> str:
    """XML's five escapes, undone. ``&amp;`` last, or ``&amp;lt;`` decodes twice."""
    for mark, ch in _XML_ENTITIES:
        text = text.replace(mark, ch)
    return text


def _xml_blocks(text: str) -> list[tuple[str, int]]:
    """SQL held in the text of an XML element, or in a CDATA section."""
    out: list[tuple[str, int]] = []
    seen: set[int] = set()
    for m in _XML_SQL_ELEMENT.finditer(text):
        start = m.start("body")
        body = m.group("body")
        inner = _CDATA.search(body)
        if inner is not None:
            start += inner.start("body")
            body = inner.group("body")
        body = _unescape_xml(body)
        if _LOOKS_SQL.search(body):
            seen.add(start)
            out.append((body, text[:start].count("\n")))
    # A CDATA section under a tag this does not know the name of. Only worth
    # taking when it is plainly SQL, which _LOOKS_SQL already decides.
    for m in _CDATA.finditer(text):
        if m.start("body") in seen:
            continue
        body = _unescape_xml(m.group("body"))
        if _LOOKS_SQL.search(body):
            out.append((body, text[: m.start("body")].count("\n")))
    return out


# bq query <<EOF ... EOF, and every variation of it: quoted so the shell leaves
# the body alone, and <<- so the terminator may be indented.
_HEREDOC = re.compile(r"<<-?[ \t]*(?P<q>['\"]?)(?P<tag>[A-Za-z_][A-Za-z0-9_]*)(?P=q)")


def _heredoc_blocks(text: str) -> list[tuple[str, int]]:
    """SQL fed to a command through a shell heredoc."""
    out: list[tuple[str, int]] = []
    lines = text.splitlines()
    starts = {}
    for m in _HEREDOC.finditer(text):
        starts.setdefault(text[: m.start()].count("\n"), []).append(m.group("tag"))
    i = 0
    while i < len(lines):
        tags = starts.get(i)
        if not tags:
            i += 1
            continue
        tag = tags[0]
        body_lines: list[str] = []
        j = i + 1
        while j < len(lines) and lines[j].strip() != tag:
            body_lines.append(lines[j])
            j += 1
        body = "\n".join(body_lines)
        if _LOOKS_SQL.search(body):
            out.append((body, i + 1))
        i = j + 1
    return out


# The OTHER way a shell script hands a query to a command: as one quoted
# argument, written across several lines. A shell leaves a single-quoted string
# completely alone, so this is every bit as ordinary as a heredoc::
#
#     bq query --use_legacy_sql=false 'CREATE OR REPLACE TABLE final_published AS
#     SELECT id, cm13 FROM customer_demographics'
#
# The string miner every other language uses refuses a newline inside a quoted
# value -- it has to, or one stray apostrophe in a Python comment swallows the
# rest of the file -- so this shape was mined by nothing. Measured, beside a
# heredoc in the same file: the heredoc was read and this was not, and the file
# reported one gap rather than naming which of the two was missed.
#
# Anchored on a command that RUNS SQL rather than on the quote, for exactly the
# apostrophe reason above. Starting from ``bq query`` and reading to the closing
# quote cannot be set off by "don't" in a comment.
_RUNS_SQL_CMD = re.compile(
    r"\b(?:bq\s+query|psql|mysql|hive\s+-e|impala-shell|spark-sql|snowsql|"
    r"sqlcmd|clickhouse-client|beeline|athena)\b[^\n'\"]*",
    re.IGNORECASE,
)


def _shell_argument_blocks(text: str) -> list[tuple[str, int]]:
    """SQL handed to a shell command as one quoted argument. See _RUNS_SQL_CMD."""
    out: list[tuple[str, int]] = []
    for m in _RUNS_SQL_CMD.finditer(text):
        i = m.end()
        # Skip the flags between the command and its query, which may run over
        # a backslash-continued line before the quote opens.
        while i < len(text) and text[i] in " \t\\\n":
            i += 1
        if i >= len(text) or text[i] not in "'\"":
            continue
        quote = text[i]
        close = text.find(quote, i + 1)
        if close == -1:
            continue
        body = text[i + 1:close]
        if _LOOKS_SQL.search(body):
            out.append((body, text[: i + 1].count("\n")))
    return out


# A file whose FIRST line of code is a SQL keyword really is SQL, whatever it is
# called. Rare, but a .xml holding nothing but a CREATE would otherwise be read
# as markup with no SQL in it and silently produce nothing.
_OPENS_WITH_SQL = re.compile(
    r"^\s*(?:--[^\n]*\n|#[^\n]*\n|/\*.*?\*/|\s)*"
    r"(SELECT|WITH|CREATE|INSERT|MERGE|UPDATE|DELETE|ALTER|TRUNCATE|EXPORT|LOAD)\b",
    re.IGNORECASE | re.DOTALL,
)


def extract_markup_sql(f: SourceFile) -> list[tuple[str, int]]:
    """SQL taken out of a YAML or XML file, with the line each block starts on."""
    ext = effective_ext(f.abs_path)
    blocks = _xml_blocks(f.text) if ext == ".xml" else _yaml_blocks(f.text)
    if blocks:
        return blocks
    if _OPENS_WITH_SQL.match(f.text):
        return [(f.text, 0)]
    return []


def statements_for(f: SourceFile) -> list[tuple[str, int]]:
    """SQL statements in a file, with the line each one starts on."""
    ext = effective_ext(f.abs_path)
    if ext in MARKUP_SQL_EXTS:
        return extract_markup_sql(f)
    if ext in EMBEDDED_SQL_EXTS:
        blocks = extract_sql_blocks(f)
        if ext == ".sh":
            blocks += _heredoc_blocks(f.text)
            blocks += _shell_argument_blocks(f.text)
            # A one-line ``bq query 'SELECT ...'`` is found by the ordinary
            # string miner AND by the argument miner. Reading it twice would
            # count every finding in it twice over.
            blocks = list(dict.fromkeys(blocks))
        return blocks
    return [(f.text, 0)]


# ── a program that runs SQL kept somewhere else ────────────────────────────
# His pipeline has two folders of Airflow DAGs. Some hold their SQL as a string,
# which is read above. Plenty of others name a .sql file and run that -- either
# by opening it, or by handing Airflow a filename and letting template_searchpath
# find it. Ripple got nothing out of those files and said nothing about them, so
# a DAG that runs the most important query in the pipeline looked identical to an
# empty file.
#
# Both shapes come down to the same thing: a string ending in .sql.
#
# ... and a templated one is named load_final.sql.j2, so the optional template
# suffix is part of the name. Without it, a .j2 that lives OUTSIDE the
# repository could not be reported either: the file was not opened, and the
# "runs the SQL in X" warning did not match the name, so nothing was said at
````

## Paste 10 of 25 — 2 files

### ripple/scanner/repo.py — piece 2 of 2

Add this to the END of `ripple/scanner/repo.py`, straight after what is already there. Do not start a new file. Do not re-type anything above.

````python
# all. See TEMPLATE_SUFFIXES.
_TEMPLATE_TAIL = r"(?:\.(?:j2|jinja2?|tmpl|template|tpl|mustache|hbs|erb))?"
_SQL_FILE_REF = re.compile(
    r"""["']([^"'\n]*?[A-Za-z0-9_\-]+\.sql""" + _TEMPLATE_TAIL + r""")["']""")
# The same thing in markup, where the value carries no quotes at all:
#     sql: queries/load_final.sql
#     <script>hive/load_final.sql</script>
_MARKUP_SQL_FILE_REF = re.compile(
    r"""(?:[:>=][ \t]*|["'])([^\s"'<>]*[A-Za-z0-9_\-]+\.sql"""
    + _TEMPLATE_TAIL + r""")\b""")


def sql_file_refs(f: SourceFile) -> list[dict]:
    """Every .sql file this program names, with the line it names it on."""
    ext = effective_ext(f.abs_path)
    if ext not in EMBEDDED_SQL_EXTS and ext not in MARKUP_SQL_EXTS:
        return []
    pattern = _MARKUP_SQL_FILE_REF if ext in MARKUP_SQL_EXTS else _SQL_FILE_REF
    out: list[dict] = []
    seen: set[str] = set()
    for m in pattern.finditer(f.text):
        ref = m.group(1).strip()
        if not ref or ref.lower() in seen:
            continue
        seen.add(ref.lower())
        out.append({"ref": ref, "line": f.text[: m.start()].count("\n") + 1})
    return out


def looks_like_unread_sql(f: SourceFile, blocks: list[tuple[str, int]]) -> bool:
    """More SQL is written in this file than could be taken out of it.

    Two shapes. The first is SQL built by adding short strings together -- no
    single piece long enough to be recognised, and the statement never existing
    as text anywhere. Worth reporting, because the alternative is a file with a
    CREATE TABLE in it that Ripple treats as empty.

    The second is why this counts rather than asking "were there any blocks".
    An Airflow YAML, an Oozie workflow and a shell job all normally hold SEVERAL
    tasks of DIFFERENT kinds, and Ripple knows how to mine some of them. One
    recognised ``sql:`` block used to buy silence for the ``bash_command:``
    beside it -- measured: two blocks in one file, one mined and one lost, and
    couldNotRead came back 0 with the coverage card reporting no gaps at all.
    Removing the recognised block from that same file put it straight back on
    the check-by-hand list, which is the whole tell.
    """
    ext = effective_ext(f.abs_path)
    if ext not in EMBEDDED_SQL_EXTS and ext not in MARKUP_SQL_EXTS:
        return False
    in_file = len(_LOOKS_SQL.findall(f.text))
    if not in_file:
        return False
    mined = sum(len(_LOOKS_SQL.findall(body)) for body, _ in blocks)
    return mined < in_file


# A Spark or Scala job usually runs a bare SELECT and then writes the result
# from the surrounding program, not from SQL. Without this the chain stops dead
# at the job -- which is exactly where the interesting renames tend to happen.
_WRITE_TARGET = re.compile(
    r"""(?:saveAsTable|insertInto|createOrReplaceTempView|registerTempTable)\s*\(\s*["']([A-Za-z0-9_.]+)["']""",
    re.IGNORECASE,
)

# The same problem in the BigQuery world. A Python job there runs a bare SELECT
# and names its destination in the job settings, not in the SQL -- so without
# this the chain stops at the job, exactly as it would for Spark. Project ids
# may contain hyphens, hence the wider character set.
_BQ_WRITE_TARGET = re.compile(
    r"""(?:destination(?:_table)?\s*=\s*["']([A-Za-z0-9_.:\-]+)["']"""
    r"""|to_gbq\s*\(\s*["']([A-Za-z0-9_.\-]+)["'])""",
    re.IGNORECASE,
)

# Airflow's BigQueryInsertJobOperator does not write the name at all. It hands
# BigQuery its own API shape -- a NESTED dict, camelCase, the name split across
# three keys::
#
#     "destinationTable": {"projectId": "prj", "datasetId": "marts",
#                          "tableId": "final_published"}
#
# Measured before this: groups [], "the name appears, but no lineage to a
# production table", over a DAG that really does load the published table.
#
# Anchored on destinationTable and stopped at the closing brace on purpose. A
# bare "tableId" also appears under sourceTable and sourceUris, and reading
# those would turn a READ into a write and invent a chain that is not there.
_BQ_JSON_TARGET = re.compile(
    r"""["']destinationTable["']\s*:\s*\{[^}]*?["']tableId["']\s*:\s*["']([A-Za-z0-9_\-]+)["']""",
    re.IGNORECASE | re.DOTALL,
)

# Straight off the bq command line, where BigQuery's OWN separator between the
# project and the dataset is a COLON and the value carries no quotes at all::
#
#     bq query --destination_table=prj:marts.final_published --use_legacy_sql=false ...
#
# The name must be QUALIFIED -- one dot or one colon in it -- because unquoted
# means anything at all otherwise, and destination_table=None would have become
# a published table called None.
_BQ_CLI_TARGET = re.compile(
    r"""destination(?:_table)?=([A-Za-z0-9_\-]+[.:][A-Za-z0-9_.:\-]+)""",
    re.IGNORECASE,
)


def written_tables(f: SourceFile) -> list[str]:
    """Tables a program file writes to, in the order they appear."""
    if effective_ext(f.abs_path) not in EMBEDDED_SQL_EXTS:
        return []
    hits: list[tuple[int, str]] = []
    for pat in (_WRITE_TARGET, _BQ_WRITE_TARGET, _BQ_JSON_TARGET, _BQ_CLI_TARGET):
        for m in pat.finditer(f.text):
            raw = next((g for g in m.groups() if g), "")
            if raw:
                # project:dataset.table and project.dataset.table both end in
                # the table, whichever separator the writer used.
                hits.append((m.start(), raw.split(".")[-1].split(":")[-1]))
    out: list[str] = []
    for _, name in sorted(hits):          # order they appear in the file
        if name not in out:
            out.append(name)
    return out
````

### ripple/scanner/rescue.py

Create the file `ripple/scanner/rescue.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""BigQuery shapes the SQL parser refuses, rewritten into ones it accepts.

Same idea as ``templating.fill_placeholders`` and ``templating.unwrap_blocks``,
and the same two rules: this is done to a COPY on the way into the parser, and
every replacement puts back the number of line breaks it swallowed, so a finding
still points at the real line of the real file.

Why it has to exist. sqlglot fails these two ways, and both are quiet:

* a hard parse error, which loses the whole statement -- and in a file of a few
  statements, sqlglot's error recovery loses its neighbours with it;
* a fall back to a generic Command node, which holds the raw text and contains
  no tables at all, so the statement is read, understood as nothing, and is
  invisible unless it is the only statement in its file.

Either way the answer that comes back is a clean "no impact". Every shape below
was measured against the installed parser rather than taken from documentation,
and every one of them appears in an ordinary BigQuery pipeline:

    CREATE MATERIALIZED VIEW p.d.mv AS REPLICA OF p.d.cust        a whole copy
    CREATE TABLE a CLONE b FOR SYSTEM_TIME AS OF TIMESTAMP(...)   a restore
    CREATE EXTERNAL TABLE t ... WITH CONNECTION `p.us.c`          every BigLake
    CREATE EXTERNAL TABLE t WITH PARTITION COLUMNS (dt DATE)      hive layout
    SELECT ... FROM APPENDS(TABLE `p.d.cust`, NULL)               incremental
    SELECT ... FROM `p.d.f`(TABLE `p.d.orders`, 'apple')          a TVF argument
    LOAD DATA INTO t (a STRING) FROM FILES (...)                  ingestion
    EXPORT DATA OPTIONS(...) AS SELECT ...                        a partner feed

The last one is worth a word. An export builds no table, so there is nothing to
carry the column onwards to -- but it is a real read, and after this it is
reported as one rather than as a file that could not be read.
"""
from __future__ import annotations

import re

# One cheap scan decides whether any of the work below is needed. Almost every
# file in a repository contains none of these words, and walking every file
# twice is minutes rather than seconds on a repository of a few thousand.
#
# The bracket half is deliberately NOT inside the \b group. A word boundary in
# front of "(" needs a word character there, and a backticked function name
# ends in a backtick -- so `p.d.f`(TABLE x) was skipped while APPENDS(TABLE x)
# was caught, which is the sort of difference nobody would ever guess at.
_WORTH_LOOKING = re.compile(
    r"(?:\b(?:SNAPSHOT|REPLICA\s+OF|SYSTEM_TIME|WITH\s+CONNECTION"
    r"|PARTITION\s+COLUMNS|LOAD\s+DATA|EXPORT\s+DATA|UNDROP)\b|[(,]\s*TABLE\s)",
    re.IGNORECASE,
)


def _keep_lines(text: str) -> str:
    return "\n" * text.count("\n")


def _same_lines(m: "re.Match[str]") -> str:
    """Drop what matched, keeping the file the same length."""
    return _keep_lines(m.group(0))


def _balanced(text: str, open_at: int) -> int:
    """The index just past the ``)`` that closes the ``(`` at ``open_at``.

    Written out rather than done with a regular expression because an OPTIONS
    clause holds quoted strings, and a bracket inside one of those closes
    nothing. Returns -1 if the bracket never closes.
    """
    depth = 0
    quote = ""
    i = open_at
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
        elif ch in "'\"`":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def _strip_clause(text: str, head: "re.Pattern[str]") -> str:
    """Remove ``<head>(...)`` wherever it appears, brackets balanced properly."""
    while True:
        m = head.search(text)
        if not m:
            return text
        open_at = text.find("(", m.end() - 1)
        if open_at < 0:
            return text
        close_at = _balanced(text, open_at)
        if close_at < 0:
            return text
        chunk = text[m.start():close_at]
        text = text[:m.start()] + _keep_lines(chunk) + text[close_at:]


# ── one shape at a time ────────────────────────────────────────────────────

# CREATE SNAPSHOT TABLE a CLONE b -- a copy, with two extra words the parser
# gives up on. Handled here rather than as a retry so it shares one code path
# with the rest.
_SNAPSHOT = re.compile(r"\bCREATE\s+SNAPSHOT\s+TABLE\b", re.IGNORECASE)

# CREATE MATERIALIZED VIEW x AS REPLICA OF y -- a full copy of a table into
# another region or cloud. Every column carries through under the same name,
# which is exactly what COPY already means to Ripple.
_REPLICA = re.compile(
    r"\bCREATE\s+(?:OR\s+REPLACE\s+)?MATERIALIZED\s+VIEW\s+(?P<t>[^\s]+)\s+"
    r"AS\s+REPLICA\s+OF\s+(?P<s>[^\s;]+)",
    re.IGNORECASE,
)

# ... CLONE b FOR SYSTEM_TIME AS OF <expr> -- the restore-from-backup form, and
# the one teams actually write. Only stripped after a CLONE or a COPY, because
# the same words are legal on an ordinary FROM and the parser reads those.
_TIME_TRAVEL = re.compile(
    r"(?<=\s)(FOR\s+SYSTEM_TIME\s+AS\s+OF\s+)(?P<e>[^;]*)",
    re.IGNORECASE,
)
_HAS_COPY = re.compile(r"\b(CLONE|COPY)\b", re.IGNORECASE)

# WITH CONNECTION `p.us.conn` -- on every BigLake, object and Iceberg table.
_CONNECTION = re.compile(
    r"\bWITH\s+CONNECTION\s+(?:`[^`]*`|\"[^\"]*\"|[\w.\-]+)", re.IGNORECASE)

# WITH PARTITION COLUMNS (dt DATE) -- hive-partitioned external tables.
_PARTITION_COLUMNS = re.compile(r"\bWITH\s+PARTITION\s+COLUMNS\s*(?=\()", re.IGNORECASE)

# APPENDS(TABLE t, ...), CHANGES(TABLE t, ...), my_tvf(TABLE t, 'x'),
# VECTOR_SEARCH(TABLE t, ...). A bare TABLE in argument position is a hard
# parse error, and it takes the neighbouring statements down with it.
_TABLE_ARG = re.compile(r"(?<=[(,])(\s*)TABLE\s+(?=[`\"\w])", re.IGNORECASE)

# LOAD DATA [OVERWRITE] INTO t (cols) FROM FILES (...) -- often the only place a
# landing table's columns are written down anywhere in the repository.
_LOAD_DATA = re.compile(
    r"\bLOAD\s+DATA\s+(?:OVERWRITE\s+|INTO\s+)+(?P<t>`[^`]*`|[\w.\-]+)\s*(?=\()",
    re.IGNORECASE,
)
_FROM_FILES = re.compile(r"\bFROM\s+FILES\s*(?=\()", re.IGNORECASE)

# EXPORT DATA [WITH CONNECTION x] OPTIONS(...) AS SELECT ... -- a delivery to
# somebody outside the warehouse. It builds no table, so what is left is the
# SELECT, and the read is reported as a real usage instead of an unreadable file.
_EXPORT = re.compile(r"\bEXPORT\s+DATA\s+(?=.*?\bOPTIONS\s*\()", re.IGNORECASE | re.DOTALL)
_OPTIONS_AS = re.compile(r"\bOPTIONS\s*(?=\()", re.IGNORECASE)


# Where an EXPORT DATA delivers to. The whole point of an export is that the
# file lands somewhere outside the warehouse and somebody else's job reads it,
# so "no production table is affected" is true and useless: the delivery that
# breaks belongs to another team, and nothing on any screen named it.
#
#     OPTIONS(uri='gs://feed/partner/*.csv', format='CSV')  ->  gs://feed/partner
#
# The last part of the path is a filename pattern, not a place. Dropping it is
# what turns a wildcard nobody recognises into the name of a feed somebody does.
_URI_OPTION = re.compile(r"\buri\s*=\s*(?:\[\s*)?(['\"])(?P<uri>[^'\"]+)\1", re.IGNORECASE)


def _feed_name(uri: str) -> str:
    """The delivery an export URI names, without its filename pattern."""
    head, sep, tail = uri.rstrip("/").rpartition("/")
    if sep and ("*" in tail or "." in tail):
        return head or uri
    return uri.rstrip("/")


def export_targets(text: str) -> list[tuple[int, str]]:
    """``(0-based line of the EXPORT, feed name)`` for every EXPORT DATA here."""
    out: list[tuple[int, str]] = []
    at = 0
    while True:
        m = _EXPORT.search(text, at)
        if not m:
            return out
        at = m.end()
        opt = _OPTIONS_AS.search(text, m.end())
        if not opt:
            return out
        open_at = text.find("(", opt.end() - 1)
        close_at = _balanced(text, open_at) if open_at >= 0 else -1
        if close_at < 0:
            return out
        found = _URI_OPTION.search(text[open_at:close_at])
        out.append((text[: m.start()].count("\n"),
                    _feed_name(found.group("uri")) if found else ""))


def _rewrite_export(text: str) -> str:
    """Leave the SELECT of an EXPORT DATA, and nothing else."""
    while True:
        m = _EXPORT.search(text)
        if not m:
            return text
        opt = _OPTIONS_AS.search(text, m.end())
        if not opt:
            return text
        open_at = text.find("(", opt.end() - 1)
        close_at = _balanced(text, open_at) if open_at >= 0 else -1
        if close_at < 0:
            return text
        after = text[close_at:]
        as_at = re.match(r"\s*AS\b", after, re.IGNORECASE)
        end = close_at + (as_at.end() if as_at else 0)
        chunk = text[m.start():end]
        text = text[:m.start()] + _keep_lines(chunk) + text[end:]


def _rewrite_load_data(text: str) -> str:
    """A LOAD DATA read as the table declaration it is."""
    while True:
        m = _LOAD_DATA.search(text)
        if not m:
            return text
        open_at = text.find("(", m.end() - 1)
        close_at = _balanced(text, open_at) if open_at >= 0 else -1
        if close_at < 0:
            return text
        columns = text[open_at:close_at]
        # Whatever follows -- FROM FILES (...) -- names no table, only a bucket.
        rest = text[close_at:]
        files = _FROM_FILES.search(rest)
        end = close_at
        if files:
            f_open = rest.find("(", files.end() - 1)
            f_close = _balanced(rest, f_open) if f_open >= 0 else -1
            if f_close >= 0:
                end = close_at + f_close
        chunk = text[m.start():end]
        replacement = f"CREATE TABLE {m.group('t')} {columns}"
        text = text[:m.start()] + replacement + _keep_lines(chunk) + text[end:]


# UNDROP TABLE t -- restoring a table somebody deleted. A HARD parse error, and
# a hard parse error costs the neighbouring statements too, so one line of a
# recovery script used to take the rest of its file with it. One extra word puts
# it in the same generic-command shape every other unreadable statement lands
# in, where sqlread.referenced_here reads the table name out of it and reports
# it as the dependency it is. Nothing is added to any line, so no line moves.
_UNDROP = re.compile(r"\bUNDROP\s+TABLE\b", re.IGNORECASE)


# ── Dataform ───────────────────────────────────────────────────────────────
# A .sqlx file is Google's own way of writing a BigQuery pipeline: an ordinary
# SELECT with a block on top that is JavaScript, not SQL.
#
#     config { type: "table", schema: "reporting" }
#     js { const x = 1 }
#     pre_operations { DELETE FROM ... }
#
#     SELECT cm13 FROM ${ref("customer_demographics")}
#
# The parser refuses the whole file on the first line, so nothing at all is
# learned from it. The blocks carry no lineage -- the config names a schema, and
# the SELECT under it is the thing that builds the table -- so they are dropped
# on the way in, keeping every line where it was.
#
# ``pre_operations`` and ``post_operations`` DO hold real SQL, so their brackets
# are dropped and their contents kept, as one more statement in the file.
_DATAFORM_BLOCK = re.compile(r"^[ \t]*(config|js)\s*\{", re.IGNORECASE | re.MULTILINE)
_DATAFORM_OPS = re.compile(r"^[ \t]*(pre_operations|post_operations)\s*\{",
                           re.IGNORECASE | re.MULTILINE)


def _balanced_braces(text: str, open_at: int) -> int:
    """The index just past the ``}`` closing the ``{`` at ``open_at``, or -1."""
    depth = 0
    quote = ""
    i = open_at
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
        elif ch in "'\"`":
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def _strip_dataform(text: str) -> str:
    """Drop the JavaScript blocks a Dataform file opens with."""
    for pattern, keep_inside in ((_DATAFORM_BLOCK, False), (_DATAFORM_OPS, True)):
        while True:
            m = pattern.search(text)
            if m is None:
                break
            brace = text.find("{", m.start())
            end = _balanced_braces(text, brace) if brace >= 0 else -1
            if end < 0:
                break
            if keep_inside:
                # Real SQL, run before or after the model builds. Keep it, as
                # one more statement in the file.
                head = _keep_lines(text[m.start():brace])
                text = text[:m.start()] + head + text[brace + 1:end - 1] + ";" + text[end:]
            else:
                text = text[:m.start()] + _keep_lines(text[m.start():end]) + text[end:]
    return text


def needed(text: str) -> bool:
    return bool(_WORTH_LOOKING.search(text) or _DATAFORM_BLOCK.search(text)
                or _DATAFORM_OPS.search(text))


def rewrite(text: str) -> str:
    """The same SQL, in a shape the parser will read. Line numbers do not move."""
    if not needed(text):
        return text
    text = _strip_dataform(text)
    out = _SNAPSHOT.sub(lambda m: "CREATE TABLE", text)
    out = _REPLICA.sub(
        lambda m: (f"CREATE TABLE {m.group('t')} COPY {m.group('s')}"
                   + _keep_lines(m.group(0))),
        out)
    if _HAS_COPY.search(out):
        out = _TIME_TRAVEL.sub(_same_lines, out)
    out = _CONNECTION.sub(_same_lines, out)
    out = _strip_clause(out, _PARTITION_COLUMNS)
    out = _TABLE_ARG.sub(lambda m: m.group(1), out)
    out = _rewrite_load_data(out)
    out = _rewrite_export(out)
    out = _UNDROP.sub(lambda m: "CREATE " + m.group(0), out)
    return out
````

## Paste 11 of 25

### ripple/scanner/sqlread.py — piece 1 of 5

Create the file `ripple/scanner/sqlread.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Reading SQL properly, rather than just matching words.

The whole value of Ripple is in this file. A word search can tell you that
MARKET_CODE appears in a file. Only parsing can tell you that it appears
*inside a WHERE clause comparing it to the literal 'US'* -- which is the
difference between "mentioned here" and "this breaks on the 18th".
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import sqlglot
from sqlglot import exp

from ..config import Settings, settings as default_settings
from .repo import (
    RepoIndex,
    SourceFile,
    looks_like_unread_sql,
    sql_file_refs,
    statements_for,
    written_tables,
)
from . import rescue
from .dialectcompat import (
    RENAME_NODE, SET_OPERATION, from_of, is_temporary, is_unpivot, merge_whens,
    output_names as query_output_names, pivot_columns, pivot_fields,
    set_branches, star_except, star_replace,
)
from .templating import (
    describe as describe_templating,
    fill_placeholders,
    has_blocks,
    has_placeholders,
    placeholder_names,
    renderings,
    unwrap_blocks,
)

# sqlglot narrates its fallbacks to the log; that noise is not useful here
# because we surface every genuinely unreadable file ourselves.
import logging

logging.getLogger("sqlglot").setLevel(logging.ERROR)
log = logging.getLogger(__name__)

# How a usage is shown to the user, in the order we prefer to report it.
LOGIC_LABEL = {
    "filter": "Filter",
    "join_key": "Join key",
    "ranking": "Ranking",
    "dedup_key": "Dedup key",
    "aggregation": "Aggregation",
    "transform": "Transform",
    "excluded": "Named in EXCEPT",
    "pivoted": "Named in PIVOT",
    "layout": "Partition or cluster key",
    "sort": "Sort order",
    "renamed": "Renamed by ALTER TABLE",
    "dropped": "Dropped by ALTER TABLE",
    "retyped": "Changed by ALTER TABLE",
    "select": "Select",
    "star": "Carried by SELECT *",
}
# Most consequential first: if a column is used several ways in one statement,
# this decides which one heads the finding.
KIND_PRIORITY = ["ranking", "dedup_key", "layout", "filter", "join_key", "transform",
                 "aggregation", "sort", "pivoted", "excluded", "renamed", "dropped",
                 "retyped", "select", "star"]

# Words that make a line likely to be the one a given usage lives on.
KIND_MARKERS = {
    "filter": ("WHERE", "AND ", "OR ", "HAVING"),
    "join_key": ("JOIN", " ON "),
    "ranking": ("ORDER BY", "OVER", "ROW_NUMBER", "RANK"),
    "aggregation": ("GROUP BY",),
    "dedup_key": ("MAX(", "MIN(", "GROUP BY"),
    "transform": ("SUBSTR", "CAST", "TRIM", "UPPER", "LOWER", "COALESCE", "CONCAT", "("),
    "excluded": ("EXCEPT", "SELECT"),
    "pivoted": ("UNPIVOT", "PIVOT", " FOR ", " IN ("),
    "layout": ("PARTITION BY", "CLUSTER BY"),
    "sort": ("ORDER BY",),
    "renamed": ("RENAME COLUMN", "RENAME", "ALTER"),
    "dropped": ("DROP COLUMN", "DROP", "ALTER"),
    "retyped": ("ALTER COLUMN", "SET DATA TYPE", "ALTER"),
    "select": ("SELECT", " AS "),
    "star": ("SELECT *", "SELECT"),
}


# ── one table's name, and whether two names are the same table ─────────────
# ``prj.raw_dataset.customer_demographics`` and
# ``prj.archive_dataset.customer_demographics`` are two different tables. Ripple
# used to keep only the last part of a name, so a change to one produced
# findings for the code that reads the other -- and in the warehouse this was
# built for the same table name really does appear in a source dataset and a
# stage dataset.
#
# The project is deliberately left out. It is templated in nearly every file
# ({{tgt_project_id}}, {{src_project_id}}), so including it would split one real
# table into two on the strength of which placeholder somebody happened to type.
# The dataset is the part that says which table this is.
# customer_demographics$20260101 -- a partition decorator. It names ONE DAY of
# one table, not another table, and BigQuery uses it wherever a single
# partition is written or read. Kept as part of the name, it split every
# decorated read off from the table it belongs to and the scan came back clean.
_DECORATOR = re.compile(r"\$[0-9]+$")


def short_name(table: str) -> str:
    """The table's own name, without the dataset in front of it."""
    return _DECORATOR.sub("", (table or "").rsplit(".", 1)[-1])


def dataset_of(table: str) -> str:
    """The dataset a name was qualified with, or '' if the SQL did not say."""
    parts = (table or "").rsplit(".", 1)
    return parts[0] if len(parts) == 2 else ""


def canonical(table: str) -> str:
    """A name cut down to the part that identifies the table: ``dataset.name``.

    Names arrive with a project in front of them -- typed into the notification,
    pasted off a screen, or written that way in the SQL. The project is dropped
    for the reason given above: it is a placeholder in nearly every file here, so
    comparing it would split one real table into two.
    """
    parts = [p for p in (table or "").split(".") if p]
    if parts:
        parts[-1] = _DECORATOR.sub("", parts[-1])
    return ".".join(parts[-2:]) if parts else (table or "")


# ── wildcard tables ────────────────────────────────────────────────────────
# Date-sharded tables are ordinary in BigQuery, and the way every one of them is
# read is a wildcard::
#
#     SELECT cm13 FROM `prj.ds.customer_demographics_*`
#     WHERE _TABLE_SUFFIX BETWEEN '20260101' AND '20260131'
#
# The name in the file is ``customer_demographics_*``, asterisk and all. Nobody
# has a table called that. The tables are ``customer_demographics_20260101`` and
# three hundred siblings, and that is what a person types into a scan -- so the
# name matched nothing, the chain was never followed, and the answer came back
# as a clean "no impact" on a change that breaks a published table.
#
# What a wildcard matches is not a guess: BigQuery only allows the star at the
# end, and it stands for every table in that dataset whose name starts with the
# part in front of it. So a wildcard covers a name when the name starts with
# that prefix.
#
# One deliberate addition to that rule. A person asked what breaks does not type
# the shard, they type the family the way they think of it -- "customer_
# demographics", with no trailing separator, which BigQuery itself would not
# match. Refusing that would print the exact clean "no impact" this exists to
# prevent, so the prefix with its trailing separator taken off matches too. It
# costs a row somebody can dismiss by opening the file. Silence costs an outage.
_STAR = "*"


def is_wildcard(table: str) -> bool:
    """Is this a BigQuery wildcard table name -- ``events_*``?"""
    return short_name(table).endswith(_STAR)


def wildcard_match(pattern: str, name: str) -> str:
    """How ``pattern`` covers ``name``: "shard", "family", "both", or "".

    Two different answers wearing one word, and shipping them as one is how a
    guess got printed as a fact.

    * "shard" -- ``customer_demographics_*`` and ``customer_demographics_20260101``.
      BigQuery itself matches this. It is a fact about the SQL.
    * "family" -- ``customer_demographics_*`` and plain ``customer_demographics``.
      BigQuery does NOT match this; the separator is required. Ripple matches it
      anyway, because somebody typing the family name they say out loud must not
      get a clean "no impact" -- but it is a guess about what they meant, and a
      guess shipped as ``certain`` is the failure this whole reader exists to
      avoid.
    * "both" -- two wildcards whose families overlap.

    Both names are compared on their short names, because the dataset is ruled
    on separately by ``same_table`` for the reason given further up this file.
    """
    prefix = short_name(pattern).upper()
    if not prefix.endswith(_STAR):
        return ""
    prefix = prefix[:-1]
    # A bare "*" -- the whole of a dataset. It genuinely does read every table
    # there, but matching on it here would put every table in the repository on
    # every chain, which is not a spare row somebody can dismiss, it is the
    # whole warehouse. It is ruled on in same_table instead, where the dataset
    # is known and can scope it.
    if not prefix:
        return ""
    other = short_name(name).upper()
    if other.endswith(_STAR):
        # Two wildcards. They are the same family if either prefix contains the
        # other -- ``customer_*`` and ``customer_demographics_*`` overlap, and
        # following both is the safe direction.
        other = other[:-1]
        return "both" if other.startswith(prefix) or prefix.startswith(other) else ""
    if other.startswith(prefix):
        return "shard"                   # customer_demographics_20260101
    # The family named the way a person says it, without the separator the
    # wildcard was written with. Deliberately tight: it matches the whole prefix
    # bar its trailing separator and nothing shorter, so ``ev`` never matches
    # ``events_*``.
    return "family" if prefix.rstrip("_-") == other else ""


def wildcard_covers(pattern: str, name: str) -> bool:
    """Does the wildcard name ``pattern`` cover the table name ``name``?"""
    return bool(wildcard_match(pattern, name))


# ── the warehouse describing itself ────────────────────────────────────────
# INFORMATION_SCHEMA is not data, it is BigQuery's catalogue of its own tables.
# Its views are called COLUMNS, TABLES, JOBS, VIEWS, PARTITIONS -- ordinary
# words, and a warehouse of any size has real tables called some of them.
#
#     CREATE TABLE `p.base.columns` (table_name STRING, column_name STRING);
#     CREATE TABLE `p.pub.report_prod` AS
#     SELECT column_name FROM `p.base`.INFORMATION_SCHEMA.COLUMNS;
#
# Measured before this: `report_prod` was reported as fed by the real table
# `base.columns`, breaking, with a warning that blamed CAPITALISATION -- so the
# one thing on screen pointing at the problem named the wrong cause, and
# following it would not have found anything.
#
# A metadata view carries no column of anybody's table. Nothing that changes in
# `customer_demographics` changes a column of INFORMATION_SCHEMA.COLUMNS -- a
# ROW of it changes, and a row is not lineage. So these are not catalogued, not
# merged with anything, and no edge is drawn from them.
#
# ``region-us`` and its siblings are the same thing at project level: the
# region-wide job history, addressed as if it were a project.
_METADATA_PART = "INFORMATION_SCHEMA"
_REGION_PROJECT = re.compile(r"^region-", re.IGNORECASE)


def is_metadata_read(table: str) -> bool:
    """Is this BigQuery describing itself, rather than a table of anybody's?"""
    parts = [p for p in (table or "").split(".") if p]
    if any(p.upper() == _METADATA_PART for p in parts):
        return True
    return bool(parts) and bool(_REGION_PROJECT.match(parts[0]))


# ── temporary tables ───────────────────────────────────────────────────────
# A TEMP table lives inside one script and is gone when it finishes. Two files
# that both build a ``t`` are not sharing a table; they cannot be, because a
# static scan has no way to know two files ever ran in one session, and BigQuery
# throws the table away at the end of each. Temp names in real repositories are
# ``t``, ``tmp``, ``stg``, ``base``, ``deduped`` -- collisions are the norm, not
# the exception.
#
# Measured before this: two unrelated files, each building its own ``t``, put
# BOTH of their published tables on the chain, marked the second one breaking,
# and printed no warning of any kind. A confident finding about a table nothing
# had touched.
#
# The dataset fix that keeps ``stage.orders`` apart from ``archive.orders``
# cannot help here, because a temp table has no dataset to compare. So one is
# invented: a scope standing for "inside this file", made of the file's own path
# and marked with a character no warehouse allows in a name. It never reaches a
# screen -- ``display`` strips it -- and ``same_table`` treats it as absolute
# rather than as the usual loose match, because "no dataset given" must not go
# on matching a table that exists nowhere outside one file.
_SESSION_DATASET = "_SESSION"
_SCOPE_MARK = "#"
_NOT_A_NAME = re.compile(r"[^A-Za-z0-9]+")


def session_scope(path: str) -> str:
    """A dataset name no warehouse can have, standing for 'inside this file'."""
    return _SCOPE_MARK + _NOT_A_NAME.sub("_", path).strip("_").upper()


def is_session_scoped(table: str) -> bool:
    """Is this name confined to one file -- a TEMP or _SESSION table?"""
    return dataset_of(table).startswith(_SCOPE_MARK)


def same_table(a: str, b: str) -> bool:
    """Are these two names the same table?

    The short name always has to match, or one of the two has to be a wildcard
    covering the other. The dataset can only rule a match OUT, and only when
    BOTH sides carry one -- these files are templated, so a great many names in
    the repository are written with a placeholder where a dataset goes, and
    treating "no dataset given" as "a different table" would cut every one of
    those chains. Two placeholders that fill to the same value produce the same
    word here, so they go on matching.
    """
    if short_name(a).upper() != short_name(b).upper():
        if is_wildcard(a) or is_wildcard(b):
            wide, other = (a, b) if is_wildcard(a) else (b, a)
            if not wildcard_covers(wide, other):
                # A dataset-wide "ds.*" has nothing in front of the star, so it
                # covers every table -- but only inside its own dataset, and
                # only when the other name says which dataset it is in. Without
                # both of those it would match the whole repository.
                if not (short_name(wide) == _STAR and dataset_of(wide)
                        and dataset_of(other)
                        and dataset_of(wide).upper() == dataset_of(other).upper()):
                    return False
        else:
            return False
    left, right = dataset_of(a).upper(), dataset_of(b).upper()
    # A temporary table only exists inside one file, so "the SQL did not say
    # which dataset" cannot mean "it might be that one". Nothing outside that
    # file can be it. This is the one place the loose match is switched off.
    if left.startswith(_SCOPE_MARK) or right.startswith(_SCOPE_MARK):
        return left == right
    return not (left and right and left != right)


# ── table-valued functions ─────────────────────────────────────────────────
# A BigQuery TABLE FUNCTION is a table as far as lineage is concerned. It is
# named, it is read in a FROM clause, and every column of its body travels
# through it::
#
#     CREATE OR REPLACE TABLE FUNCTION ds.recent_customers(d STRING) AS (
#       SELECT cm13, market_code FROM customer_demographics WHERE dt = d)
#
#     CREATE OR REPLACE TABLE published.summary AS
#     SELECT cm13 FROM ds.recent_customers('2026-01-01')
#
# Both halves were invisible. The definition parses as a function rather than a
# table, so it published nothing; and the call parses as a function call in the
# FROM clause, whose table node carries no name at all, so it read nothing. The
# chain broke in the middle and the published table was never mentioned.
#
# Some things written in a FROM clause that look the same really are not tables.
# BigQuery's own built-in table functions wrap a table rather than being one,
# and the table they wrap is parsed as its own node and found anyway -- so
# taking the wrapper's name as well would only invent a table nobody has.
_NOT_A_TABLE = {
    "EXTERNAL_QUERY", "APPENDS", "CHANGES", "GAP_FILL", "RANGE_SESSIONIZE",
    "TABLE_DATE_RANGE", "TABLE_QUERY", "OBJECT_METADATA", "VECTOR_SEARCH",
    "GENERATE_ARRAY", "GENERATE_DATE_ARRAY", "GENERATE_TIMESTAMP_ARRAY",
    "SEARCH_INDEX_STATUS", "SESSIONIZE",
}


def _called_function_name(t: exp.Table) -> str:
    """The table function this FROM clause is calling, or '' if it is not one."""
    inner = t.this
    if not isinstance(inner, exp.Anonymous):
        return ""
    name = inner.name or ""
    if not name or name.upper() in _NOT_A_TABLE:
        return ""
    return name


def _tables_handed_to_a_call(t: exp.Table) -> list[str]:
    """Tables passed INTO a function that sits in a FROM clause.

    BigQuery hands a table to a function with the word TABLE in front of it::

        SELECT cm13 FROM APPENDS(TABLE `prj.ds.customer_demographics`, NULL)
        SELECT ...  FROM `prj.ds.recent`(TABLE `prj.ds.orders`, 'apple')

    The parser refuses that outright, so the pre-pass takes the word out (see
    scanner/rescue.py) -- and what is left arrives as an ordinary column
    reference among the function's arguments, not as a table node. Without this
    the real table is nowhere in the statement, and an incremental load, which
    is exactly how a published table is kept up to date, reads nothing at all.

    Only column-shaped arguments count. A literal, a number or a nested call is
    not a table, and inventing one from a string would put a table nobody has
    on the result.
    """
    inner = t.this
    if not isinstance(inner, exp.Anonymous):
        return []
    out: list[str] = []
    for arg in inner.expressions:
        if not isinstance(arg, exp.Column):
            continue
        name = canonical(_bare(arg.sql()))
        if name and name not in out:
            out.append(name)
    return out


def _qualify(t: exp.Table) -> str:
    """One table node as ``dataset.name``, or just ``name`` when unqualified."""
    name = _DECORATOR.sub("", t.name or "")
    if not name:
        # A table function call. Backticked in full, the whole path arrives as
        # one string -- `prj.ds.recent_customers` -- so it is cut down the same
        # way any other name written in full is.
        called = _called_function_name(t)
        if not called:
            return ""
        if "." in called:
            return canonical(called)
        name = called
    db = t.text("db")
    return f"{db}.{name}" if db else name


def _bare(sql: str) -> str:
    """A name as written, with whatever quoting the dialect put round it taken off."""
    return sql.replace("`", "").replace('"', "").strip()


def reads_metadata(stmt: exp.Expression | None) -> bool:
    """Does this statement read the warehouse's own catalogue?

    Asked of the tree rather than of a Statement's sources, because a metadata
    view is deliberately never recorded as a source -- it carries no column of
    anybody's table. So the statement itself is the only place the fact
    survives, and one screen needs it to name what actually happened rather
    than blaming an in-house helper for a plain INFORMATION_SCHEMA lookup.
    """
    if stmt is None:
        return False
    return any(is_metadata_read(_qualify(t)) for t in stmt.find_all(exp.Table))


def _table_function_target(stmt: exp.Expression) -> str:
    """The name a ``CREATE TABLE FUNCTION`` publishes, or ''.

    A scalar UDF parses identically -- same node, same kind -- and must NOT be
    treated as a table, or every helper function in the repository becomes one.
    The difference is what it returns: a table function's body is a SELECT, and
    a scalar function's is an expression.
    """
    if not isinstance(stmt, exp.Create):
        return ""
    if str(stmt.args.get("kind") or "").upper() != "FUNCTION":
        return ""
    body = stmt.args.get("expression")
    if body is None or body.find(exp.Select) is None:
        return ""
    named = getattr(stmt.this, "this", None)
    if named is None:
        return ""
    return canonical(_bare(named.sql()))


def _forget_templated_datasets(stmt: exp.Expression, holes: set[str]) -> None:
    """Take off any dataset that is really a placeholder.

    Ripple fills placeholders in with an ordinary word so the statement parses,
    which leaves ``{{stage_dataset}}`` looking exactly like a dataset called
    stage_dataset. It is not one -- it is a hole, and the file next door writes
    the very same dataset as a different hole.

    Treating those two words as two datasets would split one real table in two,
    cut the chain between them, and report no impact. So a dataset that came out
    of a placeholder is recorded as what it honestly is: not stated. A name with
    no dataset goes on matching any dataset, which is the safe direction --
    Ripple would rather show a finding somebody can dismiss by opening the file
    than hide one nobody will ever know was missed.
    """
    for t in stmt.find_all(exp.Table):
        db = t.text("db")
        if db and db.upper() in holes:
            t.set("db", None)


# ── a hole where the column list goes ──────────────────────────────────────
# A great many Airflow DAGs build their SQL like this::
#
#     cols = "cm13, cm14"
#     sql = f"CREATE OR REPLACE TABLE ds.final_published AS " \
#           f"SELECT {cols} FROM ds.customer_demographics"
#
# The placeholder is filled in by Python before BigQuery ever sees it, so the
# column list genuinely is "cm13, cm14" -- but it is not in the file, and Ripple
# reads `SELECT cols FROM ...`. Measured before this: Ripple believed the
# published table had exactly one column, called `cols`, and answered
# `reachesProduction False, risk none, unreadable 0, couldNotRead 0` -- a clean,
# confident, complete zero. Identical with ``.format()``.
#
# A hole in the projection list is a SELECT * that has not been filled in yet:
# it carries columns Ripple cannot see and names none of them. That is exactly
# what the star machinery already models -- the trail carries on, the table is
# listed as one whose column list is not visible, and every finding past it is
# marked worked out rather than read. So it is turned into one, and the screen
# is told what the file actually writes.
def _holes_in_the_select_list(stmt: exp.Expression, holes: set[str]) -> str:
    """Turn a placeholder standing where columns go into the star it is.

    Returns the placeholder's name, or "" if there was none.
    """
    if not holes:
        return ""
    found = ""
    for sel in list(stmt.find_all(exp.Select)):
        for e in list(sel.expressions):
            inner = e.this if isinstance(e, exp.Alias) else e
            if not isinstance(inner, exp.Column) or inner.table:
                continue
            if inner.name.upper() not in holes:
                continue
            found = inner.name
            e.replace(exp.Star())
    return found


@dataclass
class Usage:
    kind: str
    column: str            # the source column this usage refers to
    alias: str | None      # the name it is published as, when projected
    detail: str = ""       # e.g. the literal it is compared against
    # Whether the statement actually said which table this column came from.
    # In a warehouse where the same three key columns are in nearly every table,
    # most joins have the name on both sides, and "cm13" on its own does not say
    # whose. False means the usage is real and the table is a guess.
    certain: bool = True
    # Whether this column only leaves the statement because of a SELECT *. The
    # column really is carried through -- that is what a star does -- but the
    # column list is not written down anywhere, so nothing here can be pointed
    # at. Every finding on the far side of one of these is inferred, and says so.
    via_star: bool = False

    @property
    def label(self) -> str:
        return LOGIC_LABEL.get(self.kind, self.kind.title())


@dataclass
class Statement:
    file: str
    lang: str
    line_offset: int
    # The last line of the file this statement occupies. A finding is only ever
    # pointed at a line inside its own statement -- see _with_lines.
    line_end: int
    sql: str
    target: str | None
    sources: set[str]
    select: exp.Select | None
    expr: exp.Expression | None
    # "" for an ordinary statement; otherwise the word the file used to copy a
    # whole table -- COPY, CLONE, LIKE or RENAME. The hop is followed as a
    # SELECT *, because that is what it does, but the screen has to say what is
    # actually written or it is describing a statement that is not there.
    whole_copy: str = ""
    # "" when a SELECT * in this statement really is written as SELECT *.
    # Otherwise what the file writes instead -- a placeholder the job fills in
    # when it runs. It carries whatever columns it is handed and names none of
    # them, which is what a star does, so it is followed the same way; but no
    # screen may tell somebody the file says SELECT * when it does not.
    star_note: str = ""
    # Column names in this statement that Ripple put back by hand because the
    # parser read them as something else -- see _rescue_parenless_functions.
    # Every usage of one is real and every one of them is a guess about which
    # of two things the writer meant, so they are never asserted.
    guessed_columns: set = field(default_factory=set)
    # "" when the target table is written in the statement. Otherwise how the
    # name was worked out instead -- "dbt" or "file". The table name is nowhere
    # in this file, so anybody sent to the line to check would find no such
    # table written there, and a finding that does not say so reads as a fact
    # off the page. See _named_after_its_file.
    named_by: str = ""
    # "" for a statement written as SQL. Otherwise the words the file used to
    # run it as text -- today only EXECUTE IMMEDIATE. The statement is read
    # exactly as it will run, so the hop is real; but the line in the file is a
    # quoted string, and anybody sent to it to check would find a string rather
    # than the CREATE the row describes. See _reparse_run_as_text.
    built_as_text: str = ""
    # "" for an ordinary statement. Otherwise where this EXPORT DATA delivers
    # to -- gs://feed/partner. An export builds no table, so there is nothing
    # for the trail to carry the column on to, and every screen said "no
    # production table is affected", which is true and useless: the delivery
    # that breaks belongs to another team and was named nowhere at all.
    export_uri: str = ""
    # "" for an ordinary statement. Otherwise the script variable this one
    # fills: a DECLARE or a SET whose value is a query, or the row variable of
    # a FOR loop. The variable is not a table, but it behaves exactly like a
    # temporary one -- built here, read further down, and gone at the end of the
    # file -- so it is fenced and followed as one. See _bind_script_variables.
    script_var: str = ""
    # Worked out once and kept. One scan asks the same statement about the same
    # column many times over, and on a 600-line statement each answer means
    # walking the whole expression tree again. Measured on a repository the size
    # of his, this was most of the time a scan took.
    _names: dict = field(default_factory=dict, repr=False, compare=False)
    _projected: list | None = field(default=None, repr=False, compare=False)
    _sources_upper: set | None = field(default=None, repr=False, compare=False)
    _scopes: dict | None = field(default=None, repr=False, compare=False)

    def reads_from(self, table: str) -> bool:
        if self._sources_upper is None:
            self._sources_upper = {s.upper() for s in self.sources}
        return table.upper() in self._sources_upper


@dataclass
class ParsedRepo:
    statements: list[Statement] = field(default_factory=list)
    unreadable: list[dict] = field(default_factory=list)
    parsed_files: set[str] = field(default_factory=set)
    # Statements the reader could take in but not understand the shape of: a
    # procedure call, a loop, an EXECUTE IMMEDIATE, a scripting block. They are
    # kept per file rather than reported, because whether they matter depends
    # entirely on what is being scanned for. A loop over a table list is
    # nothing at all -- until the attribute you are chasing is named inside it.
    opaque: dict[str, list[dict]] = field(default_factory=dict)
    # Programs that run SQL kept in a separate .sql file rather than holding it
    # as text. Two folders of his pipeline are written this way. Where the .sql
    # file is in the repository this is nothing to worry about -- it was read on
    # its own account -- but the program is not empty either, and saying so is
    # the difference between "this DAG does nothing" and "this DAG runs that".
    runs_sql_from: list[dict] = field(default_factory=list)
    # DDL that names a table and its columns and carries no column anywhere: a
    # search index, a vector index, a row access policy, an UNDROP. Never an
    # edge and never a hop -- a dependency somebody has to go and change,
    # reported as one. See referenced_here.
    references: list[dict] = field(default_factory=list)
    # Which file CALLs a procedure defined in which other file. A CALL runs in
    # the SAME BigQuery session as the line above it, so the caller's temporary
    # tables really are visible inside the procedure -- and the per-file fence
    # renamed only the caller's side of that pair, so the chain died on the temp
    # table and the file that actually breaks was reported as "the name appears,
    # but no lineage to a production table". See _follow_procedure_calls.
    procedure_calls: list[dict] = field(default_factory=list)
    # Built on demand by reading(); see the note there.
    _by_source: dict | None = field(default=None, repr=False, compare=False)
    _indexed: int = field(default=-1, repr=False, compare=False)
    _ambiguous: set = field(default_factory=set, repr=False, compare=False)
    _datasets: dict = field(default_factory=dict, repr=False, compare=False)
    _spellings: dict = field(default_factory=dict, repr=False, compare=False)
    # Wildcard source names, e.g. CUSTOMER_DEMOGRAPHICS_*, kept apart from the
    # main index because they can never be found by an exact lookup. Almost
    # always empty, and skipped entirely when it is.
    _wildcards: dict = field(default_factory=dict, repr=False, compare=False)
    # short table name -> the files that build it from scratch. See rebuilt_in.
    _rebuilds: dict = field(default_factory=dict, repr=False, compare=False)

    def reading(self, table: str) -> list[Statement]:
        # Indexed rather than searched. A scan asks this once per table it
        # visits, and on a repository of a few thousand statements walking the
        # whole list each time was a large part of what a scan cost.
        #
        # Indexed on the short name and then filtered on the dataset, so a name
        # the SQL qualified is not merged with a same-named table in another
        # dataset -- and a name it did not qualify still matches everything, as
        # it must, because nothing has been said to tell them apart.
        self._index()
        candidates = self._by_source.get(short_name(table).upper(), [])
        if self._wildcards or is_wildcard(table):
            candidates = self._plus_wildcards(table, candidates)
        if not dataset_of(table):
            # A name with no dataset goes on matching anything -- except a
            # table that exists only inside one file. Nothing outside that file
            # can be reading it, so an unqualified name reaching one puts an
            # unrelated file's whole chain on the answer. See session_scope.
            kept: list[Statement] = []
            for s in candidates:
                matched = [src for src in s.sources if same_table(src, table)]
                if matched and all(is_session_scoped(src) for src in matched):
                    continue
                kept.append(s)
            return kept
        return [s for s in candidates if any(same_table(src, table) for src in s.sources)]

    def _plus_wildcards(self, table: str, candidates: list[Statement]) -> list[Statement]:
        """The same statements, plus any reached only through a wildcard name.

        An exact lookup can never find these: the key in the index is
        ``CUSTOMER_DEMOGRAPHICS_*`` and the table being followed is
        ``customer_demographics_20260101``. Missing them is what produced a
        clean "no impact" on every date-sharded table in the warehouse.
        """
        short = short_name(table).upper()
        extra: list[Statement] = []
        for pattern, stmts in self._wildcards.items():
            if pattern != short and wildcard_covers(pattern, short):
                extra.extend(stmts)
        if is_wildcard(table):
            # The other way round: somebody asked about the family itself, so
            # every shard read by name in the repository is part of the answer.
            for key, stmts in self._by_source.items():
                if key != short and wildcard_covers(short, key):
                    extra.extend(stmts)
        if not extra:
            return candidates
        out = list(candidates)
        seen = {id(s) for s in out}
        for s in extra:
            if id(s) not in seen:
                seen.add(id(s))
                out.append(s)
        return out

    def wildcards_covering(self, table: str) -> list[str]:
        """Wildcard names in this repository that take in ``table``.

        Used to say so on the result. A finding that only exists because a
        wildcard was followed reads as a plain fact about one table otherwise,
        and the person acting on it has no way to know a whole family of shards
        is what the SQL actually named.
        """
        return [p for p, _ in self.wildcards_covering_how(table)]

    def wildcards_covering_how(self, table: str) -> list[tuple[str, str]]:
        """The same, with HOW each one matched -- see wildcard_match.

        A real shard match is a fact about the SQL. The family name typed
        without its separator is a guess about what somebody meant, and the two
        must never leave here wearing the same word.
        """
        self._index()
        short = short_name(table).upper()
        # Given back as the SQL spells it, not as the index keys it. This goes
        # on screen and into the text search, and neither wants shouting.
        out = [(sorted(self._spellings.get(p, {p}))[0], wildcard_match(p, short))
               for p in self._wildcards if p != short]
        return sorted((p, how) for p, how in out if how)

    def _index(self) -> None:
        if self._by_source is not None and self._indexed == len(self.statements):
            return
        by_source: dict[str, list[Statement]] = {}
        wild: dict[str, list[Statement]] = {}
        rebuilds: dict[str, list[str]] = {}
        seen: dict[str, set[str]] = {}
        spelt: dict[str, set[str]] = {}
        bare: set[str] = set()
        for s in self.statements:
            # A CREATE that replaces the whole table. An INSERT or a MERGE adds
            # to one, and several files loading one table that way is ordinary;
            # two files REPLACING it is a fork. See rebuilt_in.
            if s.target and isinstance(s.expr, exp.Create) and not is_temporary(s.expr):
                seen_in = rebuilds.setdefault(short_name(s.target).upper(), [])
                if s.file not in seen_in:
                    seen_in.append(s.file)
            for src in s.sources:
                key = short_name(src).upper()
                by_source.setdefault(key, []).append(s)
                if key.endswith(_STAR):
                    wild.setdefault(key, []).append(s)
            for name in list(s.sources) + ([s.target] if s.target else []):
                short = short_name(name)
                ds = dataset_of(name)
                # A temp table's scope is not a dataset somebody wrote, it is a
                # fence Ripple put round one file. Counting it here would report
                # every ``t`` in the repository as a name standing for more than
                # one table -- a warning on something already told apart.
                if ds.startswith(_SCOPE_MARK):
                    continue
                if ds:
                    seen.setdefault(short.upper(), set()).add(ds.upper())
                else:
                    bare.add(short.upper())
                # How this name is actually spelt, capitals and all. BigQuery
                # treats ccm_Wireless_Enroll and ccm_wireless_enroll as two
                # different tables. Ripple matches them as one, because losing a
                # chain is the worse mistake -- and then says so, rather than
                # letting a finding read as a fact about one of them.
                spelt.setdefault(short.upper(), set()).add(short)
        self._by_source = by_source
        self._wildcards = wild
        self._rebuilds = rebuilds
        self._datasets = seen
        self._spellings = spelt
        # Names Ripple cannot be sure it is following one table under. Two ways:
        # the same name in two different datasets, or one dataset plus somewhere
        # else that names the table with no dataset at all -- the second is a
        # merge just as much as the first, and it is the one that produced a
        # finding about an archive table on a scan of the source table.
        #
        # In a fully templated repository almost no name has a dataset Ripple
        # can read, so almost nothing is flagged. That is the point: this fires
````

## Paste 12 of 25

### ripple/scanner/sqlread.py — piece 2 of 5

Add this to the END of `ripple/scanner/sqlread.py`, straight after what is already there. Do not start a new file. Do not re-type anything above.

````python
        # where there really is something to tell apart, and a warning printed
        # over every table is one nobody reads.
        self._ambiguous = {k for k, v in seen.items() if len(v) > 1 or k in bare}
        self._indexed = len(self.statements)

    def ambiguous_names(self) -> set[str]:
        """Short table names this repository uses in more than one dataset."""
        self._index()
        return self._ambiguous

    def datasets_for(self, table: str) -> list[str]:
        """Every dataset this repository writes or reads this table name in."""
        self._index()
        return sorted(self._datasets.get(short_name(table).upper(), set()))

    def spellings_for(self, table: str) -> list[str]:
        """Every way this table name is capitalised in the repository."""
        self._index()
        return sorted(self._spellings.get(short_name(table).upper(), set()))

    def display(self, table: str) -> str:
        """The name to put on screen: qualified only where it has to be."""
        if is_session_scoped(table):
            # The scope is Ripple's own fence round one file, not part of any
            # name anybody wrote. Putting it on screen would show a table name
            # that is in no file.
            return short_name(table)
        if short_name(table).upper() in self.ambiguous_names():
            return table
        return short_name(table)

    def rebuilt_in(self, table: str) -> list[str]:
        """Files that build this table from scratch, when more than one does.

        A CREATE OR REPLACE replaces the whole table, so only one of them can be
        the definition that runs. Two of them in two files is a fork -- usually a
        live copy and a stale one under archive/ or dev/ that nothing schedules.

        Measured before this: the ONLY finding reported came from the archive
        copy, presented with `breaking true, certain true` and the same wording
        as any live finding, while the live definition appeared under
        "mentions only". Where the real build is generated at deploy time and
        only the stale copy is committed, that is a confident, clean answer
        about a pipeline that no longer exists.

        Ripple cannot know which one runs -- nothing in the files says -- so it
        keeps following both and says so. Empty when only one file builds it,
        which is nearly always.
        """
        self._index()
        files = self._rebuilds.get(short_name(table).upper(), [])
        return files if len(files) > 1 else []

    def statements_in(self, path: str) -> list[Statement]:
        return [s for s in self.statements if s.file == path]


# ── parsing ────────────────────────────────────────────────────────────────
def _table_name(node: exp.Expression | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, exp.Schema):
        node = node.this
    if isinstance(node, exp.Table):
        return _qualify(node)
    if isinstance(node, exp.Expression):
        t = node.find(exp.Table)
        if t is not None:
            return _qualify(t)
    return None


def _target_of(stmt: exp.Expression) -> str | None:
    # MERGE matters as much as CREATE and INSERT. On BigQuery, Snowflake and
    # Databricks it is the usual way a production table is loaded -- without it
    # the chain stops one step short of the table anyone actually reads, and
    # Ripple reports "no production impact" for a change that plainly has some.
    #
    # DELETE and UPDATE matter for a different reason. They build nothing, so
    # they look uninteresting -- but a DELETE whose WHERE clause filters on the
    # attribute that is being decommissioned stops working on the day it goes,
    # and the table it prunes quietly fills up instead. Naming the table they
    # act on is what lets that be reported at all.
    # A CREATE TABLE FUNCTION publishes a name that other statements read in a
    # FROM clause. Checked first because it is also an exp.Create, and its
    # ``this`` is a function signature that _table_name finds no table in.
    # ALTER TABLE was in none of these, so a repository holding its own rename
    # migration -- ALTER TABLE stage.customers RENAME COLUMN email TO
    # email_address -- came back target None, sources [], and reported no impact
    # for the column it renames. The rename is the plainest alias hop there is,
    # and it was the one hop Ripple could not see.
    tvf = _table_function_target(stmt)
    if tvf:
        return tvf
    if isinstance(stmt, (exp.Create, exp.Insert, exp.Merge, exp.Delete, exp.Update, exp.Alter)):
        name = _table_name(stmt.this)
        # Nothing writes into INFORMATION_SCHEMA. A name that looks like one is
        # the catalogue being read, not a table being built, and cataloguing it
        # merges it with every real table sharing its short name.
        return None if name and is_metadata_read(name) else name
    return None


def _target_node(stmt: exp.Expression) -> exp.Table | None:
    """The table node a statement WRITES, as a node rather than as a name.

    Sources are gathered by walking every table in the statement, which finds
    the write target too, so it has to be left out. That used to be done by
    comparing NAMES with same_table -- and same_table is deliberately loose,
    because a name with no dataset has to go on matching one that has a dataset
    or every templated chain in the repository breaks.

    Loose is right for FOLLOWING a chain and catastrophic for EXCLUDING a
    source. Two real shapes were silently losing every source they had:

        CREATE OR REPLACE TABLE ds.events_rollup AS SELECT ... FROM ds.events_*
        CREATE OR REPLACE TABLE {{target_dataset}}.orders AS SELECT ... FROM stage.orders

    In the first the wildcard covers the target's own name; in the second the
    templated dataset is dropped, leaving a bare "orders" that matches
    "stage.orders". Either way the one source in the statement was thrown away,
    the statement was indexed as reading nothing, and the scan came back clean.

    Comparing the node itself cannot make that mistake, and it costs nothing.
    """
    if not isinstance(stmt, (exp.Create, exp.Insert, exp.Merge, exp.Delete, exp.Update)):
        return None
    node = stmt.this
    if isinstance(node, exp.Schema):
        node = node.this
    return node if isinstance(node, exp.Table) else None


# ── a table built as a whole copy of another ───────────────────────────────
# Four shapes, every one of them ordinary in a BigQuery pipeline, and not one of
# them has a SELECT anywhere in it::
#
#     CREATE OR REPLACE TABLE published.customers COPY  stage.customers
#     CREATE TABLE            published.customers CLONE stage.customers
#     CREATE TABLE            published.customers LIKE  stage.customers
#     ALTER TABLE stage.customers RENAME TO published.customers
#
# The last step of a great many pipelines is exactly this. The table is built in
# a staging dataset, checked, and then promoted into the published one by
# copying or renaming it -- so the promotion is the single line that connects
# everything upstream to the table people actually read.
#
# Ripple recorded no source for any of these, so the trail died at the staging
# table and the screen said "last table in the chain -- not matched by your
# production naming rule". That is the worst thing this tool can print: a calm,
# confident answer over less than the whole picture, on a change that breaks a
# published table one line further down the same folder.
#
# A whole-table copy carries every column and writes none of them down, which is
# precisely what ``SELECT *`` means. So it is turned into the ``SELECT *`` it
# already is, on the parsed copy only, and everything that knows how to follow a
# star -- carrying the column on, marking the hop as worked out rather than
# read, and listing the table as one whose column list cannot be seen -- works
# on it unchanged. What is shown on screen still says COPY, because that is what
# the file says.
_COPY_WORD = {True: "COPY", False: "CLONE"}


def _copy_source(stmt: exp.Expression) -> tuple[exp.Table, str] | None:
    """The table a CREATE ... COPY/CLONE/LIKE reads, and which word was used."""
    if not isinstance(stmt, exp.Create):
        return None
    clone = stmt.args.get("clone")
    if clone is not None and isinstance(clone.this, exp.Table):
        return clone.this, _COPY_WORD[bool(clone.args.get("copy"))]
    props = stmt.args.get("properties")
    for p in (props.expressions if props is not None else []):
        if isinstance(p, exp.LikeProperty) and isinstance(p.this, exp.Table):
            return p.this, "LIKE"
    return None


# CREATE SNAPSHOT TABLE published.customers CLONE stage.customers
#
# A snapshot is a copy like any other, but those two extra words are enough for
# the parser to give up on the whole statement and hand back something with no
# tables in it at all. Retried without them -- and only once the parser has
# already failed, so it costs nothing on any statement that reads normally.
_SNAPSHOT = re.compile(r"^\s*CREATE\s+SNAPSHOT\s+TABLE\b", re.IGNORECASE)


def _reparse_snapshot(raw: str, dialect: str | None) -> exp.Expression | None:
    """A CREATE SNAPSHOT TABLE read as the plain table copy it is."""
    if not _SNAPSHOT.match(raw):
        return None
    try:
        again = sqlglot.parse_one(_SNAPSHOT.sub("CREATE TABLE", raw, count=1),
                                  read=dialect)
    except Exception:
        return None
    return again if isinstance(again, exp.Create) else None


# ── SQL written as text and run later ──────────────────────────────────────
# EXECUTE IMMEDIATE is how a BigQuery script builds a statement at run time. The
# parser gives up on it and hands back a Command, so the CREATE inside it is
# read, understood as nothing, and the scan comes back with the column reaching
# nothing. Measured before this: a whole CREATE OR REPLACE TABLE of the scanned
# column, sitting in the file in plain sight, gave prod [].
#
# Only the plain shape is followed: the whole thing after IMMEDIATE is ONE
# string literal and nothing else. That literal IS the statement, exactly as it
# will run, so reading it is not a guess about anything.
#
# Everything else stays unreadable and says so:
#
#     EXECUTE IMMEDIATE FORMAT('CREATE TABLE %s ...', x)   the name is a value
#     EXECUTE IMMEDIATE 'CREATE TABLE ' || env || '_mid'   built by adding up
#     EXECUTE IMMEDIATE 'INSERT ... VALUES (?)' USING v    holes in the text
#
# In each of those the statement never exists as text anywhere, so there is
# nothing to read -- and inventing the missing piece would be exactly the
# confident-answer-over-less-than-the-picture failure this tool exists to avoid.
_EXECUTE_IMMEDIATE = re.compile(r"^\s*EXECUTE\s+IMMEDIATE\s+", re.IGNORECASE)
# What may legally follow the literal. Anything else means the statement is
# being built rather than quoted.
_AFTER_LITERAL = re.compile(r"^\s*(?:;|INTO\b|USING\b)", re.IGNORECASE)
BUILT_AS_TEXT = "EXECUTE IMMEDIATE"


def _one_string_literal(text: str) -> str | None:
    """The contents of ``text`` when it is exactly one quoted string, else None."""
    body = text.strip()
    for quote in ("'''", '"""', "'", '"'):
        if not body.startswith(quote):
            continue
        end = body.find(quote, len(quote))
        while end != -1 and body[end - 1] == "\\" and quote in ("'", '"'):
            end = body.find(quote, end + 1)
        if end == -1:
            return None
        inner = body[len(quote):end]
        rest = body[end + len(quote):]
        # A literal followed by anything other than the end of the statement,
        # an INTO or a USING is a literal being added to something.
        if rest.strip() and not _AFTER_LITERAL.match(rest):
            return None
        return inner
    return None


def _reparse_run_as_text(raw: str, dialect: str | None) -> list[exp.Expression] | None:
    """The statement inside a plain ``EXECUTE IMMEDIATE '<sql>'``, or None."""
    m = _EXECUTE_IMMEDIATE.match(raw)
    if not m:
        return None
    inner = _one_string_literal(raw[m.end():])
    if inner is None or not inner.strip():
        return None
    # A "?" is a value supplied by USING at run time. The text is complete
    # without it only when it is not there.
    if "?" in inner:
        return None
    try:
        got = [s for s in sqlglot.parse(inner, read=dialect) if s is not None]
    except Exception:
        return None
    # A literal that parses to nothing but another Command has told us nothing.
    return got if got and not all(isinstance(s, exp.Command) for s in got) else None


# ── DDL that names a table and its columns and builds nothing ──────────────
# A search index, a vector index and a row access policy all name a table and
# name columns of it, and none of them carries a column anywhere. The parser
# gives up on every one of them and hands back a Command with no tables in it,
# so the whole statement was invisible: measured `couldNotRead 1`, and nothing
# anywhere saying which table or which column it was about.
#
#     CREATE SEARCH INDEX idx ON `p.d.cust`(market_code, email)
#     CREATE ROW ACCESS POLICY apac ON `p.d.cust`
#       GRANT TO ('group:apac@acme.com') FILTER USING (market_code IN ('IN','SG'))
#     UNDROP TABLE `p.d.cust`
#
# These are read with a regular expression rather than a parser, deliberately.
# Nothing here becomes lineage -- no edge, no hop, no published table. It is a
# dependency somebody has to go and change, reported as exactly that. Reading it
# loosely can add a row to a list; it can never move a chain.
_INDEX_DDL = re.compile(
    r"\b(?P<verb>CREATE|DROP)\s+(?:OR\s+REPLACE\s+)?"
    r"(?P<kind>SEARCH|VECTOR)?\s*INDEX\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?"
    r"(?P<name>`[^`]+`|[\w.\-]+)\s+ON\s+(?P<table>`[^`]+`|[\w.\-]+)\s*(?P<cols>\([^)]*\))?",
    re.IGNORECASE,
)
_POLICY_DDL = re.compile(
    r"\b(?P<verb>CREATE|DROP)\s+(?:OR\s+REPLACE\s+)?ROW\s+ACCESS\s+POLICY\s+"
    r"(?:IF\s+(?:NOT\s+)?EXISTS\s+)?(?P<name>`[^`]+`|[\w.\-]+)\s+ON\s+"
    r"(?P<table>`[^`]+`|[\w.\-]+)",
    re.IGNORECASE,
)
_FILTER_USING = re.compile(r"\bFILTER\s+USING\s*\(", re.IGNORECASE)
_UNDROP = re.compile(r"\bUNDROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?P<table>`[^`]+`|[\w.\-]+)",
                     re.IGNORECASE)
# A bare word that is not a quoted string, a number or a SQL keyword.
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_NOT_A_COLUMN = {
    "AND", "OR", "NOT", "IN", "IS", "NULL", "TRUE", "FALSE", "LIKE", "BETWEEN", "CASE",
    "WHEN", "THEN", "ELSE", "END", "SESSION_USER", "CURRENT_TIMESTAMP", "CURRENT_DATE",
    "CAST", "AS", "STRING", "INT64", "FLOAT64", "BOOL", "DATE", "TIMESTAMP", "ANY", "ALL",
    "COLUMNS", "EXISTS", "SELECT", "FROM", "WHERE",
}


def _column_words(text: str) -> list[str]:
    """Every bare word in a fragment that could be a column name."""
    out: list[str] = []
    without_strings = re.sub(r"'[^']*'|\"[^\"]*\"", " ", text)
    for m in _WORD.finditer(without_strings):
        word = m.group(0)
        if word.upper() in _NOT_A_COLUMN or word in out:
            continue
        out.append(word)
    return out


def referenced_here(raw: str) -> dict | None:
    """The table and columns named by index, policy or UNDROP DDL, or None.

    Never lineage. A dependency on a table, reported as one.
    """
    m = _INDEX_DDL.search(raw)
    if m is not None:
        kind = (m.group("kind") or "").lower()
        cols = _column_words(m.group("cols") or "")
        return {
            "refKind": f"{kind} index".strip(),
            "refTable": _bare(m.group("table")),
            "refColumns": cols,
            "refVerb": m.group("verb").upper(),
        }
    m = _POLICY_DDL.search(raw)
    if m is not None:
        cols: list[str] = []
        using = _FILTER_USING.search(raw)
        if using is not None:
            open_at = raw.find("(", using.end() - 1)
            close_at = _balanced_brackets(raw, open_at) if open_at >= 0 else -1
            if close_at > 0:
                cols = _column_words(raw[open_at + 1:close_at - 1])
        return {
            "refKind": "row access policy",
            "refTable": _bare(m.group("table")),
            "refColumns": cols,
            "refVerb": m.group("verb").upper(),
        }
    m = _UNDROP.search(raw)
    if m is not None:
        return {"refKind": "UNDROP", "refTable": _bare(m.group("table")),
                "refColumns": [], "refVerb": "UNDROP"}
    return None


def _balanced_brackets(text: str, open_at: int) -> int:
    """The index just past the ``)`` closing the ``(`` at ``open_at``, or -1."""
    depth = 0
    quote = ""
    i = open_at
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == quote:
                quote = ""
        elif ch in "'\"`":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


# ── what an ALTER TABLE does to one column ─────────────────────────────────
# A migration file is where a rename is WRITTEN DOWN, in the plainest words the
# language has:
#
#     ALTER TABLE stage.customers RENAME COLUMN email TO email_address;
#
# Measured before this: target None, sources [], risk none. The one statement in
# the repository that states the rename outright was the one statement Ripple
# could not read, so a repository carrying its own migration reported no impact
# for the column the migration renames.
#
# Three actions matter, and they are three different answers:
#
#   RENAME COLUMN a TO b   the alias hop. The column carries on as b.
#   DROP COLUMN a          the column stops here, in this file, by name.
#   ALTER COLUMN a ...     the column is named, so the statement fails without it.
def _alter_actions(expr: exp.Expression | None) -> dict[str, tuple[str, str]]:
    """``{COLUMN: (kind, new name)}`` for every column an ALTER names."""
    if not isinstance(expr, exp.Alter):
        return {}
    out: dict[str, tuple[str, str]] = {}
    for action in expr.args.get("actions") or []:
        if isinstance(action, exp.RenameColumn):
            old = action.this.name if action.this is not None else ""
            new = action.args.get("to")
            new_name = new.name if new is not None else ""
            if old and new_name:
                out[old.upper()] = ("renamed", new_name)
        elif isinstance(action, exp.Drop) and isinstance(action.this, exp.Column):
            name = action.this.name
            if name:
                out[name.upper()] = ("dropped", "")
        elif isinstance(action, exp.AlterColumn):
            name = action.name or (action.this.name if action.this is not None else "")
            if name:
                out[name.upper()] = ("retyped", name)
    return out


def _renamed_to(stmt: exp.Expression) -> exp.Table | None:
    """The new name in ``ALTER TABLE old RENAME TO new``."""
    if not isinstance(stmt, exp.Alter):
        return None
    for action in stmt.args.get("actions") or []:
        if isinstance(action, RENAME_NODE) and isinstance(action.this, exp.Table):
            return action.this
    return None


def _as_whole_copy(stmt: exp.Expression) -> tuple[exp.Expression, str] | None:
    """This statement rewritten as the ``SELECT *`` it is, and how it was written.

    Returns None for everything that is not a whole-table copy, which is nearly
    every statement, so this costs two attribute lookups on the common path.
    """
    found = _copy_source(stmt)
    if found is not None:
        source, how = found
        target = stmt.this
    else:
        target = _renamed_to(stmt)
        if target is None:
            return None
        source, how = stmt.this, "RENAME"
    if not isinstance(source, exp.Table) or not isinstance(target, exp.Table):
        return None
    return (
        exp.Create(
            this=target.copy(),
            kind="TABLE",
            expression=exp.Select(expressions=[exp.Star()]).from_(source.copy()),
        ),
        how,
    )


def _cte_names(stmt: exp.Expression) -> set[str]:
    """Names defined by WITH in this statement. Not tables -- a CTE is a name
    for a query, and treating one as a table invents a link that is not there."""
    out: set[str] = set()
    for with_ in stmt.find_all(exp.With):
        for cte in with_.expressions:
            if cte.alias:
                out.add(cte.alias.upper())
    return out


# ── splitting a file into separate statements ──────────────────────────────
# Only used once a whole block has already been refused. sqlglot reads a file
# as one piece and gives up at the first statement it cannot follow, taking
# every other statement in the file down with it -- so one GRANT, one procedure
# call, one line written in a dialect the rest of the file is not in, costs the
# reader the entire file. Splitting first means one bad statement costs exactly
# one statement, and the file is reported as "3 of 14" rather than "unreadable".
def split_statements(sql: str) -> list[tuple[str, int]]:
    """(statement, 0-based line it starts on), split on real statement ends.

    Semicolons inside quotes and comments do not end a statement, which is the
    only reason this is not a call to ``str.split``.
    """
    out: list[tuple[str, int]] = []
    start = start_line = line = i = 0
    n = len(sql)
    quote = ""

    def keep(chunk: str, base: int) -> None:
        if not chunk.strip():
            return
        lead = len(chunk) - len(chunk.lstrip())
        out.append((chunk, base + chunk[:lead].count("\n")))

    while i < n:
        ch = sql[i]
        if ch == "\n":
            line += 1
            i += 1
        elif quote:
            if ch == "\\" and quote != "`":
                i += 2
            else:
                if ch == quote:
                    quote = ""
                i += 1
        elif ch in "'\"`":
            quote = ch
            i += 1
        elif sql.startswith("--", i) or ch == "#":
            found = sql.find("\n", i)
            i = n if found < 0 else found
        elif sql.startswith("/*", i):
            found = sql.find("*/", i + 2)
            end = n if found < 0 else found + 2
            line += sql.count("\n", i, end)
            i = end
        elif ch == ";":
            keep(sql[start:i], start_line)
            i += 1
            start, start_line = i, line
        else:
            i += 1
    keep(sql[start:], start_line)
    return out


def _first_code_line(chunk: str) -> str:
    """The first line of a statement worth showing on screen."""
    for raw in chunk.splitlines():
        line = raw.strip()
        if line and not line.startswith("--"):
            return line[:120]
    return chunk.strip()[:120]


def _with_lines(
    statements: list[exp.Expression], text: str, base_line: int
) -> list[tuple[exp.Expression, int, int]]:
    """Give each statement the lines of the file it actually occupies.

    sqlglot reads a whole block in one go and says nothing about where each
    statement started, so every statement in a file used to carry the same
    offset: the top of the block. A finding was then free to point at any line
    in the file that happened to score well -- and in a 600-line generated file
    with sixty statements, that regularly meant a finding about one table
    pointing at a WHERE clause belonging to a different table entirely. The
    finding was right and the line was somebody else's.

    ``split_statements`` already knows where each statement begins, and costs a
    single character scan rather than another parse. Where the two line up one
    for one, each statement gets its real span; where they do not, the block
    offset is used exactly as before rather than a span that might be wrong.
    """
    chunks = split_statements(text)
    if len(chunks) != len(statements):
        last = base_line + text.count("\n")
        return [(s, base_line, last) for s in statements]
    out: list[tuple[exp.Expression, int, int]] = []
    for stmt, (chunk, line) in zip(statements, chunks):
        start = base_line + line
        out.append((stmt, start, start + chunk.strip().count("\n")))
    return out


def _parse_text(
    text: str, dialect: str | None, base_line: int
) -> tuple[list[tuple[exp.Expression, int, int]], list[dict]]:
    """Parse a block; if it is refused, parse it one statement at a time."""
    try:
        got = [s for s in sqlglot.parse(text, read=dialect) if s is not None]
        return _with_lines(got, text, base_line), []
    except Exception:
        pass
    good: list[tuple[exp.Expression, int, int]] = []
    bad: list[dict] = []
    for chunk, line in split_statements(text):
        try:
            got = sqlglot.parse(chunk, read=dialect)
        except Exception:
            bad.append({"line": base_line + line + 1, "text": _first_code_line(chunk)})
            continue
        start = base_line + line
        end = start + chunk.strip().count("\n")
        good.extend((s, start, end) for s in got if s is not None)
    return good, bad


def _best_rendering(
    raw: str, plain: str, bad: list[dict],
    parsed: list, dialect: str | None, base_line: int,
) -> tuple[list, list[dict]]:
    """Re-read a template whose control flow stopped it parsing. See renderings.

    EVERY rendering that parses is kept, not the best one. Nothing in the file
    says which way it runs -- that is decided by a variable set somewhere else
    entirely -- so choosing a branch would be a guess, and a guess that went the
    wrong way loses a source table with nothing on any screen to say a branch
    existed. Measured on a real BigQuery warehouse: of 103 templated files with
    an if/else that read more than one way, 26 name DIFFERENT tables in their
    two branches. Reading one of those files one way and calling it read is the
    quietest version of this tool's worst failure.

    So both are read and both are followed. That is the trade this tool always
    makes: a spare row somebody can dismiss by opening the file, never a chain
    that is silently not there.

    Statements are de-duplicated on the SQL the parser actually saw, so the
    parts of the file OUTSIDE the branches -- which is nearly all of it -- are
    read once, not once per rendering.
    """
    best_bad = bad
    seen: set[str] = set()
    kept: list = []

    def take(rows: list) -> None:
        for row in rows:
            stmt = row[0]
            try:
                key = stmt.sql()
            except Exception:                              # noqa: BLE001
                key = repr(stmt)
            if key in seen:
                continue
            seen.add(key)
            kept.append(row)

    take(parsed)
    for rendered in renderings(raw):
        text = unwrap_blocks(fill_placeholders(rendered))
        text = rescue.rewrite(text)
        try:
            got, worse = _parse_text(text, dialect, base_line)
        except Exception:                                  # noqa: BLE001
            continue
        take(got)
        # The file is only still "could not be read" if EVERY way of reading it
        # refused something. One rendering reading cleanly means the file was
        # read, and saying otherwise sends somebody to look at a file that is
        # already understood.
        if len(worse) < len(best_bad):
            best_bad = worse
    return kept, best_bad


def _why_not(f: SourceFile, cfg: Settings, failures: list[dict], understood: int) -> dict:
    """One entry for the 'could not read' list, saying enough to act on.

    The point of this list is that somebody goes and checks those files by
    hand, so it has to name the line and show it. "ParseError" names nothing.
    """
    first = failures[0]
    total = understood + len(failures)
    if understood:
        reason = (f"{len(failures)} of {total} statements in this file could not be read - "
                  f"the other {understood} {'was' if understood == 1 else 'were'}")
    else:
        reason = "could not be read as SQL"
    hints: list[str] = []
    kind = describe_templating(f.text)
    if kind:
        hints.append(f"It is a template - it uses {kind}. Ripple fills those in before reading, "
                     f"and this part still did not parse.")
    if not cfg.sql_dialect:
        hints.append("This repository is being read as generic SQL. If it is BigQuery, Snowflake "
                     "or anything else in particular, choose that on the settings screen - it is "
                     "the most common reason a file will not parse.")
    return {
        "file": f.path,
        "reason": reason,
        "line": first["line"],
        "snippet": first["text"],
        "hint": " ".join(hints),
    }


# ── a query with no CREATE in front of it ──────────────────────────────────
# A dbt model is a bare SELECT. There is no CREATE, no INSERT and no MERGE, so
# nothing in the file names a table it builds -- dbt names it, after the file.
# ``models/marts/customer_published.sql`` builds ``customer_published``.
#
# Measured before this existed: a three-hop dbt chain gave productionTables 0,
# reachesProduction false, and the finding text "Selected straight through into
# the next table" when there was no next table. Every dbt repository on earth,
# and dbt is the commonest way a BigQuery pipeline is written, produced ZERO
# lineage. That is the loudest possible version of Ripple's worst failure: a
# calm, clean, complete no-impact answer over none of the picture.
#
# The name is not a guess. dbt's model name IS its file stem -- that is the rule
# the tool itself runs on, and ``ref('customer_published')`` elsewhere in the
# repository resolves through exactly the same rule. Dataform and every
# hand-rolled "one query per file" runner work the same way.
#
# Two levels of evidence, and they are labelled differently on screen because
# they are not equally sure:
#
# * "dbt" -- the file is under models/ or snapshots/, or it calls ref(),
#   source() or config(). The tool that runs this file names the table.
# * "file" -- a .sql file holding exactly one query and no CREATE anywhere.
#   Something runs it and puts the rows somewhere; naming that somewhere after
#   the file is the convention every such runner uses. Following it costs a row
#   somebody can dismiss by opening the file. Not following it costs the chain.
#
# Only ever done when the file holds ONE statement and that statement builds
# nothing. Two bare SELECTs in one file cannot both be the table the file is
# named after, and guessing which would merge two unrelated queries into one.
_DBT_FOLDER = re.compile(r"(?:^|/)(?:models|snapshots|definitions)/", re.IGNORECASE)
# Dataform's own header. Its models are named after their files too.
_DATAFORM_CONFIG = re.compile(r"^[ \t]*config\s*\{", re.IGNORECASE | re.MULTILINE)
_DBT_CALL = re.compile(r"\{\{-?\s*(?:config|ref|source|this)\b", re.IGNORECASE)
# A query, rather than something that builds a table. A UNION of two SELECTs and
# a WITH ... SELECT are both queries; sqlglot wraps the second in the Select
# itself, so only these three shapes need naming.
_A_QUERY = (exp.Select, exp.Union, exp.Subquery)

# The file has to say SELECT, in its own words, on its own first line of code.
# Asking the parse tree is not enough: several statements that build nothing and
# are named after nothing are rewritten into a bare SELECT on the way into the
# parser -- EXPORT DATA is the one that caught this -- and by the time the tree
# exists they are indistinguishable from a dbt model. EXPORT DATA delivers a file
# to somebody outside the warehouse; calling its destination "a.sql" would be a
# table that does not exist anywhere.
_LINE_COMMENT = re.compile(r"(--|#)[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_QUERY_WORD = re.compile(r"^\s*(?:\(\s*)?(SELECT|WITH)\b", re.IGNORECASE)


def _is_one_query(text: str) -> bool:
    """Does this file open with SELECT or WITH once the wrapping is taken off?"""
    body = fill_placeholders(text) if has_placeholders(text) else text
    body = _BLOCK_COMMENT.sub(" ", body)
    body = _LINE_COMMENT.sub("", body)
    return bool(_QUERY_WORD.match(body.lstrip()))


# ── a column named after a function ────────────────────────────────────────
# BigQuery lets four of its built-ins be called with no brackets, so
# ``SELECT current_date FROM customer_demographics`` parses as a call to
# CURRENT_DATE and not as a column at all. A table with a column of that name
# then produces the cleanest possible zero: `risk none, prod [], found 0,
# nameInTables 0` -- Ripple did not miss the column, it never saw one.
# Backticked, the very same scan is `risk medium` and reaches production.
#
# Which of the two the writer meant cannot be known from the file: both are
# valid BigQuery and both are written exactly the same way. So both are
# followed, and the row says the table is a guess -- Ripple's standing rule,
# because a spare row is dismissed by opening the file and a lost chain is
# never seen at all.
#
# Only where the file writes the name with NO brackets. ``CURRENT_DATE()`` is
# unambiguously the function.
_PARENLESS = {
    "CURRENT_DATE": exp.CurrentDate,
    "CURRENT_TIME": getattr(exp, "CurrentTime", None),
    "CURRENT_TIMESTAMP": getattr(exp, "CurrentTimestamp", None),
    "CURRENT_DATETIME": getattr(exp, "CurrentDatetime", None),
}
_PARENLESS_NODES = tuple(n for n in _PARENLESS.values() if n is not None)


def _written_without_brackets(text: str) -> set[str]:
    """Which parenless built-ins this text writes with no brackets after them."""
    out: set[str] = set()
    upper = text.upper()
    for name in _PARENLESS:
        if name not in upper:
            continue
        for m in re.finditer(r"\b" + name + r"\b\s*(\()?", upper):
            if not m.group(1):
                out.add(name)
                break
    return out


def _rescue_parenless_functions(stmt: exp.Expression, bare: set[str]) -> set[str]:
    """Read those names as columns as well. Returns the ones put back."""
    put_back: set[str] = set()
    if not bare or not _PARENLESS_NODES:
        return put_back
    for node in list(stmt.find_all(*_PARENLESS_NODES)):
        name = next((k for k, v in _PARENLESS.items()
                     if v is not None and isinstance(node, v)), "")
        if name not in bare or node.args:
            continue
        replacement = exp.column(name.lower())
        if node.parent is None:
            continue
        node.replace(replacement)
        put_back.add(name)
    return put_back


# FOR <var> IN (...) DO -- the line the loop header was rewritten from. Read off
# the file rather than the rewritten SQL, because the rewrite is what threw the
# variable away and this is the one place the original wording survives.
_LOOP_ROW = re.compile(r"^\s*FOR\s+(\w+)\s+IN\b", re.IGNORECASE)


def _is_loop_row(f: SourceFile, stmt: Statement) -> bool:
    """Was this temporary table a FOR loop's row variable in the file itself?

    The rewrite turns the header into ``CREATE TEMP TABLE rec AS ...`` so that
    the rows the loop walks can be followed like anything else with a name. The
    file says ``FOR rec IN``, and the row on screen points at that line -- so
    the name really is written where the reader is sent, which is the whole test
    for whether Ripple is allowed to use it.
    """
    lines = f.text.splitlines()
    if not 0 <= stmt.line_offset < len(lines):
        return False
    found = _LOOP_ROW.match(lines[stmt.line_offset])
    return bool(found and found.group(1).upper() == short_name(stmt.target or "").upper())


def _declared_variable(stmt: exp.Expression) -> str:
    """The variable a DECLARE or a SET fills FROM A QUERY, or "".

        DECLARE cutoff DATE DEFAULT (SELECT MAX(cm13) FROM customer_demographics);
        CREATE OR REPLACE TABLE final_published AS
        SELECT order_id, amount FROM orders WHERE order_date > cutoff;

    Measured before this: groups [], filed as a dead end two lines above the
    CREATE that uses it. final_published's whole row set is chosen by cutoff,
    which IS MAX(cm13), so removing the column stops that statement compiling
    and stops the published table loading.

    Only a value that holds a query counts. ``DECLARE i INT64 DEFAULT 0`` binds
    nothing anybody can follow, and giving every loop counter a table of its own
    would fill the screen with names that lead nowhere.
    """
    # Everything here is checked for being an expression before it is walked.
    # sqlglot puts plain booleans in some of these slots -- BEGIN TRANSACTION is
    # an exp.Set with no assignment in it at all -- and reaching for .find on one
    # took down the whole file with an AttributeError.
    if isinstance(stmt, exp.Declare):
        for item in stmt.expressions:
            if not isinstance(item, exp.DeclareItem):
                continue
            value = item.args.get("default")
            if not isinstance(value, exp.Expression) or value.find(exp.Select) is None:
                continue
            named = item.args.get("this")
            first = named[0] if isinstance(named, list) and named else named
````

## Paste 13 of 25

### ripple/scanner/sqlread.py — piece 3 of 5

Add this to the END of `ripple/scanner/sqlread.py`, straight after what is already there. Do not start a new file. Do not re-type anything above.

````python
            if isinstance(first, exp.Expression) and getattr(first, "name", ""):
                return first.name
    if isinstance(stmt, exp.Set):
        for item in stmt.expressions:
            eq = item.args.get("this") if isinstance(item, exp.SetItem) else item
            if not isinstance(eq, exp.EQ):
                continue
            value = eq.expression
            if not isinstance(value, exp.Expression) or value.find(exp.Select) is None:
                continue
            if isinstance(eq.this, exp.Column) and eq.this.name:
                return eq.this.name
    return ""


def _bind_script_variables(f: SourceFile, out: list[Statement]) -> None:
    """Join a statement that FILLS a script variable to the ones that READ it.

    A BigQuery script does not only pass values from table to table. It passes
    them through variables -- a watermark from a DECLARE, a row from a FOR loop
    -- and both halves were being read as separate statements that had nothing
    to do with each other. Measured on both shapes: groups [], no production
    table named, over a change that really does break the published table.

    The variable is already fenced to this file by _scope_session_tables, so
    ``cutoff`` in one file cannot join up with ``cutoff`` in another. This adds
    it to the SOURCES of every statement in the file that names it, which is
    what makes the usage in a WHERE, or ``rec.seg`` in a VALUES list, count.

    Both spellings are counted: the bare name for a scalar, and the qualifier
    for a loop row. Neither is guessed at -- the name has to have been declared
    in this very file for anything to happen at all.
    """
    variables = {short_name(s.target).upper(): s.target
                 for s in out if s.script_var and s.target}
    if not variables:
        return
    for s in out:
        if s.expr is None or (s.target and short_name(s.target).upper() in variables):
            continue
        named: set[str] = set()
        for col in s.expr.find_all(exp.Column):
            for spelling in (col.table, col.name):
                if spelling and spelling.upper() in variables:
                    named.add(variables[spelling.upper()])
        if named:
            s.sources = set(s.sources) | named
            s._sources_upper = None


def _scope_session_tables(f: SourceFile, out: list[Statement]) -> None:
    """Fence this file's temporary tables off from every other file's.

    Done once the whole file is parsed, so a temp table used above the line that
    creates it is still caught. Only names with no dataset, or the ``_SESSION``
    dataset BigQuery uses for them, are moved: ``ds.t`` is a real table that
    happens to share a short name with a temp one, and taking it would cut a
    genuine chain. See the note above session_scope.
    """
    names: set[str] = set()
    for s in out:
        if s.target and (is_temporary(s.expr) or s.script_var
                         or dataset_of(s.target).upper() == _SESSION_DATASET):
            names.add(short_name(s.target).upper())
    if not names:
        return
    scope = session_scope(f.path)

    def scoped(name: str) -> str:
        if short_name(name).upper() not in names:
            return name
        ds = dataset_of(name).upper()
        if ds and ds != _SESSION_DATASET:
            return name
        return scope + "." + short_name(name)

    for s in out:
        if s.target:
            s.target = scoped(s.target)
        s.sources = {scoped(x) for x in s.sources}
        s._sources_upper = None


def _named_after_its_file(f: SourceFile, stmt: Statement, alone: bool) -> str:
    """The tool that names this file's one query, "file", or "".

    "dbt" and "Dataform" are facts: both tools name a model after its file, and
    a ``ref()`` elsewhere in the repository resolves through the same rule.
    "file" is the weaker reading -- one query, no CREATE, and something runs it,
    so it only applies when the whole file is that one query.

    A Dataform model can have ``pre_operations`` beside it, which are real
    statements with real targets. The model is still the one query that builds
    nothing of its own, so ``alone`` is not required there.
    """
    lowered = f.path.lower()
    if not (lowered.endswith(".sql") or lowered.endswith(".sqlx")):
        return ""
    if stmt.target or not isinstance(stmt.expr, _A_QUERY):
        return ""
    if lowered.endswith(".sqlx") or _DATAFORM_CONFIG.search(f.text):
        return "Dataform"
    if not alone or not _is_one_query(f.text):
        return ""
    if _DBT_FOLDER.search(f.path) or _DBT_CALL.search(f.text):
        return "dbt"
    return "file"


def parse_file(f: SourceFile, cfg: Settings) -> tuple[list[Statement], list[dict], list[dict]]:
    """Parse one file into statements, failures, and statements not understood.

    Failures are reported, never swallowed. The third list is the statements the
    reader took in but could not make sense of; they are handed back rather than
    reported, because whether they matter depends on the scan.
    """
    out: list[Statement] = []
    problems: list[dict] = []
    blocks = statements_for(f)
    # More SQL is written in this file than could be taken out of it. Asked
    # whether or not any block came out: an Airflow YAML, an Oozie workflow and
    # a shell job all normally hold several tasks of different kinds, and one
    # recognised block used to buy silence for the one beside it. See
    # looks_like_unread_sql.
    left_behind = looks_like_unread_sql(f, blocks)
    if left_behind:
        # Written as two whole sentences rather than one with a word slotted
        # into it. The slotted version read "Ripple could not take some of out
        # of it", which is not English -- on the one list whose whole job is to
        # persuade somebody to go and open a file.
        reason = ("some of the SQL written in this file could not be taken out of it"
                  if blocks else
                  "there is SQL written in this file that Ripple could not take out of it")
        problems.append({
            "file": f.path,
            "reason": reason,
            "line": 1,
            "snippet": _first_code_line(f.text),
            "hint": (("Some of this file was read and some of it was not - what is below is "
                      "not the whole of it. " if blocks else
                      "The statement is most likely built by adding short pieces of text "
                      "together, so it never exists in the file as one thing to read. ")
                     + "Open it and check by hand."),
        })
    if not blocks:
        return out, problems, []

    # For Spark/Scala jobs the destination is in the program, not the SQL.
    writes = written_tables(f)
    implied_target = writes[0] if len(writes) == 1 else None
    if len(writes) > 1:
        problems.append(
            {
                "file": f.path,
                "reason": (
                    f"writes to {len(writes)} tables ({', '.join(writes)}) - Ripple cannot tell "
                    f"which query feeds which, so lineage past this job is not traced"
                ),
            }
        )

    dialect = cfg.sql_dialect or None
    failures: list[dict] = []
    opaque: list[dict] = []
    for sql_text, offset in blocks:
        # Templating is filled in and scripting keywords are dropped on the way
        # into the parser only. Everything shown on screen still comes from the
        # file exactly as it is written, on the line it is written on.
        templated = has_placeholders(sql_text)
        text = fill_placeholders(sql_text) if templated else sql_text
        holes = placeholder_names(sql_text) if templated else set()
        # Handed straight over rather than asked about first: unwrap_blocks
        # gives the text back unchanged when there is no scripting in it, and
        # asking first meant walking every line of every file twice.
        text = unwrap_blocks(text)
        # Shapes the parser refuses outright, rewritten into ones it reads. Five
        # of them are a hard parse error, which loses the neighbouring
        # statements too; four fall back to a node with no tables in it, which
        # is invisible. See scanner/rescue.py.
        # Where each EXPORT DATA delivers to, read BEFORE the rewrite takes the
        # OPTIONS clause off. Every rewrite keeps the line count, so these line
        # numbers still line up with the statements that come out below.
        exports = rescue.export_targets(text)
        text = rescue.rewrite(text)
        parsed, bad = _parse_text(text, dialect, offset)
        # A template that uses its own control flow -- an if/else, a {% set %}
        # block, a whole block of SQL dropped in on one line -- does not survive
        # having its tags blanked and every body kept. Rendered the ordinary
        # way it is not half a file, it is no file at all: 176 of one real
        # warehouse's .sql files parsed to nothing. Each rendering is tried only
        # because THIS one failed, so a file that reads today cannot start
        # reading differently. See templating.renderings.
        if bad and templated:
            parsed, bad = _best_rendering(sql_text, text, bad, parsed,
                                          dialect, offset)
        failures.extend(bad)
        # CURRENT_DATE and its three siblings can be written with no brackets,
        # so a column of that name parses as a call and is invisible. See
        # _rescue_parenless_functions.
        bare = _written_without_brackets(sql_text)
        # Matched to statements in file order rather than by line number. The
        # rewrite takes the whole ``EXPORT DATA OPTIONS(...) AS`` away, so what
        # is left starts on the line AFTER the export's own -- the export at
        # line 0 belongs to the SELECT the parser reports at line 1.
        pending = sorted(exports)
        for outer, line, line_end in parsed:
            export_uri = ""
            while pending and pending[0][0] <= line_end:
                export_uri = pending.pop(0)[1]
            # A scripting block, a loop, a procedure call, an EXECUTE IMMEDIATE.
            # Kept, not reported: whether it matters depends on whether the name
            # somebody is chasing turns up inside it, which is not known here.
            inside: list[tuple[exp.Expression, str]] = [(outer, "")]
            if isinstance(outer, exp.Command):
                raw = outer.sql()
                again = _reparse_snapshot(raw, dialect)
                run = None if again is not None else _reparse_run_as_text(raw, dialect)
                if again is not None:
                    inside = [(again, "")]
                elif run is not None:
                    # SQL written as text and run later. The literal IS the
                    # statement, exactly as it will run, so it is read -- and
                    # every finding out of it says where it came from.
                    inside = [(s, BUILT_AS_TEXT) for s in run]
                else:
                    entry = {"line": line + 1, "text": _first_code_line(raw),
                             "sql": raw[:8000]}
                    # DDL that names a table and its columns and builds nothing:
                    # a search index, a row access policy, an UNDROP. Read for
                    # what it names, never turned into lineage.
                    ref = referenced_here(raw)
                    if ref is not None:
                        entry.update(ref)
                    opaque.append(entry)
                    continue
            for stmt, built_as_text in inside:
                guessed = _rescue_parenless_functions(stmt, bare)
                star_note = ""
                if holes:
                    _forget_templated_datasets(stmt, holes)
                    # A placeholder standing where the column list goes is a
                    # SELECT * nobody has filled in yet. See _holes_in_the_select_list.
                    filled = _holes_in_the_select_list(stmt, holes)
                    if filled:
                        star_note = ("a placeholder - this statement's column list is "
                                     "filled in when the job runs")
                # A whole-table copy or a rename has no SELECT in it at all, so the
                # chain used to stop dead on the one line that promotes a staging
                # table into the published one. See the note above _copy_source.
                written = stmt.sql()
                whole_copy = ""
                rewritten = _as_whole_copy(stmt)
                if rewritten is not None:
                    stmt, whole_copy = rewritten
                select = stmt.find(exp.Select)
                target = _target_of(stmt) or implied_target
                # A DECLARE or a SET filled from a query builds something the
                # rest of the file reads by name. See _declared_variable.
                script_var = _declared_variable(stmt)
                if script_var and not target:
                    target = script_var
                sources: set[str] = set()
                skip = _cte_names(stmt)
                # A MERGE whose USING names a table directly has no SELECT anywhere
                # in it, so it recorded no sources -- which meant the statement that
                # loads the published table was never indexed as reading anything,
                # and no scan could reach it however hard it looked. The same is
                # true of UPDATE ... FROM, which reads a whole second table and had
                # only ever recorded the table it writes.
                if select is not None or isinstance(stmt, (exp.Merge, exp.Delete, exp.Update)):
                    # Every table the whole statement reads, not just the ones in
                    # its first SELECT. A union is two SELECTs side by side, and
                    # looking only at the first made the second half of every
                    # ..._BCA_UNION table invisible: the statement was never
                    # recorded as reading that table at all, so a change to it
                    # produced no findings anywhere and the scan came back clean.
                    written = _target_node(stmt)
                    written_id = id(written) if written is not None else None
                    for t in stmt.find_all(exp.Table):
                        # The write target, left out by identity rather than by
                        # name. See the note above _target_node for what comparing
                        # names cost.
                        if written_id is not None and id(t) == written_id:
                            continue
                        qualified = _qualify(t)
                        # A metadata view is the warehouse describing itself. It
                        # carries no column of anybody's table, and its names --
                        # COLUMNS, TABLES, JOBS -- collide with real ones. See
                        # is_metadata_read.
                        if (qualified and t.name.upper() not in skip
                                and not is_metadata_read(qualified)):
                            sources.add(qualified)
                        # APPENDS(TABLE t, ...) and a TVF given a table: the table
                        # handed in is a real read and is nowhere else in the tree.
                        for handed in _tables_handed_to_a_call(t):
                            if short_name(handed).upper() not in skip:
                                sources.add(handed)
                # A DELETE or an UPDATE reads the table it changes. Without this the
                # statement has no source, so nothing ever looks at its WHERE clause
                # -- and a filter on a column that is about to disappear is exactly
                # the kind of thing this tool exists to find.
                # An ALTER is the same shape: it names one table and changes it in
                # place, and a RENAME COLUMN on it is an alias hop like any other.
                if isinstance(stmt, (exp.Delete, exp.Update, exp.Alter)) and target:
                    sources.add(target)
                # A DECLARE has no SELECT the loop above would walk into, so the
                # table its value is read from was recorded nowhere.
                if script_var and not sources:
                    for t in stmt.find_all(exp.Table):
                        qualified = _qualify(t)
                        if qualified and not is_metadata_read(qualified):
                            sources.add(qualified)
                out.append(
                    Statement(
                        file=f.path,
                        lang=f.lang,
                        line_offset=line,
                        line_end=line_end,
                        sql=written,
                        target=target,
                        sources=sources,
                        select=select,
                        expr=stmt,
                        whole_copy=whole_copy,
                        star_note=star_note,
                        guessed_columns=guessed,
                        built_as_text=built_as_text,
                        export_uri=export_uri,
                        script_var=script_var,
                    )
                )
    # A FOR loop's row variable is filled by its header, which is rewritten into
    # a temporary table of that name on the way into the parser. See _loop_read.
    for s in out:
        if not s.script_var and s.target and is_temporary(s.expr) and _is_loop_row(f, s):
            s.script_var = short_name(s.target)
    # A temporary table belongs to the file that made it and to nothing else.
    _scope_session_tables(f, out)
    # ... and now the statements that read those variables can be joined to the
    # ones that fill them. After the fence, so the names match.
    _bind_script_variables(f, out)
    # A file that is one query and builds nothing names its table after itself.
    # Done here rather than in the loop above because it is only true when the
    # whole file is that one query -- see _named_after_its_file.
    building_nothing = [s for s in out if s.target is None and isinstance(s.expr, _A_QUERY)]
    if len(building_nothing) == 1:
        one = building_nothing[0]
        how = _named_after_its_file(f, one, alone=len(out) == 1)
        if how:
            one.target = Path(f.path).stem
            one.named_by = how
    # DDL that builds nothing but names a table and its columns -- an index, a
    # row access policy, an UNDROP. Ripple DID learn what it names, and reports
    # it as exactly that rather than as a file nobody could read. Left on the
    # "check by hand" list it was pure noise on the one list that has to stay
    # short enough for somebody to read to the bottom of.
    lost = [o for o in opaque if not o.get("refKind")]
    if failures:
        failures.sort(key=lambda p: p["line"])
        problems.append(_why_not(f, cfg, failures, len(out)))
    elif lost and not out:
        # Nothing in this file was understood. The reader did not fall over, it
        # simply got nothing out -- which is the quietest way to lose a file and
        # the reason the wrong SQL dialect used to look like a clean repository.
        first = lost[0]
        problems.append({
            "file": f.path,
            "reason": f"read, but not one of its {len(lost)} statements was understood",
            "line": first["line"],
            "snippet": first["text"],
            "hint": ("Nothing was learned from this file at all - no table, no column, no "
                     "lineage." + ("" if cfg.sql_dialect else
                     " This repository is being read as generic SQL; if it is BigQuery, "
                     "Snowflake or anything else in particular, choose that on the settings "
                     "screen.")),
        })
    return out, problems, opaque


def parse_repo(index: RepoIndex, cfg: Settings | None = None, on_progress=None) -> ParsedRepo:
    """Read every file as SQL. ``on_progress(done, total, label)`` is called as
    it goes: on a repository of a few thousand files this is minutes of work,
    and it is by far the slowest thing Ripple does."""
    cfg = cfg or default_settings
    pr = ParsedRepo()
    problems: list[dict] = list(index.skipped)
    total = len(index.files)
    for done, f in enumerate(index.files, start=1):
        if on_progress is not None and (done % 10 == 0 or done == total):
            on_progress(done, total, "Understanding the SQL")
        try:
            stmts, file_problems, opaque = parse_file(f, cfg)
        except Exception as exc:
            # Reading a repository takes minutes. Letting one unexpected shape
            # end the whole thing with a traceback loses every file after it,
            # and the person is left with nothing at all rather than with an
            # answer and one file to check by hand.
            log.warning("could not read %s: %s", f.path, exc)
            problems.append({
                "file": f.path,
                "reason": (f"Ripple could not read this file at all "
                           f"({type(exc).__name__}) - check it by hand"),
            })
            continue
        if stmts:
            pr.statements.extend(stmts)
            pr.parsed_files.add(f.path)
        if opaque:
            pr.opaque[f.path] = opaque
            pr.references.extend(
                {"file": f.path, "line": o["line"], "snippet": o["text"],
                 "kind": o["refKind"], "table": o["refTable"],
                 "columns": o["refColumns"], "verb": o["refVerb"]}
                for o in opaque if o.get("refKind")
            )
        problems.extend(file_problems)
    problems.extend(_follow_sql_file_refs(index, pr))
    # Done once every file is parsed, because the two ends of a CALL are in two
    # different files and neither one alone can see the pair.
    _follow_procedure_calls(index, pr)
    pr.unreadable = _one_entry_per_file(problems)
    return pr


def _follow_sql_file_refs(index: RepoIndex, pr: ParsedRepo) -> list[dict]:
    """Match every program that names a .sql file to the file it names.

    Found is the good case and is only recorded. Not found is a real hole: the
    program runs a query that is not in this repository, so nothing in it has
    been read and no scan can cover it.
    """
    by_path = {f.path.lower(): f.path for f in index.files}
    by_name: dict[str, str] = {}
    for f in index.files:
        if f.path.lower().endswith(".sql"):
            by_name.setdefault(f.path.rsplit("/", 1)[-1].lower(), f.path)

    missing: list[dict] = []
    for f in index.files:
        for ref in sql_file_refs(f):
            wanted = ref["ref"].replace("\\", "/").lstrip("./")
            runs = by_path.get(wanted.lower()) or by_name.get(wanted.rsplit("/", 1)[-1].lower(), "")
            pr.runs_sql_from.append(
                {"file": f.path, "ref": ref["ref"], "line": ref["line"], "runs": runs}
            )
            if runs:
                continue
            missing.append({
                "file": f.path,
                "reason": f"runs the SQL in {ref['ref']}, which is not in this repository",
                "line": ref["line"],
                "snippet": ref["ref"],
                "hint": ("Ripple has never read that query, so nothing it does is covered by "
                         "this scan. If the file lives in another repository, scan that one "
                         "too; if it is generated at run time, it has to be checked by hand."),
            })
    return missing


# ── a procedure CALLed from another file ───────────────────────────────────
# CALL ds.publish_it() runs in the SAME session as the statement above it, so a
# TEMP table the caller has just built IS visible inside the procedure. Ripple's
# fence round temporary tables (see session_scope) renamed the CALLER's "stg" to
# "#A_SQL.stg" and left the procedure's "stg" alone, so the two stopped matching
# and the trail died on the temp table -- with the file that really breaks filed
# under "the name appears, but no lineage to a production table", which is the
# one sentence this tool exists to stop anybody printing over a live chain.
#
# Read off the file TEXT rather than the parse tree, because neither end
# survives parsing: the procedure signature is dropped on the way in (that is
# what lets the body be read at all), and the CALL comes out as a statement
# nobody understood.
#
# Short name only, and every file defining that name is taken. This is
# FOLLOWING a chain, which is the side of that rule where a loose match is
# right -- and the dataset in front of a procedure name is usually a
# placeholder in these files anyway.
_PROCEDURE_DEF = re.compile(
    r"^[ \t]*CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(?:IF\s+NOT\s+EXISTS\s+)?"
    r"([`\"\w.${}-]+)", re.IGNORECASE | re.MULTILINE)
_PROCEDURE_CALL = re.compile(r"(?<![\w.])CALL\s+([`\"\w.${}-]+)\s*\(", re.IGNORECASE)


def _reached_through(edges: dict[str, set[str]], start: str) -> set[str]:
    """Every file reachable from this one by following CALL edges."""
    seen: set[str] = set()
    stack = [start]
    while stack:
        for nxt in edges.get(stack.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    seen.discard(start)
    return seen


def _follow_procedure_calls(index: RepoIndex, pr: ParsedRepo) -> None:
    """Let a temporary table cross a CALL, and let nothing else cross it.

    The fence stays exactly as it is. A name is only unfenced along an edge
    Ripple can point at: this file CALLs a procedure, that file defines it, so
    the two run in one session and one file's temp table is the other's.
    Everything else -- two files that both build a ``stg`` and never call each
    other -- is untouched, which is the whole reason the fence exists.

    Widened, never replaced: the plain ``stg`` stays in sources beside the
    scoped one. So nothing that matched before stops matching, and where two
    different callers hand their own ``stg`` to the SAME procedure both are
    added and both chains are followed rather than one being guessed at.
    """
    defined: dict[str, list[str]] = {}
    called: dict[str, set[str]] = {}
    for f in index.files:
        for m in _PROCEDURE_DEF.finditer(f.text):
            defined.setdefault(short_name(_bare(m.group(1))).upper(), []).append(f.path)
        for m in _PROCEDURE_CALL.finditer(f.text):
            called.setdefault(f.path, set()).add(short_name(_bare(m.group(1))).upper())
    if not defined or not called:
        return

    runs: dict[str, set[str]] = {}
    run_by: dict[str, set[str]] = {}
    for caller, procs in sorted(called.items()):
        for proc in sorted(procs):
            for callee in defined.get(proc, []):
                if callee == caller:
                    continue                    # one file, already one fence
                pr.procedure_calls.append({"file": caller, "proc": proc, "runs": callee})
                runs.setdefault(caller, set()).add(callee)
                run_by.setdefault(callee, set()).add(caller)

    fenced: dict[str, set[str]] = {}
    by_file: dict[str, list[Statement]] = {}
    for s in pr.statements:
        by_file.setdefault(s.file, []).append(s)
        if s.target and is_session_scoped(s.target):
            fenced.setdefault(s.file, set()).add(short_name(s.target).upper())

    # Both directions, and the whole way down a chain of calls. A procedure a
    # procedure calls is still the first caller's session; and a temp table
    # built INSIDE a procedure is visible to whatever called it, which is the
    # same pair read the other way round.
    for path, names in fenced.items():
        scope = session_scope(path)
        for other in _reached_through(runs, path) | _reached_through(run_by, path):
            for s in by_file.get(other, ()):
                # A name the SQL qualified is a real table that happens to share
                # a short name, and a name already fenced belongs to its own
                # file. Neither one is this session's temporary table.
                extra = {scope + "." + short_name(x) for x in s.sources
                         if not dataset_of(x) and short_name(x).upper() in names}
                if extra:
                    s.sources |= extra
                    s._sources_upper = None


def _one_entry_per_file(problems: list[dict]) -> list[dict]:
    """Collapse repeated failures in the same file down to one entry.

    A program file can hold several blocks of SQL and fail on more than one of
    them. That is still one file for a person to go and check, so counting it
    twice would overstate "could not read" -- the number this whole tool is
    judged on. The repeats are kept as a count so nothing is hidden.
    """
    merged: dict[str, dict] = {}
    for p in problems:
        key = p.get("file", "")
        if key in merged:
            merged[key]["places"] += 1
        else:
            merged[key] = {**p, "places": 1}
    return list(merged.values())


# ── which table a column came from ─────────────────────────────────────────
# In this warehouse cm13, cm11 and pub_guid are columns in nearly every table,
# so nearly every join has the same name on both sides. Matching on the name
# alone meant a filter on the OTHER table's cm13 was reported as a usage of the
# one being changed -- a finding about the wrong table, in a repository where
# that is the ordinary case rather than an edge one.
#
# The statement usually says which is which, and when it does that is a fact
# about the SQL rather than a guess: "a.cm13" belongs to whatever "a" is. Where
# it does not say, nothing is thrown away -- the usage is kept and marked.


def _sources_of(stmt: Statement) -> dict[str, list[str]]:
    """Every alias and table name this statement reads, and what each can mean.

    A list rather than one name, because a bare ``customer_demographics`` in a
    statement that reads it out of two datasets genuinely does not say which.
    Answering that with whichever one happened to be parsed first is how a
    change to the source table produced findings about the archive copy.
    """
    out: dict[str, list[str]] = {}

    def add(key: str, value: str) -> None:
        bucket = out.setdefault(key.upper(), [])
        if value not in bucket:
            bucket.append(value)

    if stmt.expr is None:
        return out
    for t in stmt.expr.find_all(exp.Table):
        for handed in _tables_handed_to_a_call(t):
            add(short_name(handed), handed)
            if t.alias:
                add(t.alias, handed)
        qualified = _qualify(t)
        if not qualified:
            continue
        add(t.name or short_name(qualified), qualified)
        if t.alias:
            add(t.alias, qualified)
    return out


def _binds_here(sel: exp.Expression) -> dict[str, list[str]]:
    """The names THIS one SELECT binds in its own FROM and JOINs.

    Its own, not its subqueries'. A subquery given an alias binds that alias to
    whatever tables the subquery reads, because ``t.cm13`` written outside
    ``(SELECT * FROM customer_demographics) t`` really is that table's column.
    """
    out: dict[str, list[str]] = {}

    def add(key: str, value: str) -> None:
        bucket = out.setdefault(key.upper(), [])
        if value not in bucket:
            bucket.append(value)

    if not isinstance(sel, exp.Select):
        return out
    for part in [from_of(sel)] + list(sel.args.get("joins") or []):
        node = getattr(part, "this", None) if part is not None else None
        if isinstance(node, exp.Table):
            for handed in _tables_handed_to_a_call(node):
                add(short_name(handed), handed)
                if node.alias:
                    add(node.alias, handed)
            qualified = _qualify(node)
            if qualified:
                add(node.name or short_name(qualified), qualified)
                if node.alias:
                    add(node.alias, qualified)
        elif isinstance(node, exp.Subquery) and node.alias:
            # The alias stands for every table the subquery reads. Where it
            # reads more than one, the SQL has not said which -- and a list is
            # how _belongs_to is told to mark it rather than pick one.
            for inner in node.find_all(exp.Table):
                qualified = _qualify(inner)
                if qualified:
                    add(node.alias, qualified)
    return out


def _scopes_of(stmt: Statement) -> dict[int, dict[str, list[str]]]:
    """One binding map per SELECT in the statement, worked out once and kept."""
    if stmt._scopes is not None:
        return stmt._scopes
    out: dict[int, dict[str, list[str]]] = {}
    if stmt.expr is not None:
        for sel in stmt.expr.find_all(exp.Select):
            out[id(sel)] = _binds_here(sel)
    stmt._scopes = out
    return out


def _resolve_qualifier(col: exp.Column, stmt: Statement,
                       sources: dict[str, list[str]]) -> list[str]:
    """What ``t`` means where THIS ``t.cm13`` is written.

    The same alias means two different things in two scopes more often than it
    looks, and a flat map across the whole statement gets the wrong one::

        SELECT t.k, o.amount
        FROM (SELECT * FROM customer_demographics) t
        JOIN orders o ON o.k = t.k
        WHERE t.cm13 = 'A'
          AND EXISTS (SELECT 1 FROM legacy_dim t WHERE t.k = o.k)

    The inner EXISTS re-binds ``t`` to ``legacy_dim``. Flat, that was the only
    binding of ``t`` the map held -- the outer ``t`` is a subquery alias, which
    is not a table at all -- so the breaking ``WHERE t.cm13`` was ruled out as
    some other table's column and the scan said risk low over a change that
    stops this statement compiling.

    This walks OUT from the column to the nearest SELECT that binds the name,
    which is what SQL itself does. The flat map stays as the fallback: it is
    what answers for a qualifier bound somewhere this cannot see.
    """
    scopes = _scopes_of(stmt)
    node = col.parent
    while node is not None:
        binding = scopes.get(id(node))
        if binding:
            options = binding.get(col.table.upper())
            if options:
                return options
        node = node.parent
    return sources.get(col.table.upper()) or []


def _belongs_to(col: exp.Column, stmt: Statement, table: str,
                sources: dict[str, list[str]], ctes: set[str]) -> str:
    """'yes', 'no' or 'unknown' -- is this column reference `table`'s?"""
    qualifier = col.table
    if not qualifier:
        # Unqualified. If the statement only reads one table it can only have
        # come from there. If it reads several, the SQL has not said.
        return "yes" if len(stmt.sources) <= 1 else "unknown"
    options = _resolve_qualifier(col, stmt, sources)
    if not options:
        return "unknown"                 # an alias from somewhere we cannot see
    if any(short_name(o).upper() in ctes for o in options):
        # It came out of a WITH block, which was itself built from something.
        # That is exactly the chain being followed, so it is not a reason to
        # rule the usage out.
        return "unknown"
    verdicts = {"yes" if same_table(o, table) else "no" for o in options}
    if verdicts == {"yes"}:
        return "yes"
    if verdicts == {"no"}:
        return "no"
    # The name stands for two tables at once and one of them is this one. Kept,
    # and marked -- never silently counted as a fact about either.
    return "unknown"


# ── SELECT *, which carries every column and names none of them ────────────
def _direct_tables(sel: exp.Select) -> list[str]:
    """The tables this SELECT reads in its own FROM and JOINs.

    Its own, not a subquery's: a star in an outer SELECT covers whatever the
    subquery below it hands up, and that subquery has a star check of its own.
    """
    out: list[str] = []
    parts = [from_of(sel)] + list(sel.args.get("joins") or [])
    for part in parts:
        node = getattr(part, "this", None) if part is not None else None
        if isinstance(node, exp.Table):
            qualified = _qualify(node)
            if qualified and qualified not in out:
                out.append(qualified)
    return out


def _is_star(e: exp.Expression) -> bool:
    """``*`` or ``a.*`` -- either way, not a column reference."""
    return isinstance(e, exp.Star) or (isinstance(e, exp.Column)
                                       and isinstance(e.this, exp.Star))


def _star_of(e: exp.Expression) -> exp.Star:
    return e if isinstance(e, exp.Star) else e.this


def _whole_row_aliases(stmt: Statement) -> dict[str, list[str]]:
    """Names that stand for a WHOLE ROW of a table, and which table that is.

    BigQuery lets a query carry a whole row around as one value, and the
    standard dbt-utils ``deduplicate`` macro is written exactly that way::

        SELECT unique_row.* FROM (
          SELECT ARRAY_AGG(original ORDER BY loaded_at DESC LIMIT 1)[OFFSET(0)]
                   AS unique_row
          FROM customer_demographics original
          GROUP BY id)

    ``original`` on its own -- a bare name that is the table's alias rather than
    any column of it -- is the entire row. So ``unique_row.*`` publishes every
    column ``customer_demographics`` has, which is precisely what SELECT * means.

    Ripple's whole honesty guarantee rests on admitting when a table's column
````

## Paste 14 of 25

### ripple/scanner/sqlread.py — piece 4 of 5

Add this to the END of `ripple/scanner/sqlread.py`, straight after what is already there. Do not start a new file. Do not re-type anything above.

````python
    list is not written down, and that admission fired for ``SELECT *`` and for
    ``alias.*`` over a real table, but not for this. A deduplicated staging
    table -- an ordinary thing to find in a dbt repository -- gave a clean "no
    impact" with no warning of any kind.

    Only a BARE reference counts. ``original.loaded_at`` is one column, and
    ``STRUCT(a, b) AS s`` is two named ones; neither is a whole row.
    """
    if stmt.expr is None:
        return {}
    out: dict[str, list[str]] = {}
    for sel in stmt.expr.find_all(exp.Select):
        # What this SELECT's own FROM and JOINs call the tables they read.
        here: dict[str, str] = {}
        parts = [from_of(sel)] + list(sel.args.get("joins") or [])
        for part in parts:
            node = getattr(part, "this", None) if part is not None else None
            if not isinstance(node, exp.Table):
                continue
            qualified = _qualify(node)
            if not qualified:
                continue
            here[(node.alias or node.name or "").upper()] = qualified
        if not here:
            continue
        for e in sel.expressions:
            if not isinstance(e, exp.Alias) or not e.alias:
                continue
            for col in e.find_all(exp.Column):
                if col.table or isinstance(col.this, exp.Star):
                    continue                      # one column, or a star already
                owner = here.get(col.name.upper())
                if owner:
                    bucket = out.setdefault(e.alias.upper(), [])
                    if owner not in bucket:
                        bucket.append(owner)
    return out


def _stars_over(stmt: Statement, table: str, sources: dict[str, list[str]]) -> list[exp.Star]:
    """Every ``SELECT *`` in this statement that covers `table`'s columns."""
    if stmt.expr is None:
        return []
    rows = _whole_row_aliases(stmt)
    found: list[exp.Star] = []
    for sel in stmt.expr.find_all(exp.Select):
        reads = _direct_tables(sel)
        direct = any(same_table(t, table) for t in reads)
        for e in sel.expressions:
            if isinstance(e, exp.Star):
                if direct:
                    found.append(e)                  # SELECT * -- everything
            elif isinstance(e, exp.Column) and isinstance(e.this, exp.Star):
                key = (e.table or "").upper()
                # a.* -- only the table that alias stands for.
                if direct and any(same_table(o, table) for o in sources.get(key, [])):
                    found.append(e.this)
                    continue
                # x.* where x is a whole row of the table, carried as one value.
                # Not gated on this SELECT reading the table: it does not, the
                # subquery under it does, and the scoping is done where the
                # alias is worked out.
                if any(same_table(o, table) for o in rows.get(key, [])):
                    found.append(e.this)
    return found


# ── _TABLE_SUFFIX ──────────────────────────────────────────────────────────
# A wildcard table reads a whole family of date-sharded tables, and the query
# almost always narrows that down on the very next line::
#
#     SELECT cm13 FROM `p.ds.customer_demographics_*`
#     WHERE _TABLE_SUFFIX = '20260101'
#
# Ripple followed the wildcard and never read the line under it, so scanning
# ``customer_demographics_19991231`` -- a shard from 1999 that this query
# provably never touches -- came back `risk medium, prod ['g_published'],
# breaking true, certain true`, with no hedge anywhere. The predicate is on the
# same line as the wildcard, inside the snippet Ripple prints, and the answer
# contradicted it.
#
# Only literals decide anything. A parameter, a date calculation or a variable
# is not something a static reader can evaluate, and guessing at one would trade
# an over-confident finding for a missing one. Those set `certain=False` and the
# finding stays.
#
# Only ANDs. ``_TABLE_SUFFIX = 'x' OR something_else`` reads the other shards
# too, and a NOT turns every comparison below it inside out.
_SUFFIX_COL = "_TABLE_SUFFIX"


def _only_ands_above(node: exp.Expression, stop: exp.Expression) -> bool:
    """Is every branch between here and the WHERE an AND?"""
    cur = node.parent
    while cur is not None and cur is not stop:
        if isinstance(cur, (exp.Or, exp.Not)):
            return False
        cur = cur.parent
    return True


def _shard_suffix(table: str, pattern: str) -> str:
    """The part of a shard's name the wildcard stands for, or ''.

    Empty for the family itself. Somebody who typed ``customer_demographics_*``
    is asking about every shard, so no one suffix can be tested and every
    predicate has to be read as letting some of them through.
    """
    if is_wildcard(table):
        return ""
    prefix = short_name(pattern).upper()
    if not prefix.endswith(_STAR):
        return ""
    prefix = prefix[:-1]
    name = short_name(table)
    if not prefix or not name.upper().startswith(prefix):
        return ""
    suffix = name[len(prefix):]
    return "" if _STAR in suffix else suffix


def suffix_verdict(stmt: Statement, table: str) -> str:
    """"reads", "maybe" or "excluded" -- does this statement touch that shard?

    "reads" also means "nothing here says otherwise", which is the answer for
    every statement that has no _TABLE_SUFFIX in it at all.
    """
    if stmt.expr is None:
        return "reads"
    patterns = [s for s in stmt.sources if is_wildcard(s) and same_table(s, table)]
    if not patterns:
        return "reads"
    suffix = next((s for s in (_shard_suffix(table, p) for p in patterns) if s), "")
    if not suffix:
        return "reads"                      # the family name, not a shard
    verdict = "reads"
    for sel in stmt.expr.find_all(exp.Select):
        where = sel.args.get("where")
        if where is None:
            continue
        for col in where.find_all(exp.Column):
            if col.name.upper() != _SUFFIX_COL:
                continue
            test = col.parent
            if not _only_ands_above(col, where):
                return "maybe"
            hit = _suffix_allows(test, suffix)
            if hit == "excluded":
                return "excluded"
            if hit == "maybe":
                verdict = "maybe"
    return verdict


def _suffix_allows(test: exp.Expression | None, suffix: str) -> str:
    """Does this one comparison let that suffix through?"""
    def literal(node) -> str | None:
        return node.this if isinstance(node, exp.Literal) else None

    if isinstance(test, exp.Between):
        low, high = literal(test.args.get("low")), literal(test.args.get("high"))
        if low is None or high is None:
            return "maybe"
        return "reads" if low <= suffix <= high else "excluded"
    if isinstance(test, exp.In):
        values = [literal(v) for v in test.expressions]
        if not values or any(v is None for v in values):
            return "maybe"
        return "reads" if suffix in values else "excluded"
    if isinstance(test, (exp.EQ, exp.NEQ, exp.GT, exp.GTE, exp.LT, exp.LTE)):
        # Only when the column is on the left; ``'x' = _TABLE_SUFFIX`` is legal
        # and rare, and reading it backwards would exclude the wrong shard.
        if not isinstance(test.this, exp.Column):
            return "maybe"
        value = literal(test.args.get("expression"))
        if value is None:
            return "maybe"
        ok = {
            exp.EQ: suffix == value,
            exp.NEQ: suffix != value,
            exp.GT: suffix > value,
            exp.GTE: suffix >= value,
            exp.LT: suffix < value,
            exp.LTE: suffix <= value,
        }[type(test)]
        return "reads" if ok else "excluded"
    return "maybe"


def _named_in_except(star: exp.Star, column: str) -> bool:
    """``SELECT * EXCEPT(cm13)`` -- the one shape where a star drops a column."""
    for c in star_except(star):
        if getattr(c, "name", "").upper() == column.upper():
            return True
    return False


def star_carries(stmt: Statement, column: str, table: str,
                 sources: dict[str, list[str]] | None = None) -> bool:
    """Does a ``SELECT *`` carry this column of this table out of the statement?

    ``SELECT * FROM customer_demographics`` really does publish every column
    that table has, including the one being traced. The column list is simply
    not written down anywhere a parser can read it.

    Refusing to follow that was the largest hole in Ripple. Forty-four tables in
    the repository this was built for are made this way, so the trail died at
    the first one it met -- and a change that breaks a published table one hop
    later came back as a clean, confident "no impact".
    """
    stars = _stars_over(stmt, table, sources if sources is not None else _sources_of(stmt))
    return any(not _named_in_except(s, column) for s in stars)


def star_excludes(stmt: Statement, column: str, table: str,
                  sources: dict[str, list[str]] | None = None) -> bool:
    """Is the column named in a ``SELECT * EXCEPT(...)`` of this statement?

    Two things at once, and both matter. The column does not reach the table
    this statement builds, so the chain genuinely stops -- and the statement
    names the column out loud, so removing or renaming it makes this statement
    fail on the day of the change.
    """
    stars = _stars_over(stmt, table, sources if sources is not None else _sources_of(stmt))
    return any(_named_in_except(s, column) for s in stars)


# ── working out how a column is used ───────────────────────────────────────
def _cols_named(node: exp.Expression | None, name: str) -> list[exp.Column]:
    """Every reference to this column. A dotted name must match dotted.

    A STRUCT field is carried as ``payload.code``, and that name has to be
    matched against the QUALIFIER too. Matching it on the leaf alone would make
    a plain column called ``code`` on an unrelated table look like the struct's
    field -- which is the invented-column mistake the ordinary-struct guard
    exists to stop.
    """
    if node is None:
        return []
    if "." in name:
        qualifier, _, leaf = name.rpartition(".")
        return [c for c in node.find_all(exp.Column)
                if c.name.upper() == leaf.upper()
                and c.table.upper() == qualifier.upper()]
    return [c for c in node.find_all(exp.Column) if c.name.upper() == name.upper()]


def _literal_beside(node: exp.Expression, col: exp.Column) -> str:
    """If the column is compared to a literal, return it -- that is the detail
    that turns 'used in a filter' into 'compared against US'."""
    parent = col.parent
    while parent is not None and not isinstance(parent, exp.Binary):
        parent = parent.parent
    if isinstance(parent, exp.Binary):
        for side in (parent.left, parent.right):
            if isinstance(side, exp.Literal):
                return side.this
    return ""


# How many names one column may be followed under out of a single statement.
# Real SQL publishes a column under one name, occasionally two or three -- the
# value itself and a cleaned-up copy of it. The cap is here so that a generated
# statement with hundreds of derived columns cannot turn one scan into a search
# of the whole warehouse; it is set far above anything hand-written.
MAX_OUTPUT_NAMES = 6


# How many times a rename may be fed straight into another rename inside ONE
# level before this stops looking. Sibling CTEs in a single WITH are all at the
# same SELECT depth, so a chain of them is resolved here rather than by the
# level loop. Set well above anything hand-written; it only has to terminate.
MAX_CHAINED_RENAMES = 12


def _resolve_level(names: list[str], direct_map: dict, derived_map: dict) -> list[str]:
    """Every name these names become at one level, following renames fed by renames.

    The levels handed to ``output_names`` are grouped by how deeply nested each
    SELECT is, and the CTEs of a single WITH are all at the SAME depth even
    though they feed each other::

        WITH src     AS (SELECT k, cm13 FROM customer_demographics),
             renamed AS (SELECT k, cm13 AS customer_code FROM src),
             final   AS (SELECT k, customer_code AS cust_code FROM renamed)
        SELECT * FROM final

    Applying that level in one pass followed ``cm13`` to ``customer_code`` and
    stopped, because ``customer_code -> cust_code`` was in the very same map and
    the map was only ever read once. The table really does publish ``cust_code``,
    so a change to ``cm13`` reached a published table under a name Ripple never
    said, and the scan came back clean.

    Which CTE feeds which is not knowable from depth, so this does not try to
    put them in order: it runs to a fixpoint instead, which gets the same answer
    whatever order they are written in. The set only grows and every name comes
    from the statement, so it terminates; the counter is a backstop.

    Following a rename that happens to share a name with an unrelated sibling
    can add a name the column never really takes. That is the safe direction:
    a spare row is visible on screen and dismissed by opening the file, while a
    lost chain is invisible and reads as "no impact".
    """
    found: list[str] = []
    frontier = list(names)
    seen = {n.upper() for n in names}
    for _ in range(MAX_CHAINED_RENAMES):
        step: list[str] = []
        for name in frontier:
            step.extend(direct_map.get(name.upper(), ()))
        for name in frontier:
            step.extend(derived_map.get(name.upper(), ()))
        step = _dedupe(step)
        if not step:
            break
        found.extend(step)
        frontier = [s for s in step if s.upper() not in seen]
        if not frontier:
            break
        seen.update(s.upper() for s in frontier)
    return _dedupe(found)


def output_names(stmt: Statement, column: str, limit: int = MAX_OUTPUT_NAMES) -> list[str]:
    """Every name this column is published under once the statement is done.

    Renames often happen inside a subquery -- ``c.last_upd AS lut_ts`` buried in
    a ranking, then simply carried out by the enclosing SELECT. Resolving from
    the innermost query outwards is what keeps the chain joined up; without it
    the trail goes cold at exactly the statements that matter most.

    A column also leaves under more than one name more often than it looks::

        SELECT CAST(cm13 AS STRING) AS cm13_str,
               cm13
        FROM customer_demographics

    Following only the first of those was a silent, expensive mistake. The next
    table along reads ``cm13``, not ``cm13_str``, so the chain stopped one step
    short -- and a change that really does reach a published table was reported
    as no production impact, which is the exact answer this tool exists to stop
    anybody giving.

    The name carried through unchanged is always kept first, so it survives the
    cap: it is the one the rest of the warehouse is most likely to be using.
    """
    if stmt.expr is None:
        return [column]
    # An ALTER has no SELECT to walk. What it does to this column is written on
    # the statement itself: a rename carries it on under the new name, a DROP
    # ends it here, and anything else leaves the name alone.
    action = _alter_actions(stmt.expr).get(column.upper())
    if action is not None:
        kind, new_name = action
        return [] if kind == "dropped" else [new_name or column]
    cached = stmt._names.get(column.upper())
    if cached is not None:
        return cached
    names = [column]
    for direct_map, derived_map, passthrough, dropped in _projections(stmt):
        found = _resolve_level(names, direct_map, derived_map)
        # A star carries the name through untouched -- unless the star names it
        # in an EXCEPT, which is the one shape where a star drops a column.
        # Written beside explicit columns -- SELECT *, CAST(cm13 AS STRING) AS
        # cm13_str -- it leaves under BOTH names, and the untouched one is kept
        # first because it is the one the rest of the warehouse is likeliest to
        # be reading.
        if passthrough:
            kept = [n for n in names if n.upper() not in dropped]
            found = _dedupe(kept + found)
            if not found:
                # Every name was dropped by an EXCEPT. The column really does
                # stop here, and saying so is the point of tracking this at all.
                return []
        # Not projected at this level at all. That is normal -- the column may
        # only be in a WHERE or a JOIN here -- so the name it had carries on
        # rather than the trail being dropped.
        names = found[:limit] if found else names
    names = _through_insert_columns(stmt, names)
    names = _through_create_columns(stmt, names)
    names = _through_merge_columns(stmt, names)
    names = _through_declared_variable(stmt, names)
    stmt._names[column.upper()] = names
    return names


def _through_declared_variable(stmt: Statement, names: list[str]) -> list[str]:
    """A DECLARE publishes ONE thing: the variable, whatever fed it.

    ``DECLARE cutoff DATE DEFAULT (SELECT MAX(cm13) ...)`` has no select list
    the projection walk could read -- MAX(cm13) is named nothing at all -- so
    the column came out still called cm13 and the statement below, which reads
    ``cutoff``, matched nothing.

    A loop's row variable is NOT this shape: it carries a whole row, its column
    names survive, and the walk above already gets them right.
    """
    if not stmt.script_var or not isinstance(stmt.expr, (exp.Declare, exp.Set)):
        return names
    return [stmt.script_var]


def _through_insert_columns(stmt: Statement, names: list[str]) -> list[str]:
    """Rename by position, the way ``INSERT INTO t (a, b) SELECT x, y`` does.

    The load statement at the heart of every foundation file in this pipeline is
    a TRUNCATE followed by an INSERT with the target's whole column list written
    out, and the SELECT under it hands over values by position, not by name. So
    the name the column carries downstream is the one in the INSERT's list -- and
    following the SELECT's name instead walked off the end of the chain.

    Only done when the two lists are plainly the same length and no star is in
    the way. Where the arity cannot be checked, the name is left as it was
    rather than guessed at.
    """
    if not isinstance(stmt.expr, exp.Insert) or stmt.select is None:
        return names
    schema = stmt.expr.this
    if not isinstance(schema, exp.Schema):
        return names
    targets = [c.name for c in schema.expressions if getattr(c, "name", "")]
    if not targets:
        return names
    positions: list[str] = []
    for e in stmt.select.expressions:
        if _is_star(e):
            return names                      # arity unknown; nothing to line up
        positions.append(e.alias if isinstance(e, exp.Alias)
                         else e.name if isinstance(e, exp.Column) else "")
    if len(positions) != len(targets):
        return names
    wanted = {n.upper() for n in names}
    mapped = [targets[i] for i, p in enumerate(positions) if p and p.upper() in wanted]
    return _dedupe(mapped) if mapped else names


def _through_create_columns(stmt: Statement, names: list[str]) -> list[str]:
    """Rename by position, the way ``CREATE VIEW v(a, b) AS SELECT x, y`` does.

    BigQuery lets a view, a materialized view or a CTAS pin its own output
    column names in the CREATE line, and it is the ordinary way a team publishes
    friendly names over cryptic warehouse codes. The list was thrown away, which
    went wrong in both directions at once: the chain stopped at the view, and a
    downstream table reading the OLD name was reported as a confident break --
    when after the rename that name is not a column of the view at all.

    Same care as the INSERT version: only when the two lists are plainly the
    same length and no star is in the way. Where the arity cannot be checked the
    name is left alone rather than guessed at.
    """
    if not isinstance(stmt.expr, exp.Create) or stmt.select is None:
        return names
    schema = stmt.expr.this
    if not isinstance(schema, exp.Schema):
        return names
    targets: list[str] = []
    for c in schema.expressions:
        # A CTAS column list may carry types -- (cid STRING, mkt STRING) -- and
        # a view's does not. Both give the name the same way.
        name = getattr(c, "name", "") or (c.this.name if getattr(c, "this", None) is not None
                                          and hasattr(c.this, "name") else "")
        if not name:
            return names
        targets.append(name)
    if not targets:
        return names
    positions: list[str] = []
    for e in stmt.select.expressions:
        if _is_star(e):
            return names                      # arity unknown; nothing to line up
        positions.append(e.alias if isinstance(e, exp.Alias)
                         else e.name if isinstance(e, exp.Column) else "")
    if len(positions) != len(targets):
        return names
    wanted = {n.upper() for n in names}
    mapped = [targets[i] for i, p in enumerate(positions) if p and p.upper() in wanted]
    return _dedupe(mapped) if mapped else names


def _through_merge_columns(stmt: Statement, names: list[str]) -> list[str]:
    """The names a MERGE writes this column into the published table under.

    ``WHEN MATCHED THEN UPDATE SET t.market = s.cm13`` publishes cm13 as market,
    and ``WHEN NOT MATCHED THEN INSERT (pub_id, market) VALUES (s.pub_id, s.cm13)``
    renames by position exactly as a plain INSERT does. Following the source's
    own name instead walked straight off the end of the chain at the one
    statement that loads the table everybody downstream reads.

    Only done where the two lists are plainly the same length. Where the arity
    cannot be checked the name is left as it was rather than guessed at.
    """
    if not isinstance(stmt.expr, exp.Merge):
        return names
    wanted = {n.upper() for n in names}
    mapped: list[str] = []

    def carries(value: exp.Expression | None) -> bool:
        return value is not None and any(c.name.upper() in wanted
                                         for c in value.find_all(exp.Column))

    for when in merge_whens(stmt.expr):
        then = when.args.get("then")
        if isinstance(then, exp.Update):
            for setter in then.args.get("expressions") or []:
                if isinstance(setter, exp.EQ) and isinstance(setter.this, exp.Column)                         and carries(setter.expression):
                    mapped.append(setter.this.name)
        elif isinstance(then, exp.Insert):
            into = then.this
            values = then.args.get("expression")
            if not isinstance(into, exp.Tuple) or not isinstance(values, exp.Tuple):
                continue
            targets = [c.name for c in into.expressions]
            if len(targets) != len(values.expressions):
                continue
            for target, value in zip(targets, values.expressions):
                if target and carries(value):
                    mapped.append(target)
    return _dedupe(mapped) if mapped else names


# ── PIVOT and UNPIVOT ──────────────────────────────────────────────────────
# Both fold a column away and build differently-named ones out of it, and both
# NAME the column while doing it -- so the statement itself fails on the day the
# column goes. Neither was read at all, and each failed in its own direction.
#
# UNPIVOT was the worse of the two, and the only case in the whole suite that
# hedges DOWNWARDS on a statement that hard-fails::
#
#     CREATE OR REPLACE TABLE s1 AS SELECT * FROM customer_demographics
#     UNPIVOT (val FOR metric IN (cm13, other_col));
#
# read as a plain SELECT *, so the answer was `risk: low`, `breaking: false`,
# and the sentence "Nothing here fails on the day of the change" -- printed
# about a statement whose UNPIVOT list stops being valid SQL.
#
# PIVOT failed the other way: the columns it builds are `total_Q1`, `total_Q2`,
# worked out from the aggregate's alias and each IN value. Nothing derived them,
# so the trail was declared finished one hop early with the note "Last table in
# the chain", and the published table reading `total_Q1` was never named.
#
# Both column lists are facts written in the statement, not guesses. sqlglot
# works the PIVOT output names out itself; where it does not, nothing here
# invents them.
def _pivots_over(sel: exp.Select) -> list[exp.Expression]:
    """Every PIVOT or UNPIVOT applied to what this SELECT reads."""
    out: list[exp.Expression] = []
    holders: list[exp.Expression | None] = []
    frm = from_of(sel)
    if frm is not None:
        holders.append(frm.this)
    for j in sel.args.get("joins") or []:
        holders.append(j.args.get("this"))
    for node in holders:
        if node is not None:
            out.extend(node.args.get("pivots") or [])
    return out


def _pivot_consumes(pivot: exp.Expression) -> set[str]:
    """The columns this PIVOT or UNPIVOT names, upper case.

    Named means the statement stops being valid SQL if one of them goes -- an
    UNPIVOT's IN list and a PIVOT's aggregate and FOR column alike.
    """
    named: set[str] = set()
    for field_node in pivot_fields(pivot):
        for c in field_node.find_all(exp.Column):
            named.add(c.name.upper())
    if not is_unpivot(pivot):
        # PIVOT: the aggregates are over real columns of the table underneath.
        # An UNPIVOT's ``expressions`` are the NEW names it invents, not columns
        # it reads, which is why this only applies one way round.
        for e in pivot.expressions:
            for c in e.find_all(exp.Column):
                named.add(c.name.upper())
    return named


def _pivot_outputs(pivot: exp.Expression) -> list[str]:
    """The columns this PIVOT or UNPIVOT builds, or [] if they cannot be known."""
    if not is_unpivot(pivot):
        return pivot_columns(pivot)
    out: list[str] = []
    # UNPIVOT (val FOR metric IN (...)) -- the values land in ``val`` and the
    # column's own NAME lands in ``metric``. Both are followed: renaming the
    # column changes what is written into the name column just as surely.
    for e in pivot.expressions:
        out.extend(i.name for i in e.find_all(exp.Identifier))
        if not list(e.find_all(exp.Identifier)) and getattr(e, "name", ""):
            out.append(e.name)
    for field_node in pivot_fields(pivot):
        this = field_node.args.get("this") if hasattr(field_node, "args") else None
        if this is not None and getattr(this, "name", ""):
            out.append(this.name)
    return _dedupe([n for n in out if n])


# Where a nested SELECT can sit that is NOT a source of rows for the query
# around it: in the select list, or inside a WHERE, HAVING, QUALIFY, GROUP BY or
# ORDER BY. A SELECT in one of those places is a VALUE -- one number, one list to
# test against -- and the names inside it are its own business.
#
#     SELECT o.k,
#            (SELECT MAX(d.cm13) AS c_alias FROM customer_demographics d
#             WHERE d.k = o.k) AS peak_cm
#     FROM other_source o
#
# Measured before this: the statement's output name for cm13 came back as
# ``c_alias`` -- a name that exists only inside the brackets and appears on no
# table anywhere. The real name is ``peak_cm``, which is what the next table
# reads, so the chain went cold one hop early and reported no production impact.
# The mirror is just as bad: ``WHERE k IN (SELECT cm13 AS c_alias FROM ...)``
# INVENTED a column called c_alias on the table being built.
#
# A subquery in FROM or JOIN, or a CTE, really does hand its columns to the query
# around it, and its renames really do survive. Those are untouched.
_VALUE_POSITIONS = {"expressions", "where", "having", "qualify", "group", "order", "limit"}


# SELECT AS VALUE STRUCT(k AS k, cm13 AS code) FROM customer_demographics
#
# BigQuery's way of writing a table whose columns are named in one place. AS
# VALUE dissolves the wrapper, so the table this builds has columns k and code
# -- there is no column called "struct" and no struct on the table at all.
#
# Measured before this: the select list held ONE expression, a Struct with no
# alias, so the statement published nothing under any name. cm13 was carried on
# under its own name, the next table reads "code", and the chain went cold one
# hop early with a clean "no impact".
def _select_list(sel: exp.Select) -> list[exp.Expression]:
    """The expressions this SELECT publishes, with AS VALUE STRUCT unwrapped."""
    items = sel.expressions
    if str(sel.args.get("kind") or "").upper() != "VALUE" or len(items) != 1:
        return items
    struct = items[0]
    if isinstance(struct, exp.Alias):
        struct = struct.this
    if not isinstance(struct, exp.Struct):
        return items
    # PropertyEQ is "name: value" -- sqlglot's shape for STRUCT(x AS name).
    out: list[exp.Expression] = []
    for field in struct.expressions:
        if isinstance(field, exp.PropertyEQ):
            out.append(exp.alias_(field.expression.copy(), field.this.name))
        elif isinstance(field, (exp.Alias, exp.Column)):
            out.append(field)
    return out or items


# How deep a STRUCT inside a STRUCT is followed. One level covers everything
# hand-written; the cap is only here so a generated nest cannot run away.
MAX_STRUCT_DEPTH = 3


def _struct_fields(node: exp.Expression, under: str,
                   depth: int = 0) -> list[tuple[str, str]]:
    """(column it came from, dotted name it becomes) for a STRUCT built here.

    ``SELECT k, STRUCT(cm13 AS code, seg AS segment) AS payload`` builds ONE
    column called payload, and the table really does have only that column --
    ``SELECT code FROM ...`` downstream is an error, and saying otherwise would
    invent columns that are not there. But ``payload.code`` IS how that field is
    read, and following the struct only under "payload" ended the trail at the
    wrapper. Measured before this: the chain stopped at the struct while
    ``payload.code`` was both selected AND filtered on one hop later, and the
    scan came back with no production table at all.

    So the field is published under its DOTTED name, never its bare one. That is
    the name the next statement actually writes, and it cannot collide with a
    real column called ``code`` on some other table.

    ``SELECT AS VALUE STRUCT`` is the other spelling and is unwrapped earlier,
    in _select_list, because AS VALUE dissolves the wrapper outright. This one
    keeps it, so the field name is carried ALONGSIDE the wrapper's own name
    rather than instead of it -- a statement downstream that reads ``payload``
    whole is still followed.
    """
    out: list[tuple[str, str]] = []
    if not isinstance(node, exp.Struct) or depth >= MAX_STRUCT_DEPTH:
        return out
    for item in node.expressions:
        if isinstance(item, exp.PropertyEQ):        # STRUCT(x AS name)
            made, value = item.this.name, item.expression
        elif isinstance(item, exp.Alias):
            made, value = item.alias, item.this
        elif isinstance(item, exp.Column):          # STRUCT(cm13) -- named after itself
            made, value = item.name, item
        else:
            continue
        if not made:
            continue
        path = f"{under}.{made}"
        for c in value.find_all(exp.Column):
            out.append((c.name.upper(), path))
        out.extend(_struct_fields(value, path, depth + 1))
    return out


def _feeds_its_parent(sel: exp.Select) -> bool:
    """Does this SELECT hand its columns to the query around it?"""
    node = sel
    while node.parent is not None and not isinstance(node.parent, exp.Select):
        # A JOIN has two halves and they are opposite. Its SOURCE really does
        # hand its columns over -- that is what a joined subquery is. Its ON
        # condition is a value, exactly like a WHERE, and the arg_key of the
        # whole join is "joins" either way, so walking straight past this
        # counted the condition as a source.
        #
        #     ... LEFT JOIN ref_bands r
        #           ON r.k = c.k
        #          AND c.cm13 IN (SELECT cm13 AS band_code FROM allowed_bands)
        #
        # Measured before this: the statement's output name for cm13 came back
        # as band_code -- a name that exists only inside that condition and is a
        # column of no table anywhere -- so the next table, which reads plain
        # cm13, was never reached and the scan reported no production impact.
        if node.arg_key == "on" and isinstance(node.parent, exp.Join):
            return False
        node = node.parent
    if node.parent is None:
        return True                            # the statement's own SELECT
    return node.arg_key not in _VALUE_POSITIONS


def _select_depth(sel: exp.Select) -> int:
    """How many SELECTs this one is nested inside."""
    depth = 0
    node = sel.parent
    while node is not None:
        if isinstance(node, exp.Select):
            depth += 1
        node = node.parent
    return depth


# ── the names a UNION publishes its branches under ─────────────────────────
# SQL takes a set operation's output column names from the branch written
# FIRST, and applies them to every other branch BY POSITION. The second branch's
# own names are never published at all::
#
#     SELECT id, other_col AS market FROM legacy_demographics
#     UNION ALL
#     SELECT id, cm13          FROM customer_demographics
#
# builds a table whose columns are ``id`` and ``market``. Nothing downstream can
# read ``cm13`` from it, because there is no such column.
#
# The projection walk groups the two branches together -- they sit side by side,
# at the same depth -- and merged their select lists into one map, so ``cm13``
# came out still called ``cm13``. The next statement reads ``market``, matched
# nothing, and the trail ended at the staging table: `prod []`, no production
# table affected, no gap reported anywhere. Which of the two branches the traced
# column happens to be written in decided whether a real break was found -- and
# a current table UNION'd with an archive one, written in whichever order, is
# how a large part of a staging layer is built.
#
# Only done when the branches are plainly the same width and no star is in the
# way, the same care taken over INSERT and CREATE column lists. Where the arity
# cannot be checked nothing is lined up, because a name put on the wrong column
# is worse than a name not put on at all.
def _union_position_names(stmt: Statement) -> dict[int, list[str]]:
    """For each non-first branch of a set operation: its output names, in order.

    Keyed by ``id()`` of the branch's own node, which is what the projection
    walk has in hand. The first branch is left out -- its own names ARE the
    output names, and it is already read correctly.
    """
    if stmt.expr is None:
        return {}
    out: dict[int, list[str]] = {}
    for node in stmt.expr.find_all(SET_OPERATION):
        branches = set_branches(node)
        if len(branches) < 2:
            continue
        names = query_output_names(node)
        if not names:
            continue
        for branch in branches[1:]:
            # A star carries an unknown number of columns, so no position in
            # this branch can be lined up with a position in the first.
            selects = _select_list(branch) if isinstance(branch, exp.Select) else []
            if not selects or any(_is_star(e) for e in selects):
                continue
            if len(selects) != len(names):
                continue
            out[id(branch)] = list(names)
    return out


def _projections(stmt: Statement) -> list[tuple[dict, dict, bool]]:
    """For each level of SELECT, inner to outer: what each column leaves as.

    Built in one pass over the statement instead of once per column asked about.
    ``direct`` is the column carried through or plainly renamed; ``derived`` is
    the column reshaped into something else; the flag says a ``SELECT *`` is
    carrying every remaining name through untouched.

    Grouped by how deeply nested each SELECT is, which is what makes a UNION
    come out right. The two halves of a union are side by side, not one inside
    the other, and treating the second as if it wrapped the first fed the wrong
    map into the next step -- so a column renamed in the first half of
    ``..._BCA_UNION`` was followed under the second half's name and the chain
    went cold. SQL takes a union's output names from its FIRST branch, and so
    does this: the branches are read in the order they are written.
    """
    if stmt._projected is not None:
        return stmt._projected
    selects = list(stmt.expr.find_all(exp.Select)) if stmt.expr is not None else []
    by_depth: dict[int, list[exp.Select]] = {}
    for sel in selects:
        # A SELECT written as a value rather than as a source of rows never
        # names an output of the statement around it. See _feeds_its_parent.
        if not _feeds_its_parent(sel):
            continue
        by_depth.setdefault(_select_depth(sel), []).append(sel)

````

## Paste 15 of 25

### ripple/scanner/sqlread.py — piece 5 of 5

Add this to the END of `ripple/scanner/sqlread.py`, straight after what is already there. Do not start a new file. Do not re-type anything above.

````python
    # See _union_position_names. Worked out once for the whole statement.
    union_names = _union_position_names(stmt)

    out: list[tuple[dict, dict, bool, set]] = []
    for depth in sorted(by_depth, reverse=True):            # innermost first
        direct: dict[str, list[str]] = {}
        derived: dict[str, list[str]] = {}
        dropped: set[str] = set()
        passthrough = False
        # One vote per star, so that a column is only treated as dropped when
        # EVERY star at this level drops it. See the note below the loop.
        stars = 0
        star_drops: dict[str, int] = {}
        for sel in by_depth[depth]:
            # PIVOT and UNPIVOT happen to what this SELECT reads, before its own
            # select list is applied, and they rename by rule rather than with an
            # AS. Without this the trail ended one hop early on every PIVOT and
            # went on carrying a name that no longer exists on every UNPIVOT.
            for pivot in _pivots_over(sel):
                eaten = _pivot_consumes(pivot)
                built = _pivot_outputs(pivot)
                for name in eaten:
                    dropped.add(name)
                    for made in built:
                        derived.setdefault(name, []).append(made)
            # A branch of a UNION publishes under the FIRST branch's names, by
            # position. See _union_position_names.
            published = union_names.get(id(sel), [])
            for at, e in enumerate(_select_list(sel)):
                if published:
                    # The name this position really leaves under. Its own name
                    # is kept too: it reaches nothing downstream, because no
                    # such column exists on the table -- but keeping it means a
                    # miscounted branch costs a spare row rather than a lost
                    # chain, which is the trade this tool always makes.
                    under = published[at]
                    for c in e.find_all(exp.Column):
                        direct.setdefault(c.name.upper(), []).append(under)
                        if c.table:
                            direct.setdefault(
                                f"{c.table}.{c.name}".upper(), []).append(under)
                if _is_star(e):
                    passthrough = True
                    star = _star_of(e)
                    stars += 1
                    mine: set[str] = set()
                    for c in star_except(star):
                        mine.add(getattr(c, "name", "").upper())
                    # RENAME(cm13 AS cm13_new) and REPLACE(UPPER(cm13) AS cm13)
                    # both change what leaves under which name, so a star is not
                    # always a plain pass-through.
                    for a in star.args.get("rename") or []:
                        if isinstance(a, exp.Alias) and isinstance(a.this, exp.Column):
                            mine.add(a.this.name.upper())
                            direct.setdefault(a.this.name.upper(), []).append(a.alias)
                    for a in star_replace(star):
                        if isinstance(a, exp.Alias):
                            # The output column of that name now holds the
                            # replacement's value, so the ORIGINAL column of
                            # that name reaches nothing past here. Exactly what
                            # EXCEPT does, plus a value put in its place -- and
                            # without this the star went on carrying it.
                            mine.add(a.alias.upper())
                            for c in a.find_all(exp.Column):
                                derived.setdefault(c.name.upper(), []).append(a.alias)
                    for name in mine:
                        star_drops[name] = star_drops.get(name, 0) + 1
                elif isinstance(e, exp.Alias):
                    inner = e.this
                    if isinstance(inner, exp.Column):
                        direct.setdefault(inner.name.upper(), []).append(e.alias)
                        # ``payload.code AS customer_code`` also has to answer
                        # to the dotted name, because that is what a STRUCT
                        # field is carried under. See _struct_fields.
                        if inner.table:
                            direct.setdefault(
                                f"{inner.table}.{inner.name}".upper(), []
                            ).append(e.alias)
                    else:
                        # STRUCT(cm13 AS code) AS payload publishes payload.code,
                        # and the next table reads it as payload.code -- whose
                        # column name is "code". Following only "payload" ended
                        # the trail at the struct. See _struct_fields.
                        for came_from, made in _struct_fields(inner, e.alias):
                            derived.setdefault(came_from, []).append(made)
                        for c in e.find_all(exp.Column):
                            derived.setdefault(c.name.upper(), []).append(e.alias)
                elif isinstance(e, exp.Column):
                    direct.setdefault(e.name.upper(), []).append(e.name)
        # A star only drops a column when EVERY star at this level drops it.
        # The CTEs of one WITH are all at the same depth and usually read
        # DIFFERENT tables::
        #
        #     WITH cust AS (SELECT * FROM customer_demographics),
        #          hits AS (SELECT * EXCEPT (cm13) FROM web_events)
        #     SELECT cust.*, hits.url FROM cust JOIN hits USING (k)
        #
        # That EXCEPT belongs to ``hits``, which never reads the scanned table
        # at all. Applied to the whole level it deleted the column arriving
        # through ``cust.*``, the trail died inside the statement, and a change
        # that really does break the published table came back "no impact".
        # Which star a column flows through is not knowable from the select
        # list alone, so this keeps it whenever any star could still carry it --
        # a spare row rather than a lost chain.
        if stars:
            dropped |= {n for n, votes in star_drops.items() if votes == stars}
        out.append((direct, derived, passthrough, dropped))
    stmt._projected = out
    return out


def _dedupe(names: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for n in names:
        key = n.upper()
        if key not in seen:
            seen.add(key)
            out.append(n)
    return out


def output_name(stmt: Statement, column: str) -> str:
    """The one name to show on screen for this column. See output_names.

    A statement can publish the column under no name at all -- SELECT * EXCEPT
    drops it -- and the row on screen still has to say which column it is about,
    so the name it arrived under is what gets shown.
    """
    names = output_names(stmt, column)
    return names[0] if names else column


def usages_of(stmt: Statement, column: str, table: str = "") -> list[Usage]:
    """Every way `column` is used by this statement, across all its subqueries.

    ``table`` is the table the column is being traced from. Given it, a column
    the statement plainly attributes to some other table is not counted -- which
    matters enormously in a warehouse where the same three key columns are in
    nearly every table and so on both sides of nearly every join. Without a
    table this behaves as it always did and counts every match.
    """
    if stmt.expr is None:
        return []
    # An ALTER names its column outright, in one place, and has no SELECT for
    # the walk below to look in. See _alter_actions.
    action = _alter_actions(stmt.expr).get(column.upper())
    if action is not None:
        kind, new_name = action
        return [Usage(kind=kind, column=column,
                      alias=new_name or column, detail=new_name)]
    found: list[Usage] = []
    alias_for_column = output_name(stmt, column)
    sources = _sources_of(stmt) if table else {}
    ctes = _cte_names(stmt.expr) if table else set()

    # A name Ripple put back by hand because the parser read it as a built-in
    # function. The usage is real; whether the writer meant the column or the
    # function is not knowable from the file, so it is never asserted.
    a_guess = column.upper() in stmt.guessed_columns

    def owned(node: exp.Expression | None) -> tuple[list[exp.Column], bool]:
        """This table's references to the column, and whether the SQL said so."""
        cols = _cols_named(node, column)
        if not table or not cols:
            return cols, not (a_guess and cols)
        keep: list[exp.Column] = []
        certain = True
        for c in cols:
            verdict = _belongs_to(c, stmt, table, sources, ctes)
            if verdict == "no":
                continue                 # plainly another table's column
            if verdict == "unknown":
                certain = False          # kept, and marked rather than asserted
            keep.append(c)
        return keep, certain and not a_guess

    # 0. How the table it builds is laid out: PARTITION BY and CLUSTER BY.
    #
    # These sit on the CREATE line, outside the SELECT, so nothing else in this
    # function could ever see them. Measured before this: a table partitioned by
    # the very column being decommissioned returned NO usages at all, and the
    # whole chain came back `risk low, groups 0, couldNotRead 0`.
    #
    # It is not a column of the table being built -- so no chain follows from it
    # -- but the name is written down on the CREATE line, so the day the column
    # goes this statement stops compiling and the table stops being built. Every
    # published table underneath it then quietly serves data that has stopped
    # being refreshed. That is what "stops being refreshed" exists to report,
    # and this is what feeds it.
    props = stmt.expr.args.get("properties") if isinstance(stmt.expr, exp.Create) else None
    for prop in (props.expressions if props is not None else []):
        which = type(prop).__name__
        if "Partition" not in which and "Cluster" not in which:
            continue
        cols, sure = owned(prop)
        # PARTITION BY cm13 with nothing round it parses as a bare identifier
        # rather than a column, so the search above finds nothing.
        named = bool(cols) or any(i.name.upper() == column.upper()
                                  for i in prop.find_all(exp.Identifier))
        if named:
            found.append(Usage(kind="layout", column=column, alias=alias_for_column,
                               detail="CLUSTER BY" if "Cluster" in which else "PARTITION BY",
                               certain=sure))

    # A DELETE or an UPDATE has a WHERE clause and no SELECT at all. Requiring a
    # SELECT made both invisible, so "DELETE FROM stage WHERE market_code = 'US'"
    # -- which stops working the day market_code goes, and silently stops pruning
    # the table -- was reported as no usage whatsoever.
    if isinstance(stmt.expr, (exp.Delete, exp.Update)):
        cols, sure = owned(stmt.expr.args.get("where"))
        for c in cols:
            found.append(Usage(kind="filter", column=column, alias=alias_for_column,
                               detail=_literal_beside(stmt.expr, c), certain=sure))
        if isinstance(stmt.expr, exp.Update):
            for e in stmt.expr.args.get("expressions") or []:
                cols, sure = owned(e)
                if cols:
                    found.append(Usage(kind="transform", column=column,
                                       alias=alias_for_column, detail="SET", certain=sure))
        if not found:
            cols, sure = owned(stmt.expr)
            if cols:
                found.append(Usage(kind="select", column=column, alias=alias_for_column,
                                   certain=sure))

    # A MERGE is how a published table is normally loaded on BigQuery, Snowflake
    # and Databricks. When USING names a table directly the statement has no
    # SELECT of its own, so every check below was skipped and Ripple answered
    # "the name appears, but no lineage to a production table" -- its single most
    # reassuring sentence, printed about the very statement that loads the table.
    if isinstance(stmt.expr, exp.Merge):
        cols, sure = owned(stmt.expr.args.get("on"))
        if cols:
            found.append(Usage(kind="join_key", column=column, alias=alias_for_column,
                               certain=sure))
        for when in merge_whens(stmt.expr):
            # WHEN MATCHED AND s.cm13 = 'DEAD' THEN DELETE. The condition here
            # decides which rows of a published table get deleted or updated,
            # and it is often the only place in the whole statement the column
            # is named at all.
            cols, sure = owned(when.args.get("condition"))
            for c in cols:
                found.append(Usage(kind="filter", column=column, alias=alias_for_column,
                                   detail=_literal_beside(when, c), certain=sure))
            then = when.args.get("then")
            if isinstance(then, exp.Update):
                # Only the right-hand side. ``SET t.market = s.cm13`` reads
                # s.cm13 and writes t.market, and reading the whole assignment
                # would report the target's own column as a usage of the source.
                for setter in then.args.get("expressions") or []:
                    value = setter.args.get("expression") if isinstance(setter, exp.EQ) else setter
                    cols, sure = owned(value)
                    if cols:
                        found.append(Usage(kind="select", column=column,
                                           alias=alias_for_column, certain=sure))
            elif isinstance(then, exp.Insert):
                cols, sure = owned(then.args.get("expression"))
                if cols:
                    found.append(Usage(kind="select", column=column,
                                       alias=alias_for_column, certain=sure))

    # INSERT ... VALUES has no SELECT anywhere in it, so every check below was
    # skipped and the statement recorded no usage of anything. That is exactly
    # how a FOR loop's body is written -- the values are the loop row's fields --
    # and it is the half of the statement that names the published table::
    #
    #     FOR rec IN (SELECT id, cm13 AS seg FROM customer_demographics) DO
    #       INSERT INTO final_published (id, seg) VALUES (rec.id, rec.seg);
    #
    # Measured before this: groups [], while the finding's own text said the
    # column went "into the next table" and named no next table at all.
    if isinstance(stmt.expr, exp.Insert):
        values = stmt.expr.find(exp.Values)
        if values is not None:
            cols, sure = owned(values)
            if cols:
                found.append(Usage(kind="select", column=column,
                                   alias=alias_for_column, certain=sure))

    if stmt.select is None:
        return _best_of(found)

    for sel in stmt.expr.find_all(exp.Select):
        # 1. the select list
        for e in sel.expressions:
            # A star is not a column reference, and the names hanging off one --
            # EXCEPT(cm13), RENAME(cm13 AS x) -- are not usages of a column in a
            # select list. Reading them as ordinary usages made
            # "SELECT * EXCEPT(cm13)" report cm13 as carried onward, which is
            # the exact opposite of what that statement does with it. The star
            # is handled properly at the bottom of this function.
            if _is_star(e):
                for r in star_replace(_star_of(e)):
                    # REPLACE(UPPER(cm13) AS cm13) genuinely reshapes the value.
                    cols, sure = owned(r)
                    if cols:
                        found.append(Usage(kind="transform", column=column,
                                           alias=alias_for_column, detail="REPLACE",
                                           certain=sure))
                    # SELECT * REPLACE(legacy_code AS cm13) names cm13 out loud.
                    # Remove it and this statement fails, exactly as it does
                    # with EXCEPT -- and the column downstream of that name is
                    # fed by legacy_code from here on, not by this one. Ripple
                    # got the right answer for the wrong reason before: the
                    # rename was followed and nothing said the name was written
                    # down here, so the row read `breaking: false`.
                    if isinstance(r, exp.Alias) and r.alias.upper() == column.upper():
                        found.append(Usage(kind="excluded", column=column,
                                           alias=alias_for_column, detail="REPLACE"))
                continue
            cols, sure = owned(e)
            if not cols:
                continue
            inner = e.this if isinstance(e, exp.Alias) else e
            if isinstance(inner, exp.Column):
                found.append(Usage(kind="select", column=column, alias=alias_for_column,
                                   certain=sure))
            else:
                fn = inner.__class__.__name__.upper() if inner is not None else ""
                found.append(
                    Usage(kind="transform", column=column, alias=alias_for_column,
                          detail=fn, certain=sure)
                )

        # 2. WHERE / HAVING / QUALIFY
        #
        # QUALIFY is BigQuery's and Snowflake's filter on a window result, and
        # it is where nearly every dedup in this kind of pipeline is written:
        # QUALIFY ROW_NUMBER() OVER (PARTITION BY cm13 ORDER BY ts) = 1. Not
        # reading it meant a column that appears nowhere else in the statement
        # was invisible, and the scan came back with no impact at all.
        for clause_key in ("where", "having", "qualify"):
            clause = sel.args.get(clause_key)
            cols, sure = owned(clause)
            for c in cols:
                found.append(
                    Usage(kind="filter", column=column, alias=alias_for_column,
                          detail=_literal_beside(clause, c), certain=sure)
                )

        # 3. JOIN ... ON
        for j in sel.args.get("joins") or []:
            cols, sure = owned(j.args.get("on"))
            if cols:
                found.append(Usage(kind="join_key", column=column, alias=alias_for_column,
                                   certain=sure))

        # 3b. FROM t, UNNEST(cm13) -- an array column opened out into rows.
        # There is no ON clause here, so the join check above sees nothing, and
        # the column is named nowhere else in the statement.
        for j in sel.args.get("joins") or []:
            node = j.args.get("this")
            if isinstance(node, exp.Unnest):
                cols, sure = owned(node)
                if cols:
                    found.append(Usage(kind="transform", column=column,
                                       alias=alias_for_column, detail="UNNEST",
                                       certain=sure))

        # 4. GROUP BY
        cols, sure = owned(sel.args.get("group"))
        if cols:
            found.append(Usage(kind="aggregation", column=column, alias=alias_for_column,
                               certain=sure))

        # 4b. the statement's own ORDER BY. With a LIMIT under it this decides
        # which rows survive, which is the ranking case; without one it decides
        # the order rows are written in. Either way the name is written down, so
        # removing it stops the statement compiling and the table stops loading.
        cols, sure = owned(sel.args.get("order"))
        if cols:
            found.append(Usage(kind="ranking" if sel.args.get("limit") else "sort",
                               column=column, alias=alias_for_column, certain=sure))

        # 4c. PIVOT and UNPIVOT. The column is named in the statement, so the
        # statement stops being valid SQL the day it goes -- and it leaves under
        # names worked out by rule rather than written with an AS. See
        # _pivots_over. Nothing above finds these: an UNPIVOT's IN list is under
        # the FROM clause, not in any select list, WHERE or JOIN.
        for pivot in _pivots_over(sel):
            if column.upper() not in _pivot_consumes(pivot):
                continue
            found.append(Usage(kind="pivoted", column=column, alias=alias_for_column,
                               detail="UNPIVOT" if is_unpivot(pivot) else "PIVOT"))

    # 5. window ORDER BY -- the ranking case, where removal is silent and awful
    for w in stmt.expr.find_all(exp.Window):
        cols, sure = owned(w.args.get("order"))
        if cols:
            found.append(Usage(kind="ranking", column=column, alias=alias_for_column,
                               certain=sure))
        # PARTITION BY is the other half of a dedup and the half that was never
        # read. The ORDER BY picks the winner; the PARTITION BY says what it
        # wins against. Take the column away and every row falls into one group,
        # so one record survives for the whole table instead of one per key --
        # and nothing anywhere is raised to say so.
        for part in w.args.get("partition_by") or []:
            cols, sure = owned(part)
            if cols:
                found.append(Usage(kind="dedup_key", column=column, alias=alias_for_column,
                                   detail="PARTITION BY", certain=sure))
                break

    # 6. aggregates that pick which row survives
    for agg in list(stmt.expr.find_all(exp.Max)) + list(stmt.expr.find_all(exp.Min)):
        cols, sure = owned(agg)
        if cols:
            found.append(
                Usage(kind="dedup_key", column=column, alias=alias_for_column,
                      detail=agg.__class__.__name__.upper(), certain=sure)
            )

    # 7. SELECT * -- last, because anything written down beats anything inferred.
    #
    # Nothing above can see this: there is no column node to find. The column is
    # carried all the same, and refusing to say so is what turned a change that
    # breaks a published table one hop later into a clean result.
    # A column folded away by a PIVOT or an UNPIVOT is not carried on by the
    # star over it. The pivot is definitive about what happens to that one
    # column, and letting the star speak as well would put "carried through
    # untouched" beside "named here, and this statement fails without it".
    pivoted = any(column.upper() in _pivot_consumes(p)
                  for sel in stmt.expr.find_all(exp.Select)
                  for p in _pivots_over(sel))
    # Same for a column the star REPLACEs by name: the output column of that
    # name is fed by the replacement, so this one is not carried through.
    replaced = any(u.kind == "excluded" and u.detail == "REPLACE" for u in found)
    if table and not pivoted and not replaced:
        if star_excludes(stmt, column, table, sources):
            found.append(Usage(kind="excluded", column=column, alias=alias_for_column))
        elif star_carries(stmt, column, table, sources):
            found.append(Usage(kind="star", column=column, alias=alias_for_column,
                               via_star=True))

    return _best_of(found)


def _best_of(found: list[Usage]) -> list[Usage]:
    """The most informative reading of each kind, most consequential first."""
    seen: dict[str, Usage] = {}
    for u in found:
        if u.kind not in seen:
            seen[u.kind] = u
        # One the SQL was explicit about beats one it was not, and after that
        # the one carrying a detail beats the one that does not.
        elif u.certain and not seen[u.kind].certain:
            seen[u.kind] = u
        elif u.certain == seen[u.kind].certain and u.detail and not seen[u.kind].detail:
            seen[u.kind] = u
    return sorted(
        seen.values(),
        key=lambda u: KIND_PRIORITY.index(u.kind) if u.kind in KIND_PRIORITY else 99,
    )


def primary_usage(usages: list[Usage]) -> Usage | None:
    return usages[0] if usages else None


def mode_of(usages: list[Usage]) -> str:
    """How the value itself travels: unchanged, or reshaped on the way."""
    kinds = {u.kind for u in usages}
    if "transform" in kinds or "dedup_key" in kinds or "aggregation" in kinds:
        return "Transformed"
    return "Direct pull"


# ── pointing at the right line of the real file ────────────────────────────
def locate(f: SourceFile, column: str, kind: str, line_offset: int = 0,
           line_end: int | None = None) -> int:
    """Best guess at the 1-based line where this usage lives.

    Bounded to the statement the finding is about. Without the upper bound a
    finding could be sent to any line of the file that scored better -- and in a
    generated file holding sixty statements, the best-scoring WHERE clause is
    very often in somebody else's statement about somebody else's table.
    """
    pat = re.compile(r"\b" + re.escape(column) + r"\b", re.IGNORECASE)
    markers = KIND_MARKERS.get(kind, ())
    last = len(f.lines) if line_end is None else min(line_end + 1, len(f.lines))

    def best_between(low: int, high: int) -> int | None:
        best, best_score = None, -1
        for i in range(max(1, low + 1), min(high, len(f.lines)) + 1):
            line = f.lines[i - 1]
            if not pat.search(line):
                continue
            up = line.upper()
            score = 1 + sum(2 for m in markers if m in up)
            if score > best_score:
                best, best_score = i, score
        return best

    inside = best_between(line_offset, last)
    if inside is not None:
        return inside
    # Nothing inside the statement matched. That happens where the name only
    # exists after a placeholder was filled in, so the statement is widened
    # rather than the finding being dropped -- but only then.
    anywhere = best_between(0, len(f.lines))
    return anywhere or max(1, line_offset + 1)


def snippet(f: SourceFile, hit_line: int, note: str, before: int = 2, after: int = 2) -> list[dict]:
    """A few lines of real code with the important one marked."""
    lines = f.lines
    start = max(1, hit_line - before)
    end = min(len(lines), hit_line + after)
    out = []
    for n in range(start, end + 1):
        row = {"n": n, "t": lines[n - 1].rstrip()}
        if n == hit_line:
            row["hit"] = note
        out.append(row)
    return out
````

## Paste 16 of 25 — 3 files

### ripple/scanner/templating.py

Create the file `ripple/scanner/templating.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Filling in the placeholders that pipeline SQL is written with.

Almost no production SQL is plain SQL. Airflow, dbt and every in-house
generator wrap the parts that change -- the project, the dataset, the run date
-- in ``{{ ... }}`` and push the file through a templating engine before a
database ever sees it. A SQL parser has never met a ``{`` in that position, so
it refuses the file outright, and a repository that is almost entirely readable
is reported as almost entirely unreadable::

    CREATE OR REPLACE TABLE {{tgt_project_id}}.{{stage_dataset}}.web_activity AS
    SELECT ...

Ripple is not the templating engine and cannot know what those values are at
run time. It does not need to. It needs the shape of the statement and the
names in it -- and the table name, ``web_activity``, is sitting right there.

So every placeholder is replaced by an ordinary identifier made out of its own
text. ``{{tgt_project_id}}.{{stage_dataset}}.web_activity`` becomes
``tgt_project_id.stage_dataset.web_activity``, which parses as the three-part
name it always was, and the table still comes out as ``web_activity``.

Two rules this file keeps:

* Line numbers do not move. Every replacement puts back the same number of
  line breaks it swallowed, so a finding still points at the real line of the
  real file, which is the only line anybody can go and look at.
* The original text is never changed. This is done to a copy on the way into
  the parser; everything shown on screen still comes from the file itself.
"""
from __future__ import annotations

import re

# {# a comment #} -- carries nothing, and never should reach the parser.
_COMMENT = re.compile(r"\{#.*?#\}", re.DOTALL)

# {% if ... %} ... {% endif %} -- control flow, not values. The tags go and the
# SQL between them stays. That is right for the common "optional WHERE clause"
# shape; where a file uses if/else to pick between two different statements the
# result will still not parse, and it is reported like any other file that did
# not parse rather than guessed at.
_TAG = re.compile(r"\{%-?.*?-?%\}", re.DOTALL)

# {{ project }} and {{ params.run_date | upper }} -- the usual case by far.
_VAR = re.compile(r"\{\{-?\s*(?P<body>.*?)\s*-?\}\}", re.DOTALL)

# ${project} -- shell, Databricks and older Airflow jobs. sqlglot does not
# refuse these outright; it quietly gives up on the statement and hands back
# something with no tables in it, which is worse, because nothing says so.
_DOLLAR = re.compile(r"\$\{\s*(?P<body>[^{}\n]*?)\s*\}")

# {dataset} -- Python's own .format() and f-strings, which is how a great many
# Airflow DAGs build their SQL. Deliberately narrow: the body has to look like
# a name, so a regular expression's {3} or {2,4} inside a string literal is
# left alone.
_BRACE = re.compile(r"\{(?P<body>[A-Za-z_][A-Za-z0-9_.\[\]'\"]{0,60})\}")

# dbt names a real table inside the placeholder: ref('orders') is the orders
# model. Taking that name is not a guess -- it is the whole point of ref().
_DBT = re.compile(r"^\s*(?:ref|source)\s*\(", re.IGNORECASE)
_QUOTED = re.compile(r"""['"]([A-Za-z_][A-Za-z0-9_]*)['"]""")

# {{ config(materialized='table') }} -- and its siblings. These are instructions
# to dbt, not values. Every dbt model in the world opens with one, and turning it
# into a bare identifier puts a word where SQL expects a keyword, so the WHOLE
# FILE stops parsing: not one table, not one column, nothing. Measured: adding a
# config header to a readable dbt model took it from a full chain to 100%
# unreadable. They carry nothing, so they leave nothing behind.
_DBT_DIRECTIVE = re.compile(
    r"^\s*(?:config|set|test|macro|endmacro|snapshot|endsnapshot|do|print|log)\s*\(",
    re.IGNORECASE,
)

_ANY = (_COMMENT, _TAG, _VAR, _DOLLAR, _BRACE)


def has_placeholders(text: str) -> bool:
    """Is there any templating in here at all?"""
    return any(p.search(text) for p in _ANY)


def describe(text: str) -> str:
    """What kind of templating this is, in words, or '' if there is none.

    Used to explain a file that still could not be read, so the answer on
    screen is "this file is a template" rather than a parser's exception name.
    """
    found: list[str] = []
    if _COMMENT.search(text) or _TAG.search(text) or _VAR.search(text):
        found.append("{{ ... }} templating (Airflow, dbt or similar)")
    if _DOLLAR.search(text):
        found.append("${ ... } placeholders")
    if _BRACE.search(text):
        found.append("{ ... } placeholders filled in by Python")
    return " and ".join(found)


def _identifier(body: str) -> str:
    """A plain SQL identifier standing in for one placeholder."""
    body = body.strip()
    if _DBT_DIRECTIVE.match(body):
        return ""                     # {{ config(...) }} -- an instruction, not a name
    if _DBT.match(body):
        names = _QUOTED.findall(body)
        if names:
            return names[-1]          # source('raw', 'orders') -> orders
    body = body.split("|")[0]         # drop Jinja filters: {{ x | upper }}
    name = re.sub(r"[^A-Za-z0-9_]+", "_", body).strip("_")
    if not name:
        name = "placeholder"
    if name[0].isdigit():
        name = "p_" + name
    return name[:60]


def _keep_lines(text: str) -> str:
    return "\n" * text.count("\n")


def _blank(m: "re.Match[str]") -> str:
    return _keep_lines(m.group(0))


def _named(m: "re.Match[str]") -> str:
    return _identifier(m.group("body")) + _keep_lines(m.group(0))


def placeholder_names(text: str) -> set[str]:
    """The identifiers ``fill_placeholders`` would put in, upper case.

    A placeholder is not a name. It is a hole where a name goes, and nothing in
    the file says what fills it. One file writes a table as
    ``{{tgt_project_id}}.{{stage_dataset}}.card_guid_umdl`` and the DAG that
    reads it writes ``{{ params.src }}.raw.card_guid_umdl`` -- "stage_dataset"
    and "raw" are not two datasets, one of them is a hole.

    Knowing which words came out of a hole is what stops Ripple deciding that
    two names are two different tables on the strength of the placeholder
    somebody happened to type. Getting that wrong cuts a real chain in half and
    reports no impact, which is the one answer this tool exists to prevent.
    """
    out: set[str] = set()
    for pattern in (_VAR, _DOLLAR, _BRACE):
        for m in pattern.finditer(text):
            name = _identifier(m.group("body"))
            if name:
                out.add(name.upper())
    return out


def fill_placeholders(text: str) -> str:
    """The same SQL with every placeholder replaced by a name that parses."""
    out = _COMMENT.sub(_blank, text)
    out = _TAG.sub(_blank, out)
    out = _VAR.sub(_named, out)
    out = _DOLLAR.sub(_named, out)
    return _BRACE.sub(_named, out)


# ── scripting blocks ───────────────────────────────────────────────────────
# Every file in a real BigQuery pipeline is wrapped in DECLARE ... BEGIN ...
# END, often with a FOR loop or an IF inside it. A SQL parser does not know
# those keywords, hands back "BEGIN" as something it cannot read -- and, because
# BEGIN has no semicolon of its own, swallows the statement that follows it.
#
# That is the quietest possible failure: the file parses, the reader reports no
# problem, and the FIRST REAL STATEMENT OF EVERY FILE has vanished. In a
# repository where every file opens with BEGIN, that is most of the lineage.
#
# These keywords carry no lineage themselves, so they are replaced with an empty
# statement, on the copy going into the parser, keeping every line where it was.
#
# Two of them are only scripting some of the time, which is why this is a scan
# and not a line-by-line regular expression. ``ELSE`` and a bare ``END`` are also
# how an ordinary CASE expression is written across several lines::
#
#     CASE WHEN status = 'A' THEN 'Active'
#     ELSE
#       'Unknown'
#     END AS status_desc
#
# Cutting those two lines out puts a semicolon in the middle of a CASE, which
# breaks the statement they sit in -- a 600-line CREATE TABLE thrown away whole,
# with every table and column in it. So CASE is counted as the file is walked,
# and those two words are only treated as scripting when no CASE is open.
_ALWAYS_SCRIPTING = re.compile(
    r"""^\s*(?:
          BEGIN(?:\s+TRANSACTION)?
        | END\s+(?:IF|FOR|WHILE|LOOP)
        | (?:COMMIT|ROLLBACK)(?:\s+TRANSACTION)?
        | EXCEPTION\s+WHEN\s+.+?\s+THEN
        | LOOP
        | (?:LEAVE|ITERATE|BREAK|CONTINUE)\b.*
      )\s*;?\s*$""",
    re.IGNORECASE | re.VERBOSE,
)
# Scripting only while no CASE is open. See the note above.
_SCRIPTING_UNLESS_CASE = re.compile(
    r"""^\s*(?:
          END
        | ELSE
        | (?:ELSE\s*)?IF\b.*?\bTHEN
      )\s*;?\s*$""",
    re.IGNORECASE | re.VERBOSE,
)

# RAISE USING MESSAGE = @@error.message
#
# The last line of the exception handler every generated file in a BigQuery
# pipeline ends with, and by a distance the commonest thing a parser refuses. It
# re-throws an error; it reads no table and touches no column, so it is nothing
# to a scan -- but one of them is enough to put the file on the "check by hand"
# list, and a list padded with hundreds of files nobody needs to check is a list
# nobody reads. It can run past the end of its line, so it is consumed up to its
# semicolon rather than matched a line at a time.
_RAISE = re.compile(r"^\s*RAISE\b", re.IGNORECASE)

# CREATE OR REPLACE PROCEDURE `prj.foundation.refresh`(IN tbl STRING, ...)
#
# The signature, which no SQL parser reads, wrapped around a BEGIN ... END body
# that is ordinary SQL. Dropping the signature is what lets the body be read.
_PROCEDURE = re.compile(
    r"^\s*CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\b", re.IGNORECASE
)

# BEGIN followed by the body on the SAME line, which _ALWAYS_SCRIPTING cannot
# match because it wants BEGIN alone. TRANSACTION is left to that one -- it
# opens a transaction rather than a block, and has no body to keep.
_INLINE_BEGIN = re.compile(r"^\s*BEGIN[ \t]+(?!TRANSACTION\b)(?=\S)", re.IGNORECASE)

# A loop header names a real table. Keeping the query inside it costs one line
# and is the difference between seeing that table read and not. The header is
# often written across several lines, with the DO on its own, so it is gathered
# rather than matched.
_LOOP_HEADER = re.compile(
    r"^\s*(?:FOR\s+(?P<var>\w+)\s+IN|WHILE)\s*(?P<q>\(.*\))\s*(?:DO|LOOP)\s*$",
    re.IGNORECASE)
_LOOP_START = re.compile(r"^\s*(?:FOR\s+\w+\s+IN|WHILE)\b", re.IGNORECASE)
_LOOP_PLAIN = re.compile(r"^\s*(?:FOR|WHILE)\b.*\b(?:DO|LOOP)\s*$", re.IGNORECASE)
_LOOP_END = re.compile(r"\b(?:DO|LOOP)\s*$", re.IGNORECASE)

# A whole loop written on ONE line:
#     FOR rec IN (SELECT tbl FROM cfg_tables) DO SELECT 1; END FOR;
# _LOOP_START matches it and _LOOP_END does not (the line ends with END FOR, not
# with DO), so it used to go to _gather_loop -- which then looked for a line
# ending in DO, never found one, and gave back "everything to the end of the
# file". Measured: every line after it became an empty statement, silently. No
# parse error, no unreadable entry, nothing on any screen: the trail simply
# stopped one table short and reported that as where the chain ends.
_ONE_LINE_LOOP = re.compile(
    r"^(?P<lead>\s*)(?:FOR\s+(?P<var>\w+)\s+IN|WHILE)\s*(?P<q>\(.*\))\s*(?:DO|LOOP)\b"
    r"(?P<body>.*?)(?:\bEND\s+(?:FOR|WHILE|LOOP)\s*;?\s*)?$",
    re.IGNORECASE,
)


# FOR rec IN (SELECT id, cm13 AS seg FROM customer_demographics) DO
#   INSERT INTO final_published (id, seg) VALUES (rec.id, rec.seg);
# END FOR;
#
# The header was rewritten to a read with no target, and the INSERT in the body
# has no source of its own, so the two halves of ONE statement never joined up.
# Measured: groups [], over a loop that really does load the published table --
# and the finding's own text said "into the next table" while naming no next
# table at all.
#
# The loop variable is what joins them, so the header keeps it: the rows the
# loop walks are a thing with a name, exactly like a temporary table, and the
# name is written on the very line the row points at. Fenced to this file by
# _scope_session_tables, the same as any other temporary. WHILE has no variable
# and is left as the plain read it always was.
def _loop_read(var: str | None, query: str) -> str:
    if not var:
        return f"SELECT * FROM {query};"
    return f"CREATE TEMP TABLE {var} AS SELECT * FROM {query};"

# The condition of an IF or a WHILE, when it is a query.
#
#     IF (SELECT MAX(cm13) FROM customer_demographics) IS NOT NULL THEN
#
# That line READS the table, and the whole header was being replaced with an
# empty statement -- so the read went with it and the file came back with
# nothing at all: risk none, no findings, no gap reported. Written as an ASSERT
# instead, the identical guard is read correctly, which is how this was found.
# The condition is a scalar expression rather than a table, but a subquery in a
# FROM is exactly what it is: one read of one table, building nothing.
_HAS_SELECT = re.compile(r"\bSELECT\b", re.IGNORECASE)


def _condition_query(line: str) -> str:
    """The first bracketed group in this line that holds a SELECT, or ""."""
    if not _HAS_SELECT.search(line):
        return ""
    depth = 0
    start = -1
    quote = ""
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = ""
            continue
        if ch in "'\"`":
            quote = ch
        elif ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and start >= 0:
                group = line[start:i + 1]
                if _HAS_SELECT.search(group):
                    return group
                start = -1
            depth = max(0, depth)
    return ""


def _kept_read(line: str) -> str:
    """A scripting line replaced by the read it contains, or by nothing."""
    group = _condition_query(line)
    return f"SELECT * FROM {group};" if group else ";"


_CASE_OR_END = re.compile(r"\b(CASE|END)\b", re.IGNORECASE)
# Nothing to hide a keyword behind, so the line can be read as it stands.
_NEEDS_STRIPPING = re.compile(r"""['"`]|--|/\*|\#""")


def _code_only(line: str, state: dict) -> str:
    """The line with string literals and comments blanked out.

    A keyword inside a quoted string is not scripting, and a 600-line statement
    is exactly where a stray ``'... END ...'`` turns up. ``state`` carries what
    is still open when the line ends, because both can run across lines.
    """
    if not state["quote"] and not state["comment"] and not _NEEDS_STRIPPING.search(line):
        return line
    out: list[str] = []
    i, n = 0, len(line)
    while i < n:
        ch = line[i]
        if state["comment"]:
            if line.startswith("*/", i):
                state["comment"] = False
                out.append("  ")
                i += 2
            else:
                out.append(" ")
                i += 1
        elif state["quote"]:
            q = state["quote"]
            if ch == "\\" and q != "`":
                out.append("  ")
                i += 2
            elif line.startswith(q, i):
                state["quote"] = ""
                out.append(" " * len(q))
                i += len(q)
            else:
                out.append(" ")
                i += 1
        elif line.startswith("/*", i):
            state["comment"] = True
            out.append("  ")
            i += 2
        elif line.startswith("--", i) or ch == "#":
            out.append(" " * (n - i))
            i = n
        elif line.startswith('"""', i) or line.startswith("'''", i):
            state["quote"] = line[i : i + 3]
            out.append("   ")
            i += 3
        elif ch in "'\"`":
            state["quote"] = ch
            out.append(" ")
            i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _case_depth_after(code: str, depth: int) -> int:
    """How many CASE expressions are still open once this line has been read."""
    for m in _CASE_OR_END.finditer(code):
        if m.group(1).upper() == "CASE":
            depth += 1
        elif depth > 0:
            depth -= 1
    return depth


def unwrap_blocks(text: str) -> str:
    """The same SQL with scripting keywords replaced by empty statements.

    Returns the text unchanged when there is no scripting in it, so callers can
    hand everything to this rather than asking ``has_blocks`` first. Asking
    first meant walking every line of every file twice, which on a repository of
    a few thousand files is minutes rather than seconds.
    """
    lines = text.splitlines()
    state = {"quote": "", "comment": False}
    out: list[str] = []
    depth = 0          # CASE expressions currently open
    skip_until = -1    # index of the last line of a multi-line thing being dropped
    changed = False

    for n, line in enumerate(lines):
        code = _code_only(line, state)
        if n <= skip_until:
            out.append(";")
            changed = True
            continue

        # A RAISE, or a procedure signature: neither is readable, both can run
        # past the end of their line, and neither carries a table or a column.
        if depth == 0 and (_RAISE.match(code) or _PROCEDURE.match(code)):
            skip_until = _end_of_run(lines, n, state.copy(),
                                     signature=bool(_PROCEDURE.match(code)))
            out.append(";")
            changed = True
            continue

        if _LOOP_HEADER.match(code):
            # Detected on the blanked copy so a keyword in a string cannot
            # trigger it, but read back off the line as written -- the table
            # being looped over is normally a quoted name, and the blanked copy
            # no longer has it.
            loop = _LOOP_HEADER.match(line) or _LOOP_HEADER.match(code)
            out.append(_loop_read(loop.group("var"), loop.group("q")))
            changed = True
            continue
        if _LOOP_START.match(code) and not _LOOP_END.search(code):
            # A whole loop on one line first: it looks like a header that has
            # not finished, and treating it as one swallowed the rest of the
            # file. See _ONE_LINE_LOOP.
            whole = _ONE_LINE_LOOP.match(line) or _ONE_LINE_LOOP.match(code)
            if whole is not None:
                out.append(f"{whole.group('lead')}"
                           f"{_loop_read(whole.group('var'), whole.group('q'))} "
                           f"{whole.group('body').strip()}")
                changed = True
                continue
            body, skip_until = _gather_loop(lines, n, state.copy())
            out.append(body)
            changed = True
            continue
        if _ALWAYS_SCRIPTING.match(code):
            out.append(";")
            changed = True
            continue
        # BEGIN with the first statement of the body on the SAME line. The
        # check above wants BEGIN alone on its line, which is how a procedure
        # is normally written -- but written on one line the whole body went to
        # the parser as part of the BEGIN and came back as a single Command
        # nobody could read. Measured: a procedure whose body loads a published
        # table produced NO statement at all, so the table it builds was known
        # to Ripple nowhere, and the scan reported no lineage to production.
        # The keyword is swapped for a statement end, so the body behind it is
        # read and the line numbers stay exactly as they are in the file.
        inline = _INLINE_BEGIN.match(code)
        if inline:
            out.append(";" + line[inline.end():])
            depth = _case_depth_after(code[inline.end():], depth)
            changed = True
            continue
        # A WHILE or an IF header. Whatever it tests is a READ, and replacing
        # the line outright threw it away -- see _condition_query.
        if _LOOP_PLAIN.match(code):
            out.append(_kept_read(line))
            changed = True
            continue
        if _SCRIPTING_UNLESS_CASE.match(code) and depth == 0:
            out.append(_kept_read(line))
            changed = True
            continue

        out.append(line)
        depth = _case_depth_after(code, depth)

    if not changed:
        return text
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def _end_of_run(lines: list[str], start: int, state: dict, signature: bool) -> int:
    """The last line of a statement that has to be dropped whole.

    A RAISE ends at its semicolon. A procedure signature ends when its brackets
    close, or at the BEGIN that starts its body -- and the body is left alone,
    because the body is the SQL worth reading.
    """
    brackets = 0
    opened = False
    for n in range(start, len(lines)):
        code = _code_only(lines[n], state)
        if signature:
            if opened and brackets == 0 and n > start:
                return n - 1
            for ch in code:
                if ch == "(":
                    brackets += 1
                    opened = True
                elif ch == ")":
                    brackets = max(0, brackets - 1)
            if _ALWAYS_SCRIPTING.match(code):
                return n - 1
            if opened and brackets == 0:
                return n
        elif ";" in code:
            return n
    return len(lines) - 1


def _gather_loop(lines: list[str], start: int, state: dict) -> tuple[str, int]:
    """A loop header written across lines, as one statement naming its table.

    Built from the lines as written, not from the copy with the strings blanked
    out -- the table being looped over is usually a quoted name, and blanking it
    would leave a query with nothing in it.
    """
    parts: list[str] = []
    for n in range(start, len(lines)):
        code = _code_only(lines[n], state)
        parts.append(lines[n])
        if _LOOP_END.search(code):
            joined = " ".join(parts)
            open_at = joined.find("(")
            close_at = joined.rfind(")")
            if open_at >= 0 and close_at > open_at:
                return "SELECT * FROM " + joined[open_at : close_at + 1] + ";", n
            return ";", n
    # No line finished the header. Give up on THIS LINE ONLY. Returning the end
    # of the file blanked every statement after it -- silently, with no parse
    # error and nothing on any screen, so a trail stopped one table short and
    # that was reported as where the chain ends.
    return _kept_read(lines[start]), start


def has_blocks(text: str) -> bool:
    state = {"quote": "", "comment": False}
    for line in text.splitlines():
        code = _code_only(line, state)
        if (_ALWAYS_SCRIPTING.match(code) or _SCRIPTING_UNLESS_CASE.match(code)
                or _LOOP_PLAIN.match(code) or _LOOP_START.match(code)
                or _RAISE.match(code) or _PROCEDURE.match(code)):
            return True
    return False


# ── templates that are more than holes ─────────────────────────────────────
# Everything above treats templating as holes with names in them. Real pipeline
# SQL uses it as a small programming language as well, and those shapes do not
# survive having their tags blanked and their bodies kept:
#
#     {% if backfill %} ... {% else %} ... {% endif %}   both branches, run on
#     {% set clause %} ... {% endset %}                  a value, left inside
#                                                         the statement
#     {{ header }} on a line of its own                  a whole block of SQL,
#                                                         turned into a bare word
#                                                         welded to the line below
#
# Measured on a real BigQuery warehouse of 7,304 files: 329 of its 2,320 .sql
# files are templated, and 176 of those did not parse at all. Every one landed
# on the "check by hand" list -- which is honest, but it is 176 files of a real
# warehouse whose tables and columns are in NO answer Ripple gives. Rendering
# them the way below reads 119 of the 176.
#
# These renderings are only ever tried on a file that did NOT parse as it
# stands. They cannot take a file that reads today and make it read differently,
# which matters more than the extra files: the first rule of this tool is that
# it does not quietly change an answer that was right.
_JINJA_TAG = re.compile(r"\{%-?\s*(?P<kw>\w+)\b(?P<args>.*?)-?%\}", re.DOTALL)

# A placeholder with nothing else on its line. In a generated warehouse this is
# how a whole block of SQL is dropped in -- a header, a shared set of CTEs, a
# UDF. Replaced by a bare identifier it becomes a word sitting on its own line
# in front of the next statement, which no parser will take. Blanking it loses
# nothing a name lookup would have found, because it never was one name.
#
# NOT done on the first pass. A table name written on its own line under a FROM
# is exactly this shape too, and blanking that would lose a real source table
# without a word said. Only a file that has already failed to parse gets this.
#
# The trailing class has to allow \r. A repository cloned on Windows has CRLF
# line endings, Python's ``$`` in MULTILINE matches before the \n and the \r is
# still sitting there -- so this matched on a Linux checkout of a file and not
# on a Windows one. The same file, the same SQL, a different answer depending on
# which machine ran the scan, and nothing anywhere saying so.
_STANDALONE_VAR = re.compile(r"^[ \t]*\{\{-?[^}]*?-?\}\}[ \t\r]*$", re.MULTILINE)

# Blocks whose body is a value or a definition, never part of the statement
# around them. A {% set x %}...{% endset %} holds a clause that is used
# somewhere else through {{ x }}; leaving its body where it is written puts a
# WHERE in the middle of a WITH.
_VALUE_BLOCKS = {"set", "macro", "raw", "filter"}
_TRANSPARENT_BLOCKS = {"call", "block"}


def _emitting(stack: list) -> bool:
    return all(on for _, on in stack)


def _render_branches(text: str, take: bool) -> str:
    """One rendering of a template's control flow. Line numbers do not move.

    ``take`` decides which side of every ``{% if %}`` is kept: True keeps the
    if-branch and drops the else, False the other way round. Both are rendered
    and both are tried, because nothing in the file says which way it runs and
    guessing one would be a chain lost on the files that guessed wrong.
    """
    out: list[str] = []
    at = 0
    stack: list[tuple[str, bool]] = []
    for m in _JINJA_TAG.finditer(text):
        kw = m.group("kw").lower()
        chunk = text[at:m.start()]
        out.append(chunk if _emitting(stack) else _keep_lines(chunk))
        at = m.end()
        out.append(_keep_lines(m.group(0)))       # the tag itself carries nothing
        if kw == "if":
            stack.append(("if", take))
        elif kw == "elif":
            if stack and stack[-1][0] == "if":
                stack[-1] = ("if", take)
        elif kw == "else":
            if stack and stack[-1][0] == "if":
                stack[-1] = ("if", not take)
        elif kw == "endif":
            if stack and stack[-1][0] == "if":
                stack.pop()
        elif kw in _VALUE_BLOCKS:
            # "{% set x = 1 %}" assigns and opens nothing; only the block form,
            # which has no "=", has a body to leave out.
            if kw != "set" or "=" not in m.group("args"):
                stack.append((kw, False))
        elif kw in _TRANSPARENT_BLOCKS:
            stack.append((kw, True))
        elif kw.startswith("end") and stack and stack[-1][0] == kw[3:]:
            stack.pop()
        # for / endfor: the body is kept once, which is what it was before.
    tail = text[at:]
    out.append(tail if _emitting(stack) else _keep_lines(tail))
    return "".join(out)


def has_control_flow(text: str) -> bool:
    """Is there templating here that is more than a hole with a name in it?"""
    for m in _JINJA_TAG.finditer(text):
        kw = m.group("kw").lower()
        if kw in ("if", "elif", "else", "endif", "for", "endfor") or kw in _VALUE_BLOCKS:
            return True
    return bool(_STANDALONE_VAR.search(text))


def renderings(text: str) -> list[str]:
    """Ways to read a template that did not parse as it stands, best first.

    Given back as raw template text with the control flow resolved -- the caller
    still puts it through ``fill_placeholders`` and ``unwrap_blocks``, exactly
    as it does the original, so a rendering can never take a path the ordinary
    one does not.

    Every one keeps the file's line count, so a finding still points at the real
    line of the real file. That is not a nicety: the whole use of this list is
    that somebody opens the file and looks.
    """
    if not has_control_flow(text):
        return []
    out: list[str] = []
    for take in (True, False):
        rendered = _render_branches(text, take)
        if rendered != text:
            out.append(rendered)
        # A placeholder standing alone on its line is a block of SQL, not a
        # name. Tried last, because on a file that parses without it this would
        # throw a real table name away. See _STANDALONE_VAR.
        out.append(_STANDALONE_VAR.sub(lambda m: "", rendered))
    seen: set[str] = set()
    return [r for r in out if not (r in seen or seen.add(r)) and r != text]
````

### ripple_offline/folderpick.py

Create the file `ripple_offline/folderpick.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""This machine's own "choose a folder" window.

A browser cannot hand a web page the real path of a folder — that is a security
rule, not an oversight — and a real path is exactly what the scanner needs. But
Ripple Offline is not really a website: it is a program running on the same
machine as the browser looking at it. So the window it opens is this machine's
own folder picker, and the path comes back the normal way.

Typing or pasting a path always works and is never taken away. This only saves
the typing, and when there is no picker to open the screen does not offer the
button at all — a button that does nothing is worse than no button.
"""
from __future__ import annotations


def available() -> bool:
    """Can this machine open a folder picker at all?"""
    try:
        import tkinter                       # noqa: F401
        from tkinter import filedialog       # noqa: F401
    except Exception:
        return False
    return True


def choose_folder(title: str = "Choose the repository folder to scan") -> str:
    """Open the picker and return what was chosen, or "" if it was cancelled."""
    try:
        import tkinter
        from tkinter import filedialog
    except Exception:
        return ""
    root = None
    try:
        root = tkinter.Tk()
        root.withdraw()
        # Otherwise the window opens behind the browser and looks like a hang.
        root.attributes("-topmost", True)
        root.update()
        chosen = filedialog.askdirectory(title=title, mustexist=True, parent=root)
        return str(chosen or "")
    except Exception:
        # A machine with no desktop session, or a locked-down one. Typing the
        # path still works, so this is a shrug rather than a failure.
        return ""
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
````

### ripple_offline/lifecycle.py

Create the file `ripple_offline/lifecycle.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Stopping the program when nobody is looking at it any more.

The built program opens without a console window, on purpose: a black box
sitting beside the browser looks like something went wrong. The cost of that is
there is no Ctrl-C and no window to close. Closing the browser tab does nothing
at all -- the server goes on running, invisible, holding its own folder open. So
the folder cannot be deleted, the port stays taken, a second copy starts on a
different port, and the only way out is Task Manager, which nobody should need
to know about to close a program.

This module is the way out. The page says "still here" every few seconds; when
it stops saying so, Ripple stops. There is also a button that stops it now.

Two things this has to get right, because both are ways to lose somebody's work:

* A refresh, or moving between screens, briefly has no page. That is why a page
  saying goodbye only shortens the deadline rather than stopping immediately --
  the new page arrives well inside that window and cancels it.
* A tab left open in the background is still somebody using Ripple. Browsers
  throttle timers in hidden tabs to about one a minute, so the quiet limit is
  minutes rather than seconds.

Everything here is decided by ``verdict()``, which is given the time rather than
reading the clock, so the whole of it can be tested without waiting.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Any

# How often the page says it is still there. Also in web/offline.js -- if these
# two ever disagree, the smaller one is the one that matters.
BEAT_SECONDS = 10

# No word from any page for this long, so nobody is looking. Generous on
# purpose: a hidden tab may only manage one beat a minute.
QUIET_LIMIT = 300.0

# A page said it was going. Long enough for a refresh or a new tab to arrive
# and cancel it, short enough that closing the browser really does close Ripple.
LEAVING_GRACE = 12.0

# Nothing has ever said hello. The browser may still be starting, or may have
# failed to open at all -- and in that second case a program nobody can see is
# exactly what should not be left running.
STARTUP_GRACE = 600.0

_lock = threading.Lock()
_state: dict[str, Any] = {
    "server": None,      # the uvicorn Server, once it exists
    "started": None,     # when the watch began
    "last_beat": None,   # when a page last said it was there
    "leaving_at": None,  # when a page said it was going
    "stopping": False,   # a decision has been taken; do not take it twice
}


def reset(now: float | None = None) -> None:
    """Start again from nothing. Used at startup, and by the tests."""
    with _lock:
        _state.update({"server": None, "started": now if now is not None else time.time(),
                       "last_beat": None, "leaving_at": None, "stopping": False})


def attach(server: Any) -> None:
    """Remember the running server, so it can be asked to stop politely."""
    with _lock:
        _state["server"] = server


def beat(now: float | None = None) -> None:
    """A page is open and looking at Ripple."""
    with _lock:
        _state["last_beat"] = now if now is not None else time.time()
        # Whatever was leaving, something is here now.
        _state["leaving_at"] = None


def leaving(now: float | None = None) -> None:
    """A page said it was going away.

    Not a reason to stop on its own -- a refresh sends exactly this and then a
    new page appears a moment later. It starts the short clock instead.
    """
    with _lock:
        if _state["leaving_at"] is None:
            _state["leaving_at"] = now if now is not None else time.time()


def verdict(now: float) -> str:
    """'run', or why it is time to stop. Given the time; never reads the clock."""
    with _lock:
        if _state["stopping"]:
            return "stopping"
        started = _state["started"] or now
        last = _state["last_beat"]
        going = _state["leaving_at"]
    if going is not None and now - going >= LEAVING_GRACE:
        return "the browser was closed"
    if last is None:
        if now - started >= STARTUP_GRACE:
            return "no browser ever opened Ripple"
        return "run"
    if now - last >= QUIET_LIMIT:
        return "the browser has been gone for a while"
    return "run"


def stop(reason: str = "asked to close") -> str:
    """Bring the program down. Safe to call twice; the second call does nothing."""
    with _lock:
        if _state["stopping"]:
            return "already stopping"
        _state["stopping"] = True
        server = _state["server"]
    if server is not None:
        # Uvicorn's own way out: it finishes the request in hand, closes the
        # socket and returns from run(), so the process ends normally and lets
        # go of the folder. _exit would leave the reply half-written.
        server.should_exit = True
    else:
        # No server to ask -- running under a test, or something went wrong
        # early. Nothing to do; the caller decides.
        return reason
    return reason


def stopping() -> bool:
    with _lock:
        return bool(_state["stopping"])


def watch(interval: float = 2.0) -> threading.Thread:
    """Check every couple of seconds whether anybody is still there."""

    def loop() -> None:
        while True:
            time.sleep(interval)
            why = verdict(time.time())
            if why in ("run", "stopping"):
                continue
            stop(why)
            # Uvicorn returns from run() shortly after should_exit is set. If it
            # has not gone in a few seconds something is holding it, and leaving
            # an invisible program running is the failure this whole module
            # exists to prevent -- so it is ended the blunt way instead.
            time.sleep(8)
            os._exit(0)

    thread = threading.Thread(target=loop, name="ripple-lifecycle", daemon=True)
    thread.start()
    return thread


def facts(now: float | None = None) -> dict:
    """What the screen is told, so it can say this plainly rather than imply it."""
    now = now if now is not None else time.time()
    with _lock:
        last = _state["last_beat"]
    return {
        "beatSeconds": BEAT_SECONDS,
        "quietLimit": int(QUIET_LIMIT),
        "secondsSinceBeat": None if last is None else int(now - last),
        "stopping": stopping(),
    }
````

## Paste 17 of 25 — 6 files

### ripple_offline/nonet.py

Create the file `ripple_offline/nonet.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""The guard that makes "offline" a fact rather than a claim.

A build machine has internet. That is exactly how an offline build ships with
something in it that quietly reaches out: on the machine where it was tested
the call succeeded, so nothing looked wrong, and the first time anyone finds
out is on the locked-down machine where it hangs instead.

So outbound connections are blocked outright, in the running application and in
the tests. Loopback is allowed, because Ripple talks to itself: the web server
listens on 127.0.0.1 and the browser connects to it. Anything else raises, and
the message says what was attempted, so a reach-out is a loud failure with an
address in it rather than a silent success.
"""
from __future__ import annotations

import ipaddress
import socket

LOOPBACK_NAMES = {"localhost", "localhost.localdomain", "ip6-localhost", ""}


class OutboundBlocked(RuntimeError):
    """Something tried to reach the network. Offline, that is a defect."""


_installed = False
_original: dict[str, object] = {}
attempts: list[str] = []              # every address that was refused


def _host_is_local(host: object) -> bool:
    if isinstance(host, bytes):
        host = host.decode("utf-8", "ignore")
    if not isinstance(host, str):
        return False
    name = host.strip().strip("[]").lower()
    if name in LOOPBACK_NAMES:
        return True
    try:
        return ipaddress.ip_address(name).is_loopback
    except ValueError:
        # A name that is not an address would have to be looked up to be
        # judged, and looking it up is itself a call off this machine.
        return False


def _address_is_local(address: object) -> bool:
    if not isinstance(address, tuple) or not address:
        return True                    # a unix socket or a pipe, not the network
    return _host_is_local(address[0])


def _describe(address: object) -> str:
    if isinstance(address, tuple) and len(address) >= 2:
        return f"{address[0]}:{address[1]}"
    return str(address)


def _refuse(address: object) -> OutboundBlocked:
    where = _describe(address)
    attempts.append(where)
    return OutboundBlocked(
        f"Ripple Offline tried to reach {where}. This copy of Ripple must never "
        f"call out — nothing here should need the network."
    )


def install() -> None:
    """Block every outbound connection from this process. Loopback still works."""
    global _installed
    if _installed:
        return
    _original.update({
        "connect": socket.socket.connect,
        "connect_ex": socket.socket.connect_ex,
        "create_connection": socket.create_connection,
        "getaddrinfo": socket.getaddrinfo,
    })

    def connect(self, address, *a, **kw):
        if not _address_is_local(address):
            raise _refuse(address)
        return _original["connect"](self, address, *a, **kw)

    def connect_ex(self, address, *a, **kw):
        if not _address_is_local(address):
            raise _refuse(address)
        return _original["connect_ex"](self, address, *a, **kw)

    def create_connection(address, *a, **kw):
        if not _address_is_local(address):
            raise _refuse(address)
        return _original["create_connection"](address, *a, **kw)

    def getaddrinfo(host, port, *a, **kw):
        # Looking a name up is a call off the machine in its own right, so it
        # is refused here rather than at the connection it would lead to.
        if not _host_is_local(host):
            raise _refuse((host, port))
        return _original["getaddrinfo"](host, port, *a, **kw)

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.create_connection = create_connection
    socket.getaddrinfo = getaddrinfo
    _installed = True


def uninstall() -> None:
    """Put the real socket functions back. For tests that need to undo this."""
    global _installed
    if not _installed:
        return
    socket.socket.connect = _original["connect"]
    socket.socket.connect_ex = _original["connect_ex"]
    socket.create_connection = _original["create_connection"]
    socket.getaddrinfo = _original["getaddrinfo"]
    _installed = False


def installed() -> bool:
    return _installed
````

### ripple_offline/paths.py

Create the file `ripple_offline/paths.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Where things are written on the machine Ripple is copied onto.

Everything Ripple keeps — the chosen folder, the SQL dialect, the saved history
— sits next to the executable, in the folder the user copied across. Nothing
goes into a hidden application-data folder, so deleting the folder really does
remove Ripple, and copying the folder to another machine takes the settings and
the history with it.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from .engine import OFFLINE_DIR, frozen

SETTINGS_NAME = "ripple-settings.json"
HISTORY_NAME = "ripple-history.db"


def app_dir() -> Path:
    """The folder a person actually sees: the one holding Ripple.exe.

    Running from source there is no executable, so the project folder stands in
    for it. Tests point RIPPLE_OFFLINE_HOME at a temporary folder so they never
    touch a real installation.
    """
    override = os.environ.get("RIPPLE_OFFLINE_HOME", "").strip()
    if override:
        return Path(override)
    if frozen():
        return Path(sys.executable).resolve().parent
    return OFFLINE_DIR


def settings_file() -> Path:
    return app_dir() / SETTINGS_NAME


def history_file() -> Path:
    return app_dir() / HISTORY_NAME


def web_dir() -> Path:
    """The offline front end.

    Built from the shared one rather than kept as a second copy — see
    ``webbuild.py``. In the executable it has already been built and bundled.
    """
    if frozen():
        return Path(getattr(sys, "_MEIPASS", ".")) / "web"
    return OFFLINE_DIR / "build" / "web"
````

### ripple_offline/prefs.py

Create the file `ripple_offline/prefs.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""The two settings a person has to choose, kept in a file beside the app.

Online, the repository folder and the SQL dialect are environment variables.
That is fine for someone who deploys things and hopeless for everybody else: a
colleague who has been handed a folder to double-click will never set one, so
they would silently scan the wrong folder, reading BigQuery as generic SQL.

So both are asked for on screen and written to ``ripple-settings.json`` next to
the executable. Nothing else is stored, and the file is plain text so it can be
read, edited or deleted by hand.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import paths

# Dialects worth offering, in the order they are shown. BigQuery is first and
# is the default: reading a BigQuery pipeline as generic SQL does not give a
# vaguer answer, it gives the opposite answer -- 2 of 5 files parsed and a
# confident "no impact" on a change that broke two things.
DIALECT_CHOICES: tuple[dict[str, str], ...] = (
    {"id": "bigquery", "label": "BigQuery", "note": "Our stack. Backticked names, EXCEPT, QUALIFY, UNNEST, MERGE."},
    {"id": "snowflake", "label": "Snowflake", "note": ""},
    {"id": "databricks", "label": "Databricks SQL", "note": ""},
    {"id": "spark", "label": "Spark SQL", "note": ""},
    {"id": "hive", "label": "Hive", "note": ""},
    {"id": "teradata", "label": "Teradata", "note": ""},
    {"id": "oracle", "label": "Oracle", "note": ""},
    {"id": "tsql", "label": "SQL Server (T-SQL)", "note": ""},
    {"id": "postgres", "label": "PostgreSQL", "note": ""},
    {"id": "mysql", "label": "MySQL", "note": ""},
    {"id": "redshift", "label": "Redshift", "note": ""},
    {"id": "presto", "label": "Presto", "note": ""},
    {"id": "trino", "label": "Trino", "note": ""},
    {"id": "duckdb", "label": "DuckDB", "note": ""},
    {"id": "sqlite", "label": "SQLite", "note": ""},
    {"id": "", "label": "Generic SQL", "note": "Only when the stack is genuinely unknown. Reads least, and can be confidently wrong."},
)

DEFAULT_DIALECT = "bigquery"


def default_hops() -> int:
    """How many renames deep to follow, taken from the shared engine.

    Not a number of its own. This was hard-coded to 4 here while the engine
    moved to 10, so the program a colleague double-clicks would have gone on
    quietly stopping six hops short of every published table -- the exact
    failure the engine change was made to fix, shipped only to the machine
    where nobody can check it.
    """
    from ripple.config import Settings

    return Settings().max_hops


def max_hops_ceiling() -> int:
    """The deepest this program will follow when a limit is asked for.

    Zero is not capped by this: zero means "follow until the code runs out",
    which is the default and is bounded by the walk's own memory of where it has
    been rather than by a number. See ripple.config.Settings.max_hops -- a
    counter here could only ever cut a real trail short and report the cut as
    the end of the warehouse.
    """
    return 25


def clamp_hops(value) -> int:
    """A hop setting, kept meaningful. Zero survives; anything else is 1..25."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default_hops()
    if n <= 0:
        return 0
    return min(max_hops_ceiling(), n)


def default_production() -> str:
    from ripple.config import DEFAULT_PRODUCTION

    return ", ".join(DEFAULT_PRODUCTION)


DEFAULTS: dict[str, Any] = {
    "repoPath": "",
    "repoLabel": "",
    "sqlDialect": DEFAULT_DIALECT,
    # Zero: follow until the code runs out. Matches the shared engine, and
    # test_settings.py fails if the two ever drift.
    "maxHops": 0,
    # Which table names are the ones this team publishes. There is no default,
    # and there must never be one again: leaving it at _PROD on a repository
    # that names nothing _PROD is what turns a real impact into a confident
    # "no impact". Empty means NOT GIVEN, and nothing is scanned until it is.
    "prodTables": "",
}


def dialects() -> list[dict[str, str]]:
    """The choices, minus any this copy of sqlglot does not actually know.

    An option that cannot work is worse than a missing one: it would be picked,
    saved, and then quietly read every file as generic SQL anyway.
    """
    from sqlglot import Dialect
    known = set(Dialect.classes)
    return [d for d in DIALECT_CHOICES if d["id"] == "" or d["id"] in known]


def valid_dialect(value: str) -> bool:
    return (value or "") in {d["id"] for d in dialects()}


# ── the file ───────────────────────────────────────────────────────────────
def load() -> dict[str, Any]:
    """Whatever was saved last time, with anything missing or broken defaulted."""
    out = dict(DEFAULTS)
    path = paths.settings_file()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return out                      # never seen it before, or it is damaged
    if not isinstance(raw, dict):
        return out
    for key in DEFAULTS:
        if key in raw and isinstance(raw[key], type(DEFAULTS[key])):
            out[key] = raw[key]
    if not valid_dialect(str(out["sqlDialect"])):
        out["sqlDialect"] = DEFAULT_DIALECT
    out["maxHops"] = clamp_hops(out["maxHops"])
    # No fallback. An unset list is a state to be asked about, not a rule to be
    # matched against. See DEFAULTS above.
    out["prodTables"] = str(out["prodTables"] or "").strip()
    return out


def save(values: dict[str, Any]) -> dict[str, Any]:
    """Write the settings file. Returns what was actually saved."""
    keep = {k: values.get(k, DEFAULTS[k]) for k in DEFAULTS}
    # Stored as a full path. A relative one would mean something different
    # depending on where Ripple happened to be started from, and "." would mean
    # Ripple's own program folder.
    raw_path = str(keep["repoPath"] or "").strip()
    keep["repoPath"] = str(Path(raw_path).resolve()) if raw_path else ""
    keep["repoLabel"] = str(keep["repoLabel"] or "").strip() or folder_label(keep["repoPath"])
    if not valid_dialect(str(keep["sqlDialect"])):
        keep["sqlDialect"] = DEFAULT_DIALECT
    keep["maxHops"] = clamp_hops(keep["maxHops"])
    # Saved exactly as typed, empty included. Empty means NOT GIVEN -- see
    # DEFAULTS. Falling back here is what let a scan run against a rule nobody
    # chose and report "no production table is affected" from it.
    keep["prodTables"] = str(keep["prodTables"] or "").strip()
    path = paths.settings_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(keep, indent=2) + "\n", encoding="utf-8")
    return keep


def configured(values: dict[str, Any] | None = None) -> bool:
    """Is Ripple set up enough to answer anything?

    Two things, and BOTH are required. A folder with no published-table list is
    a Ripple that can read every file and still not know what any of it means
    for anybody: every table fails the published test, and a change that breaks
    three published tables comes back "no production table is affected". That is
    the same green tick as a genuinely clean answer.
    """
    values = values if values is not None else load()
    return (bool(str(values.get("repoPath") or "").strip())
            and bool(str(values.get("prodTables") or "").strip()))


def folder_label(path: str | Path) -> str:
    name = Path(str(path or "")).name
    return name or str(path or "")


# ── what the settings mean to the shared engine ────────────────────────────
def apply(values: dict[str, Any]) -> None:
    """Push the chosen settings into the shared engine's configuration.

    The engine reads one settings object. Rather than forking it, the offline
    app edits that object: the folder, the dialect and where history is kept,
    plus the things that must never be true offline -- no GitHub source, no AI
    key, and no serverless limits, because this runs on a real machine with a
    real disk.
    """
    from ripple.config import settings

    settings.repo_path = Path(str(values.get("repoPath") or ""))
    settings.repo_label = str(values.get("repoLabel") or "") or folder_label(settings.repo_path)
    settings.repo_branch = git_branch(settings.repo_path)
    settings.sql_dialect = str(values.get("sqlDialect") or "")
    settings.max_hops = clamp_hops(values.get("maxHops"))
    # The pasted list, in whatever shape it arrived. An empty one stays empty
    # and means NOT GIVEN; the scan route refuses rather than answering against
    # a rule nobody chose. See DEFAULTS.
    settings.set_production(str(values.get("prodTables") or ""))
    settings.db_path = paths.history_file()
    settings.serverless = False
    settings.repo_source = "folder"
    settings.repo_url_template = ""
    # Offline there is no AI and no GitHub, so the engine is told so directly
    # rather than being trusted to leave them alone.
    settings.ai_key = ""
    settings.github_repo = ""
    settings.github_branch = ""
    settings.github_token = ""


def git_branch(path: Path | str) -> str:
    """The branch a copied-out repository was on, read from the folder itself.

    A real fact when the folder is a git checkout, and nothing at all when it is
    not — better than showing "main" because that is the usual answer.
    """
    head = Path(str(path or "")) / ".git" / "HEAD"
    try:
        text = head.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    if text.startswith("ref:"):
        return text.split("/")[-1].strip()
    return text[:7] if text else ""     # a detached checkout: the commit itself


# ── is the folder still there, and does it hold anything? ──────────────────
def folder_state(path: str | Path) -> dict[str, Any]:
    """Is the folder there at all? Cheap enough to ask on every page load.

    A folder that has been moved, renamed or deleted since it was chosen is the
    normal case on a locked-down machine, not an exceptional one, so it gets a
    sentence a person can act on instead of an empty scan or a crash.
    """
    raw = str(path or "").strip()
    if not raw:
        return {"ok": False, "state": "unset",
                "message": "No repository folder chosen yet."}
    folder = Path(raw)
    if not folder.exists():
        return {"ok": False, "state": "missing",
                "message": f"That folder is not on this machine any more: {folder}"}
    if not folder.is_dir():
        return {"ok": False, "state": "notafolder",
                "message": f"That is a file, not a folder: {folder}"}
    return {"ok": True, "state": "ok", "message": ""}


def check_folder(path: str | Path) -> dict[str, Any]:
    """The same answer, plus how much is in there.

    This one walks the folder, so it is asked when somebody presses "check" or
    saves — not on every page load, where a large repository would make the
    screen sit there doing nothing visible.
    """
    from ripple.config import settings

    base = folder_state(path)
    if not base["ok"]:
        return {**base, "files": 0}
    folder = Path(str(path).strip())
    try:
        found = _count_code_files(folder, settings)
    except OSError as exc:
        return {"ok": False, "state": "unreadable", "files": 0,
                "message": f"That folder could not be read ({exc.strerror or exc})."}
    if not found:
        kinds = ", ".join(sorted(settings.code_extensions)[:6])
        return {"ok": False, "state": "empty", "files": 0,
                "message": f"That folder has no files Ripple can read. It looks for {kinds} and similar."}
    return {"ok": True, "state": "ok", "files": found,
            "message": f"{found} file{'' if found == 1 else 's'} Ripple can read."}


def _count_code_files(folder: Path, settings, cap: int = 20000) -> int:
    """Counted the same way the scanner counts, so the two never disagree.

    In particular the skipped-folder names are matched inside the repository
    only. A repository that happens to sit under a folder called build or venv
    is a normal thing on somebody's machine, and must not read as empty.
    """
    found = 0
    for p in folder.rglob("*"):
        if found >= cap:
            break
        if not p.is_file():
            continue
        if any(part in settings.skip_dirs for part in p.relative_to(folder).parts):
            continue
        if p.suffix.lower() in settings.code_extensions:
            found += 1
    return found
````

### ripple_offline/synced.py

Create the file `ripple_offline/synced.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Is Ripple itself sitting in a folder something is syncing to the cloud?

Ripple Offline keeps everything beside the executable -- the chosen folder, the
SQL dialect, the saved history, the log. That is deliberate: deleting the folder
really does remove Ripple, and copying the folder to another machine takes the
settings and the history with it.

It has one consequence worth saying out loud. Everyone in this office has
OneDrive sync switched on, so the folder Ripple is copied into is very likely a
folder OneDrive uploads. Two things follow, and neither is obvious:

* The saved history is a database file. A sync client holds a file open while it
  uploads it, and it copies files whenever it likes. A save can fail because of
  that, and a database copied mid-write can come back damaged.
* Everything in the folder goes up to the company's cloud -- the whole program,
  not just the settings. That is a decision somebody should make on purpose
  rather than discover afterwards.

Neither is a reason to stop. Both are a reason to say so.
"""
from __future__ import annotations

import os
from pathlib import Path

# The environment variables OneDrive sets to the root of each sync folder. This
# is the reliable signal: it comes from OneDrive itself rather than from a
# folder happening to be called something.
_ONEDRIVE_VARS = ("OneDrive", "OneDriveCommercial", "OneDriveConsumer")

# Fallbacks, for a machine where those are not set and for the other clients
# people have. Matched against whole folder names, never as substrings, so a
# folder called "dropbox-migration-notes" is not mistaken for Dropbox.
_KNOWN_CLIENTS = {
    "onedrive": "OneDrive",
    "dropbox": "Dropbox",
    "google drive": "Google Drive",
    "googledrive": "Google Drive",
    "my drive": "Google Drive",
    "box": "Box",
    "icloackdrive": "iCloud Drive",
    "icloud drive": "iCloud Drive",
}


def _roots() -> list[tuple[Path, str]]:
    out: list[tuple[Path, str]] = []
    for var in _ONEDRIVE_VARS:
        raw = os.environ.get(var, "").strip()
        if raw:
            out.append((Path(raw), "OneDrive"))
    return out


def _named_client(folder: Path) -> str:
    """The sync client whose folder this is inside, judged by folder name."""
    for part in folder.parts:
        name = part.strip().lower()
        if name in _KNOWN_CLIENTS:
            return _KNOWN_CLIENTS[name]
        # "OneDrive - Contoso Ltd" is how a work account names its root.
        if name.startswith("onedrive - ") or name.startswith("onedrive-"):
            return "OneDrive"
    return ""


def detect(folder: Path | str) -> dict:
    """What is syncing this folder, if anything, and what that means here.

    Returns a plain dict rather than raising or logging, because the only thing
    that is ever done with it is putting it on the screen.
    """
    try:
        folder = Path(folder).resolve()
    except OSError:                                   # pragma: no cover - defensive
        return {"synced": False, "client": "", "root": ""}

    for root, client in _roots():
        try:
            resolved = root.resolve()
        except OSError:                               # pragma: no cover - defensive
            continue
        if folder == resolved or resolved in folder.parents:
            return {"synced": True, "client": client, "root": str(resolved)}

    client = _named_client(folder)
    if client:
        return {"synced": True, "client": client, "root": ""}
    return {"synced": False, "client": "", "root": ""}
````

### ripple_offline/__init__.py

Create the file `ripple_offline/__init__.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Ripple, packaged for a machine where nothing can be installed.

A snapshot, not the product's own offline build. The product keeps ONE engine
and reaches back into it; this folder carries its own copy because there is
nothing here to reach back to. See engine.py for what that costs.

What lives in this package is only what genuinely differs when Ripple has to run
with no internet and no installs: settings chosen on screen instead of in
environment variables, a web service built out of Python's own library, and a
front end with nothing on it that reaches out.
"""
from __future__ import annotations

from .engine import ensure_engine_importable

ensure_engine_importable()
````

### ripple_offline/engine.py

Create the file `ripple_offline/engine.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Finding the analysis engine, in a copy that has been carried somewhere.

The product itself keeps ONE engine and never copies it: the packaged build
reaches back into ``Codebase/ripple`` so the offline copy can never quietly fall
behind the online one. That rule is right, and it is why this file is the only
part of the wrapper that differs here.

This folder is a SNAPSHOT, made to be put on a memory stick and opened on a
machine that has never heard of the rest of the repository. There is nothing to
reach back to, so the engine sits inside this folder, next to this file, and is
imported from there.

Two consequences worth being plain about.

**This copy does not update itself.** It is the engine as it stood on the day the
snapshot was taken, and the version on the settings screen is that day's version.
To move it forward, take a fresh snapshot rather than editing anything in here --
an edited snapshot is a fork, and a fork on a locked-down laptop is the copy
nobody can check.

**Replacing this file with the product's own would look like it worked.** The
product's version puts ``Codebase`` on the import path, and on the machine the
snapshot was assembled on, Codebase is right there -- so everything runs, every
test passes, and the failure only happens on the laptop the folder was made for.
That is why the snapshot tool keeps this file rather than copying it.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP_DIR = HERE.parent                            # the folder holding run.py
LOCAL_ENGINE = APP_DIR / "ripple"
LOCAL_PARSER = APP_DIR / "sqlglot"

# The rest of the wrapper asks for this by name. Kept under the name it uses in
# the product, so paths.py, prefs.py and the others are unedited copies and can
# be refreshed from the repository without a thought.
OFFLINE_DIR = APP_DIR

MISSING = f"""
Ripple could not find its own engine.

It expects a folder called "ripple" beside run.py:
    {LOCAL_ENGINE}

Copy the whole Ripple folder again, in one piece. Copying only some of it is
the usual reason for this - the folder has to arrive complete.
"""

NO_PARSER = f"""
Ripple could not find the SQL parser.

It expects a folder called "sqlglot" beside run.py:
    {LOCAL_PARSER}

That folder is the one thing here that nobody can write for you, and it is why
the whole folder has to be copied in one piece rather than assembled file by
file. Copy it again from a machine that has it.
"""


def frozen() -> bool:
    """True when running as a built program rather than from these files."""
    return bool(getattr(sys, "frozen", False))


def ensure_engine_importable() -> Path | None:
    """Make ``import ripple`` and ``import sqlglot`` work from this folder.

    The folder is put FIRST on the import path on purpose. On a machine that
    happens to have another Ripple, or another sqlglot, installed, this copy has
    to be the one that runs -- otherwise the answer on screen came from code
    nobody in this folder can look at.
    """
    if frozen():
        return None                              # a build collected it already
    if not (LOCAL_ENGINE / "config.py").is_file():
        raise SystemExit(MISSING)
    if not (LOCAL_PARSER / "__init__.py").is_file():
        raise SystemExit(NO_PARSER)
    here = str(APP_DIR)
    if sys.path[:1] != [here]:
        if here in sys.path:
            sys.path.remove(here)
        sys.path.insert(0, here)
    return APP_DIR
````

## Paste 18 of 25 — 2 files

### ripple_offline/app.py

Create the file `ripple_offline/app.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""The offline web service, built on Python's own library.

The same routes, the same JSON and the same refusals as the packaged build --
which is the whole reason the screens do not change. What is different is only
underneath: no FastAPI, no uvicorn, no pydantic, nothing that has to be
installed. See webserver.py for the plumbing.

There is no GitHub route and no AI route -- not disabled, not behind a flag,
absent -- so there is no key to leak, no address to type, and nothing that can
quietly start working because the machine turned out to have internet after all.

Every route below calls the shared engine in ``ripple``. Nothing about scanning,
reading SQL, tracing lineage or writing the summary is reimplemented here; this
is a thin layer, exactly as the packaged service is.
"""
from __future__ import annotations

import copy
import threading
from pathlib import Path
from typing import Any

from . import folderpick, lifecycle, nonet, paths, prefs, synced
from .webserver import HTTPError, Router

from ripple import narrative, production, progress, store
from ripple.build_info import build_info
from ripple.catalog import Catalog, build_catalog
from ripple.config import settings
from ripple.notification import extract_by_rules, read_upload
from ripple.scanner.lineage import trace
from ripple.scanner.repo import RepoIndex
from ripple.scanner.sqlread import ParsedRepo, parse_repo

router = Router()

_state: dict[str, Any] = {"index": None, "parsed": None, "catalog": None}

# ── reading without holding the screen hostage ─────────────────────────────
# Reading a repository the size of a real warehouse takes minutes, and
# /api/health is the request the screen makes before it can paint anything at
# all. On a few thousand files that is a window sitting blank with no way to ask
# what is happening -- because the only request that would tell it is the one it
# is already waiting on. A working program that says nothing for two minutes
# gets reported as a hung one, and here that window is the whole product.
#
# So the read happens on a thread, health answers straight away with
# indexing:true, and the screen shows the counted file numbers.
_build_lock = threading.RLock()
_reading: dict[str, Any] = {"thread": None, "error": ""}


def start_reading() -> None:
    """Begin reading on a thread, unless one is already at it."""
    with _build_lock:
        alive = _reading["thread"]
        if alive is not None and alive.is_alive():
            return

        def work() -> None:
            try:
                _reading["error"] = ""
                repo_state()
            except Exception as exc:                          # noqa: BLE001
                # Kept and shown. A read that failed and a read that never
                # finished look identical from the screen, and one of them needs
                # somebody to go and do something about it.
                _reading["error"] = str(exc)
            finally:
                progress.finish()

        t = threading.Thread(target=work, name="ripple-read", daemon=True)
        _reading["thread"] = t
        t.start()


def repo_state() -> tuple[RepoIndex, ParsedRepo, Catalog]:
    with _build_lock:
        return _read_if_needed()


def _read_if_needed() -> tuple[RepoIndex, ParsedRepo, Catalog]:
    if _state["index"] is None:
        # A folder that is missing, or has never been chosen, is a normal state
        # here rather than an error: the index comes back empty and the screen
        # says why. An unset folder is an empty path, which as a path means
        # "here" -- so without this Ripple would index its own program folder
        # and present it as the repository, which is worse than finding nothing.
        chosen = str(settings.repo_path).strip()
        if chosen in ("", "."):
            idx = RepoIndex(root=None)
        else:
            idx = RepoIndex.build(settings.repo_path, settings,
                                  on_progress=progress.reader("reading"))
        parsed = parse_repo(idx, settings, on_progress=progress.reader("parsing"))
        progress.finish()
        _state.update({"index": idx, "parsed": parsed, "catalog": build_catalog(parsed)})
    return _state["index"], _state["parsed"], _state["catalog"]


def reindex() -> None:
    _state["index"] = None
    repo_state()


# ── what the screen is told ────────────────────────────────────────────────
def _still_reading(values: dict, folder: dict) -> dict:
    """The health answer while the repository is being read for the first time.

    The SAME SHAPE as the finished one, with the counts at zero and ``indexing``
    true. One app.js paints from this, and a key left out here is a blank on
    screen that no test would ever see.
    """
    return {
        "ok": True,
        "indexing": True,
        "readError": _reading["error"],
        "progress": progress.snapshot(),
        "build": build_info(),
        "source": "folder",
        "offline": True,
        "configured": prefs.configured(values),
        "folder": folder,
        "canBrowse": folderpick.available(),
        "settingsFile": str(paths.settings_file()),
        "historyFile": str(paths.history_file()),
        "syncedFolder": synced.detect(paths.app_dir()),
        "dialects": prefs.dialects(),
        "serverless": False,
        "limits": {"maxUploadBytes": settings.max_upload_bytes, "historyKept": True},
        "repo": {
            "label": str(values.get("repoLabel") or ""),
            "path": str(values.get("repoPath") or ""),
            "branch": settings.repo_branch,
            "files": 0, "statements": 0, "unreadable": 0,
            "heldOnline": 0, "pathTooLong": 0, "inSkippedDirs": 0,
            "skippedDirNames": [], "runsSqlFrom": 0,
            "exists": folder["ok"], "kinds": [], "unknownExt": [],
        },
        "catalog": {"tables": 0, "columns": 0},
        "sqlDialect": settings.sql_dialect or "generic",
        "sqlDialectId": settings.sql_dialect,
        "maxHops": settings.max_hops,
        "production": settings.production_rule(),
        "productionRule": settings.production().to_dict(),
        "productionFrom": "entered" if settings.has_production() else "unset",
        "productionSet": settings.has_production(),
    }


def _health() -> dict:
    values = prefs.load()
    # Judged on what was actually chosen, not on the engine's path: an unset
    # path reads as "here", and "here" is Ripple's own program folder.
    folder = prefs.folder_state(values["repoPath"])
    # The folder was read into memory when Ripple started. If it has been moved
    # or deleted since, that reading is no longer true of anything -- and a
    # screen saying "the folder is gone" while offering to scan 24 files from it
    # is worse than either message on its own.
    if not folder["ok"] and _state["index"] is not None and _state["index"].files:
        _state["index"] = None
    if _state["index"] is None and str(values["repoPath"]).strip() not in ("", "."):
        start_reading()
        if _state["index"] is None:
            return _still_reading(values, folder)
    idx, parsed, cat = repo_state()
    kinds: dict[str, int] = {}
    for f in idx.files:
        kinds[f.lang] = kinds.get(f.lang, 0) + 1
    return {
        "ok": True,
        "indexing": False,
        "readError": _reading["error"],
        "build": build_info(),
        "source": "folder",
        "offline": True,
        "configured": prefs.configured(values),
        "folder": folder,
        "canBrowse": folderpick.available(),
        "settingsFile": str(paths.settings_file()),
        "historyFile": str(paths.history_file()),
        "syncedFolder": synced.detect(paths.app_dir()),
        "dialects": prefs.dialects(),
        "serverless": False,
        "limits": {"maxUploadBytes": settings.max_upload_bytes, "historyKept": True},
        "repo": {
            "label": str(values.get("repoLabel") or ""),
            "path": str(values.get("repoPath") or ""),
            "branch": settings.repo_branch,
            "files": len(idx.files),
            "statements": len(parsed.statements),
            "unreadable": len(parsed.unreadable),
            "heldOnline": len(idx.held_online),
            "pathTooLong": len(idx.too_long),
            "inSkippedDirs": len(idx.in_skipped_dirs),
            "skippedDirNames": list(idx.skipped_dir_names),
            "runsSqlFrom": len([r for r in parsed.runs_sql_from if r["runs"]]),
            "exists": folder["ok"],
            "kinds": [{"lang": k, "files": n}
                      for k, n in sorted(kinds.items(), key=lambda kv: (-kv[1], kv[0]))],
            # File types Ripple does not open, biggest first. The screen that
            # shows these is the SAME app.js the packaged build uses, so leaving
            # the key out here means this copy silently shows nothing where that
            # one shows the tally.
            "unknownExt": [
                {"ext": k, "files": n}
                for k, n in sorted(idx.unknown_ext.items(), key=lambda kv: (-kv[1], kv[0]))
            ][:12],
        },
        "catalog": {"tables": len(cat.tables),
                    "columns": sum(len(v) for v in cat.tables.values())},
        "sqlDialect": settings.sql_dialect or "generic",
        "sqlDialectId": settings.sql_dialect,
        "maxHops": settings.max_hops,
        "production": settings.production_rule(),
        "productionRule": settings.production().to_dict(),
        "productionFrom": "entered" if settings.has_production() else "unset",
        "productionSet": settings.has_production(),
    }


# ── routes ─────────────────────────────────────────────────────────────────
@router.get("/api/health")
def health() -> dict:
    return _health()


# ── knowing when to stop ───────────────────────────────────────────────────
# Without these, closing the browser leaves the program running where nobody can
# see it: the folder cannot be deleted, the port stays taken, and the only way
# out is Task Manager.
@router.post("/api/alive")
def alive() -> dict:
    """The open page saying it is still there. Sent every few seconds."""
    lifecycle.beat()
    return {"ok": True}


@router.post("/api/leaving")
def going() -> dict:
    """The page is closing. Starts a short clock rather than stopping now, so a
    refresh -- which sends exactly this -- does not take Ripple down with it."""
    lifecycle.leaving()
    return {"ok": True}


@router.post("/api/quit")
def quit_now() -> dict:
    """The Close Ripple button. Stops the program and lets go of the folder."""
    return {"ok": True, "reason": lifecycle.stop("closed from the screen")}


@router.get("/api/progress")
def progress_now() -> dict:
    """What Ripple is doing this second, asked for by the screen while it waits.

    Every number is counted rather than estimated, and where there is no total
    it says so rather than drawing a bar over a number nobody knows.
    """
    return progress.snapshot()


@router.get("/api/catalog")
def catalog() -> dict:
    _, _, cat = repo_state()
    return cat.to_dict()


@router.post("/api/reindex")
def do_reindex() -> dict:
    reindex()
    return _health()


# ── the settings, chosen on screen ─────────────────────────────────────────
@router.get("/api/settings")
def get_settings() -> dict:
    values = prefs.load()
    return {
        "values": values,
        "dialects": prefs.dialects(),
        "folder": prefs.check_folder(values["repoPath"]),
        "canBrowse": folderpick.available(),
        "settingsFile": str(paths.settings_file()),
        "historyFile": str(paths.history_file()),
    }


@router.post("/api/settings/check")
def check_settings(body: dict) -> dict:
    """Say what is in a folder before anyone commits to it."""
    return prefs.check_folder(body.get("path", ""))


@router.post("/api/settings/browse")
def browse() -> dict:
    """Open this machine's own folder picker, when there is one to open.

    Typing a path is always possible; this only saves the typing. Where the
    picker is not available the screen never offers the button, rather than
    offering one that does nothing.
    """
    if not folderpick.available():
        raise HTTPError(501, "This machine has no folder picker. "
                             "Type or paste the path instead.")
    chosen = folderpick.choose_folder()
    return {"path": chosen or "", "cancelled": not chosen}


@router.post("/api/settings")
def save_settings(body: dict) -> dict:
    """Save the folder and the dialect, then read the repository again.

    A folder that cannot be read is refused here rather than saved and
    discovered later, so the message names the folder that was actually tried.
    """
    repo_path = str(body.get("repoPath", "") or "")
    dialect = str(body.get("sqlDialect", prefs.DEFAULT_DIALECT) or prefs.DEFAULT_DIALECT)
    if not prefs.valid_dialect(dialect):
        raise HTTPError(400, "That is not a SQL dialect Ripple can read.")
    verdict = prefs.check_folder(repo_path)
    if not verdict["ok"]:
        raise HTTPError(400, verdict["message"])
    # Only two of these settings change what was read off the disk. Correcting
    # the published-table list on a repository of a few thousand files would
    # otherwise cost a full re-read -- minutes of waiting for an answer already
    # in memory, which is how somebody learns not to correct it.
    before = prefs.load()
    settled = str(Path(repo_path.strip()).resolve()) if repo_path.strip() else ""
    rereads = (str(before.get("repoPath") or "") != settled
               or str(before.get("sqlDialect") or "") != dialect
               or _state["index"] is None)
    try:
        saved = prefs.save({"repoPath": repo_path, "repoLabel": "",
                            "sqlDialect": dialect,
                            "maxHops": int(body.get("maxHops") or 0),
                            "prodTables": str(body.get("prodTables", "") or "")})
    except OSError as exc:
        # Ripple keeps its settings beside itself. Somewhere like Program Files,
        # or a network share it was opened from, may not allow that -- and
        # "Something went wrong: 500" tells nobody to move the folder.
        raise HTTPError(
            400,
            f"Ripple could not save its settings into {paths.app_dir()} "
            f"({exc.strerror or exc}). That folder does not allow writing. "
            f"Copy the whole Ripple folder somewhere you own - your Desktop or "
            f"Documents - and start it again from there.") from exc
    prefs.apply(saved)
    if rereads:
        reindex()
    return _health()


# ── the tables this team publishes ─────────────────────────────────────────
# The most expensive setting here, so it can be read back before it is saved.
# The question that matters is not "did the paste parse" but "which of these
# tables has Ripple never seen in the folder it just read".
def _production_report(rule: production.ProductionRule) -> dict:
    idx, parsed, _ = repo_state()
    return {**rule.to_dict(), "check": production.check_against_repo(rule, idx, parsed)}


@router.post("/api/production/read")
def production_read(body: dict) -> dict:
    """Read a pasted list without saving it, and say what was made of it."""
    return _production_report(production.parse(str(body.get("text", "") or "")))


@router.get("/api/production")
def production_now() -> dict:
    """The list in play, checked against the folder that is loaded."""
    return _production_report(settings.production())


# ── reading the notification ───────────────────────────────────────────────
@router.post("/api/read-email")
def read_email_file(upload: tuple) -> dict:
    name, raw = upload
    if len(raw) > settings.max_upload_bytes:
        raise HTTPError(
            413,
            f"That file is {len(raw) / 1_000_000:.1f} MB. The most this copy of "
            f"Ripple accepts is {settings.max_upload_bytes / 1_000_000:.0f} MB.")
    n = read_upload(name or "", raw)
    _, _, cat = repo_state()
    out = extract_by_rules(n, cat)
    out["emailPreview"] = {
        "subject": n.subject, "body": n.body[:4000],
        "fromName": n.from_name, "fromEmail": n.from_email,
        "attachments": n.attachments, "kind": n.source_kind,
    }
    return out


# ── scanning and writing it up ─────────────────────────────────────────────
@router.post("/api/scan")
def scan(body: dict) -> dict:
    idx, parsed, _ = repo_state()
    upstream = [{"table": u.get("table", ""), "attrs": list(u.get("attrs") or [])}
                for u in (body.get("upstream") or [])]
    if not upstream:
        raise HTTPError(400, "No upstream tables were supplied.")
    # Refused, never answered around. Without the list every table fails the
    # published test, and a scan that reaches three published tables reports
    # "no production table is affected" -- the same green tick as a genuinely
    # clean answer, over a change that breaks all of them.
    if not settings.has_production():
        raise HTTPError(
            400,
            "Ripple does not know which of your tables are the published ones yet, "
            "so it cannot say whether this change reaches any. Add them on the "
            "settings screen - paste the table names, or a pattern such as "
            "_PUBLISHED - and run this again.")
    cfg = settings
    asked = int(body.get("maxHops") or 0)
    if asked and asked != settings.max_hops:
        # The result screen offers to follow a cut-short trail further. Without
        # this the button would be pressed, the scan would run at the saved
        # depth, and the same cut-short answer would come back -- a button that
        # does nothing, on the one screen that is meant to be honest.
        cfg = copy.copy(settings)
        cfg.max_hops = max(1, min(asked, prefs.max_hops_ceiling()))
    try:
        res = trace(idx, parsed, upstream,
                    change_type=str(body.get("changeKind", "unknown") or "unknown"),
                    cfg=cfg, on_progress=progress.reader("scanning"))
    finally:
        progress.finish()
    out = res.to_dict()
    # No link template: the files are on this machine, and there is no address
    # to send anyone to. The screen offers no link rather than a broken one.
    out["repo"] = {"label": settings.repo_label, "branch": settings.repo_branch,
                   "urlTemplate": ""}
    return out


@router.post("/api/summary")
def summary(body: dict) -> dict:
    """Written from the findings by the rules. There is no AI here to fall back
    from, so this is the only path - which is why the rules-based reader had to
    be worth reading."""
    scan_out = body.get("scan") or {}
    vals = body.get("vals") or {}
    base = narrative.summarise(scan_out, vals)
    return {"summary": base, "reply": narrative.draft_reply(scan_out, vals, base)}


# ── history, which actually lasts here ─────────────────────────────────────
@router.post("/api/history")
def save_analysis(body: dict) -> dict:
    return store.save(body.get("vals") or {}, body.get("scan") or {},
                      body.get("summary") or {},
                      str(body.get("mode", "email") or "email"), settings)


@router.get("/api/history")
def history() -> list:
    return store.listing(settings)


@router.get("/api/history/{analysis_id}")
def history_item(analysis_id: str) -> dict:
    row = store.get(int(analysis_id), settings)
    if not row:
        raise HTTPError(404, "Not found.")
    return row


@router.patch("/api/history/{analysis_id}")
def history_status(analysis_id: str, body: dict) -> dict:
    if not store.set_status(int(analysis_id), str(body.get("status", "")), settings):
        raise HTTPError(400, "Unknown status or id.")
    return {"ok": True}


@router.get("/api/file")
def file_content(path: str) -> dict:
    idx, _, _ = repo_state()
    f = idx.get(path)
    if f is None:
        raise HTTPError(404, "Not in the index.")
    return {"path": f.path, "lang": f.lang, "lines": f.text.splitlines()}


# ── the offline guard, reported rather than assumed ────────────────────────
@router.get("/api/offline-check")
def offline_check() -> dict:
    """Whether this process really is barred from calling out, and what tried.

    A claim on a screen is worth nothing on its own; this is the same guard the
    tests use, answering for the copy that is actually running.
    """
    return {"guardInstalled": nonet.installed(), "attempts": list(nonet.attempts)}


# ── the site itself ────────────────────────────────────────────────────────
def mount_web() -> bool:
    """Serve the front end, from wherever this copy keeps it.

    Two places, and both are ordinary. A copy built on a machine that can
    install things generates the screens into build/web every time it starts, so
    they can never be stale. A copy carried onto a machine that cannot install
    anything has them ready-made in web/, because the thing that generates them
    was left behind with everything else that needed installing.
    """
    for web in (paths.app_dir() / "web", paths.web_dir()):
        if (web / "index.html").is_file():
            router.mount("/static", web)
            router.index(web / "index.html")
            return True
    return False
````

### ripple_offline/webserver.py

Create the file `ripple_offline/webserver.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""A web service built out of Python's own library and nothing else.

The packaged build of Ripple runs on FastAPI and uvicorn. Neither can be
installed on a machine that refuses installs, so this stands in their place.

It is deliberately small. Every route in ``app.py`` is a plain function that
takes what it needs and returns a dictionary, exactly as it does under FastAPI,
so the two versions of the service read almost identically and neither has any
thinking in it. What is here is only the plumbing: match a request to a
function, hand it the body, and turn the answer into JSON.

The shape of every reply is the one the screens already expect:

    a success   the function's dictionary or list, as JSON
    a refusal   {"detail": "one sentence a person can act on"} and a status

Get that wrong and every error on screen becomes the number 500, which tells
nobody anything.
"""
from __future__ import annotations

import json
import re
import socket
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


class HTTPError(Exception):
    """A refusal with a status and a sentence. The same idea as FastAPI's
    HTTPException, so the route bodies do not have to change."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


# What a file is served as. Anything not here is sent as bytes, which every
# browser handles; guessing a type is how a font arrives as text and the page
# renders in the wrong one.
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".png": "image/png",
    ".ico": "image/x-icon",
}

# A path piece written as {name} in a route becomes a value handed to the
# function. Everything else has to match exactly.
_PARAM = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


class Router:
    """Which function answers which request."""

    def __init__(self) -> None:
        self._routes: list[tuple[str, re.Pattern, object]] = []
        self._static: tuple[str, Path] | None = None
        self._index: Path | None = None

    def route(self, method: str, path: str):
        pattern = re.compile("^" + _PARAM.sub(r"(?P<\1>[^/]+)", re.escape(path)
                                              .replace(r"\{", "{").replace(r"\}", "}")) + "$")

        def keep(fn):
            self._routes.append((method.upper(), pattern, fn))
            return fn
        return keep

    def get(self, path: str):
        return self.route("GET", path)

    def post(self, path: str):
        return self.route("POST", path)

    def patch(self, path: str):
        return self.route("PATCH", path)

    def mount(self, prefix: str, folder: Path) -> None:
        self._static = (prefix.rstrip("/"), Path(folder))

    def index(self, file: Path) -> None:
        self._index = Path(file)

    def find(self, method: str, path: str):
        """The function for this request, and the values out of its path.

        A path that matches on the address but not the method is told so, rather
        than reported as missing: "405" and "404" send somebody looking in two
        completely different places.
        """
        wrong_method = False
        for m, pattern, fn in self._routes:
            found = pattern.match(path)
            if found is None:
                continue
            if m != method:
                wrong_method = True
                continue
            return fn, found.groupdict()
        if wrong_method:
            raise HTTPError(405, f"{path} does not answer a {method}.")
        return None, {}


# ── reading what the browser sent ──────────────────────────────────────────
def _read_body(handler: BaseHTTPRequestHandler) -> bytes:
    size = int(handler.headers.get("Content-Length") or 0)
    return handler.rfile.read(size) if size else b""


def _multipart(raw: bytes, content_type: str) -> tuple[str, bytes]:
    """The one uploaded file out of a form: its name and its bytes.

    Written by hand because the package that normally does this is one more
    install. Only the shape the screen actually sends is handled -- a single
    file field -- and anything else is refused out loud rather than half-read.
    An email that arrives empty extracts nothing, and the screen then shows a
    confident blank form as though the message said nothing at all.
    """
    marker = "boundary="
    if marker not in content_type:
        raise HTTPError(400, "That upload was not a form Ripple could read.")
    boundary = content_type.split(marker, 1)[1].strip().strip('"')
    sep = b"--" + boundary.encode()
    for part in raw.split(sep):
        head, _, body = part.partition(b"\r\n\r\n")
        if b"filename=" not in head:
            continue
        name = ""
        found = re.search(rb'filename="([^"]*)"', head)
        if found:
            name = unquote(found.group(1).decode("utf-8", "replace"))
        # Every part ends with the line break that introduces the next
        # boundary. Left on, it is two stray bytes on the end of the file.
        return name, body[:-2] if body.endswith(b"\r\n") else body
    raise HTTPError(400, "No file was found in that upload.")


def _call(fn, params: dict, query: dict, handler: BaseHTTPRequestHandler):
    """Hand the route function what it asked for, and nothing else."""
    import inspect                                            # noqa: PLC0415
    wanted = inspect.signature(fn).parameters
    args: dict = {}
    for name in wanted:
        if name in params:
            args[name] = params[name]
        elif name == "body":
            raw = _read_body(handler)
            args[name] = json.loads(raw or b"{}")
        elif name == "upload":
            args[name] = _multipart(_read_body(handler),
                                    handler.headers.get("Content-Type") or "")
        elif name in query:
            args[name] = query[name][0]
        else:
            args[name] = ""
    return fn(**args)


def make_handler(router: Router):
    class Handler(BaseHTTPRequestHandler):
        # The default writes a line to the console for every request, which on a
        # scan that polls progress every second buries anything worth reading.
        def log_message(self, *_args) -> None:
            return

        protocol_version = "HTTP/1.1"

        def _send(self, status: int, body: bytes, ctype: str, cache: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", cache)
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionAbortedError):
                # The page was closed or refreshed mid-request. Ordinary, and
                # not worth a stack trace in a window somebody is working in.
                pass

        def _json(self, status: int, payload) -> None:
            self._send(status, json.dumps(payload).encode("utf-8"),
                       "application/json", "no-store, must-revalidate")

        def _serve_file(self, file: Path) -> None:
            if not file.is_file():
                self._json(404, {"detail": "Not found."})
                return
            # The page and its script are never cached: during a demo that is
            # the difference between seeing a change and staring at yesterday's
            # page. Fonts are cached -- they never change and they are large.
            cache = ("public, max-age=2592000" if file.suffix == ".woff2"
                     else "no-store, must-revalidate")
            self._send(200, file.read_bytes(),
                       CONTENT_TYPES.get(file.suffix.lower(), "application/octet-stream"),
                       cache)

        def _handle(self, method: str) -> None:
            parsed = urlparse(self.path)
            path = unquote(parsed.path)
            try:
                if method == "GET" and router._static:
                    prefix, folder = router._static
                    if path.startswith(prefix + "/"):
                        wanted = (folder / path[len(prefix) + 1:]).resolve()
                        # Never serve outside the web folder, whatever the
                        # address asks for. ../../ in a URL is the oldest trick
                        # there is and this server is on somebody's own machine.
                        if folder.resolve() in wanted.parents or wanted == folder.resolve():
                            self._serve_file(wanted)
                        else:
                            self._json(404, {"detail": "Not found."})
                        return
                if method == "GET" and path == "/" and router._index:
                    self._serve_file(router._index)
                    return

                fn, params = router.find(method, path)
                if fn is None:
                    self._json(404, {"detail": f"{path} is not something Ripple answers."})
                    return
                out = _call(fn, params, parse_qs(parsed.query), self)
                self._json(200, out)
            except HTTPError as exc:
                self._json(exc.status_code, {"detail": exc.detail})
            except json.JSONDecodeError:
                self._json(400, {"detail": "That request was not readable JSON."})
            except Exception as exc:                          # noqa: BLE001
                # The message, not just the status. "Something went wrong: 500"
                # on screen tells nobody what to do next, and this window is the
                # whole product.
                traceback.print_exc()
                self._json(500, {"detail": f"{type(exc).__name__}: {exc}"})

        def do_GET(self) -> None:                             # noqa: N802
            self._handle("GET")

        def do_POST(self) -> None:                            # noqa: N802
            self._handle("POST")

        def do_PATCH(self) -> None:                           # noqa: N802
            self._handle("PATCH")

    return Handler


def free_port(first: int = 8000, last: int = 8020) -> int:
    """The first port in the range nothing else is holding.

    Fixing the port is fine until the day something else on the machine already
    has it, and then Ripple stops with a socket error that names no application
    and tells nobody what to close -- on the one machine where nobody can go and
    look.
    """
    for port in range(first, last + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise SystemExit(
        f"Every port from {first} to {last} is already in use on this machine. "
        f"Close whatever is using them and start Ripple again.")


def serve(router: Router, port: int) -> ThreadingHTTPServer:
    """Start answering, on a thread, and hand back the server so it can be
    stopped. Threaded because the screen asks what the scan is doing WHILE the
    scan is running, and a single-threaded server would answer that only once
    the scan it is asking about had finished."""
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(router))
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, name="ripple-web", daemon=True).start()
    return server
````

## Paste 19 of 25 — 3 files

### run.py

Create the file `run.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Start Ripple.

    python run.py

Nothing to install and nothing to configure first: the browser opens, and if no
repository folder has been chosen yet the first screen asks for one.

    python run.py --demo           point it at the pretend pipeline in mockrepo
    python run.py --no-browser     start it without opening a browser
    python run.py --check          prove it works and stop, printing what it found

This is the install-free build. It runs on Python's own library alone -- no
FastAPI, no uvicorn, no pydantic, nothing from the package site. The only thing
beside the standard library is the SQL parser, which is sitting in the sqlglot
folder next to this file as ordinary Python.
"""
from __future__ import annotations

import sys
import time
import traceback
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The parser and the code both have to be findable from wherever this was
# started, not from wherever the person happened to be standing.
sys.path.insert(0, str(HERE))

# Blocking the network is the first thing that happens, before any other part of
# Ripple is imported -- so anything that reaches out at import time is caught
# too, not just anything that reaches out during a request.
from ripple_offline import nonet                                    # noqa: E402

nonet.install()

from ripple_offline import lifecycle, paths, prefs                  # noqa: E402
from ripple_offline.webserver import free_port, serve               # noqa: E402


class _Stoppable:
    """What lifecycle stops when the Close button is pressed.

    It expects to set ``should_exit`` on something, because the packaged build
    hands it a uvicorn server. This is the same idea with nothing else in it, so
    the Close button and the "the page has gone" clock both work here exactly as
    they do there.
    """

    def __init__(self) -> None:
        self.should_exit = False


def _startup_report(values: dict, folder: dict, port: int) -> None:
    print("\n  Ripple")
    print(f"  repository : {values['repoPath'] or '(not chosen yet)'}")
    print(f"  folder     : {folder['message']}")
    print(f"  SQL read as: {values['sqlDialect'] or 'generic'}")
    print(f"  settings   : {paths.settings_file()}")
    print(f"  history    : {paths.history_file()}")
    print("  network    : blocked - loopback only")
    print(f"\n  open http://localhost:{port}\n")


def _self_check() -> int:
    """Prove the whole thing works, without a browser and without a person.

    Reads the folder, scans it, and prints what came back. This is what to run
    first on a machine you have just copied Ripple onto: if it prints a table
    name, everything underneath the screens is working, and anything wrong after
    that is the browser rather than Ripple.
    """
    from ripple_offline import app as service                       # noqa: PLC0415

    idx, parsed, cat = service.repo_state()
    print(f"  files read      : {len(idx.files)}")
    print(f"  statements read : {len(parsed.statements)}")
    print(f"  tables learned  : {len(cat.tables)}")
    if not idx.files:
        print("\n  No repository folder is chosen yet, so there was nothing to read.")
        print("  Start Ripple normally and choose one on the settings screen.")
        return 0
    table = next((t for t in cat.tables if cat.tables[t]), "")
    if not table:
        print("\n  Nothing readable was found in that folder.")
        return 1
    column = cat.tables[table][0]
    print(f"\n  scanning {table}.{column} ...")
    out = service.scan({"upstream": [{"table": table, "attrs": [column]}],
                        "changeKind": "removal"})
    print(f"  risk            : {out['risk']}")
    print(f"  published tables: {[g['prod'] for g in out['groups']] or 'none'}")
    print(f"  files with impact: {out['stats']['filesWithImpact']}")
    print("\n  Ripple works on this machine.\n")
    return 0


def _use_the_bundled_repo() -> None:
    """Point Ripple at the pretend pipeline that came with it.

    A settings file carries an absolute path, and a path from the machine this
    folder was assembled on means nothing on the machine it was carried to. So
    this copy ships with nothing chosen, and this works the folder out from
    where run.py actually is -- which is right wherever it has been put.
    """
    mockrepo = HERE / "mockrepo"
    if not mockrepo.is_dir():
        raise SystemExit(f"There is no mockrepo folder beside run.py ({mockrepo}).")
    prefs.apply(prefs.save({"repoPath": str(mockrepo), "repoLabel": "",
                            "sqlDialect": "bigquery", "maxHops": 4,
                            "prodTables": "_published"}))
    print(f"\n  Pointed at the pretend pipeline: {mockrepo}")
    print("  Change it on the settings screen when you want to scan real work.")


def main() -> int:
    try:
        values = prefs.load()
        prefs.apply(values)

        if "--demo" in sys.argv:
            _use_the_bundled_repo()
            values = prefs.load()

        from ripple_offline import app as service                   # noqa: PLC0415

        if "--check" in sys.argv:
            return _self_check()

        if not service.mount_web():
            print("The screens are missing. The web folder should sit beside run.py "
                  "and hold index.html, app.js and styles.css.")
            return 1

        port = free_port()
        folder = prefs.check_folder(values["repoPath"])
        _startup_report(values, folder, port)

        server = serve(service.router, port)
        if "--no-browser" not in sys.argv:
            try:
                webbrowser.open(f"http://localhost:{port}")
            except Exception:                                       # noqa: BLE001
                pass

        # Closing the browser used to leave this running where nobody could see
        # it, holding its own folder open so the folder could not be deleted.
        # The open page says it is there every few seconds, and when it stops
        # saying so, this stops.
        watched = _Stoppable()
        lifecycle.reset()
        lifecycle.attach(watched)
        lifecycle.watch()
        try:
            while not watched.should_exit:
                time.sleep(0.4)
        except KeyboardInterrupt:
            print("\n  Stopping.")
        server.shutdown()
        print("\n  Ripple has stopped. You can close the browser tab.\n")
        return 0
    except SystemExit:
        raise
    except Exception as exc:                                        # noqa: BLE001
        print(traceback.format_exc())
        print(f"\n  Ripple could not start: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
````

### tests/test_smoke.py

Create the file `tests/test_smoke.py` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````python
"""Does this copy of Ripple work on this machine?

    python -m unittest tests.test_smoke -v

Run from the folder holding run.py. unittest, not pytest, because pytest is one
more thing to install and the whole point of this copy is that nothing is.

These are not the product's tests -- those live with the product and there are
several hundred. These answer one question: has everything arrived, and does it
work here. Somebody who has just copied this folder onto a locked-down laptop
needs that answered in five seconds, and needs it answered by something other
than "the browser looks all right to me".
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))


class TheParserArrived(unittest.TestCase):
    """The one thing that could not be written by a chat and had to be copied."""

    def test_the_sql_parser_is_here_and_loads(self):
        import sqlglot
        self.assertTrue(sqlglot.__version__, "sqlglot loaded but has no version")

    def test_the_parser_folder_sits_beside_the_code(self):
        self.assertTrue((HERE / "sqlglot").is_dir(),
                        "the sqlglot folder is missing from beside run.py")

    def test_it_really_parses_sql(self):
        import sqlglot
        tree = sqlglot.parse_one("SELECT a, b AS c FROM t", read="bigquery")
        self.assertEqual([e.alias_or_name for e in tree.expressions], ["a", "c"])


class NothingNeedsInstalling(unittest.TestCase):
    """The reason this copy exists. If any of these is importable the copy has
    been assembled on the wrong machine, and it will fail on the locked-down one
    at the first request rather than here."""

    def test_the_web_layer_is_pythons_own(self):
        from ripple_offline import webserver
        self.assertTrue(hasattr(webserver, "Router"))

    def test_nothing_imports_fastapi(self):
        for name in ("fastapi", "uvicorn", "pydantic", "httpx"):
            with self.subTest(package=name):
                self.assertNotIn(name, sys.modules,
                                 f"{name} was imported - this copy is not install-free")


class TheEngineArrived(unittest.TestCase):
    def test_every_engine_file_is_here(self):
        for name in ("config", "production", "catalog", "narrative", "notification",
                     "progress", "store", "build_info"):
            with self.subTest(module=name):
                self.assertTrue((HERE / "ripple" / f"{name}.py").is_file())
        for name in ("repo", "templating", "rescue", "dialectcompat",
                     "sqlread", "lineage"):
            with self.subTest(module=name):
                self.assertTrue((HERE / "ripple" / "scanner" / f"{name}.py").is_file())

    def test_the_screens_are_here(self):
        for name in ("index.html", "app.js", "styles.css"):
            with self.subTest(file=name):
                self.assertTrue((HERE / "web" / name).is_file(),
                                f"web/{name} is missing - the screens will not draw")


class ItFollowsAColumn(unittest.TestCase):
    """The whole product, end to end, on a repository written here and thrown
    away. If this passes, everything under the screens works on this machine."""

    def test_a_renamed_column_is_followed_to_the_published_table(self):
        from ripple.config import Settings
        from ripple.scanner.lineage import trace
        from ripple.scanner.repo import RepoIndex
        from ripple.scanner.sqlread import parse_repo

        files = {
            "a.sql": "CREATE OR REPLACE TABLE stage_one AS\n"
                     "SELECT id, cm13 AS customer_code FROM customer_demographics;",
            "b.sql": "CREATE OR REPLACE TABLE final_published AS\n"
                     "SELECT id, customer_code FROM stage_one\n"
                     "WHERE customer_code IS NOT NULL;",
        }
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, body in files.items():
                (root / name).write_text(body, encoding="utf-8")
            cfg = Settings()
            cfg.repo_path = root
            cfg.sql_dialect = "bigquery"
            cfg.set_production("_published")
            idx = RepoIndex.build(root, cfg)
            parsed = parse_repo(idx, cfg)
            out = trace(idx, parsed,
                        [{"table": "customer_demographics", "attrs": ["cm13"]}],
                        change_type="removal", cfg=cfg).to_dict()

        self.assertEqual([g["prod"] for g in out["groups"]], ["final_published"],
                         "the rename was not followed to the published table")
        self.assertNotEqual(out["risk"], "none")
        self.assertEqual(out["stats"]["couldNotRead"], 0, out["unreadable"])

    def test_it_refuses_to_say_no_impact_over_a_file_it_could_not_read(self):
        """The rule the whole tool rests on. "I found nothing" and "I could not
        look" are different answers, and printed the same the second one is a
        lie that reads as a promise."""
        from ripple.config import Settings
        from ripple.scanner.lineage import trace
        from ripple.scanner.repo import RepoIndex
        from ripple.scanner.sqlread import parse_repo

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "fine.sql").write_text(
                "CREATE OR REPLACE TABLE t AS SELECT zz FROM elsewhere;", encoding="utf-8")
            (root / "broken.sql").write_text(
                "THIS IS NOT SQL cm13 customer_demographics {{{", encoding="utf-8")
            cfg = Settings()
            cfg.repo_path = root
            cfg.sql_dialect = "bigquery"
            cfg.set_production("_published")
            idx = RepoIndex.build(root, cfg)
            parsed = parse_repo(idx, cfg)
            out = trace(idx, parsed,
                        [{"table": "customer_demographics", "attrs": ["cm13"]}],
                        change_type="removal", cfg=cfg).to_dict()

        self.assertNotEqual(out["risk"], "none",
                            'risk read "none" over a file that could not be read')
        self.assertFalse(out["coverage"]["complete"])


class TheServiceAnswers(unittest.TestCase):
    """The routes the screens call, without starting a browser."""

    def test_health_carries_everything_the_screen_reads(self):
        from ripple_offline import app as service
        out = service.health()
        for key in ("ok", "build", "repo", "catalog", "sqlDialect", "maxHops",
                    "production", "productionSet", "offline", "folder", "dialects"):
            with self.subTest(key=key):
                self.assertIn(key, out, f"the screen reads {key} and it is missing")
        for key in ("files", "statements", "unreadable", "kinds", "unknownExt",
                    "heldOnline", "inSkippedDirs"):
            with self.subTest(repo_key=key):
                self.assertIn(key, out["repo"])

    def test_the_settings_file_sits_beside_ripple(self):
        from ripple_offline import paths
        self.assertEqual(paths.settings_file().parent, paths.app_dir())

    def test_a_scan_with_no_tables_is_refused_with_a_sentence(self):
        from ripple_offline import app as service
        from ripple_offline.webserver import HTTPError
        with self.assertRaises(HTTPError) as caught:
            service.scan({"upstream": []})
        self.assertIn("upstream", str(caught.exception).lower())


class ItCannotReachTheNetwork(unittest.TestCase):
    def test_the_outbound_guard_is_installed_when_ripple_starts(self):
        from ripple_offline import nonet
        nonet.install()
        self.assertTrue(nonet.installed())


if __name__ == "__main__":
    unittest.main(verbosity=2)
````

### web/index.html

Create the file `web/index.html` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````html
<!-- GENERATED — do not edit. Built from Codebase/web/index.html. -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ripple Offline — upstream change impact analysis</title>
<link rel="stylesheet" href="/static/fonts/fonts.css">
<link rel="stylesheet" href="/static/styles.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='44' fill='none' stroke='%23006FCF' stroke-width='8' opacity='.4'/><circle cx='50' cy='50' r='28' fill='none' stroke='%23006FCF' stroke-width='8' opacity='.75'/><circle cx='50' cy='50' r='13' fill='%2300175A'/></svg>">
</head>
<body>

<nav class="side">
  <div class="brand">
    <span class="mark"><i></i><i></i><i></i><i class="pip"></i></span>
    <div class="btext"><b>Ripple</b><span>Upstream change impact analysis</span></div>
  </div>
  <div class="sep"></div>
  <div class="steps" id="steps"></div>
  <div class="sep mid"></div>
  <div class="navs">
    <button class="navbtn" id="navHistory">Past analyses</button>
    <button class="navbtn" id="navSettings">Settings &amp; checks</button>
  </div>
  <div class="status" id="status"></div>
</nav>

<div class="main">
  <header>
    <div><h1 id="hTitle">Notification</h1><p id="hSub">Step 1 of 7</p></div>
    <div style="margin-left:auto" id="hRight"></div>
  </header>
  <div class="scroll"><div class="wrap" id="view"></div></div>
</div>

<!-- ══════════════ step 1 ══════════════ -->
<template id="t-step1">
  <div class="head">
    <div><h2 data-x="title">New impact notification</h2><p data-x="sub"></p></div>
    <div class="right">
      <span class="lbl faint">Input mode</span>
      <button class="pill" data-mode="email">From email</button>
      <button class="pill" data-mode="manual">Enter manually</button>
    </div>
  </div>

  <!-- email -->
  <div data-x="emailMode">
    <div class="grid2">
      <div>
        <div class="drop" id="drop">
          <b>Drop the notification here</b>
          <span class="muted small">Outlook <span class="mono">.msg</span>, <span class="mono">.eml</span> or a plain text file — or click to choose</span>
          <input type="file" id="file" accept=".msg,.eml,.txt" hidden>
        </div>
        <div class="small muted" style="margin-top:16px;line-height:1.55">
          No file? Use <b>Enter manually</b> above.
        </div>
      </div>
      <div class="rail">
        <div class="card pad" data-x="does"></div>
        <div class="note info" data-x="confirm"></div>
      </div>
    </div>
  </div>

  <!-- manual -->
  <div data-x="manualMode" class="hide">
    <div class="grid2">
      <div class="card clip">
        <div class="chead">
          <b>Upstream tables &amp; attributes</b>
          <span class="badge grey" style="margin-left:auto" data-x="manCount"></span>
        </div>
        <div data-x="manRows"></div>
        <div class="pad" style="border-top:1px solid var(--hair);display:flex;align-items:center;gap:12px">
          <button class="ghost sm" data-x="addRow">+ Add another table</button>
          <span class="small faint">Add every table named in the notice.</span>
        </div>
      </div>
      <div class="rail">
        <div class="card pad">
          <span class="lbl">Change details — all optional</span>
          <div data-x="manFields"></div>
        </div>
        <div class="note good" data-x="noAi"></div>
      </div>
    </div>
    <div class="card pad lg foot" style="margin-top:24px">
      <button class="pri" data-x="manStart">Continue to repository</button>
      <button class="ghost" data-x="manDemo">Fill with an example</button>
      <span class="small faint" data-x="manHint"></span>
    </div>
  </div>
</template>

<!-- ══════════════ step 2 ══════════════ -->
<template id="t-step2">
  <div class="head">
    <div><h2 data-x="title"></h2><p data-x="sub"></p></div>
    <div class="right"><span class="muted" style="font-size:13px;font-weight:600" data-x="by"></span></div>
  </div>
  <div data-x="warnings"></div>
  <div class="metagrid" data-x="meta"></div>
  <div class="card pad lg">
    <span class="lbl">Subject &amp; what is changing</span>
    <div class="field"><input type="text" data-x="subject"></div>
    <div class="field"><textarea rows="2" data-x="desc"></textarea></div>
  </div>
  <div class="card clip" style="margin-top:16px">
    <div class="chead">
      <span class="lbl">Upstream tables &amp; mapped attributes</span>
      <span class="badge grey" style="margin-left:auto" data-x="count"></span>
    </div>
    <div data-x="rows"></div>
    <div class="pad" style="border-top:1px solid var(--hair)">
      <button class="ghost sm" data-x="addRow">+ Add another table</button>
    </div>
  </div>
  <div class="foot"><button class="pri" data-x="next">Continue to repository</button></div>
</template>

<!-- ══════════════ step 3 ══════════════ -->
<template id="t-step3">
  <div class="head">
    <div><h2 data-x="title">Connected repository</h2><p data-x="sub"></p></div>
  </div>
  <div data-x="alert"></div>
  <div class="grid2 even">
    <div data-x="left"></div>
    <!-- The confirmation of what is about to be scanned comes first. It used to
         sit under the list of file types, which is a detail about the same
         thing read after the decision it informs. -->
    <div class="rail">
      <div data-x="ready"></div>
      <div class="card pad" data-x="kinds"></div>
      <div class="card pad"><span class="lbl">What was understood</span><div data-x="cat"></div></div>
      <div data-x="gaps"></div>
    </div>
  </div>
  <div class="foot"><button class="pri" data-x="next">Run impact analysis</button>
    <button class="ghost" data-x="reindex">Re-read the repository</button>
    <span class="small faint" data-x="hint"></span></div>
</template>

<!-- ══════════════ step 4 ══════════════ -->
<template id="t-step4">
  <div class="head"><div><h2>Impact analysis</h2>
    <p data-x="sub"></p></div>
    <div class="right" data-x="risk"></div></div>
  <div data-x="progress"></div>
  <div class="statgroups" data-x="stats"></div>
  <div class="groups" data-x="groups"></div>
  <div data-x="gaps"></div>
  <div class="foot"><button class="pri" data-x="next">Continue to dependency map</button></div>
</template>

<!-- ══════════════ step 5 ══════════════ -->
<template id="t-step5">
  <div class="head"><div><h2>Dependency map</h2>
    <p data-x="sub">Where the changed attribute travels, and what it is called at each step.</p></div></div>
  <div data-x="tabs" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:18px"></div>
  <div data-x="map"></div>
  <div class="foot"><button class="pri" data-x="next">Continue to summary</button></div>
</template>

<!-- ══════════════ step 6 ══════════════ -->
<template id="t-step6">
  <div class="head"><div><h2>Summary</h2><p data-x="sub"></p></div></div>
  <div data-x="body"></div>
  <div class="foot"><button class="pri" data-x="next">Continue to reply</button>
    <button class="ghost" data-x="save">Save to history</button>
    <span class="small faint" data-x="saved"></span></div>
</template>

<!-- ══════════════ step 7 ══════════════ -->
<template id="t-step7">
  <div class="head"><div><h2>Reply to the upstream team</h2>
    <p>Drafted from the findings. Edit it, then copy it into Outlook.</p></div></div>
  <div class="grid2">
    <div class="card clip">
      <div class="chead" data-x="to"></div>
      <div class="chead" style="background:#fff">
        <span class="small" style="font-weight:700;color:var(--mute);flex-shrink:0">Subject</span>
        <input type="text" class="bare" data-x="subject">
      </div>
      <textarea class="bare" rows="15" data-x="body"
        style="display:block;padding:18px 22px;font-size:14px;line-height:1.65"></textarea>
      <div class="chead" style="border-bottom:none;border-top:1px solid var(--line3)">
        <button class="pri" data-x="copy">Copy reply</button>
        <button class="ghost" data-x="restart">Start a new analysis</button>
        <span class="small faint" data-x="copied"></span>
      </div>
    </div>
    <div class="card clip">
      <div class="chead"><b>Next actions</b><span data-x="risk" style="margin-left:auto"></span></div>
      <div class="pad"><ol class="acts" data-x="acts" style="margin-top:0"></ol></div>
      <div data-x="deadline" style="margin:0 20px 20px"></div>
    </div>
  </div>
</template>

<script src="/static/app.js"></script>
</body>
</html>
````

## Paste 20 of 25

### web/styles.css

Create the file `web/styles.css` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````css
/* Ripple — visual design.
   Every colour, size, radius and spacing value here is taken from the finished
   prototype (Prototype/Ripple Prototype.html) so the built app and the design
   are the same product. Fonts are served from /static/fonts — no CDN, works
   offline. */

:root{
  /* brand */
  --navy:#00175A; --blue:#006FCF; --blued:#005CAD; --pale:#E3F0FC;
  /* structure */
  --line:#DCE4EE;   /* card borders                */
  --line2:#C7D4E4;  /* input borders               */
  --line3:#E7EDF5;  /* dividers inside a card      */
  --hair:#F0F4F9;   /* row separators              */
  --bg:#F2F5F9; --card:#fff; --tint:#FAFCFE;
  /* type */
  --ink:#10243E;    /* headings, strong text       */
  --body:#33445E;   /* paragraphs                  */
  --mute:#5C6C84;   /* card labels, secondary text */
  --faint:#8595AB;  /* field labels, hints         */
  /* neutral chip */
  --chip:#EDF2F8; --chipink:#45566E;
  /* status */
  --red:#B01C2E; --redbg:#FDE8E8; --redln:#F3C4C4;
  --amber:#8A6100; --amberbg:#FFF4D9; --amberln:#EFDFAF;
  --green:#006B40; --greenbg:#E4F5EC; --greenln:#BFE5CE;
  --violet:#6D4B9E; --violetbg:#F0EAFA; --violetln:#D8C9EF;
  /* code */
  --codebg:#FBFCFE; --codehead:#0B1F45; --codenum:#93A3B8;
  --hit:#FFF7E1; --hitln:#F0DFAE; --hitbar:#E3A008; --hitpill:#FFF1CC;

  --mono:'IBM Plex Mono',"Consolas","Cascadia Mono",ui-monospace,monospace;
  --shadow:0 1px 2px rgba(16,36,62,.06);
}
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:'Public Sans',-apple-system,"Segoe UI",system-ui,Helvetica,Arial,sans-serif;
  background:var(--bg); color:var(--ink); font-size:14px; line-height:1.5;
  display:flex; height:100vh; overflow:hidden;
  -webkit-font-smoothing:antialiased;
}
button{font-family:inherit;white-space:nowrap}
a{color:var(--blue);text-decoration:none}
a:hover{color:var(--navy);text-decoration:underline}
::selection{background:#CBE2F7}
.mono{font-family:var(--mono)}
.hide{display:none !important}
@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
@keyframes ripple{0%{transform:scale(.55);opacity:.9}70%{opacity:0}100%{transform:scale(1.5);opacity:0}}

/* ── sidebar ─────────────────────────────────────────── */
.side{width:288px;flex-shrink:0;background:var(--navy);color:#fff;display:flex;flex-direction:column;overflow-y:auto}
.brand{display:flex;align-items:center;gap:13px;padding:22px 20px 18px}
.mark{width:40px;height:40px;border-radius:11px;background:var(--blue);flex-shrink:0;position:relative;
  overflow:hidden;display:flex;align-items:center;justify-content:center}
.mark i{position:absolute;width:30px;height:30px;border:2px solid rgba(255,255,255,.5);border-radius:50%;
  animation:ripple 2.6s ease-out infinite}
.mark i:nth-child(2){animation-delay:.85s}
.mark i:nth-child(3){animation-delay:1.7s}
.mark i.pip{position:relative;width:8px;height:8px;border:none;background:#fff;animation:none}
/* scoped to .btext so these never reach the mark's own elements */
.brand .btext b{font-size:19px;font-weight:800;letter-spacing:-.01em;display:block;line-height:1.1}
.brand .btext span{font-size:11.5px;color:rgba(255,255,255,.55);display:block;margin-top:1px}
.sep{height:1px;background:rgba(255,255,255,.12);margin:0 20px 14px}
.sep.mid{margin:16px 20px 12px}

.steps,.navs{display:flex;flex-direction:column;gap:2px;padding:0 12px}
.step{display:flex;align-items:center;gap:12px;padding:9px 12px;border-radius:8px;cursor:pointer;
  border:none;background:none;text-align:left;width:100%}
.step:disabled{cursor:default}
.step .n{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:700;flex-shrink:0;box-sizing:border-box;
  background:transparent;border:1px solid rgba(255,255,255,.35);color:rgba(255,255,255,.6)}
.step.done .n{background:rgba(255,255,255,.22);border-color:transparent;color:#fff}
.step.on{background:rgba(255,255,255,.13)}
.step.on .n{background:#fff;border-color:#fff;color:var(--navy)}
.step .t{display:block;font-size:13.5px;font-weight:600;color:rgba(255,255,255,.7);line-height:1.25}
.step:disabled .t{color:rgba(255,255,255,.42)}
.step.done .t{color:rgba(255,255,255,.85)}
.step.on .t{color:#fff}
.step .s{display:block;font-size:11px;color:rgba(255,255,255,.38);margin-top:1px;line-height:1.3}
.step.on .s{color:rgba(255,255,255,.6)}

.navbtn{display:block;width:100%;text-align:left;padding:10px 12px;border-radius:8px;border:none;
  background:none;color:rgba(255,255,255,.7);font-size:13.5px;font-weight:600;cursor:pointer}
.navbtn.on{background:rgba(255,255,255,.13);color:#fff}
.status{margin-top:auto;padding:18px 20px;font-size:12px;color:rgba(255,255,255,.65)}
.status .srow{display:flex;align-items:center;gap:9px;padding:3px 0}
.dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.dot.ok{background:#2EBD6B}.dot.warn{background:#F0B429}.dot.off{background:#7A8AA6}

/* ── main ────────────────────────────────────────────── */
.main{flex:1;display:flex;flex-direction:column;min-width:0}
header{background:#fff;border-bottom:1px solid var(--line);padding:14px 32px;display:flex;
  align-items:center;gap:20px;flex-shrink:0}
header h1{font-size:15px;font-weight:700}
header p{font-size:12px;color:var(--mute)}
.scroll{flex:1;overflow-y:auto}
.wrap{max-width:1200px;margin:0 auto;padding:30px 36px 60px}
.head{margin-bottom:20px;display:flex;align-items:flex-end;gap:16px}
.head h2{font-size:22px;font-weight:800}
.head p{font-size:14px;color:var(--mute);margin-top:4px}
.head .right{margin-left:auto;display:flex;align-items:center;gap:10px}

.card{background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow)}
.card.flat{box-shadow:none}
.card.clip{overflow:hidden}
.pad{padding:18px 20px}
.pad.lg{padding:22px 26px}
/* the tinted strip that heads a card */
.chead{padding:15px 22px;border-bottom:1px solid var(--line3);display:flex;align-items:center;
  gap:12px;background:var(--tint)}
.chead b{font-size:14px;font-weight:700}
.grid2{display:grid;grid-template-columns:1.55fr 1fr;gap:24px;align-items:start}
.grid2.even{grid-template-columns:1.5fr 1fr}
.rail{display:flex;flex-direction:column;gap:16px}

.lbl{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--mute)}
.lbl.faint{font-size:10.5px;letter-spacing:.07em;color:var(--faint)}
.muted{color:var(--mute)}
.faint{color:var(--faint)}
.small{font-size:12.5px}
.prose{font-size:13.5px;line-height:1.6;color:var(--body)}

/* ── buttons ─────────────────────────────────────────── */
button.pri{border:none;background:var(--blue);color:#fff;font-size:14px;font-weight:700;
  padding:12px 24px;border-radius:8px;cursor:pointer;transition:background .15s}
button.pri:hover{background:var(--blued)}
button.pri:disabled{background:#B9C9DD;cursor:default}
button.ghost{border:1px solid var(--line2);background:#fff;color:var(--blued);font-size:14px;
  font-weight:700;padding:11px 22px;border-radius:8px;cursor:pointer;transition:border-color .15s}
button.ghost:hover{border-color:var(--blue)}
button.sm{font-size:12.5px;padding:7px 18px;border-radius:7px}
button.link{border:none;background:none;color:var(--blued);font-weight:700;font-size:12.5px;
  cursor:pointer;text-decoration:underline}
button.danger{border:1px solid #E7D0D0;background:#fff;color:var(--red);font-size:12px;font-weight:700;
  padding:8px 14px;border-radius:7px;cursor:pointer;flex-shrink:0}
.pill{font-size:12px;font-weight:700;padding:7px 14px;border-radius:999px;cursor:pointer;
  background:#fff;color:var(--chipink);border:1px solid var(--line2);transition:all .15s}
.pill.on{background:var(--navy);color:#fff;border-color:var(--navy)}
/* the attribute tabs on the dependency map — two lines inside one pill */
.pill.tab{display:flex;flex-direction:column;align-items:flex-start;gap:3px;font-size:13px;
  padding:9px 16px;border-radius:9px;color:var(--ink)}
.pill.tab .sub{font-family:var(--mono);font-size:10.5px;font-weight:500;color:var(--faint)}
.pill.tab.on{color:#fff}
.pill.tab.on .sub{color:rgba(255,255,255,.6)}

/* ── inputs ──────────────────────────────────────────── */
input[type=text],input[type=date],input[type=password],textarea,select{
  width:100%;border:1px solid var(--line2);border-radius:7px;padding:8px 11px;
  font-family:inherit;font-size:14px;font-weight:600;color:var(--ink);
  outline-color:var(--blue);background:#fff;
}
textarea{resize:vertical;line-height:1.55;font-size:13.5px;font-weight:400;color:var(--body);padding:9px 11px}
select{font-weight:600}
input.mono{font-family:var(--mono);font-size:13px;font-weight:600;color:var(--blued)}
/* a hint must never look like a value that is already filled in */
input::placeholder,textarea::placeholder{color:var(--faint);font-weight:400;opacity:1}
.field{margin-top:12px}
.field>.lbl{display:block;margin-bottom:6px}
/* borderless input, used where the card itself is the frame (the reply) */
input.bare,textarea.bare{border:none;outline:none;background:transparent;padding:0}

/* ── badges & chips ──────────────────────────────────── */
.badge{display:inline-block;font-size:12px;font-weight:700;padding:5px 14px;border-radius:999px;white-space:nowrap}
.badge.blue{background:var(--pale);color:var(--blued);border:1px solid #9CC4EA}
.badge.red{background:var(--redbg);color:var(--red);border:1px solid var(--redln)}
.badge.amber{background:var(--amberbg);color:var(--amber);border:1px solid var(--amberln)}
.badge.green{background:var(--greenbg);color:var(--green);border:1px solid var(--greenln)}
.badge.grey{background:var(--chip);color:var(--chipink);font-size:11.5px;padding:4px 11px}
.badge.violet{background:var(--violetbg);color:var(--violet)}
/* small badges are chips, not status pills — no ring */
.badge.sm{font-size:11.5px;padding:4px 11px;border:none}
/* the small upper-case tag that names what a row is */
.tag{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  padding:4px 10px;border-radius:999px;flex-shrink:0;background:var(--redbg);color:var(--red)}
.tag.blue{background:var(--pale);color:var(--blued)}
.tag.green{background:var(--greenbg);color:var(--green)}
/* soft square chips */
.chip{display:inline-block;font-size:12px;font-weight:600;background:var(--chip);color:var(--chipink);
  padding:5px 12px;border-radius:999px}
.chip.attr{font-family:var(--mono);font-size:12.5px;font-weight:500;background:var(--pale);
  color:var(--blued);border-radius:6px;padding:5px 11px}
.chip.alias{font-family:var(--mono);font-size:12px;font-weight:600;background:var(--violetbg);
  color:var(--violet);border-radius:6px;padding:4px 10px}
.chip.mono{font-family:var(--mono);font-size:13px;font-weight:600;border-radius:6px;padding:5px 12px}
/* A pattern is not a table name, and on a screen full of both that difference
   is the whole point — so it is outlined rather than filled. */
.chip.pattern{background:#fff;color:var(--violet);border:1px dashed var(--violetln)}
.chips{display:flex;flex-wrap:wrap;gap:7px}
/* A real table name is long, and a real list of them is hundreds. Both have to
   stay inside the card rather than pushing the page sideways. */
.chip{max-width:100%;overflow-wrap:anywhere}
.scrollbox{max-height:200px;overflow-y:auto;padding:10px 12px;background:var(--tint);
  border:1px solid var(--line3);border-radius:8px;align-content:flex-start}

/* A label/value row inside a settings card. The value is the long one — a
   Windows path, or a list of published tables — so it gets the room and wraps
   inside the card instead of pushing the card wider than the screen. */
.factrow{display:flex;gap:14px;padding:9px 0;border-top:1px solid var(--hair);align-items:baseline}
.factrow>:first-child{flex:0 1 auto;min-width:0}
.factrow>:last-child{flex:1 1 auto;min-width:0;text-align:right;font-weight:700;overflow-wrap:anywhere}

/* ── the information button ──────────────────────────── */
/* One disclosure control for the whole app. The fact stays on the page; the
   reasoning opens underneath it, in the normal flow, so it is never clipped by
   a card with overflow:hidden and needs no positioning maths at any width.

   A real button, never a title= tooltip: a tooltip cannot be opened on a touch
   screen, cannot be reached from a keyboard, and vanishes while it is being
   read. Nothing here is downloaded, so it works with no internet. */
/* Not a flex row. In a flex row a fact that wraps onto two lines pushes the
   button onto a third line of its own, where it reads as a control that failed
   to load. As an inline-block it simply follows the last word, at any width. */
.iwrap{display:block}
.ifact{display:block}
button.i{width:19px;height:19px;flex-shrink:0;border-radius:50%;border:1px solid var(--line2);
  background:#fff;color:var(--mute);font-family:inherit;font-size:11.5px;font-weight:800;
  line-height:1;cursor:pointer;padding:0;transition:all .13s;
  display:inline-block;vertical-align:baseline;margin-left:7px;position:relative;top:1px}
button.i:hover{border-color:var(--blue);color:var(--blued);background:var(--pale)}
button.i:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
button.i[aria-expanded="true"]{background:var(--navy);border-color:var(--navy);color:#fff}
.ipanel{margin-top:10px;padding:12px 16px;border-left:3px solid var(--line2);
  background:var(--tint);border-radius:0 8px 8px 0;font-size:13px;line-height:1.6;
  color:var(--body);animation:fadeUp .18s ease}
.ipanel p+p{margin-top:8px}
/* a card label is a heading; the fact under it needs the same air as any other */
.lbl+.iwrap{margin-top:8px}

/* ── notes ───────────────────────────────────────────── */
.note{border-radius:10px;padding:14px 18px;font-size:13.5px;line-height:1.55}
.note.info{background:#F4F9FE;border:1px solid #C9E0F5;color:var(--body)}
.note.info b{color:var(--blued)}
.note.warn{background:var(--hit);border:1px solid var(--hitln);color:var(--body)}
.note.warn b{color:var(--amber)}
.note.good{background:var(--greenbg);border:1px solid var(--greenln);color:var(--body)}
.note.good b{color:var(--green)}
.note.bad{background:var(--redbg);border:1px solid var(--redln);color:var(--body)}
.note.bad b{color:var(--red)}

/* drop zone */
.drop{border:2px dashed var(--line2);border-radius:12px;padding:34px;text-align:center;
  background:#fff;cursor:pointer;transition:all .15s}
.drop:hover{border-color:#9CC4EA;background:var(--tint)}
.drop.over{border-color:var(--blue);background:var(--pale)}
.drop b{display:block;font-size:15px;margin-bottom:5px}

/* ── stat cards ──────────────────────────────────────── */
/* Every row of stat cards is the same grid, so a card is the same size wherever
   it sits. Rows with their own column count looked wrong twice over: a row of
   two cards stretched each one to half the page while the row above held five
   narrow ones, and a row of one stranded it. Cards now fill from the left and a
   short row simply leaves the rest of the row empty. */
.statgroups{margin:22px 0}
.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;align-items:start}
@media (max-width:1499px){.stats{grid-template-columns:repeat(3,1fr)}}
@media (max-width:900px){.stats{grid-template-columns:repeat(2,1fr)}}
/* the four editable fields at the top of step 2 — same card, no reserved label row.
   align-items:start is load-bearing: the contact card carries one chip per email
   address, and without it the other three stretched to match and sat with 250px
   of white space under a single input. */
.metagrid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:16px;
  align-items:start}
@media (max-width:1100px){.metagrid{grid-template-columns:repeat(2,1fr)}}
.metagrid .stat>.lbl{min-height:0}
.stat{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px 18px;
  box-shadow:0 1px 2px rgba(16,36,62,.05);animation:fadeUp .3s ease}
.stat>.lbl{display:block;line-height:1.35;min-height:30px;letter-spacing:.07em}
.stat .v{font-size:26px;font-weight:800;margin-top:6px;font-variant-numeric:tabular-nums}
.stat .s{font-size:12px;color:var(--faint);margin-top:3px}

/* ── findings, grouped by production table ───────────── */
.groups{display:flex;flex-direction:column;gap:16px;margin-top:20px}
.group{overflow:hidden;animation:fadeUp .3s ease}
.ghead{display:flex;align-items:center;gap:14px;padding:16px 22px;cursor:pointer;flex-wrap:wrap}
.ghead:hover{background:var(--tint)}
.ghead.open{background:var(--tint)}
.ghead .caret{margin-left:auto;color:var(--faint);font-size:22px;font-weight:700;transition:transform .18s}
.ghead.open .caret{transform:rotate(90deg)}
.rowhead,.row{display:grid;grid-template-columns:1.1fr 1fr .8fr .8fr .7fr 26px;gap:0 16px;align-items:center}
/* Real table names run to forty characters and real paths to a hundred and
   sixty. Without this a single long one widens the grid until the page itself
   scrolls sideways and the findings walk off the right of the screen. */
.rowhead>*,.row>*{min-width:0;overflow-wrap:anywhere}
.ghead .mono{min-width:0;overflow-wrap:anywhere}
.rowhead{padding:11px 22px;background:var(--tint);border-top:1px solid var(--line3);
  border-bottom:1px solid var(--line3)}
.rowhead span{font-size:10.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--faint)}
.row{padding:14px 22px;border-top:1px solid var(--hair);cursor:pointer}
.row:hover{background:var(--tint)}
.row.open{background:#F4F9FE}
.row .caret{color:var(--faint);font-size:20px;font-weight:700;text-align:center;transition:transform .18s}
.row.open .caret{transform:rotate(90deg)}
.detail{padding:0 22px 20px;animation:fadeUp .25s ease}

/* ── the code snippet ────────────────────────────────── */
.code{border:1px solid var(--line);border-radius:10px;overflow:hidden;margin-top:14px}
.code .f{display:flex;align-items:center;gap:12px;padding:10px 18px;background:var(--codehead);color:#fff}
.code .f .name{font-family:var(--mono);font-size:13px;min-width:0;overflow-wrap:anywhere}
.code .f .lang{font-size:10.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  background:rgba(255,255,255,.15);padding:3px 9px;border-radius:999px}
.code .f a{margin-left:auto;font-size:12.5px;font-weight:700;color:#8FC6F5;white-space:nowrap}
.code .f a:hover{color:#fff;text-decoration:underline}
.code .body{font-family:var(--mono);font-size:13px;line-height:1.75;padding:10px 0;background:var(--codebg)}
.code .ln{display:flex;align-items:baseline;min-height:24px}
.code .ln .n{width:52px;flex-shrink:0;color:var(--codenum);text-align:right;padding-right:18px;user-select:none}
.code .ln .t{white-space:pre;overflow-x:auto;color:var(--ink)}
.code .ln.hit{background:var(--hit);box-shadow:inset 3px 0 0 var(--hitbar)}
/* the "why it matched" tag rides on the line itself — set in the UI face, not
   the code face, so it reads as annotation rather than as code */
.code .ln .why{margin-left:auto;margin-right:16px;align-self:center;font-size:11px;font-weight:700;
  font-family:'Public Sans',-apple-system,"Segoe UI",system-ui,sans-serif;
  color:var(--amber);background:var(--hitpill);padding:2px 10px;border-radius:999px;white-space:nowrap}

/* ── dependency map ──────────────────────────────────── */
.maprow{display:flex;gap:26px;align-items:flex-start}
/* The source box sticks to the top of the branches rather than being centred
   against them. Twenty real branches are several thousand pixels tall, so
   centred put the one box that says WHAT is being followed halfway down a page
   nobody had scrolled to, leaving the left of the picture empty. */
.mapsrc{width:250px;flex-shrink:0;position:sticky;top:12px}
.mapsrc>div{background:var(--navy);color:#fff;border-radius:10px;padding:16px 18px;width:100%}
.mapsrc .k{font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:rgba(255,255,255,.55)}
.mapsrc .tb{font-family:var(--mono);font-size:14px;font-weight:600;margin-top:6px}
.mapsrc .at{font-family:var(--mono);font-size:13.5px;font-weight:600;color:#8FC6F5;margin-top:10px}
.mapsrc .ct{font-size:12px;color:rgba(255,255,255,.6);margin-top:8px;line-height:1.5}
.branches{flex:1;min-width:0;display:flex;flex-direction:column;gap:14px}
/* A chain scrolls sideways inside its own row rather than wrapping. Measured at
   a 1,180px window: wrapping put every box on a line of its own and left the
   arrows stranded at the right-hand edge, so a picture of a chain read as a
   list of unconnected boxes. The page itself still never scrolls sideways. */
.branch{display:flex;align-items:center;gap:10px;flex-wrap:nowrap;overflow-x:auto;
  padding:14px 16px;border:1px solid var(--line);border-radius:10px;background:var(--codebg)}
/* The scrollbar IS the affordance. Left as the browser's overlay it appears
   only once somebody happens to scroll, so a chain that continues past the edge
   looks like a chain that was cut off. */
.branch{scrollbar-width:thin;scrollbar-color:var(--line2) transparent}
.branch::-webkit-scrollbar{height:8px}
.branch::-webkit-scrollbar-thumb{background:var(--line2);border-radius:4px}
.branch::-webkit-scrollbar-track{background:transparent}
.node{border-radius:9px;padding:11px 14px;background:#F4F9FE;border:1px solid #9CC4EA;
  flex-shrink:0;max-width:360px}
.node .nm{overflow-wrap:anywhere}
/* Below this the source box takes 250px the chain needs more. It goes above
   instead, which is the same reading order and gives the branches the width. */
@media (max-width:1240px){
  .maprow{flex-direction:column}
  .mapsrc{width:100%;position:static}
}
.node.prod{background:var(--redbg);border-color:var(--redln)}
.node .top{display:flex;align-items:center;gap:8px}
.node .k{font-size:10px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  color:var(--chipink);background:var(--chip);padding:3px 8px;border-radius:999px}
.node .nm{font-family:var(--mono);font-size:13px;font-weight:600;color:var(--ink)}
.node .al{margin-top:7px;display:flex;align-items:center;gap:6px}
.node .al span{font-size:10.5px;font-weight:700;color:var(--faint)}
.arrow{color:var(--faint);font-weight:700;font-size:16px}
.legend{display:flex;align-items:center;gap:20px;margin-top:16px;font-size:12.5px;color:var(--mute);flex-wrap:wrap}
.legend div{display:flex;align-items:center;gap:9px}
.legend i{width:14px;height:14px;border-radius:4px;display:block}

/* ── lists ───────────────────────────────────────────── */
ul.ticks{list-style:none;display:flex;flex-direction:column;gap:10px;margin-top:12px}
ul.ticks li{display:flex;gap:11px;font-size:13.5px;line-height:1.6;color:var(--ink)}
ul.ticks li::before{content:"•";color:var(--blue);font-weight:700;flex-shrink:0}
ol.nums{list-style:none;counter-reset:a;display:flex;flex-direction:column;gap:10px;margin-top:12px}
ol.nums li{counter-increment:a;display:flex;gap:10px;font-size:13.5px;line-height:1.5;color:var(--body)}
ol.nums li::before{content:counter(a);color:var(--blue);font-weight:700;flex-shrink:0}
ol.acts{list-style:none;display:flex;flex-direction:column;gap:11px;margin-top:12px}
ol.acts li{display:flex;gap:11px;font-size:13.5px;line-height:1.55;color:var(--ink)}
ol.acts li::before{content:"→";color:var(--blue);font-weight:700;flex-shrink:0}

/* ── history table ───────────────────────────────────── */
table.hist{width:100%;border-collapse:collapse}
table.hist th{font-size:10.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;
  color:var(--faint);text-align:left;padding:11px 22px;border-bottom:1px solid var(--line3);background:var(--tint)}
table.hist td{padding:13px 22px;border-bottom:1px solid var(--hair);font-size:13.5px}
table.hist td:first-child{white-space:nowrap}
table.hist tr:last-child td{border-bottom:none}
select.statussel{width:auto;padding:5px 9px;font-size:12.5px}

/* ── footers & progress ──────────────────────────────── */
.foot{display:flex;align-items:center;gap:14px;margin-top:24px}
/* flex-shrink:0 is load-bearing. Every .spin sits in a flex row next to a long
   sentence, and without it the browser shrinks the 9px dot to about 5.6px wide
   while leaving it 9px tall -- so a round dot renders as a narrow ellipse and
   reads as half a dot that failed to draw. Measured, not guessed. */
.spin{width:9px;height:9px;flex-shrink:0;border-radius:50%;background:var(--blue);
  animation:pulse 1s ease-in-out infinite}
.bar{height:8px;border-radius:4px;background:#E3EAF3;overflow:hidden;margin-top:12px}
.bar>i{display:block;height:100%;background:var(--blue);border-radius:4px;transition:width .12s linear}
.big{font-size:32px;font-weight:800;font-variant-numeric:tabular-nums}
.empty{text-align:center;padding:44px}
.empty b{display:block;font-size:17px;font-weight:800}
````

## Paste 21 of 25

### web/app.js — piece 1 of 5

Create the file `web/app.js` and put exactly this in it. Change nothing: not a space, not a quote, not a blank line.

````javascript
/* GENERATED — do not edit.
   Built from Codebase/web/app.js with the online-only parts removed, plus
   Ripple Offline's own screens appended. Edit those two files instead; this one
   is rewritten from them every time Ripple Offline starts or is built. */
/* Ripple — front end.
   Plain JavaScript on purpose: no build step, no framework, nothing to install.
   The same file can be opened, read and changed by anyone. */


const STEPS = [
  ['Notification',    'Upload or type it in'],
  ['Review fields',   'Check before scanning'],
  ['Repository',      'What will be searched'],
  ['Impact analysis', 'Grouped by production table'],
  ['Dependency map',  'Where the column goes'],
  ['Summary',         'What it means'],
  ['Reply',           'Answer the upstream team'],
];

const S = {
  step: 1, maxStep: 1, view: 'wizard',
  mode: 'email',
  health: null,
  vals: null,          // {source, changeType, changeKind, changeDesc, subject, effectiveDate, poc*, upstream:[{table,attrs}]}
  emailPreview: null,
  scan: null,
  summary: null,
  reply: null,
  savedId: null,
  manRows: [{ table: '', attrs: '' }],
  man: { source: '', changeKind: 'unknown', effectiveDate: '', changeDesc: '',
         pocName: '', pocEmail: '', pocTeam: '' },
  busy: false, busyWhat: '',
  openGroup: 'p0', openRow: null, graphTab: 0,
  // Which information buttons are open, by label. Kept here so a redraw does
  // not shut a panel somebody is in the middle of reading.
  why: {},
};

// Typed by hand, so the awkward ones are given the right control rather than a
// box and a format to remember: a real calendar for the date, the same list of
// change types the scan actually understands, and a contact box that takes as
// many addresses as you care to paste in.
const MAN_FIELDS = [
  ['source', 'Source system', 'text', 'e.g. C360'],
  ['changeKind', 'Change type', 'kind', ''],
  ['effectiveDate', 'Effective date', 'date', ''],
  // A sentence, not a word. In a single-line box a real one is typed once and
  // then unreadable, which is a field nobody can check.
  ['changeDesc', 'What is changing', 'lines', 'One line describing the change'],
  ['pocName', 'Contact name', 'text', 'Who sent the notice'],
  ['pocEmail', 'Contact email', 'emails', 'name@corp.example.com, other@corp.example.com'],
  ['pocTeam', 'Contact team', 'text', 'e.g. C360 Data Governance'],
];

const CHANGE_KINDS = [
  ['unknown', 'Not specified'],
  ['removal', 'Attribute decommission'],
  ['value_change', 'Value format change'],
  ['type_change', 'Data type change'],
  ['rename', 'Attribute rename'],
];
const kindLabel = (id) => (CHANGE_KINDS.find(([k]) => k === id) || CHANGE_KINDS[0])[1];

// ── helpers ───────────────────────────────────────────────────────────────
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const el = (tag, props = {}, ...kids) => {
  const n = Object.assign(document.createElement(tag), props);
  for (const k of kids.flat()) if (k != null) n.append(k.nodeType ? k : String(k));
  return n;
};
const x = (root, name) => root.querySelector(`[data-x="${name}"]`);
const esc = (s) => String(s ?? '');

/* ── the information button ───────────────────────────────────────────────
   The fact stays on the page. The reasoning opens underneath it.

   There is ONE of these and every screen calls it. The line it draws:

     STAYS ON THE PAGE   the fact, the number and the names. "1 file is of a
                         type Ripple does not open — .ipynb". "4 production
                         tables at risk". "2 gaps in what Ripple could see."
     GOES BEHIND THE i   why that fact matters, what Ripple did about it, and
                         what somebody should do next.

   Somebody who never presses the button still sees everything Ripple knows it
   missed. They lose the reasoning, never the fact. Putting a count, a table
   name or a warning that something was not read behind this button breaks the
   product.

   It is a real button, not a title= tooltip: a tooltip cannot be opened on a
   touch screen, cannot be reached from a keyboard, and disappears while it is
   being read. It is reached by Tab, opened by Enter or Space, closed by Escape,
   and announced as a collapsed disclosure because of aria-expanded and
   aria-controls. Nothing is downloaded, so it works with no internet.

   `fact` is the node that stays visible; `label` names it for a screen reader
   and keys whether it is open, so a redraw does not shut a panel somebody is
   reading. Everything after that is the explanation — a string becomes a
   paragraph, a node is appended as it is. */
function why(fact, label, ...body) {
  const id = 'why-' + label.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  const open = !!(S.why && S.why[label]);
  const wrap = el('div', { className: 'iwrap' });
  const btn = el('button', { className: 'i', type: 'button', textContent: 'i' });
  btn.setAttribute('aria-controls', id);
  btn.setAttribute('aria-expanded', String(open));
  btn.setAttribute('aria-label', 'Why this matters: ' + label);
  const panel = el('div', { className: 'ipanel', id, role: 'note' });
  panel.hidden = !open;
  body.flat().filter(b => b != null && b !== '').forEach(b =>
    panel.append(b.nodeType ? b : el('p', { textContent: String(b) })));
  btn.onclick = () => {
    const now = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!now));
    panel.hidden = now;
    S.why = S.why || {};
    S.why[label] = !now;
  };
  // Escape closes it from anywhere inside, so a keyboard is never trapped in an
  // open panel, and the focus goes back to the button that opened it.
  wrap.onkeydown = (e) => {
    if (e.key === 'Escape' && !panel.hidden) { btn.click(); btn.focus(); }
  };
  wrap.append(el('div', { className: 'ifact' }, fact, btn), panel);
  return wrap;
}

/* Every email address in a blob of text, once each.
   People do not type addresses one at a time into a form. They copy the To line
   out of Outlook, which arrives as "Priya Raman <priya@corp.com>; Marcus Hale
   <marcus@corp.com>", or they paste a comma-separated list. Rather than telling
   anyone which of those is allowed, the addresses are picked out of whatever
   arrives and shown back as separate values, so it is obvious what was
   understood. */
const EMAIL_RE = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
function emailList(text) {
  const found = String(text ?? '').match(EMAIL_RE) || [];
  return [...new Set(found.map(a => a.toLowerCase()))];
}

/* A box that takes any number of addresses, showing what it found underneath.
   It updates itself rather than redrawing the screen, which would throw the
   cursor out of the box on every keystroke. */
function emailField(value, onchange, opts = {}) {
  const wrap = el('div');
  const inp = el('input', { type: 'text', value: value || '', placeholder: opts.hint || '',
    style: opts.style || '' });
  const chips = el('div', { className: 'chips', style: 'margin-top:8px' });
  const note = el('div', { className: 'small faint', style: 'margin-top:5px;line-height:1.5' });
  const sync = () => {
    const found = emailList(inp.value);
    chips.innerHTML = '';
    found.forEach(a => chips.append(el('span', { className: 'chip mono', textContent: a })));
    note.textContent = found.length
      ? `${found.length} address${found.length === 1 ? '' : 'es'} read. Separate with commas, or paste the whole To line.`
      : (inp.value.trim() ? 'No email address in what is typed here.' : '');
    onchange(inp.value, found);
  };
  inp.oninput = sync;
  sync();
  wrap.append(inp, chips, note);
  return wrap;
}

/* ── the tables your team publishes ───────────────────────────────────────
   The most expensive setting in Ripple: a finding only counts as production
   impact when the table it ends at is on this list, so a list that is wrong
   turns a change that really breaks three published tables into a calm "no
   production impact". The same control is used on both settings screens —
   online it is held by the running server, offline it is written to the
   settings file beside the program — so there is one of it, here.

   The list can be pasted from wherever it lives: an Excel column, a Slack
   message, a Confluence page, a query result. Nothing is tidied silently:
   whatever the reader declined to use comes back with a reason, and every
   table on the list that Ripple has never seen in the repository is said out
   loud, because that is the one thing that has to be known before a result
   from this list is believed. */
function productionState() {
  if (!S.prod) {
    S.prod = { text: S.health?.productionRule?.text ?? '', report: null,
               checking: false, msg: null, loaded: false, timer: null };
  }
  return S.prod;
}

const PROD_HELP =
  'Paste the real list — one per line, or however it arrives from Excel, Slack or '
  + 'Confluence. Ripple reads it as written. A naming pattern works alongside: a word '
  + 'starting with an underscore matches the end of a table name (_PROD matches '
  + 'sales_prod), * matches anything (PROD_*), and * on its own means treat every table '
  + 'as published.';

/* Which build is running. Shared by both editions on purpose: this exists
   because "it does not work" has more than once turned out to be "that was
   fixed a while ago, on a copy that was never installed", and the copy nobody
   can check is exactly the offline one. Where the answer came from is shown
   too — a commit hash is a fact, a file date is a guess, and they must never
   read the same. */
function buildCard(h) {
  const b = h && h.build;
  if (!b) return null;
  const card = el('div', { className: 'card pad lg', style: 'margin-top:18px' });
  card.append(el('span', { className: 'lbl', textContent: 'This build' }));
  card.append(el('div', { className: 'mono', style: 'margin-top:10px;line-height:1.55',
    textContent: b.label }));
  if (b.from === 'files') {
    card.append(el('div', { className: 'small muted', style: 'margin-top:8px;line-height:1.55',
      textContent: 'No build record was found, so that is the date of the newest file in '
        + 'this folder. It moves whenever anything is touched, and it does not tell you '
        + 'whether this copy was ever installed anywhere.' }));
  } else {
    card.append(el('div', { className: 'small muted', style: 'margin-top:8px;line-height:1.55',
      textContent: b.from === 'build'
        ? 'Recorded when this copy was packaged.'
        : b.from === 'host'
        ? 'Reported by the host that deployed it.'
        : 'Read from the repository this copy is running out of.' }));
  }
  return card;
}

function productionCard(opts = {}) {
  const p = productionState();
  const card = el('div', { className: 'card pad lg' });
  card.append(why(
    el('span', { className: 'lbl', textContent: 'The tables your team publishes' }),
    'how this list is read',
    PROD_HELP));

  const ta = el('textarea', { className: 'mono', rows: 8, value: p.text,
    placeholder: 'cust360_customer_demographics\nfoundation.cust360_customer_address\n_PROD',
    style: 'margin-top:12px;font-size:12.5px;line-height:1.6;resize:vertical' });
  card.append(ta);

  const out = el('div', { style: 'margin-top:14px' });
  const paint = () => { out.innerHTML = ''; out.append(productionReport(p, opts)); };

  const check = () => {
    p.checking = true; paint();
    api('/api/production/read', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: p.text }),
    }).then(r => { p.report = r; })
      .catch(e => { p.report = null; p.msg = { ok: false, text: e.message }; })
      .finally(() => { p.checking = false; paint(); });
  };

  ta.oninput = () => {
    p.text = ta.value; p.msg = null;
    // Checked as it is typed rather than behind a button, but not on every
    // keystroke: the check walks the repository, which is not free.
    clearTimeout(p.timer);
    p.timer = setTimeout(check, 600);
  };
  if (opts.onSave) {
    const row = el('div', { className: 'foot', style: 'margin-top:14px' });
    const save = el('button', { className: 'pri', textContent: 'Save and use this list' });
    save.onclick = () => run(async () => {
      try {
        await opts.onSave(p.text);
        p.msg = { ok: true, text: opts.savedNote || 'Saved. Every scan from now on uses this list.' };
      } catch (e) { p.msg = { ok: false, text: e.message }; }
      p.report = null; p.loaded = false;
    });
    row.append(save);
    if (opts.persistNote) row.append(el('span', { className: 'small faint', textContent: opts.persistNote }));
    card.append(row);
  }
  card.append(out);
  // The list already in force is checked the moment the screen opens, rather
  // than waiting for somebody to touch the box. A rule that matches nothing is
  // worth knowing about before it is edited, not after.
  if (!p.loaded) { p.loaded = true; check(); } else { paint(); }
  return card;
}

/* What Ripple made of the list: what it read, what it ignored and why, and —
   the point of the whole thing — which of these tables it has never seen. */
function productionReport(p, opts = {}) {
  const box = el('div');
  if (p.msg) {
    box.append(el('div', { className: 'note ' + (p.msg.ok ? 'good' : 'bad'), style: 'margin-bottom:12px' },
      p.msg.text));
  }
  if (p.checking && !p.report) {
    box.append(el('div', { className: 'foot' }, el('span', { className: 'spin' }),
      el('span', { className: 'small muted', textContent: 'Reading the list and checking it against the repository…' })));
    return box;
  }
  const r = p.report;
  if (!r) return box;
  if (p.checking) {
    box.append(el('div', { className: 'small faint', style: 'margin-bottom:8px' },
      el('span', { className: 'spin' }), ' Re-checking…'));
  }

  if (!r.entries.length) {
    box.append(el('div', { className: 'note bad' },
      el('b', { textContent: 'Nothing in that box was read as a table name. ' }),
      'Ripple falls back to its own guess — names ending _PROD, _PRD or _PUBLISHED — which '
      + 'is almost certainly not how your tables are named. Paste the list again, one table '
      + 'per line.'));
    if (r.notes.length) box.append(productionNotes(r));
    return box;
  }

  // ── what was read ──
  const head = el('div', { style: 'display:flex;gap:10px;align-items:baseline;flex-wrap:wrap' });
  head.append(el('b', { style: 'font-size:14px', textContent:
    r.nameCount
      ? `${r.nameCount} table name${r.nameCount === 1 ? '' : 's'} read`
      : 'No exact table names — patterns only' }));
  if (r.patternCount) {
    head.append(el('span', { className: 'badge sm violet',
      textContent: `${r.patternCount} pattern${r.patternCount === 1 ? '' : 's'}` }));
  }
  box.append(head);

  const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
  r.entries.forEach(e => {
    const chip = el('span', { className: 'chip mono' + (e.isPattern ? ' pattern' : ''),
      textContent: e.given });
    if (e.isPattern) chip.title = e.kind === 'glob'
      ? 'A pattern — matched against the whole table name'
      : 'A pattern — matches the end of a table name';
    chips.append(chip);
  });
  box.append(chips);
  if (r.patternCount) {
    box.append(el('div', { className: 'small faint', style: 'margin-top:8px;line-height:1.5',
      textContent: 'The outlined ones are patterns, not table names. Everything else is matched exactly.' }));
  }

  if (r.notes.length) box.append(productionNotes(r));
  box.append(productionCheck(r));
  return box;
}

function productionNotes(r) {
  const wrap = el('div', { className: 'note info', style: 'margin-top:12px' });
  wrap.append(el('b', { style: 'display:block', textContent: 'What was left out of that paste' }));
  r.notes.forEach(n => {
    const line = el('div', { style: 'margin-top:6px;line-height:1.55' }, n.text);
    if (n.examples && n.examples.length) {
      line.append(el('span', { className: 'small faint',
        textContent: ' — ' + n.examples.join(' · ') }));
    }
    wrap.append(line);
  });
  return wrap;
}

/* The important one. If fifty tables are pasted and Ripple has only ever seen
   forty-four of them, the other six are either misspelled or built somewhere it
   could not read — and either way a clean result for those six means nothing. */
function productionCheck(r) {
  const c = r.check;
  const wrap = el('div');
  if (!c || !c.checked) {
    wrap.append(el('div', { className: 'note warn', style: 'margin-top:12px' },
      el('b', { textContent: 'This list has not been checked against a repository. ' }),
      'Nothing has been read yet, so Ripple cannot say whether these tables exist. '
      + 'Choose the repository, then come back to this box.'));
    return wrap;
  }
  const missing = c.missing || [];
  const total = c.foundCount + missing.length;
  if (total) {
    wrap.append(el('div', { className: 'note ' + (missing.length ? 'bad' : 'good'), style: 'margin-top:12px' },
      el('b', { style: 'display:block;font-size:14px', textContent: missing.length
        ? `${missing.length} of the ${total} table${total === 1 ? '' : 's'} on this list `
          + `${missing.length === 1 ? 'is' : 'are'} not in this repository`
        : `All ${total} table${total === 1 ? '' : 's'} on this list were found in this repository` }),
      el('div', { style: 'margin-top:6px;line-height:1.55', textContent: missing.length
        ? `Ripple read ${c.tablesKnown.toLocaleString()} table names out of the code it could `
          + 'understand, and these are not among them. Either the name is spelled differently '
          + 'here, or the table is built somewhere Ripple could not read. Until that is settled, '
          + 'a clean result for these tables means nothing.'
        : `Checked against the ${c.tablesKnown.toLocaleString()} table names Ripple read out of `
          + 'this repository.' })));
    // Grouped rather than listed one sentence at a time. Sixty rows each saying
    // the same thing is a page nobody scrolls to the end of, and the two groups
    // send a person to two completely different places.
    [['nowhere', 'Not written anywhere in this repository',
      'A misspelling, a table from another repository, or one no code here names at all.'],
     ['written', 'The name is here, but nothing Ripple could read builds it',
      'Something creates these somewhere it could not follow — a procedure, a generated statement, or a job it has never seen.'],
    ].forEach(([state, title, why]) => {
      const group = missing.filter(m => m.state === state);
      if (!group.length) return;
      wrap.append(el('div', { style: 'margin-top:12px' },
        el('span', { className: 'lbl', textContent: `${title} — ${group.length}` }),
        el('div', { className: 'small faint', style: 'margin-top:4px;line-height:1.5', textContent: why })));
      const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:8px' });
      group.forEach(m => chips.append(el('span', { className: 'chip mono', textContent: m.given })));
      wrap.append(chips);
    });
    // A name nobody uses as a table may have been meant as a naming rule. Said
    // rather than guessed at: quietly re-reading it as a pattern is how a rule
    // stops meaning what it says.
    const meant = missing.filter(m => m.endsWith);
    if (meant.length) {
      const note = el('div', { className: 'note warn', style: 'margin-top:12px' },
        el('b', { style: 'display:block', textContent: meant.length === 1
          ? `No table is called ${meant[0].given} — but ${meant[0].endsWith} table`
            + `${meant[0].endsWith === 1 ? '' : 's'} end with it`
          : `${meant.length} of those names are the end of a real table name here` }),
        el('div', { style: 'margin-top:6px;line-height:1.55', textContent:
          'Ripple is treating them as exact table names, so they match nothing. If they were '
          + 'meant as a naming rule, write each one with an underscore or a star in front — '
          + `${meant.slice(0, 3).map(m => '_' + m.given).join(', ')} — and it will match the `
          + 'end of a name instead.' }));
      wrap.append(note);
    }
  }
  const dead = (c.patterns || []).filter(x => !x.matches);
  if (dead.length) {
    // "Your patterns" is wrong when nobody has set a list and these are Ripple's
    // own guess -- and the consequence used to be spelled out here in the same
    // twenty-two words as the note directly underneath, so the screen said the
    // same thing twice in two amber boxes touching each other.
    const mine = S.health?.productionSet ? 'your patterns' : 'the patterns entered';
    wrap.append(el('div', { className: 'note warn', style: 'margin-top:12px' },
      why(el('b', { textContent: dead.length === 1
          ? `The pattern ${dead[0].given} matches no table in this repository`
          : `${dead.length} of ${mine} match no table here — ${dead.map(d => d.given).join(', ')}` }),
        'patterns that match nothing',
      'A pattern that matches nothing does nothing. If your published tables are named some '
      + 'other way, Ripple will not count any of them as published, and the result will look '
      + 'safer than it is. Correct the list above.')));
  }
  const live = (c.patterns || []).filter(x => x.matches);
  if (live.length) {
    live.forEach(x => wrap.append(el('div', { className: 'small muted', style: 'margin-top:8px;line-height:1.55' },
      el('span', { className: 'chip mono pattern', textContent: x.given }),
      ` matches ${x.matches} table${x.matches === 1 ? '' : 's'} here — ${x.examples.join(', ')}`
        + (x.matches > x.examples.length ? ' and others' : ''))));
  }
  return wrap;
}

async function api(path, opts = {}) {
  const r = await fetch(path, opts);
  if (!r.ok) {
    let msg = `${r.status}`;
    try { msg = (await r.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return r.json();
}

function fmtDate(iso) {
  if (!iso) return '';
  const d = new Date(iso + (iso.length === 10 ? 'T00:00:00' : ''));
  if (isNaN(d)) return iso;
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}
function daysLeft(iso) {
  if (!iso) return null;
  const d = new Date(iso + 'T00:00:00');
  if (isNaN(d)) return null;
  return Math.round((d - new Date(new Date().toDateString())) / 86400000);
}
/* "No impact" is the only thing this tool sells, so there has to be a word for
   "I found nothing AND there is something here I could not read". Those are not
   the same answer, and printed as the same green badge the second one is a lie
   that reads as a promise. See _risk_of in lineage.py. */
const RISK = {
  high:    ['red',   'High risk'],
  medium:  ['amber', 'Medium risk'],
  low:     ['blue',  'Low risk'],
  unknown: ['amber', 'Not sure — needs a person'],
  none:    ['green', 'No impact'],
};

// ── chrome ────────────────────────────────────────────────────────────────
/* Typing the change in by hand and then being shown "check what Ripple read"
   is being asked to check your own typing. In that mode step 1 is the review,
   so the review step is not in the wizard at all -- rather than being in it,
   greyed out, or silently skipped past while the count still says 7. */
function manualFlow() {
  if (S.step === 1) return S.mode === 'manual';
  return S.vals ? S.vals.extractedBy === 'manual' : false;
}
function stepNumbers() {
  return manualFlow() ? [1, 3, 4, 5, 6, 7] : [1, 2, 3, 4, 5, 6, 7];
}
function nextStepAfter(n) {
  const list = stepNumbers();
  return list[Math.min(list.indexOf(n) + 1, list.length - 1)];
}

function renderSteps() {
  const box = $('#steps');
  box.innerHTML = '';
  stepNumbers().forEach((n, i) => {
    const [label, sub] = STEPS[n - 1];
    const on = S.view === 'wizard' && S.step === n;
    const done = n < S.maxStep && !on;
    const b = el('button', { className: `step${on ? ' on' : ''}${done ? ' done' : ''}` });
    b.disabled = n > S.maxStep;
    b.append(el('span', { className: 'n', textContent: done ? '✓' : String(i + 1) }),
      el('span', {}, el('span', { className: 't', textContent: label }),
        el('span', { className: 's', textContent: sub })));
    b.onclick = () => { if (n <= S.maxStep) { S.view = 'wizard'; S.step = n; render(); } };
    box.append(b);
  });
  $('#navHistory').className = 'navbtn' + (S.view === 'history' ? ' on' : '');
  $('#navSettings').className = 'navbtn' + (S.view === 'settings' ? ' on' : '');
}

function renderStatus() {
  const h = S.health;
  const box = $('#status');
  box.innerHTML = '';
  if (!h) return;
  const repoOk = h.repo.exists && h.repo.files > 0;
  box.append(
    el('div', { className: 'srow' },
      el('span', { className: 'dot ' + (repoOk ? 'ok' : 'warn') }),
      el('span', { textContent: repoOk ? `${h.repo.label} · ${h.repo.files} files` : 'No repository found' })),
    el('div', { className: 'srow' },
      el('span', { className: 'dot ' + (h.sqlDialect === 'generic' ? 'warn' : 'ok') }),
      el('span', { textContent: `SQL read as ${h.sqlDialect}` })),
  );
}

function setHeader(title, sub) { $('#hTitle').textContent = title; $('#hSub').textContent = sub; }

// ── step 1 ────────────────────────────────────────────────────────────────
function step1(root) {
  x(root, 'title').textContent = S.mode === 'manual' ? 'Enter the change by hand' : 'New impact notification';
  x(root, 'sub').textContent = S.mode === 'manual'
    ? 'Type the upstream table and attributes yourself.'
    : 'Upload the notification file.';
  $$('[data-mode]', root).forEach(b => {
    b.className = 'pill' + (b.dataset.mode === S.mode ? ' on' : '');
    b.onclick = () => { S.mode = b.dataset.mode; render(); };
  });
  x(root, 'emailMode').classList.toggle('hide', S.mode !== 'email');
  x(root, 'manualMode').classList.toggle('hide', S.mode !== 'manual');

  if (S.mode === 'email') {
    // What Ripple does, in one line, with the four steps behind the button.
    const does = x(root, 'does');
    does.append(el('span', { className: 'lbl', textContent: 'What Ripple does' }));
    const steps = el('ol', { className: 'nums', style: 'margin-top:0' });
    ['Reads the tables, attributes, date and contact out of the notice',
     'Searches every file in the connected repository',
     'Follows each rename to the production table it feeds',
     'Says what breaks — and what it could not read',
    ].forEach(t => steps.append(el('li', {}, t)));
    does.append(why(
      el('span', { style: 'line-height:1.55',
        textContent: 'Reads your notification, searches your repository, and says what this '
          + 'change breaks.' }),
      'what Ripple does, step by step', steps));
    const confirm = x(root, 'confirm');
    confirm.append(why(
      el('b', { textContent: 'Nothing is scanned until you confirm.' }),
      'confirming before a scan',
      'Ripple shows you everything it read out of the email first, and every field can be '
      + 'edited. The scan then uses what is on that screen — not the email.'));
    const drop = $('#drop', root), file = $('#file', root);
    drop.onclick = () => file.click();
    drop.ondragover = (e) => { e.preventDefault(); drop.classList.add('over'); };
    drop.ondragleave = () => drop.classList.remove('over');
    drop.ondrop = (e) => {
      e.preventDefault(); drop.classList.remove('over');
      if (e.dataTransfer.files[0]) upload(e.dataTransfer.files[0]);
    };
    file.onchange = () => file.files[0] && upload(file.files[0]);
    return;
  }

  // manual
  x(root, 'noAi').append(why(
    el('b', { textContent: 'No AI used in this mode.' }),
    'what happens without AI',
      'Ripple searches for exactly the names you type. Nothing is sent anywhere.'));
  const rows = x(root, 'manRows');
  rows.innerHTML = '';
  S.manRows.forEach((r, i) => {
    const wrap = el('div', { style: 'display:flex;gap:20px;align-items:flex-end;padding:16px 20px' + (i ? ';border-top:1px solid var(--hair)' : '') });
    const t = el('input', { type: 'text', className: 'mono', value: r.table, placeholder: 'CUSTOMER_DEMOGRAPHICS', style: 'margin-top:6px' });
    t.oninput = () => { r.table = t.value; updateManHint(root); };
    const a = el('input', { type: 'text', className: 'mono', value: r.attrs, placeholder: 'MARKET_CODE, MARKET_NAME', style: 'margin-top:6px' });
    a.oninput = () => { r.attrs = a.value; updateManHint(root); };
    wrap.append(
      el('div', { style: 'flex:1;min-width:0' }, el('span', { className: 'lbl faint', textContent: 'Upstream table name' }), t),
      el('div', { style: 'flex:1;min-width:0' }, el('span', { className: 'lbl faint', textContent: 'Attributes — comma separated' }), a));
    if (S.manRows.length > 1) {
      const rm = el('button', { className: 'danger', textContent: 'Remove' });
      rm.onclick = () => { S.manRows.splice(i, 1); render(); };
      wrap.append(rm);
    }
    rows.append(wrap);
  });
  x(root, 'addRow').onclick = () => { S.manRows.push({ table: '', attrs: '' }); render(); };

  const fields = x(root, 'manFields');
  fields.innerHTML = '';
  const small = 'margin-top:7px;font-size:12.5px;font-weight:400;color:var(--mute);padding:7px 11px';
  MAN_FIELDS.forEach(([key, label, type, hint]) => {
    const field = el('div', { className: 'field' }, el('span', { className: 'lbl faint', textContent: label }));
    if (type === 'kind') {
      const sel = el('select', { style: 'margin-top:7px;padding:7px 11px;font-size:12.5px' });
      CHANGE_KINDS.forEach(([k, l]) => sel.append(el('option', { value: k, textContent: l, selected: k === S.man.changeKind })));
      sel.onchange = () => { S.man.changeKind = sel.value; };
      field.append(sel);
    } else if (type === 'emails') {
      field.append(emailField(S.man.pocEmail, (raw) => { S.man.pocEmail = raw; },
        { hint, style: small }));
    } else if (type === 'lines') {
      const ta = el('textarea', { rows: 3, value: S.man[key], placeholder: hint,
        style: small + ';line-height:1.55' });
      ta.oninput = () => { S.man[key] = ta.value; };
      field.append(ta);
    } else {
      const inp = el('input', { type: type === 'date' ? 'date' : 'text',
        value: S.man[key], placeholder: hint, style: small });
      inp.oninput = () => { S.man[key] = inp.value; };
      field.append(inp);
      // A date typed in a box is a date somebody has to work out. The picker is
      // the control; this is the answer in words, so a slip is visible.
      if (type === 'date') {
        const said = el('div', { className: 'small faint', style: 'margin-top:5px' });
        const sayDate = () => {
          const dl = daysLeft(inp.value);
          said.textContent = inp.value
            ? fmtDate(inp.value) + (dl === null ? '' : dl < 0 ? ' — that date has passed'
              : ` — ${dl} day${dl === 1 ? '' : 's'} away`)
            : '';
        };
        inp.addEventListener('input', sayDate);
        sayDate();
        field.append(said);
      }
    }
    fields.append(field);
  });

  x(root, 'manDemo').onclick = () => {
    S.manRows = [{ table: 'CUSTOMER_DEMOGRAPHICS', attrs: 'MARKET_CODE, MARKET_NAME' },
                 { table: 'CUSTOMER_ADDRESS', attrs: 'COUNTRY_CODE' }];
    S.man = { source: 'C360', changeKind: 'value_change', effectiveDate: '2026-09-18',
      changeDesc: "Values change from ISO abbreviations to full country names ('US' becomes 'United States').",
      pocName: 'Priya Raman',
      pocEmail: 'priya.raman@corp.example.com, dl-c360-governance@corp.example.com',
      pocTeam: 'C360 Data Governance' };
    render();
  };
  x(root, 'manStart').onclick = () => startManual();
  updateManHint(root);
}

function manValid() { return S.manRows.some(r => r.table.trim() && r.attrs.trim()); }
function updateManHint(root) {
  const tables = S.manRows.filter(r => r.table.trim()).length;
  const attrs = S.manRows.reduce((a, r) => a + r.attrs.split(',').map(s => s.trim()).filter(Boolean).length, 0);
  x(root, 'manCount').textContent = tables ? `${tables} table${tables > 1 ? 's' : ''} · ${attrs} attribute${attrs === 1 ? '' : 's'}` : 'Nothing entered yet';
  const ok = manValid();
  x(root, 'manStart').disabled = !ok;
  // The button says where it goes, so the hint no longer repeats it. It used to
  // read "Run impact analysis" and land on the repository screen instead, beside
  // a second button of the same name.
  x(root, 'manHint').textContent = ok
    ? 'Nothing is scanned yet.'
    : 'Enter at least one table name and one attribute to continue.';
}

function startManual() {
  if (!manValid()) return;
  S.vals = {
    source: S.man.source.trim() || 'Entered manually',
    changeType: kindLabel(S.man.changeKind),
    changeKind: S.man.changeKind || 'unknown',
    changeDesc: S.man.changeDesc.trim() || 'Entered by hand — no notification email was used.',
    subject: 'Manual impact check — ' + S.manRows.filter(r => r.table.trim()).map(r => r.table.trim()).join(', '),
    effectiveDate: S.man.effectiveDate.trim(),
    pocName: S.man.pocName.trim(),
    pocEmail: S.man.pocEmail.trim(), pocEmails: emailList(S.man.pocEmail),
    pocTeam: S.man.pocTeam.trim(),
    upstream: S.manRows.filter(r => r.table.trim()).map(r => ({
      table: r.table.trim(),
      attrs: r.attrs.split(',').map(s => s.trim()).filter(Boolean),
    })),
    extractedBy: 'manual', warnings: [],
  };
  S.emailPreview = null; S.scan = null; S.summary = null; S.savedId = null;
  // Straight to the repository. There is nothing on the review step that was
  // not just typed on this one.
  goto(3);
}

function upload(f) {
  // Check the size here as well as on the server. A hosted copy sits behind a
  // host that rejects an oversized upload itself, and its refusal is a bare
  // number with no explanation — so say it properly before sending anything.
  const cap = S.health?.limits?.maxUploadBytes || 25000000;
  if (f.size > cap) {
    alert(`That file is ${(f.size / 1e6).toFixed(1)} MB. The most this copy of Ripple accepts is `
      + `${Math.round(cap / 1e6)} MB.`
      + (S.health?.serverless
        ? ' It is running on a serverless host, which refuses anything bigger before Ripple'
          + ' sees it. Save the email as .eml, which is far smaller than a .msg, or enter the'
          + ' change by hand on the Enter manually tab.'
        : ''));
    return;
  }
  run(async () => {
    const fd = new FormData();
    fd.append('file', f);
    const out = await api('/api/read-email?useAI=true', { method: 'POST', body: fd });
    acceptExtract(out);
  }, 'Reading the notification…');
}

function acceptExtract(out) {
  S.emailPreview = out.emailPreview || null;
  S.vals = {
    source: out.source || '', changeType: out.changeType || '', changeKind: out.changeKind || 'unknown',
    changeDesc: out.changeDesc || '', subject: out.subject || '', effectiveDate: out.effectiveDate || '',
    pocName: out.pocName || '', pocEmail: out.pocEmail || '', pocEmails: emailList(out.pocEmail),
    pocTeam: out.pocTeam || '',
    upstream: (out.upstream || []).map(u => ({ table: u.table, attrs: u.attrs || [] })),
    extractedBy: out.extractedBy || 'rules',
    warnings: out.warnings || [], aiNote: out.aiNote || '',
  };
  S.scan = null; S.summary = null; S.savedId = null;
  goto(2);
}

// ── step 2 ────────────────────────────────────────────────────────────────
function step2(root) {
  const v = S.vals;
  const manual = v.extractedBy === 'manual';
  x(root, 'title').textContent = manual ? 'Change details' : 'What Ripple read';
  x(root, 'sub').textContent = manual
    ? 'Edit anything before scanning.'
    : 'Ripple scans on exactly what is here, not on the email.';
  x(root, 'by').textContent = manual ? 'Entered by you — no AI used'
    : 'Found by matching the catalogue — check it';

  const warn = x(root, 'warnings'); warn.innerHTML = '';
  (v.warnings || []).forEach(w => warn.append(el('div', { className: 'note warn', textContent: w, style: 'margin-bottom:12px' })));

  const meta = x(root, 'meta'); meta.innerHTML = '';
  const dl = daysLeft(v.effectiveDate);
  const metaDefs = [
    ['Source system', 'source', 'text'],
    ['Change type', 'changeKind', 'select'],
    ['Effective date', 'effectiveDate', 'date'],
    ['Contact', 'pocName', 'text'],
  ];
  metaDefs.forEach(([label, key, type]) => {
    const card = el('div', { className: 'stat' });
    card.append(el('span', { className: 'lbl', textContent: label }));
    if (type === 'select') {
      const sel = el('select', { style: 'margin-top:8px' });
      CHANGE_KINDS.forEach(([k, l]) => sel.append(el('option', { value: k, textContent: l, selected: k === v.changeKind })));
      sel.onchange = () => { v.changeKind = sel.value; v.changeType = sel.selectedOptions[0].textContent; };
      card.append(sel);
    } else {
      const inp = el('input', { type: type === 'date' ? 'date' : 'text', value: v[key] || '', style: 'margin-top:8px' });
      inp.oninput = () => { v[key] = inp.value; };
      card.append(inp);
      if (key === 'effectiveDate' && dl !== null) {
````

## Paste 22 of 25

### web/app.js — piece 2 of 5

Add this to the END of `web/app.js`, straight after what is already there. Do not start a new file. Do not re-type anything above.

````javascript
        card.append(el('span', { className: 'badge sm ' + (dl <= 21 ? 'amber' : 'blue'),
          textContent: dl < 0 ? 'date has passed' : `${dl} day${dl === 1 ? '' : 's'} left`, style: 'margin-top:8px' }));
      }
      // Every address, editable, and as many as there are. A notification is
      // often sent by one person on behalf of a mailbox, and the reply has to
      // go to both.
      if (key === 'pocName') {
        card.append(emailField(v.pocEmail, (raw, found) => { v.pocEmail = raw; v.pocEmails = found; },
          { hint: 'name@corp.example.com, other@corp.example.com', style: 'margin-top:8px' }));
      }
    }
    meta.append(card);
  });

  const subj = x(root, 'subject'); subj.value = v.subject || ''; subj.oninput = () => { v.subject = subj.value; };
  const desc = x(root, 'desc'); desc.value = v.changeDesc || ''; desc.oninput = () => { v.changeDesc = desc.value; };

  renderUpstreamRows(root, v);
  x(root, 'addRow').onclick = () => { v.upstream.push({ table: '', attrs: [] }); render(); };
  x(root, 'next').onclick = () => goto(3);
}

function renderUpstreamRows(root, v) {
  const box = x(root, 'rows'); box.innerHTML = '';
  const tables = v.upstream.filter(u => u.table.trim()).length;
  const attrs = v.upstream.reduce((a, u) => a + (u.attrs || []).length, 0);
  x(root, 'count').textContent = `${tables} table${tables === 1 ? '' : 's'} · ${attrs} attribute${attrs === 1 ? '' : 's'}`;
  v.upstream.forEach((u, i) => {
    const wrap = el('div', { style: 'display:flex;gap:24px;align-items:flex-end;padding:16px 20px;animation:fadeUp .3s ease' + (i ? ';border-top:1px solid var(--hair)' : '') });
    const t = el('input', { type: 'text', className: 'mono', value: u.table, style: 'margin-top:6px' });
    t.oninput = () => { u.table = t.value; };
    const a = el('input', { type: 'text', className: 'mono', value: (u.attrs || []).join(', '), style: 'margin-top:6px' });
    a.oninput = () => { u.attrs = a.value.split(',').map(s => s.trim()).filter(Boolean); };
    const rm = el('button', { className: 'danger', textContent: 'Remove' });
    rm.onclick = () => { v.upstream.splice(i, 1); render(); };
    wrap.append(
      el('div', { style: 'width:288px;flex-shrink:0' }, el('span', { className: 'lbl faint', textContent: 'Upstream table name' }), t),
      el('div', { style: 'flex:1;min-width:0' }, el('span', { className: 'lbl faint', textContent: 'Upstream attributes name' }), a), rm);
    box.append(wrap);
  });
  if (!v.upstream.length) box.append(el('div', { className: 'pad muted', textContent: 'Nothing to scan yet — add a table below.' }));
}

// ── step 3 ────────────────────────────────────────────────────────────────
/* Anything worth saying about the repository before anything is scanned, or
   nothing at all. Online that is a failed connection; offline it is a folder
   that has been moved or deleted since it was chosen, so the offline build
   replaces this whole function rather than sharing it. */

function step3(root) {
  const h = S.health;
  if (!h) return;

  x(root, 'title').textContent =
    'Connected repository';
  x(root, 'sub').textContent =
    'This is the code Ripple will search. It is read, never written to.';


  const alert = x(root, 'alert'); alert.innerHTML = '';
  const said = repoAlert(h);
  if (said) alert.append(said);

  x(root, 'left').innerHTML = '';
  x(root, 'left').append(
    repoFacts(h));

  // the same confirmation the prototype shows, on the numbers Ripple really has
  const ready = x(root, 'ready'); ready.innerHTML = '';
  const repoOk = h.repo.exists && h.repo.files > 0;
  // Where the code came from, and the one fact that pins down which version of
  // it was read. A folder that was never a git checkout has no branch, and says
  // nothing rather than claiming "main" because that is the usual answer.
  let where = 'a folder on this machine';
  let pin = h.repo.branch ? ['Branch ', el('span', { className: 'mono', textContent: h.repo.branch })] : [];
  ready.append(el('div', { className: 'note ' + (repoOk ? 'good' : 'warn') },
    el('b', { textContent: repoOk ? `✓ ${h.repo.label} connected` : `Nothing to scan in ${h.repo.label}`,
      style: 'display:block;font-size:14px' }),
    el('div', { className: 'small', style: 'margin-top:2px;font-weight:600;opacity:.8',
      textContent: where }),
    el('div', { style: 'margin-top:8px;line-height:1.55' },
      pin,
      (pin.length ? ' — ' : '') + (repoOk
        ? `${h.repo.files} file${h.repo.files === 1 ? '' : 's'} ready to scan.`
        : 'check the repository folder in Settings & checks.'))));
  ready.append(neverOpenedNote(h.repo.heldOnline || 0, h.repo.pathTooLong || 0));
  // Only when nobody has said. This is not a warning any more: nothing is
  // scanned until the list has been given. Ripple used to fill it in with a
  // guess -- _PROD, _PRD, _PUBLISHED -- and on a warehouse that names its
  // published tables any other way that guess matched nothing. Matching nothing
  // did not read as "I do not know which tables are yours"; it read as "no
  // production table is affected", in green, over a change that broke them all.
  if (!h.productionSet) {
    ready.append(el('div', { className: 'note warn', style: 'margin-top:12px' },
      why(el('b', { textContent: 'Ripple needs to know which tables you publish.' }),
        'why it will not scan without this',
      'A published table is one people outside your team read, and Ripple has no way of '
      + 'working out which of yours those are — every warehouse names them differently. '
      + 'Without the list, every table fails that test, and a change that breaks three of '
      + 'them comes back as "no production table is affected". That is the same green tick '
      + 'as a genuinely clean answer, which is why Ripple will not give it.',
      'Open Settings & checks and paste your published table names, or a pattern they all '
      + 'share such as _PUBLISHED. It takes a minute and it is the setting the whole answer '
      + 'rests on.')));
  }
  if (h.repo.inSkippedDirs) {
    const box = el('div', { className: 'note warn', style: 'margin-top:12px' });
    box.append(why(
      el('b', { textContent: `${h.repo.inSkippedDirs} file${h.repo.inSkippedDirs === 1 ? '' : 's'} `
        + 'skipped — in ' + (h.repo.skippedDirNames || []).join(', ') }),
      'folders Ripple skips',
      'Folders with these names usually hold generated copies of code, so Ripple walks past '
      + 'them. If your real pipeline lives in one, none of it was read and none of it is in '
      + 'this answer.'));
    ready.append(box);
  }

  // what kinds of file are in the index — counted, not assumed
  const kinds = x(root, 'kinds'); kinds.innerHTML = '';
  // Nothing indexed means nothing to list, and an empty card sitting there
  // reads as a panel that failed to load.
  kinds.classList.toggle('hide', !h.repo.kinds?.length);
  if (h.repo.kinds?.length) {
    kinds.append(el('span', { className: 'lbl', textContent: 'What gets read' }));
    const chips = el('div', { className: 'chips', style: 'margin-top:12px' });
    h.repo.kinds.forEach(k => chips.append(el('span', { className: 'chip', textContent: `${k.lang} · ${k.files}` })));
    kinds.append(chips);
    // A DAG that runs a query kept in a separate .sql file holds no SQL of its
    // own, so it used to be indistinguishable from a config file with nothing
    // in it. The query itself is read on its own account — this is the link
    // between the two, said so that "Python · 240" is not read as 240 files
    // Ripple learned nothing from.
    if (h.repo.runsSqlFrom) {
      kinds.append(el('div', { className: 'small muted', style: 'margin-top:14px' },
        why(el('span', { textContent: `${h.repo.runsSqlFrom} of these run SQL kept in a `
          + 'separate .sql file' }),
          'files that run SQL from elsewhere',
      'These files hold no SQL of their own — they run a .sql file kept beside them. Ripple '
      + 'read those .sql files separately, so nothing is lost. If one of them points at a file '
      + 'that is not in this repository, the result will say so.')));
    }
    // File types Ripple does not open. Nothing recorded these before — the walk
    // had a bare `continue` with no counter — so a repository whose pipeline is
    // written in .ipynb or .tf files looked exactly like one with no pipeline
    // in it. The point is not to read them. It is that the NEXT unlisted
    // extension is visible instead of silent.
    if (h.repo.unknownExt?.length) {
      const total = h.repo.unknownExt.reduce((n, k) => n + k.files, 0);
      // The count and the extensions stay on the page. Only the consequence and
      // what to do about it go behind the button.
      kinds.append(el('div', { className: 'small muted', style: 'margin-top:14px' },
        why(el('span', { textContent: `${total} other file${total === 1 ? '' : 's'} `
          + `${total === 1 ? 'is' : 'are'} of a type Ripple does not open — `
          + h.repo.unknownExt.map(k => `${k.ext} · ${k.files}`).join(', ') }),
          'file types Ripple does not open',
      'Ripple opens SQL files and the file types that usually hold SQL. It did not look inside '
      + 'these at all, so nothing written in them can appear in any answer. If part of your '
      + 'pipeline lives in one of these types, ask whoever set Ripple up to add it.')));
    }
  }

  const c = x(root, 'cat'); c.innerHTML = '';
  // Until the answer arrives this card has a heading and nothing under it. On a
  // repository of a few thousand files the read takes minutes, and for all of
  // them that is an empty box sitting on the screen. It says what it is waiting
  // for instead — and gets replaced, not added to, when the answer comes.
  c.append(el('div', { className: 'small faint', style: 'margin-top:10px',
    textContent: 'Counted once every file has been read.' }));
  api('/api/catalog').then(cat => {
    c.innerHTML = '';
    c.append(el('div', { style: 'display:flex;gap:26px;margin-top:10px' },
      el('div', {}, el('div', { textContent: String(cat.tableCount), style: 'font-size:26px;font-weight:800;font-variant-numeric:tabular-nums' }),
        el('div', { className: 'small faint', textContent: 'tables found' })),
      el('div', {}, el('div', { textContent: String(cat.columnCount), style: 'font-size:26px;font-weight:800;font-variant-numeric:tabular-nums' }),
        el('div', { className: 'small faint', textContent: 'columns found' }))));
    const g = x(root, 'gaps'); g.innerHTML = '';
    if (cat.gaps.length) {
      // This list used to be headed "tables Ripple could not fully read", which
      // read as a list of dead ends — and while the scan really did stop at
      // them, that was true. It no longer is: a scan follows the column
      // straight through a SELECT * and marks every step past it. Leaving the
      // old heading up would have somebody reading this page as the reason a
      // result was short, when it is not.
      const box = el('div', { className: 'note info' });
      const names = el('div');
      cat.gaps.forEach(gap => names.append(el('div', { style: 'margin-top:6px' },
        el('span', { className: 'mono', textContent: gap.table }), ' — ' + gap.reason)));
      box.append(why(
        el('b', { textContent: `${cat.gaps.length} table${cat.gaps.length === 1 ? '' : 's'} `
          + `here ${cat.gaps.length === 1 ? 'has' : 'have'} no column list written down` }),
        'tables with no column list',
      'These tables take every column at once, so the code never writes down what their '
      + 'columns are called. Your attribute still travels through them and the scan follows '
      + 'it. What Ripple cannot promise is the name it carries on the other side.'));
      box.append(names);
      g.append(box);
    } else if (!cat.tableCount) {
      // "Every table definition was readable" is technically true of nothing at
      // all, and reads as a clean bill of health for a repository that was
      // never read.
      g.append(el('div', { className: 'note info',
        textContent: 'No table definitions were read, so there is no catalogue to check.' }));
    } else if ((h.repo.heldOnline || 0) + (h.repo.pathTooLong || 0)) {
      // The same trap one branch up, one step subtler. "Every table definition
      // was readable" is true of the files that were opened, and sitting in
      // green under a warning that some were not, it reads as a clean bill of
      // health for the repository. It has to say which repository it means.
      g.append(el('div', { className: 'note info', textContent:
        'Every table definition in the files that could be opened was readable. '
        + 'The files above were not opened, so nothing is known about them.' }));
    } else {
      g.append(el('div', { className: 'note good', textContent: 'Every table definition was readable.' }));
    }
  });

  const reread = x(root, 'reindex');
  reread.disabled = S.busy;
  if (S.busy) reread.textContent = 'Reading the repository…';
  reread.onclick = () => run(async () => {
    S.health = await api('/api/reindex', { method: 'POST' });
    render();
  }, `Reading every file in ${h.repo.label}…`);
  x(root, 'next').onclick = () => runScan();
  x(root, 'hint').textContent = S.busy
    // Measured on a repository the size of his: a couple of thousand files and
    // statements six hundred lines long take minutes, not seconds. Saying
    // "a few seconds" and then taking four minutes is how a working program
    // gets reported as hung.
    ? (progressText(S.progress)
       || 'Reading every file. On a repository of a few thousand files this takes '
          + 'a few minutes — the count appears as soon as the first files are read.')
    : repoOk
      ? `The scan will search ${h.repo.label}.`
      : 'Nothing is indexed, so a scan would find nothing.';
  // Every half matters, and this is the ONLY place the button's state is set --
  // it was set twice, further up as well, and the second assignment quietly
  // undid the first. Files can be indexed from a folder that has since been
  // moved or deleted, and offering to scan it would be scanning a memory. And
  // with no published-table list there is nothing to measure an answer against:
  // the engine refuses the scan anyway, and a button that runs and comes back
  // with an error is a worse way of being told than one that says what is
  // missing before it is pressed.
  x(root, 'next').disabled = !repoOk || S.busy || !h.productionSet;
  if (!h.productionSet && !S.busy) {
    x(root, 'next').textContent = 'Add your published tables first';
  }
}

/* What Ripple is reading now — the same facts either way. */
function repoFacts(h) {
  const r = el('div', { className: 'card pad lg' });
  r.append(el('span', { className: 'lbl', textContent:
    'Folder on this machine' }));
  r.append(el('div', { className: 'mono', textContent: h.repo.label,
    style: 'font-size:17px;font-weight:600;color:var(--blued);margin-top:8px;word-break:break-all' }));
  r.append(el('div', { className: 'small faint', textContent: h.repo.path,
    style: 'margin-top:5px;word-break:break-all' }));
  const facts = [
    ['Files indexed', String(h.repo.files)],
    // Only when there are some. "Files indexed 1,770" is the number somebody
    // reads to decide the whole folder was covered, so when it was not, every
    // row saying otherwise has to sit directly underneath it.
    ...(((h.repo.heldOnline || 0) + (h.repo.pathTooLong || 0))
      ? [['Files never opened', String((h.repo.heldOnline || 0) + (h.repo.pathTooLong || 0))]]
      : []),
    ...(h.repo.unreadable ? [['Files that would not parse', String(h.repo.unreadable)]] : []),
    ...(h.repo.inSkippedDirs
      ? [['Files in folders Ripple skips', String(h.repo.inSkippedDirs)]] : []),
    ['Statements understood', String(h.repo.statements)],
    // A folder that was never a git checkout has no branch, and an empty row
    // would read as a missing answer rather than as "there isn't one".
    ...(h.repo.branch ? [['Branch', h.repo.branch]] : []),
    ['SQL read as', h.sqlDialect],
    ['Renames followed', hopsPhrase(h.maxHops)],
    // The setting that decides whether the answer says "production impact" at
    // all, on the screen where somebody decides to press Run -- rather than
    // only on a settings screen they have never opened. Learning after a clean
    // result that Ripple was guessing which tables you publish is learning it
    // one step too late.
    ['Counts as published', h.production || 'not set'],
  ];
  const t = el('div', { style: 'margin-top:18px' });
  facts.forEach(([k, val]) => t.append(el('div', { style: 'display:flex;gap:14px;padding:9px 0;border-top:1px solid var(--hair)' },
    el('span', { className: 'small muted', textContent: k, style: 'flex:1' }),
    el('span', { className: 'small' + (k === 'Commit read' ? ' mono' : ''), textContent: val, style: 'font-weight:700' }))));
  r.append(t);
  return r;
}

/* The connect form. Nothing here pretends: the button does one real request. */

/* deeper is set when a trail was cut short by the hop limit and the person
   asked for it to be followed further. It applies to that one scan; the setting
   on the settings screen is left where it was. */
function runScan(deeper) {
  // Zero is a REAL choice here -- "follow it to the end of the code" -- so this
  // asks whether an argument was given rather than whether it is truthy. Read
  // as falsy, pressing "follow these to the end" sent nothing at all and ran the
  // scan again at the same limit, for the same answer: a button that does
  // nothing, on the one screen that is meant to be honest.
  const asked = deeper !== undefined && deeper !== null;
  run(async () => {
    S.scan = await api('/api/scan', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        upstream: S.vals.upstream,
        changeKind: S.vals.changeKind || 'unknown',
        ...(asked ? { maxHops: deeper } : {}),
      }),
    });
    S.summary = null; S.openGroup = 'p0'; S.openRow = null; S.graphTab = 0;
    goto(4);
  }, !asked ? 'Searching every file for these names…'
    : deeper ? `Following the same attributes again, up to ${deeper} renames deep…`
    : 'Following the same attributes again, to the end of the code…');
}

// ── step 4 ────────────────────────────────────────────────────────────────
function step4(root) {
  const sc = S.scan;
  if (!sc) { x(root, 'progress').append(el('div', { className: 'note info', textContent: 'No scan yet.' })); return; }
  // Nothing was read, so there is no result to grade. A green "No impact" over
  // an empty folder is a statement about the folder wearing the clothes of a
  // statement about the pipeline.
  const nothingRead = !sc.filesScanned;
  // "I never saw that column" was worded exactly like "that column goes
  // nowhere" — the same green tick, the same empty list, byte for byte. They
  // are opposite answers: one is an answer to the question, the other is the
  // question never having been asked. A typo in an attribute name shipped as
  // "no impact", which is the most convincing wrong answer this tool can give.
  const [cls, label] = nothingRead ? ['amber', 'Nothing was scanned']
    : sc.lookupFailed ? ['amber', 'Column not found — nothing was checked']
    : (RISK[sc.risk] || RISK.none);
  x(root, 'risk').append(el('span', { className: 'badge ' + cls, textContent: label }));
  // Beside the risk word, never on another screen. "No impact, and I could
  // follow every step of it" and "no impact, and three tables on the way were
  // invisible to me" printed as the same three words — everything below was
  // already counted and then thrown away. Counts, not a percentage: there is no
  // honest denominator for "how much of a trail exists", and a made-up one
  // would put a precise number on a guess.
  // Not shown beside a failed lookup. "Whole trail seen" is true and reads as a
  // reassurance, over a scan that followed no trail at all because the column
  // it was given is not in this repository.
  const cov = sc.coverage;
  if (cov && !nothingRead && !sc.lookupFailed) {
    x(root, 'risk').append(el('span', {
      className: 'badge ' + (cov.complete ? 'green' : 'grey'),
      style: 'margin-left:8px',
      textContent: cov.complete
        ? 'whole trail seen'
        : `${cov.gaps.length} gap${cov.gaps.length === 1 ? '' : 's'} in what Ripple could see` }));
  }
  // The line under the title has to be true of the screen underneath it, and
  // "grouped under the production table" is not true when there is not one.
  x(root, 'sub').textContent = sc.lookupFailed
    ? 'Ripple never met these column names. Check the spelling before reading anything below.'
    : sc.groups.length
    ? 'Every finding grouped under the production table it puts at risk.'
    : (sc.reached || []).length || (sc.other || []).length
      ? 'Nothing matched your published-table rule. Every table the change does reach is below.'
      : 'What the change touches in this repository, and what could not be read.';

  // What was actually read. Real counts only — the scan has already finished by
  // the time this renders, so there is nothing to animate.
  const done = el('div', { className: 'card pad lg' });
  done.append(el('div', { style: 'display:flex;align-items:center;gap:12px;flex-wrap:wrap' },
    el('span', { className: 'chip mono', textContent: S.health.repo.label }),
    // A folder that was never a git checkout has no branch, and an empty chip
    // sitting there reads as something that failed to load.
    S.health.repo.branch ? el('span', { className: 'chip', textContent: S.health.repo.branch }) : null,
    el('span', { textContent: nothingRead
      ? 'No files were read'
      : sc.stats.filesWithImpact
        ? `Scan complete — ${sc.stats.filesWithImpact} file${sc.stats.filesWithImpact === 1 ? '' : 's'} with impact`
        : 'Scan complete — nothing carries these attributes',
      style: 'margin-left:auto;font-size:13px;font-weight:600;color:var(--blued)' })));
  done.append(el('div', { style: 'display:flex;align-items:baseline;gap:9px;margin-top:18px;flex-wrap:wrap' },
    el('span', { className: 'big', textContent: String(sc.filesScanned) }),
    el('span', { className: 'small muted', textContent: `files read · ${sc.filesMatched} mention the names you confirmed` })));
  // The sentence that qualifies every other sentence on this screen. Ripple read
  // one folder. "No impact" is a fact about that folder and about nothing else —
  // and the single commonest way to be wrong with this tool is to read it as a
  // fact about the warehouse.
  done.append(el('div', { className: 'small muted', style: 'margin-top:10px' },
    why(el('span', { textContent: `Ripple read these ${sc.filesScanned} files and nothing else.` }),
      'what "nothing found" covers',
      'Ripple only read this repository. Something it did not find here could still exist in '
      + 'another repository, in a scheduled query, or in a dashboard built straight on the '
      + 'table.')));
  x(root, 'progress').append(done);

  const st = sc.stats;
  const reached = sc.reached || [], other = sc.other || [];
  // Two rows under two headings, rather than seven cards in one row that wraps
  // six-and-one. They are not the same kind of number: the first row is the
  // answer, the second is how much of the repository the answer covers — and
  // the second one is the one that decides whether the first can be believed.
  const box = x(root, 'stats');
  const statCard = ([l, v, colour, sub]) => el('div', { className: 'stat' },
    el('span', { className: 'lbl', textContent: l }),
    el('div', { className: 'v', textContent: String(v), style: colour ? `color:${colour}` : '' }),
    el('div', { className: 's', textContent: sub }));

  box.append(el('span', { className: 'lbl', style: 'display:block;margin-bottom:10px',
    textContent: 'What the change reaches' }));
  // One grid, not two. The second row used to hold one or two cards in a
  // five-column grid of its own, which stranded them on a line looking like an
  // afterthought — and these are the two most alarming numbers on the screen.
  // Worst first, so that when there are more cards than fit a row it is the
  // mildest one that wraps. The two red ones used to sit in a grid of their own
  // underneath, which stranded the most alarming number on the screen on a line
  // by itself looking like an afterthought.
  const reach = el('div', { className: 'stats' });
  [['Production tables at risk', st.productionTables, st.productionTables ? 'var(--red)' : 'var(--green)', 'On your published-table list'],
   // Kept OUT of "production tables at risk" on purpose. Nothing about these
   // tables' columns changes — the job that fills them stops running — and one
   // number covering two different kinds of impact is a number that means
   // neither. Shown only when there are some.
   ...(st.productionStopsLoading
     ? [['Published tables that stop refreshing', st.productionStopsLoading,
         'var(--red)', 'Their columns do not change — their data stops']] : []),
   // A file delivered to a bucket is not a published table, and folding the two
   // counts together would make both of them mean nothing. Whoever reads that
   // file is outside this repository, which is exactly why it needs saying: no
   // scan of this repository will ever find them.
   ...(st.feedsBroken
     ? [['Deliveries out of the warehouse', st.feedsBroken,
         'var(--red)', 'Files another team reads — tell them']] : []),
   ['Other tables reached', st.tablesReached ?? 0, (st.tablesReached ? 'var(--amber)' : ''), 'The chain ends at these'],
   ['Attributes impacted', st.attributesImpacted, '', 'Of those you confirmed'],
   ['Files to change', st.filesWithImpact, '', `Of ${sc.filesScanned} scanned`],
   // "Across every table reached" is load-bearing: the summary counts only the
   // usages feeding a published table, so without it this card and that sentence
   // give two different numbers for the same thing one screen apart.
   ['Breaking usages', st.breakingUsages, st.breakingUsages ? 'var(--amber)' : '', 'Across every table reached'],
  ].forEach(c => reach.append(statCard(c)));
  box.append(reach);

  const uncovered = [
    ['To check by hand', st.couldNotRead, st.couldNotRead ? 'var(--amber)' : '', 'Ripple could not follow these'],
  ];
  // A trail Ripple gave up on is not a trail that ended, and a table it cannot
  // see inside is not a table it has read. Both used to be invisible on this
  // screen, so a result built on either looked exactly like one built on the
  // whole picture.
  if (st.trailsCutShort) {
    uncovered.push(['Trails cut short', st.trailsCutShort, 'var(--red)',
      `Stopped at ${sc.maxHops} renames deep`]);
  }
  if (st.tablesNotVisible) {
    // Some of these are not SELECT * at all — they are a whole table copied or
    // renamed into another. This card used to say SELECT * about all of them,
    // one card above the card that said "copied or renamed", so the screen
    // contradicted itself about the same two tables.
    const anyCopy = (sc.starTables || []).some(t => t.how);
    const anyStar = (sc.starTables || []).some(t => !t.how);
    uncovered.push(['Tables not fully readable', st.tablesNotVisible, 'var(--amber)',
      anyCopy && anyStar ? 'Copied whole, or SELECT * — no column list'
        : anyCopy ? 'Copied or renamed whole — no column list'
        : 'Built with SELECT * — no column list']);
  }
  // Only ever shown when there are some. A "0 never opened" card would be a
  // reassurance nobody asked for.
  if (st.neverOpened) {
    uncovered.push(['Never opened', st.neverOpened, 'var(--red)', 'Not on this machine, or path too long']);
  }
  if (S.health?.repo?.inSkippedDirs) {
    uncovered.push(['In folders Ripple skips', S.health.repo.inSkippedDirs, 'var(--amber)',
      (S.health.repo.skippedDirNames || []).join(', ')]);
  }
  // A file type Ripple does not open is exactly as unread as a folder it was
  // told to skip. Seen on the rendered screen and nowhere else: the green
  // "Every file was opened and read" note sat DIRECTLY ABOVE the card saying a
  // notebook had never been looked inside. Counting it here puts it in the row
  // and takes that note away, which is the same fix twice.
  const unopenedTypes = (sc.fileTypesUnopened || []).reduce((n, t) => n + t.count, 0);
  if (unopenedTypes) {
    uncovered.push(['Types Ripple does not open', unopenedTypes, 'var(--amber)',
      (sc.fileTypesUnopened || []).map(t => t.ext || 'no extension').join(', ')]);
  }
  box.append(el('span', { className: 'lbl', style: 'display:block;margin:22px 0 10px',
    textContent: 'What this result does not cover' }));
  const gaps3 = el('div', { className: 'stats' });
  uncovered.forEach(c => gaps3.append(statCard(c)));
  box.append(gaps3);
  // Only a reassurance when there was something to be reassured about. "Every
  // file was opened and read" is true of no files at all, and reads as a clean
  // bill of health for a repository that was never there.
  if (!st.couldNotRead && !unopenedTypes && uncovered.length === 1 && !nothingRead) {
    gaps3.append(el('div', { className: 'note good', style: 'grid-column:span 2;align-self:stretch;display:flex;align-items:center' },
      el('div', {}, el('b', { style: 'display:block', textContent: 'Every file was opened and read.' }),
        'Nothing was skipped, and nothing was left for a person to follow by hand.')));
  }

  // Before the findings, not after them: this is the card that says how much of
  // the repository the findings are a statement about.
  renderNeverOpened(box, sc);
  renderTrailGaps(box, sc);

  const groups = x(root, 'groups');
  groups.append(el('span', { className: 'lbl', style: 'display:block;margin-bottom:2px',
    textContent: 'The findings' }));
  // The clean result is only ever offered when there is genuinely nothing:
  // no production table, no other table, and no loose usage anywhere. Anything
  // less than that and a green tick is the tool lying to your face.
  if (nothingRead) {
    groups.append(el('div', { className: 'note bad', style: 'padding:18px 22px' },
      el('b', { style: 'display:block;font-size:15px', textContent: 'No files were read, so nothing was searched' }),
      el('div', { style: 'margin-top:5px', textContent:
        'This is not a result about your pipeline — it is a result about an empty folder. '
        + 'Point Ripple at the folder holding the code on the settings screen, then run the '
        + 'scan again.' })));
  } else if (sc.lookupFailed) {
    // Not the same answer as the green tick below, and it used to print as if
    // it were. "No table is built from them, and no code reads them" is a
    // finished answer about a real column. Ripple never met this name as a
    // column at all, so it has not answered the question — it has failed to
    // ask it, and a typo shipped as "no impact".
    groups.append(el('div', { className: 'note warn', style: 'display:flex;align-items:center;gap:14px;padding:18px 22px' },
      el('span', { textContent: '?', style: 'width:30px;height:30px;border-radius:50%;background:var(--amber);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0' }),
      el('div', {}, el('b', { textContent: 'Ripple never met these column names, so nothing was checked', style: 'display:block' }),
        el('div', { style: 'margin-top:3px', textContent: 'This is not "the change is safe" — it is "the question was not answered". The columns Ripple did read on that table are listed below; if one of them is what you meant, scan again for that name.' }))));
  } else if (!sc.groups.length && !reached.length && !other.length) {
    // "No table is built from them, and no code reads them" is a claim about
    // the WHOLE repository, and it was printed in green directly above a card
    // saying three files could not be read. Those two cannot both be true. Where
    // anything at all went unread the claim is narrowed to what Ripple could
    // read, and the box stops being a green tick — a reassuring sentence may not
    // appear while a gap is known.
    const clear = sc.coverage?.complete;
    const gaps = (sc.coverage?.gaps || []).length;
    groups.append(el('div', { className: 'note ' + (clear ? 'good' : 'info'),
      style: 'display:flex;align-items:center;gap:14px;padding:18px 22px' },
      el('span', { textContent: clear ? '✓' : '·',
        style: 'width:30px;height:30px;border-radius:50%;flex-shrink:0;color:#fff;font-weight:700;'
          + 'display:flex;align-items:center;justify-content:center;'
          + `background:var(${clear ? '--green' : '--blue'})` }),
      why(el('b', { textContent: clear
          ? 'Nothing in this repository uses these attributes'
          : `Nothing Ripple could read uses these attributes — ${gaps} gap${gaps === 1 ? '' : 's'} below` }),
        'what a clean result means',
      clear
        ? 'Nothing here builds a table from these attributes, and nothing here reads them. '
          + 'Worth checking that the names below are the ones you meant.'
        : 'Nothing that Ripple could read uses these attributes. But there are places it could '
          + 'not see into, listed below, so this is not the same as "nothing uses them". Check '
          + 'the names first, then check those gaps.')));
  }
  // With nothing on the production list, the first table the change reaches is
  // the most important thing on the screen, so it opens rather than sitting
  // shut behind a caret like a footnote.
  if (!sc.groups.length && reached.length && S.openGroup === 'p0') S.openGroup = 'r0';
  drawGroups(groups, sc.groups, 'p', 'Production table', '',
             'production table', 'production tables');

  if (reached.length) {
    // These used to be thrown away. A chain that ends at a table nobody has
    // told Ripple is published is not a chain that goes nowhere.
    groups.append(el('div', { className: 'note warn', style: 'margin-top:20px' },
      why(el('b', { textContent: `The change reaches ${reached.length} more table${reached.length === 1 ? '' : 's'}, `
          + `${sc.groups.length ? 'beyond the ones above' : 'none of them on your published list'}` }),
        'why these are not called production',
      'Ripple calls a table published only when its name is on your published-table list. '
      + 'These are not on it, so Ripple cannot tell you whether anyone outside your team reads '
      + 'them. If they are yours, add them on Settings & checks and scan again.')));
    drawGroups(groups, reached, 'r', 'Chain ends here', 'background:var(--amber);color:#fff',
               'table the chain ends at', 'tables the chain ends at');
  }

  if (other.length) {
    const card = el('div', { className: 'card clip', style: 'margin-top:20px' });
    card.append(el('div', { className: 'chead' },
      el('b', { textContent: other.length === 1
        ? '1 more usage that builds no table'
        : `${other.length} more usages that build no table` })));
    const p = el('div', { className: 'pad lg' });
    // "Builds no table" is true of all of these and only tells the whole story
    // about some of them. An EXPORT DATA writes no table either — and Ripple
    // knows exactly where it delivers to, and says so on its own card lower
    // down. Telling somebody here that the destination is "somewhere it cannot
    // see" contradicts that card by two paragraphs.
    const exports = other.filter(r => r.feed).length;
    p.append(why(
      el('span', { className: 'prose', textContent: other.length === 1
        ? 'A real usage, in code that builds no table.'
        : 'Real usages, in code that builds no table.' }),
      'usages that build no table',
      'The attribute is read here, but this code creates no table Ripple can name — it is a '
      + 'plain query, or the destination is set somewhere Ripple cannot see. These are real '
      + 'usages all the same.',
      exports
        ? `${exports === 1 ? 'One of these writes' : `${exports} of these write`} a file out of `
          + 'the warehouse instead. The destination is on the row, and again further down.'
        : null));
    other.forEach((r, ri) => {
      const key = `o${ri}`, ro = S.openRow === key;
      const line = el('div', { style: 'display:flex;gap:10px;align-items:baseline;margin-top:10px;flex-wrap:wrap;cursor:pointer' },
        el('span', { className: 'chip mono', textContent: r.file }),
        el('span', { className: 'badge sm ' + (r.breaking ? 'red' : 'grey'), textContent: r.logic }),
        r.feed
          ? el('span', { className: 'badge sm red', textContent: '→ ' + r.feed })
          : null,
        el('span', { className: 'small muted', textContent: `on ${r.attr}` }));
      line.onclick = () => { S.openRow = ro ? null : key; render(); };
      p.append(line);
      if (ro) p.append(detailFor(r));
    });
    card.append(p);
    groups.append(card);
  }

  renderStopsLoading(groups, sc);
  renderFeeds(groups, sc);

  const gapBox = x(root, 'gaps');
  gapBox.innerHTML = '';
  gapBox.append(el('span', { className: 'lbl', style: 'display:block;margin:26px 0 2px',
    textContent: 'How to check this result' }));
  renderCoverage(gapBox, sc);
  renderChecks(gapBox, sc);
  renderGaps(gapBox, sc);
  x(root, 'next').onclick = () => goto(5);
}

/* A run of table cards, with a readable number of them drawn.

````

## Paste 23 of 25

### web/app.js — piece 3 of 5

Add this to the END of `web/app.js`, straight after what is already there. Do not start a new file. Do not re-type anything above.

````javascript
   Measured on a repository the size of the one this was built for: following a
   key column reaches over two hundred tables, and two hundred identical
   collapsed cards is a page nobody scrolls to the end of — so the tables at the
   bottom of it are, in practice, hidden. Nothing is dropped: the ones with the
   most impacts are drawn (they are sorted that way), and every remaining table
   is named, with its count, in a list underneath. */
const GROUPS_DRAWN = 20;

function drawGroups(box, list, prefix, tag, tagStyle, one, many) {
  list.slice(0, GROUPS_DRAWN).forEach((g, gi) =>
    box.append(groupCard(g, `${prefix}${gi}`, tag, tagStyle)));
  const rest = list.slice(GROUPS_DRAWN);
  if (!rest.length) return;
  const card = el('div', { className: 'card pad lg', style: 'margin-top:16px' });
  card.append(why(
    el('span', { className: 'lbl', textContent:
      `${rest.length} more ${rest.length === 1 ? one : many}` }),
    'why only ' + GROUPS_DRAWN + ' are drawn as cards',
      `Every table is still counted in the analysis. Only the ${GROUPS_DRAWN} with the most `
      + 'impacts get a card of their own; the rest are named here with their counts.'));
  const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
  rest.forEach(g => chips.append(el('span', { className: 'chip mono',
    textContent: `${g.prod} · ${g.rows.length}` })));
  card.append(chips);
  box.append(card);
}

/* One production table, or one table a chain ends at. The same rows either
   way -- what differs is what Ripple is able to claim about the table. */
function groupCard(g, key, tag, tagStyle) {
  const card = el('div', { className: 'card clip group' });
  const open = S.openGroup === key;
  const head = el('div', { className: 'ghead' + (open ? ' open' : '') });
  head.append(
    el('span', { className: 'tag', textContent: tag, style: tagStyle }),
    el('div', { className: 'mono', textContent: g.prod, style: 'font-size:15px;font-weight:600' }),
    el('span', { className: 'badge grey', textContent: `${g.rows.length} impact${g.rows.length === 1 ? '' : 's'}` }),
    el('span', { className: 'small muted', textContent: g.note }),
    el('span', { className: 'caret', textContent: '›' }));
  head.onclick = () => { S.openGroup = open ? null : key; S.openRow = null; render(); };
  card.append(head);
  if (!open) return card;
  const hr = el('div', { className: 'rowhead' });
  ['Table it lands in', 'Attribute impacted', 'Alias used', 'What the code does', 'Value', ''].forEach(h => hr.append(el('span', { textContent: h })));
  card.append(hr);
  g.rows.forEach((r, ri) => {
    const rowKey = `${key}-${ri}`, ro = S.openRow === rowKey;
    const row = el('div', { className: 'row' + (ro ? ' open' : '') });
    // Two hops down the chain the column is no longer called what the person
    // typed into the notification, so a row can read "mc" on a scan of three
    // attributes with nothing to say which of them it belongs to. The
    // attribute that was asked about is named whenever it differs.
    const other = (r.roots || []).filter(n => n.toUpperCase() !== (r.attr || '').toUpperCase());
    row.append(
      el('span', { className: 'mono', textContent: r.inter, style: 'font-weight:600;font-size:13px;min-width:0;overflow-wrap:break-word' }),
      el('span', { style: 'min-width:0' },
        el('span', { className: 'mono', textContent: r.attr,
          style: 'font-size:13px;font-weight:600;color:var(--blued);overflow-wrap:break-word' }),
        other.length
          ? el('span', { className: 'small faint', style: 'display:block;margin-top:3px',
              textContent: 'from ' + other.join(', ') })
          : null),
      el('span', {}, el('span', { className: 'chip alias', textContent: r.alias })),
      // The second badge goes inside the same cell rather than adding a column,
      // so a row that has it lines up with the rows that do not.
      el('span', {}, el('span', { className: 'badge sm ' + (r.breaking ? 'red' : 'grey'), textContent: r.logic }),
        r.certain === false
          ? el('span', { className: 'badge sm grey', style: 'margin-left:6px',
              textContent: 'table not stated' })
          : null,
        // The chain got here through a table whose column list is not written
        // down. The row is real; what is inferred is that the column still
        // travels under this name on the far side of the star.
        r.inferredHops
          ? el('span', { className: 'badge sm amber', style: 'margin-left:6px',
              textContent: r.viaStar ? 'column list not visible' : 'inferred' })
          : null,
        // The line holds a quoted string, not the statement this row describes.
        r.builtAsText
          ? el('span', { className: 'badge sm amber', style: 'margin-left:6px',
              textContent: 'run as text' })
          : null),
      el('span', {}, el('span', { className: 'badge sm ' + (r.mode === 'Direct pull' ? 'blue' : 'violet'), textContent: r.mode })),
      el('span', { className: 'caret', textContent: '›' }));
    row.onclick = () => { S.openRow = ro ? null : rowKey; render(); };
    card.append(row);
    if (ro) card.append(detailFor(r));
  });
  return card;
}

/* Attribute by attribute: what was looked for and what came back.
   "It said no impact and I have no way to check" is answered here rather than
   by asking anyone to trust the headline. An attribute that is not written
   down anywhere in the repository looks nothing like one that is used in nine
   files, and both used to end up behind the same green tick. */
/* How much of this trail Ripple could see, in the counts it already had.

   Every number here was being worked out and then thrown away. "No impact" was
   computed from one thing only — whether any finding was breaking — so a scan
   that followed every step of the chain and a scan with three invisible tables
   on it printed the same three words. This is not a score and not a percentage:
   there is no honest denominator for "how much of a trail exists", and putting
   a precise-looking number on a guess is the one thing this tool may not do. */
function renderCoverage(box, sc) {
  const cov = sc.coverage;
  // Nothing was followed, so there is no coverage to report — and "every step
  // of every trail was read" over a trail that does not exist is the same
  // reassuring nonsense in longer words.
  if (!cov || sc.lookupFailed) return;
  const card = el('div', { className: 'card pad lg', style: 'margin-top:12px' });
  if (cov.complete) {
    card.append(why(
      el('b', { textContent: 'Every step of every trail above was read out of the SQL' }),
      'what "every step was read" means',
      'Ripple read the real SQL for every step of every trail above. Nothing was skipped, '
      + 'guessed at, or cut short. That is true of the files it read, and of nothing outside '
      + 'them.'));
    box.append(card);
    return;
  }
  const list = el('div', { style: 'margin-top:10px' });
  cov.gaps.forEach(g => list.append(el('div', {
    className: 'small', style: 'margin-top:6px;line-height:1.55' },
    el('b', { textContent: String(g.count) + ' ' }),
    g.what)));
  // No count in this heading. It would be counting KINDS of gap, sitting above
  // lines that count files and findings, so "1 place ... 3 files" read as two
  // numbers for one thing. The badge beside the risk word carries the count.
  card.append(why(
    el('span', { className: 'lbl', textContent: 'Where Ripple could not see through' }),
    'why these are counts and not a score',
      'Each of these is somewhere Ripple could not see through. They are given as counts, not '
      + 'as a percentage: nobody knows how big the whole picture is, so a percentage would be '
      + 'made up.'));
  card.append(list);
  box.append(card);
}

function renderChecks(box, sc) {
  const rows = sc.attributes || [];
  if (!rows.length) return;
  const card = el('div', { className: 'card clip', style: 'margin-top:20px' });
  card.append(el('div', { className: 'chead' },
    why(el('b', { textContent: 'Every attribute you asked about' }),
      'how to check a scan',
      'If a result looks too quiet, start here. An attribute that is not written down anywhere '
      + 'in your code is the usual reason a scan comes back clean.')));
  const p = el('div', { className: 'pad lg' });
  rows.forEach(a => {
    const used = a.found > 0;
    // A name Ripple never met as a column on ANY table is not a column with no
    // impact — it is a question that never got asked. Said first, and in amber,
    // because the two used to be the same grey line.
    const badge = a.reachesProduction
      ? ['red', 'reaches a published table']
      : used
        ? ['amber', `used in ${a.files} file${a.files === 1 ? '' : 's'}`]
        : a.lookupFailed
          ? ['amber', 'Ripple never saw a column of this name']
          : a.mentionedIn
          ? ['grey', `named in ${a.mentionedIn} file${a.mentionedIn === 1 ? '' : 's'}, never read from`]
          : ['grey', 'this name is not in the repository at all'];
    p.append(el('div', { style: 'display:flex;gap:10px;align-items:baseline;margin-top:10px;flex-wrap:wrap' },
      el('span', { className: 'chip mono', textContent: `${a.table}.${a.attr}` }),
      el('span', { className: 'badge sm ' + badge[0], textContent: badge[1] }),
      (a.endsAt || []).length
        ? el('span', { className: 'small muted', textContent: 'ends at ' + a.endsAt.join(', ') })
        : null,
      // Kept apart from "ends at" on purpose. They read the same and mean
      // opposite things: one is where the code ran out, the other is where
      // Ripple stopped looking.
      (a.cutShortAt || []).length
        ? el('span', { className: 'badge sm red',
            textContent: 'still going at ' + a.cutShortAt.join(', ') })
        : null));
    // The instant self-correction. Printing back the columns Ripple DID read on
    // the table turns a silent wrong answer into a spelling mistake somebody
    // spots in two seconds. An empty list is a different answer again and says
    // so: it means Ripple has no column list for this table at all, so "I never
    // saw it" is not the same as "it is not there".
    if (a.lookupFailed) {
      // The columns Ripple DID read stay on the page: that list is what turns a
      // silent wrong answer into a spelling mistake somebody spots in seconds.
      const cols = a.tableColumns || [];
      const box = el('div', { className: 'note warn', style: 'margin:8px 0 0 4px' });
      box.append(why(
        el('b', { textContent: `Nothing was checked for ${a.attr}.` }),
        'nothing was checked for ' + a.attr,
      cols.length
        ? `Ripple read ${a.table} and never found a column called ${a.attr} — on it, or on `
          + 'anything else here. The columns it did find are listed below. If one of those is '
          + 'the one you meant, scan again for that name.'
        : `Ripple never found a column called ${a.attr} anywhere here, and nothing in your code `
          + `writes down what the columns of ${a.table} are. So this is not "that column is `
          + 'safe" — it is "Ripple could not check". Check the spelling, and check that this '
          + 'table is built in this repository at all.'));
      if (cols.length) {
        box.append(el('div', { className: 'small', style: 'margin-top:8px;line-height:1.55' },
          `What Ripple did read on ${a.table}: `, el('span', { className: 'mono', textContent: cols.join(', ') })));
      }
      p.append(box);
    }
    if ((a.cutShortAt || []).length) {
      p.append(el('div', { className: 'small muted', style: 'margin:6px 0 0 4px' },
        why(el('span', { textContent: `Ripple stopped at ${sc.maxHops} renames — the trail had `
          + 'not finished.' }),
          'a trail that was cut short',
      'Whether it ends at a published table is not something this scan can tell you. Use the '
      + 'button above to follow it further.')));
    }
    if ((a.notVisible || []).length) {
      // Both counts stay on the page. Only the "why" moved.
      p.append(el('div', { className: 'small muted', style: 'margin:6px 0 0 4px;line-height:1.55',
        textContent: `Goes through ${a.notVisible.join(', ')} — ${a.inferred} finding`
          + `${a.inferred === 1 ? '' : 's'} past that point ${a.inferred === 1 ? 'is' : 'are'} `
          + 'worked out, not read.' }));
    }
    // How widely the name is used as a name. A scan for a column half the
    // warehouse shares looks identical on screen to a scan for one only this
    // table has, and the two are not remotely the same answer: the first
    // produces a long list because the name is everywhere, the second because
    // something is badly wrong. Only said when the name really is widespread —
    // "this name is in 1 of 60 tables" is a fact nobody needs.
    // Two conditions, and both matter. A big share says the name is common;
    // a real count says the repository is big enough for that to mean anything.
    // "3 of the 3 tables" is a fact about a folder with three files in it, and
    // printing it there teaches somebody to skip the line in the repository
    // where it is the whole point.
    if (a.nameInTables >= 8 && a.tablesRead) {
      const share = a.nameInTables / a.tablesRead;
      if (share >= 0.25) {
        p.append(el('div', { className: 'small muted', style: 'margin:6px 0 0 4px' },
          why(el('span', { textContent: `"${a.attr}" is a column name in ${a.nameInTables} of the `
            + `${a.tablesRead} tables Ripple could read.` }),
            'a column name that is everywhere',
      `Plenty of tables use this column name. The findings only follow it out of ${a.table}, so `
      + 'a long list here means the name is common — not that the change is bigger.')));
      }
    }
    if (a.uncertain) {
      p.append(el('div', { className: 'small muted', style: 'margin:6px 0 0 4px' },
        why(el('span', { textContent: `${a.uncertain} of these `
          + `${a.uncertain === 1 ? 'is' : 'are'} marked "table not stated".` }),
          'rows where the table is inferred',
      `On these lines the SQL does not say which table the ${a.attr} came from, and more than `
      + 'one table in the same statement has a column of that name. The usage is real; which '
      + 'table it belongs to is Ripple\u2019s best guess.')));
    }
  });
  card.append(p);
  box.append(card);
}

/* The address of a finding in the connected repository, or nothing at all.
   Points at the first line that actually matched, not the top of the file. */

function detailFor(r) {
  const d = el('div', { className: 'detail' });
  d.append(el('div', { className: 'note ' + (r.noLocalFix ? 'bad' : r.breaking ? 'warn' : 'info') },
    el('b', { textContent: r.noLocalFix ? 'No local fix — the upstream team must supply a replacement. ' : r.breaking ? 'This breaks. ' : 'Changes, but does not break. ' }),
    r.impact));
  // The usage is on that line and it is real. What is inferred is which table
  // the column came from, and in a warehouse where the same key columns are in
  // nearly every table that is worth stating rather than glossing.
  if (r.certain === false) {
    d.append(el('div', { className: 'note info', style: 'margin-top:10px' },
      el('b', { textContent: 'The table is inferred here. ' }),
      `This statement reads more than one table with a column called ${r.attr}, and the SQL `
      + `does not say which one this is. Ripple has counted it as ${r.from}'s. Worth a look at `
      + 'the code below before acting on it.'));
  }
  // How much of the path to this row was read and how much was worked out. A
  // row two hops past a SELECT * is exactly as real as the code below it, and
  // exactly as uncertain about what the column is called by the time it lands.
  if (r.inferredHops) {
    d.append(el('div', { className: 'note warn', style: 'margin-top:10px' },
      el('b', { textContent: r.viaStar
        ? 'This step is a SELECT *. '
        : `${r.inferredHops} step${r.inferredHops === 1 ? '' : 's'} on the way here could not be read. ` }),
      r.viaStar
        ? `The statement takes every column, so ${r.attr} is carried into ${r.inter} without `
          + `ever being named. The hop is real — that is what ${r.copiedBy || 'SELECT *'} does — `
          + 'but Ripple cannot read the column list of the table it builds, so anything past '
          + 'this point is worked out rather than read.'
        : `A table earlier in this chain takes every column at once, so its column list is not `
          + `in the code. This row is a real usage on a real line; what Ripple cannot promise is `
          + `that ${r.attr} is still the name the column carries by the time it gets here.`));
  }
  // The statement is inside quotes on the line below. Said here as well as on
  // the card, because the code shown underneath is a string and looks nothing
  // like the CREATE this row describes — and a row somebody cannot verify on
  // the line it points at is a row they dismiss.
  if (r.builtAsText) {
    d.append(el('div', { className: 'note warn', style: 'margin-top:10px' },
      el('b', { textContent: `Written as text and run — ${r.builtAsText}. ` }),
      'The line below holds this statement as a quoted string, so the code shown is the '
      + 'string rather than the statement. Ripple read what is inside the quotes and it is '
      + 'complete SQL, which is why this row exists. If anything is added to that text when '
      + 'the job runs, this scan has not seen it.'));
  }
  const code = el('div', { className: 'code' });
  const head = el('div', { className: 'f' },
    el('span', { className: 'name', textContent: r.file }),
    el('span', { className: 'lang', textContent: r.lang }));
  // Only offered when Ripple genuinely knows the address of this code. On a
  // local folder there is nothing to link to, so no link is shown.
  code.append(head);
  const body = el('div', { className: 'body' });
  (r.lines || []).forEach(ln => {
    const line = el('div', { className: 'ln' + (ln.hit ? ' hit' : '') },
      el('span', { className: 'n', textContent: String(ln.n) }),
      el('span', { className: 't', textContent: ln.t }));
    // why this line matched, sitting on the line itself rather than under it
    if (ln.hit) line.append(el('span', { className: 'why', textContent: ln.hit }));
    body.append(line);
  });
  code.append(body);
  d.append(code);
  return d;
}

/* Files that were never opened at all.

   Not the same thing as a file that was read and not understood, and much
   worse. A file Ripple could not parse is on the "check by hand" list and
   somebody goes and looks at it. A file that was never opened leaves no trace
   anywhere: the finding list is shorter, the tick is green, and nothing on the
   screen is false — it is just answering a question about half a repository.

   So this says the number, says why, and says the one thing that fixes it. */
function neverOpenedNote(heldOnline, tooLong) {
  const total = (heldOnline || 0) + (tooLong || 0);
  if (!total) return el('span', { className: 'hide' });
  // Every count and every reason stays on the page. Only "why it happened" and
  // "how to fix it" move behind the button — this is the one card that decides
  // whether the numbers above it can be believed at all.
  const note = el('div', { className: 'note warn', style: 'margin-top:12px' });
  const reasons = [
    heldOnline ? `${heldOnline} held online-only by OneDrive` : null,
    tooLong ? `${tooLong} with a path too long for Windows` : null,
  ].filter(Boolean);
  note.append(why(
    el('b', { style: 'font-size:14px',
      textContent: `${total} file${total === 1 ? '' : 's'} here ${total === 1 ? 'was' : 'were'} `
        + 'never opened — ' + reasons.join(', ') }),
    'files that were never opened',
      'Nothing in these files was read, so nothing in them can appear in this answer.',
      heldOnline
        ? 'OneDrive is keeping them in the cloud rather than on this machine. To fix it: '
          + 'right-click the repository folder in File Explorer, choose "Always keep on this '
          + 'device", wait for OneDrive to finish, then read the repository again.'
        : null,
      tooLong
        ? 'Windows cannot open a file whose path is this long. To fix it: move the repository '
          + 'nearer the top of the drive — C:\\repo rather than a deep folder inside '
          + 'Documents — then read it again.'
        : null));
  return note;
}

/* Files that were never opened. Drawn directly under the counts rather than at
   the bottom of the page, because it is the one card that decides whether every
   number above it can be believed — and the bottom of a long page is where a
   caveat goes to be missed. */
function renderNeverOpened(box, sc) {
  if (sc.heldOnline?.length || sc.pathTooLong?.length) {
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(neverOpenedNote(sc.heldOnline?.length || 0, sc.pathTooLong?.length || 0));
    const names = [...(sc.heldOnline || []), ...(sc.pathTooLong || [])];
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:12px' });
    names.slice(0, 300).forEach(f => chips.append(el('span', { className: 'chip mono', textContent: f })));
    card.append(chips);
    if (names.length > 300) {
      card.append(el('div', { className: 'small muted', style: 'margin-top:8px',
        textContent: `and ${names.length - 300} more, not listed here to keep this page readable.` }));
    }
    box.append(card);
  }
  // A whole folder of code walked past because of what it is called. In most
  // repositories "build" and "target" hold generated output; in a few they hold
  // the pipeline, and then this is a scan of half a repository with a green
  // tick on it.
  // Only when the scan itself did not report them. The scan's own card lists the
  // file names and the folders; this one has the same count and no names, and
  // the two sat ten cards apart on the same screen saying the same thing about
  // the same 310 files — with the stat card above making it three times.
  const skipped = sc.skippedInFolders?.length ? 0 : (S.health?.repo?.inSkippedDirs || 0);
  if (skipped) {
    box.append(el('div', { className: 'note warn', style: 'margin-top:16px' },
      why(el('b', { style: 'font-size:14px',
          textContent: `${skipped} file${skipped === 1 ? '' : 's'} Ripple can read `
            + `${skipped === 1 ? 'was' : 'were'} skipped — in `
            + (S.health.repo.skippedDirNames || []).join(', ') }),
        'files skipped for the folder they are in',
      'Folders with these names usually hold generated copies of code, so Ripple walks past '
      + 'them. If your real pipeline lives in one, nothing in it was read and nothing in it can '
      + 'appear in this answer.')));
  }
}

/* Three ways a trail can be shorter than the truth, all of them invisible until
   now, and all of them producing a calm answer over less than the whole picture.

   These are drawn on the RESULT, beside the findings they qualify. Two of them
   were already known somewhere else in the app — the repository screen has
   listed the tables built with SELECT * for months — and a warning on another
   screen is a warning nobody reads while they are deciding whether to worry. */
function renderTrailGaps(box, sc) {
  // 1. The hop limit stopped the walk. This is a setting, and until now it was
  //    reported as a fact: "the chain ends at t4 and does not reach production".
  if (sc.cutShort?.length) {
    const deeper = Math.min((sc.maxHops || 4) * 2, 25);
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px;border-color:var(--redln)' });
    card.append(why(
      el('b', { style: 'font-size:14px', textContent:
        `${sc.cutShort.length} trail${sc.cutShort.length === 1 ? '' : 's'} `
        + 'stopped because of a setting, not because the code ran out' }),
      'trails cut short',
      `Ripple follows a column through ${sc.maxHops} renames and then stops. `
      + `${sc.cutShort.length === 1 ? 'This one had' : 'These had'} not finished. Anything past `
      + 'that point was never looked at, so this result cannot tell you whether they reach a '
      + 'published table.'));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:12px' });
    sc.cutShort.forEach(c => chips.append(el('span', { className: 'chip mono',
      textContent: `${c.table} · ${c.attr}` })));
    card.append(chips);
    if (sc.maxHops) {
      // To the END, not twice as far. Doubling was a button that could be
      // pressed and pressed and never finish: measured on a 36-hop chain, ten
      // renames cut the trail short, twenty cut it short, and twenty-five --
      // the deepest this ever offered -- cut it short as well, for the same
      // empty answer each time. There is no number worth offering, so it offers
      // the only thing that answers the question.
      const again = el('button', { className: 'ghost', style: 'margin-top:14px',
        textContent: 'Follow these to the end of the code' });
      again.onclick = () => runScan(0);
      card.append(el('div', { style: 'margin-top:14px' },
        why(again, 'what following them to the end costs',
      'This runs the scan again on code Ripple has already read. No file is opened a second '
      + 'time, and nothing on the settings screen changes.')));
    }
    box.append(card);
  }

  // 2. A table built with SELECT * carries every column and names none of them.
  if (sc.starTables?.length) {
    const n = sc.starTables.length;
    // Some of these are not SELECT * at all — they are a staging table promoted
    // into a published one with COPY, CLONE, LIKE or RENAME. Ripple follows them
    // the same way, because they do the same thing, but the card has to name the
    // word the file actually uses or it describes a statement that is not there.
    const copies = sc.starTables.filter(s => s.how);
    // Not a star in the file either — a placeholder where the column list goes,
    // filled in by the job at run time. Ripple used to read it as a column
    // called "cols" and report the published table as having exactly that one.
    const holes = sc.starTables.filter(s => s.filledIn);
    const stars = sc.starTables.length - copies.length - holes.length;
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(why(
      el('b', { style: 'font-size:14px', textContent:
        `${n} table${n === 1 ? '' : 's'} the column passes through ${n === 1 ? 'has' : 'have'} no column list to read` }),
      'tables with no column list on the trail',
      // "Either way" only makes sense when there ARE two ways. On a scan with
      // one kind it referred back to nothing.
      (copies.length && stars
        ? 'Some of these take every column at once with a SELECT *; the rest are a whole table '
          + 'copied or renamed into another. Either way, the code never writes down what their '
          + 'columns are called. Your attribute '
        : copies.length
        ? 'These are a whole table copied or renamed into another, so the code never writes '
          + 'down what their columns are called. Your attribute '
        : 'These take every column at once with a SELECT *, so the code never writes down what '
          + 'their columns are called. Your attribute ')
      + 'really does travel through — what Ripple cannot promise is the name it carries on the '
      + 'other side.',
      holes.length
        ? 'Some of these do not say SELECT * at all. The file leaves a gap where the column '
          + 'list goes and the job fills it in when it runs, so the list is never in the file '
          + 'to read.'
        : null));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:12px' });
    sc.starTables.forEach(s => chips.append(el('span', { className: 'chip mono',
      textContent: s.how
        ? `${s.table} — ${s.how} of ${s.from}`
        : s.filledIn
        ? `${s.table} — column list filled in at run time, from ${s.from}`
        : `${s.table} — from ${s.from}` })));
    card.append(chips);
    box.append(card);
  }

  // 3. One name, more than one table, and nothing in the SQL to tell them apart.
  if (sc.mergedNames?.length) {
    const n = sc.mergedNames.length;
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px' });
    card.append(why(
      el('span', { className: 'lbl', textContent:
        `${n} table name${n === 1 ? '' : 's'} here may stand for more than one table` }),
      'one name, more than one table',
      'Two different tables here share a name. Ripple followed both, so nothing is missed — but '
      + 'a finding under this name could be about either one. Open the file to check before '
      + 'you act on it.',
      sc.mergedNames.some(m => m.reason === 'capitals')
        ? 'BigQuery treats capital letters as significant, so two names that differ only in '
          + 'case really are two different tables there.'
        : null));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
    sc.mergedNames.forEach(m => chips.append(el('span', { className: 'chip mono',
      textContent: m.reason === 'capitals'
        ? `${m.spellings.join('  vs  ')} — same name, different capitals`
        : `${m.table} — in ${m.datasets.join(', ')}` })));
    card.append(chips);
    box.append(card);
  }

  // 4. The SQL named a family of date-sharded tables, not the one being scanned.
  //    This has to sit here, beside the findings it qualifies. Ripple used to
  //    match the name literally, asterisk and all, so a scan of a real shard
  //    matched nothing and printed a clean "no impact" — on a warehouse where
  //    date sharding is how half the source tables are read.
  if (sc.wildcardNames?.length) {
    const n = sc.wildcardNames.length;
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px' });
    card.append(why(
      el('span', { className: 'lbl', textContent:
        `${n} table${n === 1 ? '' : 's'} here ${n === 1 ? 'is' : 'are'} read through a wildcard, not by name` }),
      'tables read through a wildcard',
      'The query asks for a whole family of dated tables at once instead of naming one. The '
      + 'table you scanned is inside that family, so these usages are real — but the same '
      + 'query reads the others too, so a fix has to cover all of them.'));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
    sc.wildcardNames.forEach(w => chips.append(el('span', { className: 'chip mono',
      textContent: `${w.table} — matched by ${w.patterns.join(', ')}` })));
    card.append(chips);
    // The family name as a person says it, without the separator BigQuery
    // requires. BigQuery matches nothing here; Ripple matches it anyway so
    // that typing the name you say out loud cannot produce a clean "no
    // impact" — and then says out loud that it is a guess about what you
    // meant, because it used to ship as certain.
    const loose = (sc.wildcardNames || []).filter(w => (w.shorthand || []).length);
    if (loose.length) {
      card.append(el('div', { className: 'note warn', style: 'margin-top:12px' },
        why(el('b', { textContent: 'Some of these are the family name, not a shard — '
            + loose.map(w => `${w.table} vs ${w.shorthand.join(', ')}`).join('; ') }),
          'the family name, not a shard',
      'You scanned the family name rather than one dated table. A real query cannot read a '
      + 'table by that exact name, so Ripple matched the whole family instead — which is a '
      + 'guess about what you meant. Every row from it is marked "table not stated". To be '
      + 'exact, scan for the full name of one table.')));
    }
    box.append(card);
  }

  // 4a. One table, two files that build it from scratch. Only one of them can
  //     be the definition that runs, and nothing in the files says which. The
  //     measured case: the only finding came from a stale copy under archive/,
  //     presented as certainly as any live one, while the live definition sat
  //     under "mentions only".
  if (sc.twoDefinitions?.length) {
    const n = sc.twoDefinitions.length;
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px' });
    card.append(why(
      el('span', { className: 'lbl', textContent:
        `${n} table${n === 1 ? '' : 's'} here ${n === 1 ? 'is' : 'are'} built from scratch in more than one file` }),
      'a table built in two files',
      'Two files each build this table from scratch, so only one of them can be the one that '
      + 'really runs — and the code does not say which. Ripple followed both. Check what your '
      + 'scheduler actually runs before acting on a finding from one of them.'));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
    sc.twoDefinitions.forEach(t => chips.append(el('span', { className: 'chip mono',
      textContent: `${t.table} — ${t.files.join('  and  ')}` })));
    card.append(chips);
    box.append(card);
  }

  // 4b. Code files Ripple would have read, sitting in a folder it skips. The
  //     count used to reach the repository screen and nothing else, so a scan
  //     of a dbt project — whose target/ folder holds the SQL that actually
  //     runs — came back clean with the reason on a screen nobody looked at.
  if (sc.skippedInFolders?.length) {
    const n = sc.skippedInFolders.length;
    const where = (sc.skippedFolderNames || []).join(', ');
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(why(
      el('b', { style: 'font-size:14px', textContent:
        `${n} code file${n === 1 ? '' : 's'} ${n === 1 ? 'was' : 'were'} not read — in ${where}` }),
      'code in a skipped folder',
      `Folders called ${where} usually hold generated copies of code, so Ripple walks past `
      + 'them. Nothing in there was read. If your pipeline really runs from one of them — '
      + "dbt's target folder does — change the skip list on Settings & checks and scan again."));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:12px' });
    sc.skippedInFolders.slice(0, 200).forEach(f => chips.append(
      el('span', { className: 'chip mono', textContent: f })));
    card.append(chips);
    if (n > 200) {
      card.append(el('div', { className: 'small muted', style: 'margin-top:8px',
        textContent: `Showing the first 200 of ${n}.` }));
    }
    box.append(card);
  }

  // 4c. File types Ripple does not open at all. The repository screen has always
  //     listed these; the ANSWER never did. Measured: the middle hop of a chain
  //     sat in a .ipynb, and the scan printed "the name appears, but no lineage
  //     to a production table" with nothing beside it saying a file had been
  //     passed over. A caveat may never live on a different screen from the
  //     answer it qualifies.
  if (sc.fileTypesUnopened?.length) {
    const total = sc.fileTypesUnopened.reduce((n, t) => n + t.count, 0);
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(why(
      el('b', { style: 'font-size:14px', textContent:
        `${total} file${total === 1 ? '' : 's'} ${total === 1 ? 'is' : 'are'} of a type Ripple does not open` }),
      'file types not opened by this scan',
      'Ripple opens SQL files and the file types that usually hold SQL. It did not look inside '
      + 'these at all. If part of your chain sits in one of them, the answer stops there. '
      + 'Notebooks and Terraform files are the usual ones to check.'));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:12px' });
    sc.fileTypesUnopened.slice(0, 40).forEach(t => chips.append(
      el('span', { className: 'chip mono', textContent: `${t.ext || 'no extension'} — ${t.count}` })));
    card.append(chips);
    box.append(card);
  }

  // 5. The file builds a table but never writes its name. A dbt model is a bare
  //    SELECT — dbt names the table after the file when it runs it. Ripple
  //    follows the same rule, because without it a dbt repository produced no
  //    lineage at all: every chain came back empty and the answer was a clean
  //    "no impact". Saying so here matters — anybody who opens the file to check
  //    will not find the table name written in it.
  if (sc.namedByFile?.length) {
    const n = sc.namedByFile.length;
    // "dbt" and "Dataform" are facts — both tools name a model after its file.
    // "file" is the weaker reading: one query, no CREATE, and something runs it.
    const dbt = sc.namedByFile.filter(t => t.how !== 'file').length;
    const tools = [...new Set(sc.namedByFile.filter(t => t.how !== 'file').map(t => t.how))].join(' and ');
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px' });
    card.append(why(
      el('span', { className: 'lbl', textContent:
        `${n} table${n === 1 ? '' : 's'} here ${n === 1 ? 'is' : 'are'} named after ${n === 1 ? 'its' : 'their'} file, not by the SQL` }),
      'tables named after their file',
      (dbt === n
        ? `These are ${tools} models. A model is a query with no CREATE in front of it, and the `
          + 'tool that runs it names the table after the file. '
        : dbt
        ? `Some are ${tools} models; the rest hold one query and no CREATE. Whatever runs them `
````

## Paste 24 of 25

### web/app.js — piece 4 of 5

Add this to the END of `web/app.js`, straight after what is already there. Do not start a new file. Do not re-type anything above.

````javascript
          + 'puts the rows in a table named after the file. '
        : 'Each of these files holds one query and no CREATE. Whatever runs it puts the rows in '
          + 'a table named after the file. ')
      + 'So you will not find the table name written inside the file — only the query.'));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
    sc.namedByFile.forEach(t => chips.append(el('span', { className: 'chip mono',
      textContent: `${t.table} — from ${t.file}` })));
    card.append(chips);
    box.append(card);
  }

  // 6. SQL the file holds as a quoted string and runs as text. Ripple reads the
  //    string, so the hop is followed instead of lost — measured before this, a
  //    whole CREATE OR REPLACE TABLE of the scanned column inside an EXECUTE
  //    IMMEDIATE gave no production tables at all. But the line the rows point
  //    at holds a string, not the CREATE they describe, and somebody who opens
  //    it expecting the statement will doubt the finding rather than the label.
  if (sc.builtAsText?.length) {
    const n = sc.builtAsText.length;
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px' });
    card.append(why(
      el('span', { className: 'lbl', textContent:
        `${n} statement${n === 1 ? '' : 's'} here ${n === 1 ? 'is' : 'are'} written as text and run, not written as SQL` }),
      'SQL written as text and run',
      'The file keeps the whole statement inside quotes and hands that text to the warehouse to '
      + 'run. Ripple read what is inside the quotes, so the trail carries on. But open that '
      + 'line and you will see a quoted string, not the statement — and anything added to the '
      + 'text while the job runs is not covered here.'));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
    sc.builtAsText.forEach(t => chips.append(el('span', { className: 'chip mono',
      textContent: `${t.file}:${t.line} — ${t.how} → ${t.table}` })));
    card.append(chips);
    box.append(card);
  }

  // 7. Statements that NAME the table or the column and carry it nowhere: a
  //    search index, a vector index, a row access policy, an UNDROP. These are
  //    not lineage and are never drawn as a hop — but a policy filtering on the
  //    column stops working on the day it goes, and no lineage anywhere would
  //    ever have said so. Measured before this: the parser gave up on the whole
  //    statement, the file landed on the "check by hand" list, and nothing said
  //    which table or which column it was about.
  if (sc.referencedHere?.length) {
    const rows = sc.referencedHere;
    const named = rows.filter(r => (r.namesColumns || []).length);
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px' });
    // The count of places that name the COLUMN stays on the page: those stop
    // working on the day it changes, which is the whole reason this card exists.
    card.append(why(
      el('span', { className: 'lbl', textContent:
        `${rows.length} place${rows.length === 1 ? '' : 's'} name${rows.length === 1 ? 's' : ''} this, and carr${rows.length === 1 ? 'ies' : 'y'} it nowhere`
        + (named.length ? ` — ${named.length} name${named.length === 1 ? 's' : ''} the column itself` : '') }),
      'named here, but carried nowhere',
      (named.length
        ? `The ${named.length} that name the column itself stop working the day it changes. `
        : '')
      + 'None of these passes the column on to another table, so none of them is on a chain '
      + 'above. They are listed because nothing else on this screen would mention them.'));
    const list = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
    rows.forEach(r => list.append(el('span', { className: 'chip mono', textContent:
      `${r.verb} ${r.kind} on ${r.table}`
      + ((r.namesColumns || []).length ? ` — names ${r.namesColumns.join(', ')}` : '')
      + ` · ${r.file}:${r.line}` })));
    card.append(list);
    box.append(card);
  }
}

/* Published tables that stop being REFRESHED, rather than ones whose columns
   change. A different question, so it gets its own words and its own place —
   folding it into the findings above would make both of them vaguer.

   Why it exists: a column used only in a WHERE, a JOIN or a GROUP BY never
   reaches the table the statement builds, so the trail for that COLUMN really
   does end there, and Ripple said so and stopped. But the statement itself
   stops working on the day the column goes. The table it builds stops being
   rebuilt, and everything under it is served from data nobody is updating any
   more — which is an outage that arrives quietly, days later. */
function renderStopsLoading(box, sc) {
  const rows = sc.stopsLoading || [];
  if (!rows.length) return;
  const n = rows.length;
  box.append(el('span', { className: 'lbl', style: 'display:block;margin:26px 0 2px',
    textContent: `${n} published table${n === 1 ? '' : 's'} stop${n === 1 ? 's' : ''} being refreshed` }));
  const card = el('div', { className: 'card pad lg', style: 'margin-top:12px;border-color:var(--redln)' });
  card.append(why(
    el('b', { textContent: 'Not because a column of these changes.' }),
    'tables that stop being refreshed',
      'The change stops the job that fills these tables from running at all, so they keep '
      + 'whatever data they already held. Nobody sees an error — the numbers simply stop being '
      + 'current, and stay that way until somebody fixes the job.'));
  rows.forEach(r => {
    const line = el('div', { style: 'margin-top:14px' });
    line.append(el('div', {},
      el('span', { className: 'badge sm red', textContent: 'PRODUCTION TABLE' }),
      el('span', { className: 'mono', style: 'margin-left:10px;font-weight:600',
        textContent: r.prod })));
    line.append(el('div', { className: 'small muted', style: 'margin-top:6px;line-height:1.55' },
      'Because ',
      el('span', { className: 'mono', textContent: r.because }),
      ' stops loading. The path: ',
      el('span', { className: 'mono', textContent: (r.via || []).join(' → ') })));
    card.append(line);
  });
  if (sc.stopsLoadingCapped) {
    card.append(el('div', { className: 'note warn', style: 'margin-top:14px' },
      why(el('b', { textContent: 'This list was cut short — there may be more than these.' }),
        'why this list was cut short',
      'Ripple stopped after looking 400 tables downstream, so there may be more than these.')));
  }
  box.append(card);
}

/* A file delivered OUT of the warehouse, rather than a table inside it.

   EXPORT DATA writes a file to a bucket and somebody else's job picks it up
   every morning. It builds no table, so the trail had nothing to carry the
   column on to, and the answer read "no production table is affected" — true,
   and no use to anybody. The delivery is what breaks, and whoever reads it is
   outside this repository, so no scan of this repository will ever find them.
   That is exactly why it has to be named here. */
function renderFeeds(box, sc) {
  const rows = sc.feeds || [];
  if (!rows.length) return;
  const n = rows.length;
  box.append(el('span', { className: 'lbl', style: 'display:block;margin:26px 0 2px',
    textContent: `${n} deliver${n === 1 ? 'y' : 'ies'} out of the warehouse` }));
  const card = el('div', { className: 'card pad lg', style: 'margin-top:12px;border-color:var(--redln)' });
  card.append(why(
    el('b', { textContent: 'These are not tables — tell whoever reads them.' }),
    'deliveries out of the warehouse',
      'This writes a file to a bucket rather than a table. Whoever picks that file up is '
      + 'outside this repository, so no scan can tell you who they are. Tell them before the '
      + 'change goes live.'));
  rows.forEach(r => {
    const line = el('div', { style: 'margin-top:14px' });
    line.append(el('div', {},
      el('span', { className: 'badge sm ' + (r.breaking ? 'red' : 'grey'),
        textContent: r.breaking ? 'DELIVERY BREAKS' : 'DELIVERY CHANGES' }),
      el('span', { className: 'mono', style: 'margin-left:10px;font-weight:600',
        textContent: r.uri || 'destination not written down' })));
    line.append(el('div', { className: 'small muted', style: 'margin-top:6px;line-height:1.55' },
      'Carries ',
      el('span', { className: 'mono', textContent: (r.attrs || []).join(', ') }),
      ' out of ',
      el('span', { className: 'mono', textContent: r.from }),
      ` · ${r.file}:${r.line}`));
    card.append(line);
  });
  box.append(card);
}

/* The honest half of the report: what Ripple could NOT account for. Styled to
   stand out, never to shrink — a clean finding list is only worth what was read. */
function renderGaps(box, sc) {
  if (sc.unreadable?.length) {
    const card = el('div', { className: 'card clip', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(el('div', { className: 'chead', style: 'background:var(--amberbg);border-bottom-color:var(--amberln)' },
      el('span', { className: 'tag', style: 'background:var(--amber);color:#fff', textContent: 'Check by hand' }),
      el('b', { textContent: `${sc.unreadable.length} file${sc.unreadable.length === 1 ? '' : 's'} to check by hand` })));
    const p = el('div', { className: 'pad lg' });
    p.append(why(
      el('span', { className: 'prose', textContent: 'Not covered by the findings above.' }),
      'why a person has to read these',
      'Ripple could not read these files, or found your column somewhere it cannot follow — '
      + 'inside a procedure call, a loop, or written as text. Nothing in them is covered by the '
      + 'findings above, so somebody has to open them.'));
    // The advice is usually the same sentence on every entry — "this repository
    // is being read as generic SQL", on sixty-eight files. Printed sixty-eight
    // times it stops being advice and becomes wallpaper the eye skips, taking
    // the file names with it. Anything said more than once is said once, here.
    const counts = {};
    sc.unreadable.forEach(u => { if (u.hint) counts[u.hint] = (counts[u.hint] || 0) + 1; });
    const shared = Object.keys(counts).filter(h => counts[h] > 1);
    shared.forEach(h => p.append(el('div', { className: 'note info', style: 'margin-top:12px' },
      why(el('b', { textContent: `Applies to ${counts[h]} of these files.` }),
        'the reason shared by ' + counts[h] + ' of these files', h))));
    // The point of this list is that somebody opens those files and checks
    // them, so it gives them the line to open at and the line itself. "Could
    // not parse" sends a person hunting through a thousand-line file.
    //
    // Measured on a repository the size of the one this was built for: two
    // hundred and twelve of these, each with a name, a reason and a snippet,
    // made this one card 22,000 pixels tall -- more than half of a 40,000-pixel
    // page. A list that long is not worked through on screen. So the ones most
    // likely to be SQL are given in full (they are sorted that way) and every
    // remaining file is still NAMED, with its count said out loud. Nothing is
    // dropped from the analysis or from the page -- only from the long form.
    const SHOWN = 40;
    sc.unreadable.slice(0, SHOWN).forEach(u => {
      const item = el('div', { style: 'margin-top:14px' });
      item.append(el('div', { style: 'display:flex;gap:10px;align-items:baseline;flex-wrap:wrap' },
        el('span', { className: 'chip mono', textContent: u.file }),
        el('span', { className: 'small muted',
          textContent: u.reason + (u.places > 1 ? ` — in ${u.places} places` : '') })));
      if (u.snippet) {
        item.append(el('div', { className: 'mono small',
          style: 'margin-top:6px;padding:8px 12px;background:var(--amberbg);border:1px solid var(--amberln);'
            + 'border-radius:6px;overflow-x:auto;white-space:pre' },
          `line ${u.line} · ${u.snippet}`));
      }
      if (u.hint && !shared.includes(u.hint)) {
        item.append(el('div', { className: 'small muted', style: 'margin-top:6px;line-height:1.55', textContent: u.hint }));
      }
      p.append(item);
    });
    const rest = sc.unreadable.slice(SHOWN);
    if (rest.length) {
      p.append(why(
        el('span', { className: 'lbl', style: 'display:block;margin-top:20px',
          textContent: `${rest.length} more file${rest.length === 1 ? '' : 's'} to check by hand` }),
        'the rest of the check-by-hand list',
      `The ${SHOWN} most likely to hold SQL are shown above, each with the line to open. The `
      + 'rest are named here. None of them is covered by the findings.'));
      const more = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
      rest.forEach(u => more.append(el('span', { className: 'chip mono', textContent: u.file })));
      p.append(more);
    }
    card.append(p);
    box.append(card);
  }
  if (sc.mentionsOnly?.length) {
    const card = el('div', { className: 'card pad lg', style: 'margin-top:16px' });
    card.append(el('span', { className: 'lbl',
      textContent: sc.mentionsOnly.length === 1
        ? '1 file mentions the name but carries it nowhere'
        : `${sc.mentionsOnly.length} files mention the name but carry it nowhere` }));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:10px' });
    sc.mentionsOnly.forEach(m => chips.append(el('span', { className: 'chip mono', textContent: m.file })));
    card.append(chips);
    box.append(card);
  }
}

// ── step 5 ────────────────────────────────────────────────────────────────
function step5(root) {
  const gs = S.scan?.graphs || [];
  const tabs = x(root, 'tabs'), map = x(root, 'map');
  // The line under the title has to be true of the picture underneath it, and
  // "to the production tables it feeds" is not true of a branch that ends at a
  // table Ripple has not been told is published — which is most of them when
  // the published-table list is wrong, exactly when it matters most.
  const anyProd = gs.some(g => (g.branches || []).length);
  // "None of these reach a published table" is a claim, and it is not one this
  // picture can make while some of its branches were cut short by a setting.
  const anyCut = (S.scan?.cutShort || []).length;
  x(root, 'sub').textContent = anyProd
    ? 'Where the changed attribute travels, what it is called at each step, and which published tables it reaches.'
    : anyCut
      ? `Where the changed attribute travels, and what it is called at each step. Ripple stopped `
        + `following ${anyCut === 1 ? 'one branch' : `${anyCut} branches`} at ${S.scan.maxHops} `
        + `renames deep, so where ${anyCut === 1 ? 'it ends' : 'they end'} is not known.`
      : 'Where the changed attribute travels, and what it is called at each step. None of these branches reach a table on your published list.';
  if (!gs.length) {
    // The same rule as the findings screen: a reassuring sentence may not appear
    // while a gap is known, and this picture is an answer in its own right.
    const clear = S.scan?.coverage?.complete;
    const gaps = (S.scan?.coverage?.gaps || []).length;
    map.append(el('div', { className: 'note ' + (clear ? 'good' : 'info'),
      style: 'max-width:600px;padding:22px 26px' },
      why(el('b', { style: 'font-size:15px', textContent: clear
          ? 'No downstream lineage found'
          : `No downstream lineage found — ${gaps} gap${gaps === 1 ? '' : 's'} on the previous step` }),
        'what no lineage means',
      clear
        ? 'These attributes do not feed any table on your published-table list.'
        : 'These attributes do not feed any table on your published-table list, out of what '
          + 'Ripple could read. There are places it could not see into, listed on the impact '
          + 'analysis step — so this picture may not be the whole picture.')));
    // The summary is written here, not on the summary step. Sending someone
    // straight on to step 6 left that screen with nothing to draw and two
    // buttons that did nothing -- which only ever happened on a clean result,
    // exactly when somebody most wants to get to the reply.
    x(root, 'next').onclick = () => makeSummary();
    return;
  }
  const gi = Math.min(S.graphTab, gs.length - 1);
  tabs.append(el('span', { className: 'lbl faint', textContent: 'Attribute', style: 'margin-right:4px' }));
  gs.forEach((g, i) => {
    const b = el('button', { className: 'pill tab' + (i === gi ? ' on' : '') });
    b.append(el('span', { className: 'mono', textContent: g.attr }),
      el('span', { className: 'sub', textContent: g.table }));
    b.onclick = () => { S.graphTab = i; render(); };
    tabs.append(b);
  });
  const g = gs[gi];
  const ends = g.endBranches || [];
  const all = g.branches.concat(ends);
  const card = el('div', { className: 'card pad lg' });
  const row = el('div', { className: 'maprow' });
  const src = el('div', { className: 'mapsrc' });
  src.append(el('div', {},
    el('div', { className: 'k', textContent: 'Upstream source' }),
    el('div', { className: 'tb', textContent: g.table }),
    el('div', { className: 'at', textContent: g.attr }),
    el('div', { className: 'ct', textContent: `${all.length} branch${all.length === 1 ? '' : 'es'} followed`
      + (g.branches.length ? ` · ${g.branches.length} to production` : '') })));
  const branches = el('div', { className: 'branches' });
  // Measured on a repository the size of the one this was built for: following
  // one of the key columns produces about 1,500 branches. Drawing all of them
  // is a wall of boxes nobody can read, and a map nobody can read is the same
  // as no map. So a readable number is drawn — the ones that reach a published
  // table first, because those are the ones that matter — and the rest are
  // COUNTED OUT LOUD rather than quietly left off. Nothing is lost: every
  // branch here is already a finding in the list on the previous step.
  //
  // Twenty, not forty. Measured again, at a 1,180px window: forty branches of
  // real table names wrap to three lines each and make this one picture 16,000
  // pixels tall, which is forty screens of scrolling to see a diagram.
  const DRAWN = 20;
  all.slice(0, DRAWN).forEach(br => {
    const line = el('div', { className: 'branch' });
    br.forEach((n, i) => {
      line.append(nodeEl(n));
      if (i < br.length - 1) line.append(el('span', { className: 'arrow', textContent: '→' }));
    });
    branches.append(line);
  });
  row.append(src, branches);
  card.append(row);
  if (all.length > DRAWN) {
    card.append(el('div', { className: 'note info', style: 'margin-top:14px' },
      why(el('b', { textContent: `${all.length - DRAWN} of the ${all.length} branches are not drawn here.` }),
        'branches not drawn',
      'Every branch is still in the findings on the previous step, grouped by published table. '
      + 'The ones drawn here are the ones that reach a published table, longest first.')));
  }
  map.append(card);
  if (ends.length) {
    map.append(el('div', { className: 'note warn', style: 'margin-top:14px' },
      why(el('b', { textContent: ends.length === 1
          ? 'One of these branches ends at a table that is not on your published list.'
          : `${ends.length} of these branches end at a table that is not on your published list.` }),
        'branches that end off the published list',
      'The change reaches them either way. Ripple simply cannot tell you whether anyone outside '
      + 'your team reads them, because they are not on your published-table list.')));
  }

  const legend = el('div', { className: 'legend' });
  [['var(--redbg)', 'var(--redln)', 'Production table'],
   ['#F4F9FE', '#9CC4EA', 'Intermediate table'],
   ['var(--violetbg)', 'var(--violetln)', 'Alias used for the attribute']].forEach(([bg, ln, label]) =>
    legend.append(el('div', {}, el('i', { style: `background:${bg};border:1px solid ${ln}` }), label)));
  map.append(legend);
  map.append(el('div', { className: 'small muted', style: 'margin-top:12px' },
    why(el('span', { textContent: 'Each box is a table.' }),
      'reading this map',
      'The alias is what your column is called at that point. That rename is exactly what a '
      + 'plain search of the code would miss.')));
  x(root, 'next').onclick = () => makeSummary();
}

function nodeEl(n) {
  const d = el('div', { className: 'node' + (n.prod ? ' prod' : '') });
  d.append(el('div', { className: 'top' },
    el('span', { className: 'k', textContent: n.kind }),
    el('span', { className: 'nm', textContent: n.name })));
  if (n.alias) d.append(el('div', { className: 'al' },
    el('span', { textContent: 'alias' }),
    el('span', { className: 'chip alias', textContent: n.alias })));
  // The two things a box on this map can hide. Drawn on the box itself, because
  // a picture of a chain is exactly where somebody reads "and then it stops".
  if (n.inferred) {
    d.append(el('div', { className: 'small muted', style: 'margin-top:5px;line-height:1.4',
      textContent: (n.how ? `${n.how} of a whole table` : 'built with SELECT *')
        + ' — column list not visible' }));
  }
  if (n.cut) {
    d.append(el('div', { className: 'small', style: 'margin-top:5px;line-height:1.4;color:var(--red)',
      textContent: 'Ripple stopped here — hop limit, not the end of the chain' }));
  }
  return d;
}

// ── step 6 ────────────────────────────────────────────────────────────────
function makeSummary() {
  if (S.summary) { goto(6); return; }
  run(async () => {
    const out = await api('/api/summary', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scan: S.scan, vals: { ...S.vals, effectiveLabel: fmtDate(S.vals.effectiveDate) }, useAI: true }),
    });
    S.summary = out.summary; S.reply = out.reply; S.aiNote = out.aiNote || '';
    goto(6);
  }, 'Writing the summary…');
}

function step6(root) {
  const s = S.summary;
  // A screen with nothing on it and two buttons that do nothing is the worst
  // way to say "the summary has not been written yet". If we ever arrive here
  // without one, say so and offer the one button that fixes it.
  if (!s) {
    x(root, 'sub').textContent = 'The summary has not been written yet.';
    const b = x(root, 'body');
    const go = el('button', { className: 'pri', textContent: 'Write the summary now' });
    go.onclick = () => makeSummary();
    b.append(el('div', { className: 'note info', style: 'max-width:620px' },
      el('b', { textContent: 'Nothing to show yet. ', style: 'display:block' }),
      'The summary is written from the findings when you leave the dependency map. '
      + 'It has not been written for this scan.'), el('div', { style: 'margin-top:14px' }, go));
    x(root, 'next').onclick = () => makeSummary();
    x(root, 'save').disabled = true;
    x(root, 'saved').textContent = 'Nothing to save until the summary is written.';
    return;
  }
  const [cls, label] = RISK[S.scan.risk] || RISK.none;
  x(root, 'sub').textContent =
    'Written from the findings without AI.';

  const b = x(root, 'body');
  const grid = el('div', { className: 'grid2', style: 'grid-template-columns:1.7fr 1fr' });

  // ── the summary itself ──
  const main = el('div', { className: 'card clip' });
  main.append(el('div', { className: 'chead', style: 'background:#fff;padding:18px 26px' },
    el('b', { textContent: s.headline, style: 'font-size:16px;font-weight:800;line-height:1.35' }),
    el('span', { className: 'badge ' + cls, textContent: label, style: 'margin-left:auto;flex-shrink:0' })));
  main.append(el('p', { style: 'padding:20px 26px 4px;font-size:14.5px;line-height:1.7;color:var(--body)', textContent: s.narrative }));
  const ul = el('ul', { className: 'ticks', style: 'padding:16px 26px 24px;margin-top:0' });
  (s.bullets || []).forEach(t => ul.append(el('li', {}, t)));
  main.append(ul);
  const fields = el('div', { style: 'padding:0 26px 24px;display:grid;grid-template-columns:1fr 1fr;gap:16px 24px' });
  [['Source system', S.vals.source, false], ['Change type', S.vals.changeType, false],
   ['Upstream tables name', S.vals.upstream.map(u => u.table).join(', '), true],
   ['Upstream attributes name', S.vals.upstream.flatMap(u => u.attrs).join(', '), true]].forEach(([k, v, mono]) =>
    fields.append(el('div', {}, el('span', { className: 'lbl', textContent: k }),
      el('div', { textContent: v || '—',
        style: 'margin-top:5px;font-size:14px;font-weight:600;line-height:1.45;overflow-wrap:break-word;'
          + (mono ? 'font-family:var(--mono);color:var(--blued)' : 'color:var(--ink)') }))));
  main.append(fields);

  // ── right rail ──
  const rail = el('div', { className: 'rail' });
  const dl = daysLeft(S.vals.effectiveDate);
  const dead = el('div', { className: 'card pad' });
  dead.append(el('span', { className: 'lbl', textContent: 'Deadline' }));
  dead.append(el('div', { textContent: fmtDate(S.vals.effectiveDate) || 'Not given',
    style: 'font-size:20px;font-weight:800;margin-top:8px' }));
  if (dl !== null) dead.append(el('span', { className: 'badge sm ' + (dl <= 21 ? 'amber' : 'blue'),
    textContent: dl < 0 ? 'date has passed' : `${dl} day${dl === 1 ? '' : 's'} left`, style: 'margin-top:8px' }));
  if (S.vals.pocName || S.vals.pocTeam) {
    dead.append(el('div', { className: 'small muted', style: 'margin-top:12px;line-height:1.55' },
      'Upstream contact: ', el('b', { textContent: S.vals.pocName || '—', style: 'color:var(--body)' }),
      S.vals.pocTeam ? ', ' + S.vals.pocTeam : ''));
  }

  const st = S.scan.stats;
  const radius = el('div', { className: 'card pad' });
  radius.append(el('span', { className: 'lbl', textContent: 'Blast radius' }));
  [[st.productionTables, 'production tables impacted'], [st.intermediateTables, 'intermediate tables in the path'],
   [st.filesWithImpact, 'code files to change'], [st.couldNotRead, 'files that must be checked by hand']]
    .forEach(([n, lab]) => radius.append(el('div', { style: 'display:flex;align-items:baseline;gap:10px;padding:6px 0' },
      el('span', { textContent: String(n), style: 'font-size:18px;font-weight:800;color:var(--blued);font-variant-numeric:tabular-nums;min-width:26px' }),
      el('span', { style: 'font-size:13px;color:var(--body)', textContent: lab }))));

  const acts = el('div', { className: 'card pad' });
  acts.append(el('span', { className: 'lbl', textContent: 'What to do' }));
  const ol = el('ol', { className: 'acts' });
  (s.actions || []).forEach(a => ol.append(el('li', {}, a)));
  acts.append(ol);

  rail.append(dead, radius, acts);
  grid.append(main, rail);
  b.append(grid);
  // The caveat has to be on the same screen as the answer it qualifies, so it
  // stays -- but not the whole card. The findings screen already carries every
  // line, every reason and every snippet; repeating that here printed a hundred
  // and forty identical words two clicks apart, which is how a warning stops
  // being read. The count and the file names are the facts, so they are here.
  if (S.scan.unreadable?.length) {
    const n = S.scan.unreadable.length;
    const card = el('div', { className: 'card pad lg', style: 'margin-top:20px;border-color:var(--amberln)' });
    card.append(why(
      el('b', { style: 'font-size:14px', textContent: `${n} file${n === 1 ? '' : 's'} to check by hand` }),
      'the files a person still has to read',
      'Ripple could not read these, or found your column somewhere it cannot follow. They are '
      + 'not covered by the findings above. The line to open in each one is on the impact '
      + 'analysis step.'));
    const chips = el('div', { className: 'chips scrollbox', style: 'margin-top:12px' });
    S.scan.unreadable.forEach(u => chips.append(el('span', { className: 'chip mono',
      textContent: u.file })));
    card.append(chips);
    b.append(card);
  }

  x(root, 'next').onclick = () => goto(7);
  // "Saved" has to mean saved. Where it does not really last, say so in the
  // same breath rather than letting the word stand on its own. This sits in a
  // row between two buttons, so it stays one short line -- the full
  // explanation is on the Past analyses screen.
  const saved = x(root, 'saved');
  saved.textContent = '';
  if (S.savedId) {
    saved.append(el('span', { className: 'badge sm green', textContent: `Saved as analysis #${S.savedId}` }));
    if (S.health?.limits?.historyKept === false) {
      saved.append(el('span', { className: 'small faint',
        textContent: ' This host wipes saved analyses — copy out anything you need to keep.' }));
    }
  }
  x(root, 'save').onclick = () => run(async () => {
    const out = await api('/api/history', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vals: S.vals, scan: S.scan, summary: S.summary, mode: S.vals.extractedBy }),
    });
    S.savedId = out.id || null;
    if (!out.saved) alert('History is not available here: ' + (out.reason || ''));
    render();
  }, 'Saving this analysis…');
}

// ── step 7 ────────────────────────────────────────────────────────────────
function step7(root) {
  const r = S.reply || { subject: '', body: '' };
  const subj = x(root, 'subject'); subj.value = r.subject; subj.oninput = () => { r.subject = subj.value; };
  const body = x(root, 'body'); body.value = r.body; body.oninput = () => { r.body = body.value; };
  const ol = x(root, 'acts');
  (S.summary?.actions || []).forEach(a => ol.append(el('li', {}, a)));

  // who the reply is for — real values only, and nothing here sends anything.
  // Every address, one chip each, so a list of four is not one long unreadable
  // string that hides a typo in the middle of it.
  const to = x(root, 'to');
  const addresses = S.vals.pocEmails?.length ? S.vals.pocEmails : emailList(S.vals.pocEmail);
  to.append(el('span', { className: 'small', textContent: 'To', style: 'font-weight:700;color:var(--mute);flex-shrink:0' }));
  if (S.vals.pocName) to.append(el('span', { className: 'chip', textContent: S.vals.pocName }));
  addresses.forEach(a => to.append(el('span', { className: 'chip mono', textContent: a })));
  if (!S.vals.pocName && !addresses.length) {
    to.append(el('span', { className: 'chip', textContent: 'No contact was given' }));
  }
  if (S.vals.pocTeam) to.append(el('span', { className: 'badge sm blue', textContent: S.vals.pocTeam }));

  if (S.scan) {
    const [cls, label] = RISK[S.scan.risk] || RISK.none;
    x(root, 'risk').append(el('span', { className: 'badge ' + cls, textContent: label }));
  }
  const dl = daysLeft(S.vals.effectiveDate);
  if (S.vals.effectiveDate) {
    x(root, 'deadline').append(el('div', { className: 'note info', style: 'padding:14px 18px' },
      el('span', { className: 'lbl', style: 'color:var(--blued);display:block', textContent: 'Respond by' }),
      el('div', { style: 'font-size:15px;font-weight:700;margin-top:6px;color:var(--ink)',
        textContent: fmtDate(S.vals.effectiveDate) + (dl !== null ? ` · ${dl} day${dl === 1 ? '' : 's'} left` : '') })));
  }

  x(root, 'copy').onclick = async () => {
    // The addresses go with it. Copying a reply and then having to gather the
    // recipients again by hand is half a job.
    const head = addresses.length ? `To: ${addresses.join('; ')}\n` : '';
    await navigator.clipboard.writeText(`${head}Subject: ${r.subject}\n\n${r.body}`);
    x(root, 'copied').textContent = addresses.length
      ? `Copied, with ${addresses.length} recipient${addresses.length === 1 ? '' : 's'} — paste it into Outlook.`
      : 'Copied — paste it into Outlook.';
  };
  x(root, 'restart').onclick = () => {
    Object.assign(S, { step: 1, maxStep: 1, vals: null, scan: null, summary: null, reply: null,
      savedId: null, emailPreview: null, openGroup: 'p0', openRow: null, graphTab: 0 });
    render();
  };
}

// ── history & settings ────────────────────────────────────────────────────
function historyView(root) {
  const kept = S.health?.limits?.historyKept !== false;
  root.append(el('div', { className: 'head' }, el('div', {},
    el('h2', { textContent: 'Past analyses' }),
    // "On this server" is wrong in the copy that runs as a program on somebody's
    // own laptop, where there is no server and nothing is shared with anyone.
    el('p', { textContent: kept
      ? (S.health?.offline
        ? 'Everything saved on this machine, newest first. They stay in the folder beside Ripple.'
        : 'Everything saved on this server, newest first.')
      : 'Newest first — but this list does not last on this host. See the note below.' }))));
  // A hosted copy is replaced constantly and takes its saved rows with it.
  // An empty list would otherwise look like a bug or like lost work.
  if (!kept) {
    root.append(el('div', { className: 'note warn', style: 'margin-bottom:18px' },
      why(el('b', { textContent: 'Saved analyses do not survive here — copy out anything you '
          + 'need to keep.' }),
        'why saved analyses do not last here',
      'This copy runs on a shared host that replaces its machine constantly and wipes anything '
      + 'saved on it. An analysis can disappear within minutes, and the list can look different '
      + 'from one refresh to the next. Nothing is broken — there is simply nowhere permanent '
      + 'to save.')));
  }
  const card = el('div', { className: 'card clip' });
  root.append(card);
  api('/api/history').then(rows => {
    if (!rows.length) {
      card.append(el('div', { className: 'pad lg muted', textContent: kept
        ? 'Nothing saved yet.'
        : 'Nothing here — either nothing has been saved yet, or this host has already been replaced.' }));
      return;
    }
    const t = el('table', { className: 'hist' });
    const hr = el('tr');
    ['When', 'Subject', 'Source', 'Change', 'Risk', 'Mode', 'Status'].forEach(h => hr.append(el('th', { textContent: h })));
    t.append(hr);
    rows.forEach(r => {
      const [cls, label] = RISK[r.risk] || RISK.none;
      const sel = el('select', { className: 'statussel' });
      ['New', 'In progress', 'Verified', 'Closed'].forEach(s =>
        sel.append(el('option', { value: s, textContent: s, selected: s === r.status })));
      sel.onchange = () => api(`/api/history/${r.id}`, {
        method: 'PATCH', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: sel.value }),
      });
      // The same date format as every other screen. This column used to print
      // the raw stored value -- 2026-08-13 04:38 beside "18 Sept 2026"
      // everywhere else, which reads as two different kinds of date.
      const when = (r.created_at || '');
      t.append(el('tr', {},
        el('td', { className: 'small muted',
          textContent: (fmtDate(when.slice(0, 10)) + ' ' + when.slice(11, 16)).trim() }),
        el('td', { textContent: r.subject || '—' }),
        el('td', { textContent: r.source || '—' }),
        el('td', { className: 'small', textContent: r.change_type || '—' }),
        el('td', {}, el('span', { className: 'badge ' + cls, textContent: label })),
        el('td', { className: 'small muted', textContent: r.mode || '' }),
        el('td', {}, sel)));
    });
    card.append(t);
  });
}

/* Settings, and the AI key form that is most of it. The offline build replaces
   this whole screen: it has no key to set, and it has two settings of its own
   that online reads from environment variables — which folder to scan, and
   which SQL dialect to read it as. */

// ── plumbing ──────────────────────────────────────────────────────────────
function goto(n) { S.step = n; S.maxStep = Math.max(S.maxStep, n); S.view = 'wizard'; render(); }

/* Everything slow goes through here, and everything slow says what it is doing.
   Reading a repository takes seconds on a big one, and a spinning dot in the
   far corner is not an answer -- numbers that change by themselves a while
   later read as a page that did something on its own. */
function run(fn, what) {
  S.busy = true; S.busyWhat = what || 'Working…'; S.progress = null; render();
  watchProgress();
  Promise.resolve(fn()).catch(e => {
    alert('Something went wrong: ' + e.message);
  }).finally(() => { S.busy = false; S.busyWhat = ''; S.progress = null; render(); });
}

/* Ask the running program what it is doing, twice a second, for as long as it
   is doing something.

   On a repository of a few thousand files, reading it takes minutes and a scan
   takes about a minute. A spinner and a fixed sentence for that long is
   indistinguishable from a program that has hung, and the usual answer to that
   is a progress bar with a number nobody can check underneath it. This shows
   only what the engine has actually counted: files really read, statements
   really followed. Where there is no total — a chain looks at as many
   statements as it turns out to need — it says the count and no fraction,
   because a fraction would need a denominator nobody knows. */
function watchProgress() {
  if (S.progressTimer) return;
  S.progressTimer = setInterval(async () => {
````

## Paste 25 of 25

### web/app.js — piece 5 of 5

Add this to the END of `web/app.js`, straight after what is already there. Do not start a new file. Do not re-type anything above.

````javascript
    if (!S.busy) { clearInterval(S.progressTimer); S.progressTimer = null; S.progress = null; return; }
    try {
      const p = await api('/api/progress');
      const was = progressText(S.progress);
      S.progress = p.job ? p : null;
      if (progressText(S.progress) !== was) render();
    } catch { /* the request it belongs to will report the real failure */ }
  }, 500);
}

/* How deep the trail is followed, in words. Zero is not "0 hops" -- it means
   the trail is followed until the CODE runs out, which is the default and is
   the whole answer to "why did it stop there". Printed as a number, zero read
   as "Ripple follows no renames at all", which is the opposite of what it is. */
function hopsPhrase(n) {
  return n ? `${n} renames deep` : 'to the end of the code';
}

function progressText(p) {
  if (!p || !p.job) return '';
  const label = p.label || ({ reading: 'Reading the files',
                              parsing: 'Understanding the SQL',
                              scanning: 'Following the column' })[p.job] || 'Working';
  if (p.total > 0) return `${label} — ${p.done.toLocaleString()} of ${p.total.toLocaleString()}`;
  if (p.done > 0) return `${label} — ${p.done.toLocaleString()} so far`;
  return label;
}

function render() {
  renderSteps(); renderStatus();
  const view = $('#view'); view.innerHTML = '';
  $('#hRight').innerHTML = '';
  if (S.busy) {
    // The counted line if there is one, the fixed sentence until there is.
    $('#hRight').append(el('span', { className: 'spin' }),
      el('span', { className: 'small', textContent: progressText(S.progress) || S.busyWhat,
        style: 'margin-left:9px;font-weight:600;color:var(--blued)' }));
  }

  if (S.view === 'history') {
    setHeader('Past analyses', S.health?.limits?.historyKept === false
      ? 'Kept only until this host is replaced'
      : S.health?.offline ? 'Saved beside Ripple, on this machine' : 'Saved on this server');
    historyView(view); return;
  }
  if (S.view === 'settings') { setHeader('Settings & checks', 'Connections and health'); settingsView(view); return; }

  const list = stepNumbers();
  setHeader(STEPS[S.step - 1][0], `Step ${list.indexOf(S.step) + 1} of ${list.length}`);
  const tpl = $(`#t-step${S.step}`);
  if (!tpl) return;
  const node = tpl.content.cloneNode(true);
  const holder = el('div');
  holder.append(node);
  view.append(holder);
  ({ 1: step1, 2: step2, 3: step3, 4: step4, 5: step5, 6: step6, 7: step7 })[S.step](holder);
}

$('#navHistory').onclick = () => { S.view = 'history'; render(); };
$('#navSettings').onclick = () => { S.view = 'settings'; render(); };

/* Run once, after the server has answered and before the first screen is drawn.
   Nothing to do online. The offline build replaces this to open on the settings
   screen the very first time, when no repository folder has been chosen yet —
   there, that is a question that has to be asked rather than a default that can
   be assumed. */

/* Reading a repository the size of a real warehouse takes minutes. Measured on
   7,304 files: 101 seconds, during which this page was blank and had no way to
   ask what was going on, because the only request that would answer was the one
   it was waiting on. A working program that says nothing for a hundred seconds
   is reported as a hung one.

   So the server reads on a thread and answers straight away with indexing:true,
   and this waits here — showing the counted file numbers it was already keeping
   — until the read is done. Nothing is estimated and no bar moves on a timer:
   every number below is files that have really been read. */
async function waitForTheRepository() {
  while (S.health && S.health.indexing) {
    renderReading();
    await new Promise(r => setTimeout(r, 700));
    try { S.health = await api('/api/health'); }
    catch (e) { S.bootError = e.message; return; }
  }
}

function renderReading() {
  const h = S.health || {};
  const p = h.progress || {};
  const view = $('#view');
  if (!view) return;
  view.innerHTML = '';
  const card = el('div', { className: 'card pad lg', style: 'margin:40px auto;max-width:640px' });
  card.append(el('b', { style: 'font-size:15px;display:block',
    textContent: `Reading ${h.repo?.label || 'the repository'}` }));
  card.append(el('div', { className: 'small muted', style: 'margin-top:8px',
    textContent: h.readError
      ? h.readError
      : (progressText(p)
         || 'Opening every file and reading the SQL in it. On a repository of a few '
            + 'thousand files this takes a few minutes. Nothing has been missed — '
            + 'Ripple is still going.') }));
  card.append(el('div', { className: 'small muted', style: 'margin-top:10px',
    textContent: h.repo?.path || '' }));
  view.append(card);
}

(async function boot() {
  try { S.health = await api('/api/health'); }
  catch (e) { alert('Could not reach the Ripple server: ' + e.message); }
  await waitForTheRepository();
  afterBoot();
  render();
})();

/* Ripple Offline — the screens that only exist here.

   Appended to the shared front end when the offline build is made. Everything
   else on screen is the shared file, unchanged, so the two editions cannot
   drift apart. What is here is what genuinely differs: online, the folder to
   scan and the SQL dialect are environment variables set by whoever deploys
   the thing. Offline there is nobody to set them, so they are asked for on
   screen and remembered in a file beside the program.

   These three functions replace ones of the same name in the shared file.
   JavaScript hoists every function declaration in a file before running any of
   it, so the later ones — these — are the ones that run. */

// ── the first run ─────────────────────────────────────────────────────────
/* Nothing has been chosen yet, so the first thing on screen is the question,
   rather than a wizard that would scan nothing and say nothing was found. */
function afterBoot() {
  if (S.health && !S.health.configured) S.view = 'settings';
  keepAlive();
}

// ── telling the program somebody is still here ────────────────────────────
/* The built program has no console window and nothing to close. Closing this
   tab used to leave it running where nobody could see it, holding its own
   folder open — so the folder could not be deleted, the port stayed taken, and
   the only way out was Task Manager.

   So this page says it is here, every few seconds, and says goodbye on the way
   out. The goodbye is the reliable half: sendBeacon is delivered even as the
   tab is closing, which fetch is not. The repeating beat is the backstop for a
   browser that was killed outright and never got to say anything.

   BEAT is deliberately shorter than the program's quiet limit by a long way —
   a hidden tab is throttled to about one timer a minute, and being throttled
   must never look like being gone. */
const BEAT = 10000;

function keepAlive() {
  if (S.beatTimer) return;
  const beat = () => { fetch('/api/alive', { method: 'POST' }).catch(() => {}); };
  beat();
  S.beatTimer = setInterval(beat, BEAT);
  // pagehide covers closing the tab, closing the window and navigating away,
  // in every browser that matters. It also fires on a refresh, which is why
  // the program treats this as "start a short clock", not "stop now".
  addEventListener('pagehide', () => {
    try { navigator.sendBeacon('/api/leaving'); } catch (e) { /* going anyway */ }
  });
}

/* Stop the program, and say so, rather than leaving a dead tab that looks
   exactly like a working one. */
function closeRipple() {
  if (S.beatTimer) { clearInterval(S.beatTimer); S.beatTimer = null; }
  fetch('/api/quit', { method: 'POST' }).catch(() => {});
  // The reply may never arrive — the server is shutting down as it answers —
  // so the screen changes on the way out rather than waiting for it.
  setTimeout(() => {
    document.body.innerHTML = '';
    document.body.append(el('div', { className: 'empty', style: 'padding-top:120px' },
      el('b', { textContent: 'Ripple has stopped.' }),
      el('div', { className: 'small muted', style: 'margin-top:10px;line-height:1.6',
        textContent: 'You can close this tab. The program is no longer running, so its folder '
          + 'can be moved or deleted now.' }),
      el('div', { className: 'small faint', style: 'margin-top:10px',
        textContent: 'To use Ripple again, double-click Ripple Offline.exe.' })));
  }, 250);
}

// ── what step 3 says when the folder is not there ─────────────────────────
/* Online this reports a connection that failed. Offline there is no connection
   to fail — but a folder chosen last week can be moved, renamed or deleted, and
   that is an ordinary Tuesday on a locked-down machine, not an exception. */
function repoAlert(h) {
  const f = h.folder;
  if (!f || f.ok) return null;
  const box = el('div', { className: 'note bad', style: 'margin-bottom:18px' },
    el('b', { textContent: f.state === 'unset' ? 'No repository folder chosen yet. ' : 'Nothing can be scanned. ' }),
    f.message);
  const go = el('button', { className: 'ghost sm', textContent: 'Choose the folder', style: 'margin-top:12px' });
  go.onclick = () => { S.view = 'settings'; render(); };
  box.append(el('div', {}, go));
  return box;
}

// ── settings ──────────────────────────────────────────────────────────────
function offState() {
  const h = S.health;
  if (!S.off) {
    S.off = {
      path: (h && h.repo.path) || '',
      dialect: (h && h.sqlDialectId) || '',
      hops: (h && h.maxHops) || 0,
      check: null,        // the answer to "check this folder", before saving
      msg: null,          // the answer to the last save
      working: '',        // which button is busy: 'check', 'browse' or 'save'
    };
  }
  // The published-table list lives in the shared control's own state, so that
  // one box and one reading of it are used by both editions.
  productionState();
  return S.off;
}

/* Slow work here has to be visible on the button that started it. The header
   spinner is across the screen from whatever was pressed, and a folder being
   read is the one moment on this screen where nothing happens for a while and
   then several numbers change at once. */
function offRun(which, fn) {
  const o = offState();
  o.working = which;
  run(async () => {
    try { await fn(); } finally { o.working = ''; }
  }, which === 'save' ? 'Reading every file in the folder…'
    : which === 'check' ? 'Counting what is in the folder…'
    : 'Waiting for the folder picker…');
}

function settingsView(root) {
  const h = S.health;
  const o = offState();
  // The shared header says "Connections and health", and offline there are no
  // connections to have.
  setHeader('Settings & checks', h.configured
    ? 'What Ripple reads, and where it keeps things'
    : 'Choose the folder to scan');
  root.append(el('div', { className: 'head' }, el('div', {},
    el('h2', { textContent: 'Settings & checks' }),
    el('p', { textContent: h.configured
      ? 'What Ripple is reading, and where it keeps what it saves.'
      : 'Two things to choose before the first scan.' }))));

  if (!h.configured) {
    root.append(el('div', { className: 'note info', style: 'margin-bottom:18px' },
      why(el('b', { textContent: 'Choose the repository folder to get started.' }),
        'what choosing a folder does',
        'Ripple reads a copy of your code that is already on this machine. It downloads '
        + 'nothing and it never writes to your code. Point it at the folder, check the SQL '
        + 'type underneath, and save.')));
  }

  const grid = el('div', { className: 'grid2 even' });
  const prod = el('div', { style: 'margin-top:18px' },
    productionCard({ persistNote: '' }),
    el('div', { className: 'note warn', style: 'margin-top:14px' },
      why(el('b', { textContent: 'Get this wrong and a real impact reads as a clean result.' }),
        'what the published-table list decides',
        'A finding only counts as production impact when the table it ends at is on this list. '
        + 'Nothing is hidden either way — every table the change reaches is still listed — but '
        + 'the headline, the risk level and the drafted reply all follow this list.')));
  grid.append(el('div', {}, folderCard(h, o), dialectCard(h, o), prod, saveRow(h, o)),
              el('div', { className: 'rail' }, whereCard(h), guardCard(), factsCard(h),
                 buildCard(h), closeCard()));
  root.append(grid);
}

/* The way out. There is no console window and no application window, so
   without this the only way to stop Ripple is Task Manager — and until it is
   stopped, its own folder cannot be deleted or moved. */
function closeCard() {
  const card = el('div', { className: 'card pad lg', style: 'margin-top:18px' });
  card.append(why(
    el('span', { className: 'lbl', textContent: 'Finished with Ripple' }),
    'closing the tab is not closing Ripple',
    'Ripple is a small program running on this machine, not a website. Closing this tab leaves '
    + 'it running, and while it runs its own folder cannot be moved or deleted.'));
  const stop = el('button', { className: 'ghost', style: 'margin-top:12px',
    textContent: 'Close Ripple' });
  stop.onclick = () => closeRipple();
  card.append(stop);
  card.append(el('div', { className: 'small faint', style: 'margin-top:10px' },
    why(el('span', { textContent: 'It also closes itself.' }),
      'when Ripple closes itself',
      'A few minutes after the last tab is closed, so a forgotten one is not left holding the '
      + 'folder open.')));
  return card;
}

/* The folder to scan. Typing a path always works; the picker is only offered
   when this machine actually has one to open. */
function folderCard(h, o) {
  const card = el('div', { className: 'card pad lg' });
  card.append(why(
    el('span', { className: 'lbl', textContent: 'Repository folder' }),
    'what Ripple does with this folder',
    'The folder holding the code you want searched. Ripple reads every file in it and never '
    + 'writes to any of them.'));

  const inp = el('input', { type: 'text', className: 'mono', value: o.path,
    placeholder: 'D:\\code\\our-pipelines', style: 'margin-top:12px;padding:12px 14px' });
  inp.oninput = () => { o.path = inp.value; o.check = null; };
  inp.onkeydown = (e) => { if (e.key === 'Enter') checkFolder(); };
  card.append(inp);

  const row = el('div', { className: 'foot', style: 'margin-top:14px' });
  if (h.canBrowse) {
    const browse = el('button', { className: 'ghost',
      textContent: o.working === 'browse' ? 'Waiting for the picker…' : 'Browse…' });
    browse.disabled = !!o.working;
    browse.onclick = () => browseForFolder();
    row.append(browse);
  }
  const check = el('button', { className: 'ghost',
    textContent: o.working === 'check' ? 'Counting the files…' : 'Check this folder' });
  check.disabled = !!o.working;
  check.onclick = () => checkFolder();
  row.append(check);
  if (o.working === 'check') {
    row.append(el('span', { className: 'spin' }),
      el('span', { className: 'small muted', textContent: 'Walking the folder. A large one takes a moment.' }));
  }
  card.append(row);

  // A note with nothing in it is an empty coloured box, which reads as
  // something that failed to load rather than as an answer.
  if (o.check && o.check.message) {
    card.append(el('div', { className: 'note ' + (o.check.ok ? 'good' : 'bad'), style: 'margin-top:14px' },
      o.check.message));
  }
  return card;
}

/* The dialect. This is the setting that looks cosmetic and is not. */
function dialectCard(h, o) {
  const card = el('div', { className: 'card pad lg', style: 'margin-top:18px' });
  card.append(el('span', { className: 'lbl', textContent: 'How the SQL is read' }));
  const sel = el('select', { className: 'statussel', style: 'width:100%;padding:11px 12px;margin-top:12px' });
  (h.dialects || []).forEach(d => sel.append(el('option', {
    value: d.id, textContent: d.label, selected: d.id === o.dialect })));
  // NOT called `why`. That is the name of the shared information-button helper,
  // and a local const of the same name shadows it for the whole function -- so
  // calling it here would throw instead of drawing a button.
  const note = el('div', { className: 'small faint', style: 'margin-top:6px;line-height:1.55' });
  const showNote = () => {
    const d = (h.dialects || []).find(x => x.id === sel.value);
    note.textContent = d ? d.note : '';
  };
  sel.onchange = () => { o.dialect = sel.value; showNote(); };
  showNote();
  card.append(sel, note);
  card.append(el('div', { className: 'note warn', style: 'margin-top:14px' },
    why(el('b', { textContent: 'This matters more than it looks.' }),
      'why the dialect changes the answer',
      'Every warehouse writes SQL a little differently. Choose the wrong one and Ripple cannot '
      + 'read some of your files — and a file it cannot read is a file it cannot warn you '
      + 'about. That does not give you a vaguer answer. It gives you the wrong one. If you are '
      + 'not sure which to pick, ask whoever runs the pipeline.')));
  return card;
}

function saveRow(h, o) {
  const row = el('div', { className: 'card pad lg foot', style: 'margin-top:18px' });
  const busy = o.working === 'save';
  const save = el('button', { className: 'pri',
    textContent: busy ? 'Reading the folder…'
      : h.configured ? 'Save and read the repository again' : 'Save and read the repository' });
  save.disabled = !!o.working;
  save.onclick = () => saveOfflineSettings();
  row.append(save);
  if (busy) {
    // Reading a real repository is thousands of files. Without this the screen
    // sits still and then several numbers change on their own, which reads as
    // the page having done something by itself.
    row.append(el('span', { className: 'spin' }),
      el('span', { className: 'small muted',
        textContent: 'Reading every file and parsing the SQL — the counts on the right '
          + 'update when it finishes.' }));
  } else {
    row.append(el('span', { className: 'small faint',
      textContent: 'Saved to the settings file beside Ripple, so it is remembered next time.' }));
  }
  const box = el('div', {}, row);
  if (o.msg) {
    box.append(el('div', { className: 'note ' + (o.msg.ok ? 'good' : 'bad'), style: 'margin-top:14px' },
      o.msg.text));
  }
  return box;
}

/* Where the two files Ripple writes actually are. Nobody should have to guess,
   and "somewhere in your user profile" is not an answer. */
function whereCard(h) {
  const card = el('div', { className: 'card pad' });
  card.append(el('span', { className: 'lbl', textContent: 'What Ripple writes' }));
  [['Settings', h.settingsFile], ['Saved analyses', h.historyFile]].forEach(([k, v]) =>
    card.append(el('div', { style: 'padding:9px 0;border-top:1px solid var(--hair);margin-top:8px' },
      el('div', { className: 'small muted', textContent: k }),
      el('div', { className: 'small mono', textContent: v,
        style: 'margin-top:3px;font-weight:600;word-break:break-all' }))));
  card.append(el('div', { className: 'small faint', style: 'margin-top:12px' },
    why(el('span', { textContent: 'Both sit in the folder you copied across.' }),
      'what moving the folder takes with it',
      'Move that folder to another machine and your settings and saved analyses go with it. '
      + 'Delete it and Ripple is gone.')));
  const sync = h.syncedFolder;
  if (sync && sync.synced) {
    // Keeping everything beside the executable is what makes this copy portable.
    // In an office where sync is on for everybody it also means the folder is
    // being uploaded, and that is worth one plain paragraph rather than a
    // surprise. Neither point is a reason to stop; both are a reason to say so.
    card.append(el('div', { className: 'note warn', style: 'margin-top:14px' },
      el('b', { style: 'display:block', textContent: `${sync.client} is syncing this folder` }),
      why(el('div', { style: 'margin-top:6px;line-height:1.55', textContent:
          'Everything in this folder is being uploaded to your company\u2019s cloud — including '
          + 'the Ripple program itself, about 44 MB across roughly 1,770 files, and not '
          + 'signed by a known publisher.' }),
        'what a synced folder means for Ripple',
        'Your saved analyses live in a file inside this folder, and a sync tool copies files '
        + 'whenever it likes. If Ripple ever says it could not save an analysis, that is the '
        + 'usual reason, and trying again normally works.'),
      el('div', { className: 'small', style: 'margin-top:8px;line-height:1.55', textContent:
        'If you would rather neither happened, close Ripple and move this folder somewhere '
        + 'that is not synced — C:\\Ripple, for example — then start it again from there. '
        + 'Your settings and saved analyses move with it.' })));
  }
  return card;
}

/* Whether this copy really is sealed off, asked of the running program rather
   than asserted on a screen. */
function guardCard() {
  const card = el('div', { className: 'card pad' });
  card.append(el('span', { className: 'lbl', textContent: 'Nothing leaves this machine' }));
  const state = el('div', { style: 'margin-top:12px' },
    el('span', { className: 'small muted', textContent: 'Checking…' }));
  card.append(state);
  card.append(el('div', { className: 'small faint', style: 'margin-top:12px' },
    why(el('span', { textContent: 'No connection to anywhere, and no AI.' }),
      'what this copy can and cannot do',
      'There is nowhere here to type a key or an address. Ripple reads the folder above and '
      + 'writes the two files listed.')));
  api('/api/offline-check').then(g => {
    state.innerHTML = '';
    if (g.guardInstalled) {
      state.append(el('div', { className: 'note good' },
        why(el('b', { textContent: 'Outbound connections are blocked.' }),
          'how the block behaves',
          'If anything in this program tried to reach the internet it would fail immediately. '
          + 'It would not quietly succeed just because this machine happens to be online.')));
    } else {
      state.append(el('div', { className: 'note warn' },
        why(el('b', { textContent: 'The block is not switched on in this copy.' }),
          'what an unenforced block means',
          'Ripple still has nothing in it that reaches out, but that is not being enforced in '
          + 'this copy. Start Ripple the normal way to switch it back on.')));
    }
    if (g.attempts && g.attempts.length) {
      state.append(el('div', { className: 'note bad', style: 'margin-top:10px' },
        el('b', { textContent: `${g.attempts.length} attempt${g.attempts.length === 1 ? '' : 's'} to reach the network were refused: ` }),
        g.attempts.slice(0, 5).join(', ')));
    }
  }).catch(() => {
    state.innerHTML = '';
    state.append(el('div', { className: 'note warn', textContent: 'Could not ask this copy whether the block is on.' }));
  });
  return card;
}

function factsCard(h) {
  const card = el('div', { className: 'card pad' });
  card.append(el('span', { className: 'lbl', textContent: 'What was read' }));
  // "Files indexed 3, files unreadable 0" is the line somebody reads to decide
  // whether the whole folder was covered, and on its own it answers yes. The
  // row below it only appears when the answer is no, and then it has to appear,
  // because this is the panel that gets believed.
  const neverOpened = (h.repo.heldOnline || 0) + (h.repo.pathTooLong || 0);
  [['Files indexed', String(h.repo.files)],
   ['Statements understood', String(h.repo.statements)],
   ['Files unreadable', String(h.repo.unreadable)],
   ...(neverOpened ? [['Files never opened', String(neverOpened)]] : []),
   ['Tables found', String(h.catalog.tables)],
   ['SQL read as', h.sqlDialect],
   ['Renames followed', `${h.maxHops} hops`],
   ['Tables you publish', h.production || 'not set']].forEach(([k, v]) =>
    card.append(el('div', { className: 'factrow' },
      el('span', { className: 'small muted', textContent: k }),
      el('span', { className: 'small', textContent: v }))));
  return card;
}

// ── the three things those buttons do ─────────────────────────────────────
function checkFolder() {
  const o = offState();
  offRun('check', async () => {
    o.check = await api('/api/settings/check', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: o.path.trim() }),
    });
  });
}

function browseForFolder() {
  const o = offState();
  offRun('browse', async () => {
    const out = await api('/api/settings/browse', { method: 'POST' });
    if (out.path) { o.path = out.path; o.check = null; o.msg = null; }
  });
}

function saveOfflineSettings() {
  const o = offState();
  const p = productionState();
  offRun('save', async () => {
    try {
      S.health = await api('/api/settings', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repoPath: o.path.trim(), sqlDialect: o.dialect,
                               maxHops: o.hops, prodTables: p.text }),
      });
      // The box keeps whatever was pasted, so it can be edited rather than
      // handed back a tidied version of somebody's list. An empty box is the
      // exception: the server falls back to the default rather than treating
      // no table as published, and the box has to show what is really in force.
      p.text = S.health.productionRule?.text ?? p.text;
      p.report = null; p.loaded = false;
      // The saved message below says what happened. Leaving the "check this
      // folder" answer up as well puts an empty green box on screen, because
      // once it has been saved there is nothing left for it to report.
      o.check = null;
      o.msg = { ok: true, text: `Saved. ${S.health.repo.files} file`
        + `${S.health.repo.files === 1 ? '' : 's'} indexed from ${S.health.repo.label}, `
        + `read as ${S.health.sqlDialect}. ${S.health.repo.statements} statement`
        + `${S.health.repo.statements === 1 ? '' : 's'} understood, ${S.health.repo.unreadable} file`
        + `${S.health.repo.unreadable === 1 ? '' : 's'} could not be read. `
        + `Published tables: ${S.health.production}.` };
      // Whatever was scanned before came from a different folder or a different
      // dialect, so it is dropped rather than left on screen looking current.
      S.scan = null; S.summary = null; S.reply = null;
    } catch (e) {
      o.msg = { ok: false, text: e.message };
    }
  });
}
````

---

## Check you got it right

Do not trust your eyes for this. A file missing thirty lines in the middle looks
perfectly normal.

Save this as `check_ripple.py` in the project root and run `python check_ripple.py`:

````python
"""Did every file arrive whole? One word each."""
import base64
import hashlib
import io
import sys
import tempfile
import zipfile
from pathlib import Path

WANT = {
    "ripple/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "ripple/build_info.py": "37715e99df60286e18cb4295fb62794662005f0bdc70486c693fad525ce13285",
    "ripple/catalog.py": "414c7849764dbaab62fd12200fe5203dec5a4ccaf830bb5ac1dcb17893f941e2",
    "ripple/config.py": "cb62d3381fb90968c9aa58ba85cf6964afa120645340a49f645f125e8f43f89d",
    "ripple/narrative.py": "86075b4ba0a724f8f5204045ffc00b5b56c11f11c1a1506511aed6e98b50689d",
    "ripple/notification.py": "b0de5bb6e624b4f6bd163987ce7b227624bc08c7c37cb71ca719cefcee55e488",
    "ripple/production.py": "577b6df2178348f38e4a2bc6133cdc94f7f3e6b37fb54d68dbdbf933279c4f6b",
    "ripple/progress.py": "997c263a4c07f55f649a269b7808e64d9d895026b30db0c59003449663f5d39c",
    "ripple/providers.py": "9c6879d29f0f63d01b3492ce5740a92001d3c8beae7985d9574baaaa966c46a5",
    "ripple/store.py": "d08eeaa1bd638f033691bd9f1a4b96e6f97c4639384fd1fec98d51369f6dc4dd",
    "ripple/scanner/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "ripple/scanner/dialectcompat.py": "6a985d2993b9660959191170c62e7f637c356a4841cb4594f7c7379ffdcef73e",
    "ripple/scanner/lineage.py": "7051e62d44bea3b5c380a69c360f59d02538e229aaa8a87c736fcc33ef0bf50c",
    "ripple/scanner/repo.py": "bd41a66e20dc4339d74ad2c94cb77b23e111e624624b4257ff95db894b1c0e36",
    "ripple/scanner/rescue.py": "48b24cbaad0e9c8ea46a94a58de9f3253f48f42d4ea592f1bb89444272da3038",
    "ripple/scanner/sqlread.py": "1daaac12e7ae638db231633ce8eaf08de3e15586c80705cb03623d45eafa1f13",
    "ripple/scanner/templating.py": "7e0e37bfdc0132da586ffe73fb266b45094859a8648e26addecf2aebd9a904c5",
    "ripple_offline/folderpick.py": "e1854d250482e092f33dc667ca396364f18dbecb2bab880dbbcbc9999daba8ab",
    "ripple_offline/lifecycle.py": "62de2d22050a818b8e48aaba1318cb4fa840b1ce7759684330e78af80bc32f02",
    "ripple_offline/nonet.py": "e771b5715f6352a7206503e5148d37a9557d53434fa07976eb3acbc18d80b27f",
    "ripple_offline/paths.py": "486642e80a68fd88486bf5804e992c93d4884488bb59c666479fe5d8d1853eb1",
    "ripple_offline/prefs.py": "dcf99cc6af81fb7a1440d12d0940dd7dc968dfb1238e0e0a9bb2d5191961f03b",
    "ripple_offline/synced.py": "24b80ca232558668647f39a2e3073ae64099cfada0081d3edb71d1d10356a50f",
    "ripple_offline/__init__.py": "b1a52421c3d50ec1af1000c3d330cddf06430257849fe95439d167937085961e",
    "ripple_offline/engine.py": "e9ef3a3b2a9d44e73f8eee4859162286a98fb429e2da4f8bb6d5990978587a8c",
    "ripple_offline/app.py": "9e8d13162a4ab7d6d044fb092908f5ccbc9f88561392a6f9a2da81a83a9bf86d",
    "ripple_offline/webserver.py": "e2ded35aa1a1e6bd0b65d8d55edf881a1eeb77bc7d7d7276ac9cf3e5cb4fd94e",
    "run.py": "afe1a30c96287bc937dada53ecab299cac0641716343e8b8c8d44f498dc6eaea",
    "tests/test_smoke.py": "60ab5c5d68f1022081b26d0f53aae152fa10d5c8a5cf0ddc11b7cab91ff0a72b",
    "web/index.html": "9b9456b41da7c61d76107a04991f440c60d8d7322a4a60496340ea7b7c890b11",
    "web/styles.css": "152ae02a224ff20bc8e8bd12066917d3b93e9d8322febcf3c2148d0b5bc40b48",
    "web/app.js": "8b1d3ada7018690e15d21cd929ca5b5d960c892d64a7e54a6099b3ad0c79da47",
}

bad = []
for name, want in WANT.items():
    f = Path(name)
    if not f.is_file():
        print(f"{name:34} MISSING")
        bad.append(name)
        continue
    got = hashlib.sha256(f.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    if got == want:
        print(f"{name:34} exact")
    else:
        n = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
        print(f"{name:34} DIFFERENT  ({n} lines here)")
        bad.append(name)

print()
if bad:
    print(f"{len(bad)} file(s) are not identical. Paste each from its first piece again:")
    for n in bad:
        print("   ", n)
else:
    print("Every file is identical to the original.")
````

`exact` means byte for byte. `DIFFERENT` with a line count well below the table
above means a piece was skipped, or a chat summarised part of it — paste that
file again from its first piece.

Line endings are not counted as a difference: Windows may store these with
different line breaks and nothing about the program changes.

## When every file says `exact`

You still need `sqlglot` as a folder beside `run.py` — see the top of this file.
Nothing works without it.

Then, from the folder holding `run.py`:

````
python run.py
````

It prints the address it got. Read it rather than assuming 8000 — if something
else on the machine holds that port, Ripple quietly takes the next free one up
to 8020.

To prove the engine before opening anything:

````
python -m unittest tests.test_smoke
````

Thirteen checks, a second or two. They cover the parser arriving, the engine
arriving, the screens arriving, a column being followed end to end, and the rule
that Ripple must never say "no impact" over a file it could not read.

Do not open `index.html` by double-clicking it. The page asks the server for
`/static/styles.css`, and a file opened directly has no server to ask.

---

*Generated from the live files by `Ripple Offline/tools/make_exact_kits.py`. Do
not edit this by hand — run that again instead. A hand-edited copy of a source
file inside a document is a second copy of it, and the second copy is the one
that goes stale.*

