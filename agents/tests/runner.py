#!/usr/bin/env python3.14
"""Load and execute stored catalog/data suites."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SUITES = Path(__file__).resolve().parent / "suites"


def load_suite(agent: str) -> dict[str, Any]:
    return json.loads((SUITES / agent / "cases.json").read_text(encoding="utf-8"))


def run_catalog_case(case: dict[str, Any], use_llm: bool = False) -> dict[str, Any]:
    from agents.catalog_agent.tools import expand_graph, search_catalog

    result = search_catalog(
        query=case["query"],
        industry=case.get("industry"),
        domain=case.get("domain"),
        includeOntology=case.get("includeOntology", False),
        limit=20,
        useLlm=use_llm,
    )
    expect = case.get("expect") or {}
    ok, detail = _check_catalog(result, expect, case)
    if case.get("expand") and result.get("matches"):
        iri = next((m["iri"] for m in result["matches"] if expect.get("iriContains", "") in (m.get("iri") or "")), result["matches"][0]["iri"])
        expanded = expand_graph(iri=iri, depth=1, rels=["subClassOf"])
        if not expanded.get("edges"):
            ok = False
            detail.append("expand produced no edges")
        result["expand"] = {"nodeCount": len(expanded.get("nodes") or []), "edgeCount": len(expanded.get("edges") or [])}
    return {"id": case["id"], "level": case["level"], "status": "pass" if ok else "fail", "detail": detail, "result": _clip_result(result)}


def run_data_case(case: dict[str, Any], source_id: str, use_llm: bool = False) -> dict[str, Any]:
    from agents.data_agent.tools import query_mapped_data

    result = query_mapped_data(id=source_id, query=case["query"], useLlm=use_llm)
    expect = case.get("expect") or {}
    ok = True
    detail = []
    if expect.get("targetClass") and (result.get("plan") or {}).get("targetClass") != expect["targetClass"]:
        ok = False
        detail.append(f"target {(result.get('plan') or {}).get('targetClass')} != {expect['targetClass']}")
    if "count" in expect and result.get("result") != expect["count"]:
        ok = False
        detail.append(f"count {result.get('result')} != {expect['count']}")
    if expect.get("filterField"):
        fields = [f.get("field") for f in (result.get("plan") or {}).get("filters") or []]
        if expect["filterField"] not in fields:
            ok = False
            detail.append(f"missing filter {expect['filterField']}")
    return {"id": case["id"], "level": case["level"], "status": "pass" if ok else "fail", "detail": detail, "result": _clip_result(result)}


def rerun(agent: str = "all", source_id: str = "sample", use_llm: bool = False) -> dict[str, Any]:
    cases_out: list[dict[str, Any]] = []
    if agent in {"catalog", "all"}:
        from agents.shared.catalog_index import get_index

        get_index()
        suite = load_suite("catalog")
        for case in suite["cases"]:
            cases_out.append(run_catalog_case(case, use_llm=use_llm))
    if agent in {"data", "all"}:
        _ensure_fixture_source(source_id)
        suite = load_suite("data")
        for case in suite["cases"]:
            cases_out.append(run_data_case(case, source_id, use_llm=use_llm))
    passed = sum(1 for c in cases_out if c["status"] == "pass")
    return {"cases": cases_out, "passed": passed, "failed": len(cases_out) - passed, "total": len(cases_out)}


def _ensure_fixture_source(source_id: str) -> None:
    from agents.data_agent.registry import register
    from agents.data_agent.tools import generate_source_ontology, introspect_schema, map_to_catalog
    from agents.tests.fixtures_loader import memory_sample_store, sample_mapping_selections

    store = memory_sample_store()
    register(source_id, store, {"kind": "memory"})
    introspect_schema(id=source_id)
    generate_source_ontology(id=source_id)
    map_to_catalog(id=source_id, selections=sample_mapping_selections())


def _check_catalog(result: dict[str, Any], expect: dict[str, Any], case: dict[str, Any]) -> tuple[bool, list[str]]:
    detail: list[str] = []
    matches = result.get("matches") or []
    iris = [m.get("iri") or "" for m in matches]
    domains = {m.get("domainId") for m in matches}
    ok = True
    if expect.get("iriContains"):
        if not any(expect["iriContains"] in iri for iri in iris):
            ok = False
            detail.append(f"missing IRI fragment {expect['iriContains']} in {iris[:5]}")
    if expect.get("domainId") and expect["domainId"] not in domains and not any(m.get("domainId") == expect["domainId"] for m in matches):
        # allow if top match
        if not matches or matches[0].get("domainId") != expect["domainId"]:
            if expect["domainId"] not in domains:
                ok = False
                detail.append(f"domain {expect['domainId']} not in {domains}")
    if expect.get("ontologyPresent") and not (result.get("ontology") or {}).get("turtle"):
        ok = False
        detail.append("ontology turtle missing")
    if expect.get("homonymDomains"):
        missing = [d for d in expect["homonymDomains"] if d not in domains]
        if missing:
            ok = False
            detail.append(f"homonym domains missing {missing}")
        if len(domains) < 2:
            ok = False
            detail.append("expected distinct homonym domains")
    if expect.get("anyDomain") and not (domains & set(expect["anyDomain"])):
        ok = False
        detail.append(f"none of {expect['anyDomain']} in {domains}")
    if expect.get("anyLocalName"):
        locals_ = { (m.get("localName") or "") for m in matches }
        if not (set(expect["anyLocalName"]) & locals_):
            # also check IRI tails
            tails = {iri.rsplit("#", 1)[-1] for iri in iris}
            if not (set(expect["anyLocalName"]) & tails):
                ok = False
                detail.append(f"missing local names {expect['anyLocalName']}")
    return ok, detail


def _clip_result(result: dict[str, Any]) -> dict[str, Any]:
    out = dict(result)
    if isinstance(out.get("ontology"), dict) and out["ontology"].get("turtle"):
        turtle = out["ontology"]["turtle"]
        out["ontology"] = {**out["ontology"], "turtle": turtle[:400] + ("…" if len(turtle) > 400 else "")}
    matches = out.get("matches")
    if isinstance(matches, list) and len(matches) > 8:
        out["matches"] = matches[:8]
    llm = out.get("llm")
    if isinstance(llm, dict) and isinstance(llm.get("trace"), list) and len(llm["trace"]) > 4:
        out["llm"] = {**llm, "trace": llm["trace"][:4]}
    return out
