#!/usr/bin/env python3.14
"""Parse CREATE TABLE DDL into a schema-only store definition."""

from __future__ import annotations

import re
from typing import Any

import sqlparse


def parse_ddl(ddl: str) -> dict[str, dict[str, Any]]:
    tables: dict[str, dict[str, Any]] = {}
    for statement in sqlparse.parse(ddl or ""):
        text = str(statement).strip()
        if not re.match(r"CREATE\s+TABLE", text, re.I):
            continue
        name, body = _split_table(text)
        if not name or body is None:
            continue
        tables[name] = {"columns": _parse_columns(body)}
    return tables


def _split_table(text: str) -> tuple[str | None, str | None]:
    match = re.search(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<name>\"[^\"]+\"|`[^`]+`|\w+)\s*\((?P<body>.*)\)\s*;?\s*$",
        text,
        re.I | re.S,
    )
    if not match:
        return None, None
    return _unquote(match.group("name")), match.group("body")


def _parse_columns(body: str) -> list[dict[str, Any]]:
    columns: list[dict[str, Any]] = []
    for raw in _split_defs(body):
        piece = raw.strip().rstrip(",")
        if not piece or re.match(r"(PRIMARY|UNIQUE|CHECK|CONSTRAINT|FOREIGN)\b", piece, re.I):
            fk = re.search(
                r"FOREIGN\s+KEY\s*\(\s*(?P<col>\"[^\"]+\"|`[^`]+`|\w+)\s*\)\s*REFERENCES\s+(?P<table>\"[^\"]+\"|`[^`]+`|\w+)",
                piece,
                re.I,
            )
            if fk and columns:
                col_name = _unquote(fk.group("col"))
                for col in columns:
                    if col["name"] == col_name:
                        col["ref_table"] = _unquote(fk.group("table"))
            continue
        name_match = re.match(r"(?P<name>\"[^\"]+\"|`[^`]+`|\w+)\s+(?P<rest>.*)$", piece, re.S)
        if not name_match:
            continue
        name = _unquote(name_match.group("name"))
        rest = name_match.group("rest")
        type_match = re.match(r"(\w+(?:\s*\([^)]*\))?)", rest.strip())
        col_type = (type_match.group(1) if type_match else "text").split("(")[0].lower()
        ref_table = None
        refs = re.search(r"REFERENCES\s+(?P<table>\"[^\"]+\"|`[^`]+`|\w+)", rest, re.I)
        if refs:
            ref_table = _unquote(refs.group("table"))
        columns.append({"name": name, "type": col_type, "ref_table": ref_table})
    return columns


def _split_defs(body: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return parts


def _unquote(name: str) -> str:
    n = name.strip()
    if (n.startswith('"') and n.endswith('"')) or (n.startswith("`") and n.endswith("`")):
        return n[1:-1]
    return n
