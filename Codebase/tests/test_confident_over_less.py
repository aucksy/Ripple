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
        # Bytes, not text, when the test is about how the file was SAVED -- a
        # byte-order mark, UTF-16, a stray NUL. Writing those through write_text
        # would put the very bytes under test back through an encoder.
        if isinstance(text, bytes):
            p.write_bytes(text)
        else:
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


# ── 12. table-valued functions ─────────────────────────────────────────────
# A BigQuery TABLE FUNCTION is a table as far as lineage is concerned: it is
# named, it is read in a FROM clause, and every column of its body travels
# through it. Both halves used to be invisible. The definition parses as a
# function rather than a table, so it published nothing; and the call parses as
# a function call whose table node carries no name at all, so it read nothing.
# The chain broke in the middle and the published table was never mentioned.
def tvf(tmp_path, define: str, call: str) -> dict:
    return scan(tmp_path, {"a.sql": define, "b.sql": call})


@pytest.mark.parametrize("define,call", [
    ("CREATE OR REPLACE TABLE FUNCTION mid_tvf(d STRING) AS"
     " (SELECT cm13 FROM customer_demographics WHERE dt = d);",
     "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM mid_tvf('x');"),
    ("CREATE OR REPLACE TABLE FUNCTION ds.mid_tvf(d STRING) AS"
     " (SELECT cm13 FROM customer_demographics);",
     "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM ds.mid_tvf('x');"),
    ("CREATE OR REPLACE TABLE FUNCTION `prj.ds.mid_tvf`(d STRING) AS"
     " (SELECT cm13 FROM customer_demographics);",
     "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM `prj.ds.mid_tvf`('x');"),
])
def test_a_table_function_carries_the_chain(tmp_path, define, call):
    out = tvf(tmp_path, define, call)
    assert [g["prod"] for g in out["groups"]] == ["final_published"], define


def test_a_scalar_udf_is_not_treated_as_a_table(tmp_path):
    """A scalar UDF parses as the same node, with the same kind. Only its body
    tells them apart: a table function returns a SELECT, a scalar one returns an
    expression. Get that wrong and every helper in the repository becomes a
    table nobody has."""
    out = scan(tmp_path, {"a.sql":
        "CREATE TEMP FUNCTION scrub(x STRING) AS (UPPER(x));\n"
        "CREATE OR REPLACE TABLE final_published AS"
        " SELECT scrub(cm13) AS cm13 FROM customer_demographics;"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    rows = [r for g in out["groups"] for r in g["rows"]]
    assert not any("scrub" in (r["inter"] or "").lower() for r in rows), \
        "scrub is a function, not a table on the trail"


def test_a_builtin_wrapper_is_not_invented_as_a_table(tmp_path):
    """BigQuery's own table functions wrap a table rather than being one, and
    the table they wrap is parsed separately and found anyway. Taking the
    wrapper's name too would put a table nobody has on the result."""
    out = scan(tmp_path, {"a.sql":
        "CREATE OR REPLACE TABLE final_published AS "
        "SELECT cm13 FROM customer_demographics UNION ALL "
        "SELECT cm13 FROM EXTERNAL_QUERY('conn', 'SELECT cm13 FROM x');"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    names = [r["inter"] for g in out["groups"] for r in g["rows"]]
    assert not any("external_query" in (n or "").lower() for n in names), names


def test_unnest_is_still_not_a_table(tmp_path):
    """The guard on the change above: UNNEST sits in a FROM clause and looks
    like a function call, and turning it into a table would put one on every
    result in the repository."""
    out = scan(tmp_path, {"a.sql":
        "CREATE OR REPLACE TABLE final_published AS"
        " SELECT cm13, t FROM customer_demographics, UNNEST(tags) AS t;"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    names = [r["inter"] for g in out["groups"] for r in g["rows"]]
    assert not any("unnest" in (n or "").lower() for n in names), names


# ── 13. a source is not the target just because the names look alike ───────
# Sources are gathered by walking every table in a statement, which finds the
# write target too, so the target has to be left out. That was done by
# comparing NAMES with same_table -- and same_table is deliberately loose,
# because a name with no dataset must go on matching one that has a dataset or
# every templated chain in this repository breaks.
#
# Loose is right for FOLLOWING a chain and catastrophic for EXCLUDING a source.
# Both shapes below threw away the only source the statement had, so the
# statement was indexed as reading nothing and the scan came back clean.
def test_a_wildcard_covering_its_own_target_does_not_erase_the_source(tmp_path):
    """events_* covers events_rollup, because a wildcard is a prefix match and
    that really is what BigQuery does. It is still the source, not the target."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE `p.ds.events_rollup` AS "
                 "SELECT cm13 FROM `p.ds.events_*`;",
        "b.sql": "CREATE OR REPLACE TABLE `p.pub.exec_published` AS "
                 "SELECT cm13 FROM `p.ds.events_rollup`;",
    }, table="events_20260101")
    assert [g["prod"] for g in out["groups"]] == ["exec_published"]


def test_a_templated_target_dataset_does_not_erase_the_source(tmp_path):
    """The dataset on the target is a placeholder, so it is dropped -- leaving a
    bare "orders" that matched "stage.orders" and took the source with it."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE {{ target_dataset }}.orders AS "
                 "SELECT id, cm13 AS promo FROM stage.orders;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT promo FROM orders;",
    }, table="stage.orders")
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_a_table_rebuilt_from_itself_is_still_read(tmp_path):
    """INSERT INTO t SELECT ... FROM t reads t. Excluding the target by name
    threw that away, and the statement was filed under "the name appears, but
    no lineage to a production table" -- the opposite of the truth."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE final_published AS "
                 "SELECT cm13 FROM customer_demographics;\n"
                 "INSERT INTO final_published (cm13) "
                 "SELECT UPPER(cm13) FROM final_published;",
    })
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert len([r for g in out["groups"] for r in g["rows"]]) >= 2, \
        "both the build and the self-referencing insert are usages"


def test_a_wildcard_with_nothing_in_front_of_it_does_not_match_everything(tmp_path):
    """A bare * matches every table there is. Following that would put the whole
    warehouse on every chain -- not a spare row somebody can dismiss."""
    from ripple.scanner.sqlread import same_table, wildcard_covers
    assert wildcard_covers("*", "anything_at_all") is False
    assert same_table("*", "customer_demographics") is False
    # Scoped by a dataset it is meaningful again, and only inside that dataset.
    assert same_table("ds.*", "ds.customer_demographics") is True
    assert same_table("ds.*", "other_ds.customer_demographics") is False
    assert same_table("ds.*", "customer_demographics") is False, \
        "an unqualified name does not say it is in that dataset"


# ── 14. shapes the SQL parser refuses ──────────────────────────────────────
# sqlglot fails these two ways, and both are quiet: a hard parse error, which
# loses the statement AND its neighbours; or a fall back to a node holding raw
# text and no tables, which is invisible unless it is the only statement in its
# file. Either way the answer is a clean "no impact". Each shape below was
# measured against the installed parser, and each appears in ordinary BigQuery.
@pytest.mark.parametrize("what,files", [
    ("APPENDS(TABLE t) - the incremental read", {
        "a.sql": "CREATE OR REPLACE TABLE stage1 AS "
                 "SELECT cm13 FROM APPENDS(TABLE `prj.ds.customer_demographics`, NULL);",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM stage1;"}),
    ("a TVF handed a table", {
        "a.sql": "CREATE OR REPLACE TABLE final_published AS "
                 "SELECT cm13 FROM `prj.ds.pick`(TABLE `prj.ds.customer_demographics`, 'x');"}),
    ("ML.PREDICT(MODEL m, TABLE t)", {
        "a.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM "
                 "ML.PREDICT(MODEL `prj.ds.m1`, TABLE `prj.ds.customer_demographics`);"}),
    ("EXTERNAL TABLE with a BigLake connection", {
        "a.sql": "CREATE OR REPLACE EXTERNAL TABLE customer_demographics (cm13 STRING)\n"
                 " WITH CONNECTION `prj.us.myconn`\n"
                 " WITH PARTITION COLUMNS (dt DATE)\n"
                 " OPTIONS (format='PARQUET', uris=['gs://b/*']);",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS "
                 "SELECT cm13 FROM customer_demographics;"}),
    ("LOAD DATA INTO declares the columns", {
        "a.sql": "LOAD DATA INTO customer_demographics (cm13 STRING, region STRING)\n"
                 " FROM FILES (format='CSV', uris=['gs://b/x.csv']);",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS "
                 "SELECT cm13 FROM customer_demographics;"}),
    ("CLONE ... FOR SYSTEM_TIME AS OF - the restore", {
        "a.sql": "CREATE OR REPLACE TABLE stage1 AS SELECT cm13 FROM customer_demographics;",
        "b.sql": "CREATE TABLE final_published CLONE stage1 "
                 "FOR SYSTEM_TIME AS OF TIMESTAMP('2026-01-01');"}),
    ("MATERIALIZED VIEW AS REPLICA OF", {
        "a.sql": "CREATE OR REPLACE TABLE stage1 AS SELECT cm13 FROM customer_demographics;",
        "b.sql": "CREATE MATERIALIZED VIEW final_published AS REPLICA OF stage1;"}),
])
def test_a_shape_the_parser_refuses_is_still_followed(tmp_path, what, files):
    out = scan(tmp_path, files)
    assert [g["prod"] for g in out["groups"]] == ["final_published"], what


def test_an_export_is_a_real_read_not_an_unreadable_file(tmp_path):
    """EXPORT DATA delivers to somebody outside the warehouse. It builds no
    table, so there is nothing to carry the column on to -- but it IS a read,
    and it used to be filed as a file that could not be read."""
    out = scan(tmp_path, {
        "a.sql": "EXPORT DATA OPTIONS(uri='gs://b/out/*.csv', format='CSV') AS\n"
                 " SELECT cm13 FROM customer_demographics;"})
    assert out["stats"]["couldNotRead"] == 0, "it can be read now"
    assert out["other"], "and the usage is reported, under no production table"


def test_a_partition_decorator_is_the_same_table(tmp_path):
    """customer_demographics$20260101 is ONE DAY of one table, not another
    table. Kept as part of the name it split every decorated read off from the
    table it belongs to, and the scan came back clean."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE stage1 AS "
                 "SELECT cm13 FROM `prj.ds.customer_demographics$20260101`;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM stage1;"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_the_rescue_pass_never_moves_a_line():
    """Everything above is done to a copy on the way into the parser. A finding
    that points at the wrong line is worse than no finding, because the person
    goes and looks and finds nothing there."""
    from ripple.scanner import rescue
    for text in [
        "CREATE MATERIALIZED VIEW m\n  AS REPLICA OF\n  src",
        "EXPORT DATA OPTIONS(\n  uri='gs://b/*.csv',\n  format='CSV')\nAS SELECT cm13 FROM cust",
        "CREATE EXTERNAL TABLE t (a STRING)\n WITH CONNECTION `p.us.c`\n"
        " WITH PARTITION COLUMNS (dt DATE)\n OPTIONS (format='PARQUET');",
        "LOAD DATA INTO t (a STRING)\n FROM FILES (format='CSV', uris=['gs://b/x.csv']);",
        "SELECT cm13\n FROM APPENDS(TABLE `p.d.cust`,\n NULL)",
    ]:
        assert rescue.rewrite(text).count("\n") == text.count("\n"), text[:40]


def test_ordinary_sql_goes_through_the_rescue_pass_untouched():
    from ripple.scanner import rescue
    for text in ["SELECT a, b FROM t WHERE x = 1",
                 "CREATE OR REPLACE TABLE x AS SELECT * FROM y",
                 "MERGE INTO t USING s ON t.k = s.k WHEN MATCHED THEN UPDATE SET a = s.a"]:
        assert rescue.rewrite(text) == text, text


# ── 15. a column list written on the CREATE line ───────────────────────────
def test_a_view_with_its_own_column_list_renames_the_column(tmp_path):
    """BigQuery lets a view pin its output names in the CREATE line, and it is
    the ordinary way a team publishes friendly names over warehouse codes. The
    list was thrown away, so the chain stopped at the view."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE VIEW v1(a, b) AS "
                 "SELECT cm13, region FROM customer_demographics;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT a FROM v1;"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_a_ctas_with_a_column_list_renames_the_column(tmp_path):
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE s1(a STRING, b STRING) AS "
                 "SELECT cm13, region FROM customer_demographics;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT a FROM s1;"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_a_column_list_of_the_wrong_length_is_not_guessed_at(tmp_path):
    """Where the two lists cannot be lined up, the name is left alone rather
    than mapped to whatever happens to be in that position."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE VIEW v1(a) AS "
                 "SELECT cm13, region FROM customer_demographics;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM v1;"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"], \
        "the old name is kept, so the chain is followed rather than dropped"


# ── 16. an unreadable statement that names a table on the trail ────────────
def test_a_statement_ripple_cannot_read_that_names_a_trail_table_is_reported(tmp_path):
    """The quietest hole left: the file parses, the readable statements produce
    findings, and the one statement that carries the chain onwards is simply
    absent. The result reads as complete because nothing says otherwise."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE staging AS SELECT cm13 FROM customer_demographics;\n"
                 "CALL ds.load_published(staging);"})
    assert out["stats"]["couldNotRead"] == 1
    assert "staging" in out["unreadable"][0]["reason"]


def test_an_unreadable_statement_about_something_else_is_not_reported(tmp_path):
    """Every real pipeline is full of DECLAREs and CALLs that carry no lineage.
    Reporting those would bury the list this is meant to protect."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE staging AS SELECT cm13 FROM customer_demographics;\n"
                 "CALL ds.publish_from_elsewhere();"})
    assert out["stats"]["couldNotRead"] == 0


# ── 17. a table that stops being refreshed ─────────────────────────────────
# A column used only in a WHERE, a JOIN or a GROUP BY never reaches the table
# the statement builds, so the trail for that COLUMN really does end there --
# and Ripple said so, and stopped. But the statement stops working on the day
# the column goes, so the table it builds stops being rebuilt, and everything
# under it is served from data nobody is updating any more. That is an outage
# that arrives quietly, days later, and it was invisible.
FILTER_ONLY = {
    "a.sql": "CREATE OR REPLACE TABLE stage_f AS "
             "SELECT id, amount FROM customer_demographics WHERE cm13 = 'US';",
    "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT id, amount FROM stage_f;",
}


def test_a_published_table_below_a_broken_statement_is_named(tmp_path):
    out = scan(tmp_path, FILTER_ONLY)
    assert [g["prod"] for g in out["groups"]] == [], \
        "cm13 genuinely does not reach final_published as a column"
    stops = out["stopsLoading"]
    assert [r["prod"] for r in stops] == ["final_published"]
    assert stops[0]["because"] == "stage_f"
    assert stops[0]["via"] == ["stage_f", "final_published"]
    assert out["stats"]["productionStopsLoading"] == 1


def test_it_is_counted_apart_from_the_tables_whose_columns_change(tmp_path):
    """Two different kinds of impact. One number covering both is a number that
    means neither, so the headline count must not absorb it."""
    out = scan(tmp_path, FILTER_ONLY)
    assert out["stats"]["productionTables"] == 0
    assert out["stats"]["productionStopsLoading"] == 1


def test_it_is_followed_more_than_one_hop_down(tmp_path):
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE stage_f AS "
                 "SELECT id FROM customer_demographics WHERE cm13 = 'US';",
        "b.sql": "CREATE OR REPLACE TABLE mid_t AS SELECT id FROM stage_f;",
        "c.sql": "CREATE OR REPLACE TABLE final_published AS SELECT id FROM mid_t;"})
    stops = out["stopsLoading"]
    assert [r["prod"] for r in stops] == ["final_published"]
    assert stops[0]["via"] == ["stage_f", "mid_t", "final_published"]


def test_a_table_already_reported_above_is_not_reported_twice(tmp_path):
    """When the column really does travel, the table is in the findings. Saying
    it again under a different heading reads as two problems."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE stage_s AS SELECT cm13 FROM customer_demographics;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM stage_s;"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert out["stopsLoading"] == []


def test_nothing_breaking_means_nothing_stops(tmp_path):
    """A value change does not stop a statement running, so nothing downstream
    stops loading. This list must not fire on every scan."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE stage_f AS SELECT id FROM customer_demographics;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT id FROM stage_f;"},
        change="value_change")
    assert out["stopsLoading"] == []


# ── 18. a whole row carried as one value ───────────────────────────────────
# BigQuery lets a query carry an entire row around as a single value, and the
# standard dbt-utils deduplicate macro is written exactly that way. Ripple's
# whole honesty guarantee rests on admitting when a table's column list is not
# written down -- and that admission fired for SELECT * and for alias.* over a
# real table, but not for this. A deduplicated staging table, an ordinary thing
# in a dbt repository, gave a clean "no impact" with no warning at all.
DEDUP = {
    "a.sql": "CREATE OR REPLACE TABLE stage_dedup AS\n"
             "SELECT unique_row.* FROM (\n"
             "  SELECT ARRAY_AGG(original ORDER BY original.loaded_at DESC LIMIT 1)[OFFSET(0)]"
             " AS unique_row\n"
             "  FROM customer_demographics original\n"
             "  GROUP BY original.id);",
    "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM stage_dedup;",
}


def test_the_dbt_deduplicate_macro_does_not_stop_the_trail(tmp_path):
    out = scan(tmp_path, DEDUP)
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_a_whole_row_star_admits_the_column_list_is_not_visible(tmp_path):
    """It carries every column and names none of them, which is exactly what a
    SELECT * does -- so it has to be marked the same way, or the finding on the
    far side reads as read rather than worked out."""
    out = scan(tmp_path, DEDUP)
    assert [t["table"] for t in out["starTables"]] == ["stage_dedup"]
    assert out["stats"]["inferredFindings"] >= 1


def test_a_qualified_star_over_a_real_table_still_only_carries_that_table(tmp_path):
    """The guard on the change above, restated: b.* is b's columns, not a's."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE stage_star AS "
                 "SELECT b.* FROM customer_demographics a JOIN other_side b ON a.k = b.k;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM stage_star;"})
    assert out["groups"] == []


def test_a_struct_of_named_columns_is_not_a_whole_row(tmp_path):
    """STRUCT(other_col AS z) names its columns. Treating it as a whole row
    would put every column of the table on the chain, including ones the
    statement plainly never touched."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE s1 AS SELECT p.* FROM "
                 "(SELECT STRUCT(other_col AS z) AS p FROM customer_demographics);",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM s1;"})
    assert out["groups"] == []


# ── a query with no CREATE in front of it ──────────────────────────────────
# A dbt model is a bare SELECT. Nothing in the file names the table it builds --
# dbt does, after the file. Before this, a dbt repository produced ZERO lineage:
# every chain came back empty, no production table was ever named, and the answer
# was the calmest, cleanest "no impact" this tool can print. dbt is the commonest
# way a BigQuery pipeline is written.
DBT = {
    "models/staging/stg_customers.sql":
        "SELECT cust_id, cm13 FROM {{ source('raw', 'customer_demographics') }}",
    "models/intermediate/int_customers.sql":
        "SELECT cust_id, cm13 FROM {{ ref('stg_customers') }}",
    "models/marts/customer_published.sql":
        "{{ config(materialized='table') }}\n"
        "SELECT cust_id, cm13, COUNT(*) AS n FROM {{ ref('int_customers') }}\n"
        "GROUP BY cust_id, cm13",
}


def test_a_dbt_repository_reaches_its_published_table(tmp_path):
    """The reproduction. Three models, one chain, and a published table at the
    end of it -- which used to come back as no production table at all."""
    out = scan(tmp_path, DBT)
    assert [g["prod"] for g in out["groups"]] == ["customer_published"]
    assert out["stats"]["productionTables"] == 1


def test_a_dbt_config_header_does_not_make_the_file_unreadable(tmp_path):
    """``{{ config(materialized='table') }}`` is an instruction to dbt, not a
    value. Turned into a bare identifier it put a word where SQL expects a
    keyword, so the WHOLE FILE stopped parsing -- measured at 100% unreadable in
    every spelling tried. Every dbt model in the world opens with one."""
    out = scan(tmp_path, DBT)
    assert out["stats"]["couldNotRead"] == 0, out["unreadable"]


def test_the_dbt_chain_says_the_table_name_came_from_the_file(tmp_path):
    """Nobody sent to that line will find the table name written on it. A
    finding somebody cannot verify is one they dismiss."""
    out = scan(tmp_path, DBT)
    named = {t["table"]: t for t in out["namedByFile"]}
    assert "customer_published" in named
    assert named["customer_published"]["how"] == "dbt"
    assert named["customer_published"]["file"] == "models/marts/customer_published.sql"


def test_one_query_in_a_plain_sql_file_is_still_followed(tmp_path):
    """No models/ folder and no dbt call, so this is the weaker evidence -- but
    something runs the file and puts the rows somewhere, and every tool that
    works this way names it after the file. Labelled for what it is."""
    out = scan(tmp_path, {
        "jobs/mid.sql": "SELECT cust_id, cm13 FROM customer_demographics",
        "jobs/final_published.sql": "SELECT cust_id, cm13 FROM mid"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert {t["how"] for t in out["namedByFile"]} == {"file"}


def test_a_file_holding_two_queries_is_not_named_after_itself(tmp_path):
    """Two bare SELECTs cannot both be the table the file is named after, and
    guessing which would merge two unrelated queries into one table."""
    out = scan(tmp_path, {
        "jobs/mid.sql": "SELECT cm13 FROM customer_demographics;\n"
                        "SELECT other_col FROM customer_demographics;",
        "jobs/final_published.sql": "SELECT cm13 FROM mid"})
    assert out["groups"] == []
    assert "mid" not in {t["table"] for t in out["namedByFile"]}


def test_export_data_is_not_a_table_named_after_its_file(tmp_path):
    """EXPORT DATA is rewritten to a bare SELECT on the way into the parser, so
    by the time the tree exists it is indistinguishable from a dbt model. It
    delivers a file to somebody outside the warehouse and builds no table;
    naming its destination after the .sql file would be a table nobody has."""
    out = scan(tmp_path, {
        "a.sql": "EXPORT DATA OPTIONS(uri='gs://b/out/*.csv', format='CSV') AS\n"
                 " SELECT cm13 FROM customer_demographics;"})
    assert out["groups"] == []
    assert out["namedByFile"] == []
    assert out["other"], "the read itself is still reported"


# ── a temporary table belongs to one file ──────────────────────────────────
# A TEMP table is gone when its script finishes, so two files that both build a
# ``t`` are not sharing a table -- and a static scan can never know two files
# ran in one session. Temp names in real repositories are t, tmp, stg, base,
# deduped, so collisions are the norm. Before this, the second file's published
# table was reported as broken by a change nothing in it had touched, and
# mergedNames was EMPTY: no warning of any kind.
TEMP_COLLISION = {
    "a.sql": "CREATE TEMP TABLE t AS SELECT cm13 AS mkt FROM `p.d.customer_demographics`;\n"
             "CREATE OR REPLACE TABLE `p.d.report_a_published` AS SELECT mkt FROM t;",
    "b.sql": "CREATE TEMP TABLE t AS SELECT mkt FROM `p.d.unrelated`;\n"
             "CREATE OR REPLACE TABLE `p.d.report_b_published` AS SELECT mkt FROM t;",
}


def test_two_files_with_the_same_temp_table_name_are_not_one_chain(tmp_path):
    out = scan(tmp_path, TEMP_COLLISION)
    assert [g["prod"] for g in out["groups"]] == ["report_a_published"]


def test_the_unrelated_table_is_named_nowhere_on_the_result(tmp_path):
    """The same merge, one screen further along. "Stops being refreshed" walks
    onwards from a finding, and it walked from the name shown on SCREEN -- which
    for a temporary table is the short one that matches every other file's. So
    fencing the chain off moved the false claim rather than removing it: the
    unrelated published table left the findings and reappeared under "stops
    being refreshed", worded as certainly as before."""
    out = scan(tmp_path, TEMP_COLLISION)
    everywhere = repr(out)
    assert "report_b_published" not in everywhere, out["stopsLoading"]


def test_a_session_table_is_scoped_the_same_way(tmp_path):
    """BigQuery's other spelling for the same thing."""
    out = scan(tmp_path, {
        "a.sql": "CREATE TABLE _SESSION.stg AS SELECT cm13 AS mkt FROM `p.d.customer_demographics`;\n"
                 "CREATE OR REPLACE TABLE `p.d.report_a_published` AS SELECT mkt FROM _SESSION.stg;",
        "b.sql": "CREATE TABLE _SESSION.stg AS SELECT mkt FROM `p.d.unrelated`;\n"
                 "CREATE OR REPLACE TABLE `p.d.report_b_published` AS SELECT mkt FROM _SESSION.stg;"})
    assert [g["prod"] for g in out["groups"]] == ["report_a_published"]


def test_a_temp_table_still_carries_the_chain_inside_its_own_file(tmp_path):
    """The guard on the change above. Fencing them off must not cut the chain
    that runs through one, which is what a temp table is for."""
    out = scan(tmp_path, {
        "a.sql": "CREATE TEMP TABLE t AS SELECT cm13 AS mkt FROM `p.d.customer_demographics`;\n"
                 "CREATE OR REPLACE TABLE `p.d.report_a_published` AS SELECT mkt FROM t;"})
    assert [g["prod"] for g in out["groups"]] == ["report_a_published"]


def test_the_fence_is_not_shown_as_part_of_the_table_name(tmp_path):
    """The scope is Ripple's own, not something anybody wrote. A name on screen
    that is in no file sends somebody looking for a table that does not exist."""
    out = scan(tmp_path, TEMP_COLLISION)
    names = [r["inter"] for g in out["groups"] for r in g["rows"]]
    assert "t" in names, names
    assert not any("#" in (n or "") for n in names), names


def test_a_real_table_sharing_a_name_with_a_temp_one_is_left_alone(tmp_path):
    """``ds.t`` is a real table that happens to be called t. Fencing it off with
    the temporary one would cut a genuine chain."""
    out = scan(tmp_path, {
        "a.sql": "CREATE TEMP TABLE t AS SELECT other_col FROM `p.d.unrelated`;",
        "b.sql": "CREATE OR REPLACE TABLE `p.d.t` AS SELECT cm13 FROM `p.d.customer_demographics`;",
        "c.sql": "CREATE OR REPLACE TABLE `p.d.real_published` AS SELECT cm13 FROM `p.d.t`;"})
    assert [g["prod"] for g in out["groups"]] == ["real_published"]


# ── the warehouse describing itself ────────────────────────────────────────
# INFORMATION_SCHEMA views are called COLUMNS, TABLES, JOBS, VIEWS -- ordinary
# words, and a warehouse of any size has real tables called some of them. Before
# this, the metadata view and the real table were treated as one, a published
# table was reported as fed by a table it never reads, and the warning printed
# beside it blamed CAPITALISATION -- so the one thing on screen pointing at the
# problem named the wrong cause.
METADATA = {
    "a.sql": "CREATE TABLE `p.base.columns` (table_name STRING, column_name STRING);",
    "b.sql": "CREATE OR REPLACE TABLE `p.pub.report_published` AS "
             "SELECT column_name FROM `p.base`.INFORMATION_SCHEMA.COLUMNS;",
}


def test_a_real_table_is_not_merged_with_the_metadata_view_of_that_name(tmp_path):
    out = scan(tmp_path, METADATA, table="columns", attrs=("column_name",))
    assert out["groups"] == []
    assert out["risk"] == "none"


def test_no_warning_blames_capitals_for_a_metadata_read(tmp_path):
    """A warning naming the wrong cause is worse than none: following it does
    not lead anywhere near what actually happened."""
    out = scan(tmp_path, METADATA, table="columns", attrs=("column_name",))
    assert out["mergedNames"] == []


def test_the_region_wide_job_history_is_not_a_table_either(tmp_path):
    """``region-us`` is a whole region's job log addressed as if it were a
    project. Nothing in it is anybody's data -- and ``jobs`` is a name plenty of
    warehouses have a real table under."""
    out = scan(tmp_path, {
        "a.sql": "CREATE TABLE `p.base.jobs` (job_id STRING, cm13 STRING);",
        "b.sql": "CREATE OR REPLACE TABLE `p.pub.usage_published` AS "
                 "SELECT job_id FROM `region-us`.INFORMATION_SCHEMA.JOBS;"},
        table="jobs", attrs=("job_id",))
    assert out["groups"] == []
    assert out["mergedNames"] == []


def test_a_real_table_called_columns_still_carries_its_own_chain(tmp_path):
    """The guard on the change above. Only the metadata view is dropped."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE `p.pub.report_published` AS "
                 "SELECT column_name FROM `p.base.columns`;"},
        table="columns", attrs=("column_name",))
    assert [g["prod"] for g in out["groups"]] == ["report_published"]


# ── PIVOT and UNPIVOT ──────────────────────────────────────────────────────
# Both fold a column away and build differently-named ones out of it, and both
# NAME the column while doing it. Neither was read, and each failed in its own
# direction.
UNPIVOTED = {
    "a.sql": "CREATE OR REPLACE TABLE s1 AS SELECT * FROM customer_demographics\n"
             "UNPIVOT (val FOR metric IN (cm13, other_col));",
    "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT val, metric FROM s1;",
}
PIVOTED = {
    "a.sql": "CREATE OR REPLACE TABLE s1 AS "
             "SELECT * FROM (SELECT k, quarter, cm13 FROM customer_demographics)\n"
             "PIVOT (SUM(cm13) AS total FOR quarter IN ('Q1', 'Q2'));",
    "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT k, total_Q1 FROM s1;",
}


def test_an_unpivot_that_names_the_column_is_breaking(tmp_path):
    """The only case in this suite that hedged DOWNWARDS on a statement that
    hard-fails. It read as a plain SELECT *, so the answer was risk low,
    breaking false, and the sentence "Nothing here fails on the day of the
    change" -- about a statement whose UNPIVOT list stops being valid SQL."""
    out = scan(tmp_path, UNPIVOTED)
    rows = [r for g in out["groups"] for r in g["rows"]] + \
           [r for e in out["reached"] for r in e["rows"]]
    named = [r for r in rows if r["file"] == "a.sql"]
    assert named, rows
    assert named[0]["breaking"] is True
    assert "Nothing here fails" not in named[0]["impact"]


def test_an_unpivot_carries_the_column_on_under_its_new_name(tmp_path):
    """The values land in ``val`` and the column's own NAME lands in ``metric``.
    Following neither ended the trail before the published table."""
    out = scan(tmp_path, UNPIVOTED)
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_an_unpivot_row_says_unpivot_and_not_pivot(tmp_path):
    """They are opposite operations and the file says which. A row labelled
    PIVOT beside a line reading UNPIVOT describes a statement that is not
    there, and the reader doubts the finding rather than the label."""
    out = scan(tmp_path, UNPIVOTED)
    rows = [r for g in out["groups"] for r in g["rows"] if r["file"] == "a.sql"]
    assert rows[0]["logic"] == "Named in UNPIVOT", rows[0]["logic"]


def test_a_pivot_output_column_is_derived_so_the_trail_carries_on(tmp_path):
    """PIVOT builds total_Q1 and total_Q2 from the aggregate's alias and each IN
    value. Nothing derived them, so the trail was declared finished one hop
    early -- with the note "Last table in the chain" -- and the published table
    reading total_Q1 was never named."""
    out = scan(tmp_path, PIVOTED)
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    rows = [r for g in out["groups"] for r in g["rows"] if r["file"] == "a.sql"]
    assert rows[0]["alias"] == "total_Q1", rows[0]["alias"]
    assert rows[0]["breaking"] is True


def test_an_unpivoted_column_is_not_also_reported_as_carried_by_a_star(tmp_path):
    """The star over an UNPIVOT does not carry the folded column: it no longer
    exists as a column. Letting both speak puts "carried through untouched"
    beside "named here, and this statement fails without it"."""
    out = scan(tmp_path, UNPIVOTED)
    assert out["starTables"] == []
    assert out["stats"]["inferredFindings"] == 0


def test_a_column_the_pivot_never_names_is_still_carried_by_the_star(tmp_path):
    """The guard on the change above. UNPIVOT folds the columns in its IN list
    and leaves every other column of the table alone."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE s1 AS SELECT * FROM customer_demographics\n"
                 "UNPIVOT (val FOR metric IN (other_col, third_col));",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM s1;"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert [t["table"] for t in out["starTables"]] == ["s1"]


# ── how the file was saved ─────────────────────────────────────────────────
# A byte-order mark is invisible in every editor and lethal to a SQL parser. It
# lands on the FIRST statement of the file, which in a pipeline file is the one
# that names the source table -- so the statement that matters is the one that
# is lost, and the file still reports as read. Windows writes these by default:
# Notepad, PowerShell's Out-File, Excel's CSV export, every Office "save as".
BOM = b"\xef\xbb\xbf"
FIRST = "CREATE OR REPLACE TABLE stage1 AS SELECT cm13 FROM customer_demographics;"
SECOND = "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM stage1;"


def test_a_byte_order_mark_does_not_eat_the_first_statement(tmp_path):
    out = scan(tmp_path, {"a.sql": BOM + FIRST.encode("utf-8"), "b.sql": SECOND})
    assert out["stats"]["couldNotRead"] == 0, out["unreadable"]
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_a_utf_16_file_is_read_rather_than_half_read(tmp_path):
    """PowerShell's ``>`` has written UTF-16-LE by default for twenty years.
    Read as UTF-8 the file comes back with a NUL between every letter."""
    out = scan(tmp_path, {"a.sql": FIRST.encode("utf-16"), "b.sql": SECOND})
    assert out["stats"]["couldNotRead"] == 0, out["unreadable"]
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_a_file_full_of_nul_bytes_is_said_out_loud(tmp_path):
    """The worst of the three. The parser swallowed the statement and said
    nothing: couldNotRead 0, no warning anywhere, risk none."""
    out = scan(tmp_path, {"a.sql": FIRST.encode("utf-8") + b"\x00\x00rubbish\x00"})
    assert out["stats"]["couldNotRead"] == 1, out["unreadable"]
    assert "NUL" in out["unreadable"][0]["reason"]


# ── "No impact" is the one word that must never cover a gap ────────────────
def test_risk_is_never_none_while_a_file_on_the_subject_could_not_be_read(tmp_path):
    """EXECUTE IMMEDIATE holds a whole CREATE ... SELECT of the scanned column
    as text. Ripple can SEE it and cannot parse it -- and printed a green
    "No impact" over it. "I found nothing" and "I could not look" are not the
    same answer, however similar they look on screen."""
    out = scan(tmp_path, {
        "a.sql": "EXECUTE IMMEDIATE '''CREATE OR REPLACE TABLE final_published AS "
                 "SELECT cm13 FROM customer_demographics''';"})
    assert out["stats"]["couldNotRead"] == 1
    assert out["risk"] == "unknown", out["risk"]


def test_a_clean_repository_still_says_no_impact(tmp_path):
    """The guard on the change above. A badge that says "not sure" on every scan
    ever run is a badge nobody reads."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE final_published AS SELECT other_col "
                 "FROM customer_demographics;"})
    assert out["stats"]["couldNotRead"] == 0
    assert out["risk"] == "none"


# ── the CREATE line, outside the SELECT ────────────────────────────────────
def test_a_partition_key_is_read(tmp_path):
    """A table partitioned by the very column being decommissioned returned NO
    usages at all -- the whole chain came back risk low, groups 0, couldNotRead
    0. Nothing published loses a column; the table simply stops being built,
    and everything under it serves data that is no longer refreshed."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE ds.mid PARTITION BY DATE(cm13)\n"
                 "AS SELECT other_col FROM ds.customer_demographics;",
        "b.sql": "CREATE OR REPLACE TABLE ds.final_published AS SELECT other_col FROM ds.mid;"})
    assert out["risk"] != "none"
    assert [s["prod"] for s in out["stopsLoading"]] == ["final_published"], out["stopsLoading"]


def test_a_cluster_key_is_read_too(tmp_path):
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE ds.mid CLUSTER BY cm13\n"
                 "AS SELECT other_col FROM ds.customer_demographics;",
        "b.sql": "CREATE OR REPLACE TABLE ds.final_published AS SELECT other_col FROM ds.mid;"})
    assert [s["prod"] for s in out["stopsLoading"]] == ["final_published"], out["stopsLoading"]


def test_a_bare_partition_column_is_read(tmp_path):
    """``PARTITION BY cm13`` with nothing round it parses as a bare identifier,
    not a column, so searching for columns finds nothing."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE ds.mid PARTITION BY cm13\n"
                 "AS SELECT other_col FROM ds.customer_demographics;",
        "b.sql": "CREATE OR REPLACE TABLE ds.final_published AS SELECT other_col FROM ds.mid;"})
    assert [s["prod"] for s in out["stopsLoading"]] == ["final_published"], out["stopsLoading"]


# ── a column named after a function ────────────────────────────────────────
PARENLESS = {
    "a.sql": "CREATE OR REPLACE TABLE stage_k AS SELECT current_date FROM customer_demographics;",
    "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT current_date FROM stage_k;",
}


def test_a_column_named_after_a_parenless_function_is_followed(tmp_path):
    """BigQuery lets CURRENT_DATE be written with no brackets, so a column of
    that name parses as a call and is invisible: risk none, found 0,
    nameInTables 0. Backticked, the very same scan reaches production."""
    out = scan(tmp_path, PARENLESS, attrs=("current_date",))
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_that_column_is_never_asserted_because_it_could_be_the_function(tmp_path):
    """Both readings are valid BigQuery and both are written the same way. So
    both are followed, and the row says the table is a guess."""
    out = scan(tmp_path, PARENLESS, attrs=("current_date",))
    rows = [r for g in out["groups"] for r in g["rows"]]
    assert rows and all(r["certain"] is False for r in rows), rows


def test_an_ordinary_use_of_the_function_is_left_alone(tmp_path):
    """The guard. ``WHERE dt = current_date`` is in a great many files, and a
    scan of an unrelated column must not be dragged into doubt by it."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 "
                 "FROM customer_demographics WHERE dt = current_date;"})
    rows = [r for g in out["groups"] for r in g["rows"]]
    assert rows and all(r["certain"] is True for r in rows), rows


# ── a hole where the column list goes ──────────────────────────────────────
def test_a_placeholder_in_the_select_list_is_not_a_column(tmp_path):
    """A great many Airflow DAGs build SQL as f"SELECT {cols} FROM ...". Ripple
    read it as a column called ``cols``, believed the published table had
    exactly that one, and answered risk none, unreadable 0, couldNotRead 0 -- a
    clean, confident, complete zero."""
    out = scan(tmp_path, {
        "job.py": 'cols = "cm13, cm14"\n'
                  'sql = f"""CREATE OR REPLACE TABLE ds.final_published AS '
                  'SELECT {cols} FROM ds.customer_demographics"""\n'})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_that_placeholder_is_not_described_as_a_select_star(tmp_path):
    """It carries columns nobody can see and names none of them, which is what
    a star does -- but the file does not say SELECT *, and a row that claims it
    does sends somebody to a line where no such statement is written."""
    out = scan(tmp_path, {
        "job.py": 'cols = "cm13, cm14"\n'
                  'sql = f"""CREATE OR REPLACE TABLE ds.final_published AS '
                  'SELECT {cols} FROM ds.customer_demographics"""\n'})
    star = out["starTables"]
    assert len(star) == 1 and star[0]["filledIn"], star
    rows = [r for g in out["groups"] for r in g["rows"]]
    assert all("SELECT *" not in r["logic"] for r in rows), [r["logic"] for r in rows]


# ── a SELECT written as a value, not as a source of rows ───────────────────
def test_an_alias_inside_a_scalar_subquery_is_not_the_output_name(tmp_path):
    """``c_alias`` exists only inside the brackets and is on no table anywhere.
    The real output name is peak_cm, which is what the next table reads -- so
    the chain went cold one hop early and reported no production impact."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE s1 AS\n"
                 "SELECT o.k, (SELECT MAX(d.cm13) AS c_alias FROM customer_demographics d "
                 "WHERE d.k = o.k) AS peak_cm\nFROM other_source o;",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT k, peak_cm FROM s1;"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


def test_an_alias_inside_an_in_subquery_does_not_invent_a_column(tmp_path):
    """The mirror of the same bug, over-reporting instead of under-reporting: a
    name written inside WHERE ... IN (SELECT cm13 AS c_alias ...) was published
    as a column of the table being built."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE s1 AS SELECT k FROM other_source\n"
                 "WHERE k IN (SELECT cm13 AS c_alias FROM customer_demographics);",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT c_alias FROM s1;"})
    assert out["groups"] == [], "c_alias is not a column of s1"


def test_a_rename_inside_a_from_subquery_still_survives(tmp_path):
    """The guard. A subquery in FROM really does hand its columns to the query
    around it, and its renames really do reach the table being built."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE s1 AS SELECT mc FROM "
                 "(SELECT cm13 AS mc FROM customer_demographics);",
        "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT mc FROM s1;"})
    assert [g["prod"] for g in out["groups"]] == ["final_published"]


# ── a folder Ripple is told to skip ────────────────────────────────────────
def test_code_in_a_skipped_folder_is_named_beside_the_answer(tmp_path):
    """``target/`` is dbt's compiled output -- the SQL that actually runs. The
    count reached the repository screen and nothing else, so the scan came back
    clean with the reason on a screen nobody was looking at."""
    out = scan(tmp_path, {
        "target/compiled/a.sql": "CREATE OR REPLACE TABLE final_published AS "
                                 "SELECT cm13 FROM customer_demographics;"})
    assert out["skippedInFolders"] == ["target/compiled/a.sql"]
    assert "target" in out["skippedFolderNames"]


# ── SELECT * REPLACE names the column ──────────────────────────────────────
REPLACED = {
    "a.sql": "CREATE OR REPLACE TABLE stage_r AS "
             "SELECT * REPLACE(legacy_code AS cm13) FROM customer_demographics;",
    "b.sql": "CREATE OR REPLACE TABLE final_published AS SELECT cm13 FROM stage_r;",
}


def test_a_replaced_column_breaks_the_statement_that_names_it(tmp_path):
    """Ripple got the right answer for the wrong reason: the rename was
    followed, but nothing said the name is written down here, so the row read
    breaking false about a statement that stops compiling."""
    out = scan(tmp_path, REPLACED)
    rows = [r for e in out["reached"] for r in e["rows"] if r["file"] == "a.sql"]
    assert rows and rows[0]["breaking"] is True, rows
    assert "REPLACE" in rows[0]["logic"], rows[0]["logic"]


def test_a_replaced_column_stops_carrying_its_own_values_onward(tmp_path):
    """The output column of that name holds the replacement's value from here
    on. The original column reaches nothing past this statement -- but the
    table it builds does stop being refreshed."""
    out = scan(tmp_path, REPLACED)
    assert out["groups"] == []
    assert [s["prod"] for s in out["stopsLoading"]] == ["final_published"]
    assert out["starTables"] == [], "it is not carried by the star either"


# ── the line under the wildcard ────────────────────────────────────────────
SUFFIXED = {
    "a.sql": "CREATE OR REPLACE TABLE g_published AS SELECT cm13 FROM "
             "`p.ds.customer_demographics_*` WHERE _TABLE_SUFFIX = '20260101';",
}


def test_a_shard_the_query_never_reads_is_not_reported(tmp_path):
    """A shard from 1999 against a query pinned to one day in 2026 came back
    risk medium, breaking true, CERTAIN true -- with the predicate that
    contradicts it printed in the snippet underneath."""
    out = scan(tmp_path, SUFFIXED, table="customer_demographics_19991231")
    assert out["groups"] == []


def test_the_shard_the_query_does_read_is_still_reported(tmp_path):
    """The guard on the change above."""
    out = scan(tmp_path, SUFFIXED, table="customer_demographics_20260101")
    assert [g["prod"] for g in out["groups"]] == ["g_published"]


def test_a_range_of_shards_is_read_as_a_range(tmp_path):
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE g_published AS SELECT cm13 FROM "
                 "`p.ds.customer_demographics_*` WHERE _TABLE_SUFFIX BETWEEN "
                 "'20260101' AND '20260131';"}, table="customer_demographics_20260115")
    assert [g["prod"] for g in out["groups"]] == ["g_published"]


def test_a_suffix_filter_ripple_cannot_evaluate_hedges_rather_than_drops(tmp_path):
    """A parameter is not something a static reader can work out. Dropping the
    finding on a guess would trade an over-confident answer for a missing one."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE g_published AS SELECT cm13 FROM "
                 "`p.ds.customer_demographics_*` WHERE _TABLE_SUFFIX = @run_date;"},
        table="customer_demographics_19991231")
    rows = [r for g in out["groups"] for r in g["rows"]]
    assert rows and all(r["certain"] is False for r in rows), rows


def test_asking_about_the_family_itself_is_never_narrowed(tmp_path):
    """Somebody who typed the asterisk is asking about every shard, so no one
    suffix can be tested against the predicate."""
    out = scan(tmp_path, SUFFIXED, table="customer_demographics_*")
    assert [g["prod"] for g in out["groups"]] == ["g_published"]


# ── one table, two files that build it ─────────────────────────────────────
def test_a_table_built_in_two_files_is_said_out_loud(tmp_path):
    """The only finding reported came from a stale copy under archive/,
    presented with breaking true and certain true and the same wording as any
    live finding, while the live definition sat under "mentions only"."""
    out = scan(tmp_path, {
        "live/a.sql": "CREATE OR REPLACE TABLE ds.final_published AS "
                      "SELECT id FROM ds.customer_demographics;",
        "archive/old.sql": "CREATE OR REPLACE TABLE ds.final_published AS "
                           "SELECT cm13 FROM ds.customer_demographics;"})
    forked = out["twoDefinitions"]
    assert len(forked) == 1, forked
    assert forked[0]["table"] == "final_published"
    assert forked[0]["files"] == ["archive/old.sql", "live/a.sql"]


def test_one_table_built_in_one_file_says_nothing(tmp_path):
    """The guard. A warning printed on every scan is one nobody reads."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE ds.final_published AS "
                 "SELECT cm13 FROM ds.customer_demographics;"})
    assert out["twoDefinitions"] == []


def test_a_table_loaded_by_several_inserts_is_not_a_fork(tmp_path):
    """Several files adding rows to one table is ordinary. Only a CREATE that
    replaces the whole thing makes two definitions of it."""
    out = scan(tmp_path, {
        "a.sql": "CREATE OR REPLACE TABLE ds.final_published AS "
                 "SELECT cm13 FROM ds.customer_demographics;",
        "b.sql": "INSERT INTO ds.final_published (cm13) "
                 "SELECT cm13 FROM ds.customer_demographics;"})
    assert out["twoDefinitions"] == []


# ── Dataform ───────────────────────────────────────────────────────────────
# Google's own tool for building BigQuery pipelines, and the likeliest thing in
# a BigQuery repository after dbt. A .sqlx file is an ordinary SELECT with a
# JavaScript ``config { }`` block on top. It was not opened, not counted and not
# mentioned: indexed False, risk none, prod [], with nothing anywhere recording
# that the file existed.
DATAFORM = {
    "definitions/mid.sqlx": 'config { type: "table" }\n\n'
                            'SELECT cm13 FROM ${ref("customer_demographics")}',
    "definitions/final_published.sqlx": 'config { type: "table" }\n\n'
                                        'SELECT cm13 FROM ${ref("mid")}',
}


def test_a_dataform_repository_reaches_its_published_table(tmp_path):
    out = scan(tmp_path, DATAFORM)
    assert [g["prod"] for g in out["groups"]] == ["final_published"]
    assert out["stats"]["couldNotRead"] == 0, out["unreadable"]


def test_a_dataform_model_says_where_its_name_came_from(tmp_path):
    out = scan(tmp_path, DATAFORM)
    assert {t["how"] for t in out["namedByFile"]} == {"Dataform"}


def test_dataform_pre_operations_are_read_as_the_sql_they_are(tmp_path):
    """config { } and js { } carry no lineage. pre_operations { } holds real
    SQL that runs before the model builds, so its brackets go and its contents
    stay."""
    _, _, parsed = build(tmp_path, {
        "definitions/mid.sqlx":
            'config { type: "incremental" }\n'
            'pre_operations {\n'
            '  DELETE FROM `p.d.staging_published` WHERE cm13 IS NULL\n'
            '}\n'
            'SELECT other_col FROM ${ref("customer_demographics")}'})
    targets = {s.target for s in parsed.statements}
    assert "d.staging_published" in targets, targets
    assert "mid" in targets, "the model itself is still named after its file"
    assert parsed.unreadable == [], parsed.unreadable
