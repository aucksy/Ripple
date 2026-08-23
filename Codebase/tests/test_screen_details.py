"""Small things on screen that were wrong, and that only a person ever notices.

Neither of these is a wrong answer. Both are the app looking broken or saying
something that is no longer true, which costs it exactly the trust the rest of
the work is spent earning.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

WEB = Path(__file__).resolve().parent.parent / "web"


def test_the_pulsing_dot_cannot_be_squashed_by_its_own_row():
    """Reported as "the dot that pulsates is halved", and measured in a browser:
    9 pixels tall, 5.61 wide.

    Every .spin sits in a flex row (.foot) beside a long sentence. Flex items
    shrink by default, so the browser squeezed the 9px dot sideways and left it
    9px tall -- and a round dot rendered as a narrow ellipse reads as half a dot
    that failed to draw. The neighbouring .dot rule already had this; .spin was
    simply missed.
    """
    css = (WEB / "styles.css").read_text(encoding="utf-8")
    rule = next(line for line in css.splitlines() if line.strip().startswith(".spin{"))
    # Gathered from the whole rule: it is written across two lines.
    at = css.index(".spin{")
    body = css[at:css.index("}", at)]
    assert "flex-shrink:0" in body.replace(" ", ""), rule


def test_the_dot_and_the_spinner_are_protected_the_same_way():
    """They sit in the same kind of row and are the same size. If one needs it
    and the other does not, one of them is wrong."""
    css = (WEB / "styles.css").read_text(encoding="utf-8").replace(" ", "").replace("\n", "")
    for name in (".dot{", ".spin{"):
        at = css.index(name)
        assert "flex-shrink:0" in css[at:css.index("}", at)], name


def test_the_repository_screen_no_longer_calls_a_select_star_table_a_dead_end():
    """That list is headed on the repository screen and read while somebody is
    deciding whether a scan result can be believed.

    It used to say Ripple "could not fully read" those tables, which was true
    when a scan stopped dead at them. A scan now follows the column straight
    through, so the old heading would send somebody looking for a gap that is
    not there.
    """
    js = (WEB / "app.js").read_text(encoding="utf-8")
    at = js.index("cat.gaps.length")
    # Comment lines are stripped: the note explaining WHY the old wording went
    # is allowed to quote it, and only what reaches the screen is being checked.
    card = "\n".join(line for line in js[at:at + 2400].splitlines()
                     if not line.strip().startswith("//"))
    assert "could not fully read" not in card
    assert "no column list written down" in card
    assert "does not stop here" in card


# ── several contact addresses, in BOTH ways in ─────────────────────────────
# The reply goes to whoever sent the notification, and a notification is very
# often addressed to two or three people. One address means the other two never
# hear that their change breaks something.
#
# There are two ways into the app -- typing the change by hand, and uploading
# the email -- and the box only has to be forgotten on one of them for half the
# recipients to be dropped without anything on screen saying so.
def test_the_contact_box_reads_every_address_it_is_given():
    """Commas, semicolons, "Name <addr>", newlines, and the same address twice."""
    js = (WEB / "app.js").read_text(encoding="utf-8")
    line = next(l for l in js.splitlines() if l.strip().startswith("const EMAIL_RE"))
    pattern = line.split("=", 1)[1].strip().rstrip(";")
    # The screen's own regular expression, read out of the screen's own file, so
    # this cannot pass while the app uses a different one.
    body = pattern[1:pattern.rfind("/")]
    flags = pattern[pattern.rfind("/") + 1:]
    import re
    rx = re.compile(body.replace("\\d", "[0-9]"), re.I if "i" in flags else 0)

    def addresses(text: str) -> list[str]:
        return sorted({a.lower() for a in rx.findall(text)})

    assert addresses("priya@corp.com, marcus@corp.com") == \
        ["marcus@corp.com", "priya@corp.com"]
    assert addresses("Priya Raman <priya@corp.com>; Marcus <marcus@corp.com>") == \
        ["marcus@corp.com", "priya@corp.com"]
    assert addresses("a@x.com\nb@x.com") == ["a@x.com", "b@x.com"]
    assert addresses("one@x.com, One@X.com") == ["one@x.com"], "the same person once"
    assert addresses("nobody here") == []


def test_both_ways_in_collect_every_address():
    """Manual mode and a read email must both fill pocEmails. Forgetting one of
    them drops half the recipients with nothing on screen to show for it."""
    js = (WEB / "app.js").read_text(encoding="utf-8")
    assert "pocEmails: emailList(S.man.pocEmail)" in js, \
        "manual mode must read every address typed into the contact box"
    assert "pocEmails: emailList(out.pocEmail)" in js, \
        "a notification that was read must keep every address it named"


def test_the_reply_screen_uses_all_of_them():
    js = (WEB / "app.js").read_text(encoding="utf-8")
    assert "S.vals.pocEmails?.length ? S.vals.pocEmails" in js, \
        "the drafted reply must be addressed to everyone, not to the first one"


def test_the_clean_bill_of_health_cannot_print_over_a_file_type_never_opened():
    """Seen on the rendered screen and nowhere else: the green "Every file was
    opened and read. Nothing was skipped" note sat DIRECTLY ABOVE the card
    saying a notebook had never been looked inside.

    That note is the tool's clean bill of health for coverage, and it may not be
    printed while a whole file type went unread. Two things had to be true for
    the contradiction to survive: the unopened types were not counted into the
    "what this result does not cover" row, and the note's own condition did not
    mention them. Both are pinned here, because a JS change cannot be caught by
    a Python test any other way and this one only shows up in a picture.
    """
    js = (WEB / "app.js").read_text(encoding="utf-8")
    # Counted into the row, so a reader sees the number beside the other gaps.
    assert "'Types Ripple does not open'" in js, \
        "unopened file types are not counted into the coverage row"
    # ... and named in the note's own guard, so it cannot fire regardless.
    note = js.index("Every file was opened and read.")
    guard = js.rindex("if (", 0, note)
    condition = js[guard:note]
    assert "unopenedTypes" in condition, condition
    assert "couldNotRead" in condition, condition
