"""Choosing the repository folder and the SQL dialect on screen.

Online these are environment variables. Offline nobody is going to set one, so
they are asked for — and the answers have to survive a restart, survive the
folder being moved, and never quietly fall back to reading BigQuery as generic
SQL.
"""
from __future__ import annotations

import json

import pytest

from conftest import MOCKREPO
from ripple_offline import prefs


def test_the_default_dialect_is_bigquery(clean_home):
    """Our stack. A wrong default here inverts answers rather than blurring them."""
    assert prefs.load()["sqlDialect"] == "bigquery"


def test_nothing_is_configured_on_a_fresh_machine(clean_home):
    assert prefs.configured(prefs.load()) is False


def test_settings_survive_a_restart(clean_home):
    prefs.save({"repoPath": str(MOCKREPO), "sqlDialect": "snowflake", "maxHops": 5})
    again = prefs.load()
    assert again["repoPath"] == str(MOCKREPO)
    assert again["sqlDialect"] == "snowflake"
    assert again["maxHops"] == 5
    assert prefs.configured(again) is True


def test_the_settings_file_is_readable_by_a_person(clean_home):
    prefs.save({"repoPath": str(MOCKREPO), "sqlDialect": "bigquery", "maxHops": 4})
    written = json.loads((clean_home / "ripple-settings.json").read_text(encoding="utf-8"))
    assert written["repoPath"] == str(MOCKREPO)
    assert written["sqlDialect"] == "bigquery"


def test_a_damaged_settings_file_does_not_stop_ripple_starting(clean_home):
    (clean_home / "ripple-settings.json").write_text("{not json at all", encoding="utf-8")
    values = prefs.load()
    assert values["sqlDialect"] == "bigquery" and values["repoPath"] == ""


def test_a_dialect_that_does_not_exist_is_refused(clean_home):
    assert not prefs.valid_dialect("klingon")
    saved = prefs.save({"repoPath": str(MOCKREPO), "sqlDialect": "klingon", "maxHops": 4})
    assert saved["sqlDialect"] == "bigquery"


def test_every_offered_dialect_is_one_sqlglot_really_knows():
    """An option that cannot work is worse than a missing one: it gets picked,
    saved, and then quietly reads everything as generic SQL anyway."""
    from sqlglot import Dialect
    for choice in prefs.dialects():
        assert choice["id"] == "" or choice["id"] in Dialect.classes


def test_the_label_defaults_to_the_folder_name(clean_home):
    saved = prefs.save({"repoPath": str(MOCKREPO), "sqlDialect": "bigquery", "maxHops": 4})
    assert saved["repoLabel"] == "mockrepo"


# ── a folder that is not where it was ──────────────────────────────────────
def test_a_good_folder_says_how_much_it_holds():
    verdict = prefs.check_folder(MOCKREPO)
    assert verdict["ok"] and verdict["files"] > 15
    assert "file" in verdict["message"]


def test_a_deleted_folder_says_so_plainly():
    verdict = prefs.check_folder(r"D:\this\folder\was\deleted")
    assert not verdict["ok"] and verdict["state"] == "missing"
    assert "not on this machine any more" in verdict["message"]
    assert "deleted" in verdict["message"]        # names the folder it tried


def test_a_folder_that_is_really_a_file_says_so(tmp_path):
    f = tmp_path / "notafolder.txt"
    f.write_text("hello", encoding="utf-8")
    verdict = prefs.check_folder(f)
    assert not verdict["ok"] and "not a folder" in verdict["message"]


def test_a_folder_with_no_code_says_so(tmp_path):
    (tmp_path / "holiday.jpg").write_bytes(b"\x00")
    verdict = prefs.check_folder(tmp_path)
    assert not verdict["ok"] and verdict["state"] == "empty"
    assert "no files Ripple can read" in verdict["message"]


def test_no_folder_chosen_is_not_an_error_message_about_crashes():
    verdict = prefs.check_folder("")
    assert not verdict["ok"] and verdict["state"] == "unset"


# ── what the settings mean to the shared engine ────────────────────────────
def test_applying_settings_points_the_shared_engine_at_the_folder(clean_home):
    from ripple.config import settings
    prefs.apply(prefs.save({"repoPath": str(MOCKREPO), "sqlDialect": "bigquery", "maxHops": 4}))
    assert str(settings.repo_path) == str(MOCKREPO)
    assert settings.sql_dialect == "bigquery"
    assert settings.repo_source == "folder"


def test_applying_settings_leaves_no_way_to_reach_out(clean_home):
    """Belt and braces: the engine is told there is no key and no repository to
    pull, rather than trusted to leave them alone."""
    from ripple.config import settings
    prefs.apply(prefs.load())
    assert settings.groq_api_key == ""
    assert settings.github_token == "" and settings.github_repo == ""
    assert settings.ai_available() is False


def test_history_is_kept_beside_the_program(clean_home):
    from ripple.config import settings
    prefs.apply(prefs.load())
    assert settings.db_path.parent == clean_home
    assert settings.serverless is False


@pytest.mark.parametrize("head,expected", [
    ("ref: refs/heads/main\n", "main"),
    ("ref: refs/heads/release-2026\n", "release-2026"),
    ("9f8c1a2b3c4d5e6f\n", "9f8c1a2"),       # a detached checkout
])
def test_the_branch_is_read_from_the_folder_itself(tmp_path, head, expected):
    """A copied-out repository still knows which branch it came from, and that
    is a real fact rather than a guess of "main"."""
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text(head, encoding="utf-8")
    assert prefs.git_branch(tmp_path) == expected


def test_a_folder_that_was_never_a_checkout_claims_no_branch(tmp_path):
    assert prefs.git_branch(tmp_path) == ""
