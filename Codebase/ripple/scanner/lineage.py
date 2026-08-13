"""Following a column through the pipeline, and saying what it means.

A column rarely keeps its name. MARKET_CODE becomes mc, then mkt_cd, and the
thing that finally breaks is three files away from the one the notification
named. This module walks that chain and groups what it finds under the
production table each chain ends at -- because that is the thing an engineer
actually has to defend.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from sqlglot import exp

from ..config import Settings, settings as default_settings
from .repo import RepoIndex
from .sqlread import ParsedRepo, Usage, mode_of, locate, output_names, snippet, usages_of

# What a given kind of change does to a given kind of usage.
BREAKS = {
    "removal":      {"filter", "join_key", "ranking", "dedup_key", "transform", "aggregation", "select"},
    "rename":       {"filter", "join_key", "ranking", "dedup_key", "transform", "aggregation", "select"},
    "value_change": {"filter", "join_key", "transform"},
    "type_change":  {"filter", "join_key", "transform"},
    "unknown":      {"filter", "join_key", "ranking", "dedup_key", "transform"},
}
# Usages with no local fix: the replacement has to come from the upstream team.
NO_LOCAL_FIX = {"ranking", "dedup_key"}


def _impact_sentence(u: Usage, change_type: str, target: str | None) -> str:
    tgt = target or "the next table"
    lit = f" '{u.detail}'" if u.kind == "filter" and u.detail else ""
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
        return (f"{u.detail or 'An aggregate'} on this column decides which row survives. "
                f"Without it {tgt} can publish stale records with no error.")
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
    # Whether the statement said which table this column came from. False means
    # the usage is real and on that line, but the same column name is in more
    # than one table the statement reads and the SQL did not say whose it is.
    # Shown, never dropped -- and never asserted either.
    certain: bool = True

    def key(self) -> tuple:
        return (self.file, self.source_table, self.source_column, self.kind)


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
    mentions_only: list[dict] = field(default_factory=list)
    # Files that were never opened at all, which is a different and worse thing
    # than a file that was read and not understood. A scan over a repository
    # half of which was never opened produces a short finding list and a green
    # tick, and that green tick is the only thing this tool sells.
    held_online: list[str] = field(default_factory=list)
    too_long: list[str] = field(default_factory=list)
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
            "filesScanned": self.files_scanned,
            "filesMatched": self.files_matched,
            "risk": self.risk,
            "stats": self.stats(),
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
    res.files_scanned = len(index.files)
    res.unreadable = list(parsed.unreadable)
    res.held_online = list(index.held_online)
    res.too_long = list(index.too_long)
    breaks = BREAKS.get(change_type, BREAKS["unknown"])

    all_names: list[str] = []
    for u in upstream:
        all_names.append(u["table"])
        all_names.extend(u.get("attrs") or [])
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

    for up in upstream:
        table = up["table"]
        for attr in up.get("attrs") or []:
            branches: list[list[dict]] = []
            end_branches: list[list[dict]] = []
            attr_findings: list[Finding] = []

            def walk(cur_table: str, cur_col: str, hop: int, path: list[dict],
                     chain: list[Finding], seen: set) -> bool:
                """Follow the column onwards. True if anything was recorded."""
                if hop >= cfg.max_hops:
                    return False
                key = (cur_table.upper(), cur_col.upper())
                if key in seen:
                    return False
                seen = seen | {key}
                recorded = False

                for stmt in parsed.reading(cur_table):
                    looked[0] += 1
                    if on_progress is not None and looked[0] % 200 == 0:
                        on_progress(looked[0], 0,
                                    f"Following {cur_col} — {len(findings_by_key)} usages so far")
                    us = usages_of(stmt, cur_col, cur_table)
                    if not us:
                        continue
                    primary = us[0]
                    src = index.get(stmt.file)
                    if src is None:
                        continue
                    hit = locate(src, cur_col, primary.kind, stmt.line_offset)
                    note = {
                        "filter": "Filter - stops matching after the change",
                        "join_key": "Join key - verify both sides change together",
                        "ranking": "Ranking order - breaks silently if removed",
                        "dedup_key": "Decides which row survives",
                        "transform": "Value is reshaped here",
                        "aggregation": "Group label changes with the value",
                        "select": f"Carried forward as {primary.alias or cur_col}",
                    }.get(primary.kind, "Used here")

                    f = Finding(
                        source_table=cur_table,
                        source_column=cur_col,
                        target_table=stmt.target,
                        alias=primary.alias or cur_col,
                        logic=primary.label,
                        kind=primary.kind,
                        mode=mode_of(us),
                        impact=_impact_sentence(primary, change_type, stmt.target),
                        breaking=primary.kind in breaks,
                        no_local_fix=primary.kind in NO_LOCAL_FIX
                        and change_type in ("removal", "rename"),
                        file=stmt.file,
                        lang=src.lang,
                        lines=snippet(src, hit, note),
                        hop=hop,
                        certain=primary.certain,
                    )
                    findings_by_key.setdefault(f.key(), f)
                    f = findings_by_key[f.key()]
                    if f not in attr_findings:
                        attr_findings.append(f)
                    new_chain = chain + [f]

                    tgt = stmt.target
                    if not tgt:
                        continue
                    node = {
                        "name": tgt,
                        "kind": _kind_of_node(tgt, cfg),
                        "alias": primary.alias or cur_col,
                    }
                    # A column can leave a statement under more than one name --
                    # reshaped into one column and passed through unchanged as
                    # another, in the same SELECT. Following only one of them
                    # stopped the chain one table short of the published table
                    # that reads the other, and reported no production impact.
                    onwards = output_names(stmt, cur_col)
                    if cfg.is_production_table(tgt):
                        node["prod"] = True
                        branch = path + [node]
                        if branch not in branches:
                            branches.append(branch)
                        _collect(prod_groups, tgt, new_chain)
                        recorded = True
                        # And keep going. One published table feeding another is
                        # exactly how a change spreads, and stopping at the first
                        # one under-counts the number this whole tool is judged
                        # on -- while showing a shorter chain than the real one.
                        for onward in onwards:
                            walk(tgt, onward, hop + 1, path + [node], new_chain, seen)
                        continue
                    if any(walk(tgt, onward, hop + 1, path + [node], new_chain, seen)
                           for onward in onwards):
                        recorded = True
                    else:
                        # Nothing further is built from this table, so the trail
                        # ends here. Recorded rather than dropped: an end that
                        # does not happen to match the production naming rule is
                        # still a table somebody has to look at.
                        branch = path + [node]
                        if branch not in end_branches:
                            end_branches.append(branch)
                        _collect(end_groups, tgt, new_chain)
                        recorded = True
                return recorded

            walk(table, attr, 0, [], [], set())

            # A chain that carries on past a published table is drawn once, at
            # its full length. The shorter version of it is the same chain with
            # the end cut off, and drawing both reads as two findings.
            branches = _longest_only(branches)
            end_branches = _longest_only(end_branches)

            res.findings.extend([f for f in attr_findings if f not in res.findings])
            if branches or end_branches:
                graphs.append({"attr": attr, "table": table,
                               "branches": branches, "endBranches": end_branches})
            res.attributes.append(
                {
                    "table": table,
                    "attr": attr,
                    "found": len(attr_findings),
                    "files": len({f.file for f in attr_findings}),
                    # How many files so much as write the name down. Zero here
                    # is the answer to "why did it find nothing?" -- the name is
                    # not in this repository at all.
                    "mentionedIn": len({m.file for m in index.search([attr])}),
                    "reachesProduction": bool(branches),
                    "endsAt": sorted({b[-1]["name"] for b in end_branches}),
                    # How widely this column name is used as a name. A scan for
                    # a name half the warehouse shares is a different kind of
                    # answer from a scan for a name only one table has, and the
                    # screen has no way to say so without these two numbers.
                    "nameInTables": shared.get(attr.upper(), 0),
                    "tablesRead": table_count,
                    # Findings on lines where the SQL did not say which table
                    # the column came from. Real usages; the table is inferred.
                    "uncertain": len([f for f in attr_findings if not f.certain]),
                }
            )

    res.graphs = graphs
    res.groups = [
        {
            "prod": prod,
            "note": f"Published by this team - {_kind_of_node(prod, cfg).lower()} table",
            "rows": [_finding_row(f) for f in fs],
        }
        for prod, fs in sorted(prod_groups.items())
    ]
    placed = {f.key() for fs in prod_groups.values() for f in fs}
    res.reached = [
        {
            "prod": table,
            "note": "Last table in the chain - not matched by your production naming rule",
            "rows": [_finding_row(f) for f in fs],
        }
        for table, fs in sorted(end_groups.items())
    ]
    placed |= {f.key() for fs in end_groups.values() for f in fs}
    res.other = [_finding_row(f) for f in res.findings if f.key() not in placed]

    # Honesty: anything the search matched but the reader could not turn into a
    # finding is surfaced, never quietly dropped. Which of the three things it
    # is matters enormously -- "the name is written down here and nothing reads
    # it" is reassuring, and "the name is inside a call I cannot follow" is the
    # opposite, and they used to be told apart by nothing at all.
    impacted_files = {f.file for f in res.findings}
    already = {u.get("file"): u for u in res.unreadable}
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

    res.risk = _risk_of(res)
    return res


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
        match = pattern.search(record.get("sql") or record.get("text") or "")
        if match:
            line, text = _line_naming(src, match.group(1))
            return {
                "file": path,
                "reason": "the name is used in a statement Ripple cannot follow",
                "line": line,
                "snippet": text,
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
            line, text = _line_naming(src, match.group(1))
            return {
                "file": path,
                "reason": f'the name appears as text inside a call - "{match.group(1)}"',
                "line": line,
                "snippet": text,
                "hint": "Written as a quoted string rather than used as a column, which is "
                        "how in-house helpers take a column or table name. Ripple cannot "
                        "follow what the helper does with it.",
            }
    return None


def _line_naming(src, name: str) -> tuple[int, str]:
    """The line of the real file where this name is written, and that line.

    Quoted occurrences win: that is the one being reported, and it is the line
    somebody has to open the file at.
    """
    if src is None:
        return 1, ""
    quoted = re.compile(r"['\"]" + re.escape(name) + r"['\"]", re.IGNORECASE)
    plain = re.compile(r"\b" + re.escape(name) + r"\b", re.IGNORECASE)
    fallback = None
    for number, line in enumerate(src.lines, start=1):
        if quoted.search(line):
            return number, line.strip()[:140]
        if fallback is None and plain.search(line):
            fallback = (number, line.strip()[:140])
    return fallback or (1, "")


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
        if isinstance(schema, exp.Schema):
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
    }


def _risk_of(res: ScanResult) -> str:
    if not res.findings:
        return "none"
    if any(f.no_local_fix for f in res.findings):
        return "high"
    if any(f.breaking for f in res.findings):
        return "medium"
    return "low"
