#!/usr/bin/env python3.14
"""Derive five complexity levels from a completed source mapping graph."""

from __future__ import annotations

import json
from typing import Any

import networkx as nx

from agents.data_agent.mapping import load_mapping
from agents.shared.paths import source_dir


def assess_complexity(source_id: str) -> dict[str, Any]:
    mapping = load_mapping(source_id)
    mapped = mapping.get("mapped") or []
    g = nx.Graph()
    enum_fields: list[str] = []
    temporal_fields: list[str] = []
    props = 0
    for m in mapped:
        g.add_node(m["entity"])
        props += len(m.get("properties") or [])
        for field, values in (m.get("enums") or {}).items():
            if values:
                enum_fields.append(f"{m['entity']}.{field}")
        for t in m.get("temporalFields") or []:
            temporal_fields.append(f"{m['entity']}.{t}")
        for j in m.get("joins") or []:
            if j.get("targetEntity"):
                g.add_edge(m["entity"], j["targetEntity"])

    join_paths: list[list[str]] = []
    max_path = 0
    nodes = list(g.nodes)
    for a in nodes:
        for b in nodes:
            if a == b:
                continue
            try:
                for path in nx.all_simple_paths(g, a, b, cutoff=3):
                    hop = len(path) - 1
                    max_path = max(max_path, hop)
                    if hop >= 2:
                        join_paths.append(path)
            except nx.NetworkXNoPath:
                continue
    # unique paths
    uniq_paths = []
    seen_p = set()
    for p in join_paths:
        key = tuple(p)
        if key in seen_p:
            continue
        seen_p.add(key)
        uniq_paths.append(p)
    join_paths = uniq_paths[:8]

    supported: list[int] = []
    unsupported: list[dict[str, Any]] = []
    if mapped:
        supported.append(1)
    else:
        unsupported.append({"level": 1, "status": "skipped", "reason": "no_mapped_classes"})
    if mapped and (enum_fields or props):
        supported.append(2)
    else:
        unsupported.append({"level": 2, "status": "skipped", "reason": "no_filter_fields"})
    if mapped and temporal_fields:
        supported.append(3)
    else:
        unsupported.append({"level": 3, "status": "skipped", "reason": "no_temporal_fields"})
    if len(mapped) >= 2 and g.number_of_edges() >= 1:
        supported.append(4)
    else:
        unsupported.append({"level": 4, "status": "skipped", "reason": "no_join_edge"})
    if max_path >= 2 and enum_fields and temporal_fields:
        supported.append(5)
    else:
        unsupported.append({"level": 5, "status": "skipped", "reason": "no_multihop_compound"})

    result = {
        "ok": True,
        "sourceId": source_id,
        "maxLevel": max(supported) if supported else 0,
        "supportedLevels": supported,
        "evidence": {
            "mappedClasses": len(mapped),
            "mappedProperties": props,
            "enumFields": enum_fields,
            "temporalFields": temporal_fields,
            "maxJoinPath": max_path,
            "joinPaths": join_paths[:8],
        },
        "unsupported": [u for u in unsupported if u["level"] not in supported],
    }
    dest = source_dir(source_id) / "complexity.json"
    dest.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def export_rerun_suite(source_id: str, include_unsupported: bool = False) -> dict[str, Any]:
    complexity = assess_complexity(source_id)
    mapping = load_mapping(source_id)
    mapped = {m["entity"]: m for m in mapping.get("mapped") or []}
    cases = []
    templates = {
        1: {
            "query": "how many customers do i have",
            "expect": {"targetClass": "Customer", "aggregate": "count"},
        },
        2: {
            "query": "how many active customers",
            "expect": {"targetClass": "Customer", "filterField": "status"},
        },
        3: {
            "query": "how many orders in the last month",
            "expect": {"targetClass": "Order"},
        },
        4: {
            "query": "how many orders have customers",
            "expect": {"targetClass": "Order"},
        },
        5: {
            "query": "how many orders have customers that are active that ordered in the last month",
            "expect": {"targetClass": "Order"},
        },
    }
    for level, tmpl in templates.items():
        supported = level in complexity["supportedLevels"]
        if not supported and not include_unsupported:
            continue
        case = {
            "id": f"L{level}-{source_id}",
            "level": level,
            "query": tmpl["query"],
            "expect": tmpl["expect"],
            "status": "active" if supported else "skipped",
            "reason": None if supported else next((u["reason"] for u in complexity["unsupported"] if u["level"] == level), None),
            "collections": {k: v.get("collection") for k, v in mapped.items()},
        }
        cases.append(case)
    suite = {"sourceId": source_id, "complexity": complexity, "cases": cases}
    path = source_dir(source_id) / "rerun_suite.json"
    path.write_text(json.dumps(suite, indent=2), encoding="utf-8")
    return {"ok": True, "path": str(path), "cases": cases, "maxLevel": complexity["maxLevel"]}
