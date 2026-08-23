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
    RENAME_NODE, from_of, merge_whens, star_except,
)
from .templating import (
    describe as describe_templating,
    fill_placeholders,
    has_blocks,
    has_placeholders,
    placeholder_names,
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
    "sort": "Sort order",
    "select": "Select",
    "star": "Carried by SELECT *",
}
# Most consequential first: if a column is used several ways in one statement,
# this decides which one heads the finding.
KIND_PRIORITY = ["ranking", "dedup_key", "filter", "join_key", "transform", "aggregation",
                 "sort", "excluded", "select", "star"]

# Words that make a line likely to be the one a given usage lives on.
KIND_MARKERS = {
    "filter": ("WHERE", "AND ", "OR ", "HAVING"),
    "join_key": ("JOIN", " ON "),
    "ranking": ("ORDER BY", "OVER", "ROW_NUMBER", "RANK"),
    "aggregation": ("GROUP BY",),
    "dedup_key": ("MAX(", "MIN(", "GROUP BY"),
    "transform": ("SUBSTR", "CAST", "TRIM", "UPPER", "LOWER", "COALESCE", "CONCAT", "("),
    "excluded": ("EXCEPT", "SELECT"),
    "sort": ("ORDER BY",),
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


def wildcard_covers(pattern: str, name: str) -> bool:
    """Does the wildcard name ``pattern`` cover the table name ``name``?

    Both are compared on their short names, because the dataset is ruled on
    separately by ``same_table`` for the reason given further up this file.
    """
    prefix = short_name(pattern).upper()
    if not prefix.endswith(_STAR):
        return False
    prefix = prefix[:-1]
    # A bare "*" -- the whole of a dataset. It genuinely does read every table
    # there, but matching on it here would put every table in the repository on
    # every chain, which is not a spare row somebody can dismiss, it is the
    # whole warehouse. It is ruled on in same_table instead, where the dataset
    # is known and can scope it.
    if not prefix:
        return False
    other = short_name(name).upper()
    if other.endswith(_STAR):
        # Two wildcards. They are the same family if either prefix contains the
        # other -- ``customer_*`` and ``customer_demographics_*`` overlap, and
        # following both is the safe direction.
        other = other[:-1]
        return other.startswith(prefix) or prefix.startswith(other)
    if other.startswith(prefix):
        return True                      # the real shard: customer_demographics_20260101
    # The family named the way a person says it, without the separator the
    # wildcard was written with. Deliberately tight: it matches the whole prefix
    # bar its trailing separator and nothing shorter, so ``ev`` never matches
    # ``events_*``.
    return bool(prefix) and prefix.rstrip("_-") == other


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
    # Worked out once and kept. One scan asks the same statement about the same
    # column many times over, and on a 600-line statement each answer means
    # walking the whole expression tree again. Measured on a repository the size
    # of his, this was most of the time a scan took.
    _names: dict = field(default_factory=dict, repr=False, compare=False)
    _projected: list | None = field(default=None, repr=False, compare=False)
    _sources_upper: set | None = field(default=None, repr=False, compare=False)

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
            return candidates
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
        self._index()
        short = short_name(table).upper()
        # Given back as the SQL spells it, not as the index keys it. This goes
        # on screen and into the text search, and neither wants shouting.
        return sorted(sorted(self._spellings.get(p, {p}))[0]
                      for p in self._wildcards
                      if p != short and wildcard_covers(p, short))

    def _index(self) -> None:
        if self._by_source is not None and self._indexed == len(self.statements):
            return
        by_source: dict[str, list[Statement]] = {}
        wild: dict[str, list[Statement]] = {}
        seen: dict[str, set[str]] = {}
        spelt: dict[str, set[str]] = {}
        bare: set[str] = set()
        for s in self.statements:
            for src in s.sources:
                key = short_name(src).upper()
                by_source.setdefault(key, []).append(s)
                if key.endswith(_STAR):
                    wild.setdefault(key, []).append(s)
            for name in list(s.sources) + ([s.target] if s.target else []):
                short = short_name(name)
                ds = dataset_of(name)
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
        if short_name(table).upper() in self.ambiguous_names():
            return table
        return short_name(table)

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
    tvf = _table_function_target(stmt)
    if tvf:
        return tvf
    if isinstance(stmt, (exp.Create, exp.Insert, exp.Merge, exp.Delete, exp.Update)):
        return _table_name(stmt.this)
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
        # No SQL came out. Before treating the file as empty, work out whether
        # it is empty or whether the SQL is simply somewhere this reader cannot
        # follow -- a DAG that runs a .sql file, or a statement glued together
        # from short strings. Both used to be indistinguishable from a config
        # file with nothing in it.
        if looks_like_unread_sql(f, blocks):
            problems.append({
                "file": f.path,
                "reason": "there is SQL written in this file that Ripple could not take out of it",
                "line": 1,
                "snippet": _first_code_line(f.text),
                "hint": ("The statement is most likely built by adding short pieces of text "
                         "together, so it never exists in the file as one thing to read. "
                         "Nothing in it has been followed - open it and check by hand."),
            })
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
        text = rescue.rewrite(text)
        parsed, bad = _parse_text(text, dialect, offset)
        failures.extend(bad)
        for stmt, line, line_end in parsed:
            if holes:
                _forget_templated_datasets(stmt, holes)
            # A scripting block, a loop, a procedure call, an EXECUTE IMMEDIATE.
            # Kept, not reported: whether it matters depends on whether the name
            # somebody is chasing turns up inside it, which is not known here.
            if isinstance(stmt, exp.Command):
                raw = stmt.sql()
                again = _reparse_snapshot(raw, dialect)
                if again is None:
                    opaque.append({"line": line + 1, "text": _first_code_line(raw),
                                   "sql": raw[:8000]})
                    continue
                stmt = again
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
                    if qualified and t.name.upper() not in skip:
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
            if isinstance(stmt, (exp.Delete, exp.Update)) and target:
                sources.add(target)
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
        problems.extend(file_problems)
    problems.extend(_follow_sql_file_refs(index, pr))
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


def _belongs_to(col: exp.Column, stmt: Statement, table: str,
                sources: dict[str, list[str]], ctes: set[str]) -> str:
    """'yes', 'no' or 'unknown' -- is this column reference `table`'s?"""
    qualifier = col.table
    if not qualifier:
        # Unqualified. If the statement only reads one table it can only have
        # come from there. If it reads several, the SQL has not said.
        return "yes" if len(stmt.sources) <= 1 else "unknown"
    options = sources.get(qualifier.upper())
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


def _stars_over(stmt: Statement, table: str, sources: dict[str, list[str]]) -> list[exp.Star]:
    """Every ``SELECT *`` in this statement that covers `table`'s columns."""
    if stmt.expr is None:
        return []
    found: list[exp.Star] = []
    for sel in stmt.expr.find_all(exp.Select):
        reads = _direct_tables(sel)
        if not any(same_table(t, table) for t in reads):
            continue
        for e in sel.expressions:
            if isinstance(e, exp.Star):
                found.append(e)                      # SELECT * -- everything
            elif isinstance(e, exp.Column) and isinstance(e.this, exp.Star):
                # a.* -- only the table that alias stands for
                for option in sources.get((e.table or "").upper(), []):
                    if same_table(option, table):
                        found.append(e.this)
                        break
    return found


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
    cached = stmt._names.get(column.upper())
    if cached is not None:
        return cached
    names = [column]
    for direct_map, derived_map, passthrough, dropped in _projections(stmt):
        direct: list[str] = []
        derived: list[str] = []
        for name in names:
            direct.extend(direct_map.get(name.upper(), ()))
        for name in names:
            derived.extend(derived_map.get(name.upper(), ()))
        found = _dedupe(direct + derived)
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
    stmt._names[column.upper()] = names
    return names


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


def _select_depth(sel: exp.Select) -> int:
    """How many SELECTs this one is nested inside."""
    depth = 0
    node = sel.parent
    while node is not None:
        if isinstance(node, exp.Select):
            depth += 1
        node = node.parent
    return depth


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
        by_depth.setdefault(_select_depth(sel), []).append(sel)

    out: list[tuple[dict, dict, bool, set]] = []
    for depth in sorted(by_depth, reverse=True):            # innermost first
        direct: dict[str, list[str]] = {}
        derived: dict[str, list[str]] = {}
        dropped: set[str] = set()
        passthrough = False
        for sel in by_depth[depth]:
            for e in sel.expressions:
                if _is_star(e):
                    passthrough = True
                    star = _star_of(e)
                    for c in star_except(star):
                        dropped.add(getattr(c, "name", "").upper())
                    # RENAME(cm13 AS cm13_new) and REPLACE(UPPER(cm13) AS cm13)
                    # both change what leaves under which name, so a star is not
                    # always a plain pass-through.
                    for a in star.args.get("rename") or []:
                        if isinstance(a, exp.Alias) and isinstance(a.this, exp.Column):
                            dropped.add(a.this.name.upper())
                            direct.setdefault(a.this.name.upper(), []).append(a.alias)
                    for a in star.args.get("replace") or []:
                        if isinstance(a, exp.Alias):
                            for c in a.find_all(exp.Column):
                                derived.setdefault(c.name.upper(), []).append(a.alias)
                elif isinstance(e, exp.Alias):
                    inner = e.this
                    if isinstance(inner, exp.Column):
                        direct.setdefault(inner.name.upper(), []).append(e.alias)
                    else:
                        for c in e.find_all(exp.Column):
                            derived.setdefault(c.name.upper(), []).append(e.alias)
                elif isinstance(e, exp.Column):
                    direct.setdefault(e.name.upper(), []).append(e.name)
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
                for r in _star_of(e).args.get("replace") or []:
                    # REPLACE(UPPER(cm13) AS cm13) genuinely reshapes the value.
                    cols, sure = owned(r)
                    if cols:
                        found.append(Usage(kind="transform", column=column,
                                           alias=alias_for_column, detail="REPLACE",
                                           certain=sure))
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
    if table:
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
