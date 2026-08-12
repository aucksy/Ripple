"""Start Ripple Offline.

    python run.py

The built executable runs this same code, so what is tested here is what ships.
There is nothing to install and nothing to configure first: the browser opens,
and if no repository folder has been chosen yet the first screen asks for one.
"""
from __future__ import annotations

import socket
import sys
import traceback
import webbrowser
from pathlib import Path

# Blocking the network is the first thing that happens, before any other part
# of Ripple is imported -- so anything that reaches out at import time is
# caught too, not just anything that reaches out during a request.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ripple_offline import nonet                                    # noqa: E402

nonet.install()

from ripple_offline import paths, prefs                             # noqa: E402
from ripple_offline.engine import frozen                            # noqa: E402

FIRST_PORT = 8000
LAST_PORT = 8020


def log_path() -> Path:
    return paths.app_dir() / "ripple-log.txt"


def start_logging() -> None:
    """With no terminal there is nowhere for a message to go, so make one.

    The built executable opens without a console window on purpose -- a black
    box beside the browser looks like something went wrong. That leaves nothing
    to print to, so everything goes to a file beside the program instead, which
    is also the thing to ask for when someone says it did not start.
    """
    if not frozen():
        return
    handle = open(log_path(), "a", encoding="utf-8", buffering=1)
    sys.stdout = handle
    sys.stderr = handle


def free_port() -> int:
    """The first port nothing else is already using.

    A fixed port is fine until the day something else on the machine has it,
    and then Ripple simply fails to start with no explanation anyone can act on.
    """
    for port in range(FIRST_PORT, LAST_PORT + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
            try:
                probe.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(
        f"Ports {FIRST_PORT} to {LAST_PORT} are all in use on this machine, so Ripple "
        f"has nowhere to listen. Close whatever is using them and start Ripple again.")


def show_failure(message: str) -> None:
    """Say so on screen when there is no terminal to say it in."""
    print(message)
    if not frozen():
        return
    try:
        import tkinter
        from tkinter import messagebox
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror("Ripple could not start", message)
        root.destroy()
    except Exception:
        pass


def main() -> int:
    start_logging()
    try:
        values = prefs.load()
        prefs.apply(values)

        if not frozen():
            # Running from source, the offline front end is rebuilt from the
            # shared one every time, so it can never be a stale copy.
            from ripple_offline import webbuild
            webbuild.build()

        from ripple_offline.app import app

        port = free_port()
        folder = prefs.check_folder(values["repoPath"])
        print("\n  Ripple Offline")
        print(f"  repository : {values['repoPath'] or '(not chosen yet)'}")
        print(f"  folder     : {folder['message']}")
        print(f"  SQL read as: {values['sqlDialect'] or 'generic'}")
        print(f"  settings   : {paths.settings_file()}")
        print(f"  history    : {paths.history_file()}")
        print("  network    : blocked - loopback only")
        print(f"\n  open http://localhost:{port}\n")

        if "--no-browser" not in sys.argv:
            try:
                webbrowser.open(f"http://localhost:{port}")
            except Exception:
                pass

        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
        return 0
    except SystemExit:
        raise
    except Exception as exc:
        detail = f"{exc}\n\nThe full details are in:\n{log_path()}"
        print(traceback.format_exc())
        show_failure(detail)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
