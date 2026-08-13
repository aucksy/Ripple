"""Reading the repository and finding candidate files.

Step one of a scan is deliberately dumb and fast: find every file that so much
as mentions the name. Understanding what the mention *means* happens later.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from ..config import Settings, settings as default_settings

# Which files carry SQL inside string literals rather than being SQL themselves.
EMBEDDED_SQL_EXTS = {".py", ".scala", ".java", ".sh"}

# ── files that are not really on this machine ──────────────────────────────
# OneDrive's Files On-Demand leaves a file in the folder listing, with its real
# name and its real size, when the contents are still in the cloud. It looks
# exactly like a file. Opening it asks OneDrive to fetch it, which needs the
# network -- and Ripple Offline is for a machine that has none.
#
# This is the most dangerous thing that can happen to a scan. A repository half
# of which was never read comes back with a short finding list and a green tick,
# and the whole point of this tool is that the green tick can be trusted. So
# these are found before anything is opened, counted, and said out loud.
FILE_ATTRIBUTE_OFFLINE = 0x1000
FILE_ATTRIBUTE_RECALL_ON_OPEN = 0x40000
FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x400000

# The two recall flags are set by the cloud provider itself and mean one thing
# only: the contents are not here. OFFLINE is older and much looser -- some
# backup software sets it on files that are perfectly local -- so on its own it
# is treated as a suspicion, and the file is still opened. Refusing to read a
# repository because a backup tool touched a flag would be its own disaster.
_DEFINITELY_ONLINE_ONLY = FILE_ATTRIBUTE_RECALL_ON_OPEN | FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS

ONLINE_ONLY_REASON = "not really on this machine - OneDrive is holding it online-only"

# Windows still refuses a path over 260 characters unless long path support has
# been switched on, and on a managed office laptop it usually has not been. His
# real folders are about 140 characters before the filename even starts, so this
# is not a theoretical limit. Prefixing the root with \\?\ opts this walk out of
# the limit whatever the machine is set to.
_LONG_PATH_LIMIT = 260


def _walk_root(root: Path) -> Path:
    """The same folder, in the form Windows will walk past 260 characters."""
    if os.name != "nt":
        return root
    text = str(root)
    if text.startswith("\\\\?\\"):
        return root
    absolute = os.path.abspath(text)
    if absolute.startswith("\\\\"):                 # \\server\share\...
        return Path("\\\\?\\UNC\\" + absolute[2:])
    return Path("\\\\?\\" + absolute)


def online_only(p: Path) -> int:
    """Which placeholder flags this file carries, or 0 for an ordinary file."""
    if os.name != "nt":
        return 0
    try:
        attrs = p.stat().st_file_attributes            # type: ignore[attr-defined]
    except (OSError, AttributeError):
        return 0
    return attrs & (_DEFINITELY_ONLINE_ONLY | FILE_ATTRIBUTE_OFFLINE)


def _looks_like_a_cloud_error(exc: BaseException) -> bool:
    """Did this read fail because the file was still in the cloud?

    Matched on the words Windows itself uses rather than on error numbers, so a
    number remembered wrongly cannot turn a real problem into a reassuring one.
    """
    return "cloud" in str(exc).lower()

LANG_BY_EXT = {
    ".sql": "SQL",
    ".ddl": "SQL",
    ".hql": "Hive SQL",
    # "Python", not "Spark SQL": a .py file here might be a Spark job, a
    # BigQuery job or neither, and guessing wrong is visible on screen.
    ".py": "Python",
    ".scala": "Scala",
    ".java": "Java",
    ".sh": "Shell",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
}


@dataclass
class SourceFile:
    path: str            # repo-relative, forward slashes
    abs_path: Path
    text: str
    lang: str

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()


@dataclass
class Match:
    file: str
    line_no: int
    line: str
    name: str


@dataclass
class RepoIndex:
    """Every readable file in the repository, held in memory.

    The mock repository is tiny. A real one is bigger but still small compared
    with the memory on any server -- text compresses extremely well and we only
    keep files with an extension we can do something with.
    """

    files: list[SourceFile] = field(default_factory=list)
    skipped: list[dict] = field(default_factory=list)
    root: Path | None = None
    # Files OneDrive is keeping in the cloud, which is a different thing from a
    # file that would not parse and needs saying differently.
    held_online: list[str] = field(default_factory=list)
    # Files whose path went past what Windows will open on this machine.
    too_long: list[str] = field(default_factory=list)

    @classmethod
    def build(cls, root: Path | str, cfg: Settings | None = None,
              on_progress=None) -> "RepoIndex":
        """Read the repository. ``on_progress(done, total, label)`` is called as
        it goes, with real counts -- a repository this size takes minutes, and a
        screen that says nothing for four of them looks broken."""
        cfg = cfg or default_settings
        root = Path(root)
        idx = cls(root=root)
        if not root.exists():
            idx.skipped.append({"file": str(root), "reason": "repository folder not found"})
            return idx

        walk = _walk_root(root)
        candidates = [p for p in sorted(walk.rglob("*")) if p.is_file()]
        total = len(candidates)
        for seen, p in enumerate(candidates, start=1):
            if on_progress is not None and (seen % 25 == 0 or seen == total):
                on_progress(seen, total, "Reading the files")
            # Judged on the path *inside* the repository, never the whole path.
            # Otherwise a repository that merely happens to live under a folder
            # called build, dist, target or venv has every one of its files
            # skipped, and the scan comes back clean because it read nothing.
            relative = p.relative_to(walk)
            if any(part in cfg.skip_dirs for part in relative.parts):
                continue
            ext = p.suffix.lower()
            if ext not in cfg.code_extensions:
                continue
            rel = relative.as_posix()

            # Held in the cloud: do not open it. Opening asks OneDrive to fetch
            # it, which on a machine with no network hangs and then fails, once
            # per file -- and there can be thousands.
            # Counted here and nowhere else. A file that was never opened is not
            # a file to "check by hand" -- there is nothing on this machine to
            # open. Listing it in both places counts two problems where there is
            # one, and tells somebody to go and read a file that is not there.
            flags = online_only(p)
            if flags & _DEFINITELY_ONLINE_ONLY:
                idx.held_online.append(rel)
                continue

            try:
                size = p.stat().st_size
                if size > cfg.max_file_bytes:
                    idx.skipped.append(
                        {"file": rel, "reason": f"file is {size // 1024} KB - too large to read"}
                    )
                    continue
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    text = p.read_text(encoding="latin-1")
                except Exception as exc:  # pragma: no cover - defensive
                    idx.skipped.append({"file": rel, "reason": f"could not decode ({exc})"})
                    continue
            except Exception as exc:
                # A read that fails on a file already flagged OFFLINE, or that
                # fails with Windows' own cloud wording, is the same problem as
                # above -- said in the same words rather than as an error code
                # nobody can act on.
                if flags or _looks_like_a_cloud_error(exc):
                    idx.held_online.append(rel)
                elif len(str(p)) > _LONG_PATH_LIMIT:
                    idx.too_long.append(rel)
                else:
                    idx.skipped.append({"file": rel, "reason": f"could not open ({exc})"})
                continue
            idx.files.append(
                SourceFile(path=rel, abs_path=p, text=text, lang=LANG_BY_EXT.get(ext, "Text"))
            )
        return idx

    # ── searching ──────────────────────────────────────────────────────────
    @staticmethod
    def _pattern(names: list[str]) -> re.Pattern:
        parts = sorted({re.escape(n) for n in names if n}, key=len, reverse=True)
        if not parts:
            return re.compile(r"(?!x)x")  # matches nothing
        return re.compile(r"\b(" + "|".join(parts) + r")\b", re.IGNORECASE)

    def search(self, names: list[str]) -> list[Match]:
        """Every line mentioning any of these names, as whole words."""
        pat = self._pattern(names)
        out: list[Match] = []
        for f in self.files:
            if not pat.search(f.text):
                continue
            for i, line in enumerate(f.lines, start=1):
                m = pat.search(line)
                if m:
                    out.append(Match(file=f.path, line_no=i, line=line.rstrip(), name=m.group(1)))
        return out

    def files_mentioning(self, names: list[str]) -> list[SourceFile]:
        pat = self._pattern(names)
        return [f for f in self.files if pat.search(f.text)]

    def get(self, path: str) -> SourceFile | None:
        for f in self.files:
            if f.path == path:
                return f
        return None


# ── pulling SQL out of programs that build it as text ──────────────────────
_TRIPLE = re.compile(r'("""|\'\'\')(?P<body>.*?)\1', re.DOTALL)
_SINGLE = re.compile(r'"(?P<body>[^"\n]{40,})"|\'(?P<body2>[^\'\n]{40,})\'')
_LOOKS_SQL = re.compile(
    r"\b(SELECT|INSERT\s+INTO|CREATE\s+TABLE|CREATE\s+OR\s+REPLACE|MERGE\s+INTO|UPDATE)\b",
    re.IGNORECASE,
)


def extract_sql_blocks(f: SourceFile) -> list[tuple[str, int]]:
    """Return (sql_text, line_offset) for SQL found inside a program file.

    line_offset is the 0-based line number in the file where the block starts,
    so findings can still point at a real line in the real file.
    """
    blocks: list[tuple[str, int]] = []
    for m in _TRIPLE.finditer(f.text):
        body = m.group("body")
        if _LOOKS_SQL.search(body):
            offset = f.text[: m.start("body")].count("\n")
            blocks.append((body, offset))
    for m in _SINGLE.finditer(f.text):
        body = m.group("body") or m.group("body2") or ""
        if _LOOKS_SQL.search(body):
            start = m.start("body") if m.group("body") else m.start("body2")
            offset = f.text[:start].count("\n")
            blocks.append((body, offset))
    return blocks


def statements_for(f: SourceFile) -> list[tuple[str, int]]:
    """SQL statements in a file, with the line each one starts on."""
    ext = f.abs_path.suffix.lower()
    if ext in EMBEDDED_SQL_EXTS:
        return extract_sql_blocks(f)
    return [(f.text, 0)]


# ── a program that runs SQL kept somewhere else ────────────────────────────
# His pipeline has two folders of Airflow DAGs. Some hold their SQL as a string,
# which is read above. Plenty of others name a .sql file and run that -- either
# by opening it, or by handing Airflow a filename and letting template_searchpath
# find it. Ripple got nothing out of those files and said nothing about them, so
# a DAG that runs the most important query in the pipeline looked identical to an
# empty file.
#
# Both shapes come down to the same thing: a string ending in .sql.
_SQL_FILE_REF = re.compile(r"""["']([^"'\n]*?[A-Za-z0-9_\-]+\.sql)["']""")


def sql_file_refs(f: SourceFile) -> list[dict]:
    """Every .sql file this program names, with the line it names it on."""
    if f.abs_path.suffix.lower() not in EMBEDDED_SQL_EXTS:
        return []
    out: list[dict] = []
    seen: set[str] = set()
    for m in _SQL_FILE_REF.finditer(f.text):
        ref = m.group(1).strip()
        if not ref or ref.lower() in seen:
            continue
        seen.add(ref.lower())
        out.append({"ref": ref, "line": f.text[: m.start()].count("\n") + 1})
    return out


def looks_like_unread_sql(f: SourceFile, blocks: list[tuple[str, int]]) -> bool:
    """SQL is plainly written in this file, and none of it could be taken out.

    The shape that does this is SQL built by adding short strings together --
    no single piece long enough to be recognised, and the statement never
    existing as text anywhere. Worth reporting, because the alternative is a
    file with a CREATE TABLE in it that Ripple treats as empty.
    """
    if f.abs_path.suffix.lower() not in EMBEDDED_SQL_EXTS or blocks:
        return False
    return bool(_LOOKS_SQL.search(f.text))


# A Spark or Scala job usually runs a bare SELECT and then writes the result
# from the surrounding program, not from SQL. Without this the chain stops dead
# at the job -- which is exactly where the interesting renames tend to happen.
_WRITE_TARGET = re.compile(
    r"""(?:saveAsTable|insertInto|createOrReplaceTempView|registerTempTable)\s*\(\s*["']([A-Za-z0-9_.]+)["']""",
    re.IGNORECASE,
)

# The same problem in the BigQuery world. A Python job there runs a bare SELECT
# and names its destination in the job settings, not in the SQL -- so without
# this the chain stops at the job, exactly as it would for Spark. Project ids
# may contain hyphens, hence the wider character set.
_BQ_WRITE_TARGET = re.compile(
    r"""(?:destination(?:_table)?\s*=\s*["']([A-Za-z0-9_.\-]+)["']"""
    r"""|to_gbq\s*\(\s*["']([A-Za-z0-9_.\-]+)["'])""",
    re.IGNORECASE,
)


def written_tables(f: SourceFile) -> list[str]:
    """Tables a program file writes to, in the order they appear."""
    if f.abs_path.suffix.lower() not in EMBEDDED_SQL_EXTS:
        return []
    hits: list[tuple[int, str]] = []
    for pat in (_WRITE_TARGET, _BQ_WRITE_TARGET):
        for m in pat.finditer(f.text):
            raw = next((g for g in m.groups() if g), "")
            if raw:
                hits.append((m.start(), raw.split(".")[-1]))
    out: list[str] = []
    for _, name in sorted(hits):          # order they appear in the file
        if name not in out:
            out.append(name)
    return out
