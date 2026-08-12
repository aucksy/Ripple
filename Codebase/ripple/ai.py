"""The optional AI layer.

Two jobs only: read the notification email at the front, and write the English
at the back. It is never shown a single line of source code -- the findings it
summarises are already structured facts produced by the scanner.

If there is no key, or the call fails, every function here falls back to a
written-out version. Ripple must work with the AI switched off.
"""
from __future__ import annotations

import json
import re

import httpx

from .config import Settings, settings as default_settings

READ_EMAIL_PROMPT = """You extract structured fields from a data-change notification email.

Return ONLY a JSON object, no prose, with exactly these keys:
  source        - the upstream system or team sending the notice (short, e.g. "C360")
  changeType    - one of: "Attribute decommission", "Value format change",
                  "Data type change", "Attribute rename", "Not specified"
  changeKind    - one of: "removal", "value_change", "type_change", "rename", "unknown"
  changeDesc    - one plain sentence describing what is changing
  effectiveDate - the date the change takes effect, as YYYY-MM-DD, or ""
  pocName       - the person to reply to
  pocEmail      - their email address, or ""
  pocTeam       - their team
  upstream      - a list of {"table": "...", "attrs": ["...", "..."]}

Rules:
- Only list tables and attributes the email actually names. Never invent one.
- Use the exact spelling from the email, including underscores and case.
- If a value is not stated, use an empty string rather than guessing.
"""

SUMMARY_PROMPT = """You write a short impact summary for a data engineering team.

You are given structured findings from a code scan. Write plain English for a
reader who is not a database expert. Never invent a table, file or number that
is not in the findings.

Return ONLY a JSON object with exactly these keys:
  headline  - one line, under 90 characters, stating the situation
  narrative - two or three sentences explaining what happens and why
  bullets   - 3 to 5 short strings, the most consequential points first
  actions   - 3 to 5 short strings, each a concrete next step
"""

REPLY_PROMPT = """You draft a reply to the team who sent a data-change notification.

Be brief, factual and specific. State the impact found, what this team will do,
and any question the upstream team must answer. Never invent findings.

Return ONLY a JSON object with exactly these keys:
  subject - the reply subject line
  body    - the email body, plain text, with line breaks
"""


class AIUnavailable(Exception):
    pass


def _chat(messages: list[dict], cfg: Settings, max_tokens: int = 1400) -> str:
    if not cfg.groq_api_key:
        raise AIUnavailable("no API key configured")
    try:
        r = httpx.post(
            f"{cfg.groq_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {cfg.groq_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": cfg.groq_model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"},
            },
            timeout=45.0,
        )
    except Exception as exc:
        raise AIUnavailable(f"could not reach the model ({type(exc).__name__})") from exc
    if r.status_code != 200:
        detail = r.text[:200]
        raise AIUnavailable(f"the model returned {r.status_code}: {detail}")
    try:
        return r.json()["choices"][0]["message"]["content"]
    except Exception as exc:
        raise AIUnavailable(f"unexpected response shape ({exc})") from exc


def _json_from(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    raise AIUnavailable("the model did not return usable JSON")


def read_email(text: str, cfg: Settings | None = None) -> dict:
    cfg = cfg or default_settings
    out = _json_from(
        _chat(
            [
                {"role": "system", "content": READ_EMAIL_PROMPT},
                {"role": "user", "content": text[:12000]},
            ],
            cfg,
        )
    )
    upstream = []
    for u in out.get("upstream") or []:
        table = (u.get("table") or "").strip()
        attrs = [a.strip() for a in (u.get("attrs") or []) if a and a.strip()]
        if table:
            upstream.append({"table": table, "attrs": attrs})
    out["upstream"] = upstream
    out["extractedBy"] = "ai"
    out.setdefault("warnings", [])
    return out


def write_summary(payload: dict, cfg: Settings | None = None) -> dict:
    cfg = cfg or default_settings
    out = _json_from(
        _chat(
            [
                {"role": "system", "content": SUMMARY_PROMPT},
                {"role": "user", "content": json.dumps(payload)[:14000]},
            ],
            cfg,
        )
    )
    out["writtenBy"] = "ai"
    return out


def write_reply(payload: dict, cfg: Settings | None = None) -> dict:
    cfg = cfg or default_settings
    out = _json_from(
        _chat(
            [
                {"role": "system", "content": REPLY_PROMPT},
                {"role": "user", "content": json.dumps(payload)[:14000]},
            ],
            cfg,
        )
    )
    out["writtenBy"] = "ai"
    return out


def check_key(cfg: Settings | None = None) -> dict:
    """Used by the settings screen so a bad key is obvious immediately."""
    cfg = cfg or default_settings
    if not cfg.groq_api_key:
        return {"ok": False, "reason": "No key set. Ripple is running without AI."}
    try:
        _chat(
            [
                {"role": "system", "content": 'Reply with {"ok":true} and nothing else.'},
                {"role": "user", "content": "ping"},
            ],
            cfg,
            max_tokens=20,
        )
        return {"ok": True, "model": cfg.groq_model}
    except AIUnavailable as exc:
        return {"ok": False, "reason": str(exc)}
