#!/usr/bin/env python3.14
"""Introspect collections or tables, samples, and lookup enums."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from agents.data_agent.store import PII_EXCLUDE, DocumentStore

INFRA = {"users", "settings", "logs", "lookups"}


def entity_from_collection(name: str) -> str:
    parts = re.split(r"[_\-]+", name or "")
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def infer_field_type(values: list[Any]) -> str:
    for v in values:
        if isinstance(v, bool):
            return "boolean"
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return "number"
        if isinstance(v, dict):
            return "object"
        if isinstance(v, list):
            return "array"
        s = str(v)
        if "T" in s and re.match(r"\d{4}-\d{2}-\d{2}", s):
            return "dateTime"
    return "string"


def _ref_entity(field_name: str, ref_table: str | None = None) -> str | None:
    if ref_table:
        return entity_from_collection(ref_table)
    if field_name.startswith("id_"):
        target = field_name[3:]
    elif field_name.endswith("_id"):
        target = field_name[:-3]
    elif field_name.endswith("Id"):
        target = field_name[:-2]
    else:
        return None
    return entity_from_collection(target) if target else None


def introspect(store: DocumentStore, sample_size: int = 20) -> dict[str, Any]:
    collections = []
    lookups_enums: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    names = store.list_collections()
    if "lookups" in names:
        for row in store.find("lookups", limit=5000):
            entity = str(row.get("entity") or "")
            field = str(row.get("field") or "")
            value = row.get("value")
            if entity and field and value is not None and str(value) not in lookups_enums[entity][field]:
                lookups_enums[entity][field].append(str(value))

    declared = store.column_defs() or {}

    for name in names:
        count = store.count(name)
        samples = [] if getattr(store, "schema_only", False) else store.find(name, limit=sample_size, projection=PII_EXCLUDE)
        fields: dict[str, dict[str, Any]] = {}
        for col in declared.get(name) or []:
            fname = col.get("name") or ""
            if not fname or fname.startswith("__"):
                continue
            fields[fname] = {
                "name": fname,
                "types": {col.get("type") or "string"},
                "ref": _ref_entity(fname, col.get("ref_table")),
            }
        for doc in samples:
            for key, val in doc.items():
                if key.startswith("__"):
                    continue
                slot = fields.setdefault(key, {"name": key, "types": set(), "ref": None})
                slot["types"].add(type(val).__name__)
                if not slot.get("ref"):
                    slot["ref"] = _ref_entity(key)
        entity = entity_from_collection(name)
        enums = dict(lookups_enums.get(entity) or {})
        for key in list(fields):
            if key.lower() in {"status", "state", "region", "channel", "gender", "segment"} and key not in enums:
                values = [str(v) for v in store.distinct(name, key) if v is not None]
                if 0 < len(values) <= 24:
                    enums[key] = values
        collections.append(
            {
                "name": name,
                "entity": entity,
                "count": count,
                "infrastructure": name.lower() in INFRA,
                "schemaOnly": bool(getattr(store, "schema_only", False)),
                "fields": [
                    {
                        "name": f["name"],
                        "types": sorted(str(t) for t in f["types"]),
                        "ref": f["ref"],
                    }
                    for f in fields.values()
                ],
                "enumsFromLookups": enums,
            }
        )
    return {
        "ok": True,
        "kind": getattr(store, "kind", "memory"),
        "schemaOnly": bool(getattr(store, "schema_only", False)),
        "collections": collections,
    }
