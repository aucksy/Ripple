"""Reading the SQL a real pipeline is actually written in.

Almost nothing in a production repository is plain SQL. The project and dataset
names are placeholders filled in by Airflow, dbt or an in-house generator before
a database ever sees the file. A parser refuses those outright, so an entire
repository comes back "could not be read" -- and a scan over a repository that
was never read reports no impact, confidently, on a change that breaks things.

That is the worst failure this tool has, so the shapes that caused it are
pinned here: the templating, one bad statement taking a whole file down with it,
and a chain that ends somewhere the production naming rule does not match.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ripple import narrative                                    # noqa: E402
from ripple.catalog import build_catalog                        # noqa: E402
from ripple.config import Settings, parse_production_rule       # noqa: E402
from ripple.scanner.lineage import trace                        # noqa: E402
from ripple.scanner.repo import RepoIndex                       # noqa: E402
from ripple.scanner.sqlread import parse_repo, split_statements  # noqa: E402
from ripple.scanner.templating import fill_placeholders         # noqa: E402

# The shape of the office repository this was reported from: Airflow-templated
# BigQuery, tables named _umdl and _gdi, and not one of them named _prod.
FILES = {
    "src/sql/DML/transform/cmdl_TL_web_activity_umdl.sql": """
        SET operation_time = PARSE_TIMESTAMP("%Y-%m-%dT%H:%M:%S", CURRENT_TIMESTAMP());

        --pub Guid AND pvt guid
        CREATE OR REPLACE TABLE {{tgt_project_id}}.{{stage_dataset}}.myca_web_activity AS
        SELECT LOWER(user_pvt_guid) AS user_pvt_guid,
               LOWER(pub_guid)      AS pub_guid,
               MAX(creat_ts)        AS creat_ts
        FROM {{src_project_id}}.{{src_anon_dataset}}.myca_mobile_web_logon_activity
        WHERE TRIM(logon_sta_cd) = '0'
          AND TRIM(UPPER(pub_guid)) <> 'BLUEBOXPUBLIC'
        GROUP BY LOWER(user_pvt_guid), LOWER(pub_guid);

        CREATE OR REPLACE TABLE {{tgt_project_id}}.{{stage_dataset}}.card_pub_pvt_guid_umdl AS
        SELECT w.pub_guid, w.creat_ts
        FROM {{tgt_project_id}}.{{stage_dataset}}.myca_web_activity w
        WHERE w.pub_guid IS NOT NULL;
    """,
    "src/dag/transformation/gdi/cmdl_transaction_billed_gdi.py": '''
BILLED_SQL = """
CREATE OR REPLACE TABLE {{ params.tgt }}.{dataset}.transaction_billed_gdi AS
SELECT c.pub_guid, t.bill_amt
FROM {{ params.src }}.raw.card_pub_pvt_guid_umdl AS c
JOIN {{ params.src }}.raw.txn AS t ON t.pub_guid = c.pub_guid
"""
''',
    "src/sql/DML/common/cmdl_get_last_lumi_source_creation_time.sql": """
        CREATE OR REPLACE TABLE {{p}}.{{d}}.first_one AS
        SELECT pub_guid FROM {{p}}.{{d}}.myca_web_activity;

        THIS LINE IS NOT SQL AND NEVER WAS @@@ ;

        CREATE OR REPLACE TABLE {{p}}.{{d}}.last_one AS
        SELECT pub_guid FROM {{p}}.{{d}}.myca_web_activity;
    """,
}


def build(tmp_path: Path, dialect: str = "bigquery", production: str = "") -> tuple:
    for rel, text in FILES.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    cfg = Settings()
    cfg.sql_dialect = dialect
    cfg.repo_path = tmp_path
    if production:
        cfg.production_patterns = parse_production_rule(production)
    idx = RepoIndex.build(tmp_path, cfg)
    parsed = parse_repo(idx, cfg)
    return cfg, idx, parsed


def scan(tmp_path: Path, production: str = "") -> dict:
    cfg, idx, parsed = build(tmp_path, production=production)
    return trace(idx, parsed,
                 [{"table": "myca_mobile_web_logon_activity", "attrs": ["pub_guid"]}],
                 change_type="value_change", cfg=cfg).to_dict()


# ── filling the placeholders in ────────────────────────────────────────────
def test_a_templated_table_name_still_names_the_table():
    """{{project}}.{{dataset}}.orders is the orders table, and always was."""
    out = fill_placeholders("SELECT * FROM {{tgt_project_id}}.{{stage_dataset}}.orders")
    assert out == "SELECT * FROM tgt_project_id.stage_dataset.orders"


def test_line_numbers_do_not_move():
    """Findings point at a line of the real file, so a replacement must never
    swallow a line break -- a finding on the wrong line is worse than none."""
    sql = "SELECT 1\n{% if params.full %}\nWHERE {{ x }} = 1\n{% endif %}\n"
    assert fill_placeholders(sql).count("\n") == sql.count("\n")


def test_dbt_ref_names_the_model_it_refers_to():
    assert fill_placeholders("SELECT * FROM {{ ref('orders') }}") == "SELECT * FROM orders"
    assert fill_placeholders("FROM {{ source('raw', 'orders') }}") == "FROM orders"


def test_a_regular_expression_is_left_alone():
    """{3} in a pattern is a quantifier, not a placeholder."""
    sql = r"SELECT REGEXP_CONTAINS(x, r'\d{3}') FROM t"
    assert fill_placeholders(sql) == sql


def test_a_templated_repository_is_read(tmp_path):
    _, _, parsed = build(tmp_path)
    targets = {s.target for s in parsed.statements}
    assert {"myca_web_activity", "card_pub_pvt_guid_umdl", "transaction_billed_gdi"} <= targets
    cat = build_catalog(parsed)
    assert "MYCA_WEB_ACTIVITY" in cat.tables


# ── one bad statement is one bad statement ─────────────────────────────────
def test_one_unreadable_statement_does_not_lose_the_whole_file(tmp_path):
    _, _, parsed = build(tmp_path)
    targets = {s.target for s in parsed.statements}
    assert {"first_one", "last_one"} <= targets, "the statements either side survived"


def test_the_gap_says_which_line_and_shows_it(tmp_path):
    """This list exists so somebody goes and checks those files. "ParseError"
    sends them hunting; a line number and the line itself does not."""
    _, _, parsed = build(tmp_path)
    gap = next(u for u in parsed.unreadable if "lumi" in u["file"])
    assert gap["line"] == 5
    assert "NOT SQL" in gap["snippet"]
    assert "1 of 3 statements" in gap["reason"]


def test_semicolons_inside_quotes_do_not_split_a_statement():
    parts = split_statements("SELECT ';' AS a FROM t; SELECT 2;")
    assert len(parts) == 2


def test_a_semicolon_in_a_comment_does_not_split_a_statement():
    parts = split_statements("SELECT 1 -- a; comment\nFROM t;\nSELECT 2;")
    assert len(parts) == 2


# ── a chain that reaches no _PROD table is still a chain ───────────────────
def test_findings_are_reported_even_when_nothing_matches_the_production_rule(tmp_path):
    """The report that started all of this: three real, breaking usages shown
    as a clean result, purely because no table in the repository is named
    _PROD. Nothing may be hidden behind the naming rule."""
    out = scan(tmp_path)
    assert out["groups"] == [], "nothing here is named _PROD"
    assert out["reached"], "but the change plainly reaches tables, and they must be listed"
    assert out["risk"] != "none"
    assert out["stats"]["tablesReached"] >= 1


def test_correcting_the_rule_turns_them_into_production_tables(tmp_path):
    out = scan(tmp_path, production="_UMDL, _GDI")
    assert [g["prod"] for g in out["groups"]] == ["card_pub_pvt_guid_umdl",
                                                  "transaction_billed_gdi"]
    assert out["stats"]["productionTables"] == 2


def test_the_summary_does_not_say_no_impact_over_a_list_of_findings(tmp_path):
    """This wording is forwarded to the upstream team in writing."""
    out = scan(tmp_path)
    vals = {"upstream": [{"table": "myca_mobile_web_logon_activity", "attrs": ["pub_guid"]}]}
    s = narrative.summarise(out, vals)
    r = narrative.draft_reply(out, {**vals, "pocName": "Priya Raman"}, s)
    assert "no impact" not in s["headline"].lower()
    assert "no impact" not in r["body"].lower()
    assert "no impact" not in r["subject"].lower()


def test_a_genuinely_clean_result_still_says_no_impact(tmp_path):
    """The honest half of the same rule: nothing found really is nothing."""
    cfg, idx, parsed = build(tmp_path)
    out = trace(idx, parsed, [{"table": "nowhere", "attrs": ["not_a_column"]}],
                change_type="removal", cfg=cfg).to_dict()
    assert out["groups"] == [] and out["reached"] == [] and out["other"] == []
    s = narrative.summarise(out, {"upstream": []})
    assert "No impact" in s["headline"]


# ── the answer to "how do I check this?" ───────────────────────────────────
def test_every_attribute_reports_what_came_back(tmp_path):
    cfg, idx, parsed = build(tmp_path)
    out = trace(idx, parsed,
                [{"table": "myca_mobile_web_logon_activity",
                  "attrs": ["pub_guid", "attribute_that_is_not_there"]}],
                change_type="value_change", cfg=cfg).to_dict()
    by_attr = {a["attr"]: a for a in out["attributes"]}
    assert by_attr["pub_guid"]["found"] > 0
    assert by_attr["pub_guid"]["mentionedIn"] > 0
    missing = by_attr["attribute_that_is_not_there"]
    assert missing["found"] == 0 and missing["mentionedIn"] == 0


def test_attributes_impacted_counts_what_was_confirmed(tmp_path):
    """The card says "of those you confirmed", so a column renamed twice on the
    way down is one attribute, not three."""
    out = scan(tmp_path)
    assert out["stats"]["attributesImpacted"] == 1


# ── the production rule itself ─────────────────────────────────────────────
@pytest.mark.parametrize("rule,table,expected", [
    ("_PROD", "sales_prod", True),
    ("_PROD", "sales_umdl", False),
    ("_UMDL, _GDI", "card_pub_pvt_guid_umdl", True),
    ("_UMDL, _GDI", "transaction_billed_gdi", True),
    ("PROD_*", "prod_sales", True),
    ("PROD_*", "sales_prod", False),
    ("*", "anything_at_all", True),
    ("CUSTOMER_PROFILE_PROD", "customer_profile_prod", True),
])
def test_the_production_rule_matches_the_way_it_is_described(rule, table, expected):
    cfg = Settings()
    cfg.production_patterns = parse_production_rule(rule)
    assert cfg.is_production_table(table) is expected


def test_an_empty_rule_is_not_read_as_every_table_being_safe():
    """An empty list would make is_production_table always false, which reports
    every repository in the world as clean."""
    assert parse_production_rule("  ,  , ") == ()
    assert Settings().production_patterns, "the default must never be empty"
