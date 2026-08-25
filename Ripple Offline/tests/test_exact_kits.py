"""Do the two exact kits actually put Ripple back together?

Their whole promise is one sentence: paste these pieces in order and you have
Ripple's own files, not something that resembles them. A kit that drops a line,
cuts one in half, or splits inside a fenced block breaks that promise while
still looking completely normal to read.

So these tests do what a person following a kit does — take the fenced blocks
out in order, join them, and compare to the real file byte for byte.

They also fail when a kit has gone stale. The kits are generated from the live
files; edit app.js and forget to regenerate, and the kit hands somebody last
week's screens together with a checksum saying they are current. That is worse
than having no kit at all, because the check the kit ships would say "exact".

Every path read here is a tracked one. Nothing reads the demo output folder,
which would be green on this machine and missing everywhere else.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
OFF = ROOT / "Ripple Offline"
TOOL = OFF / "tools" / "make_exact_kits.py"
SNAPSHOT_TOOL = OFF / "tools" / "make_demo_snapshot.py"

HERE_KIT = ROOT / "RUN-RIPPLE-HERE.md"                 # pip works
NO_INSTALL_KIT = ROOT / "RUN-RIPPLE-HERE-NO-INSTALLS.md"  # pip is blocked

UI_NAMES = ("web/index.html", "web/styles.css", "web/app.js")


@pytest.fixture(scope="session")
def offline_web(tmp_path_factory) -> Path:
    """The screens as the offline build really makes them.

    NOT ``Codebase/web``. Those are the online screens; the offline ones are
    built from them with the GitHub source and the AI key box deleted and the
    folder-and-dialect screens added. Comparing the kit against the online copy
    would pass while the kit handed a key box to a machine that must have no way
    out, and left out the only screen that can point Ripple at a repository.
    """
    import sys
    sys.path.insert(0, str(OFF))
    from ripple_offline import webbuild
    out = tmp_path_factory.mktemp("offline-web")
    webbuild.build(out_dir=out)
    return out


def ui_source(name: str, web: Path) -> Path:
    return web / name.split("/", 1)[1]

BLOCK = re.compile(
    r"^### ([\w./-]+\.\w+)(?: — piece \d+ of \d+)?\s*\n"   # which file
    r".*?"                                                 # the instruction
    r"^````\w*\n(.*?)^````\s*$",                           # the block
    re.DOTALL | re.MULTILINE,
)


def read(kit: Path) -> str:
    if not kit.is_file():
        pytest.fail(f"{kit.name} is missing - run tools/make_exact_kits.py")
    return kit.read_text(encoding="utf-8")


def rebuilt(kit_text: str) -> dict[str, str]:
    """Reassemble every file the way somebody following the kit would."""
    out: dict[str, list[str]] = {}
    for m in BLOCK.finditer(kit_text):
        out.setdefault(m.group(1), []).append(m.group(2))
    return {name: "".join(pieces) for name, pieces in out.items()}


def source_for(kit_path: Path, saved_as: str, web: Path) -> Path:
    """Where a file a kit hands over is really kept.

    The two kits disagree about web/ on purpose. The ONLINE kit hands over
    Codebase/web as it stands; the locked-down one hands over what webbuild
    makes of it, with the key box and the GitHub source deleted.
    """
    if kit_path == HERE_KIT:
        return ROOT / "Codebase" / saved_as
    if saved_as in UI_NAMES:
        return web / saved_as.split("/", 1)[1]
    return engine_source(saved_as)


def engine_source(saved_as: str) -> Path:
    """Where a file the engine kit hands over is really kept."""
    if saved_as.startswith("ripple/"):
        return ROOT / "Codebase" / saved_as
    if saved_as.startswith("ripple_offline/"):
        owned = OFF / "demo_files" / saved_as
        return owned if owned.is_file() else OFF / saved_as
    return OFF / "demo_files" / saved_as


# ── both kits ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("kit_path", [HERE_KIT, NO_INSTALL_KIT], ids=["here", "no-installs"])
def test_the_pieces_join_back_into_the_real_files(kit_path, offline_web):
    """The one that matters. Byte for byte, or it is not the same Ripple."""
    got = rebuilt(read(kit_path))
    assert got, f"{kit_path.name} handed over no files at all"

    for name, mine in got.items():
        src = source_for(kit_path, name, offline_web)
        assert src.is_file(), f"{kit_path.name} hands over {name}, which is not in the repo"
        real = src.read_text(encoding="utf-8")
        if mine == real:
            continue
        rl, ml = real.splitlines(), mine.splitlines()
        where = next((i for i, (a, b) in enumerate(zip(rl, ml), 1) if a != b),
                     min(len(rl), len(ml)) + 1)
        pytest.fail(
            f"{name} does not come back whole from {kit_path.name}. Real file "
            f"{len(rl):,} lines, rebuilt {len(ml):,} lines, first difference at "
            f"line {where}. Re-run tools/make_exact_kits.py."
        )


@pytest.mark.parametrize("kit_path", [HERE_KIT, NO_INSTALL_KIT], ids=["here", "no-installs"])
def test_the_checksums_the_kit_publishes_are_the_real_ones(kit_path, offline_web):
    """Each kit ships a checker. Stale digests tell somebody their imitation is
    exact, which is the worst answer it could possibly give."""
    kit = read(kit_path)
    for name in rebuilt(kit):
        src = source_for(kit_path, name, offline_web)
        digest = hashlib.sha256(src.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        assert digest in kit, (
            f"the checksum {kit_path.name} publishes for {name} is not the "
            f"current one. The kit is stale - run tools/make_exact_kits.py."
        )


@pytest.mark.parametrize("kit_path", [HERE_KIT, NO_INSTALL_KIT], ids=["here", "no-installs"])
def test_no_piece_is_big_enough_to_be_refused(kit_path):
    """A chat window will not take an unlimited paste, and a piece that gets
    truncated produces a file that looks finished and is not."""
    blocks = re.findall(r"^````\w*\n(.*?)^````\s*$", read(kit_path),
                        re.DOTALL | re.MULTILINE)
    over = [len(b.encode("utf-8")) for b in blocks if len(b.encode("utf-8")) > 45_000]
    assert not over, f"{len(over)} piece(s) over 45 KB in {kit_path.name}: {over}"


@pytest.mark.parametrize("kit_path", [HERE_KIT, NO_INSTALL_KIT], ids=["here", "no-installs"])
def test_each_kit_is_generated_and_says_so(kit_path):
    """A copy of a source file inside a document is a second copy of it, and the
    second copy is always the one that goes stale."""
    kit = read(kit_path)
    assert TOOL.is_file(), "the generator is missing"
    assert "make_exact_kits.py" in kit, f"{kit_path.name} does not say what generated it"
    assert "edit this by hand" in kit, f"{kit_path.name} does not warn against hand-editing"


@pytest.mark.parametrize("kit_path", [HERE_KIT, NO_INSTALL_KIT], ids=["here", "no-installs"])
def test_each_kit_is_honest_about_what_it_cannot_give_you(kit_path):
    """Neither kit can contain the SQL parser, and saying so is the difference
    between a kit and a wasted evening."""
    kit = read(kit_path)
    assert "sqlglot" in kit, f"{kit_path.name} never mentions the one thing that must be copied"


# ── the two kits together ─────────────────────────────────────────────────

def test_each_kit_is_a_whole_Ripple_on_its_own():
    """Neither is half a job.

    These used to be three files -- one for the screens, one for the engine, one
    for everything -- and somebody following the first two had to know they were
    a pair. They are one kit each now: pick the one that matches your machine,
    follow it to the end, and you have Ripple. So each has to carry BOTH halves,
    and a kit that quietly lost one would still read perfectly well.
    """
    for kit_path in (HERE_KIT, NO_INSTALL_KIT):
        got = set(rebuilt(read(kit_path)))
        screens = {n for n in got if n.startswith("web/")}
        engine = {n for n in got if n.startswith("ripple")}
        assert screens, f"{kit_path.name} hands over no screens"
        assert engine, f"{kit_path.name} hands over no engine"
        assert "web/app.js" in got, f"{kit_path.name} is missing web/app.js"
        assert any(n.endswith("run.py") for n in got), \
            f"{kit_path.name} hands over no way to start it"


def test_the_two_kits_are_told_apart_by_pip_and_say_so():
    """The words 'online' and 'offline' mean two opposite things depending on
    who is saying them -- hosted-or-not to most people, network-or-not inside
    this repository. Both kits were named with the second meaning and read with
    the first, and somebody went to the wrong file because of it. Neither name
    carries either word now, and the one for a normal machine says out loud that
    running it here and hosting it later are the same files.
    """
    for kit_path in (HERE_KIT, NO_INSTALL_KIT):
        assert "online" not in kit_path.name.lower(), f"{kit_path.name} says 'online'"
        assert "offline" not in kit_path.name.lower(), f"{kit_path.name} says 'offline'"
    here = read(HERE_KIT)
    assert "pip install" in here, "the usual kit never says what to install"
    assert "same files" in here, (
        "RUN-RIPPLE-HERE.md does not say that running it here and hosting it "
        "later are the same files, which is the thing people get wrong."
    )
    assert "pip install" in read(NO_INSTALL_KIT), (
        "the no-installs kit does not tell somebody to try pip first, so people "
        "who could use the shorter kit will follow the longer one."
    )


def test_the_engine_kit_matches_what_the_snapshot_actually_ships():
    """The engine kit and the demo snapshot must describe the same Ripple.

    The snapshot folder is the configuration proven to run with nothing
    installed. If the kit hands over a different set of files, it is handing
    over a Ripple nobody has ever run.
    """
    tool = TOOL.read_text(encoding="utf-8")
    snap = SNAPSHOT_TOOL.read_text(encoding="utf-8")
    for listname in ("ENGINE", "SCANNER", "WRAPPER"):
        a = re.search(listname + r" = \[(.*?)\]", tool, re.DOTALL)
        b = re.search(listname + r" = \[(.*?)\]", snap, re.DOTALL)
        assert a and b, f"{listname} is missing from one of the two tools"
        names_a = set(re.findall(r'"([^"]+)"', a.group(1)))
        names_b = set(re.findall(r'"([^"]+)"', b.group(1)))
        assert names_a == names_b, (
            f"{listname} differs: the exact kit has {sorted(names_a - names_b)} "
            f"that the snapshot does not, and is missing {sorted(names_b - names_a)}."
        )


def test_the_no_install_screens_carry_no_way_out_of_the_machine(offline_web):
    """The bug this test was written for, caught the day the kit was made.

    The first version of the UI kit handed over ``Codebase/web/app.js`` — the
    ONLINE screens. They contain a box asking for an AI provider key and a
    button that downloads a repository from GitHub. Pasted onto a locked-down
    laptop that is the exact opposite of what the machine is for, and the
    settings screen it does need, choosing a folder and a dialect, was not in
    there at all.

    The offline build already refuses to ship those words. So must the kit.
    """
    import sys
    sys.path.insert(0, str(OFF))
    from ripple_offline import webbuild

    # Only the SCREENS, and only the handed-over code rather than the prose
    # around it. webbuild applies this list to the front end alone, and it has
    # to: ripple/providers.py is a table of which company a pasted key belongs
    # to, so it names all three of them. It opens no connection, and it ships
    # inside the no-install build that is proven to run.
    code = "\n".join(v for k, v in rebuilt(read(NO_INSTALL_KIT)).items()
                     if k.startswith("web/")).lower()
    found = [w for w in webbuild.BANNED if w.lower() in code]
    assert not found, (
        f"{NO_INSTALL_KIT.name} hands over screens containing {found}. That is the "
        f"online front end. The offline one is built from it with those parts "
        f"deleted - regenerate with tools/make_exact_kits.py."
    )
    assert "dialect" in code, (
        "the kit's screens have no way to choose a SQL dialect, so this is not "
        "the offline front end and nobody can point it at a repository."
    )


def test_every_empty_file_gets_its_own_command():
    """A kit that lists two empty files and gives one command creates one of them.

    The empty __init__.py files are the ones people skip, because everything
    works without them. What they actually stop is Python merging EVERY folder
    called `ripple` on the machine into one package -- measured: without the
    file, `ripple.__path__` spans two folders and a module from an unrelated
    decoy folder imports as though it were Ripple's own. Nothing errors and
    nothing warns, which is the one failure this tool exists to make impossible.
    """
    kit = read(HERE_KIT)
    if "## First: the empty files" not in kit:
        pytest.skip("this kit hands over no empty files")
    section = kit.split("## First: the empty files")[1].split("\n---")[0]
    listed = re.findall(r"^\s{4}([\w./]+\.py)$", section, re.MULTILINE)
    assert listed, "the section lists no files"
    for name in listed:
        want = "type nul > " + name.replace("/", "\\")
        assert want in section, (
            f"{HERE_KIT.name} lists {name} as an empty file to create but gives "
            f"no command for it. Somebody creates the ones that have a line."
        )
    assert "namespace package" in section, (
        "the section does not say what skipping these actually costs, so it reads "
        "as housekeeping somebody can skip - and everything does work without them."
    )


# ── the page that decides which file somebody opens ───────────────────────

START_HERE = ROOT / "START-HERE.md"


def test_start_here_names_every_kit_and_no_kit_that_is_gone():
    """The index is the first thing anybody reads, so it is the worst thing to
    let go stale.

    It sent somebody to a file called BUILD-KIT-ONLINE-EXACT.md when what they
    wanted was to run Ripple on their own laptop, because "online" reads as
    "hosted" to everybody except this repository. Renaming fixed that; this
    stops the index drifting away from the files that actually exist.
    """
    assert START_HERE.is_file(), "START-HERE.md is missing"
    page = START_HERE.read_text(encoding="utf-8")

    on_disk = {p.name for p in ROOT.glob("*.md")} - {"START-HERE.md"}
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
    page = START_HERE.read_text(encoding="utf-8")
    assert "same files" in page, "START-HERE.md does not say it plainly"

    hosted = (ROOT / "Codebase" / "api" / "index.py").read_text(encoding="utf-8")
    local = (ROOT / "Codebase" / "run.py").read_text(encoding="utf-8")
    assert "ripple.api import app" in hosted, "the hosted entry no longer loads ripple.api"
    assert "ripple.api:app" in local or "ripple.api import app" in local, \
        "run.py no longer starts ripple.api - the claim in START-HERE.md is stale"


def test_the_setup_commands_are_there_and_in_order():
    """Three commands before the first paste, and the order is the whole point.

    On a managed laptop pip is often absent, and `pip` then says "not
    recognized" - which reads as a locked door and is not one. And pypi.org is
    blocked, so pip left pointing at it hangs and times out, which reads as a
    broken machine rather than a blocked address. Both are one command each, and
    both have to happen BEFORE the install or the install is what fails and the
    reason is two steps back.
    """
    kit = read(HERE_KIT)
    wanted = [
        "python -m ensurepip --upgrade --user",
        "python -m pip config set global.index-url",
        "python -m pip install --user sqlglot==",
    ]
    where = []
    for cmd in wanted:
        assert cmd in kit, f"{HERE_KIT.name} no longer carries `{cmd}`"
        where.append(kit.index(cmd))
    assert where == sorted(where), (
        f"the setup commands are out of order in {HERE_KIT.name}. ensurepip, "
        f"then the mirror, then the install - any other order and the step that "
        f"fails is not the step that is wrong."
    )


def test_the_install_line_pins_every_version():
    """An unpinned install takes whatever was published this morning. sqlglot
    renamed three parse-tree keys between majors and the renames are silent, so
    a newer one switches features off with nothing raised anywhere."""
    kit = read(HERE_KIT)
    line = next(l for l in kit.splitlines() if l.startswith("python -m pip install --user"))
    packages = [p for p in line.split()[5:] if not p.startswith("-")]
    unpinned = [p for p in packages if "==" not in p]
    assert not unpinned, f"not pinned to a version: {unpinned}"
    assert "sqlglot==30.17.0" in packages, (
        "the pinned sqlglot is not 30.17.0, which is the version every rule in "
        "the build kits was written against."
    )


# ── the repair kit ────────────────────────────────────────────────────────

REPAIR_KIT = ROOT / "BUILD-KIT-REPAIR.md"
REPAIR_TOOL = OFF / "tools" / "make_repair_kit.py"


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


def test_the_rescue_prompts_for_the_two_hard_phases_are_in_both_kits():
    """Phases 4 and 8 are where a build stalls, and both kits already NAMED what
    goes wrong without ever giving somebody the sentence to send back. A person
    in a broken window at ten at night does not compose one."""
    for kit_name in ("BUILD-KIT.md", "BUILD-KIT-OFFLINE.md"):
        kit = (ROOT / kit_name).read_text(encoding="utf-8")
        for phase in (4, 8):
            assert f"## When Phase {phase} goes wrong" in kit, \
                f"{kit_name} has no rescue section for Phase {phase}"
        # Each rescue block has to be pasteable, not described.
        four = kit.split("## When Phase 4 goes wrong")[1].split("# PHASE 5")[0]
        eight = kit.split("## When Phase 8 goes wrong")[1].split("# PHASE 9")[0]
        assert four.count("````text") >= 5, f"{kit_name}: Phase 4 has too few ready prompts"
        assert eight.count("````text") >= 6, f"{kit_name}: Phase 8 has too few ready prompts"
        # The two silent ones that cost an evening each.
        assert "0.0.0.0" in eight, f"{kit_name}: nothing about binding to 0.0.0.0"
        assert "dialectcompat" in four, f"{kit_name}: nothing about reading a parse-tree key directly"
