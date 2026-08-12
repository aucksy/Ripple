"""Shared setup for the offline tests.

Every test runs against a throwaway folder rather than a real installation, so
a test can never overwrite somebody's chosen repository folder or their saved
analyses.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

OFFLINE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OFFLINE_DIR))

# A home for the settings file and the history database, set before anything
# reads them.
_HOME = OFFLINE_DIR / "build" / "test-home"
_HOME.mkdir(parents=True, exist_ok=True)
os.environ["RIPPLE_OFFLINE_HOME"] = str(_HOME)

from ripple_offline.engine import SHARED_DIR                       # noqa: E402

MOCKREPO = SHARED_DIR / "mockrepo"
SAMPLES = SHARED_DIR / "samples"


@pytest.fixture(scope="session")
def home() -> Path:
    return _HOME


@pytest.fixture
def clean_home(home: Path):
    """No settings file and no history, as on a machine that has never run it."""
    for name in ("ripple-settings.json", "ripple-history.db"):
        target = home / name
        if target.exists():
            target.unlink()
    yield home
