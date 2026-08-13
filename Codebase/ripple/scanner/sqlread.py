"""Reading SQL properly, rather than just matching words.

The whole value of Ripple is in this file. A word search can tell you that
MARKET_CODE appears in a file. Only parsing can tell you that it appears
*inside a WHERE clause comparing it to the literal 'US'* -- which is the
difference between "mentioned here" and "this breaks on the 18th".
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import sqlglot
from sqlglot import exp

from ..config import Settings, settings as default_settings
from .repo import RepoIndex, SourceFile, statements_for, written_tables
from .templating import (
    describe as describe_templating,
    fill_placeholders,
    has_blocks,
    has_placeholders,
    unwrap_blocks,
)

# sqlglot narrates its fallbacks to the log; that noise is not useful here
# because we surface every genuinely unreadable file ourselves.
import logging

logging.getLogger("sqlglot").setLevel(logging.ERROR)

# How a usage is shown to the user, in the order we prefer to report it.
LOGIC_LABEL = {
    "filter": "Filter",
    "join_key": "Join key",
    "ranking": "Ranking",
    "dedup_key": "Dedup key",
    "aggregation": "Aggregation",
    "transform": "Transform",
    "select": "Select",
}
# Most consequential first: if a column is used several ways in one statement,
# this decides which one heads the finding.
KIND_PRIORITY = ["ranking", "dedup_key", "filter", "join_key", "transform", "aggregation", "select"]

# Words that make a line likely to be the one a given usage lives on.
KIND_MARKERS = {
    "filter": ("WHERE", "AND ", "OR ", "HAVING"),
    "join_key": ("JOIN", " ON "),
    "ranking": ("ORDER BY", "OVER", "ROW_NUMBER", "RANK"),
    "aggregation": ("GROUP BY",),
    "dedup_key": ("MAX(", "MIN(", "GROUP BY"),
    "transform": ("SUBSTR", "CAST", "TRIM", "UPPER", "LOWER", "COALESCE", "CONCAT", "("),
    "select": ("SELECT", " AS "),
}


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

    @property
    def label(self) -> str:
        return LOGIC_LABEL.get(self.kind, self.kind.title())


@dataclass
class Statement:
    file: str
    lang: str
    line_offset: int
    sql: str
    target: str | None
    sources: set[str]
    select: exp.Select | None
    expr: exp.Expression | None

    def reads_from(self, table: str) -> bool:
        return table.upper() in {s.upper() for s in self.sources}


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

    def reading(self, table: str) -> list[Statement]:
        return [s for s in self.statements if s.reads_from(table)]

    def statements_in(self, path: str) -> list[Statement]:
        return [s for s in self.statements if s.file == path]


# ── parsing ────────────────────────────────────────────────────────────────
def _table_name(node: exp.Expression | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, exp.Schema):
        node = node.this
    if isinstance(node, exp.Table):
        return node.name
    if isinstance(node, exp.Expression):
        t = node.find(exp.Table)
        if t is not None:
            return t.name
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
    if isinstance(stmt, (exp.Create, exp.Insert, exp.Merge, exp.Delete, exp.Update)):
        return _table_name(stmt.this)
    return None


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


def _parse_text(
    text: str, dialect: str | None, base_line: int
) -> tuple[list[tuple[exp.Expression, int]], list[dict]]:
    """Parse a block; if it is refused, parse it one statement at a time."""
    try:
        got = sqlglot.parse(text, read=dialect)
        return [(s, base_line) for s in got if s is not None], []
    except Exception:
        pass
    good: list[tuple[exp.Expression, int]] = []
    bad: list[dict] = []
    for chunk, line in split_statements(text):
        try:
            got = sqlglot.parse(chunk, read=dialect)
        except Exception:
            bad.append({"line": base_line + line + 1, "text": _first_code_line(chunk)})
            continue
        good.extend((s, base_line + line) for s in got if s is not None)
    return good, bad


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


def parse_file(f: SourceFile, cfg: Settings) -> tuple[list[Statement], list[dict], list[dict]]:
    """Parse one file into statements, failures, and statements not understood.

    Failures are reported, never swallowed. The third list is the statements the
    reader took in but could not make sense of; they are handed back rather than
    reported, because whether they matter depends on the scan.
    """
    out: list[Statement] = []
    problems: list[dict] = []
    blocks = statements_for(f)
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
        text = fill_placeholders(sql_text) if has_placeholders(sql_text) else sql_text
        text = unwrap_blocks(text) if has_blocks(text) else text
        parsed, bad = _parse_text(text, dialect, offset)
        failures.extend(bad)
        for stmt, line in parsed:
            # A scripting block, a loop, a procedure call, an EXECUTE IMMEDIATE.
            # Kept, not reported: whether it matters depends on whether the name
            # somebody is chasing turns up inside it, which is not known here.
            if isinstance(stmt, exp.Command):
                raw = stmt.sql()
                opaque.append({"line": line + 1, "text": _first_code_line(raw),
                               "sql": raw[:8000]})
                continue
            select = stmt.find(exp.Select)
            target = _target_of(stmt) or implied_target
            sources: set[str] = set()
            skip = _cte_names(stmt)
            if select is not None:
                for t in select.find_all(exp.Table):
                    if t.name and t.name.upper() not in skip and t.name.upper() != (target or "").upper():
                        sources.add(t.name)
            # A DELETE or an UPDATE reads the table it changes. Without this the
            # statement has no source, so nothing ever looks at its WHERE clause
            # -- and a filter on a column that is about to disappear is exactly
            # the kind of thing this tool exists to find.
            if isinstance(stmt, (exp.Delete, exp.Update)) and target:
                sources.add(target)
            out.append(
                Statement(
                    file=f.path,
                    lang=f.lang,
                    line_offset=line,
                    sql=stmt.sql(),
                    target=target,
                    sources=sources,
                    select=select,
                    expr=stmt,
                )
            )
    if failures:
        failures.sort(key=lambda p: p["line"])
        problems.append(_why_not(f, cfg, failures, len(out)))
    elif opaque and not out:
        # Nothing in this file was understood. The reader did not fall over, it
        # simply got nothing out -- which is the quietest way to lose a file and
        # the reason the wrong SQL dialect used to look like a clean repository.
        first = opaque[0]
        problems.append({
            "file": f.path,
            "reason": f"read, but not one of its {len(opaque)} statements was understood",
            "line": first["line"],
            "snippet": first["text"],
            "hint": ("Nothing was learned from this file at all - no table, no column, no "
                     "lineage." + ("" if cfg.sql_dialect else
                     " This repository is being read as generic SQL; if it is BigQuery, "
                     "Snowflake or anything else in particular, choose that on the settings "
                     "screen.")),
        })
    return out, problems, opaque


def parse_repo(index: RepoIndex, cfg: Settings | None = None) -> ParsedRepo:
    cfg = cfg or default_settings
    pr = ParsedRepo()
    problems: list[dict] = list(index.skipped)
    for f in index.files:
        stmts, file_problems, opaque = parse_file(f, cfg)
        if stmts:
            pr.statements.extend(stmts)
            pr.parsed_files.add(f.path)
        if opaque:
            pr.opaque[f.path] = opaque
        problems.extend(file_problems)
    pr.unreadable = _one_entry_per_file(problems)
    return pr


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


def _sources_of(stmt: Statement) -> dict[str, str]:
    """Every alias and table name this statement reads, pointing at its table."""
    out: dict[str, str] = {}
    if stmt.expr is None:
        return out
    for t in stmt.expr.find_all(exp.Table):
        if not t.name:
            continue
        out.setdefault(t.name.upper(), t.name)
        alias = t.alias
        if alias:
            out[alias.upper()] = t.name
    return out


def _belongs_to(col: exp.Column, stmt: Statement, table: str,
                sources: dict[str, str], ctes: set[str]) -> str:
    """'yes', 'no' or 'unknown' -- is this column reference `table`'s?"""
    qualifier = col.table
    if not qualifier:
        # Unqualified. If the statement only reads one table it can only have
        # come from there. If it reads several, the SQL has not said.
        return "yes" if len(stmt.sources) <= 1 else "unknown"
    resolved = sources.get(qualifier.upper())
    if resolved is None:
        return "unknown"                 # an alias from somewhere we cannot see
    if resolved.upper() in ctes:
        # It came out of a WITH block, which was itself built from something.
        # That is exactly the chain being followed, so it is not a reason to
        # rule the usage out.
        return "unknown"
    return "yes" if resolved.upper() == table.upper() else "no"


# ── working out how a column is used ───────────────────────────────────────
def _cols_named(node: exp.Expression | None, name: str) -> list[exp.Column]:
    if node is None:
        return []
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
    names = [column]
    selects = list(stmt.expr.find_all(exp.Select))  # outermost first
    for sel in reversed(selects):                   # so walk inner -> outer
        if any(isinstance(e, exp.Star) for e in sel.expressions):
            continue  # SELECT * carries every name through untouched
        direct: list[str] = []
        derived: list[str] = []
        for name in names:
            for e in sel.expressions:
                if isinstance(e, exp.Alias):
                    inner = e.this
                    if isinstance(inner, exp.Column) and inner.name.upper() == name.upper():
                        direct.append(e.alias)      # cm13 AS customer_key
                    elif any(c.name.upper() == name.upper() for c in e.find_all(exp.Column)):
                        derived.append(e.alias)     # CAST(cm13 AS STRING) AS cm13_str
                elif isinstance(e, exp.Column) and e.name.upper() == name.upper():
                    direct.append(e.name)           # cm13, or c.cm13
        found = _dedupe(direct + derived)
        # Not projected at this level at all. That is normal -- the column may
        # only be in a WHERE or a JOIN here -- so the name it had carries on
        # rather than the trail being dropped.
        names = found[:limit] if found else names
    return names


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
    """The one name to show on screen for this column. See output_names."""
    return output_names(stmt, column)[0]


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
    found: list[Usage] = []
    alias_for_column = output_name(stmt, column)
    sources = _sources_of(stmt) if table else {}
    ctes = _cte_names(stmt.expr) if table else set()

    def owned(node: exp.Expression | None) -> tuple[list[exp.Column], bool]:
        """This table's references to the column, and whether the SQL said so."""
        cols = _cols_named(node, column)
        if not table or not cols:
            return cols, True
        keep: list[exp.Column] = []
        certain = True
        for c in cols:
            verdict = _belongs_to(c, stmt, table, sources, ctes)
            if verdict == "no":
                continue                 # plainly another table's column
            if verdict == "unknown":
                certain = False          # kept, and marked rather than asserted
            keep.append(c)
        return keep, certain

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

    if stmt.select is None:
        return _best_of(found)

    for sel in stmt.expr.find_all(exp.Select):
        # 1. the select list
        for e in sel.expressions:
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

        # 2. WHERE / HAVING
        for clause_key in ("where", "having"):
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

        # 4. GROUP BY
        cols, sure = owned(sel.args.get("group"))
        if cols:
            found.append(Usage(kind="aggregation", column=column, alias=alias_for_column,
                               certain=sure))

    # 5. window ORDER BY -- the ranking case, where removal is silent and awful
    for w in stmt.expr.find_all(exp.Window):
        cols, sure = owned(w.args.get("order"))
        if cols:
            found.append(Usage(kind="ranking", column=column, alias=alias_for_column,
                               certain=sure))

    # 6. aggregates that pick which row survives
    for agg in list(stmt.expr.find_all(exp.Max)) + list(stmt.expr.find_all(exp.Min)):
        cols, sure = owned(agg)
        if cols:
            found.append(
                Usage(kind="dedup_key", column=column, alias=alias_for_column,
                      detail=agg.__class__.__name__.upper(), certain=sure)
            )

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
def locate(f: SourceFile, column: str, kind: str, line_offset: int = 0) -> int:
    """Best guess at the 1-based line where this usage lives."""
    pat = re.compile(r"\b" + re.escape(column) + r"\b", re.IGNORECASE)
    markers = KIND_MARKERS.get(kind, ())
    best, best_score = None, -1
    for i, line in enumerate(f.lines, start=1):
        if i <= line_offset:
            continue
        if not pat.search(line):
            continue
        up = line.upper()
        score = 1 + sum(2 for m in markers if m in up)
        if score > best_score:
            best, best_score = i, score
    if best is None:
        for i, line in enumerate(f.lines, start=1):
            if pat.search(line):
                return i
    return best or 1


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
