r"""Write the build kits that produce THIS Ripple, rather than one like it.

    ..\Codebase\.venv\Scripts\python tools\make_exact_kits.py

Writes two files at D:\Apps\Ripple:
    BUILD-KIT-UI-EXACT.md      the three screen files       6 pastes
    BUILD-KIT-ENGINE-EXACT.md  the Python underneath       19 pastes

WHY THESE EXIST, said plainly.

BUILD-KIT.md and BUILD-KIT-OFFLINE.md describe Ripple. They are specifications:
what each file must do, which colours to use, which facts may never be hidden.
A chat given those builds a Ripple that behaves the same way and looks close.

It does not build THIS Ripple. Measured on 25 Aug 2026: of 5,174 substantial
lines of shipped source, 26 appear word for word in either kit. One per cent.
For web/app.js and web/index.html it is zero. Eleven thousand lines of
description, and description does not come back out of a chat as the same file.

These two kits do the opposite of describing. They hand over the files, in
pieces small enough to paste, and ask for them back unchanged. There is no
cleverness in that at all, and that is the point: the only way to end up with an
identical Ripple is to start from identical files.

WHAT NEITHER OF THEM CAN DO. sqlglot is 183 files and 2.7 MB -- about seventy
five pastes. It has to be copied. Follow that through and it decides the whole
question: anything that can carry sqlglot onto a machine can carry the finished
4.3 MB Ripple, so these kits are for when the BUILDING has to happen there, not
for when a working copy is all that is wanted.

WHY GENERATED AND NEVER HAND-WRITTEN. A copy of app.js pasted into a document is
a second copy of app.js, and the second copy is always the one that goes stale.
This reads the live files every run. tests/test_exact_kits.py fails if either
kit has drifted from them.
"""
from __future__ import annotations

import base64
import hashlib
import io
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(r"D:\Apps\Ripple")
CODE = ROOT / "Codebase"
OFF = ROOT / "Ripple Offline"
OWNED_SRC = OFF / "demo_files"

# Roughly 38 KB a piece: small enough that a chat window takes it, large enough
# that nobody is pasting for an hour.
CHUNK_BYTES = 38_000

# Four backticks, because app.js contains single ones inside template strings
# and a three-backtick fence would end early, in the middle of the file, in a
# way that looks like the file simply stopped.
FENCE = "````"

# ── which files each kit hands over ───────────────────────────────────────
# The engine list is the same one tools/make_demo_snapshot.py assembles, which
# is the configuration proven to run on plain Python with nothing installed.
# test_exact_kits.py checks the two lists still agree.
ENGINE = ["__init__.py", "build_info.py", "catalog.py", "config.py", "narrative.py",
          "notification.py", "production.py", "progress.py", "providers.py", "store.py"]
SCANNER = ["__init__.py", "dialectcompat.py", "lineage.py", "repo.py", "rescue.py",
           "sqlread.py", "templating.py"]
WRAPPER = ["folderpick.py", "lifecycle.py", "nonet.py", "paths.py", "prefs.py",
           "synced.py"]
OWNED = ["ripple_offline/__init__.py", "ripple_offline/engine.py",
         "ripple_offline/app.py", "ripple_offline/webserver.py",
         "run.py", "tests/test_smoke.py"]


def offline_web() -> Path:
    """Build the offline front end and return the folder holding it.

    NOT ``Codebase/web``. The shipped screens are made FROM those files, not
    copied from them: the parts that reach out -- the GitHub source and the AI
    key box -- are deleted, and the screens that only exist offline, choosing a
    folder and a dialect, are added. Hand over the online copy instead and two
    things go wrong at once. A machine that is meant to have no way out gets a
    box asking for an API key, and the settings screen it actually needs is not
    there at all, so nobody can point it at a repository.
    """
    sys.path.insert(0, str(OFF))
    from ripple_offline import webbuild                       # noqa: PLC0415
    out = Path(tempfile.mkdtemp(prefix="ripple-ui-kit-"))
    webbuild.build(out_dir=out)
    return out


def ui_files() -> list[tuple[str, Path, str, str]]:
    """(saved as, read from, language, what it decides)"""
    web = offline_web()
    return [
        ("web/index.html", web / "index.html", "html",
         "the empty page the screens are drawn into"),
        ("web/styles.css", web / "styles.css", "css",
         "every colour, size and spacing rule"),
        ("web/app.js", web / "app.js", "javascript",
         "every screen, every card, every word"),
    ]


def online_files() -> list[tuple[str, Path, str, str]]:
    """Every file of the Ripple that runs on a laptop where pip works.

    This is the whole product, not the locked-down variant: the AI reader and
    the GitHub source are in it, because on a machine that installed httpx they
    work. It is the same Ripple that runs from the repository on the machine
    this was written on, which is what "the same output" has to mean.
    """
    out: list[tuple[str, Path, str, str]] = []
    for p in sorted((CODE / "ripple").rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        out.append((f"ripple/{p.relative_to(CODE / 'ripple').as_posix()}", p, "python",
                    "the engine"))
    for n, lang, what in (("index.html", "html", "the empty page the screens are drawn into"),
                          ("styles.css", "css", "every colour, size and spacing rule"),
                          ("app.js", "javascript", "every screen, every card, every word")):
        out.append((f"web/{n}", CODE / "web" / n, lang, what))
    out.append(("run.py", CODE / "run.py", "python", "starting it up"))
    out.append(("requirements.txt", CODE / "requirements.txt", "text",
                "the libraries, with the versions that were tested"))
    return out


def fonts_section() -> tuple[str, int]:
    """The two typefaces, as text, because a .woff2 cannot be pasted.

    web/index.html asks the server for /static/fonts/fonts.css. Leave the folder
    out and that request 404s, the browser falls back to Segoe UI and Consolas,
    and the screens are close but not the same. Measured: layout, colour and
    spacing identical, letterforms not.

    A font file is binary, so it goes through a chat window the only way binary
    can -- base64. One zip of the whole folder rather than sixteen separate
    files: one thing to paste, one thing to check, one thing to get wrong.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted((CODE / "web" / "fonts").iterdir()):
            if p.is_file():
                z.write(p, p.name)
    blob = base64.b64encode(buf.getvalue()).decode("ascii")
    digest = hashlib.sha256(buf.getvalue()).hexdigest()

    # Fixed-width lines so a piece is a block of text rather than one enormous
    # line no editor and no chat window handles well.
    wrapped = "\n".join(blob[i:i + 76] for i in range(0, len(blob), 76)) + "\n"
    pieces = chunks(wrapped)

    out = [f"""## The fonts

Ripple's screens are set in Public Sans and IBM Plex Mono, and `web/index.html`
asks the server for `/static/fonts/fonts.css`. Without this folder that request
comes back 404, the browser falls back to Segoe UI and Consolas, and the screens
are **close but not the same** — same layout, same colours, same spacing,
different letterforms.

A font is a binary file, so it cannot be pasted the way the others can. This is
the whole folder as one zip, written as text, in {len(pieces)} pieces.

**If matching exactly does not matter to you, skip this section.** Everything
works without it and nothing else changes.

### Step 1 — paste the pieces into one file

Create `fonts.b64` and paste piece 1 into it, then add each following piece to
the END of the same file, exactly as with the split files above.

"""]
    for i, piece in enumerate(pieces, 1):
        order = ("Create `fonts.b64` and put exactly this in it."
                 if i == 1 else
                 "Add this to the END of `fonts.b64`. Do not start a new file.")
        out.append(f"#### fonts.b64 — piece {i} of {len(pieces)}\n\n{order}\n\n"
                   f"{FENCE}text\n{piece}{FENCE}\n")

    out.append(f"""### Step 2 — turn it back into the fonts

Save this as `unpack_fonts.py` beside `run.py` and run `python unpack_fonts.py`:

{FENCE}python
\"\"\"Turn fonts.b64 back into web/fonts/, and say plainly if it did not arrive whole.\"\"\"
import base64, hashlib, io, zipfile
from pathlib import Path

WANT = "{digest}"

raw = base64.b64decode("".join(Path("fonts.b64").read_text().split()))
got = hashlib.sha256(raw).hexdigest()
if got != WANT:
    raise SystemExit(
        "fonts.b64 did not arrive whole - a piece is missing or out of order.\\n"
        "Paste it again from piece 1.")

out = Path("web/fonts")
out.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    z.extractall(out)
    print(f"{{len(z.namelist())}} font files written to {{out}}")
{FENCE}

It either prints the number of files or tells you to paste it again. There is no
third answer, and nothing here can half-succeed.

You can delete `fonts.b64` and `unpack_fonts.py` afterwards.

---

""")
    return "\n".join(out), len(pieces)


def engine_files() -> list[tuple[str, Path, str, str]]:
    out: list[tuple[str, Path, str, str]] = []
    for n in ENGINE:
        out.append((f"ripple/{n}", CODE / "ripple" / n, "python", "the engine"))
    for n in SCANNER:
        out.append((f"ripple/scanner/{n}", CODE / "ripple" / "scanner" / n, "python",
                    "reading the repository and following the column"))
    for n in WRAPPER:
        out.append((f"ripple_offline/{n}", OFF / "ripple_offline" / n, "python",
                    "the wrapper"))
    for n in OWNED:
        out.append((n, OWNED_SRC / n, "python", "written for this build, not copied"))
    return out


def chunks(text: str, limit: int = CHUNK_BYTES) -> list[str]:
    """Split on line boundaries so no line is ever cut in half.

    Joined with nothing between them these must equal the file they came from,
    byte for byte. test_exact_kits.py checks exactly that.
    """
    out: list[str] = []
    buf = ""
    for line in text.splitlines(keepends=True):
        if buf and len(buf.encode("utf-8")) + len(line.encode("utf-8")) > limit:
            out.append(buf)
            buf = ""
        buf += line
    if buf:
        out.append(buf)
    return out


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


HOW_TO_SAY_IT = f"""## How to say it to the chat

Paste this once, at the top, before the first piece:

{FENCE}text
I am going to paste some files in pieces. Each piece says which file it belongs
to and whether it starts that file or continues it.

Write them out exactly as given. Do not reformat, do not re-indent, do not
"improve" anything, do not add or remove comments, do not change quote marks,
and do not shorten anything with a comment saying the rest is unchanged. If a
piece looks like it was cut off mid-way, that is correct -- the next piece
continues it.

If you cannot write the whole piece, say so and stop. Do not summarise it.
{FENCE}

That last line matters. A chat asked for a long file will sometimes write half
of it and put `# ... rest unchanged ...` in the middle, which produces a file
that looks finished and is not. The check at the bottom catches it.
"""


def build_kit(out_path: Path, title: str, intro: str, files, check_name: str,
              tail: str, with_fonts: bool = False) -> tuple[int, int]:
    parts: list[str] = [intro]
    plan: list[tuple[str, int, int, str]] = []

    # One block per file, or per piece of a file too big for a single paste.
    blocks: list[tuple[str, int]] = []          # (rendered block, size in bytes)
    empties: list[str] = []
    for saved_as, src, lang, _what in files:
        text = src.read_text(encoding="utf-8")
        # An EMPTY file has no pieces, so it produces no paste and is simply
        # absent from what somebody builds. Both __init__.py files are empty,
        # and without them Python cannot find the package at all -- a folder
        # that looks complete and imports nothing.
        if not text:
            empties.append(saved_as)
            plan.append((saved_as, 0, 0, sha(text)))
            continue
        pieces = chunks(text)
        plan.append((saved_as, len(pieces), len(text.splitlines()), sha(text)))
        for i, piece in enumerate(pieces, 1):
            many = len(pieces) > 1
            head = (f"### {saved_as} — piece {i} of {len(pieces)}" if many
                    else f"### {saved_as}")
            if i == 1:
                order = (f"Create the file `{saved_as}` and put exactly this in it. "
                         f"Change nothing: not a space, not a quote, not a blank line.")
            else:
                order = (f"Add this to the END of `{saved_as}`, straight after what is "
                         f"already there. Do not start a new file. Do not re-type "
                         f"anything above.")
            nl = "" if piece.endswith("\n") else "\n"
            blocks.append((f"{head}\n\n{order}\n\n{FENCE}{lang}\n{piece}{nl}{FENCE}\n",
                           len(piece.encode("utf-8"))))

    # Pack the small ones together. Twenty-nine files pasted one at a time is
    # twenty-nine copy-and-pastes, and most of them are under two hundred lines.
    pastes: list[list[str]] = []
    room = 0
    for block, size in blocks:
        if not pastes or room + size > CHUNK_BYTES:
            pastes.append([])
            room = 0
        pastes[-1].append(block)
        room += size

    bodies: list[str] = []
    for i, group in enumerate(pastes, 1):
        many = "" if len(group) == 1 else f" — {len(group)} files"
        bodies.append(f"## Paste {i} of {len(pastes)}{many}\n")
        bodies.extend(group)

    total_pastes = len(pastes)
    total_lines = sum(p[2] for p in plan)

    if empties:
        listed = "\n".join(f"    {n}" for n in empties)
        cmds = "\n".join(f"type nul > {n.replace('/', chr(92))}" for n in empties)
        parts.append(f"""## First: the empty files

Before anything else, create these. They are empty — nothing goes in them — and
there is no paste for them below for that reason.

````
{listed}
````

In a Command Prompt, from the folder you are building in:

````
{cmds}
````

Nothing is printed and nothing happens on screen. That is correct.

**Do not skip them because everything works without them.** It does. That is
exactly what makes them worth the two commands.

Leave them out and Python still imports Ripple perfectly happily — as a
"namespace package", which is a package assembled out of EVERY folder called
`ripple` it can find, merged together. Measured: with the empty file, `ripple`
is one folder and a decoy folder elsewhere on the path cannot get in. Without
it, `ripple` spans two folders and a module from the decoy imports as though it
were Ripple's own.

Nothing errors. Nothing warns. On a laptop that has ever had another copy of
Ripple, or a folder called `ripple` belonging to something else, the answer on
screen comes partly from code that is not in the folder you are looking at —
which is the one failure this whole tool exists to make impossible.

---

""")

    parts.append("## What you are pasting\n")
    parts.append("| File | What it decides | Lines | Pieces |")
    parts.append("|---|---|---|---|")
    for (saved_as, npieces, nlines, _), (_, _, _, what) in zip(plan, files):
        parts.append(f"| `{saved_as}` | {what} | {nlines:,} | {npieces if npieces else "empty file"} |")
    parts.append(f"""
**{total_lines:,} lines in {total_pastes} pastes.** Do them in the order below.
Where a file is split, the pieces MUST go one after another into the SAME file —
piece 2 goes on the end of piece 1, never into a new file.

---

{HOW_TO_SAY_IT}
---

""")

    font_pastes = 0
    if with_fonts:
        section, font_pastes = fonts_section()
        parts.append(section)

    parts.append("## The pieces\n")
    parts.extend(bodies)

    parts.append(f"""---

## Check you got it right

Do not trust your eyes for this. A file missing thirty lines in the middle looks
perfectly normal.

Save this as `{check_name}` in the project root and run `python {check_name}`:

{FENCE}python
\"\"\"Did every file arrive whole? One word each.\"\"\"
import base64
import hashlib
import io
import sys
import tempfile
import zipfile
from pathlib import Path

WANT = {{""")
    for saved_as, _, _, digest in plan:
        parts.append(f'    "{saved_as}": "{digest}",')
    parts.append("""}

bad = []
for name, want in WANT.items():
    f = Path(name)
    if not f.is_file():
        print(f"{name:34} MISSING")
        bad.append(name)
        continue
    got = hashlib.sha256(f.read_bytes().replace(b"\\r\\n", b"\\n")).hexdigest()
    if got == want:
        print(f"{name:34} exact")
    else:
        n = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
        print(f"{name:34} DIFFERENT  ({n} lines here)")
        bad.append(name)

print()
if bad:
    print(f"{len(bad)} file(s) are not identical. Paste each from its first piece again:")
    for n in bad:
        print("   ", n)
else:
    print("Every file is identical to the original.")
""" + FENCE + f"""

`exact` means byte for byte. `DIFFERENT` with a line count well below the table
above means a piece was skipped, or a chat summarised part of it — paste that
file again from its first piece.

Line endings are not counted as a difference: Windows may store these with
different line breaks and nothing about the program changes.

{tail}

---

*Generated from the live files by `Ripple Offline/tools/make_exact_kits.py`. Do
not edit this by hand — run that again instead. A hand-edited copy of a source
file inside a document is a second copy of it, and the second copy is the one
that goes stale.*
""")

    out_path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return total_pastes + font_pastes, total_lines


UI_INTRO = """# Ripple — the screens, exactly

**What this is.** The three files that ARE Ripple's user interface, handed over
whole, in pieces you paste one after another.

**Why it is not written like the other kits.** `BUILD-KIT.md` and
`BUILD-KIT-OFFLINE.md` describe how Ripple works and let a chat write the code.
That is right for the engine and wrong for the screens. Of every substantial
line of Ripple's shipped source, **one per cent** appears word for word in those
two kits — and for `app.js` and `index.html` it is **none**. They are a
description, and a description does not come back out as the same file. Follow
them and you get a Ripple that behaves the same and looks close. You do not get
the same screens.

If what you need is the same screens, you need the same files. That is all this
kit is.

---

## Read this before you start

**No Python file builds the screens.** This surprises everybody. Every screen,
every card and every word on them lives in `web/app.js`, which is JavaScript.
`web/styles.css` holds the colours and spacing. Python only serves those files
and hands them the numbers. Nothing in the engine draws anything.

That is also the good news: there is nothing to compile, nothing to install and
nothing to get right. Three text files in a folder called `web`, and the screens
are exact.

**This kit gives you the screens, not the engine.** For the Python underneath,
either follow `BUILD-KIT-OFFLINE.md` — which builds a working engine that is
simpler than the shipped one — or use `BUILD-KIT-ENGINE-EXACT.md`, which hands
that over whole the same way this hands over the screens.

**One thing cannot be typed by anybody.** The SQL parser, `sqlglot`, is 183
files and 2.7 MB. No chat can write it and no kit can contain it. It has to be
copied. That is Phase 0 of the offline kit and it has not changed.

---
"""

ENGINE_INTRO = """# Ripple — the engine, exactly

**What this is.** Every Python file Ripple needs, handed over whole, in pieces
you paste one after another. This is the same set of files that runs on a
machine with nothing installed: Python's own library, plus the SQL parser.

**Why it is not written like the other kits.** `BUILD-KIT-OFFLINE.md` describes
the engine and lets a chat write it. That produces a working Ripple, and it is
the right kit if you want to understand how Ripple works or change it. But its
phases budget about 4,500 lines and the shipped engine is 10,797. The difference
is edge cases — odd SQL shapes, rescue paths, dialect quirks — so a Ripple built
from the description and this one can disagree on a hard repository.

For a tool whose whole value is that "no impact" can be trusted, disagreeing on
hard repositories is the disagreement that matters. That is what this kit is
for.

---

## Read this before you start

**This is a transcription, not a build.** You are not writing Ripple here; you
are having a chat write out files you already have, because that is a way to get
them onto a machine that will not take a memory stick. Be clear with yourself
about which of those two you need — the other kits genuinely build it.

**One thing cannot be typed by anybody.** The SQL parser, `sqlglot`, is 183
files, 80,000 lines and 2.7 MB — about seventy-five pastes. It has to be copied
onto the machine as files, and no kit can change that.

Follow that all the way, because it decides whether you want this kit at all:

> Anything that can carry 2.7 MB of `sqlglot` onto that laptop can carry the
> whole of Ripple, which is 4.3 MB. If a memory stick, a shared drive or a
> download works at all, copying a finished Ripple is one step.

Use this kit when the building has to have happened on that machine. Copy a
finished folder when a working Ripple is all you need.

**The screens are a separate kit.** `BUILD-KIT-UI-EXACT.md`, seven pastes.

---
"""

UI_TAIL = """## When it is running

Start the server from the project root and open the address it prints:

````
python run.py
````

Do not open `index.html` by double-clicking it. The page asks the server for
`/static/styles.css`, and a file opened directly has no server to ask, so you
get black text on white and nothing to say why."""

ENGINE_TAIL = """## When every file says `exact`

You still need two things this kit does not contain:

1. **`sqlglot`** — copied in as a folder beside `run.py`. Nothing works without it.
2. **The screens** — `web/index.html`, `web/styles.css`, `web/app.js`, from
   `BUILD-KIT-UI-EXACT.md`.

Then, from the project root:

````
python run.py
````

It prints the address it got. Read it rather than assuming 8000 — if something
else on the machine has that port, Ripple quietly takes the next free one.

To prove the engine works before opening anything:

````
python -m unittest tests.test_smoke
````

Thirteen checks. They cover the parser arriving, the engine arriving, the screens
arriving, a column being followed end to end, and the rule that Ripple must never
say "no impact" over a file it could not read."""


ONLINE_INTRO = """# Ripple — the whole thing, exactly

**What this is.** Every file of Ripple, handed over whole, in pieces you paste
one after another. Not a description of Ripple: the files.

**Use this one when `pip install` works on the machine.** If it does, this is
the shortest honest road to a Ripple that is identical to the one it came from —
the same engine, the same screens, the same answers. There is nothing to copy
across and nothing to carry on a memory stick.

The other kits exist for other situations. `BUILD-KIT.md` and
`BUILD-KIT-OFFLINE.md` describe Ripple and let a chat write it, which is what
you want in order to understand it or change it — but of every substantial line
of shipped source, only **one per cent** appears word for word in them, and for
`app.js` none at all. They produce a Ripple that behaves the same and looks
close, not the same one.

---

## Before the first paste: the libraries

This kit hands over Ripple's own code. It does not contain the libraries Ripple
uses, because those are installed rather than written:

````
python -m pip install --user sqlglot==30.17.0 fastapi==0.115.0 uvicorn==0.30.6 pydantic==2.13.4 python-multipart==0.0.9 extract-msg==0.48.7 httpx==0.27.2
````

**The versions are not decoration.** `sqlglot` renamed three parse-tree keys
between its version 25 and 30. Read a tree with the old key on the new library
and it returns nothing at all — so a feature switches itself off, quietly, and
no error is raised anywhere. Ripple was written and tested against 30.17.0. If
the machine already has a different one, say so before trusting any answer it
gives.

Check what is actually there:

````
python -c "import sqlglot; print(sqlglot.__version__)"
````

---

## Read this before you start

**No Python file builds the screens.** This surprises everybody. Every screen,
every card and every word on them lives in `web/app.js`, which is JavaScript.
`web/styles.css` holds the colours and spacing. Python only serves those files
and hands them the numbers.

**This is a transcription, not a build.** You are not writing Ripple here; you
are having a chat write out files, which is a way to get them onto a machine
that will not take a memory stick or a download. The other two kits genuinely
build it. Be clear with yourself about which of those you need.

---
"""

ONLINE_TAIL = """## When every file says `exact`

From the folder holding `run.py`:

````
python run.py
````

It prints the address it got. Read it rather than assuming 8000 — if something
else on the machine holds that port, Ripple quietly takes the next free one up
to 8020.

Do not open `index.html` by double-clicking it. The page asks the server for
`/static/styles.css`, and a file opened directly has no server to ask, so you
get black text on a white page and nothing to say why.

**First run.** Ripple starts with no folder chosen, because a folder path from
another machine would mean nothing here. Open **Settings & checks**, put in the
folder to scan, choose the SQL dialect, and put your published-table names in.
That last one matters most: Ripple only calls something "production impact" if
the table the chain ends at is on that list."""


def main() -> None:
    n0, l0 = build_kit(ROOT / "BUILD-KIT-ONLINE-EXACT.md", "everything", ONLINE_INTRO,
                       online_files(), "check_ripple.py", ONLINE_TAIL,
                       with_fonts=True)
    print(f"BUILD-KIT-ONLINE-EXACT.md  {n0:>3} pastes  {l0:>7,} lines   <- pip works")

    n1, l1 = build_kit(ROOT / "BUILD-KIT-UI-EXACT.md", "screens", UI_INTRO,
                       ui_files(), "check_ui.py", UI_TAIL)
    print(f"BUILD-KIT-UI-EXACT.md      {n1:>3} pastes  {l1:>7,} lines   <- locked down")

    n2, l2 = build_kit(ROOT / "BUILD-KIT-ENGINE-EXACT.md", "engine", ENGINE_INTRO,
                       engine_files(), "check_engine.py", ENGINE_TAIL)
    print(f"BUILD-KIT-ENGINE-EXACT.md  {n2:>3} pastes  {l2:>7,} lines   <- locked down")
    print(f"\npip works        : {n0} pastes, nothing to copy")
    print(f"nothing installs : {n1 + n2} pastes, plus sqlglot copied as a folder")


main()
