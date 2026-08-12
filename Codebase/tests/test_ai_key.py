"""Tests for turning the AI on from the Settings screen.

The key is a secret on exactly the same terms as the GitHub access token, and
the thing most worth guarding is the same: it must never come back out of the
app, in any response, ever. Everything else here exists so that "AI is on"
means the model actually answered, not merely that a key was typed somewhere.

No test touches the network -- the one call Ripple would make is stubbed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ripple import ai                                           # noqa: E402
from ripple import api as rapi                                  # noqa: E402
from ripple.api import app                                      # noqa: E402
from ripple.config import AI_MODELS, DEFAULT_AI_MODEL, settings  # noqa: E402

SECRET = "gsk_thisisnotarealgroqkey000000000000"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def no_key_left_behind():
    """No test may leak a key into the next one."""
    yield
    rapi._state.update({"aiKey": "", "aiModel": ""})


@pytest.fixture
def model_answers(monkeypatch):
    """The model replies successfully, and records what it was called with."""
    seen: dict = {}

    def fake_chat(messages, cfg, max_tokens=1400):
        seen["key"] = cfg.groq_api_key
        seen["model"] = cfg.groq_model
        return '{"ok": true}'

    monkeypatch.setattr(ai, "_chat", fake_chat)
    return seen


@pytest.fixture
def model_refuses(monkeypatch):
    def fake_chat(messages, cfg, max_tokens=1400):
        raise ai.AIUnavailable("the model returned 401: invalid api key")

    monkeypatch.setattr(ai, "_chat", fake_chat)


# ── the secret ─────────────────────────────────────────────────────────────
def test_the_key_never_comes_back_out(client, model_answers):
    r = client.post("/api/ai/connect", json={"key": SECRET, "model": DEFAULT_AI_MODEL})
    assert r.status_code == 200
    assert SECRET not in r.text

    # ...nor from anywhere else that reports on the AI.
    for path, method in (("/api/health", "get"), ("/api/ai/check", "post")):
        body = getattr(client, method)(path).text
        assert SECRET not in body, path
        assert "gsk_" not in body, path


def test_health_says_a_key_is_set_without_saying_what(client, model_answers):
    client.post("/api/ai/connect", json={"key": SECRET, "model": DEFAULT_AI_MODEL})
    h = client.get("/api/health").json()["ai"]
    assert h["available"] is True
    assert h["keyFrom"] == "entered"
    assert "key" not in h and "apiKey" not in h


# ── turning it on ──────────────────────────────────────────────────────────
def test_a_key_that_works_turns_the_ai_on(client, model_answers):
    assert client.get("/api/health").json()["ai"]["available"] is False
    out = client.post("/api/ai/connect", json={"key": SECRET, "model": DEFAULT_AI_MODEL}).json()
    assert out["ai"]["available"] is True
    assert model_answers["key"] == SECRET, "the entered key must be the one used"


def test_a_key_that_does_not_work_is_refused_and_not_kept(client, model_refuses):
    r = client.post("/api/ai/connect", json={"key": SECRET, "model": DEFAULT_AI_MODEL})
    assert r.status_code == 502
    assert "401" in r.json()["detail"]
    assert client.get("/api/health").json()["ai"]["available"] is False, \
        "a rejected key must not be left switched on"


def test_connecting_with_no_key_at_all_is_refused(client):
    r = client.post("/api/ai/connect", json={"key": "", "model": DEFAULT_AI_MODEL})
    assert r.status_code == 400


def test_forgetting_the_key_turns_the_ai_off(client, model_answers):
    client.post("/api/ai/connect", json={"key": SECRET, "model": DEFAULT_AI_MODEL})
    out = client.post("/api/ai/forget").json()
    assert out["ai"]["available"] is False
    assert out["ai"]["keyFrom"] == ""


# ── choosing a model ───────────────────────────────────────────────────────
def test_the_chosen_model_is_the_one_called(client, model_answers):
    other = AI_MODELS[1]["id"]
    client.post("/api/ai/connect", json={"key": SECRET, "model": other})
    client.post("/api/ai/check")
    assert model_answers["model"] == other


def test_a_model_ripple_does_not_offer_is_refused(client, model_answers):
    r = client.post("/api/ai/connect", json={"key": SECRET, "model": "gpt-9-ultra"})
    assert r.status_code == 400
    assert client.get("/api/health").json()["ai"]["available"] is False


def test_the_screen_is_given_the_models_to_choose_from(client):
    h = client.get("/api/health").json()["ai"]
    assert [m["id"] for m in h["models"]] == [m["id"] for m in AI_MODELS]
    assert all(m["label"] and m["note"] for m in h["models"])
    assert h["model"] == DEFAULT_AI_MODEL
    assert h["modelLabel"] == AI_MODELS[0]["label"]


def test_the_default_model_is_a_real_groq_production_model(client):
    """Guards against a typo in the id, which only shows up as a 404 mid-demo."""
    assert DEFAULT_AI_MODEL == "openai/gpt-oss-120b"
    assert all("/" in m["id"] or m["id"].startswith("llama-") for m in AI_MODELS)


# ── it must still work with no key at all ──────────────────────────────────
def test_everything_still_runs_with_no_key(client):
    """Manual mode with no AI is the path that must never depend on any of this."""
    scan = client.post("/api/scan", json={
        "upstream": [{"table": "customer_demographics", "attrs": ["market_code"]}],
        "changeKind": "value_change"}).json()
    assert scan["groups"]
    out = client.post("/api/summary", json={"scan": scan, "vals": {}, "useAI": True}).json()
    assert out["summary"] and out["reply"]


def test_a_key_in_the_environment_is_reported_as_such(client, monkeypatch, model_answers):
    monkeypatch.setattr(settings, "groq_api_key", "gsk_from_the_environment", raising=False)
    h = client.get("/api/health").json()["ai"]
    assert h["available"] is True
    assert h["keyFrom"] == "environment"
    assert "gsk_from_the_environment" not in client.get("/api/health").text


# ── what a person reads when it goes wrong ─────────────────────────────────
@pytest.mark.parametrize("status,body,expect", [
    (401, '{"error":{"message":"Invalid API Key"}}', "mistyped, expired or revoked"),
    (429, '{"error":{"message":"rate limit"}}', "allowance on this key is used up"),
    (404, '{"error":{"message":"The model does not exist"}}', "no longer offers"),
    (503, "upstream unavailable", "trouble at its end"),
])
def test_a_failure_is_explained_in_words_not_json(status, body, expect):
    """A blob of provider JSON on screen helps nobody standing in front of it."""
    msg = ai._explain(status, body, settings)
    assert expect in msg
    assert "{" not in msg and "error" not in msg.lower().split("(")[0][:20]
