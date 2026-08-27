r"""Assemble the folder somebody ends up with after following BUILD-KIT.md.

    ..\Codebase\.venv\Scripts\python tools\make_build_folder.py

Writes D:\Apps\Ripple\RIPPLE COPILOT DEMO -- Ripple laid out exactly as the
kit's "this is what you are building towards" picture lays it out: run.py, a
start-ripple.bat, ripple\, web\, tests\, mockrepo\. Started with a double-click.
No .exe, no virtual environment, no .git, nothing the kit does not describe.

WHY THIS EXISTS. Ripple gets rebuilt by hand, in a chat window, on a machine
that has never seen this repository. Before doing that for real it is worth
having the finished shape sitting on disk to run and to look at -- and a folder
assembled by hand for that purpose goes stale the first time the product moves,
silently, because nothing compares the two. So it is generated, and refreshing
it is one command.

WHAT IT NEEDS ON THE MACHINE. Exactly what the kit installs, and by the same
command: pip install --user sqlglot fastapi uvicorn pydantic and the rest. This
folder deliberately carries no virtual environment and no vendored parser,
because a folder built from the kit has neither.

TWO SHAPES, ONE FOLDER NAME. make_demo_snapshot.py writes this same folder in a
different shape -- the one that runs where nothing at all can be installed,
carrying its own copy of the SQL parser and a web layer rewritten on
http.server. The two cannot both be there. Whichever tool ran last is what is on
disk. Both say so when they finish.

NOTHING IN THE OUTPUT IS EDITED BY HAND. Every file is copied from Codebase, and
the batch file is written here, from the four lines the kit gives. To move the
folder forward, run this again.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(r"D:\Apps\Ripple")
CODE = ROOT / "Codebase"

# Somewhere else, if you say so:  python tools\make_build_folder.py C:\ripple-build
# Two copies of this folder is two copies that drift, so there is normally one.
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "RIPPLE COPILOT DEMO"

# The four lines the kit tells somebody to put in start-ripple.bat. Written
# here rather than copied from Codebase\start-ripple.bat, which carries extra
# lines for finding this repository's virtual environment -- a folder built
# from the kit has no virtual environment to find.
BAT = "@echo off\r\ncd /d \"%~dp0\"\r\npython run.py\r\nif errorlevel 1 pause\r\n"

# Tests left behind, each for a reason that is about this folder and not about
# the test. Named one by one, because silently dropping a test is how a suite
# stops proving anything.
TESTS_LEFT_OUT = {
    # Reads BUILD-KIT.md itself. A folder built FROM the kit has no copy of it,
    # so the test cannot pass, and its presence would be odd in a folder that is
    # meant to look like somebody's own work.
    "test_build_kits.py":
        "reads BUILD-KIT.md, which is not in a folder built from it",
    # Checks that the hosting entry point loads the same application object as
    # run.py. The kit builds no hosting entry point, so there is nothing to check.
    "test_one_engine.py":
        "checks api/index.py, which the kit does not build",
}

# Copied whole. Derived by walking the disk rather than typed out, so a file
# added to the product arrives here without anybody remembering to come back.
TREES = [
    ("ripple", "*.py"),        # the engine, including scanner/
    ("mockrepo", "*"),         # the pretend pipeline to scan
    ("samples", "*"),          # the example emails, for the upload box
]

# Everything at the top of Codebase that must NOT come, and why.
TOP_LEVEL_SKIPPED = {
    ".venv": "a virtual environment; the kit installs with pip --user instead",
    "api": "the hosting entry point; the kit builds a laptop, not a host",
    "ripple.db": "saved analyses from this machine",
    "vercel.json": "hosting configuration",
    ".vercelignore": "hosting configuration",
    ".python-version": "a tool-manager file the kit never mentions",
    "requirements-dev.txt": "the tools used to develop the product, not to run it",
    "README.md": "written for this repository, not for a folder built from the kit",
    "start-ripple.bat": "rewritten below, without this repository's venv lines",
}


def say(line: str) -> None:
    print(f"   {line}")


def empty(folder: Path) -> None:
    """Clear the folder without removing the folder itself.

    Removing it fails with WinError 32 whenever any shell has its current
    directory inside -- and a half-finished remove is how this folder was lost
    once already. Everything written here comes from Codebase, which is in git,
    so emptying costs one re-run and never costs a file.
    """
    folder.mkdir(parents=True, exist_ok=True)
    for child in folder.iterdir():
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
        else:
            child.unlink(missing_ok=True)
    left = list(folder.iterdir())
    if left:
        sys.exit(f"could not empty {folder} - still holds {[p.name for p in left]}. "
                 f"Close any window whose current folder is inside it.")


def copy_tree(name: str, pattern: str) -> int:
    src = CODE / name
    if not src.is_dir():
        sys.exit(f"{src} is missing - nothing to copy")
    n = 0
    for p in sorted(src.rglob(pattern)):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        dest = OUT / name / p.relative_to(src)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        n += 1
    return n


def main() -> None:
    if not CODE.is_dir():
        sys.exit(f"{CODE} is missing")

    print(f"\nBuilding the kit-shaped Ripple into {OUT}\n")
    empty(OUT)

    # run.py and the list of what to install. Both are named in the kit.
    for name in ("run.py", "requirements.txt"):
        shutil.copy2(CODE / name, OUT / name)
    say(f"root       : run.py, requirements.txt")

    for name, pattern in TREES:
        say(f"{name:<11}: {copy_tree(name, pattern)} files")

    # The screens. index.html asks for /static/fonts/fonts.css, so the fonts
    # come too -- leave them out and every screen quietly falls back to Segoe UI
    # and stops looking like Ripple.
    (OUT / "web").mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "styles.css", "app.js"):
        shutil.copy2(CODE / "web" / name, OUT / "web" / name)
    shutil.copytree(CODE / "web" / "fonts", OUT / "web" / "fonts")
    fonts = len(list((OUT / "web" / "fonts").iterdir()))
    say(f"web        : 3 screens, {fonts} font files")

    (OUT / "tests").mkdir(parents=True, exist_ok=True)
    shutil.copy2(CODE / "tests" / "conftest.py", OUT / "tests" / "conftest.py")
    kept = 0
    for p in sorted((CODE / "tests").glob("test_*.py")):
        if p.name in TESTS_LEFT_OUT:
            continue
        shutil.copy2(p, OUT / "tests" / p.name)
        kept += 1
    say(f"tests      : {kept} files kept")
    for name, why in sorted(TESTS_LEFT_OUT.items()):
        say(f"             left out {name} - {why}")

    (OUT / "start-ripple.bat").write_bytes(BAT.encode("ascii"))
    say("start-ripple.bat written")

    # Check its own work rather than trust the copying above.
    problems = []
    for pattern, what in ((("*.exe",), "a packaged program"),
                          ((".venv",), "a virtual environment"),
                          ((".git",), "version history"),
                          (("dist", "build"), "packaging output")):
        for pat in pattern:
            hits = [p for p in OUT.rglob(pat)]
            if hits:
                problems.append(f"{what} found: {[str(p) for p in hits[:3]]}")
    must_exist = ["run.py", "start-ripple.bat", "ripple/api.py",
                  "ripple/scanner/sqlread.py", "web/app.js", "web/fonts/fonts.css"]
    for rel in must_exist:
        if not (OUT / rel).is_file():
            problems.append(f"missing {rel}")
    if problems:
        sys.exit("\n".join(["the folder is wrong:"] + problems))

    total = sum(1 for p in OUT.rglob("*") if p.is_file())
    print(f"\n   {total} files. No .exe, no virtual environment, no version history.")
    print(f"   Start it by double-clicking {OUT / 'start-ripple.bat'}")
    print("   This folder is now the KIT-SHAPED Ripple. Running "
          "make_demo_snapshot.py replaces it with the no-install one.\n")


main()
