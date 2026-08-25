# Which file do I follow?

Four files. You need one, and this page picks it.

---

## First, two words that mean opposite things

This trips everybody, so it is worth thirty seconds.

**What most people mean:** "offline" = running on my own laptop, "online" = once
it is hosted somewhere.

**What a codebase usually means:** "offline" = a build that may not reach the
network at all. A different question entirely, and a file named for one of them
gets read as the other. So no file here is named either word.

**And the thing worth knowing:** running Ripple on your own machine and hosting
it later are **the same files**. One codebase. `run.py` starts it here; a hosting
platform's entry point loads the very same application. Nothing is rebuilt,
ported or reconfigured when it gets hosted. Getting it running on a laptop is not
a detour on the way to hosting it — it is the same thing, started a different way.

---

## Pick one

### I want to BUILD Ripple, in a chat, on this machine

**`BUILD-KIT.md`.** Twelve chat windows, about two evenings. You do not need to
be able to code — the chat writes it, you save the files and run one command to
check each phase.

This is the one to follow if you want to understand Ripple, change it, or be
able to show how it was built. It is a specification: it says what every file
must do, which colours to use, which facts may never be hidden, and what each
test must prove, with the reasoning behind every rule.

It ends with a working Ripple that behaves the same way and uses the same
palette. **It does not end with the same files** — of 5,174 substantial lines of
shipped source, 26 appear word for word in it, and none of `app.js`. That is not
a flaw; it is what a specification is. Which is why the next file exists.

### I want Ripple running, identical, now

**`RUN-RIPPLE-HERE.md`.** 36 pastes. Ripple's actual files, handed over whole
rather than described, fonts included. It ends with a script that prints `exact`
or `DIFFERENT` for every file, so you never judge by eye.

Use it on its own when you just need a working copy. Use it **alongside**
`BUILD-KIT.md` as the repair shop: build a phase, and where the chat's output
falls short, take that one file's pieces from here.

### I already have a working Ripple and want to change something

**`BUILD-KIT-REPAIR.md`.** One prompt to paste. Type what is wrong underneath it
and the chat answers with the files to open and where they are saved — every
file that has to change together, not just the obvious one, because the prompt
carries the real dependency graph.

### I already have the files and just want to run them

No kit needed. From the `Codebase` folder:

```
python -m pip install -r requirements.txt
```
```
python run.py
```

It prints the address it got — read it rather than assuming 8000.

---

## Before anything, on a managed laptop

Three commands, in this order. `BUILD-KIT.md` and `RUN-RIPPLE-HERE.md` both
open with them and explain what each prevents.

```
python -m ensurepip --upgrade --user
```
```
python -m pip config set global.index-url <your company mirror>
```
```
python -m pip install --user sqlglot==30.17.0 fastapi==0.115.0 uvicorn==0.30.6 pydantic==2.13.4 python-multipart==0.0.9 extract-msg==0.48.7 httpx==0.27.2
```

**If none of that can reach anything**, `BUILD-KIT.md` has a section called *"If
the install step will not work at all"* with three routes for getting `sqlglot`
onto the machine as files. It is the only package that cannot be worked around —
183 files, 2.7 MB, and it is what makes Ripple more than a word search.

**Python itself:** 3.10 or newer. It was developed on 3.12.

---

## What is in this folder

| | |
|---|---|
| `Codebase/` | The product. Python plus plain HTML, CSS and JavaScript. This is what runs locally and what gets hosted. |
| `Ripple Offline/` | A separate packaging of the same engine as a double-clickable program. Generated from `Codebase`, never forked. |
| `BUILD-KIT.md` | How to build Ripple from nothing, written for a chat. |
| `RUN-RIPPLE-HERE.md` | Ripple's own files, handed over to paste. Generated — do not edit by hand. |
| `BUILD-KIT-REPAIR.md` | One prompt that routes a complaint to the right files. Generated. |

*`RUN-RIPPLE-HERE.md` and `BUILD-KIT-REPAIR.md` are written by the tools in
`Ripple Offline/tools/` and checked by `Ripple Offline/tests/test_exact_kits.py`,
which rebuilds Ripple out of the first one and compares it byte for byte. Edit
either by hand and that test fails.*
