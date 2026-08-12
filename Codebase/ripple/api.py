"""The web service.

Thin on purpose: every route is a few lines that call the scanner, the reader
or the writer. All of the thinking lives in those modules, so the same logic
runs from the command line, from a test, or from this API.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import ai, narrative, store
from .catalog import Catalog, build_catalog
from .config import _serverless, settings
from .notification import Notification, extract_by_rules, read_upload
from .scanner import github as ghub
from .scanner.lineage import trace
from .scanner.repo import RepoIndex
from .scanner.sqlread import ParsedRepo, parse_repo

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(title="Ripple", docs_url="/api/docs", redoc_url=None)

# ── the index, built once and reused ───────────────────────────────────────
# "token" is a secret held only in this process. It is never written to disk,
# never logged, and never put in a response -- routes report whether one is set,
# never what it is.
_state: dict[str, Any] = {
    "index": None, "parsed": None, "catalog": None,
    "source": "folder", "conn": None, "token": "", "error": "",
}


def _active_token() -> str:
    """A token typed into the app wins over one set in the environment."""
    return _state["token"] or settings.github_token


def _install(idx: RepoIndex, source: str, conn: "ghub.Connection | None") -> None:
    parsed = parse_repo(idx, settings)
    _state.update({
        "index": idx, "parsed": parsed, "catalog": build_catalog(parsed),
        "source": source, "conn": conn,
    })


def _use_folder() -> None:
    _install(RepoIndex.build(settings.repo_path, settings), "folder", None)


def _use_github(repo: str, token: str, branch: str) -> None:
    idx, conn = ghub.connect(repo, token, branch, settings)
    _install(idx, "github", conn)
    _state["error"] = ""


def repo_state() -> tuple[RepoIndex, ParsedRepo, Catalog]:
    """The current repository, built on first use and kept until re-read.

    If GitHub is configured but cannot be reached, Ripple falls back to the
    local folder and remembers why, so the screen can say so rather than the
    whole app failing.
    """
    if _state["index"] is None:
        if settings.repo_source == "github" and settings.github_repo:
            token = _active_token()
            if not token:
                _state["error"] = ("GitHub is configured but no access token is set. "
                                   "Add one on the Repository step, or set GITHUB_TOKEN.")
                _use_folder()
            else:
                try:
                    _use_github(settings.github_repo, token, settings.github_branch)
                except ghub.GitHubError as exc:
                    _state["error"] = str(exc)
                    _use_folder()
        else:
            _use_folder()
    return _state["index"], _state["parsed"], _state["catalog"]


def reindex() -> None:
    """Read the repository again from wherever it currently comes from."""
    source, conn = _state["source"], _state["conn"]
    _state["index"] = None
    if source == "github" and conn is not None:
        _use_github(conn.ref.slug, _active_token(), conn.branch)
    else:
        _state["index"] = None
        repo_state()


# ── models ─────────────────────────────────────────────────────────────────
class UpstreamIn(BaseModel):
    table: str
    attrs: list[str] = []


class ScanIn(BaseModel):
    upstream: list[UpstreamIn]
    changeKind: str = "unknown"


class SummaryIn(BaseModel):
    scan: dict
    vals: dict
    useAI: bool = True


class SaveIn(BaseModel):
    vals: dict
    scan: dict
    summary: dict
    mode: str = "email"


class StatusIn(BaseModel):
    status: str


class PasteIn(BaseModel):
    text: str
    useAI: bool = True


class ConnectIn(BaseModel):
    repo: str = ""          # owner/repository, or the address pasted from GitHub
    branch: str = ""        # blank means the repository's default branch
    token: str = ""         # blank means keep using whatever is already set


# ── routes ─────────────────────────────────────────────────────────────────
def _token_origin() -> str:
    """Where the token in play came from -- never the token itself."""
    if _state["token"]:
        return "entered"
    if settings.github_token:
        return "environment"
    return ""


def _github_facts() -> dict | None:
    conn: ghub.Connection | None = _state["conn"]
    if _state["source"] != "github" or conn is None:
        return None
    return {
        "slug": conn.ref.slug,
        "owner": conn.ref.owner,
        "repo": conn.ref.repo,
        "branch": conn.branch,
        "commit": conn.commit,
        "shortCommit": conn.commit[:7],
        "private": conn.private,
        "defaultBranch": conn.default_branch,
        "archiveFiles": conn.total_files,
        "webUrl": conn.ref.web_url(),
    }


@app.get("/api/health")
def health() -> dict:
    idx, parsed, cat = repo_state()
    # What kinds of file are actually in the index, biggest group first. The
    # screen shows these, so they have to be counted rather than assumed.
    kinds: dict[str, int] = {}
    for f in idx.files:
        kinds[f.lang] = kinds.get(f.lang, 0) + 1
    gh = _github_facts()
    on_github = gh is not None
    return {
        "ok": True,
        "source": _state["source"],
        "github": gh,
        "tokenSet": bool(_active_token()),
        "tokenFrom": _token_origin(),
        "connectError": _state["error"],
        # On a serverless host each request can land on a fresh instance, so a
        # token typed into the screen will not last. The screen says so.
        "serverless": _serverless(),
        "repo": {
            "label": gh["slug"] if on_github else settings.repo_label,
            "branch": gh["branch"] if on_github else settings.repo_branch,
            "path": gh["webUrl"] if on_github else str(settings.repo_path),
            "files": len(idx.files),
            "statements": len(parsed.statements),
            "unreadable": len(parsed.unreadable),
            "exists": True if on_github else settings.repo_path.exists(),
            "kinds": [
                {"lang": k, "files": n}
                for k, n in sorted(kinds.items(), key=lambda kv: (-kv[1], kv[0]))
            ],
        },
        "catalog": {"tables": len(cat.tables), "columns": sum(len(v) for v in cat.tables.values())},
        "sqlDialect": settings.sql_dialect or "generic",
        "maxHops": settings.max_hops,
        "ai": {"available": settings.ai_available(), "model": settings.groq_model},
    }


@app.get("/api/catalog")
def catalog() -> dict:
    _, _, cat = repo_state()
    return cat.to_dict()


@app.post("/api/ai/check")
def ai_check() -> dict:
    return ai.check_key(settings)


@app.post("/api/reindex")
def do_reindex() -> dict:
    try:
        reindex()
    except ghub.GitHubError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return health()


# ── connecting to GitHub ───────────────────────────────────────────────────
@app.post("/api/repo/connect")
def repo_connect(payload: "ConnectIn") -> dict:
    """Read a GitHub repository with an access token.

    The token is kept in this process only, for as long as it is running. It is
    not written anywhere and is not returned by this or any other route.
    """
    repo = (payload.repo or "").strip()
    if not repo:
        raise HTTPException(status_code=400, detail="Enter the repository to read.")
    # No token is required up front: a public repository can be read without one.
    # If GitHub refuses, its own answer tells the person to add a token.
    token = (payload.token or "").strip() or _active_token()
    try:
        _use_github(repo, token, (payload.branch or "").strip())
    except ghub.GitHubError as exc:
        # Leave whatever was connected before in place, and say what went wrong.
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if payload.token and payload.token.strip():
        _state["token"] = payload.token.strip()
    return health()


@app.post("/api/repo/disconnect")
def repo_disconnect() -> dict:
    """Forget the token and go back to the folder on this machine."""
    _state["token"] = ""
    _state["error"] = ""
    _state["index"] = None
    _state["conn"] = None
    _state["source"] = "folder"
    _use_folder()
    return health()


def _extract(n: Notification, use_ai: bool) -> dict:
    _, _, cat = repo_state()
    rules = extract_by_rules(n, cat)
    if not (use_ai and settings.ai_available()):
        rules.setdefault("aiNote", "AI is off - fields were found by matching the repository catalogue.")
        return rules
    try:
        out = ai.read_email(n.text(), settings)
    except ai.AIUnavailable as exc:
        rules["warnings"] = list(rules.get("warnings", [])) + [
            f"The AI reader was unavailable ({exc}). Fields below were found without it."
        ]
        rules["aiNote"] = "AI unavailable - fell back to matching the repository catalogue."
        return rules
    # Keep the rules-based answers for anything the model left blank, and always
    # keep our own warnings about names that are not in the repository.
    for key in ("source", "changeType", "changeKind", "changeDesc", "subject",
                "effectiveDate", "pocName", "pocEmail", "pocTeam"):
        if not out.get(key):
            out[key] = rules.get(key, "")
    if not out.get("upstream"):
        out["upstream"] = rules.get("upstream", [])
    out["warnings"] = list(out.get("warnings") or []) + _unknown_name_warnings(out, cat)
    out["aiNote"] = f"Read by {settings.groq_model}. Check it before scanning."
    return out


def _unknown_name_warnings(vals: dict, cat: Catalog) -> list[str]:
    missing = [u["table"] for u in vals.get("upstream", []) if not cat.has_table(u["table"])]
    if missing:
        return [
            "Not found in the connected repository: " + ", ".join(missing)
            + ". Scanning will still run, but expect no results for those."
        ]
    return []


@app.post("/api/read-email")
async def read_email_file(file: UploadFile = File(...), useAI: str = "true") -> dict:
    raw = await file.read()
    if len(raw) > 25_000_000:
        raise HTTPException(status_code=413, detail="That file is too large.")
    n = read_upload(file.filename or "", raw)
    out = _extract(n, useAI.lower() == "true")
    out["emailPreview"] = {
        "subject": n.subject,
        "body": n.body[:4000],
        "fromName": n.from_name,
        "fromEmail": n.from_email,
        "attachments": n.attachments,
        "kind": n.source_kind,
    }
    return out


@app.post("/api/read-text")
def read_email_text(payload: PasteIn) -> dict:
    n = Notification(body=payload.text, source_kind="paste")
    out = _extract(n, payload.useAI)
    out["emailPreview"] = {
        "subject": n.subject, "body": n.body[:4000],
        "fromName": "", "fromEmail": "", "attachments": [], "kind": "paste",
    }
    return out


@app.post("/api/scan")
def scan(payload: ScanIn) -> dict:
    idx, parsed, _ = repo_state()
    upstream = [{"table": u.table, "attrs": u.attrs} for u in payload.upstream]
    if not upstream:
        raise HTTPException(status_code=400, detail="No upstream tables were supplied.")
    res = trace(idx, parsed, upstream, change_type=payload.changeKind, cfg=settings)
    out = res.to_dict()
    conn: ghub.Connection | None = _state["conn"]
    on_github = _state["source"] == "github" and conn is not None
    # A link is only offered when Ripple genuinely knows the address. On GitHub
    # it points at the exact commit that was read, not at whatever the branch
    # has moved on to since.
    out["repo"] = {
        "label": conn.ref.slug if on_github else settings.repo_label,
        "branch": conn.branch if on_github else settings.repo_branch,
        "urlTemplate": conn.url_template() if on_github else settings.repo_url_template,
    }
    return out


@app.post("/api/summary")
def summary(payload: SummaryIn) -> dict:
    base = narrative.summarise(payload.scan, payload.vals)
    reply = narrative.draft_reply(payload.scan, payload.vals, base)
    out = {"summary": base, "reply": reply}
    if not (payload.useAI and settings.ai_available()):
        return out
    trimmed = {
        "risk": payload.scan.get("risk"),
        "stats": payload.scan.get("stats"),
        "groups": [
            {
                "prod": g["prod"],
                "rows": [
                    {k: r[k] for k in ("inter", "attr", "alias", "logic", "mode", "impact",
                                       "breaking", "noLocalFix", "file")}
                    for r in g["rows"]
                ],
            }
            for g in payload.scan.get("groups", [])
        ],
        "couldNotRead": [u.get("file") for u in payload.scan.get("unreadable", [])],
        "change": {k: payload.vals.get(k) for k in
                   ("source", "changeType", "changeDesc", "effectiveLabel", "pocName", "pocTeam")},
        "upstream": payload.vals.get("upstream", []),
    }
    try:
        out["summary"] = {**base, **ai.write_summary(trimmed, settings)}
        out["reply"] = {**reply, **ai.write_reply({**trimmed, "summary": out["summary"]}, settings)}
    except ai.AIUnavailable as exc:
        out["aiNote"] = f"AI unavailable ({exc}). Written without it."
    return out


@app.post("/api/history")
def save_analysis(payload: SaveIn) -> dict:
    return store.save(payload.vals, payload.scan, payload.summary, payload.mode, settings)


@app.get("/api/history")
def history() -> list[dict]:
    return store.listing(settings)


@app.get("/api/history/{analysis_id}")
def history_item(analysis_id: int) -> dict:
    row = store.get(analysis_id, settings)
    if not row:
        raise HTTPException(status_code=404, detail="Not found.")
    return row


@app.patch("/api/history/{analysis_id}")
def history_status(analysis_id: int, payload: StatusIn) -> dict:
    if not store.set_status(analysis_id, payload.status, settings):
        raise HTTPException(status_code=400, detail="Unknown status or id.")
    return {"ok": True}


@app.get("/api/file")
def file_content(path: str) -> dict:
    """The real text of a scanned file, so a finding can be opened in place."""
    idx, _, _ = repo_state()
    f = idx.get(path)
    if f is None:
        raise HTTPException(status_code=404, detail="Not in the index.")
    return {"path": f.path, "lang": f.lang, "lines": f.text.splitlines()}


# ── static site ────────────────────────────────────────────────────────────
@app.middleware("http")
async def no_cache_static(request, call_next):
    """Browsers hold on to app.js hard. During a demo or an edit that means you
    stare at yesterday's page and think the change did not work."""
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-store, must-revalidate"
    return response


if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(WEB_DIR / "index.html")
else:  # pragma: no cover
    @app.get("/")
    def index() -> JSONResponse:
        return JSONResponse({"error": "web folder missing"}, status_code=500)
