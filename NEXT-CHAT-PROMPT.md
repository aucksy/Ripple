# Prompt: report issues with Ripple

Paste everything below the line into a new Claude Code session started in
`D:\Apps\Ripple`. Fill in the ISSUES section first — everything above it is
context the session needs, and everything below it is what you actually want.

---

I want to report some issues with Ripple. Read this whole message before doing
anything, then start with the issues at the bottom.

## WHERE THINGS ARE

- Repository root: `D:\Apps\Ripple` → github.com/aucksy/Ripple, branch `main`.
  Commit and push straight to `main` yourself. No branches, no pull requests.
- **Online Ripple**: `D:\Apps\Ripple\Codebase` — FastAPI plus plain HTML, CSS and
  JavaScript. No build step, no framework.
  - Run it: `.venv\Scripts\python run.py` then open http://localhost:8000
  - Tests: `.venv\Scripts\python -m pytest tests -q` → **141 pass**
- **Ripple Offline**: `D:\Apps\Ripple\Ripple Offline` — the same app packaged for
  a machine with no internet. A wrapper, not a fork.
  - Run it from source: `..\Codebase\.venv\Scripts\python run.py`
  - Tests: `..\Codebase\.venv\Scripts\python -m pytest tests -q` → **98 pass**
  - Build the Windows program: `..\Codebase\.venv\Scripts\python build.py`
    → produces `dist\Ripple Offline`, about 44 MB, double-click to run
- Prototype (design source of truth, READ ONLY — never edit):
  `D:\Apps\Ripple\Prototype\Ripple Prototype.html`
- `D:\Apps\CLAUDE.md` loads automatically — follow it. Above all: write to me in
  plain English (I am a product manager, not a coder), and end every session with
  the Done / Needs you / Next block.

## THE ONE DESIGN RULE THAT MUST NOT BE BROKEN

Ripple Offline holds **no copy** of the analysis engine and **no copy** of the
front end. Two copies would drift, and the drifting one would be the build
running where nobody can check it.

- Its build script reads the engine straight out of `Codebase\ripple`.
- Its screens are generated from `Codebase\web\app.js`: the blocks between
  `//<online-only>` and `//</online-only>` are deleted, then
  `Ripple Offline\web\offline.js` is appended.

If you change the shared front end, keep those markers valid — deleting a
marked block's lines has to leave working JavaScript. The offline build checks
its own output and fails loudly if anything that reaches out survives, so a
failing offline build after an online edit usually means a marker moved, not
that the offline app is broken. **If a fix seems to need a fork, stop and tell
me why before copying anything.**

## RULES THAT STILL APPLY

- No fake behaviour: no invented counts, no progress bars that animate while
  nothing is happening, no links that go nowhere, no empty coloured boxes.
- Don't weaken the honesty features: the confirm-before-scanning step, the
  "could not read" list and its stat card, the "mentions only" list, and the
  labels saying whether AI or rules produced something.
- Manual mode must keep working end to end.
- Ripple Offline must stay hard offline: no GitHub option, no AI card, no key
  boxes, and the outbound-connection guard stays on.
- Never commit `Ripple - Overview.pdf` or `ripple-overview.html` — they name
  internal hostnames and the repository is public. `.gitignore` already excludes
  them.

## HOW TO SEE THE SCREENS (this cost the last session real time)

- The Browser pane **cannot screenshot** on this machine — it fails with "not
  compositing frames". Its click and read-page tools do work.
- For pictures, drive headless Chrome over the DevTools protocol.
  Chrome is at `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`.
  Three things fail first, and all three look like "Chrome never started":
  1. `--remote-allow-origins=*` is required, or the connection is refused 403.
  2. Never pin the debugging port. Use `--remote-debugging-port=0` and read the
     real port from the first line of `DevToolsActivePort` in the profile folder.
  3. Use a fresh `--user-data-dir` each run, and kill leftovers by matching
     `--headless` in the command line, never by process name — otherwise you
     kill my browser.
- `websocket-client` is already installed in the Codebase virtual environment.
- The app scrolls an inner container, not the page, so a full-page capture
  returns one screenful. Use a tall window size instead.
- After clicking something, wait for the busy flag to go **true and then false**.
  Polling only for "not busy" returns instantly and looks like a click that did
  nothing.

## WHAT WAS BUILT LAST SESSION

Ripple Offline: a folder to copy onto a locked-down machine, double-click, no
Python, no install, no network. The repository folder and the SQL dialect are
chosen on screen and remembered beside the program. Also fixed, in the shared
engine so both editions got it: pasting an email now reads the source system,
contact, team and subject as well as uploading does; and a repository sitting
inside a folder named build, dist, target or venv was being read as completely
empty, producing a false "no impact".

## STILL OPEN FROM LAST SESSION

- I have not yet tested the built program on my office laptop. It may be blocked
  by policy or flagged by antivirus, because it is unsigned. A page for IT ships
  inside the folder (`READ-ME-FIRST-for-IT.txt`) with the fingerprint they need.
- Undecided: whether to publish the built folder as a zip on the GitHub releases
  page so it can be handed over as a link.

---

# ISSUES

Deal with these in the order listed. For each one, tell me in plain English what
was actually wrong before you change anything.

## Issue 1 —

- **Which Ripple**: online / offline / both
- **Where**: which screen, or which step of the seven
- **What I did**:
- **What I expected**:
- **What actually happened**:

## Issue 2 —

- **Which Ripple**:
- **Where**:
- **What I did**:
- **What I expected**:
- **What actually happened**:

---

Before you finish: both test suites must pass, and if you touched anything the
offline build uses, rebuild it and actually run the built program rather than
assuming it still works. Then commit and push to `main` yourself.
