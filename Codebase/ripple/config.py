"""Settings for a Ripple installation.

Everything that would differ between a laptop, a demo host and a real corporate
network lives here, so nothing has to be hunted for in code.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .production import (           # noqa: F401  (re-exported for older callers)
    DEFAULT_PRODUCTION,
    DEFAULT_TEXT as DEFAULT_PRODUCTION_TEXT,
    ProductionRule,
    parse as parse_production_text,
    parse_production_rule,
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Which tables are the ones this team publishes -- the tables a finding has to
# reach before anybody outside the team notices. Every organisation names them
# differently, and getting this wrong is the most expensive mistake Ripple can
# make: a change that really breaks three tables is reported as "no impact"
# purely because the tables are not called _PROD. So it is a setting, it is on
# screen, and findings that reach nothing on this list are still shown.
#
# Two shapes are accepted, side by side. A pasted list of the real table names
# is read as written -- that is the answer rather than a guess about it. A
# pattern is still a pattern, unchanged: a word beginning with an underscore
# matches the end of a table name (_PROD, _UMDL, _PUBLISHED), and one with a *
# is matched in full, so PROD_* works too and * on its own means every table.
# See ripple/production.py for how a paste is read.

# The models Ripple offers on the Settings screen. Only Groq's production
# models are listed -- preview ones get withdrawn without notice, and a model
# that disappears mid-demo is worse than one that is merely adequate.
#
# The job is narrow: pull table and attribute names out of a forwarded, badly
# quoted email and return strict JSON, then write a few careful sentences from
# findings that are already worked out. That rewards instruction-following, not
# breadth -- which is why the largest model is the default and the fastest one
# carries a warning rather than being hidden.
AI_MODELS: tuple[dict[str, str], ...] = (
    {
        "id": "openai/gpt-oss-120b",
        "label": "GPT-OSS 120B",
        "note": "Best at reading a messy forwarded email. Recommended.",
    },
    {
        "id": "llama-3.3-70b-versatile",
        "label": "Llama 3.3 70B",
        "note": "A solid all-rounder, and a little quicker.",
    },
    {
        "id": "openai/gpt-oss-20b",
        "label": "GPT-OSS 20B",
        "note": "Lighter and faster. Fine for tidy notifications.",
    },
    {
        "id": "llama-3.1-8b-instant",
        "label": "Llama 3.1 8B",
        "note": "Fastest. Misses fields in awkward emails -- check its answers.",
    },
)

DEFAULT_AI_MODEL = AI_MODELS[0]["id"]


def model_label(model_id: str) -> str:
    """The friendly name for a model id, or the id itself if it is not ours."""
    for m in AI_MODELS:
        if m["id"] == model_id:
            return m["label"]
    return model_id


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default).strip()


def _env_any(names: tuple[str, ...], default: str = "") -> str:
    """First of several environment variables that is actually set."""
    for n in names:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return default


def _serverless() -> bool:
    return bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))


def _default_db() -> str:
    if os.environ.get("RIPPLE_DB"):
        return os.environ["RIPPLE_DB"].strip()
    return "/tmp/ripple.db" if _serverless() else str(BASE_DIR / "ripple.db")


@dataclass
class Settings:
    # ── is this a serverless host? ─────────────────────────────────────────
    # Vercel, Lambda and friends impose limits a laptop does not: the disk is
    # read-only apart from /tmp, the machine is thrown away between requests,
    # a request body cannot exceed about 4.5 MB, and a request is killed at
    # 60 seconds. Several defaults below change because of that, so the app
    # says what it will really do instead of promising laptop behaviour.
    serverless: bool = field(default_factory=_serverless)

    # ── where the code comes from ──────────────────────────────────────────
    # "folder" reads a directory on this machine. "github" pulls a repository
    # over the network with an access token. Either can be chosen on screen.
    repo_source: str = field(default_factory=lambda: _env("RIPPLE_REPO_SOURCE", "folder"))

    # ── which repository is scanned (folder mode) ──────────────────────────
    repo_path: Path = field(
        default_factory=lambda: Path(_env("RIPPLE_REPO", str(BASE_DIR / "mockrepo")))
    )
    repo_label: str = field(default_factory=lambda: _env("RIPPLE_REPO_LABEL", "mockrepo"))
    repo_branch: str = field(default_factory=lambda: _env("RIPPLE_REPO_BRANCH", "main"))

    # ── GitHub mode ────────────────────────────────────────────────────────
    # The token is a secret. It is only ever sent to GitHub as a header; it is
    # never logged, never saved to disk, and never returned by any route.
    github_repo: str = field(default_factory=lambda: _env("RIPPLE_GITHUB_REPO", ""))
    github_branch: str = field(default_factory=lambda: _env("RIPPLE_GITHUB_BRANCH", ""))
    github_token: str = field(
        default_factory=lambda: _env_any(("RIPPLE_GITHUB_TOKEN", "GITHUB_TOKEN"))
    )
    github_api: str = field(default_factory=lambda: _env("RIPPLE_GITHUB_API", "https://api.github.com"))
    github_timeout: float = field(default_factory=lambda: float(_env("RIPPLE_GITHUB_TIMEOUT", "30")))
    # How much compressed repository Ripple will pull in one go. Lower on a
    # serverless host, where the whole request is killed at 60 seconds: a clear
    # "that repository is too big for this host" beats a blank timeout.
    max_repo_bytes: int = field(
        default_factory=lambda: int(
            _env("RIPPLE_MAX_REPO_BYTES", "25000000" if _serverless() else "60000000")
        )
    )

    # Link template so a finding can jump to the real file. {path} and {line}
    # are filled in. Point this at your own Git host when you get there.
    repo_url_template: str = field(
        default_factory=lambda: _env("RIPPLE_REPO_URL_TEMPLATE", "")
    )

    # ── how the SQL is read ────────────────────────────────────────────────
    # One of: oracle, teradata, snowflake, hive, spark, postgres, mysql, tsql,
    # duckdb, bigquery, redshift, databricks, presto, trino, sqlite, "" (generic).
    sql_dialect: str = field(default_factory=lambda: _env("RIPPLE_SQL_DIALECT", ""))

    # How many renames deep to follow a column.
    max_hops: int = field(default_factory=lambda: int(_env("RIPPLE_MAX_HOPS", "4")))

    # Which tables count as the ones this team publishes. See the note at the
    # top of this file for why this is a setting and not a constant.
    #
    # Two fields, and both matter. ``production_patterns`` is what is matched
    # against: every entry Ripple recognised, whether a real table name or a
    # pattern. ``production_text`` is what was actually pasted, kept exactly as
    # it arrived so the box can be opened and edited again rather than being
    # handed back a tidied-up version of somebody's list.
    production_patterns: tuple[str, ...] = field(
        default_factory=lambda: parse_production_rule(_env("RIPPLE_PROD_TABLES", ""))
        or DEFAULT_PRODUCTION
    )
    production_text: str = field(
        default_factory=lambda: _env("RIPPLE_PROD_TABLES", "") or DEFAULT_PRODUCTION_TEXT
    )

    # File types worth reading at all.
    code_extensions: tuple[str, ...] = (
        ".sql", ".ddl", ".hql", ".py", ".scala", ".java", ".sh", ".xml", ".yaml", ".yml",
    )
    # Never walk into these.
    skip_dirs: tuple[str, ...] = (
        ".git", ".venv", "venv", "node_modules", "__pycache__", "target", "build", "dist",
    )
    max_file_bytes: int = 2_000_000

    # The biggest email file that can be uploaded. A serverless host refuses a
    # request body over roughly 4.5 MB before Ripple ever sees it, so the limit
    # on screen has to be the real one, not a friendlier invented one.
    max_upload_bytes: int = field(
        default_factory=lambda: int(
            _env("RIPPLE_MAX_UPLOAD_BYTES", "4000000" if _serverless() else "25000000")
        )
    )

    # ── AI (entirely optional) ─────────────────────────────────────────────
    groq_api_key: str = field(default_factory=lambda: _env("GROQ_API_KEY", ""))
    groq_model: str = field(default_factory=lambda: _env("GROQ_MODEL", DEFAULT_AI_MODEL))
    groq_base_url: str = field(
        default_factory=lambda: _env("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    )
    # How long to wait for the model. Writing the summary makes two calls one
    # after the other, so on a serverless host both have to finish inside the
    # 60-second cap -- otherwise the page dies with no explanation instead of
    # falling back to the written-without-AI version.
    ai_timeout: float = field(
        default_factory=lambda: float(_env("RIPPLE_AI_TIMEOUT", "20" if _serverless() else "45"))
    )

    # ── storage ────────────────────────────────────────────────────────────
    # Serverless hosts give you a read-only filesystem apart from /tmp, and even
    # that is wiped between runs -- so on Vercel, history is per-session only.
    db_path: Path = field(default_factory=lambda: Path(_default_db()))

    def ai_available(self) -> bool:
        return bool(self.groq_api_key)

    # ── the published-table rule ───────────────────────────────────────────
    def production(self) -> ProductionRule:
        """The rule, read. Rebuilt only when the entries themselves change.

        Asked once per table visited on every hop of every scan, and a real
        list is hundreds of names long, so the answer is worked out once and
        kept rather than re-parsed each time.
        """
        entries = tuple(self.production_patterns)
        cached = getattr(self, "_production_cache", None)
        if cached is None or cached[0] != entries:
            rule = ProductionRule(text=self.production_text,
                                  entries=parse_production_text(
                                      "\n".join(entries)).entries)
            object.__setattr__(self, "_production_cache", (entries, rule))
            return rule
        return cached[1]

    def set_production(self, text: str) -> ProductionRule:
        """Take a pasted list, in whatever shape it arrived. Returns what was read.

        An empty box would mean "no table is ever production", which reports
        every repository as clean whatever it does. Falling back to the shipped
        default is the only safe reading of one.
        """
        rule = parse_production_text(text or "")
        if rule.is_empty():
            rule = parse_production_text(DEFAULT_PRODUCTION_TEXT)
            self.production_text = DEFAULT_PRODUCTION_TEXT
        else:
            self.production_text = str(text or "")
        self.production_patterns = tuple(e.given for e in rule.entries)
        object.__setattr__(self, "_production_cache",
                           (self.production_patterns, rule))
        return rule

    def is_production_table(self, table: str) -> bool:
        return self.production().matches(table)

    def production_rule(self) -> str:
        """The rule as one short line, for a status row rather than a screen.

        Two hundred pasted table names do not fit on a line, and pretending
        otherwise produces a row of dots that says nothing. A long list is
        counted instead; a short one is still shown in full.
        """
        return self.production().one_line()


settings = Settings()
