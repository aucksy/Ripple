r"""Write a build kit that produces the EXACT Ripple screens, not a lookalike.

    ..\Codebase\.venv\Scripts\python tools\make_ui_kit.py

Writes D:\Apps\Ripple\BUILD-KIT-UI-EXACT.md.

WHY THIS EXISTS, said plainly.

BUILD-KIT.md and BUILD-KIT-OFFLINE.md describe Ripple. They are specifications:
what each screen shows, which colours to use, which class names the script
expects, which facts may never be hidden. A chat given those builds a Ripple
that behaves the same way and uses the same palette.

It does not build THIS Ripple. Measured on 25 Aug 2026: of 5,174 substantial
lines of shipped source, 26 appear word for word in either kit. One per cent.
For web/app.js and web/index.html it is zero. The two kits are 11,678 lines of
description, and description cannot come out the far end as the same file.

For the engine that is a reasonable trade -- the behaviour is what matters and
the tests pin it. For the SCREENS it is not, because "the same screens" means
the same pixels, and no amount of prose gets two people to the same pixels.

So this kit does the opposite of describing. It hands over the three files, in
pieces small enough to paste, and asks for them back unchanged. There is no
cleverness in it at all, and that is the point: the only way to end up with
identical screens is to start from identical files.

WHY IT IS GENERATED AND NEVER HAND-WRITTEN. A copy of app.js pasted into a
document is a second copy of app.js, and the second copy is always the one that
goes stale. This reads the live files every time it runs, so the kit is either
current or regenerated. tests/test_ui_kit.py fails if it has drifted.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(r"D:\Apps\Ripple")
WEB = ROOT / "Codebase" / "web"
OUT = ROOT / "BUILD-KIT-UI-EXACT.md"

# Roughly 38 KB a piece. Small enough to paste into a chat window without it
# being refused, large enough that nobody is pasting for an hour.
CHUNK_BYTES = 38_000

# Four backticks, because app.js contains single ones inside template strings
# and a three-backtick fence would end early, in the middle of the file, in a
# way that looks like the file simply stopped.
FENCE = "````"

FILES = [
    ("web/index.html", "the empty page the screens are drawn into", "html"),
    ("web/styles.css", "every colour, size and spacing rule", "css"),
    ("web/app.js", "every screen, every card, every word", "javascript"),
]


def chunks(text: str, limit: int = CHUNK_BYTES) -> list[str]:
    """Split on line boundaries so no line is ever cut in half.

    Joined back together with nothing between them, these must equal the file
    they came from, byte for byte. test_ui_kit.py checks exactly that.
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


def main() -> None:
    parts: list[str] = []
    plan: list[tuple[str, int, int, str]] = []
    bodies: list[str] = []

    for name, what, lang in FILES:
        text = (ROOT / "Codebase" / name).read_text(encoding="utf-8")
        pieces = chunks(text)
        plan.append((name, len(pieces), len(text.splitlines()), sha(text)))

        for i, piece in enumerate(pieces, 1):
            first = i == 1
            many = len(pieces) > 1
            head = f"### {name} — piece {i} of {len(pieces)}" if many else f"### {name}"
            if first:
                order = (f"Create the file `{name}` and put exactly this in it. "
                         f"Change nothing: not a space, not a quote, not a blank line.")
            else:
                order = (f"Add this to the END of `{name}`, straight after what is "
                         f"already there. Do not start a new file. Do not re-type "
                         f"anything above.")
            bodies.append(
                f"{head}\n\n{order}\n\n{FENCE}{lang}\n{piece}"
                f"{'' if piece.endswith(chr(10)) else chr(10)}{FENCE}\n"
            )

    total_pastes = sum(p[1] for p in plan)
    total_lines = sum(p[2] for p in plan)

    parts.append(f"""# Ripple — the screens, exactly

**What this is.** The three files that ARE Ripple's user interface, handed over
whole, in {total_pastes} pieces you paste one after another.

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

**This kit gives you the screens, not the engine.** You still need the Python
underneath, from `BUILD-KIT-OFFLINE.md`. The two fit together: build the engine
from that kit, then put these three files in `web/` and the screens are Ripple's
own rather than an imitation.

**One thing cannot be typed by anybody.** The SQL parser, `sqlglot`, is 183
files. No chat can write it and no kit can contain it. It has to be copied. That
is Phase 0 of the offline kit and it has not changed.

---

## What you are pasting

| File | What it decides | Lines | Pieces |
|---|---|---|---|""")

    for (name, npieces, nlines, _), (_, what, _) in zip(plan, FILES):
        parts.append(f"| `{name}` | {what} | {nlines:,} | {npieces} |")

    parts.append(f"""
**{total_lines:,} lines in {total_pastes} pastes.** Do them in the order below.
Where a file is split, the pieces MUST go in one after another, into the same
file — piece 2 goes on the end of piece 1, not into a new file.

---

## How to say it to the chat

Paste this once, at the top, before the first piece:

{FENCE}text
I am going to paste some files in pieces. Each piece says which file it belongs
to and whether it starts that file or continues it.

Write them out exactly as given. Do not reformat, do not re-indent, do not
"improve" anything, do not add or remove comments, do not change quote marks,
and do not shorten anything with a comment saying the rest is unchanged. If a
piece looks like it was cut off mid-way, that is correct — the next piece
continues it.

If you cannot write the whole piece, say so and stop. Do not summarise it.
{FENCE}

That last line matters. A chat asked for a long file will sometimes write half
and put `// ... rest of the file unchanged ...` in the middle, which produces a
file that looks finished and is not. The check at the bottom catches it.

---

## The pieces

""")

    parts.extend(bodies)

    parts.append("""---

## Check you got it right

Do not trust your eyes for this. A file that is missing thirty lines in the
middle looks perfectly normal.

Save this as `check_ui.py` next to `run.py`, and run `python check_ui.py`:

""" + FENCE + """python
\"\"\"Did the three screen files arrive whole? Answers in one word each.\"\"\"
import hashlib
from pathlib import Path

WANT = {""")

    for name, _, _, digest in plan:
        parts.append(f'    "{name}": "{digest}",')

    parts.append("""}

ok = True
for name, want in WANT.items():
    f = Path(name)
    if not f.is_file():
        print(f"{name:16} MISSING")
        ok = False
        continue
    got = hashlib.sha256(f.read_bytes().replace(b"\\r\\n", b"\\n")).hexdigest()
    if got == want:
        print(f"{name:16} exact")
    else:
        n = len(f.read_text(encoding='utf-8', errors='replace').splitlines())
        print(f"{name:16} DIFFERENT  ({n} lines here)")
        ok = False

print()
print("The screens are Ripple's own." if ok else
      "Something is not identical. Paste that file again, in its pieces.")
""" + FENCE + """

`exact` means byte for byte, so the screens cannot differ. `DIFFERENT` with a
line count well below the table above means a piece was skipped or a chat
summarised part of it — paste that file again from its first piece.

Line endings are not counted as a difference: Windows may store these with
different line breaks and that changes nothing on screen.

---

## When it is running

Start the server from the project root and open the address it prints:

""" + FENCE + """
python run.py
""" + FENCE + """

Do not open `index.html` by double-clicking it. The page asks the server for
`/static/styles.css`, and a file opened directly has no server to ask, so you
get black text on white and nothing to say why.

---

*Generated from the live files by `Ripple Offline/tools/make_ui_kit.py`. Do not
edit this by hand — run that again instead. A hand-edited copy of app.js is a
second copy of app.js, and the second copy is the one that goes stale.*
""")

    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")

    kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT.name}: {kb:,.0f} KB, {total_pastes} pastes, {total_lines:,} lines of UI")
    for name, npieces, nlines, digest in plan:
        print(f"  {name:16} {nlines:>6,} lines  {npieces} piece(s)  {digest[:12]}...")


main()
