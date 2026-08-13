"""The offline app, end to end, and the things that must not be in it."""
from __future__ import annotations

import shutil

import pytest
from fastapi.testclient import TestClient

from conftest import MOCKREPO, SAMPLES
from ripple_offline import prefs
from ripple_offline.app import app, reindex


@pytest.fixture(scope="module")
def client():
    prefs.apply(prefs.save({"repoPath": str(MOCKREPO), "sqlDialect": "bigquery", "maxHops": 4}))
    reindex()
    return TestClient(app)


@pytest.fixture
def unconfigured(clean_home):
    prefs.apply(prefs.load())
    reindex()
    with TestClient(app) as c:
        yield c
    prefs.apply(prefs.save({"repoPath": str(MOCKREPO), "sqlDialect": "bigquery", "maxHops": 4}))
    reindex()


# ── nothing that reaches out ───────────────────────────────────────────────
@pytest.mark.parametrize("method,path", [
    ("post", "/api/repo/connect"),
    ("post", "/api/repo/disconnect"),
    ("post", "/api/ai/check"),
    ("post", "/api/ai/connect"),
    ("post", "/api/ai/forget"),
])
def test_the_routes_that_reach_out_do_not_exist(client, method, path):
    """Not disabled, not behind a flag -- absent."""
    assert getattr(client, method)(path).status_code == 404


def test_health_says_nothing_about_ai_or_a_token(client):
    h = client.get("/api/health").json()
    assert "ai" not in h and "github" not in h and "tokenSet" not in h
    assert h["offline"] is True


def test_the_guard_is_reported_honestly(client):
    """The screen claims nothing about being sealed off that this cannot confirm."""
    from ripple_offline import nonet
    out = client.post("/api/offline-check").status_code
    assert out == 405 or out == 404          # it is a GET, and only a GET
    body = client.get("/api/offline-check").json()
    assert body["guardInstalled"] == nonet.installed()


# ── before anything has been chosen ────────────────────────────────────────
def test_a_fresh_machine_does_not_crash_and_says_what_is_missing(unconfigured):
    h = unconfigured.get("/api/health").json()
    assert h["ok"] is True and h["configured"] is False
    assert h["folder"]["state"] == "unset"


def test_ripple_never_scans_its_own_program_folder(unconfigured):
    """An unset folder is an empty path, and an empty path means "here". Without
    care that indexes Ripple's own files and shows them as the repository."""
    h = unconfigured.get("/api/health").json()
    assert h["repo"]["files"] == 0
    assert h["repo"]["path"] == ""


def test_a_scan_before_a_folder_is_chosen_finds_nothing_rather_than_lying(unconfigured):
    out = unconfigured.post("/api/scan", json={
        "upstream": [{"table": "customer_demographics", "attrs": ["market_code"]}],
        "changeKind": "value_change"}).json()
    assert out["risk"] == "none" and out["groups"] == []


# ── choosing the folder and the dialect ────────────────────────────────────
def test_saving_a_folder_reads_it(clean_home):
    with TestClient(app) as c:
        h = c.post("/api/settings", json={"repoPath": str(MOCKREPO),
                                          "sqlDialect": "bigquery", "maxHops": 4}).json()
        assert h["configured"] is True
        assert h["repo"]["files"] > 15
        assert h["sqlDialect"] == "bigquery"


def test_saving_a_folder_that_is_not_there_is_refused_with_the_reason(client):
    r = client.post("/api/settings", json={"repoPath": r"D:\gone\missing",
                                           "sqlDialect": "bigquery", "maxHops": 4})
    assert r.status_code == 400
    assert "not on this machine any more" in r.json()["detail"]


def test_saving_an_unknown_dialect_is_refused(client):
    r = client.post("/api/settings", json={"repoPath": str(MOCKREPO),
                                           "sqlDialect": "klingon", "maxHops": 4})
    assert r.status_code == 400


def test_a_folder_that_disappears_stops_being_offered(clean_home, tmp_path):
    """Ripple reads the folder into memory when it starts. If the folder is gone
    by the time somebody looks at the screen, the reading is no longer true of
    anything -- and "that folder is gone" beside "24 files ready to scan" is
    worse than either on its own."""
    repo = tmp_path / "a-real-repo"
    repo.mkdir()
    (repo / "load.sql").write_text("CREATE TABLE A_PROD AS SELECT 1 AS X;", encoding="utf-8")
    with TestClient(app) as c:
        h = c.post("/api/settings", json={"repoPath": str(repo),
                                          "sqlDialect": "bigquery", "maxHops": 4}).json()
        assert h["repo"]["files"] == 1 and h["repo"]["exists"] is True

        shutil.rmtree(repo)                       # as if somebody tidied up
        after = c.get("/api/health").json()
        assert after["repo"]["exists"] is False
        assert after["repo"]["files"] == 0, "a folder that is gone cannot have files in it"
        assert "not on this machine any more" in after["folder"]["message"]


def test_a_place_ripple_cannot_write_to_says_what_to_do(client, monkeypatch):
    """Copied into Program Files, or opened straight off a network share, Ripple
    cannot save its settings beside itself. "Something went wrong: 500" tells
    nobody to move the folder."""
    def refuse(*_a, **_kw):
        raise PermissionError(13, "Access is denied")

    monkeypatch.setattr(prefs, "save", refuse)
    r = client.post("/api/settings", json={"repoPath": str(MOCKREPO),
                                           "sqlDialect": "bigquery", "maxHops": 4})
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert "does not allow writing" in detail
    assert "Desktop or Documents" in detail


def test_a_folder_can_be_checked_before_it_is_saved(client):
    out = client.post("/api/settings/check", json={"path": str(MOCKREPO)}).json()
    assert out["ok"] and out["files"] > 15


def test_the_dialect_really_changes_what_is_read(client, tmp_path):
    """The whole reason the setting is on screen. Read as generic SQL, a
    BigQuery file is not read less well -- it is not read at all.

    Measured on BigQuery SQL, not on the plain-SQL mock repository. Plain SQL
    reads the same either way, so proving the point there proved nothing.
    """
    (tmp_path / "snapshot.sql").write_text(
        "CREATE OR REPLACE TABLE `acme.stage.snap` AS\n"
        "SELECT c.customer_id, UPPER(c.market_code) AS mkt_cd\n"
        "FROM `acme.c360.customer_demographics` AS c\n"
        "QUALIFY ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY c.last_upd) = 1;\n",
        encoding="utf-8")
    bq = client.post("/api/settings", json={"repoPath": str(tmp_path),
                                            "sqlDialect": "bigquery", "maxHops": 4}).json()
    generic = client.post("/api/settings", json={"repoPath": str(tmp_path),
                                                 "sqlDialect": "", "maxHops": 4}).json()
    assert bq["repo"]["statements"] == 1 and bq["repo"]["unreadable"] == 0
    assert generic["repo"]["statements"] == 0 and generic["repo"]["unreadable"] == 1
    client.post("/api/settings", json={"repoPath": str(MOCKREPO),
                                       "sqlDialect": "bigquery", "maxHops": 4})


# ── the whole flow ─────────────────────────────────────────────────────────
def test_the_whole_flow_from_pasted_text(client):
    pasted = (SAMPLES / "01-market-code-value-change.eml").read_text(encoding="utf-8")
    read = client.post("/api/read-text", json={"text": pasted}).json()
    assert read["extractedBy"] == "rules"
    assert read["source"] == "C360"
    assert read["pocName"] == "Priya Raman"
    assert [u["table"].upper() for u in read["upstream"]][0] == "CUSTOMER_DEMOGRAPHICS"

    scan = client.post("/api/scan", json={
        "upstream": [{"table": u["table"], "attrs": u["attrs"]} for u in read["upstream"]],
        "changeKind": read["changeKind"]}).json()
    assert scan["groups"] and scan["stats"]["productionTables"] >= 1

    written = client.post("/api/summary", json={"scan": scan, "vals": read}).json()
    assert written["summary"]["headline"] and written["reply"]["body"]
    assert written["summary"]["writtenBy"] == "rules"

    saved = client.post("/api/history", json={"vals": read, "scan": scan,
                                              "summary": written["summary"], "mode": "email"}).json()
    assert saved["saved"] is True
    rows = client.get("/api/history").json()
    assert any(r["id"] == saved["id"] for r in rows)


def test_an_uploaded_eml_is_read(client):
    raw = (SAMPLES / "02-timestamp-decommission.eml").read_bytes()
    out = client.post("/api/read-email", files={"file": ("02.eml", raw, "message/rfc822")}).json()
    assert out["changeKind"] == "removal"
    assert out["pocTeam"] == "CODN Platform Team"


def test_history_is_kept_rather_than_thrown_away(client):
    """The one thing that is better offline: a real disk."""
    assert client.get("/api/health").json()["limits"]["historyKept"] is True


def test_a_finding_offers_no_link_to_click(client):
    """The files are on this machine. There is nowhere to send anyone."""
    scan = client.post("/api/scan", json={
        "upstream": [{"table": "customer_demographics", "attrs": ["market_code"]}],
        "changeKind": "value_change"}).json()
    assert scan["repo"]["urlTemplate"] == ""


def test_the_honesty_features_are_still_there(client):
    scan = client.post("/api/scan", json={
        "upstream": [{"table": "customer_demographics", "attrs": ["market_code"]}],
        "changeKind": "value_change"}).json()
    assert scan["unreadable"], "the 'could not read' list must survive"
    clean = client.post("/api/scan", json={
        "upstream": [{"table": "prospect_master", "attrs": ["legacy_segment_code"]}],
        "changeKind": "removal"}).json()
    assert clean["mentions_only"] if "mentions_only" in clean else clean["mentionsOnly"]


def test_file_contents_can_be_opened_in_place(client):
    out = client.get("/api/file", params={"path": "odl/customer_profile_odl.sql"}).json()
    assert any("market_code" in line.lower() for line in out["lines"])


def test_a_path_outside_the_index_is_refused(client):
    assert client.get("/api/file", params={"path": "../../secrets.txt"}).status_code == 404


def test_the_offline_page_is_served(client):
    page = client.get("/")
    assert page.status_code == 200
    assert "Ripple Offline" in page.text
