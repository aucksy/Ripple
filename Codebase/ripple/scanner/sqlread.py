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

    def reading(self, table: str) -> list[Statement]:
        return [s for s in self.statements if s.reads_from(table)]


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
    if isinstance(stmt, (exp.Create, exp.Insert)):
        return _table_name(stmt.this)
    return None


def parse_file(f: SourceFile, cfg: Settings) -> tuple[list[Statement], list[dict]]:
    """Parse one file into statements. Failures are reported, never swallowed."""
    out: list[Statement] = []
    problems: list[dict] = []
    blocks = statements_for(f)
    if not blocks:
        return out, problems

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
    for sql_text, offset in blocks:
        try:
            parsed = sqlglot.parse(sql_text, read=dialect)
        except Exception as exc:
            problems.append(
                {
                    "file": f.path,
                    "reason": f"the SQL reader could not parse this file ({type(exc).__name__})",
                }
            )
            continue
        for stmt in parsed:
            if stmt is None:
                continue
            select = stmt.find(exp.Select)
            target = _target_of(stmt) or implied_target
            sources: set[str] = set()
            if select is not None:
                for t in select.find_all(exp.Table):
                    if t.name and t.name.upper() != (target or "").upper():
                        sources.add(t.name)
            out.append(
                Statement(
                    file=f.path,
                    lang=f.lang,
                    line_offset=offset,
                    sql=stmt.sql(),
                    target=target,
                    sources=sources,
                    select=select,
                    expr=stmt,
                )
            )
    return out, problems


def parse_repo(index: RepoIndex, cfg: Settings | None = None) -> ParsedRepo:
    cfg = cfg or default_settings
    pr = ParsedRepo()
    pr.unreadable.extend(index.skipped)
    for f in index.files:
        stmts, problems = parse_file(f, cfg)
        if stmts:
            pr.statements.extend(stmts)
            pr.parsed_files.add(f.path)
        pr.unreadable.extend(problems)
    return pr


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


def output_name(stmt: Statement, column: str) -> str:
    """The name this column is published under once the statement is done.

    Renames often happen inside a subquery -- ``c.last_upd AS lut_ts`` buried in
    a ranking, then simply carried out by the enclosing SELECT. Resolving from
    the innermost query outwards is what keeps the chain joined up; without it
    the trail goes cold at exactly the statements that matter most.
    """
    if stmt.expr is None:
        return column
    name = column
    selects = list(stmt.expr.find_all(exp.Select))  # outermost first
    for sel in reversed(selects):                   # so walk inner -> outer
        if any(isinstance(e, exp.Star) for e in sel.expressions):
            continue  # SELECT * carries the name through untouched
        for e in sel.expressions:
            if isinstance(e, exp.Alias):
                if any(c.name.upper() == name.upper() for c in e.find_all(exp.Column)):
                    name = e.alias
                    break
            elif isinstance(e, exp.Column) and e.name.upper() == name.upper():
                name = e.name
                break
    return name


def usages_of(stmt: Statement, column: str) -> list[Usage]:
    """Every way `column` is used by this statement, across all its subqueries."""
    if stmt.expr is None or stmt.select is None:
        return []
    found: list[Usage] = []
    alias_for_column = output_name(stmt, column)

    for sel in stmt.expr.find_all(exp.Select):
        # 1. the select list
        for e in sel.expressions:
            if not _cols_named(e, column):
                continue
            inner = e.this if isinstance(e, exp.Alias) else e
            if isinstance(inner, exp.Column):
                found.append(Usage(kind="select", column=column, alias=alias_for_column))
            else:
                fn = inner.__class__.__name__.upper() if inner is not None else ""
                found.append(
                    Usage(kind="transform", column=column, alias=alias_for_column, detail=fn)
                )

        # 2. WHERE / HAVING
        for clause_key in ("where", "having"):
            clause = sel.args.get(clause_key)
            for c in _cols_named(clause, column):
                found.append(
                    Usage(kind="filter", column=column, alias=alias_for_column,
                          detail=_literal_beside(clause, c))
                )

        # 3. JOIN ... ON
        for j in sel.args.get("joins") or []:
            on = j.args.get("on")
            if _cols_named(on, column):
                found.append(Usage(kind="join_key", column=column, alias=alias_for_column))

        # 4. GROUP BY
        if _cols_named(sel.args.get("group"), column):
            found.append(Usage(kind="aggregation", column=column, alias=alias_for_column))

    # 5. window ORDER BY -- the ranking case, where removal is silent and awful
    for w in stmt.expr.find_all(exp.Window):
        if _cols_named(w.args.get("order"), column):
            found.append(Usage(kind="ranking", column=column, alias=alias_for_column))

    # 6. aggregates that pick which row survives
    for agg in list(stmt.expr.find_all(exp.Max)) + list(stmt.expr.find_all(exp.Min)):
        if _cols_named(agg, column):
            found.append(
                Usage(kind="dedup_key", column=column, alias=alias_for_column,
                      detail=agg.__class__.__name__.upper())
            )

    # keep the most informative reading of each kind, most consequential first
    seen: dict[str, Usage] = {}
    for u in found:
        if u.kind not in seen or (u.detail and not seen[u.kind].detail):
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
