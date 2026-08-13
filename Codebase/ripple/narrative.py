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


def _unique(groups: list[dict]) -> list[dict]:
    """Rows across groups, listed once. A finding upstream of two tables appears
    in both groups; counting it twice makes the actions read like a stutter."""
    rows, seen = [], set()
    for g in groups:
        for r in g["rows"]:
            k = (r.get("file"), r.get("attr"), r.get("alias"), r.get("logic"))
            if k not in seen:
                seen.add(k)
                rows.append(r)
    return rows


def summarise(scan: dict, vals: dict) -> dict:
    stats = scan.get("stats", {})
    groups = scan.get("groups", [])
    # Chains that end somewhere that is not on the production list, and usages
    # in code that builds no table at all. Both are real usages of the
    # attribute, and saying "no impact" while holding them would be a lie the
    # person then forwards to the upstream team in writing.
    reached = scan.get("reached", [])
    other = scan.get("other", [])
    unreadable = scan.get("unreadable", [])
    prod_names = [g["prod"] for g in groups]
    rows = _unique(groups)
    elsewhere = _unique(reached) + other
    breaking = [r for r in rows if r.get("breaking")]
    no_fix = [r for r in rows if r.get("noLocalFix")]
    attrs = ", ".join(
        a for u in vals.get("upstream", []) for a in u.get("attrs", [])
    ) or "the changed attributes"
    when = vals.get("effectiveLabel") or "the effective date"

    if not groups and elsewhere:
        # Found, and consumed -- but nothing it feeds is on the list of tables
        # this team publishes. That is either a genuinely internal chain or a
        # production naming rule that does not match this repository, and only
        # a person can tell which. So the wording says exactly that.
        end_names = [g["prod"] for g in reached]
        headline = (f"{_plural(len(elsewhere), 'usage')} found - none of them reaching "
                    f"a table on your published list")
        narrative = (
            f"{attrs} is used in {_plural(len({r.get('file') for r in elsewhere}), 'file')} "
            f"of the {scan.get('filesScanned', 0)} scanned. "
            + (f"Those chains end at {', '.join(end_names)}. " if end_names else "")
            + "None of those names match the rule Ripple has been given for a table this "
              "team publishes, so this is not a clean result - it is an unfinished one. "
              "Check the rule on the settings screen before replying."
        )
        bullets = [f"{r['inter']} - {r['logic'].lower()} on {r['alias']}" for r in elsewhere[:4]]
        bullets.append("Nothing here matched the production naming rule, so Ripple cannot say "
                       "whether these tables are ones anybody outside the team reads.")
        actions = [
            "Check the production table rule on the settings screen against how your tables "
            "are really named, then run the scan again.",
            "Until then, treat the tables listed above as impacted.",
        ]
    elif not groups:
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
            f"{_plural(len(unreadable), 'file')} could not be followed and must be checked by hand."
        )
        actions.append(
            f"Read the {_plural(len(unreadable), 'file')} in the 'check by hand' list yourself - "
            f"Ripple could not read them, or found the name somewhere it cannot follow."
        )

    # Files that were never opened go first among the caveats and are worded
    # harder, because every other number on the page is a number about the files
    # that WERE opened. Left unsaid, this reads as an answer about the whole
    # repository when it is an answer about part of one.
    never_opened = stats.get("neverOpened", 0)
    if never_opened:
        bullets.insert(0, (
            f"{_plural(never_opened, 'file')} in this repository could not even be opened, so "
            f"nothing in them was read - this result covers the rest."
        ))
        actions.insert(0, (
            f"Make the {_plural(never_opened, 'file')} that could not be opened available on this "
            f"machine and read the repository again before trusting this result."
        ))

    return {
        "headline": headline,
        "narrative": narrative,
        "bullets": bullets[:6],
        "actions": actions[:6],
        "writtenBy": "rules",
    }


def draft_reply(scan: dict, vals: dict, summary: dict) -> dict:
    groups = scan.get("groups", [])
    reached = scan.get("reached", [])
    other = scan.get("other", [])
    rows = [r for g in groups for r in g["rows"]]
    elsewhere = _unique(reached) + other
    no_fix = [r for r in rows if r.get("noLocalFix")]
    poc = vals.get("pocName") or "there"
    first = poc.split()[0] if poc and poc != "there" else "there"
    attrs = ", ".join(a for u in vals.get("upstream", []) for a in u.get("attrs", []))
    subject_base = vals.get("subject") or f"{attrs} change"

    if not groups and elsewhere:
        # This draft is a letter somebody sends. It must never say "no impact"
        # while the analysis behind it is holding a list of usages.
        end_names = ", ".join(g["prod"] for g in reached) or "tables in our own pipeline"
        subject = f"RE: {subject_base} - assessment in progress"
        body = (
            f"Hi {first},\n\n"
            f"We have run our impact analysis and are still confirming the result.\n\n"
            f"{attrs} is used in {_plural(len({r.get('file') for r in elsewhere}), 'file')} "
            f"in our repository, feeding {end_names}. We are confirming which of those are "
            f"published outside our team before we can tell you whether this is impacting.\n\n"
            f"We will come back to you with a firm answer before the effective date.\n\n"
            f"Thanks,\nData Engineering"
        )
    elif not groups:
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
        never_opened = scan.get("stats", {}).get("neverOpened", 0)
        if never_opened:
            lines += [
                "",
                f"Also for transparency: {_plural(never_opened, 'file')} could not be opened at all "
                f"on the machine this was run on, so this assessment does not cover them.",
            ]
        lines += ["", "Thanks,", "Data Engineering"]
        subject = f"RE: {subject_base} - impact confirmed"
        body = "\n".join(lines)

    return {"subject": subject, "body": body, "writtenBy": "rules"}
