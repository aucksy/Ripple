"""Answers Ripple used to give confidently over less than the whole picture.

Every case here produced a calm, clean, wrong result. Not a crash, not a "could
not read" -- a green tick on a change that breaks a published table. That is the
one failure this tool cannot have, so each shape is pinned here.

The three that started it:

* A table built with ``SELECT *`` stopped the trail dead. Forty-four tables in
  the repository this was built for are made that way.
* A trail deeper than the hop limit was reported as "the chain ends here and
  does not reach production" -- a setting reported as a fact about a warehouse.
* Two tables sharing a short name in different datasets were treated as one.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ripple.config import Settings, parse_production_rule       # noqa: E402
from ripple.scanner.lineage import trace                        # noqa: E402
from ripple.scanner.repo import RepoIndex                       # noqa: E402
from ripple.scanner.sqlread import parse_repo                   # noqa: E402


def build(tmp_path: Path, files: dict, production: str = "_published",
          max_hops: int = 4) -> tuple:
    for name, text in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    cfg = Settings()
    cfg.sql_dialect = "bigquery"
    cfg.repo_path = tmp_path
    cfg.max_hops = max_hops
    cfg.production_patterns = parse_production_rule(production)
    idx = RepoIndex.build(tmp_path, cfg)
    return cfg, idx, parse_repo(idx, cfg)


def scan(tmp_path: Path, files: dict, table: str = "customer_demographics",
         attrs: tuple[str, ...] = ("cm13",), production: str = "_published",
         change: str = "removal", max_hops: int = 4) -> dict:
    cfg, idx, parsed = build(tmp_path, files, production=production, max_hops=max_hops)
    return trace(idx, parsed, [{"table": table, "attrs": list(attrs)}],
                 change_type=change, cfg=cfg).to_dict()


# ── 1. SELECT * ────────────────────────────────────────────────────────────
STAR = {
    "a.sql": """
        CREATE OR REPLACE TABLE stage_star AS
        SELECT * FROM customer_demographics;
    """,
    "b.sql": """
        CREATE OR REPLACE TABLE final_published AS
        SELECT cm13 FROM stage_star WHERE cm13 IS NOT NULL;
    """,
}


def test_a_table_built_with_select_star_does_not_stop_the_trail(tmp_path):
    """The reproduction this was reported with. Two files, one hop apart, and a
    completely clean answer for a change that breaks a published table."""
    out = scan(tmp_path, STAR)
    assert [g["prod"] for g in out["groups"]] == ["final_published"], \
        "the change reaches final_published and always did"
    assert out["stats"]["productionTables"] == 1
    assert out["risk"] != "none"


def test_the_scan_result_itself_says_the_column_list_was_not_visible(tmp_path):
    """Not a different screen. The repository screen has listed these tables for
    months and nothing joined it up to the answer, so the scan said no impact
    while the warning sat somewhere nobody was looking."""
    out = scan(tmp_path, STAR)
    assert [s["table"] for s in out["starTables"]] == ["stage_star"]
    assert out["stats"]["tablesNotVisible"] == 1
    assert out["stats"]["inferredFindings"] == 2, "both findings are past the star"
    assert out["attributes"][0]["notVisible"] == ["stage_star"]


def test_the_star_hop_itself_is_not_called_breaking(tmp_path):
    """A SELECT * does not fail when a column disappears. It quietly builds a
    narrower table, and what breaks is whatever reads the missing column."""
    out = scan(tmp_path, STAR)
    rows = out["groups"][0]["rows"]
    star_row = next(r for r in rows if r["viaStar"])
    assert star_row["breaking"] is False
    assert "SELECT *" in star_row["impact"]
    named = next(r for r in rows if not r["viaStar"])
    assert named["breaking"] is True


def test_a_qualified_star_only_carries_its_own_table(tmp_path):
    """``SELECT a.*`` takes a's columns, not b's."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE stage_star AS
            SELECT b.* FROM customer_demographics a JOIN other_side b ON a.k = b.k;
        """,
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM stage_star;",
    })
    assert out["groups"] == [], "cm13 travels through b, and b is not being changed"


def test_select_star_except_stops_the_chain_and_still_reports_the_break(tmp_path):
    """Both halves matter. The column never reaches the next table, so the trail
    genuinely stops -- and the statement names it, so removing it breaks here."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE stage_star AS
            SELECT * EXCEPT(cm13) FROM customer_demographics;
        """,
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM stage_star;",
    })
    assert out["groups"] == [], "cm13 is dropped by name and never reaches final_published"
    rows = [r for g in out["reached"] for r in g["rows"]]
    assert rows, "but the statement that drops it by name is still broken by the change"
    assert rows[0]["breaking"] is True
    assert "EXCEPT" in rows[0]["impact"]


# ── 2. the hop limit ───────────────────────────────────────────────────────
def deep_chain(depth: int) -> dict:
    files = {"t0.sql": "CREATE OR REPLACE TABLE t1 AS SELECT cm13 FROM customer_demographics;"}
    for i in range(1, depth):
        files[f"t{i}.sql"] = f"CREATE OR REPLACE TABLE t{i + 1} AS SELECT cm13 FROM t{i};"
    files["tp.sql"] = f"CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM t{depth};"
    return files


def test_a_trail_the_limit_cut_is_not_reported_as_a_trail_that_ended(tmp_path):
    """"The chain ends at t4 and does not reach production" is a sentence about
    a setting, printed on the screen where somebody decides whether to worry."""
    out = scan(tmp_path, deep_chain(8))
    assert out["attributes"][0]["endsAt"] == [], "nothing here actually ended"
    assert out["attributes"][0]["cutShortAt"] == ["t4"]
    assert out["stats"]["trailsCutShort"] == 1
    assert [c["table"] for c in out["cutShort"]] == ["t4"]
    assert out["maxHops"] == 4


def test_the_table_the_limit_stopped_at_says_so_on_its_own_card(tmp_path):
    out = scan(tmp_path, deep_chain(8))
    card = next(g for g in out["reached"] if g["prod"] == "t4")
    assert card["cut"] is True
    assert "hop limit" in card["note"]


def test_raising_the_limit_finds_the_published_table(tmp_path):
    """The whole point of saying a trail was cut: it can be run again deeper."""
    out = scan(tmp_path, deep_chain(8), max_hops=12)
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert out["stats"]["trailsCutShort"] == 0
    assert out["cutShort"] == []


def test_a_trail_that_really_ends_is_not_called_cut_short(tmp_path):
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE t1 AS SELECT cm13 FROM customer_demographics;",
    })
    assert out["attributes"][0]["endsAt"] == ["t1"]
    assert out["attributes"][0]["cutShortAt"] == []
    assert out["stats"]["trailsCutShort"] == 0


# ── 3. two tables with the same short name ─────────────────────────────────
TWO_DATASETS = {
    "raw.sql": """
        CREATE OR REPLACE TABLE `prj.stage_dataset.from_raw` AS
        SELECT cm13 FROM `prj.raw_dataset.customer_demographics`;
    """,
    "arch.sql": """
        CREATE OR REPLACE TABLE `prj.stage_dataset.from_archive` AS
        SELECT cm13 FROM `prj.archive_dataset.customer_demographics`;
    """,
}


def test_a_change_to_one_dataset_does_not_produce_findings_for_the_other(tmp_path):
    out = scan(tmp_path, TWO_DATASETS, table="prj.raw_dataset.customer_demographics")
    files = {r["file"] for g in out["reached"] for r in g["rows"]}
    assert files == {"raw.sql"}, "arch.sql reads a different table of the same name"
    assert [g["prod"] for g in out["reached"]] == ["from_raw"]


def test_the_other_dataset_is_reported_as_a_mention_rather_than_dropped(tmp_path):
    out = scan(tmp_path, TWO_DATASETS, table="prj.raw_dataset.customer_demographics")
    assert [m["file"] for m in out["mentionsOnly"]] == ["arch.sql"]


def test_a_project_in_front_of_the_name_does_not_stop_it_matching(tmp_path):
    """Typed in full into the notification, written with a placeholder in the
    file. Ripple used to find nothing at all, which reads as no impact."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE {{tgt}}.{{stage}}.final_published AS
            SELECT cm13 FROM {{src}}.{{raw}}.customer_demographics;
        """,
    }, table="prj-p-cmdl.raw_dataset.customer_demographics")
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_a_templated_dataset_is_not_treated_as_a_dataset_name(tmp_path):
    """One file writes {{stage_dataset}}.orders_umdl, the DAG that reads it
    writes {{params.src}}.raw.orders_umdl. Those are not two datasets -- one of
    them is a hole. Splitting them cuts a real chain and reports no impact."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE {{tgt_project_id}}.{{stage_dataset}}.orders_umdl AS
            SELECT cm13 FROM customer_demographics;
        """,
        "b.sql": """
            CREATE OR REPLACE TABLE final_published AS
            SELECT cm13 FROM `prj.raw.orders_umdl`;
        """,
    })
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_a_name_ripple_had_to_merge_is_said_out_loud(tmp_path):
    """The SQL did not say which of two same-named tables it meant. Ripple
    matches both, because losing the chain is the worse mistake -- and says so
    rather than letting the finding read as a fact about one of them."""
    out = scan(tmp_path, {
        "raw.sql": "CREATE OR REPLACE TABLE mid AS SELECT cm13 FROM `prj.raw_dataset.cust`;",
        "arch.sql": "CREATE OR REPLACE TABLE other AS SELECT cm13 FROM `prj.archive_dataset.cust`;",
        "c.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM mid;",
    }, table="cust")
    merged = out["mergedNames"]
    assert [m["table"] for m in merged] == ["cust"]
    assert merged[0]["datasets"] == ["ARCHIVE_DATASET", "RAW_DATASET"]


# ── 4. the same class, found by asking the same question ───────────────────
def test_both_halves_of_a_union_are_read(tmp_path):
    """One of his tables is called ..._BCA_UNION. Only the first SELECT of a
    union was recorded as reading anything, so a change to a table named in the
    second half produced no findings anywhere at all."""
    for first, second in (("customer_demographics", "other_source"),
                          ("other_source", "customer_demographics")):
        out = scan(tmp_path / f"{first}{second}", {
            "u.sql": f"""
                CREATE OR REPLACE TABLE deduped_bca_union AS
                SELECT cm13 FROM {first}
                UNION ALL
                SELECT cm13 FROM {second};
            """,
            "p.sql": "CREATE OR REPLACE TABLE final_published AS "
                     "SELECT cm13 FROM deduped_bca_union;",
        })
        assert [g["prod"] for g in out["groups"]] == ["final_published"], \
            f"the union half naming customer_demographics was {first}/{second}"


def test_a_finding_points_at_a_line_inside_its_own_statement(tmp_path):
    """A 600-line generated file holds sixty statements. A finding used to be
    free to point at any line in the file that scored well, which regularly
    meant a WHERE clause belonging to a different table entirely -- the finding
    right, the line somebody else's, and the whole finding wasted."""
    out = scan(tmp_path, {
        "f.sql": """CREATE OR REPLACE TABLE final_published AS
SELECT a FROM customer_demographics
WHERE cm13 IS NOT NULL;

CREATE OR REPLACE TABLE unrelated_tbl AS
SELECT a FROM something_else
WHERE cm13 = 'X' AND flag = 1 OR other IS NULL;
""",
    })
    row = out["groups"][0]["rows"][0]
    hit = next(line for line in row["lines"] if line.get("hit"))
    assert hit["n"] == 3, "line 7 belongs to a statement about a different table"
    assert "IS NOT NULL" in hit["t"]


def test_an_insert_column_list_renames_by_position(tmp_path):
    """Every foundation file here loads with TRUNCATE then INSERT INTO t (the
    whole column list) SELECT ... . The SELECT hands values over by position, so
    the name downstream is the one in the INSERT list -- and following the
    SELECT's name instead walked off the end of the chain."""
    out = scan(tmp_path, {
        "a.sql": "INSERT INTO stage_tbl (member_id) SELECT cm13 FROM customer_demographics;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT member_id FROM stage_tbl;",
    })
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_a_mismatched_insert_column_list_is_not_guessed_at(tmp_path):
    """Two lists of different lengths cannot be lined up, so nothing is."""
    out = scan(tmp_path, {
        "a.sql": "INSERT INTO stage_tbl (a, b) SELECT cm13 FROM customer_demographics;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM stage_tbl;",
    })
    assert [g["prod"] for g in out["groups"]] == ["final_published"], \
        "the name it arrived under is kept rather than a position being invented"


def test_two_names_differing_only_by_capitals_are_said_out_loud(tmp_path):
    """He has ccm_Wireless_Enroll and ccm_Dell_Enroll. BigQuery treats capitals
    as significant, so two spellings really are two tables there. Ripple follows
    both -- losing a chain is worse -- and says which ones it merged."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE mid AS SELECT cm13 FROM ccm_Wireless_Enroll;",
        "b.sql": "CREATE OR REPLACE TABLE other AS SELECT cm13 FROM ccm_wireless_enroll;",
        "c.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM mid;",
    }, table="ccm_Wireless_Enroll")
    merged = [m for m in out["mergedNames"] if m["reason"] == "capitals"]
    assert merged, "both spellings were followed, and nothing said so"
    assert merged[0]["spellings"] == ["ccm_Wireless_Enroll", "ccm_wireless_enroll"]


def test_a_column_leaving_under_two_names_has_both_followed(tmp_path):
    """Following the onward names stopped at the first one that found
    something, so the second name was dropped exactly when the first name
    worked -- which is most of the time."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE stage_tbl AS
            SELECT cm13, CAST(cm13 AS STRING) AS cm13_str FROM customer_demographics;
        """,
        "b.sql": "CREATE OR REPLACE TABLE ends_here AS SELECT cm13 FROM stage_tbl;",
        "c.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13_str FROM stage_tbl;",
    })
    assert [g["prod"] for g in out["groups"]] == ["final_published"], \
        "cm13_str reaches the published table and is the second name, not the first"


def test_a_dataset_matched_against_a_bare_name_is_also_said_out_loud(tmp_path):
    """One file names archive_dataset.cust_stage, another just says cust_stage.
    Ripple matches them, because a bare name has said nothing to rule anything
    out — and that is a merge exactly as much as two named datasets are."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE `prj.archive_dataset.cust_stage` AS
            SELECT cm13 FROM customer_demographics;
        """,
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM cust_stage;",
    })
    merged = [m for m in out["mergedNames"] if m["table"] == "cust_stage"]
    assert merged, "the bare cust_stage was matched to the archive one, and nothing said so"
    assert merged[0]["reason"] == "dataset"


def test_a_repository_with_no_dataset_names_flags_nothing(tmp_path):
    """His files are templated, so almost no name carries a dataset Ripple can
    read. A warning printed over every table is one nobody reads."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE {{tgt}}.{{stage_dataset}}.mid AS
            SELECT cm13 FROM {{src}}.{{src_dataset}}.customer_demographics;
        """,
        "b.sql": """
            CREATE OR REPLACE TABLE {{tgt}}.{{tgt_dataset}}.final_published AS
            SELECT cm13 FROM {{tgt}}.{{stage_dataset}}.mid;
        """,
    })
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert out["mergedNames"] == []


def test_an_unambiguous_table_is_still_shown_by_its_own_name(tmp_path):
    """Printing "stage_dataset." in front of every table in a repository with
    one dataset is noise, and noise is what stops the line that matters."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE `prj.stage_dataset.final_published` AS
            SELECT cm13 FROM `prj.stage_dataset.customer_demographics`;
        """,
    })
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert out["mergedNames"] == []


# ── 8. clauses a column can hide in ────────────────────────────────────────
# Every case below came back "the name appears, but no lineage to a production
# table" -- the most reassuring sentence Ripple can print -- for a change that
# stops a published table loading. They are one defect wearing several hats: the
# reader had a list of the places in a statement a column can be used, and the
# list was short. Grouped here so the next clause anyone adds gets a case too.
def only_row(out: dict) -> dict:
    assert [g["prod"] for g in out["groups"]] == ["final_published"], out["groups"]
    rows = [r for g in out["groups"] for r in g["rows"]]
    assert len(rows) == 1, rows
    return rows[0]


def test_qualify_is_read_as_the_filter_it_is(tmp_path):
    """QUALIFY is where nearly every dedup in a BigQuery pipeline is written.
    Not reading it made the column invisible whenever it appeared nowhere else
    in the statement -- and the standard dedup is exactly that shape."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE final_published AS
            SELECT pub_id, last_upd FROM customer_demographics
            QUALIFY ROW_NUMBER() OVER (PARTITION BY pub_id ORDER BY last_upd) = 1
               AND cm13 = 'US';
        """,
    })
    assert only_row(out)["logic"] == "Filter"
    assert out["mentionsOnly"] == []


def test_the_partition_key_of_a_ranking_is_a_dedup_key(tmp_path):
    """PARTITION BY is the half of a dedup that was never read. The ORDER BY
    picks the winner; the PARTITION BY says what it wins against. Remove it and
    one record survives for the whole table instead of one per key."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE final_published AS
            SELECT pub_id, last_upd FROM customer_demographics
            QUALIFY ROW_NUMBER() OVER (PARTITION BY cm13 ORDER BY last_upd) = 1;
        """,
    })
    row = only_row(out)
    assert row["logic"] == "Dedup key"
    assert row["noLocalFix"], "a missing partition key cannot be fixed downstream"
    assert out["risk"] == "high"


def test_a_named_window_clause_is_read_like_an_inline_one(tmp_path):
    """WINDOW w AS (PARTITION BY cm13 ...) puts the same dedup somewhere else in
    the statement. Writing it the other way round is not a reason to miss it."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE final_published AS
            SELECT pub_id, ROW_NUMBER() OVER w AS rn
            FROM customer_demographics
            WINDOW w AS (PARTITION BY cm13 ORDER BY last_upd);
        """,
    })
    assert only_row(out)["logic"] == "Dedup key"


def test_a_merge_that_names_its_source_table_is_followed(tmp_path):
    """MERGE is how a published table is normally loaded. With USING naming a
    table directly there is no SELECT in the statement at all, so it recorded no
    sources, was never indexed as reading anything, and no scan could reach it
    however hard it looked."""
    out = scan(tmp_path, {
        "a.sql": """
            MERGE INTO final_published t
            USING customer_demographics s
            ON t.pub_id = s.pub_id AND t.cm13 = s.cm13
            WHEN MATCHED THEN UPDATE SET t.last_upd = s.last_upd;
        """,
    })
    assert only_row(out)["logic"] == "Join key"


def test_a_merge_renames_the_column_into_the_published_table(tmp_path):
    """SET t.market = s.cm13 publishes cm13 as market, and the INSERT list
    renames by position exactly as a plain INSERT does. Following the source's
    own name walked off the end of the chain at the loading statement."""
    out = scan(tmp_path, {
        "a.sql": """
            MERGE INTO mid_stage t
            USING customer_demographics s
            ON t.pub_id = s.pub_id
            WHEN MATCHED THEN UPDATE SET t.market = s.cm13
            WHEN NOT MATCHED THEN INSERT (pub_id, market) VALUES (s.pub_id, s.cm13);
        """,
        "b.sql": """
            CREATE OR REPLACE TABLE final_published AS
            SELECT market FROM mid_stage WHERE market IS NOT NULL;
        """,
    })
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    hops = {(r["from"], r["attr"], r["alias"]) for g in out["groups"] for r in g["rows"]}
    assert ("customer_demographics", "cm13", "market") in hops, hops
    assert ("mid_stage", "market", "market") in hops, hops


def test_the_condition_on_a_merge_when_is_read(tmp_path):
    """WHEN MATCHED AND s.cm13 = 'DEAD' THEN DELETE decides which rows of a
    published table are deleted, and is often the only place in the whole
    statement the column is named."""
    out = scan(tmp_path, {
        "a.sql": """
            MERGE INTO final_published t
            USING customer_demographics s
            ON t.pub_id = s.pub_id
            WHEN MATCHED AND s.cm13 = 'DEAD' THEN DELETE;
        """,
    })
    assert only_row(out)["logic"] == "Filter"


def test_an_update_reads_the_table_its_from_clause_names(tmp_path):
    """UPDATE ... FROM reads a whole second table. Only the table being written
    was ever recorded, so the source was invisible -- the same hole as MERGE,
    one statement type along."""
    out = scan(tmp_path, {
        "a.sql": """
            UPDATE final_published t SET t.market = s.cm13
            FROM customer_demographics s WHERE t.pub_id = s.pub_id;
        """,
    })
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert out["mentionsOnly"] == []


def test_a_column_opened_out_by_unnest_is_reported(tmp_path):
    """FROM t, UNNEST(cm13) has no ON clause to look at, and the column is named
    nowhere else in the statement."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE final_published AS
            SELECT pub_id, c FROM customer_demographics, UNNEST(cm13) AS c;
        """,
    })
    assert only_row(out)["logic"] == "Transform"


def test_the_statements_own_order_by_is_reported(tmp_path):
    """ORDER BY writes the name down, so removing the column stops the statement
    compiling and the table stops loading. With a LIMIT under it the column also
    decides which rows survive, which is the ranking case."""
    plain = scan(tmp_path / "plain", {
        "a.sql": """
            CREATE OR REPLACE TABLE final_published AS
            SELECT pub_id FROM customer_demographics ORDER BY cm13;
        """,
    })
    row = only_row(plain)
    assert row["logic"] == "Sort order"
    assert row["breaking"], "the statement stops compiling without the column"
    assert not row["noLocalFix"], "a sort order can be changed in this file"

    limited = scan(tmp_path / "limited", {
        "a.sql": """
            CREATE OR REPLACE TABLE final_published AS
            SELECT pub_id FROM customer_demographics ORDER BY cm13 LIMIT 100;
        """,
    })
    assert only_row(limited)["logic"] == "Ranking", "with a LIMIT it picks the survivors"


# ── 9. one file, several statements ────────────────────────────────────────
def test_each_statement_in_a_file_is_its_own_finding(tmp_path):
    """A finding used to be one per file, table, column and kind. One file very
    often builds several tables and filters on the same source column in each,
    so the second and third statements were folded into the first: the row shown
    under the published table pointed at another statement's lines, named
    another statement's target, and the count of usages was quietly short."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE stage_one AS
            SELECT pub_id FROM customer_demographics WHERE cm13 = 'A';

            CREATE OR REPLACE TABLE stage_two AS
            SELECT pub_id FROM customer_demographics WHERE cm13 = 'B';

            CREATE OR REPLACE TABLE final_published AS
            SELECT pub_id FROM customer_demographics WHERE cm13 = 'C';
        """,
    })
    assert out["attributes"][0]["found"] == 3, "three statements, three usages"
    row = only_row(out)
    assert row["inter"] == "final_published", \
        "the row under final_published must be the statement that builds it"
    assert "final_published" in row["impact"], row["impact"]


# ── 10. BigQuery wildcard tables ───────────────────────────────────────────
# Date sharding is how a great deal of BigQuery source data is stored, and the
# only way to read it is a wildcard:
#
#     SELECT cm13 FROM `prj.ds.customer_demographics_*`
#     WHERE _TABLE_SUFFIX BETWEEN '20260101' AND '20260131'
#
# Ripple recorded the source as "customer_demographics_*", asterisk and all.
# Nobody has a table called that. Scanning a real shard matched nothing, and
# scanning the family name matched nothing either -- zero findings, a clean
# "no impact", on a change that breaks a published table.
WILDCARD = {
    "a.sql": """
        CREATE OR REPLACE TABLE stage_wild AS
        SELECT cm13 FROM `prj.ds.customer_demographics_*`
        WHERE _TABLE_SUFFIX BETWEEN '20260101' AND '20260131';
    """,
    "b.sql": """
        CREATE OR REPLACE TABLE final_published AS
        SELECT cm13 FROM stage_wild WHERE cm13 IS NOT NULL;
    """,
}


def test_a_real_shard_is_found_by_the_wildcard_that_reads_it(tmp_path):
    """The reproduction. A shard name is what a person types, and it used to
    match nothing at all."""
    out = scan(tmp_path, WILDCARD, table="customer_demographics_20260101")
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert out["stats"]["productionTables"] == 1
    assert out["risk"] != "none"


def test_the_family_name_a_person_types_is_found_too(tmp_path):
    """BigQuery itself would not match "customer_demographics" against
    "customer_demographics_*" -- the trailing separator is part of the prefix.
    Ripple matches it anyway, because that is what somebody asked what breaks
    actually types, and the cost of refusing is the clean "no impact" this
    whole file exists to prevent."""
    out = scan(tmp_path, WILDCARD, table="customer_demographics")
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_the_wildcard_is_named_on_the_result_not_somewhere_else(tmp_path):
    """A caveat on a different screen from the answer it qualifies is a caveat
    nobody reads. The finding says the table was reached through a wildcard,
    and names the wildcard as the SQL spells it."""
    out = scan(tmp_path, WILDCARD, table="customer_demographics_20260101")
    wild = out["wildcardNames"]
    assert len(wild) == 1, wild
    assert wild[0]["table"] == "customer_demographics_20260101"
    assert wild[0]["patterns"] == ["customer_demographics_*"], \
        "spelt as the file spells it, not as the index keys it"


def test_a_wildcard_does_not_swallow_an_unrelated_table(tmp_path):
    """The star only stands for what comes after the prefix. A shorter name
    that happens to start the same way is a different table, and matching it
    would put a finding about somebody else's table on this result."""
    out = scan(tmp_path, WILDCARD, table="cust")
    assert out["groups"] == []
    assert out["wildcardNames"] == []


def test_nothing_is_said_when_the_wildcard_is_what_was_typed(tmp_path):
    """Somebody who typed the asterisk knows the answer covers a family. A
    warning printed on every scan is a warning nobody reads."""
    out = scan(tmp_path, WILDCARD, table="customer_demographics_*")
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert out["wildcardNames"] == []


def test_a_wildcard_in_another_dataset_is_still_a_different_table(tmp_path):
    """The dataset rules a match out exactly as it does for an ordinary name.
    A wildcard is not a licence to ignore what the SQL did say."""
    out = scan(tmp_path, {
        "a.sql": """
            CREATE OR REPLACE TABLE final_published AS
            SELECT cm13 FROM `prj.archive_ds.customer_demographics_*`;
        """,
    }, table="live_ds.customer_demographics_20260101")
    assert out["groups"] == [], "archive_ds and live_ds are two different tables"


# ── 11. a staging table promoted into a published one ──────────────────────
# The last step of a great many pipelines: build the table in a staging dataset,
# check it, then promote it by copying or renaming it into the published one.
# None of these four statements has a SELECT anywhere in it, so Ripple recorded
# no source for any of them. The trail died at the staging table and the screen
# said "last table in the chain - not matched by your production naming rule" --
# a calm, confident answer, with the published table one line further down the
# same folder never mentioned.
PROMOTE = "CREATE OR REPLACE TABLE stage_x AS SELECT cm13 FROM customer_demographics;"


def promote(tmp_path, statement: str) -> dict:
    return scan(tmp_path, {"a.sql": PROMOTE, "b.sql": statement})


@pytest.mark.parametrize("statement,word", [
    ("CREATE OR REPLACE TABLE final_published COPY stage_x;", "COPY"),
    ("CREATE TABLE final_published CLONE stage_x;", "CLONE"),
    ("CREATE TABLE final_published LIKE stage_x;", "LIKE"),
    ("CREATE SNAPSHOT TABLE final_published CLONE stage_x;", "CLONE"),
    ("ALTER TABLE stage_x RENAME TO final_published;", "RENAME"),
])
def test_a_whole_table_copy_carries_the_chain_into_production(tmp_path, statement, word):
    out = promote(tmp_path, statement)
    assert [g["prod"] for g in out["groups"]] == ["final_published"], statement
    assert out["stats"]["productionTables"] == 1


@pytest.mark.parametrize("statement,word", [
    ("CREATE OR REPLACE TABLE final_published COPY stage_x;", "COPY"),
    ("CREATE TABLE final_published CLONE stage_x;", "CLONE"),
    ("ALTER TABLE stage_x RENAME TO final_published;", "RENAME"),
])
def test_a_copied_table_is_marked_worked_out_and_named_by_its_own_word(
        tmp_path, statement, word):
    """A copy carries every column and writes none of them down, which is what
    SELECT * does -- so it is followed the same way and every step past it is
    marked worked out rather than read. What it must NOT do is tell the reader
    the file says SELECT *, because the file says COPY."""
    out = promote(tmp_path, statement)
    assert out["stats"]["inferredFindings"] >= 1, "the hop is worked out, not read"
    assert out["stats"]["tablesNotVisible"] == 1
    star = out["starTables"][0]
    assert star["table"] == "final_published"
    assert star["from"] == "stage_x"
    assert star["how"] == word, "the card names the word the file actually uses"


def test_an_ordinary_select_star_is_still_not_labelled_a_copy(tmp_path):
    """The guard on the other side: a real SELECT * must not start claiming to
    be a COPY, or the card lies in the opposite direction."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE stage_x AS SELECT * FROM customer_demographics;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM stage_x;"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert out["starTables"][0]["how"] == "", "an ordinary star has no copy word"


def test_a_copy_of_an_unrelated_table_is_not_dragged_in(tmp_path):
    """A promote step only carries the chain when it copies a table the chain
    actually reached."""
    out = scan(tmp_path, {
        "a.sql": PROMOTE,
        "b.sql": "CREATE OR REPLACE TABLE final_published COPY some_other_table;"})
    assert out["groups"] == [], "final_published is a copy of a table with no cm13 in it"
