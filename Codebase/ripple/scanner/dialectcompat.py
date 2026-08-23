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


def is_unpivot(pivot: exp.Expression) -> bool:
    """PIVOT turns rows into columns; UNPIVOT turns columns into rows."""
    return bool(pivot.args.get("unpivot"))


def pivot_fields(pivot: exp.Expression) -> list:
    """The ``FOR x IN (...)`` parts of a PIVOT or UNPIVOT.

    Where the names live. For an UNPIVOT the IN list IS the column list being
    folded away, so reading the wrong key means a statement that hard-fails on
    the day the column goes is reported as carrying it through untouched.
    """
    fields = pivot.args.get("fields")
    if fields is None:
        fields = pivot.args.get("field")
    if fields is None:
        return []
    return list(fields) if isinstance(fields, list) else [fields]


def pivot_columns(pivot: exp.Expression) -> list[str]:
    """The output column names a PIVOT produces -- ``total_Q1``, ``total_Q2``.

    sqlglot works these out itself, which is worth having: the rule involves the
    aggregate's alias, whether it has one, and each IN value. Empty means it did
    not, and the caller must not pretend it knows the names.
    """
    return [c.name if hasattr(c, "name") else str(c)
            for c in (pivot.args.get("columns") or [])]


def is_temporary(stmt: exp.Expression | None) -> bool:
    """Was this CREATE written as TEMP or TEMPORARY?

    A temporary table lives inside one script and is gone when it ends, so two
    files that both call one ``t`` are not sharing a table. Read the wrong key
    and they get merged, which invents a chain to a published table nobody
    touched -- and the finding on it looks exactly like a real one.
    """
    props = getattr(stmt, "args", {}).get("properties") if stmt is not None else None
    node = getattr(exp, "TemporaryProperty", None)
    if props is None or node is None:
        return False
    return any(isinstance(p, node) for p in props.expressions)


def merge_whens(merge: exp.Expression) -> list:
    """Every WHEN branch of a MERGE, whichever shape it arrives in."""
    whens = merge.args.get("whens")
    if whens is not None:
        return list(getattr(whens, "expressions", whens) or [])
    return list(merge.args.get("expressions") or [])
