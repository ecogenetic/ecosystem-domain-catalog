#!/usr/bin/env python3.14
from __future__ import annotations

from fastapi.testclient import TestClient


def test_catalog_app_health_and_search(catalog_ready):
    from agents.catalog_agent.app import app

    client = TestClient(app)
    assert client.get("/v1/health").json()["ok"] is True
    listed = client.post("/mcp/tools/list").json()["tools"]
    names = {t["name"] for t in listed}
    assert "search_catalog" in names
    body = client.post("/v1/search", json={"query": "deal", "limit": 8}).json()
    iris = [m.get("iri", "") for m in body.get("matches") or []]
    assert any("Opportunity" in iri for iri in iris)


def test_gateway_one_port(catalog_ready):
    from agents.gateway import app

    client = TestClient(app)
    health = client.get("/v1/health").json()
    assert health["ok"] is True
    assert client.get("/catalog/v1/health").json()["ok"] is True
    assert client.get("/data/v1/health").json()["ok"] is True
    assert "search_catalog" in {t["name"] for t in client.post("/catalog/mcp/tools/list").json()["tools"]}
    assert "query_mapped_data" in {t["name"] for t in client.post("/data/mcp/tools/list").json()["tools"]}
    listed = client.get("/docs")
    assert listed.status_code == 200


def test_data_app_health(catalog_ready):
    from agents.data_agent.app import app

    client = TestClient(app)
    assert client.get("/v1/health").json()["ok"] is True
    listed = client.post("/mcp/tools/list").json()["tools"]
    names = {t["name"] for t in listed}
    assert "query_mapped_data" in names
    assert "assess_complexity" in names
    query_tool = next(t for t in listed if t["name"] == "query_mapped_data")
    assert "query" in (query_tool.get("inputSchema") or {}).get("properties") or {}


def test_openapi_plan_paths(catalog_ready):
    from agents.catalog_agent.app import app as catalog_app
    from agents.data_agent.app import app as data_app

    catalog_paths = TestClient(catalog_app).get("/openapi.json").json()["paths"]
    assert "/v1/search" in catalog_paths
    assert "/v1/ontology/{domainId}" in catalog_paths
    assert "/v1/ontologies/preview" in catalog_paths
    data_paths = TestClient(data_app).get("/openapi.json").json()["paths"]
    assert "/v1/sources/connect" in data_paths
    assert "/v1/sources/{id}/introspect" in data_paths
    assert "/v1/sources/{id}/query" in data_paths
    assert "/v1/sources/{id}/complexity" in data_paths


def test_source_path_and_ontology_routes(catalog_ready):
    from agents.catalog_agent.app import app as catalog_app
    from agents.data_agent.app import app as data_app
    from agents.data_agent.registry import connect
    from agents.tests.fixtures_loader import sample_mapping_selections

    ont = TestClient(catalog_app).get("/v1/ontology/card", params={"industry": "banking"}).json()
    assert ont.get("ok") is True
    assert "RetailCreditCard" in (ont.get("turtle") or "") or ont.get("classes")

    connect(kind="memory", uri="memory://sample", source_id="sample")
    client = TestClient(data_app)
    schema = client.post("/v1/sources/sample/introspect", json={}).json()
    names = {c["name"] for c in schema.get("collections") or []}
    assert "customer" in names
    proposed = client.post("/v1/sources/sample/map", json={}).json()
    assert proposed["readiness"]["readyForQuery"] is False
    assert proposed["homonyms"]
    mapped = client.post(
        "/v1/sources/sample/map",
        json={"selections": sample_mapping_selections()},
    ).json()
    assert mapped.get("mapped")
    assert mapped["readiness"]["readyForQuery"] is True
    counted = client.post("/v1/sources/sample/query", json={"query": "how many customers do i have"}).json()
    assert counted.get("result") == 4
    assert counted.get("store")
    assert counted.get("mongo")


def test_preview_ontology_is_stateless(catalog_ready):
    from agents.catalog_agent.app import app as catalog_app

    turtle = """
@prefix : <https://example.com/ontology/demo#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

<https://example.com/ontology/demo> a owl:Ontology .
:Party a owl:Class ; skos:prefLabel "Party" .
:Customer a owl:Class ; rdfs:subClassOf :Party ; skos:prefLabel "Customer" .
"""
    client = TestClient(catalog_app)
    body = client.post("/v1/ontologies/preview", json={"turtle": turtle}).json()
    assert body.get("ok") is True
    assert body.get("stored") is False
    labels = {n.get("prefLabel") for n in body.get("nodes") or []}
    assert "Party" in labels
    assert "Customer" in labels
    rels = {(e.get("from"), e.get("to"), e.get("rel")) for e in body.get("edges") or []}
    assert any(edge[2] == "subClassOf" for edge in rels)


def test_preview_ontology_includes_rdfs_class(catalog_ready):
    from agents.catalog_agent.app import app as catalog_app

    turtle = """
@prefix env: <http://example.com/env/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.com/env/> a owl:Ontology .
env:Quantity a rdfs:Class ;
    rdfs:label "Quantity" .
env:Area a env:KindOfQuantity ;
    rdfs:label "Area" ;
    rdfs:subClassOf env:Quantity .
"""
    client = TestClient(catalog_app)
    body = client.post("/v1/ontologies/preview", json={"turtle": turtle}).json()
    assert body.get("ok") is True
    labels = {n.get("prefLabel") for n in body.get("nodes") or []}
    assert "Quantity" in labels
    assert "Area" in labels


def test_preview_ontology_rdf12_turtle(catalog_ready):
    from agents.catalog_agent.app import app as catalog_app

    turtle = """
VERSION "1.2"
PREFIX env: <http://example.com/env/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

<http://example.com/env/> a owl:Ontology .
env:Quantity a rdfs:Class ;
    rdfs:label "Quantity" .
env:Area rdfs:subClassOf env:Quantity {| rdfs:comment "IES building class" |} .
"""
    client = TestClient(catalog_app)
    body = client.post("/v1/ontologies/preview", json={"turtle": turtle}).json()
    assert body.get("ok") is True, body
    labels = {n.get("prefLabel") for n in body.get("nodes") or []}
    assert "Quantity" in labels
    assert "Area" in labels
