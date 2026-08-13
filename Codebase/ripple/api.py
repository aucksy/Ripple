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

from dataclasses import replace

from . import ai, narrative, progress, store
from .catalog import Catalog, build_catalog
from .config import AI_MODELS, Settings, model_label, settings
from .notification import Notification, extract_by_rules, read_pasted, read_upload
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
    # The AI key is a secret on exactly the same terms as the GitHub token:
    # held here while the process runs, and nowhere else, ever.
    "aiKey": "", "aiModel": "",
}


def _active_token() -> str:
    """A token typed into the app wins over one set in the environment."""
    return _state["token"] or settings.github_token


def _ai_cfg() -> Settings:
    """Settings as the AI should see them, with anything typed in applied.

    A copy is made rather than the global being edited, so a key entered on the
    screen can be forgotten again by clearing one value -- and so nothing else
    in the app can accidentally read it.
    """
    return replace(
        settings,
        groq_api_key=_state["aiKey"] or settings.groq_api_key,
        groq_model=_state["aiModel"] or settings.groq_model,
    )


def _ai_facts() -> dict:
    """What the screen may know about the AI -- never the key itself."""
    cfg = _ai_cfg()
    return {
        "available": cfg.ai_available(),
        "model": cfg.groq_model,
        "modelLabel": model_label(cfg.groq_model),
        # Where the key came from, so "it stopped working" has an explanation.
        "keyFrom": "entered" if _state["aiKey"] else ("environment" if settings.groq_api_key else ""),
        "models": list(AI_MODELS),
        # A key typed in here dies with the machine, and while it lives anyone
        # else using this copy of Ripple is spending it. The screen says both.
        "keyLasts": not settings.serverless,
    }


def _install(idx: RepoIndex, source: str, conn: "ghub.Connection | None") -> None:
    parsed = parse_repo(idx, settings, on_progress=progress.reader("parsing"))
    _state.update({
        "index": idx, "parsed": parsed, "catalog": build_catalog(parsed),
        "source": source, "conn": conn,
    })
    progress.finish()


def _use_folder() -> None:
    idx = RepoIndex.build(settings.repo_path, settings,
                          on_progress=progress.reader("reading"))
    _install(idx, "folder", None)


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


class AIKeyIn(BaseModel):
    key: str = ""            # blank means keep whatever is already set
    model: str = ""          # blank means keep the model already selected


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
        "serverless": settings.serverless,
        # The real ceilings on this host, so the screen never promises more than
        # it can do. On a laptop these are generous; on Vercel they are not.
        "limits": {
            "maxUploadBytes": settings.max_upload_bytes,
            "maxRepoBytes": settings.max_repo_bytes,
            "historyKept": not settings.serverless,
        },
        "repo": {
            "label": gh["slug"] if on_github else settings.repo_label,
            "branch": gh["branch"] if on_github else settings.repo_branch,
            "path": gh["webUrl"] if on_github else str(settings.repo_path),
            "files": len(idx.files),
            "statements": len(parsed.statements),
            "unreadable": len(parsed.unreadable),
            # Files never opened at all. Shown next to the file count, because
            # "1,770 files read" beside "412 never opened" is a different
            # sentence from "1,770 files read".
            "heldOnline": len(idx.held_online),
            "pathTooLong": len(idx.too_long),
            # Programs that run SQL kept in a separate .sql file. Two folders of
            # DAGs are written that way, and without this they read as empty.
            "runsSqlFrom": len([r for r in parsed.runs_sql_from if r["runs"]]),
            "exists": True if on_github else settings.repo_path.exists(),
            "kinds": [
                {"lang": k, "files": n}
                for k, n in sorted(kinds.items(), key=lambda kv: (-kv[1], kv[0]))
            ],
        },
        "catalog": {"tables": len(cat.tables), "columns": sum(len(v) for v in cat.tables.values())},
        "sqlDialect": settings.sql_dialect or "generic",
        "maxHops": settings.max_hops,
        # Which table names count as the ones this team publishes. On screen so
        # that "no production table is impacted" can be checked rather than
        # believed -- it is only ever as true as this rule is.
        "production": settings.production_rule(),
        "ai": _ai_facts(),
    }


@app.get("/api/progress")
def progress_now() -> dict:
    """What Ripple is doing this second.

    Asked for by the screen while it waits. Every number is counted rather than
    estimated, and where there is genuinely no total it says so rather than
    drawing a bar over a number nobody knows.
    """
    return progress.snapshot()


@app.get("/api/catalog")
def catalog() -> dict:
    _, _, cat = repo_state()
    return cat.to_dict()


@app.post("/api/ai/check")
def ai_check() -> dict:
    """Really call the model that is really selected, and say which one.

    A key that is present is not the same as a key that works, and a key that
    works with one model can be refused by another. The only honest check is
    the round trip.
    """
    return ai.check_key(_ai_cfg())


@app.post("/api/ai/connect")
def ai_connect(payload: "AIKeyIn") -> dict:
    """Turn the AI on from the screen, without touching the environment.

    The key is held in this process and nowhere else: not written to disk, not
    logged, and not returned by this or any other route.
    """
    model = (payload.model or "").strip()
    if model and model not in {m["id"] for m in AI_MODELS}:
        raise HTTPException(status_code=400, detail="That is not a model Ripple offers.")
    key = (payload.key or "").strip()
    if not key and not settings.groq_api_key:
        raise HTTPException(status_code=400, detail="Enter a Groq API key to turn the AI on.")
    if key:
        _state["aiKey"] = key
    if model:
        _state["aiModel"] = model
    # Prove it works now rather than at the worst moment. A key the model
    # provider refuses is reported straight back, and is not kept.
    result = ai.check_key(_ai_cfg())
    if not result.get("ok") and key:
        _state["aiKey"] = ""
        raise HTTPException(status_code=502, detail=result.get("reason", "The key did not work."))
    return health()


@app.post("/api/ai/forget")
def ai_forget() -> dict:
    """Forget a key typed into the screen. One set in the environment stays."""
    _state["aiKey"] = ""
    _state["aiModel"] = ""
    return health()


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
    cfg = _ai_cfg()
    rules = extract_by_rules(n, cat)
    if not (use_ai and cfg.ai_available()):
        rules.setdefault("aiNote", "AI is off - fields were found by matching the repository catalogue.")
        return rules
    try:
        out = ai.read_email(n.text(), cfg)
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
    out["aiNote"] = f"Read by {model_label(cfg.groq_model)}. Check it before scanning."
    return out


def _unknown_name_warnings(vals: dict, cat: Catalog) -> list[str]:
    missing = [u["table"] for u in vals.get("upstream", []) if not cat.has_table(u["table"])]
    if missing:
        return [
            "Not found in the connected repository: " + ", ".join(missing)
            + ". Scanning will still run, but expect no results for those."
        ]
    return []


def _too_big(size: int) -> str:
    """Say what the real ceiling is, and why it is that number."""
    # One decimal on the file, none on the limit -- otherwise a 4.4 MB file
    # reads as "that file is 4 MB, the most accepted is 4 MB", which is absurd.
    msg = (f"That file is {size / 1_000_000:.1f} MB. The most this copy of Ripple "
           f"accepts is {settings.max_upload_bytes / 1_000_000:.0f} MB.")
    if settings.serverless:
        msg += (" This copy runs on a serverless host, which refuses anything bigger"
                " before Ripple sees it. Save the email as .eml and try again, or"
                " paste the text instead.")
    return msg


@app.post("/api/read-email")
async def read_email_file(file: UploadFile = File(...), useAI: str = "true") -> dict:
    raw = await file.read()
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail=_too_big(len(raw)))
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
    n = read_pasted(payload.text)
    out = _extract(n, payload.useAI)
    out["emailPreview"] = {
        "subject": n.subject, "body": n.body[:4000],
        "fromName": n.from_name, "fromEmail": n.from_email,
        "attachments": [], "kind": "paste",
    }
    return out


@app.post("/api/scan")
def scan(payload: ScanIn) -> dict:
    idx, parsed, _ = repo_state()
    upstream = [{"table": u.table, "attrs": u.attrs} for u in payload.upstream]
    if not upstream:
        raise HTTPException(status_code=400, detail="No upstream tables were supplied.")
    try:
        res = trace(idx, parsed, upstream, change_type=payload.changeKind, cfg=settings,
                    on_progress=progress.reader("scanning"))
    finally:
        progress.finish()
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
    cfg = _ai_cfg()
    base = narrative.summarise(payload.scan, payload.vals)
    reply = narrative.draft_reply(payload.scan, payload.vals, base)
    out = {"summary": base, "reply": reply}
    if not (payload.useAI and cfg.ai_available()):
        return out
    def _trim(groups: list[dict]) -> list[dict]:
        return [
            {
                "prod": g["prod"],
                "rows": [
                    {k: r[k] for k in ("inter", "attr", "alias", "logic", "mode", "impact",
                                       "breaking", "noLocalFix", "file")}
                    for r in g["rows"]
                ],
            }
            for g in groups
        ]

    trimmed = {
        "risk": payload.scan.get("risk"),
        "stats": payload.scan.get("stats"),
        "groups": _trim(payload.scan.get("groups", [])),
        # Sent as well, or the model writes "no impact" over a list of findings
        # that simply did not match the production naming rule.
        "reachedButNotOnTheProductionList": _trim(payload.scan.get("reached", [])),
        "couldNotRead": [u.get("file") for u in payload.scan.get("unreadable", [])],
        "change": {k: payload.vals.get(k) for k in
                   ("source", "changeType", "changeDesc", "effectiveLabel", "pocName", "pocTeam")},
        "upstream": payload.vals.get("upstream", []),
    }
    try:
        out["summary"] = {**base, **ai.write_summary(trimmed, cfg)}
        out["reply"] = {**reply, **ai.write_reply({**trimmed, "summary": out["summary"]}, cfg)}
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
async def cache_rules(request, call_next):
    """Browsers hold on to app.js hard. During a demo or an edit that means you
    stare at yesterday's page and think the change did not work -- so the page
    and its script are never cached.

    The font files are the exception. They are 350 KB together and they do not
    change. On a hosted copy there is no separate web server for them: every
    request runs the app itself, so refusing to cache them means re-serving a
    third of a megabyte on every page view. A month is long enough to help and
    short enough that a replaced font is not stuck forever.
    """
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/static/fonts/") and path.endswith(".woff2"):
        response.headers["Cache-Control"] = "public, max-age=2592000, s-maxage=2592000"
    elif path.startswith("/static") or path == "/":
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
