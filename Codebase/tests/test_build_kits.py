"""The build kits are specifications, and a stale line in one gets obeyed.

Three documents, two of which are five thousand lines and have to agree with each
other word for word wherever they describe the same behaviour. Keeping that true
by reading them is not something anybody manages twice.

None of this checks prose quality. It checks the four things that have gone wrong
before and would go wrong silently again: a file that exists in the code and is
named in no kit, a payload key the screens read and the kits never mention, one
rule written down twice in two different ways, and a behaviour block that made it
into one kit and not the other.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parent.parent.parent
ONLINE = ROOT / "BUILD-KIT.md"
OFFLINE = ROOT / "BUILD-KIT-OFFLINE.md"
REPAIR = ROOT / "BUILD-KIT-REPAIR.md"
BUILD_KITS = (ONLINE, OFFLINE)


def text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def test_all_three_kits_are_here():
    """One builds on an ordinary laptop, one on a locked-down one, one changes a
    Ripple that already exists. Losing any of them loses a road in."""
    for kit in (ONLINE, OFFLINE, REPAIR):
        assert kit.is_file(), f"{kit.name} is missing"
        assert len(text(kit).splitlines()) > 400, f"{kit.name} is too short to be the kit"


def test_each_kit_says_which_of_the_three_it_is():
    """Somebody who opens the wrong one and follows it to the end has wasted two
    evenings, so each kit names all three and says when to use each."""
    for kit in (ONLINE, OFFLINE, REPAIR):
        body = text(kit)
        for other in ("BUILD-KIT.md", "BUILD-KIT-OFFLINE.md"):
            assert other in body, f"{kit.name} never mentions {other}"


# ── every engine file is named somewhere ──────────────────────────────────
# A file the kits never name is a file nobody builds. dialectcompat.py and
# build_info.py were both in this state: real, imported, load-bearing, and
# absent from every file map and every phase.
ENGINE_FILES = [
    "config.py", "production.py", "catalog.py", "narrative.py", "notification.py",
    "progress.py", "store.py", "api.py", "build_info.py",
    "scanner/repo.py", "scanner/templating.py", "scanner/sqlread.py",
    "scanner/lineage.py", "scanner/rescue.py", "scanner/dialectcompat.py",
]


@pytest.mark.parametrize("name", ENGINE_FILES)
def test_every_engine_file_is_named_in_both_build_kits(name):
    leaf = name.split("/")[-1]
    assert (Path(__file__).resolve().parent.parent / "ripple" / name).is_file(), \
        f"{name} is not in the shipped code - fix the list in this test"
    for kit in BUILD_KITS:
        assert leaf in text(kit), f"{kit.name} never names {leaf}"


@pytest.mark.parametrize("name", ENGINE_FILES)
def test_every_engine_file_is_named_in_the_repair_kit(name):
    """The repair kit's whole job is telling somebody which file to open."""
    assert name.split("/")[-1] in text(REPAIR), f"the repair kit never names {name}"


# ── the kits declare the payload the screens read ─────────────────────────
def _real_payload() -> dict:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from test_confident_over_less import scan          # noqa: PLC0415
    with tempfile.TemporaryDirectory() as d:
        return scan(Path(d), {"a.sql": "CREATE OR REPLACE TABLE final_published AS "
                                       "SELECT cm13 FROM customer_demographics;"})


def test_the_contract_card_declares_every_key_the_answer_carries():
    """Every window builds against the contract card and none of them can see the
    others. A key missing from it is a key one window sends and the next never
    reads - which shows up as a blank on screen and as nothing at all in a test."""
    out = _real_payload()
    body = text(ONLINE)
    start = body.index("{attributes[], groups[], reached[]")
    declared = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", body[start:start + 1200]))
    missing = sorted(set(out) - declared)
    assert not missing, f"the contract card never names: {missing}"


def test_the_contract_card_declares_every_stat():
    out = _real_payload()
    body = text(ONLINE)
    start = body.index("stats = {productionTables")
    declared = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", body[start:start + 600]))
    missing = sorted(set(out["stats"]) - declared)
    assert not missing, f"the contract card never names these stats: {missing}"


def test_the_contract_card_declares_every_field_on_a_finding():
    out = _real_payload()
    row = out["groups"][0]["rows"][0]
    body = text(ONLINE)
    start = body.index("{inter, from, attr, roots[]")
    declared = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", body[start:start + 500]))
    missing = sorted(set(row) - declared)
    assert not missing, f"the contract card never names these finding fields: {missing}"


# ── the two build kits agree with each other ──────────────────────────────
_HEADING = re.compile(r"^[A-Z][A-Z '\*\-,\.\(\)/_]{24,}", re.M)

# Blocks that belong to one kit only, and why. Anything NOT on this list has to
# appear in both, because both build the same tool.
ONLY_ONLINE = {"NAME WHAT YOU PRODUCE FOR ITS VERSION"}     # nothing is packaged offline
ONLY_OFFLINE = {"EVERY COMMAND RUNS FROM THE PROJECT ROOT",  # the parser sits beside the code
                "FIVE THINGS THAT MUST BE EXACTLY RIGHT"}    # getting the parser on at all


def _headings(body: str) -> set[str]:
    return {m.group(0).split(".")[0].strip() for m in _HEADING.finditer(body)}


def test_the_two_build_kits_carry_the_same_behaviour_blocks():
    """They build the same tool out of the same engine. A rule that reaches one
    kit and not the other is a product that behaves differently depending on
    which laptop it was built on, and nothing anywhere would say so."""
    a, b = _headings(text(ONLINE)), _headings(text(OFFLINE))
    only_a = {h for h in a - b if not any(h.startswith(x) for x in ONLY_ONLINE)}
    only_b = {h for h in b - a if not any(h.startswith(x) for x in ONLY_OFFLINE)}
    assert not only_a, f"only in the normal kit: {sorted(only_a)}"
    assert not only_b, f"only in the offline kit: {sorted(only_b)}"


def test_neither_build_kit_states_one_rule_twice():
    """Two accounts of one rule is worse than none: a chat obeys whichever it
    read last, and nobody can tell which that was."""
    for kit in BUILD_KITS:
        heads = [m.group(0).split(".")[0].strip() for m in _HEADING.finditer(text(kit))]
        twice = sorted({h for h in heads if heads.count(h) > 1})
        assert not twice, f"{kit.name} states these twice: {twice}"


def test_the_sqlglot_pin_is_the_one_the_kits_name():
    """The kits tell somebody to pin the parser. If they name a version the
    project no longer uses, the copy they build reads SQL differently from this
    one and nothing anywhere says so."""
    pinned = next(line.split("==")[1].split()[0].strip()
                  for line in (Path(__file__).resolve().parent.parent
                               / "requirements.txt").read_text(encoding="utf-8").splitlines()
                  if line.startswith("sqlglot=="))
    for kit in BUILD_KITS:
        found = set(re.findall(r"sqlglot[=<> ]*([0-9]+\.[0-9]+\.[0-9]+)", text(kit)))
        wrong = {v for v in found if v != pinned}
        assert not wrong, f"{kit.name} names sqlglot {sorted(wrong)}, pinned is {pinned}"


def test_the_offline_kit_does_not_name_a_version_that_disagrees_with_itself():
    """Phase 0 has somebody type a version file by hand. The string and the
    numbers in it are read by different things, so they have to match."""
    body = text(OFFLINE)
    strings = re.findall(r"__version__ = version = '([0-9.]+)'", body)
    tuples = re.findall(r"__version_tuple__ = version_tuple = \((\d+), (\d+), (\d+)\)", body)
    assert strings and tuples, "the hand-typed version file is not in the offline kit"
    for s, parts in zip(strings, tuples):
        assert s == ".".join(parts), f"version string {s} does not match tuple {parts}"


RAW_KEYS = ('args["except"]', 'args["from"]', 'args["replace"]',
            'args["expressions"]', 'args["columns"]', 'args["fields"]')


def test_a_kit_only_shows_a_raw_parse_tree_key_while_warning_about_it():
    """Every one of these has a helper, and reading the raw key gives back
    nothing rather than raising on a newer parser. So a kit may PRINT one - that
    is how the danger is explained - but only on a line that also shows what it
    was renamed to, or names the module that wraps it. A raw key shown on its
    own reads as an instruction, and a chat will write exactly what it sees."""
    for kit in BUILD_KITS:
        for n, line in enumerate(text(kit).splitlines(), 1):
            for raw in RAW_KEYS:
                if raw not in line:
                    continue
                warned = ("became" in line or "->" in line
                          or "dialectcompat" in line or "never" in line.lower())
                assert warned, f"{kit.name}:{n} shows {raw} with no warning beside it"
