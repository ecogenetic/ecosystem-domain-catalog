#!/usr/bin/env python3.14
"""Emit MongoDB JSON Schema from a PhysicalModel."""

from __future__ import annotations

import json
from typing import Any


def generate_mongo_schema(model: dict[str, Any]) -> dict[str, Any]:
    collections: dict[str, Any] = {}
    for tbl in model.get("tables") or []:
        props: dict[str, Any] = {}
        required: list[str] = []
        for col in tbl.get("columns") or []:
            if col.get("primaryKey"):
                continue
            prop: dict[str, Any] = {"bsonType": col.get("bsonType") or "string"}
            if col.get("enum"):
                prop["enum"] = col["enum"]
            props[col["name"]] = prop
            if not col.get("nullable", True):
                required.append(col["name"])
        schema: dict[str, Any] = {
            "bsonType": "object",
            "properties": props,
        }
        if required:
            schema["required"] = required
        collections[tbl["table"]] = schema
    return {"ok": True, "collections": collections}


def generate_mongo_schema_text(model: dict[str, Any]) -> str:
    return json.dumps(generate_mongo_schema(model), indent=2)
