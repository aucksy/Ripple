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
_BLOCK_LINE = re.compile(
    r"""^\s*(?:
          BEGIN(?:\s+TRANSACTION)?
        | END(?:\s+(?:IF|FOR|WHILE|LOOP))?
        | (?:COMMIT|ROLLBACK)(?:\s+TRANSACTION)?
        | EXCEPTION\s+WHEN\s+.+?\s+THEN
        | (?:ELSE\s*)?IF\b.*?\bTHEN
        | ELSE
        | LOOP
        | (?:LEAVE|ITERATE|BREAK|CONTINUE)\b.*
      )\s*;?\s*$""",
    re.IGNORECASE | re.VERBOSE,
)

# A loop header names a real table. Keeping the query inside it costs one line
# and is the difference between seeing that table read and not.
_LOOP_HEADER = re.compile(r"^\s*(?:FOR\s+\w+\s+IN|WHILE)\s*(\(.*\))\s*(?:DO|LOOP)\s*$",
                          re.IGNORECASE)
_LOOP_PLAIN = re.compile(r"^\s*(?:FOR|WHILE)\b.*\b(?:DO|LOOP)\s*$", re.IGNORECASE)


def unwrap_blocks(text: str) -> str:
    """The same SQL with scripting keywords replaced by empty statements."""
    out: list[str] = []
    for line in text.splitlines():
        loop = _LOOP_HEADER.match(line)
        if loop:
            out.append("SELECT * FROM " + loop.group(1) + ";")
        elif _BLOCK_LINE.match(line) or _LOOP_PLAIN.match(line):
            out.append(";")
        else:
            out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def has_blocks(text: str) -> bool:
    return any(_BLOCK_LINE.match(line) or _LOOP_PLAIN.match(line)
               for line in text.splitlines())
