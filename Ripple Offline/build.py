"""Make the folder a colleague copies onto the locked-down machine.

    python build.py

What comes out is ``dist/Ripple Offline``: an executable, the things it needs
beside it, and nothing to install. Copy that folder anywhere and double-click.

Two things are pulled in here rather than kept as copies, which is the whole
point of how this is put together:

* the analysis engine, from ``Codebase/ripple`` — one copy, so the offline
  build can never quietly fall behind the online one;
* the front end, built from ``Codebase/web`` with the parts that reach out
  deleted.

Both are read at build time. Neither exists as a second copy on disk.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ripple_offline import webbuild                                  # noqa: E402
from ripple_offline.engine import SHARED_DIR, SHARED_ENGINE          # noqa: E402

APP_NAME = "Ripple Offline"
WORK = HERE / "build"
DIST = HERE / "dist"
WEB_OUT = WORK / "web"
ICON = HERE / "assets" / "ripple.ico"
SAMPLES = SHARED_DIR / "samples"


def say(message: str) -> None:
    print(f"  {message}", flush=True)


def folder_size(path: Path) -> str:
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return f"{total / 1_000_000:.0f} MB"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Ripple Offline for Windows.")
    parser.add_argument("--keep-work", action="store_true",
                        help="leave PyInstaller's working files behind, for debugging")
    args = parser.parse_args()

    print(f"\n  Building {APP_NAME}\n")

    if not (SHARED_ENGINE / "api.py").is_file():
        say(f"ERROR: the shared engine is not at {SHARED_ENGINE}.")
        say("Ripple Offline has no copy of its own on purpose. Nothing can be built without it.")
        return 1
    say(f"engine     : {SHARED_ENGINE}  (read, never copied)")

    # ── the front end, with everything that reaches out removed ────────────
    try:
        webbuild.build(out_dir=WEB_OUT)
    except webbuild.BuildError as exc:
        say("ERROR: the offline front end could not be built.")
        say(str(exc))
        return 1
    say(f"front end  : built from {SHARED_DIR / 'web'} into {WEB_OUT}")

    # ── the executable ─────────────────────────────────────────────────────
    if DIST.exists():
        shutil.rmtree(DIST, ignore_errors=True)
    command = [
        sys.executable, "-m", "PyInstaller",
        str(HERE / "run.py"),
        "--name", APP_NAME,
        "--noconfirm",
        "--clean",
        # A folder rather than one big file: it starts straight away instead of
        # unpacking itself into a temporary folder on every launch, and some
        # locked-down machines refuse to run programs out of one.
        "--onedir",
        # No console window. Nothing is lost -- everything it would have said
        # goes to ripple-log.txt beside the program.
        "--noconsole",
        # Where the shared engine is found at build time. This is the line that
        # keeps there being one copy of it.
        "--paths", str(SHARED_DIR),
        "--add-data", f"{WEB_OUT}{os.pathsep}web",
        "--collect-all", "sqlglot",
        "--collect-all", "extract_msg",
        "--distpath", str(DIST),
        "--workpath", str(WORK / "pyinstaller"),
        "--specpath", str(WORK),
    ]
    if ICON.is_file():
        command += ["--icon", str(ICON)]
    say("packaging  : PyInstaller (this takes a minute)")
    started = time.time()
    done = subprocess.run(command, capture_output=True, text=True)
    if done.returncode != 0:
        say("ERROR: PyInstaller failed.")
        print(done.stdout[-4000:])
        print(done.stderr[-4000:])
        return 1
    say(f"packaged   : in {time.time() - started:.0f} seconds")

    out = DIST / APP_NAME
    exe = out / f"{APP_NAME}.exe"
    if not exe.is_file():
        say(f"ERROR: PyInstaller reported success but {exe} is not there.")
        return 1

    # ── a couple of example notifications, so it can be tried immediately ──
    if SAMPLES.is_dir():
        target = out / "example-notifications"
        target.mkdir(exist_ok=True)
        for f in SAMPLES.glob("*.eml"):
            shutil.copyfile(f, target / f.name)
        say(f"examples   : {len(list(target.glob('*.eml')))} example emails to try it with")

    if not args.keep_work:
        shutil.rmtree(WORK / "pyinstaller", ignore_errors=True)

    print()
    say(f"Done. {folder_size(out)} in {out}")
    say(f"Copy that whole folder to the other machine and double-click {exe.name}.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
