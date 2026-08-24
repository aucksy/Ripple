r"""Assemble a Ripple that can be carried onto a machine which installs nothing.

    ..\Codebase\.venv\Scripts\python tools\make_demo_snapshot.py

Writes D:\Apps\Ripple\RIPPLE COPILOT DEMO -- the engine, the wrapper, the
screens, the SQL parser and a pretend pipeline, in one folder that runs on
Python's own library alone.

WHY THIS EXISTS. The packaged build needs FastAPI to run and PyInstaller to
package, and both are installs. On a laptop that refuses installs neither is
reachable, so this leaves both behind: the web layer is rewritten on
http.server, and there is no .exe. What comes out is started with
``python run.py``.

WHAT IT DOES NOT DO. It does not touch the product. Everything it copies is
copied unchanged, and the four files that cannot be copied -- the web layer, the
launcher, the engine finder and a smoke test -- are kept in the snapshot folder
and put back each time this runs, so re-running refreshes the copied parts
without losing them.

THE SNAPSHOT IS A FORK, DELIBERATELY, AND ONLY THIS ONCE. The product keeps ONE
engine and never copies it, because two copies drift and the fork is always the
one running where nobody can check it. A folder carried to another machine has
nothing to reach back to, so it carries its own. That is why it is git-ignored,
why it says so on its own settings screen, and why the way to move it forward is
to run this again rather than to edit anything inside it.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(r"D:\Apps\Ripple")
CODE = ROOT / "Codebase"
OFF = ROOT / "Ripple Offline"
DEMO = ROOT / "RIPPLE COPILOT DEMO"

# The engine, exactly as it ships. ai.py, api.py and scanner/github.py are left
# out: all three reach the network, and none of them is on any path this build
# can take.
ENGINE = ["__init__.py", "build_info.py", "catalog.py", "config.py", "narrative.py",
          "notification.py", "production.py", "progress.py", "providers.py", "store.py"]
SCANNER = ["__init__.py", "dialectcompat.py", "lineage.py", "repo.py", "rescue.py",
           "sqlread.py", "templating.py"]
# The offline wrapper. app.py is rewritten by hand (FastAPI to http.server) and
# webbuild.py is only needed on the machine that assembles this.
# __init__.py and engine.py are NOT here. The product's pair points the import
# path at Codebase, which is right for the product and wrong for a folder that
# has been carried somewhere. The snapshot keeps its own.
WRAPPER = ["folderpick.py", "lifecycle.py", "nonet.py", "paths.py", "prefs.py",
           "synced.py"]

KEPT_WHY = """The snapshot owns four things the product cannot give it: a web
layer built on http.server rather than FastAPI, a launcher for it, an engine
finder that looks inside this folder instead of reaching back into Codebase, and
a smoke test written for unittest. Re-running this refreshes everything else
around them."""


def fresh(p: Path) -> None:
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True)


def main() -> None:
    keep = {}
    # Everything that cannot simply be copied from the product. Leave any of
    # these out and re-running this quietly puts the product's own version back
    # -- and the product's engine.py reaches into Codebase, which does not exist
    # on the machine this folder is carried to. It would still work here, next
    # to Codebase, and fail there. See KEPT_WHY below.
    for name in ("ripple_offline/__init__.py", "ripple_offline/engine.py",
                 "ripple_offline/app.py", "ripple_offline/webserver.py",
                 "run.py", "HOW-TO-RUN-THIS.md", "tests/test_smoke.py",
                 "START RIPPLE.bat"):
        f = DEMO / name
        if f.is_file():
            keep[name] = f.read_text(encoding="utf-8")

    fresh(DEMO)
    (DEMO / "ripple" / "scanner").mkdir(parents=True)
    (DEMO / "ripple_offline").mkdir()
    (DEMO / "tests").mkdir()

    for n in ENGINE:
        shutil.copy2(CODE / "ripple" / n, DEMO / "ripple" / n)
    for n in SCANNER:
        shutil.copy2(CODE / "ripple" / "scanner" / n, DEMO / "ripple" / "scanner" / n)
    for n in WRAPPER:
        shutil.copy2(OFF / "ripple_offline" / n, DEMO / "ripple_offline" / n)
    print(f"engine   : {len(ENGINE) + len(SCANNER)} files")
    print(f"wrapper  : {len(WRAPPER)} files")

    # The SQL parser, as a plain folder. Pure Python, no compiled parts, so it
    # travels by being copied -- which is the whole point on a machine where
    # nothing can be installed.
    src = CODE / ".venv" / "Lib" / "site-packages" / "sqlglot"
    shutil.copytree(src, DEMO / "sqlglot",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    n = len(list((DEMO / "sqlglot").rglob("*.py")))
    mb = sum(f.stat().st_size for f in (DEMO / "sqlglot").rglob("*")) / 1_000_000
    print(f"sqlglot  : {n} files, {mb:.1f} MB")

    # The front end, generated from the shared one the same way the real build
    # does it, so the screens here are the screens there.
    sys.path.insert(0, str(OFF))
    from ripple_offline import webbuild                       # noqa: PLC0415
    webbuild.build(out_dir=DEMO / "web")
    print(f"web      : {len(list((DEMO / 'web').rglob('*')))} files")

    shutil.copytree(CODE / "mockrepo", DEMO / "mockrepo",
                    ignore=shutil.ignore_patterns("__pycache__"))
    print(f"mockrepo : {len(list((DEMO / 'mockrepo').rglob('*.sql')))} .sql files to scan")

    for name, body in keep.items():
        out = DEMO / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
    if keep:
        print(f"kept     : {', '.join(keep)}")

    total = len(list(DEMO.rglob("*.py"))) - n
    print(f"\nPython files a person has to have (sqlglot not counted): {total}")


main()
