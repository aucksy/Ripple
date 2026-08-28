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


# ── the folder somebody ends up with ──────────────────────────────────────

BUILD_FOLDER_TOOL = OFF / "tools" / "make_build_folder.py"


def test_the_kits_picture_of_the_folder_names_every_file_it_will_contain():
    """The kit draws the finished folder and says "this is what you are building
    towards". Somebody compares their folder against that picture.

    It had already gone stale: build_info.py, scanner/rescue.py,
    scanner/dialectcompat.py, paths.py and start-ripple.bat were all missing
    from it while later phases created them, so five files in a correct folder
    had nothing to account for them. A picture that is not exhaustive sends
    somebody hunting for a mistake that is not theirs.

    make_build_folder.py builds that folder for real by walking the disk, so
    what it produces is the honest list. Every engine file it copies has to
    appear in the picture.
    """
    body = read(BUILD_KIT)
    block = re.search(r"^C:\\ripple-build\\\n(.*?)^```", body, re.DOTALL | re.MULTILINE)
    assert block, "BUILD-KIT.md no longer draws the finished folder"
    picture = block.group(1)

    engine = ROOT / "Codebase" / "ripple"
    missing = sorted(
        p.name for p in engine.rglob("*.py")
        if "__pycache__" not in p.parts and p.name != "__init__.py"
        and p.name not in picture
    )
    assert not missing, (
        f"the folder picture in BUILD-KIT.md never names {missing}, which the "
        f"phases build and make_build_folder.py copies. Somebody comparing their "
        f"folder against that picture finds files they cannot account for."
    )
    for named in ("run.py", "start-ripple.bat", "index.html", "app.js", "mockrepo"):
        assert named in picture, f"the folder picture never names {named}"


def test_every_file_in_the_picture_is_actually_commissioned_by_a_phase():
    """Drawing a file is not the same as asking anybody to write it.

    The test above checks one direction: every shipped engine file appears in
    the picture. Nothing checked the other, and three files fell through it.
    Measured by running the whole kit through fresh chat windows on 27 Aug 2026:
    providers.py, ai.py and scanner/github.py were drawn in the picture, listed
    in the contract card's FILE MAP, and described in the "what each file is
    for" table -- and no phase anywhere carried a "Saves to:" line for any of
    them. api.py imported ripple.ai, which nobody had been asked to write, so
    the finished build died on `python run.py` with ModuleNotFoundError before
    a single screen was drawn.

    The front matter even said providers.py was "written out in full later in
    this kit, under THE AI KEY BOX" -- a section that describes the settings
    SCREEN, in a different window, and never says to save a Python file.
    """
    body = read(BUILD_KIT)

    block = re.search(r"^C:\\ripple-build\\\n(.*?)^```", body, re.DOTALL | re.MULTILINE)
    assert block, "BUILD-KIT.md no longer draws the finished folder"
    # Hyphens matter: start-ripple.bat and getfonts.py both live in the picture.
    NAME = r"([a-z_][a-z0-9_-]*\.(?:py|js|css|html|bat|txt))"
    drawn = set(re.findall(r"(?<![\w.-])" + NAME + r"\b", block.group(1)))
    drawn -= {"__init__.py"}          # the kit tells the PERSON to make these

    # ONLY the places that actually ask somebody to produce a file. Naming a
    # file in the FILE MAP or in the "what each file is for" table is not
    # commissioning it -- that is exactly how three files went missing, so this
    # must not be a search of the whole document.
    commissioned: set[str] = set()

    # 1. every "**Saves to:** ..." block, which runs to the next blank line
    for chunk in re.findall(r"\*\*Saves to:\*\*(.*?)\n\n", body, re.DOTALL):
        commissioned |= set(re.findall(NAME, chunk))
    # 2. "**Optional, and only if...:** `ripple-build/ripple/ai.py`" style blocks
    for chunk in re.findall(r"\*\*Optional[^\n]*\*\*(.*?)\n\n", body, re.DOTALL):
        commissioned |= set(re.findall(NAME, chunk))
    # 3. files the PERSON creates from the command line, e.g. start-ripple.bat
    commissioned |= set(re.findall(r"type nul > [^\n]*?" + NAME, body))
    # 4. files a pasted prompt asks the chat for, e.g. "Write me ripple-build/getfonts.py"
    commissioned |= set(re.findall(r"Write me [^\n]*?" + NAME, body))

    orphans = sorted(drawn - commissioned)

    assert not orphans, (
        f"BUILD-KIT.md draws {orphans} in the finished-folder picture, but no "
        f"phase says 'Saves to:' for them. Somebody following the kit ends up "
        f"without those files, and whichever window imports one of them "
        f"produces a build that will not start."
    )


def test_the_contract_card_names_the_functions_that_cross_a_window():
    """Twelve strangers cannot agree on a name nobody wrote down.

    The card fixed every FILE that crosses a window boundary and every DATA
    SHAPE, and not one function name. Measured on a full clean-room run,
    27 Aug 2026: nine of nine guessed names were wrong -- api.py wanted
    get_settings, write_summary, read_message_bytes, parse_rule and check_rule;
    lineage.py wanted is_production and wildcard_match; sqlread.py wanted
    rescue_sql. Ten broken links in one build, and re-running one window
    changed WHICH ten, so it is not a list of typos anybody can fix once.

    The same run showed the screens calling four addresses the server does not
    serve, so the route names have to be on the card too.
    """
    body = read(BUILD_KIT)
    for heading in ("FUNCTION MAP", "ROUTE MAP", "PAGE MAP"):
        assert heading in body, (
            f"the contract card no longer carries a {heading}. Without it every "
            f"window guesses the names it calls in another window's file, and "
            f"nothing fails until the whole build is assembled."
        )
    # The blank-screen one: the page and the script have to agree on these.
    for element in ('id="view"', '"t-step1"', "'t-step' + n"):
        assert element in body, (
            f"the PAGE MAP no longer pins {element}. An element id that does not "
            f"match produces no error at all - the screen simply draws nothing."
        )
    # The seams that actually broke, each one measured.
    for name in ("rescue_text", "summarise", "read_upload", "wildcard_match",
                 "parse_repo", "trace", "build_catalog", "has_production"):
        assert name in body, f"the FUNCTION MAP no longer names {name}"
    for route in ("/api/read-email", "/api/history", "/api/scan", "/api/health"):
        assert route in body, f"the ROUTE MAP no longer names {route}"
    assert "There is no /api/notification" in body, (
        "the ROUTE MAP no longer rules out the addresses the screens invented"
    )


def test_the_folder_tool_leaves_nothing_out_silently():
    """Two tests and a hosting file are deliberately not copied into the folder.
    Dropping a test quietly is how a suite stops proving anything, so each one
    has to carry its reason in the tool itself."""
    tool = BUILD_FOLDER_TOOL.read_text(encoding="utf-8")
    block = re.search(r"TESTS_LEFT_OUT = \{(.*?)\n\}", tool, re.DOTALL)
    assert block, "make_build_folder.py no longer lists what it leaves out"
    named = re.findall(r'"(test_[a-z_]+\.py)":', block.group(1))
    assert named, "no test is named as left out, yet the list exists"
    for name in named:
        assert (ROOT / "Codebase" / "tests" / name).is_file(), (
            f"make_build_folder.py leaves out {name}, which is not in the suite "
            f"any more - the reason it was skipped is gone and nobody noticed."
        )
    # Every reason is a sentence, not an empty string.
    reasons = re.findall(r'"test_[a-z_]+\.py":\s*\n?\s*"([^"]*)"', block.group(1))
    assert len(reasons) == len(named), "a test is left out with no reason given"
    assert all(len(r) > 15 for r in reasons), f"a reason is too short to be one: {reasons}"


def test_the_batch_file_never_trusts_the_word_python():
    """`python run.py` in a batch file is a guess about which Python answers.

    Measured on 27 Aug 2026, one ordinary Windows laptop answered to `python`
    three times: a 3.12 with Ripple's packages in it, a shim for a 3.14 with
    none, and a zero-byte Microsoft Store stub. A double-click reached a wrong
    one and printed `ModuleNotFoundError: No module named 'uvicorn'` at somebody
    who does not write code. Nothing was broken, and nothing said so.

    Both batch files -- the generated one and this repository's own -- have to
    ask each candidate whether it can load the packages, and say the one line to
    run when none can. The build kit has to teach the same thing, or the next
    person builds the fragile one straight back.
    """
    generated = re.search(r"BAT = (.*?)\n\]\)", BUILD_FOLDER_TOOL.read_text(encoding="utf-8"),
                          re.DOTALL)
    assert generated, "make_build_folder.py no longer writes a batch file"

    here = (ROOT / "Codebase" / "start-ripple.bat").read_text(encoding="utf-8")
    kit = read(BUILD_KIT)

    for where, body in (("the generated batch file", generated.group(1)),
                        ("Codebase/start-ripple.bat", here),
                        ("BUILD-KIT.md", kit)):
        assert "import uvicorn" in body, (
            f"{where} does not check that the Python it picked can actually load "
            f"Ripple. It is trusting whichever one answers first."
        )
        assert "py -3" in body, f"{where} tries only one Python and gives up"
        assert "pip install --user -r" in body, (
            f"{where} has no plain sentence for somebody whose packages are not "
            f"installed - they get a Python traceback instead."
        )
        assert "not installed on this machine yet" in body, (
            f"{where} never says, in words, that nothing is broken"
        )


# Everything a build has to get right that ONLY goes wrong on somebody else's
# machine. Each of these was found by running Ripple on a managed office laptop
# after it had passed every check on the machine it was written on. A kit that
# describes the product but not these builds a Ripple that works until it is
# carried somewhere, which is the only place it is ever needed.
TRAVELS_BADLY = {
    "taking a port rather than naming one": [
        "TAKE THE PORT BEFORE YOU ANNOUNCE IT",
        "port 0",                       # the last resort when a whole range is refused
        "BIND to each",                 # not "is anything listening"
        "10013",                        # reserved by Windows, not in use
        "excludedportrange",            # how somebody sees the reserved ranges
        "closing things is wasted effort",
    ],
    "starting from a batch file at all": [
        "import uvicorn, fastapi, sqlglot",   # ask the Python, do not trust the name
        "py -3.12",
        "not installed on this machine yet",  # a sentence, not a traceback
    ],
    "installing into the Python that will actually run it": [
        "you have more than one Python",
        "where python",                 # how to see them
        "py --list",
        "py -3.12 -m pip install --user",   # how to stop guessing which one
    ],
    "not claiming a commit that is not yours": [
        "git ls-files --error-unmatch",
    ],
    "reading the SQL as the right language": [
        # The kit used to say "set it to the warehouse this is being built for",
        # which a chat window cannot answer, having seen nothing else. Measured:
        # the phase text names bigquery only inside a war story about two wrong
        # builds. Now the value itself is written out, so require the value.
        'ONE default, and it is the literal string "bigquery"',
        "comes back CLEANER than",      # why a wrong dialect is the worst setting
        "two different languages",      # what happened when two builds disagreed
    ],
    "not inventing a branch for a folder that has none": [
        "EMPTY, and read off the folder",
        'Not\n                       "main"',
    ],
    "reading YOUR folder rather than the practice one": [
        "RIPPLE_REPO is the one that decides whether this was worth building",
        'set "RIPPLE_REPO=',            # what makes the choice last
        "POST /api/repo/folder",        # the route that makes it choosable at all
        "THE FOLDER BOX",               # and the control on the screen
        "Read this folder",             # the words on the button
        "a typo is not an empty repository",   # why a wrong path must be refused
        "CLEAR ANY RESULT ON SCREEN",   # or a finding outlives its repository
    ],
    "getting the two typefaces, which no chat can produce": [
        "The two typefaces, which no chat can hand you",
        "latin-ext",                    # 30 files come back, 16 are wanted
        "User-Agent",                   # or Google sends .ttf instead of .woff2
        "unicode-range",                # losing it costs real download size
        "<link rel=\"stylesheet\" href=\"/static/fonts/fonts.css\">",  # the line to delete
    ],
}


def flowed(doc: str) -> str:
    """The document with its line wrapping taken out.

    It is hand-wrapped prose. Any sentence in it can move across a line break the
    next time a paragraph is edited, and a test that matched an exact substring
    would then fail for a reason that has nothing to do with what it guards.
    """
    return " ".join(doc.split())


@pytest.mark.parametrize("what", sorted(TRAVELS_BADLY))
def test_the_kit_teaches_what_only_breaks_on_somebody_elses_machine(what):
    """Describing the product is not enough. These are the rules whose absence
    is invisible until the build is carried to a different laptop."""
    body = flowed(read(BUILD_KIT))
    missing = [phrase for phrase in TRAVELS_BADLY[what] if flowed(phrase) not in body]
    assert not missing, (
        f"BUILD-KIT.md no longer says {missing} about {what}. A build made from "
        f"it will pass every check on the machine it was written on and fail on "
        f"the one it was written for."
    )


def test_the_kit_makes_somebody_prove_the_port_search_rather_than_trust_it():
    """A phase check that cannot fail teaches nothing.

    Phase 8's check was `curl http://127.0.0.1:8000/api/health`, hard-coded. A
    build that named port 8000 instead of taking one passed it every time, on any
    machine where 8000 happened to be free -- which is every machine except the
    one that matters. And once run.py started choosing its own port, that check
    was also simply wrong.

    Starting Ripple a second time while the first is running is the whole proof,
    costs nothing, and cannot pass by accident.
    """
    body = flowed(read(BUILD_KIT))
    assert "Use the address it actually printed" in body, (
        "the phase check still tells somebody to assume 8000"
    )
    for must in ("open a THIRD Command Prompt",
                 "must print a **different** address",
                 "NAMED a port instead of taking one"):
        assert flowed(must) in body, (
            f"BUILD-KIT.md never makes somebody prove the port search: missing `{must}`"
        )
    # And a prompt to send back, because naming what went wrong without giving
    # the sentence to fix it is what the rescue sections exist to stop.
    after = body.split("NAMED a port instead of taking one", 1)[1][:3000]
    assert "````text" in after, "the port failure names itself but hands over no prompt"


def test_the_folder_tool_refuses_to_ship_a_packaged_program():
    """The whole point of the folder is that it looks like something built by
    hand in a chat window. An .exe, a virtual environment or a .git folder in
    there is the one thing that gives it away, so the tool checks its own output
    rather than trusting the copying above it."""
    tool = BUILD_FOLDER_TOOL.read_text(encoding="utf-8")
    for guard in ("*.exe", ".venv", ".git", "dist"):
        assert guard in tool, f"make_build_folder.py no longer checks for {guard}"
    assert "sys.exit" in tool, "the tool reports problems without failing on them"


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
