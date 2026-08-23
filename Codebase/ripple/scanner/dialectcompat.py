"""Reading the parse tree the same way whichever sqlglot is installed.

sqlglot renames the keys inside its own nodes between major versions, and three
of the renames that matter here are SILENT: the old key simply returns None, so
the code carries on and finds nothing. Two of the three switch off things this
tool exists to do --

* ``Star.args["except"]`` became ``except_``. Read the old key and
  ``SELECT * EXCEPT(col)`` stops being noticed, so a column that is dropped by
  name is reported as carried through.
* ``Merge.args["expressions"]`` became ``whens`` (wrapped in a ``Whens`` node).
  Read the old key and every rename a MERGE makes disappears -- and a MERGE is
  how a published table is normally loaded.

-- and the third, ``Select.args["from"]`` becoming ``from_``, quietly empties
the check that decides which tables a ``SELECT *`` covers.

None of that raises. The tests would go on passing on the version that is
installed today and the answers would go quietly wrong on any newer one. So
every one of those keys is read through a function here, and there is a test
that fails loudly if a key stops resolving at all.
"""
from __future__ import annotations

from sqlglot import exp

# ALTER TABLE a RENAME TO b. The one rename that is loud -- the class simply
# stops existing -- but it belongs with the rest.
RENAME_NODE = getattr(exp, "AlterRename", None) or getattr(exp, "RenameTable")


def from_of(select: exp.Select):
    """The FROM clause of a SELECT."""
    return select.args.get("from") or select.args.get("from_")


def star_except(star: exp.Star) -> list:
    """The columns named in ``SELECT * EXCEPT(a, b)``."""
    return list(star.args.get("except") or star.args.get("except_") or [])


def star_replace(star: exp.Star) -> list:
    """The columns swapped by ``SELECT * REPLACE(x AS a)``."""
    return list(star.args.get("replace") or star.args.get("replace_") or [])


def merge_whens(merge: exp.Expression) -> list:
    """Every WHEN branch of a MERGE, whichever shape it arrives in."""
    whens = merge.args.get("whens")
    if whens is not None:
        return list(getattr(whens, "expressions", whens) or [])
    return list(merge.args.get("expressions") or [])
