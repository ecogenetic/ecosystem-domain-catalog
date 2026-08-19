#!/usr/bin/env python3.14
from __future__ import annotations

import json
from pathlib import Path

from agents.catalog_agent.tools import (
    expand_graph,
    get_ontology,
    heal_index,
    index_health,
    list_domains,
    search_catalog,
    validate_iris,
    validate_text,
)
from agents.shared.catalog_index import is_stub_mapping
from agents.tests.runner import load_suite, run_catalog_case


def test_index_has_all_domains(catalog_ready):
    listed = {d["id"] for d in list_domains()["domains"]}
    indexed = {
        r["domain_id"]
        for r in catalog_ready.connect().execute("SELECT DISTINCT domain_id FROM docs WHERE domain_id IS NOT NULL")
    }
    missing = listed - indexed - {"core"}
    assert not missing, missing


def test_stub_mappings_not_indexed(catalog_ready):
    rows = catalog_ready.connect().execute("SELECT extra FROM docs WHERE kind='mapping'").fetchall()
    for row in rows:
        extra = json.loads(row["extra"] or "{}")
        for m in extra.get("mappings") or []:
            assert not m.get("isStub")
    health = index_health()
    assert health.get("stubMappingsIndexed", 0) == 0


def test_stub_detector():
    stub = Path(__file__).resolve().parents[2] / "domains" / "bi" / "mappings" / "generic-mapping.ttl"
    assert is_stub_mapping(stub.read_text(encoding="utf-8"))
    real = Path(__file__).resolve().parents[2] / "domains" / "cvm" / "mappings" / "generic-mapping.ttl"
    assert not is_stub_mapping(real.read_text(encoding="utf-8"))


def test_catalog_suite_levels(catalog_ready):
    suite = load_suite("catalog")
    assert [c["level"] for c in suite["cases"]] == [1, 2, 3, 4, 5]
    failures = []
    for case in suite["cases"]:
        out = run_catalog_case(case)
        if out["status"] != "pass":
            failures.append(out)
    assert not failures, failures


def test_validate_iris_strips_unknown(catalog_ready):
    real = catalog_ready.connect().execute("SELECT iri FROM docs WHERE kind='class' LIMIT 1").fetchone()["iri"]
    checked = validate_iris(iris=[real, "https://example.com/not-a-term"])
    assert real in {v["iri"] for v in checked["valid"]}
    assert "https://example.com/not-a-term" in checked["invalid"]


def test_expand_object_property_edges(catalog_ready):
    iri = "https://ecosystemcode.com/ontology/crm#Opportunity"
    expanded = expand_graph(iri=iri, depth=1, rels=["objectProperty"])
    assert expanded["ok"]
    prop_edges = [e for e in expanded["edges"] if e.get("rel") and e["rel"] not in {"subClassOf", "mapping", "alignment", "equivalentClass"}]
    assert prop_edges, "CRM Opportunity should have at least one objectProperty class–class edge"
    assert any(e["from"] == iri or e["to"] == iri for e in prop_edges)


def test_opportunity_shapes_on_concept(catalog_ready):
    from agents.catalog_agent.tools import get_concept

    iri = "https://ecosystemcode.com/ontology/crm#Opportunity"
    concept = get_concept(iri=iri)
    assert concept.get("ok") is not False
    shapes = concept.get("shapes") or []
    lifecycle = concept.get("lifecycleStates") or []
    assert shapes or lifecycle, "Opportunity should expose SHACL shapes or lifecycle states"
    if shapes:
        assert any(s.get("in") or s.get("minCount") is not None or s.get("class") for s in shapes)
    if lifecycle:
        assert "won" in lifecycle or "lead" in lifecycle


def test_expand_customer_subclass(catalog_ready):
    iri = "https://ecosystemcode.com/ontology/cvm#Customer"
    expanded = expand_graph(iri=iri, depth=1, rels=["subClassOf"])
    assert expanded["ok"]
    assert expanded["nodes"]


def test_heal_index_runs(catalog_ready):
    result = heal_index()
    assert result.get("ok")


def test_industry_search_is_exclusive(catalog_ready):
    from agents.catalog_agent.tools import search_catalog

    result = search_catalog(query="Account", industry="banking", limit=20)
    assert result.get("ok")
    for match in result.get("matches") or []:
        assert match.get("industryId") == "banking", match


def test_validate_text_homonym(catalog_ready):
    result = validate_text(text="Account")
    statuses = {t["token"]: t["status"] for t in result["terms"]}
    assert statuses.get("account") in {"homonym", "matched"}
