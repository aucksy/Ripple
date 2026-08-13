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

# A loop header names a real table. Keeping the query inside it costs one line
# and is the difference between seeing that table read and not. The header is
# often written across several lines, with the DO on its own, so it is gathered
# rather than matched.
_LOOP_HEADER = re.compile(r"^\s*(?:FOR\s+\w+\s+IN|WHILE)\s*(\(.*\))\s*(?:DO|LOOP)\s*$",
                          re.IGNORECASE)
_LOOP_START = re.compile(r"^\s*(?:FOR\s+\w+\s+IN|WHILE)\b", re.IGNORECASE)
_LOOP_PLAIN = re.compile(r"^\s*(?:FOR|WHILE)\b.*\b(?:DO|LOOP)\s*$", re.IGNORECASE)
_LOOP_END = re.compile(r"\b(?:DO|LOOP)\s*$", re.IGNORECASE)

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
    """The same SQL with scripting keywords replaced by empty statements."""
    lines = text.splitlines()
    state = {"quote": "", "comment": False}
    out: list[str] = []
    depth = 0          # CASE expressions currently open
    skip_until = -1    # index of the last line of a multi-line thing being dropped

    for n, line in enumerate(lines):
        code = _code_only(line, state)
        if n <= skip_until:
            out.append(";")
            continue

        # A RAISE, or a procedure signature: neither is readable, both can run
        # past the end of their line, and neither carries a table or a column.
        if depth == 0 and (_RAISE.match(code) or _PROCEDURE.match(code)):
            skip_until = _end_of_run(lines, n, state.copy(),
                                     signature=bool(_PROCEDURE.match(code)))
            out.append(";")
            continue

        if _LOOP_HEADER.match(code):
            # Detected on the blanked copy so a keyword in a string cannot
            # trigger it, but read back off the line as written -- the table
            # being looped over is normally a quoted name, and the blanked copy
            # no longer has it.
            loop = _LOOP_HEADER.match(line) or _LOOP_HEADER.match(code)
            out.append("SELECT * FROM " + loop.group(1) + ";")
            continue
        if _LOOP_START.match(code) and not _LOOP_END.search(code):
            body, skip_until = _gather_loop(lines, n, state.copy())
            out.append(body)
            continue
        if _ALWAYS_SCRIPTING.match(code) or _LOOP_PLAIN.match(code):
            out.append(";")
            continue
        if _SCRIPTING_UNLESS_CASE.match(code) and depth == 0:
            out.append(";")
            continue

        out.append(line)
        depth = _case_depth_after(code, depth)

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
    return ";", len(lines) - 1


def has_blocks(text: str) -> bool:
    state = {"quote": "", "comment": False}
    for line in text.splitlines():
        code = _code_only(line, state)
        if (_ALWAYS_SCRIPTING.match(code) or _SCRIPTING_UNLESS_CASE.match(code)
                or _LOOP_PLAIN.match(code) or _LOOP_START.match(code)
                or _RAISE.match(code) or _PROCEDURE.match(code)):
            return True
    return False
