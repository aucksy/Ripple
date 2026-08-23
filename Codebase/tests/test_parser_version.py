"""The parse tree must be read the same way whichever sqlglot is installed.

sqlglot renames the keys inside its own nodes between major versions, and three
of the renames that matter here are SILENT: the old key simply returns None, so
the code carries on and finds nothing. Two of them switch off things this tool
exists to do -- ``SELECT * EXCEPT(col)`` stops being noticed, and every rename a
MERGE makes disappears.

Nothing raises. Every test would go on passing on the version installed today
and the answers would go quietly wrong on the next one. So the keys are read
through ripple/scanner/dialectcompat.py, and these tests fail LOUDLY the moment
one of them stops resolving.

They are written against the real parser rather than against a mock, because
the thing being guarded is exactly the gap between what the code expects and
what the library actually returns.
"""
from __future__ import annotations

import sys
from pathlib import Path

import sqlglot
from sqlglot import exp

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ripple.scanner import dialectcompat as compat          # noqa: E402


def parse(sql: str):
    return sqlglot.parse_one(sql, dialect="bigquery")


def test_the_from_clause_still_resolves():
    """Empty, the check that decides which tables a SELECT * covers finds
    nothing, and every star hop stops being followed."""
    sel = parse("SELECT * FROM customer_demographics").find(exp.Select)
    found = compat.from_of(sel)
    assert found is not None
    assert isinstance(found.this, exp.Table)


def test_select_star_except_still_resolves():
    """Empty, a column dropped BY NAME is reported as carried through -- which
    is the opposite of the truth, on the one shape that stops a chain."""
    star = parse("SELECT * EXCEPT(cm13) FROM customer_demographics").find(exp.Star)
    assert [c.name for c in compat.star_except(star)] == ["cm13"]


def test_select_star_replace_still_resolves():
    star = parse("SELECT * REPLACE(legacy AS cm13) FROM customer_demographics").find(exp.Star)
    assert compat.star_replace(star), "REPLACE swaps a column and must be visible"


def test_every_merge_branch_still_resolves():
    """Empty, every rename a MERGE makes disappears -- and a MERGE is how a
    published table is normally loaded on BigQuery."""
    merged = parse(
        "MERGE INTO tgt t USING src s ON t.k = s.k "
        "WHEN MATCHED THEN UPDATE SET market = s.cm13 "
        "WHEN NOT MATCHED THEN INSERT (k, market) VALUES (s.k, s.cm13)")
    whens = compat.merge_whens(merged)
    assert len(whens) == 2, whens


def test_the_rename_node_still_exists():
    """The one rename that is loud: the class stops existing altogether."""
    renamed = parse("ALTER TABLE old_name RENAME TO new_name")
    actions = renamed.args.get("actions") or []
    assert any(isinstance(a, compat.RENAME_NODE) for a in actions), actions


def test_the_pinned_version_is_the_one_installed():
    """A build made against a different parser is a different tool. The pin is
    in requirements.txt; this fails if the environment has drifted from it."""
    pinned = ""
    for line in (Path(__file__).resolve().parent.parent / "requirements.txt") \
            .read_text(encoding="utf-8").splitlines():
        if line.strip().lower().startswith("sqlglot=="):
            pinned = line.split("==", 1)[1].split()[0].strip()
            break
    assert pinned, "sqlglot must be pinned in requirements.txt"
    assert sqlglot.__version__ == pinned, (
        f"requirements.txt pins {pinned} but {sqlglot.__version__} is installed")
