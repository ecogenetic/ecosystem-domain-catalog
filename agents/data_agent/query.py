#!/usr/bin/env python3.14
"""Deterministic NL → mapped query compiler and sandbox executor."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

from agents.data_agent.mapping import load_mapping
from agents.data_agent.store import DocumentStore

MONTH_RE = re.compile(r"last month|past month|previous month|over the last month", re.I)
HOW_MANY_RE = re.compile(r"how many\s+([a-z0-9_]+)", re.I)


def compile_query_plan(source_id: str, query: str) -> dict[str, Any]:
    mapping = load_mapping(source_id)
    mapped = mapping.get("mapped") or []
    if not mapped:
        return {"ok": False, "error": "no_mapping"}
    q = query.lower()
    target = _pick_target(q, mapped)
    if not target:
        return {"ok": False, "error": "no_target_class"}
    filters: list[dict[str, Any]] = []
    unmapped: list[str] = []

    for entity_entry in mapped:
        enums = entity_entry.get("enums") or {}
        for field, values in enums.items():
            for value in values:
                if str(value).lower() in q:
                    filters.append(
                        {
                            "entity": entity_entry["entity"],
                            "field": field,
                            "op": "eq",
                            "value": value,
                        }
                    )
        for prop in entity_entry.get("properties") or []:
            for value in prop.get("enums") or []:
                if str(value).lower() in q and not any(
                    f["field"] == prop["field"] and str(f["value"]).lower() == str(value).lower() for f in filters
                ):
                    filters.append(
                        {
                            "entity": entity_entry["entity"],
                            "field": prop["field"],
                            "op": "eq",
                            "value": value,
                        }
                    )

    if MONTH_RE.search(q):
        temporal = _first_temporal(mapped)
        if temporal:
            start = datetime.now(timezone.utc) - timedelta(days=31)
            filters.append(
                {
                    "entity": temporal["entity"],
                    "field": temporal["field"],
                    "op": "gte",
                    "value": start.isoformat(),
                }
            )

    joins = _needed_joins(target, filters, mapped, q)
    plan = {
        "ok": True,
        "targetClass": target["entity"],
        "collection": target["collection"],
        "filters": filters,
        "joins": joins,
        "aggregate": "count",
    }
    if unmapped:
        plan = {"ok": False, "error": "unmapped_field", "unmapped": unmapped, **plan}
        plan["ok"] = False
    return plan


def execute_query_plan(store: DocumentStore, source_id: str, plan: dict[str, Any]) -> dict[str, Any]:
    if plan.get("error") == "unmapped_field" and not plan.get("ok", True):
        return {"ok": False, "error": "unmapped_field", "unmapped": plan.get("unmapped")}
    mapping = load_mapping(source_id)
    mapped = {m["entity"]: m for m in mapping.get("mapped") or []}
    target_name = plan.get("targetClass")
    if target_name not in mapped:
        return {"ok": False, "error": "no_target_class"}

    tables: dict[str, list[dict[str, Any]]] = {}
    for entity, entry in mapped.items():
        tables[entity] = [_with_id(d) for d in store.find(entry["collection"], limit=10000)]

    for filt in plan.get("filters") or []:
        entity = filt["entity"]
        if entity not in mapped:
            return {"ok": False, "error": "unmapped_field", "unmapped": [entity]}
        entry = mapped[entity]
        allowed = _allowed_fields(entry)
        if filt["field"] not in allowed:
            return {"ok": False, "error": "unmapped_field", "unmapped": [filt["field"]]}
        docs = tables.get(entity) or []
        field = filt["field"]
        if filt["op"] == "eq":
            want = str(filt["value"]).lower()
            docs = [d for d in docs if str(d.get(field, "")).lower() == want]
        elif filt["op"] == "gte":
            bound = str(filt["value"])
            docs = [d for d in docs if str(d.get(field) or "") >= bound]
        tables[entity] = docs

    involved = {target_name} | {f["entity"] for f in plan.get("filters") or []}
    for join in plan.get("joins") or []:
        involved.add(join.get("from") or "")
        involved.add(join.get("to") or "")
    involved.discard("")
    if len(involved) > 1:
        tables = _apply_joins(tables, mapped, involved)

    result = len(tables.get(target_name) or [])
    store_filter = _local_filter(plan, target_name)
    store_info = {
        "kind": getattr(store, "kind", "memory"),
        "collection": mapped[target_name]["collection"],
        "filter": store_filter,
        "joins": plan.get("joins") or [],
    }
    return {
        "ok": True,
        "result": result,
        "store": store_info,
        "mongo": store_info,
    }


def query_mapped_data(store: DocumentStore, source_id: str, query: str) -> dict[str, Any]:
    plan = compile_query_plan(source_id, query)
    if not plan.get("ok", True):
        if plan.get("error") == "unmapped_field":
            plan.pop("error", None)
            plan["filters"] = [f for f in plan.get("filters") or [] if f.get("field") not in (plan.get("unmapped") or [])]
            plan["ok"] = True
        else:
            return plan
    executed = execute_query_plan(store, source_id, plan)
    if not executed.get("ok"):
        executed["plan"] = plan
        return executed
    executed["plan"] = plan
    executed["query"] = query
    return executed


def _with_id(doc: dict[str, Any]) -> dict[str, Any]:
    out = dict(doc)
    if "_id" not in out and "id" in out:
        out["_id"] = str(out["id"])
    elif "_id" in out:
        out["_id"] = str(out["_id"])
    return out


def _allowed_fields(entry: dict[str, Any]) -> set[str]:
    allowed = {p["field"] for p in entry.get("properties") or []}
    allowed |= set((entry.get("enums") or {}).keys())
    allowed |= {j["field"] for j in entry.get("joins") or []}
    allowed |= set(entry.get("temporalFields") or [])
    return allowed


def _pick_target(q: str, mapped: list[dict[str, Any]]) -> dict[str, Any] | None:
    how = HOW_MANY_RE.search(q)
    if how:
        stem = how.group(1).rstrip("s").lower()
        for m in mapped:
            name = m["entity"].lower()
            if name == stem or name == how.group(1).lower() or name.rstrip("s") == stem:
                return m
    ranked = []
    for m in mapped:
        score = 0
        name = m["entity"].lower()
        if name in q or name + "s" in q:
            score += 5
        for word in re.findall(r"[a-z]+", name):
            if len(word) > 2 and word in q:
                score += 2
        ranked.append((score, m))
    ranked.sort(key=lambda x: -x[0])
    if ranked and ranked[0][0] > 0:
        return ranked[0][1]
    return mapped[0] if mapped else None


def _first_temporal(mapped: list[dict[str, Any]]) -> dict[str, str] | None:
    for m in mapped:
        for f in m.get("temporalFields") or []:
            return {"entity": m["entity"], "field": f}
        for p in m.get("properties") or []:
            fname = p["field"].lower()
            if fname.endswith("at") or "date" in fname or "time" in fname:
                return {"entity": m["entity"], "field": p["field"]}
    return None


def _needed_joins(
    target: dict[str, Any],
    filters: list[dict[str, Any]],
    mapped: list[dict[str, Any]],
    query: str = "",
) -> list[dict[str, Any]]:
    mentioned = {m["entity"] for m in mapped if _mentioned(m["entity"], query)}
    entities = {target["entity"]} | {f["entity"] for f in filters} | mentioned
    by_name = {m["entity"]: m for m in mapped}
    joins: list[dict[str, Any]] = []
    for entity, entry in by_name.items():
        for j in entry.get("joins") or []:
            other = j.get("targetEntity")
            if entity in entities and other in entities:
                joins.append({"from": entity, "to": other, "field": j["field"]})
    uniq = []
    seen = set()
    for j in joins:
        key = (j.get("from"), j.get("to"), j.get("field"))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(j)
    return uniq


def _mentioned(entity: str, query: str) -> bool:
    q = (query or "").lower()
    name = entity.lower()
    return name in q or name + "s" in q or name.rstrip("s") in q.split()


def _apply_joins(
    tables: dict[str, list[dict[str, Any]]],
    mapped: dict[str, dict[str, Any]],
    involved: set[str],
) -> dict[str, list[dict[str, Any]]]:
    joins: list[tuple[str, str, str]] = []
    for entity, entry in mapped.items():
        if entity not in involved:
            continue
        for j in entry.get("joins") or []:
            other = j.get("targetEntity")
            if other in involved:
                joins.append((entity, other, j["field"]))
    if not joins:
        return tables
    working = {k: list(v) for k, v in tables.items()}
    for _ in range(6):
        changed = False
        for src, tgt, field in joins:
            src_docs = working.get(src) or []
            tgt_docs = working.get(tgt) or []
            tgt_ids = {_row_id(d) for d in tgt_docs}
            src_keys = {str(d.get(field) or "") for d in src_docs}
            new_src = [d for d in src_docs if str(d.get(field) or "") in tgt_ids]
            new_tgt = [d for d in tgt_docs if _row_id(d) in src_keys]
            if len(new_src) != len(src_docs) or len(new_tgt) != len(tgt_docs):
                changed = True
            working[src] = new_src
            working[tgt] = new_tgt
        if not changed:
            break
    return working


def _row_id(doc: dict[str, Any]) -> str:
    return str(doc.get("_id") or doc.get("id") or "")


def _local_filter(plan: dict[str, Any], entity: str) -> dict[str, Any]:
    clauses = []
    for filt in plan.get("filters") or []:
        if filt["entity"] != entity:
            continue
        if filt["op"] == "eq":
            clauses.append({filt["field"]: filt["value"]})
        elif filt["op"] == "gte":
            clauses.append({filt["field"]: {"$gte": filt["value"]}})
    if not clauses:
        return {}
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}
