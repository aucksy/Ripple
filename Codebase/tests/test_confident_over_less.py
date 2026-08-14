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
