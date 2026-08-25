"""The two documents somebody actually opens, and the page that picks between them.

BUILD-KIT.md builds Ripple from nothing in a chat window. BUILD-KIT-REPAIR.md
changes a Ripple that already exists. That is the whole set, and the point of
the first one is that it is SELF-CONTAINED: somebody following it on a machine
that has never seen this repository must never be sent to another document, told
to fetch anything, or told that copying a finished Ripple would have been easier.

There was a third document once, RUN-RIPPLE-HERE.md, which handed Ripple's own
files over to paste. It defeated the purpose. The build has to happen in the chat
window, on the machine it is being built on, or it is not a build. Both it and
its generator are gone, and ``test_the_build_kit_sends_nobody_anywhere_else``
below is what stops the idea coming back one helpful sentence at a time.

Every path read here is a tracked one. Nothing reads the demo output folder,
which would be green on this machine and missing everywhere else.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
OFF = ROOT / "Ripple Offline"
SNAPSHOT_TOOL = OFF / "tools" / "make_demo_snapshot.py"

BUILD_KIT = ROOT / "BUILD-KIT.md"
REPAIR_KIT = ROOT / "BUILD-KIT-REPAIR.md"
REPAIR_TOOL = OFF / "tools" / "make_repair_kit.py"
START_HERE = ROOT / "START-HERE.md"


def read(doc: Path) -> str:
    if not doc.is_file():
        pytest.fail(f"{doc.name} is missing")
    return doc.read_text(encoding="utf-8")


# ── the build kit stands on its own ───────────────────────────────────────

# Named or shown in bold, which is how these documents refer to each other.
NAMES_A_DOC = re.compile(r"[`*]{1,2}([A-Z][A-Za-z0-9._-]*\.md)[`*]{1,2}")


def test_the_build_kit_sends_nobody_anywhere_else():
    """The reason the kit exists is that Ripple gets rebuilt by hand, in a chat,
    on a machine that has nothing. A single line pointing at another document,
    another laptop or a finished copy takes the whole exercise away -- and it is
    always added helpfully, as a shortcut for somebody stuck.

    So: the only documents the build kit may name are itself and the repair kit,
    and none of the sentences below may come back.
    """
    body = read(BUILD_KIT)

    named = set(NAMES_A_DOC.findall(body)) - {BUILD_KIT.name, REPAIR_KIT.name}
    assert not named, (
        f"BUILD-KIT.md sends somebody to {sorted(named)}. It has to be followable "
        f"on a machine that has only this one file."
    )

    banned = [
        "RUN-RIPPLE-HERE",       # the document that handed the files over
        "repair shop",           # what it was called when used alongside this kit
        "copying a finished",    # "copying a finished Ripple is one step"
        "Copy a finished",
        "memory stick",          # ...and the three ways of carrying one across
        "shared drive",
        "the copy it came from",
        "shipped Ripple",        # there is no other Ripple to compare against
        "shipped engine",
        "yours, not ours",
    ]
    found = [p for p in banned if p.lower() in body.lower()]
    assert not found, (
        f"BUILD-KIT.md is pointing at another source again: {found}. Nobody "
        f"following it has another Ripple to copy from, and telling them one "
        f"exists is how two evenings of work get thrown away."
    )


def test_the_build_kit_still_says_which_two_documents_exist():
    """Self-contained is not the same as silent. Somebody who has finished
    building and now wants to change something has to know the repair kit is
    there, or they start editing files with no idea which ones move together."""
    body = read(BUILD_KIT)
    assert REPAIR_KIT.name in body, "BUILD-KIT.md never mentions BUILD-KIT-REPAIR.md"
    assert REPAIR_KIT.is_file(), "BUILD-KIT-REPAIR.md is missing"


def test_no_document_that_was_deleted_is_still_referenced():
    """A dead pointer in a tracked file is a live instruction to whoever reads
    it. This checks the tracked documents and the tools, not just the kit."""
    gone = "RUN-RIPPLE-HERE"
    for doc in (BUILD_KIT, REPAIR_KIT, START_HERE):
        assert gone not in read(doc), f"{doc.name} still points at {gone}.md, which is gone"
    for tool in sorted((OFF / "tools").glob("*.py")):
        assert gone not in tool.read_text(encoding="utf-8"), \
            f"{tool.name} still writes or names {gone}.md, which is gone"


# ── the page that decides which file somebody opens ───────────────────────

def test_start_here_names_every_kit_and_no_kit_that_is_gone():
    """The index is the first thing anybody reads, so it is the worst thing to
    let go stale.

    It sent somebody to a file called BUILD-KIT-ONLINE-EXACT.md when what they
    wanted was to run Ripple on their own laptop, because "online" reads as
    "hosted" to everybody except this repository. Renaming fixed that; this
    stops the index drifting away from the files that actually exist.
    """
    page = read(START_HERE)

    on_disk = {p.name for p in ROOT.glob("*.md")} - {START_HERE.name}
    named = {n for n in re.findall(r"`([A-Z][\w.-]+\.md)`", page)}

    assert not (on_disk - named), (
        f"START-HERE.md never mentions {sorted(on_disk - named)}, so nobody "
        f"reading it knows those files exist."
    )
    assert not (named - on_disk), (
        f"START-HERE.md sends people to {sorted(named - on_disk)}, which is not "
        f"there any more."
    )


def test_start_here_says_local_and_hosted_are_the_same_files():
    """One codebase. run.py starts it here and the hosting entry point loads the
    same application object -- verified in Codebase/api/index.py, which does
    `from ripple.api import app`, exactly as run.py does. Somebody who thinks
    those are two builds goes looking for a second kit that does not exist.
    """
    page = read(START_HERE)
    assert "same files" in page, "START-HERE.md does not say it plainly"

    hosted = (ROOT / "Codebase" / "api" / "index.py").read_text(encoding="utf-8")
    local = (ROOT / "Codebase" / "run.py").read_text(encoding="utf-8")
    assert "ripple.api import app" in hosted, "the hosted entry no longer loads ripple.api"
    assert "ripple.api:app" in local or "ripple.api import app" in local, \
        "run.py no longer starts ripple.api - the claim in START-HERE.md is stale"


# ── the three commands that come before the first paste ───────────────────

def install_line(body: str) -> str:
    return next(l for l in body.splitlines() if l.startswith("python -m pip install --user")
                and "--no-index" not in l)


def test_the_setup_commands_are_there_and_in_order():
    """Three commands before the first paste, and the order is the whole point.

    On a managed laptop pip is often absent, and `pip` then says "not
    recognized" - which reads as a locked door and is not one. And pypi.org is
    blocked, so pip left pointing at it hangs and times out, which reads as a
    broken machine rather than a blocked address. Both are one command each, and
    both have to happen BEFORE the install or the install is what fails and the
    reason is two steps back.
    """
    kit = read(BUILD_KIT)
    wanted = [
        "python -m ensurepip --upgrade --user",
        "python -m pip config set global.index-url",
        "python -m pip install --user sqlglot==",
    ]
    where = []
    for cmd in wanted:
        assert cmd in kit, f"BUILD-KIT.md no longer carries `{cmd}`"
        where.append(kit.index(cmd))
    assert where == sorted(where), (
        "the setup commands are out of order in BUILD-KIT.md. ensurepip, then "
        "the mirror, then the install - any other order and the step that fails "
        "is not the step that is wrong."
    )


def test_the_install_line_pins_every_version():
    """An unpinned install takes whatever was published this morning. sqlglot
    renamed three parse-tree keys between majors and the renames are silent, so
    a newer one switches features off with nothing raised anywhere."""
    packages = [p for p in install_line(read(BUILD_KIT)).split()[5:] if not p.startswith("-")]
    unpinned = [p for p in packages if "==" not in p]
    assert not unpinned, f"not pinned to a version: {unpinned}"
    assert "sqlglot==30.17.0" in packages, (
        "the pinned sqlglot is not 30.17.0, which is the version every rule in "
        "the build kit was written against."
    )


def test_start_here_installs_exactly_what_the_build_kit_installs():
    """Two copies of one command line is one copy that goes stale, and this pair
    already had: START-HERE.md was short typing-inspection and pytest. Somebody
    who runs the shorter one gets eleven phases in and finds pytest missing at
    the point where the first check is meant to prove the phase worked.
    """
    mine = set(install_line(read(START_HERE)).split()[5:])
    theirs = set(install_line(read(BUILD_KIT)).split()[5:])
    assert mine == theirs, (
        f"the install line differs. START-HERE.md is missing {sorted(theirs - mine)} "
        f"and has {sorted(mine - theirs)} that BUILD-KIT.md does not."
    )


# ── the repair kit ────────────────────────────────────────────────────────

def test_the_repair_kit_carries_the_real_line_counts():
    """It is generated for exactly this reason.

    The hand-written version said sqlread.py was 3,573 lines when it was 3,720,
    repo.py 832 when it was 964, and app.js 2,883 when it was 3,235. Nothing
    failed; the document simply stopped being true, and a size is the least of
    what a hand-kept catalogue gets wrong.
    """
    kit = read(REPAIR_KIT)
    checked = 0
    for p in sorted((ROOT / "Codebase" / "ripple").rglob("*.py")):
        if "__pycache__" in p.parts or p.stat().st_size == 0:
            continue
        name = "ripple/" + p.relative_to(ROOT / "Codebase" / "ripple").as_posix()
        n = len(p.read_text(encoding="utf-8").splitlines())
        assert f"### {name}   ({n:,} lines" in kit, (
            f"{REPAIR_KIT.name} does not give {name} as {n:,} lines. It is stale - "
            f"run tools/make_repair_kit.py."
        )
        checked += 1
    assert checked > 15, f"only checked {checked} files - the walk is wrong"


def test_the_repair_kit_gives_both_directions_of_every_dependency():
    """One direction is half a routing decision.

    Changing what a file PRODUCES breaks everything under NEEDED BY. Changing
    what it CONSUMES means everything under IT NEEDS is worth reading first. A
    catalogue with only one of those gets a chat asking for one file when the
    change needs three, and the answer that comes back is confident and
    half-right.
    """
    kit = read(REPAIR_KIT)
    for field in ("IT NEEDS      :", "NEEDED BY     :"):
        n = kit.count(field)
        assert n > 25, f"only {n} entries carry `{field.strip()}`"
    assert kit.count("### ") >= 30, "the catalogue is short a file"


def test_the_repair_kit_is_one_block_somebody_can_paste():
    """The whole design is: paste one thing, type the problem, get a file list.
    Two blocks and somebody pastes the first and wonders why it does not work.
    """
    kit = read(REPAIR_KIT)
    blocks = re.findall(r"^````text\n(.*?)^````\s*$", kit, re.DOTALL | re.MULTILINE)
    assert len(blocks) == 1, f"expected one pasteable block, found {len(blocks)}"
    prompt = blocks[0]
    assert prompt.startswith("YOU ARE REPAIRING RIPPLE"), "the block does not open with the instruction"
    for must in ("WHICH FILES I SHOULD SEND", "IT NEEDS", "NEEDED BY",
                 "ASK FOR EVERY FILE THAT MIGHT HAVE TO CHANGE TOGETHER",
                 "THE CATALOGUE", "no impact"):
        assert must in prompt, f"the pasteable block never says `{must}`"


def test_the_repair_kit_is_generated_and_says_so():
    """A hand edit to a generated file survives until the next run and then
    disappears without anybody noticing it went."""
    assert REPAIR_TOOL.is_file(), "make_repair_kit.py is missing"
    assert "make_repair_kit.py" in read(REPAIR_KIT), \
        "BUILD-KIT-REPAIR.md does not say what generated it"


def test_the_rescue_prompts_for_the_two_hard_phases_are_there():
    """Phases 4 and 8 are where a build stalls, and the kit already NAMED what
    goes wrong without ever giving somebody the sentence to send back. A person
    in a broken window at ten at night does not compose one.

    These matter more now than they did. There is no second document to take a
    finished file from, so a stalled window has to be fixable from inside this
    one."""
    kit = read(BUILD_KIT)
    for phase in (4, 8):
        assert f"## When Phase {phase} goes wrong" in kit, \
            f"BUILD-KIT.md has no rescue section for Phase {phase}"
    # Each rescue block has to be pasteable, not described.
    four = kit.split("## When Phase 4 goes wrong")[1].split("# PHASE 5")[0]
    eight = kit.split("## When Phase 8 goes wrong")[1].split("# PHASE 9")[0]
    assert four.count("````text") >= 5, "BUILD-KIT.md: Phase 4 has too few ready prompts"
    assert eight.count("````text") >= 6, "BUILD-KIT.md: Phase 8 has too few ready prompts"
    # The two silent ones that cost an evening each.
    assert "0.0.0.0" in eight, "BUILD-KIT.md: nothing about binding to 0.0.0.0"
    assert "dialectcompat" in four, "BUILD-KIT.md: nothing about reading a parse-tree key directly"


# ── the demo snapshot ─────────────────────────────────────────────────────

def test_the_snapshot_only_lists_files_that_exist():
    """The snapshot names the engine files it carries in three hand-kept lists.
    A file renamed in Codebase leaves the old name sitting in one of them, and
    the snapshot then ships a Ripple missing a module -- which fails at import,
    on the machine that can install nothing to debug it.

    This used to be checked by comparing the lists against a second tool that
    kept its own copy. That tool is gone, so the comparison is against the disk,
    which is the thing both were meant to agree with anyway.
    """
    snap = SNAPSHOT_TOOL.read_text(encoding="utf-8")
    where = {
        "ENGINE": ROOT / "Codebase" / "ripple",
        "SCANNER": ROOT / "Codebase" / "ripple" / "scanner",
        "WRAPPER": OFF / "ripple_offline",
    }
    for listname, folder in where.items():
        block = re.search(listname + r" = \[(.*?)\]", snap, re.DOTALL)
        assert block, f"{listname} is missing from make_demo_snapshot.py"
        names = set(re.findall(r'"([^"]+)"', block.group(1)))
        assert names, f"{listname} is empty"
        missing = sorted(n for n in names if not (folder / n).is_file())
        assert not missing, (
            f"make_demo_snapshot.py lists {missing} under {listname}, and there "
            f"is no such file in {folder.name}/. The snapshot would ship a Ripple "
            f"that cannot import."
        )
