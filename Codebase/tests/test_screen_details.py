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
