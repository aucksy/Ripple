"""What tables and columns exist, learned from the repository itself.

This is the "mock database" for the demo: rather than being handed a data
dictionary, Ripple reads every CREATE TABLE it can find and builds one. The
same code works against a real repository -- and whatever it cannot read shows
up as a gap rather than silently shrinking the catalogue.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from sqlglot import exp

from .scanner.sqlread import ParsedRepo, short_name


@dataclass
class Catalog:
    tables: dict[str, list[str]] = field(default_factory=dict)   # TABLE -> [COLUMN, ...]
    defined_in: dict[str, str] = field(default_factory=dict)     # TABLE -> file
    gaps: list[dict] = field(default_factory=list)

    def has_table(self, name: str) -> bool:
        return (name or "").upper() in self.tables

    def columns(self, table: str) -> list[str]:
        return self.tables.get((table or "").upper(), [])

    def has_column(self, table: str, column: str) -> bool:
        return (column or "").upper() in {c.upper() for c in self.columns(table)}

    def to_dict(self) -> dict:
        return {
            "tables": self.tables,
            "definedIn": self.defined_in,
            "gaps": self.gaps,
            "tableCount": len(self.tables),
            "columnCount": sum(len(v) for v in self.tables.values()),
        }


def build_catalog(parsed: ParsedRepo) -> Catalog:
    cat = Catalog()
    for stmt in parsed.statements:
        expr = stmt.expr
        if not isinstance(expr, exp.Create):
            continue
        schema = expr.this
        # CREATE TABLE x (col type, ...) -- an explicit column list
        if isinstance(schema, exp.Schema):
            table = schema.this.name if isinstance(schema.this, exp.Table) else None
            cols: list[str] = []
            for d in schema.expressions:
                if isinstance(d, exp.ColumnDef):
                    cols.append(d.this.name)
            if table and cols:
                cat.tables[table.upper()] = cols
                cat.defined_in[table.upper()] = stmt.file
                continue
            if table:
                cat.gaps.append(
                    {"table": table, "file": stmt.file,
                     "reason": "created without a readable column list"}
                )
                continue
        # CREATE TABLE x AS SELECT ... -- columns come from the query
        #
        # Keyed on the table's own name, without the dataset. What asks this
        # catalogue anything is the notification, and a notification names a
        # table the way a person writes one down.
        target = short_name(stmt.target) if stmt.target else None
        if target and stmt.select is not None:
            cols = []
            for e in stmt.select.expressions:
                if isinstance(e, exp.Star):
                    cols = []
                    # Not a dead end. A scan follows the column straight through
                    # a star and marks the steps past it as inferred; this note
                    # says what the catalogue is missing, not what the scan is.
                    cat.gaps.append(
                        {"table": target, "file": stmt.file,
                         "reason": "built with SELECT * - a scan follows your column through it, "
                                   "but the column names it publishes are not written down"}
                    )
                    break
                if isinstance(e, exp.Alias):
                    cols.append(e.alias)
                elif isinstance(e, exp.Column):
                    cols.append(e.name)
            if cols:
                cat.tables.setdefault(target.upper(), cols)
                cat.defined_in.setdefault(target.upper(), stmt.file)
    return cat
