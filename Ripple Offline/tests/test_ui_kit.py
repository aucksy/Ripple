"""Does BUILD-KIT-UI-EXACT.md actually put the screens back together?

The kit's whole promise is one sentence: paste these pieces in order and you
have Ripple's own screen files, not something that resembles them. A kit that
drops a line, cuts a line in half, or splits inside a fenced block breaks that
promise while still looking completely normal to read.

So this does what a person following the kit does -- takes the fenced blocks out
in order, joins them, and compares the result to the real file byte for byte.

It also fails when the kit has gone stale. The kit is generated from the live
files; edit app.js and forget to regenerate, and the kit hands somebody last
week's screens with a checksum that says they are current. That is worse than no
kit, because the check at the bottom of it would say "exact".
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
KIT = ROOT / "BUILD-KIT-UI-EXACT.md"
WEB = ROOT / "Codebase" / "web"
TOOL = ROOT / "Ripple Offline" / "tools" / "make_ui_kit.py"

FILES = ["web/index.html", "web/styles.css", "web/app.js"]


@pytest.fixture(scope="module")
def kit() -> str:
    if not KIT.is_file():
        pytest.fail(f"{KIT.name} is missing - run tools/make_ui_kit.py")
    return KIT.read_text(encoding="utf-8")


def rebuilt(kit_text: str) -> dict[str, str]:
    """Reassemble each file exactly the way somebody following the kit would.

    Every piece is announced by a '### <path>' heading and followed by one
    four-backtick block. Pieces for one file appear in order, and joining them
    with nothing between them is the whole instruction.
    """
    out: dict[str, list[str]] = {}
    pattern = re.compile(
        r"^### (web/[\w.]+)(?: — piece \d+ of \d+)?\s*\n"      # which file
        r".*?"                                                  # the instruction
        r"^````\w*\n(.*?)^````\s*$",                            # the block
        re.DOTALL | re.MULTILINE,
    )
    for m in pattern.finditer(kit_text):
        out.setdefault(m.group(1), []).append(m.group(2))
    return {name: "".join(pieces) for name, pieces in out.items()}


def test_the_kit_exists_and_names_every_screen_file(kit):
    for name in FILES:
        assert f"### {name}" in kit, f"{KIT.name} never hands over {name}"


def test_the_pieces_join_back_into_the_real_files(kit):
    """The one that matters. Byte for byte, or the screens are not the same."""
    got = rebuilt(kit)
    assert set(got) == set(FILES), f"recovered {sorted(got)}, expected {FILES}"

    for name in FILES:
        real = (ROOT / "Codebase" / name).read_text(encoding="utf-8")
        mine = got[name]
        if mine == real:
            continue
        # Say something useful rather than dumping 3,000 lines of diff.
        rl, ml = real.splitlines(), mine.splitlines()
        where = next((i for i, (a, b) in enumerate(zip(rl, ml), 1) if a != b), min(len(rl), len(ml)) + 1)
        pytest.fail(
            f"{name} does not come back whole. Real file {len(rl):,} lines, "
            f"rebuilt from the kit {len(ml):,} lines, first difference at line "
            f"{where}. Re-run tools/make_ui_kit.py."
        )


def test_the_checksums_in_the_kit_are_the_real_ones(kit):
    """The kit ships a check_ui.py. If its digests are stale it tells somebody
    their imitation is exact, which is the worst answer it could give."""
    for name in FILES:
        real = (ROOT / "Codebase" / name).read_text(encoding="utf-8")
        digest = hashlib.sha256(real.encode("utf-8")).hexdigest()
        assert digest in kit, (
            f"the checksum the kit publishes for {name} is not the current one. "
            f"The kit is stale - run tools/make_ui_kit.py."
        )


def test_no_piece_is_big_enough_to_be_refused(kit):
    """A chat window will not take an unlimited paste, and a piece that gets
    truncated produces a file that looks finished and is not."""
    blocks = re.findall(r"^````\w*\n(.*?)^````\s*$", kit, re.DOTALL | re.MULTILINE)
    oversize = [len(b.encode("utf-8")) for b in blocks if len(b.encode("utf-8")) > 45_000]
    assert not oversize, f"{len(oversize)} piece(s) over 45 KB: {oversize}"


def test_the_kit_is_generated_and_says_so(kit):
    """A hand-edited copy of app.js inside a document is a second copy of
    app.js, and the second copy is always the one that goes stale."""
    assert TOOL.is_file(), "the generator is missing"
    assert "make_ui_kit.py" in kit, "the kit does not say what generated it"
    assert "Do not\nedit this by hand" in kit or "Do not edit this by hand" in kit, \
        "the kit does not warn against hand-editing"


def test_the_kit_is_honest_about_what_it_does_not_give_you(kit):
    """It hands over the screens. It does not hand over the engine, and it
    cannot hand over the SQL parser. Saying so is the difference between a kit
    and a disappointment."""
    assert "sqlglot" in kit, "the kit never mentions the one thing that must be copied"
    assert "BUILD-KIT-OFFLINE.md" in kit, "the kit never says where the engine comes from"
