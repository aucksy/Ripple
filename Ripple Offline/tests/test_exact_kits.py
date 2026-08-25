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

UI_KIT = ROOT / "BUILD-KIT-UI-EXACT.md"
ENGINE_KIT = ROOT / "BUILD-KIT-ENGINE-EXACT.md"

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


def engine_source(saved_as: str) -> Path:
    """Where a file the engine kit hands over is really kept."""
    if saved_as.startswith("ripple/"):
        return ROOT / "Codebase" / saved_as
    if saved_as.startswith("ripple_offline/"):
        owned = OFF / "demo_files" / saved_as
        return owned if owned.is_file() else OFF / saved_as
    return OFF / "demo_files" / saved_as


# ── both kits ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("kit_path", [UI_KIT, ENGINE_KIT], ids=["ui", "engine"])
def test_the_pieces_join_back_into_the_real_files(kit_path, offline_web):
    """The one that matters. Byte for byte, or it is not the same Ripple."""
    got = rebuilt(read(kit_path))
    assert got, f"{kit_path.name} handed over no files at all"

    for name, mine in got.items():
        src = ui_source(name, offline_web) if name in UI_NAMES else engine_source(name)
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


@pytest.mark.parametrize("kit_path", [UI_KIT, ENGINE_KIT], ids=["ui", "engine"])
def test_the_checksums_the_kit_publishes_are_the_real_ones(kit_path, offline_web):
    """Each kit ships a checker. Stale digests tell somebody their imitation is
    exact, which is the worst answer it could possibly give."""
    kit = read(kit_path)
    for name in rebuilt(kit):
        src = ui_source(name, offline_web) if name in UI_NAMES else engine_source(name)
        digest = hashlib.sha256(src.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        assert digest in kit, (
            f"the checksum {kit_path.name} publishes for {name} is not the "
            f"current one. The kit is stale - run tools/make_exact_kits.py."
        )


@pytest.mark.parametrize("kit_path", [UI_KIT, ENGINE_KIT], ids=["ui", "engine"])
def test_no_piece_is_big_enough_to_be_refused(kit_path):
    """A chat window will not take an unlimited paste, and a piece that gets
    truncated produces a file that looks finished and is not."""
    blocks = re.findall(r"^````\w*\n(.*?)^````\s*$", read(kit_path),
                        re.DOTALL | re.MULTILINE)
    over = [len(b.encode("utf-8")) for b in blocks if len(b.encode("utf-8")) > 45_000]
    assert not over, f"{len(over)} piece(s) over 45 KB in {kit_path.name}: {over}"


@pytest.mark.parametrize("kit_path", [UI_KIT, ENGINE_KIT], ids=["ui", "engine"])
def test_each_kit_is_generated_and_says_so(kit_path):
    """A copy of a source file inside a document is a second copy of it, and the
    second copy is always the one that goes stale."""
    kit = read(kit_path)
    assert TOOL.is_file(), "the generator is missing"
    assert "make_exact_kits.py" in kit, f"{kit_path.name} does not say what generated it"
    assert "edit this by hand" in kit, f"{kit_path.name} does not warn against hand-editing"


@pytest.mark.parametrize("kit_path", [UI_KIT, ENGINE_KIT], ids=["ui", "engine"])
def test_each_kit_is_honest_about_what_it_cannot_give_you(kit_path):
    """Neither kit can contain the SQL parser, and saying so is the difference
    between a kit and a wasted evening."""
    kit = read(kit_path)
    assert "sqlglot" in kit, f"{kit_path.name} never mentions the one thing that must be copied"


# ── the two kits together ─────────────────────────────────────────────────

def test_the_two_kits_do_not_overlap():
    """One hands over the screens, the other the Python. A file appearing in
    both means pasting them both leaves one of the two copies losing."""
    both = set(rebuilt(read(UI_KIT))) & set(rebuilt(read(ENGINE_KIT)))
    assert not both, f"handed over by both kits: {sorted(both)}"


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


def test_the_ui_kit_carries_no_way_out_of_the_machine(offline_web):
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

    kit = read(UI_KIT).lower()
    # Only look inside the handed-over code, never the prose around it.
    code = "\n".join(v for k, v in rebuilt(read(UI_KIT)).items()).lower()
    found = [w for w in webbuild.BANNED if w.lower() in code]
    assert not found, (
        f"{UI_KIT.name} hands over screens containing {found}. That is the "
        f"online front end. The offline one is built from it with those parts "
        f"deleted - regenerate with tools/make_exact_kits.py."
    )
    assert "dialect" in code, (
        "the kit's screens have no way to choose a SQL dialect, so this is not "
        "the offline front end and nobody can point it at a repository."
    )
