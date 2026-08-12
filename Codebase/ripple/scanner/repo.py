"""Reading the repository and finding candidate files.

Step one of a scan is deliberately dumb and fast: find every file that so much
as mentions the name. Understanding what the mention *means* happens later.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from ..config import Settings, settings as default_settings

# Which files carry SQL inside string literals rather than being SQL themselves.
EMBEDDED_SQL_EXTS = {".py", ".scala", ".java", ".sh"}

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

    @classmethod
    def build(cls, root: Path | str, cfg: Settings | None = None) -> "RepoIndex":
        cfg = cfg or default_settings
        root = Path(root)
        idx = cls(root=root)
        if not root.exists():
            idx.skipped.append({"file": str(root), "reason": "repository folder not found"})
            return idx

        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            # Judged on the path *inside* the repository, never the whole path.
            # Otherwise a repository that merely happens to live under a folder
            # called build, dist, target or venv has every one of its files
            # skipped, and the scan comes back clean because it read nothing.
            relative = p.relative_to(root)
            if any(part in cfg.skip_dirs for part in relative.parts):
                continue
            ext = p.suffix.lower()
            if ext not in cfg.code_extensions:
                continue
            rel = relative.as_posix()
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
            except Exception as exc:  # pragma: no cover - defensive
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
