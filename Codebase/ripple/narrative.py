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


def _names(items: list[str], limit: int = 6) -> str:
    """A readable list of table names, however many there really are.

    On a real repository one key column reaches hundreds of tables. Joining
    them all into a sentence produces a paragraph nobody reads, in the one place
    on the screen written to be read -- and the count, which is the fact that
    matters, disappears into the middle of it.
    """
    if len(items) <= limit:
        return ", ".join(items)
    return ", ".join(items[:limit]) + f" and {len(items) - limit} more"


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

    # How much of the repository this answer does NOT cover. A headline is a
    # sentence somebody quotes in a meeting and pastes into a reply, so it must
    # never claim more than was read: "no impact" over four hundred files that
    # were never opened is the exact answer this tool exists to stop anybody
    # giving, and so is "all fixable in code" over a list of files nobody could
    # follow -- the fix that is missing may well be in one of them.
    files_scanned = scan.get("filesScanned", 0)
    never_opened = stats.get("neverOpened", 0)
    blind = never_opened + len(unreadable)

    def _blind_phrase() -> str:
        bits = []
        if never_opened:
            bits.append(f"{_plural(never_opened, 'file')} could not be opened at all")
        if unreadable:
            bits.append(f"{_plural(len(unreadable), 'file')} could not be followed")
        return " and ".join(bits)

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
            + (f"Those chains end at {_names(end_names)}. " if end_names else "")
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
    elif not files_scanned:
        # Nothing was read at all. "No impact" here is a statement about an
        # empty folder dressed up as a statement about a pipeline.
        headline = "Nothing was scanned - there was no code to search"
        narrative = (
            f"Ripple read no files at all, so it has looked for {attrs} in nothing. This is not "
            f"a result about your pipeline; it is a result about an empty repository. Choose the "
            f"folder holding the code on the settings screen and run the scan again."
        )
        bullets = ["No file was read, so nothing can be said about the change either way."]
        actions = [
            "Point Ripple at the folder holding the code, on the settings screen.",
            "Run the scan again once files have been read.",
        ]
    elif not groups:
        if blind:
            headline = (f"No usage found in the {_plural(files_scanned, 'file')} that could be "
                        f"read - {_plural(blind, 'other file')} could not be")
        else:
            headline = "No impact - nothing in this repository consumes the attribute"
        narrative = (
            f"The scan read {stats.get('filesWithImpact', 0) or 0} of "
            f"{files_scanned} files looking for {attrs}, and found no path from it "
            f"to any production table this team publishes."
            + (f" It is not a clean result for the whole repository: {_blind_phrase()}, "
               f"so nothing in those is covered either way." if blind else "")
        )
        bullets = [
            f"No production table depends on {attrs}.",
            f"{_plural(scan.get('filesMatched', 0), 'file')} mentioned the name, none of them in a way that carries it downstream.",
        ]
        actions = (["Read the files below by hand before replying - this result does not cover them."]
                   if blind else []) + [
            "Reply to the upstream team confirming no impact." if not blind
            else "Reply only once those files have been checked.",
            "Re-run the scan if this repository takes on the table later.",
        ]
    else:
        if no_fix:
            headline = "Ranking logic has no replacement - escalate before the date"
        elif breaking and blind:
            # "All fixable in code" is a promise about the whole repository. The
            # fix that has no substitute may well be inside one of the files
            # nobody could follow, and that is not a promise to make on a
            # headline somebody forwards.
            headline = (f"{_plural(len(prod_names), 'production table')} at risk, and "
                        f"{_plural(blind, 'file')} Ripple could not follow")
        elif breaking:
            headline = f"{_plural(len(prod_names), 'production table')} at risk, all fixable in code"
        elif blind:
            headline = (f"Labels change - and {_plural(blind, 'file')} could not be checked")
        else:
            headline = "Labels change, but nothing breaks"
        narrative = (
            f"{attrs} changes on {when}. "
            f"{_plural(len(rows), 'pipeline object')} consume it across "
            f"{_plural(stats.get('filesWithImpact', 0), 'file')}, feeding "
            f"{_names(prod_names)}. "
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
        end_names = _names([g["prod"] for g in reached], 10) or "tables in our own pipeline"
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
    elif not scan.get("filesScanned", 0):
        # There was nothing to read. A letter saying "no impact" here is a
        # letter about an empty folder, sent to somebody who will act on it.
        subject = f"RE: {subject_base} - assessment not yet run"
        body = (
            f"Hi {first},\n\n"
            f"We are not able to give you an answer yet. Our impact analysis read no files at "
            f"all, so nothing has actually been checked.\n\n"
            f"We will come back to you with a firm answer before the effective date.\n\n"
            f"Thanks,\nData Engineering"
        )
    elif not groups:
        # "No impact, proceed as planned" is the single most consequential
        # sentence this tool writes. It is only ever sent when the whole
        # repository really was read.
        blind = (scan.get("stats", {}).get("neverOpened", 0)
                 + len(scan.get("unreadable", [])))
        if blind:
            subject = f"RE: {subject_base} - no impact found so far"
            body = (
                f"Hi {first},\n\n"
                f"We have run our impact analysis and are still confirming the result.\n\n"
                f"No usage of {attrs} was found in the "
                f"{_plural(scan.get('filesScanned', 0), 'file')} we were able to read, and no "
                f"production table traces back to it.\n\n"
                f"{_plural(blind, 'further file')} could not be read or followed automatically "
                f"and {'is' if blind == 1 else 'are'} being checked by hand, so we are not "
                f"confirming no impact yet.\n\n"
                f"We will come back to you with a firm answer before the effective date.\n\n"
                f"Thanks,\nData Engineering"
            )
        else:
            subject = f"RE: {subject_base} - no impact"
            body = (
                f"Hi {first},\n\n"
                f"We have completed our impact analysis.\n\n"
                f"No impact. Our repository scan found no usage of {attrs} in any SQL, Spark job, "
                f"view or ETL script, and no production table traces back to it.\n\n"
                f"No action required from our side. Please proceed as planned.\n\n"
                f"Thanks,\nData Engineering"
            )
    else:
        # Capped like every other list of table names here: this is a letter
        # somebody sends, and a paragraph of two hundred names is not read.
        prod = _names([g["prod"] for g in groups], 10)
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
