"""Reading the impact notification.

Two ways in, and both end at the same editable form:

* upload a saved Outlook message, or paste the text
* type the tables and attributes yourself (manual mode)

Extraction never has the last word. Whatever comes out of here is shown to a
human to correct before a single file is scanned.
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from datetime import date, datetime

from .catalog import Catalog

# A table or column name as people actually write them in these emails.
IDENT = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")

DATE_PATTERNS = [
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "%Y-%m-%d"),
    (re.compile(r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b", re.I), None),
    (re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s*(\d{4})?\b", re.I), None),
]
MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}

CHANGE_HINTS = [
    (("decommission", "removed", "removal", "dropped", "retire", "sunset"), "removal", "Attribute decommission"),
    (("renamed", "rename"), "rename", "Attribute rename"),
    (("format", "value", "iso", "full country"), "value_change", "Value format change"),
    (("data type", "datatype", "length", "precision", "varchar", "widened"), "type_change", "Data type change"),
]


@dataclass
class Notification:
    subject: str = ""
    body: str = ""
    from_name: str = ""
    from_email: str = ""
    attachments: list[str] = field(default_factory=list)
    source_kind: str = "paste"          # msg | eml | paste | manual
    warnings: list[str] = field(default_factory=list)

    def text(self) -> str:
        return f"{self.subject}\n\n{self.body}"


# ── getting the words out of the file ──────────────────────────────────────
def read_eml(raw: bytes) -> Notification:
    from email import policy
    from email.parser import BytesParser

    msg = BytesParser(policy=policy.default).parsebytes(raw)
    n = Notification(source_kind="eml")
    n.subject = str(msg.get("subject") or "")
    sender = str(msg.get("from") or "")
    m = re.match(r"\s*\"?([^\"<]*)\"?\s*<?([^>]*)>?", sender)
    if m:
        n.from_name = m.group(1).strip()
        n.from_email = m.group(2).strip()
    body_parts: list[str] = []
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition") or "")
            if "attachment" in disp:
                n.attachments.append(part.get_filename() or "attachment")
                continue
            if ctype == "text/plain":
                body_parts.append(part.get_content())
            elif ctype == "text/html" and not body_parts:
                body_parts.append(strip_html(part.get_content()))
    else:
        content = msg.get_content()
        body_parts.append(
            strip_html(content) if msg.get_content_type() == "text/html" else content
        )
    n.body = "\n".join(p for p in body_parts if p).strip()
    if not n.body:
        n.warnings.append("The email had no readable text body - paste the text instead.")
    return n


def read_msg(raw: bytes) -> Notification:
    try:
        import extract_msg
    except ImportError:  # pragma: no cover
        n = Notification(source_kind="msg")
        n.warnings.append("Outlook .msg support is not installed - paste the text instead.")
        return n
    n = Notification(source_kind="msg")
    try:
        m = extract_msg.Message(io.BytesIO(raw))
        n.subject = m.subject or ""
        n.from_name = (m.sender or "").split("<")[0].strip().strip('"')
        em = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", m.sender or "")
        n.from_email = em.group(0) if em else ""
        n.body = (m.body or "").strip()
        if not n.body and getattr(m, "htmlBody", None):
            html = m.htmlBody
            n.body = strip_html(html.decode("utf-8", "ignore") if isinstance(html, bytes) else html)
        n.attachments = [a.longFilename or a.shortFilename or "attachment"
                         for a in (m.attachments or [])]
    except Exception as exc:
        n.warnings.append(f"Could not open the Outlook file ({type(exc).__name__}) - paste the text instead.")
    if not n.body and not n.warnings:
        n.warnings.append("The Outlook file had no readable text body - paste the text instead.")
    return n


def strip_html(html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html or "")
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", text)
    text = re.sub(r"(?i)</t[dh]>", "\t", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def read_upload(filename: str, raw: bytes) -> Notification:
    name = (filename or "").lower()
    if name.endswith(".msg"):
        return read_msg(raw)
    if name.endswith(".eml"):
        return read_eml(raw)
    try:
        return Notification(body=raw.decode("utf-8"), source_kind="paste")
    except UnicodeDecodeError:
        n = Notification(source_kind="paste")
        n.warnings.append("That file is not a .msg, .eml or plain text file.")
        return n


# ── turning the words into fields, with no AI involved ─────────────────────
def parse_date(text: str) -> str:
    for pat, fmt in DATE_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        try:
            if fmt:
                return datetime.strptime(m.group(0), fmt).date().isoformat()
            groups = [g for g in m.groups() if g]
            if groups[0].isdigit():                     # 18 September 2026
                day, mon, year = int(groups[0]), MONTHS[groups[1][:3].lower()], int(groups[2])
            else:                                       # September 18, 2026
                mon = MONTHS[groups[0][:3].lower()]
                day = int(groups[1])
                year = int(groups[2]) if len(groups) > 2 and groups[2] else date.today().year
            return date(year, mon, day).isoformat()
        except (ValueError, KeyError, IndexError):
            continue
    return ""


def classify_change(text: str) -> tuple[str, str]:
    low = (text or "").lower()
    for words, kind, label in CHANGE_HINTS:
        if any(w in low for w in words):
            return kind, label
    return "unknown", "Not specified"


def extract_by_rules(n: Notification, cat: Catalog) -> dict:
    """Pull fields out using the catalogue - the fallback when there is no AI.

    Columns are only accepted once their own table has matched. Without that
    rule, generic words like STATUS or AMOUNT produce a page of false hits.
    """
    text = n.text()
    idents = [m.group(0) for m in IDENT.finditer(text)]
    seen_tables: list[str] = []
    for tok in idents:
        if cat.has_table(tok) and tok.upper() not in [t.upper() for t in seen_tables]:
            seen_tables.append(tok)

    upstream = []
    for t in seen_tables:
        attrs = [tok for tok in idents if cat.has_column(t, tok)]
        deduped: list[str] = []
        for a in attrs:
            if a.upper() not in [x.upper() for x in deduped]:
                deduped.append(a)
        upstream.append({"table": t, "attrs": deduped})

    kind, label = classify_change(text)
    warnings = list(n.warnings)
    unknown = [tok for tok in dict.fromkeys(idents)
               if not cat.has_table(tok) and not any(cat.has_column(t, tok) for t in seen_tables)]
    if unknown:
        warnings.append(
            "These names were mentioned but are not in the connected repository: "
            + ", ".join(unknown[:8])
        )
    if not upstream:
        warnings.append(
            "No table from the connected repository was recognised. Add the table and "
            "attributes by hand before scanning."
        )

    return {
        "source": (n.from_name.split()[0] if n.from_name else "") or "Unknown",
        "changeType": label,
        "changeKind": kind,
        "changeDesc": first_sentence(n.body),
        "subject": n.subject,
        "effectiveDate": parse_date(text),
        "pocName": n.from_name,
        "pocEmail": n.from_email,
        "pocTeam": n.from_name,
        "upstream": upstream,
        "warnings": warnings,
        "extractedBy": "rules",
    }


def first_sentence(body: str, limit: int = 240) -> str:
    clean = re.sub(r"\s+", " ", (body or "")).strip()
    for line in (body or "").splitlines():
        line = line.strip()
        if len(line) > 40 and not line.lower().startswith(("hi ", "hello", "team", "dear")):
            clean = line
            break
    return clean[:limit]
