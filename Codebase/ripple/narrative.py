"""Writing the summary and the reply without any AI.

This is what runs when there is no key, when the key stops working, or when
someone decides no data may leave the network. It is plainer than the AI
version, but it says exactly the same things -- the facts come from the scan
either way.
"""
from __future__ import annotations

from datetime import date


def _plural(n: int, one: str, many: str | None = None) -> str:
    return f"{n} {one}" if n == 1 else f"{n} {many or one + 's'}"


def days_until(iso: str) -> int | None:
    if not iso:
        return None
    try:
        y, m, d = (int(x) for x in iso.split("-"))
        return (date(y, m, d) - date.today()).days
    except (ValueError, TypeError):
        return None


def summarise(scan: dict, vals: dict) -> dict:
    stats = scan.get("stats", {})
    groups = scan.get("groups", [])
    unreadable = scan.get("unreadable", [])
    prod_names = [g["prod"] for g in groups]
    # A finding upstream of two production tables appears in both groups; count
    # and list it once, or the actions read like a stutter.
    rows, seen = [], set()
    for g in groups:
        for r in g["rows"]:
            k = (r.get("file"), r.get("attr"), r.get("alias"), r.get("logic"))
            if k not in seen:
                seen.add(k)
                rows.append(r)
    breaking = [r for r in rows if r.get("breaking")]
    no_fix = [r for r in rows if r.get("noLocalFix")]
    attrs = ", ".join(
        a for u in vals.get("upstream", []) for a in u.get("attrs", [])
    ) or "the changed attributes"
    when = vals.get("effectiveLabel") or "the effective date"

    if not groups:
        headline = "No impact - nothing in this repository consumes the attribute"
        narrative = (
            f"The scan read {stats.get('filesWithImpact', 0) or 0} of "
            f"{scan.get('filesScanned', 0)} files looking for {attrs}, and found no path from it "
            f"to any production table this team publishes."
        )
        bullets = [
            f"No production table depends on {attrs}.",
            f"{_plural(scan.get('filesMatched', 0), 'file')} mentioned the name, none of them in a way that carries it downstream.",
        ]
        actions = [
            "Reply to the upstream team confirming no impact.",
            "Re-run the scan if this repository takes on the table later.",
        ]
    else:
        if no_fix:
            headline = "Ranking logic has no replacement - escalate before the date"
        elif breaking:
            headline = f"{_plural(len(prod_names), 'production table')} at risk, all fixable in code"
        else:
            headline = "Labels change, but nothing breaks"
        narrative = (
            f"{attrs} changes on {when}. "
            f"{_plural(len(rows), 'pipeline object')} consume it across "
            f"{_plural(stats.get('filesWithImpact', 0), 'file')}, feeding "
            f"{', '.join(prod_names)}. "
            + (
                f"{_plural(len(breaking), 'of those usages breaks', 'of those usages break')} outright."
                if breaking
                else "None of those usages break outright - the values simply change shape."
            )
        )
        bullets = []
        for r in breaking[:4]:
            bullets.append(f"{r['inter']} - {r['logic'].lower()} on {r['alias']} - {r['impact']}")
        if no_fix:
            bullets.append(
                "At least one usage has no local fix: a replacement must come from the upstream team."
            )
        if not bullets:
            bullets.append("Every usage carries the value through unchanged; only labels move.")
        actions = []
        for r in breaking[:4]:
            actions.append(f"Fix the {r['logic'].lower()} on {r['alias']} in {r['file']}.")
        if no_fix:
            actions.insert(0, "Ask the upstream team for a replacement attribute - this one has no substitute.")
        actions.append("Re-run the scan once the fixes are in, and confirm the findings clear.")

    if unreadable:
        bullets.append(
            f"{_plural(len(unreadable), 'file')} could not be read and must be checked by hand."
        )
        actions.append(
            f"Check the {_plural(len(unreadable), 'file')} in the 'could not read' list by hand."
        )

    return {
        "headline": headline,
        "narrative": narrative,
        "bullets": bullets[:6],
        "actions": actions[:6],
        "writtenBy": "rules",
    }


def draft_reply(scan: dict, vals: dict, summary: dict) -> dict:
    groups = scan.get("groups", [])
    rows = [r for g in groups for r in g["rows"]]
    no_fix = [r for r in rows if r.get("noLocalFix")]
    poc = vals.get("pocName") or "there"
    first = poc.split()[0] if poc and poc != "there" else "there"
    attrs = ", ".join(a for u in vals.get("upstream", []) for a in u.get("attrs", []))
    subject_base = vals.get("subject") or f"{attrs} change"

    if not groups:
        subject = f"RE: {subject_base} - no impact"
        body = (
            f"Hi {first},\n\n"
            f"We have completed our impact analysis.\n\n"
            f"No impact. Our repository scan found no usage of {attrs} in any SQL, Spark job, view "
            f"or ETL script, and no production table traces back to it.\n\n"
            f"No action required from our side. Please proceed as planned.\n\n"
            f"Thanks,\nData Engineering"
        )
    else:
        prod = ", ".join(g["prod"] for g in groups)
        lines = [f"Hi {first},", "", "We have completed our impact analysis.", ""]
        lines.append(
            f"Impact confirmed. {attrs} is consumed by {_plural(len(rows), 'pipeline object')} "
            f"feeding {_plural(len(groups), 'production table')}: {prod}."
        )
        lines.append("")
        lines.append("What we will do before the effective date:")
        for a in summary.get("actions", [])[:4]:
            lines.append(f"  - {a}")
        if no_fix:
            lines += [
                "",
                "One ask of your team: at least one of these usages orders or deduplicates on the "
                "attribute, and has no local substitute. Can you confirm a replacement attribute, "
                "or retain this one, before the effective date?",
            ]
        unreadable = scan.get("unreadable", [])
        if unreadable:
            lines += [
                "",
                f"For transparency: {_plural(len(unreadable), 'file')} in our repository could not be "
                f"read automatically and are being checked by hand, so this assessment may still grow.",
            ]
        lines += ["", "Thanks,", "Data Engineering"]
        subject = f"RE: {subject_base} - impact confirmed"
        body = "\n".join(lines)

    return {"subject": subject, "body": body, "writtenBy": "rules"}
