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
MAX_LOCAL_JOIN_ROWS = 10_000


def compile_query_plan(source_id: str, query: str) -> dict[str, Any]:
    mapping = load_mapping(source_id)
    mapped = mapping.get("mapped") or []
    if not mapped:
        return {"ok": False, "error": "no_mapping"}
    if not _mapping_ready(mapping):
        return {
            "ok": False,
            "error": "mapping_not_ready",
            "readiness": mapping.get("readiness"),
            "unmapped": mapping.get("unmapped") or [],
            "homonyms": mapping.get("homonyms") or [],
        }
    q = query.lower()
    target, target_candidates = _pick_target(q, mapped)
    if not target:
        if target_candidates:
            return {
                "ok": False,
                "error": "ambiguous_target_class",
                "targetCandidates": target_candidates,
            }
        return {"ok": False, "error": "no_target_class"}
    filters: list[dict[str, Any]] = []
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
        temporal = _first_temporal(mapped, q)
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

    joins, disconnected = _needed_joins(target, filters, mapped, q)
    if disconnected:
        return {
            "ok": False,
            "error": "unmapped_relationship",
            "targetClass": target["entity"],
            "unmappedRelationships": disconnected,
        }
    plan = {
        "ok": True,
        "targetClass": target["entity"],
        "collection": target["collection"],
        "filters": filters,
        "joins": joins,
        "aggregate": "count",
    }
    return plan


def execute_query_plan(store: DocumentStore, source_id: str, plan: dict[str, Any]) -> dict[str, Any]:
    if not plan.get("ok", True):
        return {
            "ok": False,
            "error": plan.get("error") or "invalid_plan",
            "unmapped": plan.get("unmapped"),
        }
    mapping = load_mapping(source_id)
    if not _mapping_ready(mapping):
        return {"ok": False, "error": "mapping_not_ready", "readiness": mapping.get("readiness")}
    mapped = {m["entity"]: m for m in mapping.get("mapped") or []}
    target_name = plan.get("targetClass")
    if target_name not in mapped:
        return {"ok": False, "error": "no_target_class"}
    if plan.get("aggregate", "count") != "count":
        return {"ok": False, "error": "unsupported_aggregate"}

    joins = plan.get("joins") or []
    filters = plan.get("filters") or []
    invalid_filter = _validate_filters(filters, mapped)
    if invalid_filter:
        return invalid_filter
    invalid_join = _validate_joins(joins, mapped)
    if invalid_join:
        return invalid_join
    foreign_filters = [f for f in filters if f.get("entity") != target_name]
    if foreign_filters and not joins:
        return {
            "ok": False,
            "error": "unmapped_relationship",
            "unmappedRelationships": [
                {"from": target_name, "to": filt.get("entity")} for filt in foreign_filters
            ],
        }
    store_filter = _local_filter(plan, target_name)

    # Push filters to the store when the plan stays on one collection (Mongo/Postgres/memory).
    if not joins and not foreign_filters:
        collection = mapped[target_name]["collection"]
        for filt in filters:
            entry = mapped.get(filt["entity"])
            if not entry:
                return {"ok": False, "error": "unmapped_field", "unmapped": [filt["entity"]]}
            if filt["field"] not in _allowed_fields(entry):
                return {"ok": False, "error": "unmapped_field", "unmapped": [filt["field"]]}
        result = store.count(collection, store_filter or None)
        store_info = {
            "kind": getattr(store, "kind", "memory"),
            "collection": collection,
            "filter": store_filter,
            "joins": [],
            "pushdown": True,
            "complete": True,
        }
        return {"ok": True, "result": result, "store": store_info, "mongo": store_info}

    involved = {target_name} | {f["entity"] for f in filters}
    for join in joins:
        involved.add(join.get("from") or "")
        involved.add(join.get("to") or "")
    involved.discard("")

    row_counts: dict[str, int] = {}
    for entity in involved:
        entry = mapped.get(entity)
        if not entry:
            return {"ok": False, "error": "unmapped_field", "unmapped": [entity]}
        row_counts[entity] = store.count(entry["collection"])
    over_limit = {entity: count for entity, count in row_counts.items() if count > MAX_LOCAL_JOIN_ROWS}
    if over_limit:
        return {
            "ok": False,
            "error": "incomplete_execution",
            "reason": "local_join_row_limit",
            "maxRowsPerEntity": MAX_LOCAL_JOIN_ROWS,
            "rowCounts": over_limit,
        }

    tables: dict[str, list[dict[str, Any]]] = {}
    for entity in involved:
        entry = mapped[entity]
        tables[entity] = [
            _with_id(d)
            for d in store.find(entry["collection"], limit=max(1, row_counts[entity]))
        ]

    for filt in filters:
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

    if len(involved) > 1:
        tables = _apply_joins(tables, mapped, involved)

    result = len(tables.get(target_name) or [])
    store_info = {
        "kind": getattr(store, "kind", "memory"),
        "collection": mapped[target_name]["collection"],
        "filter": store_filter,
        "joins": joins,
        "pushdown": False,
        "complete": True,
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


def _pick_target(
    q: str,
    mapped: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, list[str]]:
    how = HOW_MANY_RE.search(q)
    if how:
        stem = how.group(1).rstrip("s").lower()
        for m in mapped:
            name = m["entity"].lower()
            if name == stem or name == how.group(1).lower() or name.rstrip("s") == stem:
                return m, []
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
        top_score = ranked[0][0]
        tied = [item[1] for item in ranked if item[0] == top_score]
        if len(tied) == 1:
            return tied[0], []
        return None, [item["entity"] for item in tied]
    return None, []


def _mapping_ready(mapping: dict[str, Any]) -> bool:
    readiness = mapping.get("readiness")
    if isinstance(readiness, dict) and "readyForQuery" in readiness:
        return bool(readiness.get("readyForQuery"))
    return bool(mapping.get("mapped")) and not (mapping.get("unmapped") or mapping.get("homonyms"))


def _first_temporal(mapped: list[dict[str, Any]], query: str = "") -> dict[str, str] | None:
    q = (query or "").lower()
    ranked: list[tuple[int, dict[str, str]]] = []
    for m in mapped:
        score = 0
        if _mentioned(m["entity"], q):
            score += 5
        # prefer interaction/event timestamps when the NL mentions interacting
        if "interact" in q and "interact" in m["entity"].lower():
            score += 8
        if "order" in q and "order" in m["entity"].lower():
            score += 4
        for f in m.get("temporalFields") or []:
            ranked.append((score + 2, {"entity": m["entity"], "field": f}))
        for p in m.get("properties") or []:
            fname = p["field"].lower()
            if fname.endswith("at") or "date" in fname or "time" in fname:
                ranked.append((score + 1, {"entity": m["entity"], "field": p["field"]}))
    ranked.sort(key=lambda x: -x[0])
    return ranked[0][1] if ranked else None


def _needed_joins(
    target: dict[str, Any],
    filters: list[dict[str, Any]],
    mapped: list[dict[str, Any]],
    query: str = "",
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    mentioned = {m["entity"] for m in mapped if _mentioned(m["entity"], query)}
    required = {target["entity"]} | {f["entity"] for f in filters} | mentioned
    graph: dict[str, list[tuple[str, dict[str, Any]]]] = {m["entity"]: [] for m in mapped}
    for entry in mapped:
        source = entry["entity"]
        for raw_join in entry.get("joins") or []:
            destination = _mapped_entity_name(raw_join.get("targetEntity"), mapped)
            if not destination:
                continue
            join = {"from": source, "to": destination, "field": raw_join["field"]}
            graph[source].append((destination, join))
            graph[destination].append((source, join))

    selected: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str]] = set()
    disconnected: list[dict[str, str]] = []
    start = target["entity"]
    for destination in sorted(required - {start}):
        path = _shortest_join_path(graph, start, destination)
        if path is None:
            disconnected.append({"from": start, "to": destination})
            continue
        for join in path:
            key = (join["from"], join["to"], join["field"])
            if key not in seen_edges:
                seen_edges.add(key)
                selected.append(join)
    return selected, disconnected


def _shortest_join_path(
    graph: dict[str, list[tuple[str, dict[str, Any]]]],
    start: str,
    destination: str,
) -> list[dict[str, Any]] | None:
    queue: list[tuple[str, list[dict[str, Any]]]] = [(start, [])]
    visited = {start}
    while queue:
        node, path = queue.pop(0)
        if node == destination:
            return path
        for neighbor, join in graph.get(node, []):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            queue.append((neighbor, [*path, join]))
    return None


def _mapped_entity_name(value: Any, mapped: list[dict[str, Any]]) -> str | None:
    wanted = str(value or "").lower()
    return next((item["entity"] for item in mapped if item["entity"].lower() == wanted), None)


def _validate_filters(
    filters: list[dict[str, Any]],
    mapped: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    for filt in filters:
        entity = filt.get("entity")
        field = filt.get("field")
        if entity not in mapped:
            return {"ok": False, "error": "unmapped_field", "unmapped": [entity]}
        if field not in _allowed_fields(mapped[entity]):
            return {"ok": False, "error": "unmapped_field", "unmapped": [field]}
        if filt.get("op") not in {"eq", "gte"}:
            return {
                "ok": False,
                "error": "unsupported_operator",
                "operator": filt.get("op"),
            }
        if "value" not in filt:
            return {"ok": False, "error": "invalid_filter", "field": field}
    return None


def _validate_joins(
    joins: list[dict[str, Any]],
    mapped: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    allowed = {
        (entry["entity"], str(join.get("targetEntity") or ""), join.get("field"))
        for entry in mapped.values()
        for join in entry.get("joins") or []
    }
    for join in joins:
        key = (join.get("from"), join.get("to"), join.get("field"))
        if key not in allowed:
            return {
                "ok": False,
                "error": "unmapped_relationship",
                "unmappedRelationships": [
                    {"from": str(key[0] or ""), "to": str(key[1] or "")}
                ],
            }
    return None


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
