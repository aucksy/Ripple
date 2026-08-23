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
from .dialectcompat import merge_whens
from .repo import RepoIndex
from .sqlread import (
    ParsedRepo,
    Usage,
    canonical,
    dataset_of,
    is_wildcard,
    same_table,
    mode_of,
    locate,
    output_names,
    short_name,
    snippet,
    usages_of,
)

# What a given kind of change does to a given kind of usage.
#
# "star" is in none of them, and that is deliberate. A SELECT * does not fail
# when a column disappears -- it quietly builds a narrower table, and the thing
# that breaks is whatever reads the missing column further down. Calling the
# star hop itself breaking would put a red badge on the one row in the chain
# that carries on working.
BREAKS = {
    "removal":      {"filter", "join_key", "ranking", "dedup_key", "transform", "aggregation",
                     "sort", "excluded", "select"},
    "rename":       {"filter", "join_key", "ranking", "dedup_key", "transform", "aggregation",
                     "sort", "excluded", "select"},
    "value_change": {"filter", "join_key", "transform"},
    "type_change":  {"filter", "join_key", "transform"},
    "unknown":      {"filter", "join_key", "ranking", "dedup_key", "transform", "sort"},
}
# Usages with no local fix: the replacement has to come from the upstream team.
NO_LOCAL_FIX = {"ranking", "dedup_key"}


def _impact_sentence(u: Usage, change_type: str, target: str | None,
                     copied_by: str = "") -> str:
    tgt = target or "the next table"
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
        return (f"This statement takes every column EXCEPT this one by name. The column never "
                f"reaches {tgt}, so the trail stops here - but the name is written down, so "
                f"removing or renaming it makes this statement itself fail.")
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
    # Published tables that are not built FROM this column, but that stop being
    # refreshed because the statement feeding them stops running on the day of
    # the change. A different kind of impact from the findings above, and it
    # must never be presented as the same one.
    stops_loading: list[dict] = field(default_factory=list)
    # True when the walk that found them hit its own ceiling. A cap nobody is
    # told about reads as "there were only these".
    stops_loading_capped: bool = False
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
            "stopsLoading": self.stops_loading,
            "stopsLoadingCapped": self.stops_loading_capped,
            "maxHops": self.max_hops,
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
        """
        if is_wildcard(name):
            return
        key = short_name(name).upper()
        if key in wild_seen:
            return
        patterns = parsed.wildcards_covering(name)
        if patterns:
            wild_seen[key] = {"table": short_name(name), "patterns": patterns}

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
                if hop >= cfg.max_hops:
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
                        "excluded": "Named in EXCEPT - dropped here, and breaks here",
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
                                                stmt.whole_copy),
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
                        inferred_hops=inferred + (1 if carried_by_star else 0),
                        at=stmt.line_offset,
                    )
                    findings_by_key.setdefault(f.key(), f)
                    f = findings_by_key[f.key()]
                    if attr not in f.roots:
                        f.roots.append(attr)
                    if f not in attr_findings:
                        attr_findings.append(f)
                    new_chain = chain + [f]

                    tgt = stmt.target
                    if not tgt:
                        continue
                    shown = show(tgt)
                    node = {
                        "name": shown,
                        "kind": _kind_of_node(short_name(tgt), cfg),
                        "alias": primary.alias or cur_col,
                    }
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
    res.wildcard_names = sorted(wild_seen.values(), key=lambda w: w["table"].upper())
    placed |= {f.key() for fs in end_groups.values() for f in fs}
    res.other = [_finding_row(f) for f in res.findings if f.key() not in placed]

    # Honesty: anything the search matched but the reader could not turn into a
    # finding is surfaced, never quietly dropped. Which of the three things it
    # is matters enormously -- "the name is written down here and nothing reads
    # it" is reassuring, and "the name is inside a call I cannot follow" is the
    # opposite, and they used to be told apart by nothing at all.
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
            broken.setdefault(short_name(f.target_table).upper(), f.target_table)
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

    res.risk = _risk_of(res)
    return res


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
    for _ in range(max(1, cfg.max_hops)):
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


def _opaque_on_the_trail(index: RepoIndex, parsed: ParsedRepo, visited: set[str],
                         already: set) -> list[dict]:
    """Statements Ripple could not read that name a table the chain reached."""
    if not visited or not parsed.opaque:
        return []
    out: list[dict] = []
    pattern = index._pattern(sorted(visited))
    for path, records in sorted(parsed.opaque.items()):
        if path in already:
            continue
        for record in records:
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
        "inferredHops": f.inferred_hops,
    }


def _risk_of(res: ScanResult) -> str:
    if not res.findings:
        return "none"
    if any(f.no_local_fix for f in res.findings):
        return "high"
    if any(f.breaking for f in res.findings):
        return "medium"
    return "low"
