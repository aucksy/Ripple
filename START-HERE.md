# Which file do I follow?

There are five. You need one. This page picks it for you.

---

## First, two words that mean opposite things

This trips everybody, so it is worth thirty seconds.

**What most people mean:** "offline" = running on my own laptop, "online" = once
it is hosted somewhere.

**What this repository means:** "offline" = a Ripple that may not reach the
network at all — no AI reader, no downloading a repository — built for a machine
where nothing can be installed. "Online" = the ordinary full product.

Those are two completely different questions, and a file named for one of them
gets read as the other. So **no file here is named "online" or "offline" any
more** except the two original build kits, which keep their names for the sake
of everything that already points at them.

**And the thing worth knowing:** running Ripple on your own machine and hosting
it later are **the same files**. One codebase. `run.py` starts it here; the
hosting platform's entry point loads the very same application. Nothing is
rebuilt, ported or reconfigured when it gets hosted. Getting it running on a
laptop is not a detour on the way to hosting it — it is the same thing, started
a different way.

---

## Pick one

**I want Ripple running on a machine, now.**

Can that machine run `pip install`?

| | Follow this | How long |
|---|---|---|
| **Yes** | **`RUN-RIPPLE-HERE.md`** | 36 pastes. Nothing to copy. Fonts included. |
| **No** | `RUN-RIPPLE-HERE-NO-INSTALLS.md` | 25 pastes, and `sqlglot` still has to arrive as a folder. |

Not sure? Run this. If it prints a version, the answer is yes:

```
python -m pip install sqlglot==30.17.0
```

Both hand over Ripple's actual files rather than describing them, and both end
with a script that prints `exact` or `DIFFERENT` for every file, so you never
have to judge by eye.

**Already have the files?** Then you need no kit at all. From the `Codebase`
folder:

```
python -m pip install -r requirements.txt
```
```
python run.py
```

It prints the address it got — read it rather than assuming 8000.

---

**I want to BUILD Ripple from scratch, in a chat, to understand it or change it.**

| | Follow this |
|---|---|
| The machine can install packages | `BUILD-KIT.md` |
| The machine can install nothing | `BUILD-KIT-OFFLINE.md` |

These are a different job. They are specifications — 5,900 lines each — that
tell a chat what to write, phase by phase, with the reasoning behind every rule.
Follow one and you get a Ripple that behaves the same way and uses the same
palette. **You do not get the same files:** of 5,174 substantial lines of
shipped source, 26 appear word for word in them, and none of `app.js`. That is
not a flaw in them; it is what a specification is.

---

**I already have a working Ripple and want to change something.**

`BUILD-KIT-REPAIR.md`. It tells you which single file to put in front of the
chat and exactly what to say to it.

---

## The one thing no kit can contain

`sqlglot`, the SQL parser: 183 files, 2.7 MB. It is what makes Ripple more than
a word search, no chat can write it, and pasted through a chat window it is
about seventy-five pastes.

On a machine where `pip install` works this is a non-issue — one command
installs it. On a machine where it does not, it has to arrive as files, and
Phase 0 of `BUILD-KIT-OFFLINE.md` is four routes for getting it there.

---

## What is in this folder

| | |
|---|---|
| `Codebase/` | The product. Python plus plain HTML, CSS and JavaScript. This is what runs locally and what gets hosted. |
| `Ripple Offline/` | A separate packaging of the same engine as a double-clickable program, for a machine that can install nothing. Generated from `Codebase`, never forked. |
| `RUN-RIPPLE-HERE*.md` | Ripple's files, handed over to paste. Generated — do not edit by hand. |
| `BUILD-KIT*.md` | How to build Ripple from nothing, written for a chat. |

*The two `RUN-RIPPLE-HERE` files are written by
`Ripple Offline/tools/make_exact_kits.py` and checked by
`Ripple Offline/tests/test_exact_kits.py`, which rebuilds Ripple out of each one
and compares it byte for byte. Edit either by hand and that test fails.*
