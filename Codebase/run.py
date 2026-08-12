"""Start Ripple on this machine.

    python run.py

Then open http://localhost:8000 in a browser. Nothing else to install or set up.
"""
from __future__ import annotations

import os
import sys
import webbrowser

import uvicorn

from ripple.config import settings


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    print("\n  Ripple")
    print(f"  repository : {settings.repo_path}")
    print(f"  SQL read as: {settings.sql_dialect or 'generic'}")
    print(f"  AI         : {'on (' + settings.groq_model + ')' if settings.ai_available() else 'off - rules only'}")
    if not settings.repo_path.exists():
        print(f"\n  WARNING: the repository folder does not exist: {settings.repo_path}")
    print(f"\n  open http://localhost:{port}\n")
    if "--no-browser" not in sys.argv:
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass
    uvicorn.run("ripple.api:app", host="127.0.0.1", port=port, reload="--reload" in sys.argv)


if __name__ == "__main__":
    main()
