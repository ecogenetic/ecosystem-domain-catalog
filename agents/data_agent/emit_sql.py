#!/usr/bin/env python3.14
"""Emit PostgreSQL DDL from a PhysicalModel."""

from __future__ import annotations

from typing import Any


def _quote(name: str) -> str:
    if name.lower() in {"order", "user", "group", "table", "select"}:
        return f'"{name}"'
    return name


def generate_ddl(model: dict[str, Any]) -> str:
    lines: list[str] = []
    fk_lines: list[str] = []
    for tbl in model.get("tables") or []:
        table = _quote(tbl["table"])
        col_defs: list[str] = []
        pk_cols: list[str] = []
        for col in tbl.get("columns") or []:
            name = _quote(col["name"])
            sql_type = col.get("sqlType") or "TEXT"
            parts = [name, sql_type]
            if col.get("primaryKey"):
                parts.append("PRIMARY KEY")
                pk_cols.append(col["name"])
            elif not col.get("nullable", True):
                parts.append("NOT NULL")
            if col.get("enum"):
                vals = ", ".join(f"'{v}'" for v in col["enum"])
                parts.append(f"CHECK ({name} IN ({vals}))")
            col_defs.append(" ".join(parts))
        lines.append(f"CREATE TABLE {table} (\n    " + ",\n    ".join(col_defs) + "\n);")
        for col in tbl.get("columns") or []:
            if col.get("kind") == "fk" and col.get("refTable"):
                ref = _quote(col["refTable"])
                ref_pk = _quote(f"{col['refEntity'].lower()}_id" if col.get("refEntity") else f"{col['refTable']}_id")
                # find PK on ref table
                ref_tbl = next((t for t in model.get("tables") or [] if t["table"] == col["refTable"]), None)
                if ref_tbl:
                    ref_pk_col = next((c["name"] for c in ref_tbl.get("columns") or [] if c.get("primaryKey")), None)
                    if ref_pk_col:
                        ref_pk = _quote(ref_pk_col)
                fk_lines.append(
                    f"ALTER TABLE {table} ADD CONSTRAINT fk_{tbl['table']}_{col['name']} "
                    f"FOREIGN KEY ({_quote(col['name'])}) REFERENCES {ref} ({ref_pk});"
                )
    if fk_lines:
        lines.append("")
        lines.extend(fk_lines)
    return "\n\n".join(lines) + "\n"
