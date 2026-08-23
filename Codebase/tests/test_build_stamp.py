"""Which build is this? Every screen used to be silent about it.

"It does not work" has more than once turned out to be "that was fixed a while
ago, on a copy that was never installed", and there was no way to tell those
two apart from anything Ripple showed.

What is guarded here is not the version number. It is the honesty of the stamp:
a commit hash read out of git is a fact, the date of the newest file in a folder
is a guess, and the screen must never let those two read the same.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ripple import build_info as bi                             # noqa: E402
from ripple.api import app                                      # noqa: E402


def test_health_carries_a_build_stamp():
    """The screen reads this. Without it there is nothing to show."""
    out = TestClient(app).get("/api/health").json()
    assert "build" in out, "/api/health must say which build it is"
    b = out["build"]
    assert b["version"], "a build with no version is no answer"
    assert b["label"], "the screen shows this line and it cannot be blank"
    assert b["from"] in {"build", "host", "git", "files"}


def test_a_guessed_date_says_it_is_a_guess():
    """File dates move whenever anything is touched, and say nothing at all
    about whether this copy was ever installed anywhere. If that is all Ripple
    has, the line has to admit it -- a guess that looks like a fact is worse
    than no line."""
    label = bi._label({"version": "1.0", "commit": "", "built": "2026-08-23T10:00:00",
                       "from": "files"})
    assert "guess" in label.lower(), label
    assert "newest file" in label, label


def test_a_real_commit_is_not_hedged():
    """The other half of the same rule: a fact must not be dressed up as a
    guess, or the honest wording stops meaning anything."""
    label = bi._label({"version": "1.0", "commit": "abc1234",
                       "built": "2026-08-23T10:00:00+05:30", "from": "git"})
    assert "abc1234" in label
    assert "guess" not in label.lower(), label
    assert "23 Aug 2026" in label


def test_a_packaged_folder_is_stamped_and_read_back(tmp_path):
    """The packaged executable has no git, and its file dates are the dates the
    files were copied -- true, useless, and impossible to tell from a real build
    date. The stamp file is the only thing that can tell one build of it from
    another, so writing it and reading it back has to work."""
    written = bi.write_stamp(tmp_path, commit="deadbee", built="2026-08-23T09:30:00+05:30")
    assert written.name == bi.STAMP_FILE
    saved = json.loads(written.read_text(encoding="utf-8"))
    assert saved["commit"] == "deadbee"

    # Read back the way the running program reads it, from a folder it is told
    # to look in rather than from wherever this test happens to live.
    original = bi._places_to_look
    bi._places_to_look = lambda: [tmp_path]
    try:
        found = bi._from_stamp_file()
    finally:
        bi._places_to_look = original
    assert found == {"commit": "deadbee", "built": "2026-08-23T09:30:00+05:30",
                     "from": "build"}
    assert "built 23 Aug 2026" in bi._label({"version": "1.0", **found})


def test_a_missing_or_broken_stamp_never_throws(tmp_path):
    """A damaged stamp file must cost the line on the screen, not the program.
    Ripple falls back to the next honest answer instead."""
    (tmp_path / bi.STAMP_FILE).write_text("{ not json", encoding="utf-8")
    original = bi._places_to_look
    bi._places_to_look = lambda: [tmp_path]
    try:
        assert bi._from_stamp_file() is None
    finally:
        bi._places_to_look = original


def test_a_working_copy_with_edits_does_not_claim_to_be_the_commit(monkeypatch):
    """A build made from a working copy that has been edited is NOT that
    commit. Left unmarked it claims to be, which is exactly the confusion this
    whole file exists to remove."""
    monkeypatch.setattr(bi, "_has_edits", lambda: True)
    found = bi._from_git()
    if found is None:
        return                      # not run from a git working copy; nothing to check
    assert found["commit"].endswith("+edits"), found
