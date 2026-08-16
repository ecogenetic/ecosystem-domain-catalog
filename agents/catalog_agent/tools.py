#!/usr/bin/env python3.14
"""Catalog Agent tool handlers bound to the catalog graph index."""

from __future__ import annotations

from typing import Any

from agents.shared.catalog_index import get_index
from agents.shared.server import ToolSpec


def rebuild_index(incremental: bool = False) -> dict[str, Any]:
    return get_index().rebuild(incremental=bool(incremental))


def index_health() -> dict[str, Any]:
    return get_index().health()


def heal_index(paths: list[str] | None = None) -> dict[str, Any]:
    return get_index().heal_index(paths)


def search_catalog(
    query: str,
    industry: str | None = None,
    domain: str | None = None,
    includeOntology: bool = False,
    include_ontology: bool | None = None,
    limit: int = 12,
    useLlm: bool = False,
    use_llm: bool | None = None,
) -> dict[str, Any]:
    include = includeOntology or bool(include_ontology)
    want_llm = useLlm or bool(use_llm)
    idx = get_index()
    result = idx.search(query or "", industry=industry, domain=domain, include_ontology=include, limit=limit or 12)
    if not result.get("matches"):
        health = idx.health()
        if health.get("staleFiles"):
            idx.heal_index()
            result = idx.search(query or "", industry=industry, domain=domain, include_ontology=include, limit=limit or 12)
        elif result.get("matches") == []:
            terms = result.get("validatedTerms") or []
            for term in terms:
                for iri in (term.get("iris") or [])[:2]:
                    expanded = idx.expand_graph(iri, depth=1)
                    for node in expanded.get("nodes") or []:
                        if node.get("kind") in {"class", "overlay_class"}:
                            result.setdefault("matches", []).append({**node, "score": 1, "reason": ["expand"]})
            # unique
            seen = set()
            uniq = []
            for m in result.get("matches") or []:
                if m.get("iri") in seen:
                    continue
                seen.add(m.get("iri"))
                uniq.append(m)
            result["matches"] = uniq[:limit]
    # strip hallucinated IRIs
    iris = [m.get("iri") for m in result.get("matches") or [] if m.get("iri")]
    checked = idx.validate_iris(iris)
    invalid = set(checked.get("invalid") or [])
    if invalid:
        result["matches"] = [m for m in result["matches"] if m.get("iri") not in invalid]
        result["strippedIris"] = list(invalid)
    if want_llm:
        from agents.shared.llm_plan import refine_catalog_search

        result = refine_catalog_search(
            query or "",
            result,
            industry=industry,
            domain=domain,
            includeOntology=include,
            limit=limit or 12,
        )
    return result


def validate_text(text: str = "", industry: str | None = None, domain: str | None = None, query: str | None = None) -> dict[str, Any]:
    return get_index().validate_text(text or query or "", industry=industry, domain=domain)


def get_concept(iri: str) -> dict[str, Any]:
    return get_index().get_concept(iri)


def get_ontology(domainId: str | None = None, domain_id: str | None = None, industry: str | None = None) -> dict[str, Any]:
    did = domainId or domain_id or ""
    return get_index().get_ontology(did, industry)


def expand_graph(iri: str, depth: int = 1, rels: list[str] | None = None) -> dict[str, Any]:
    return get_index().expand_graph(iri, depth=depth or 1, rels=rels)


def list_domains() -> dict[str, Any]:
    return get_index().list_domains()


def list_industries() -> dict[str, Any]:
    return get_index().list_industries()


def get_mappings_for_concept(iri: str) -> dict[str, Any]:
    return get_index().get_mappings_for_concept(iri)


def get_alignments(iri: str) -> dict[str, Any]:
    return get_index().get_alignments(iri)


def diagnose_failure(error: str = "", lastTool: str = "", lastArgs: dict | None = None, last_tool: str = "", last_args: dict | None = None) -> dict[str, Any]:
    return get_index().diagnose_failure(error, lastTool or last_tool, lastArgs or last_args or {})


def validate_iris(iris: list[str] | None = None) -> dict[str, Any]:
    return get_index().validate_iris(iris or [])


def preview_ontology(turtle: str = "") -> dict[str, Any]:
    from agents.shared.catalog_index import preview_ontology_text

    return preview_ontology_text(turtle)


def catalog_tools() -> list[ToolSpec]:
    return [
        ToolSpec(name="rebuild_index", description="Rebuild the catalog knowledge graph index", method="POST", path="/v1/index/rebuild", handler=rebuild_index),
        ToolSpec(name="index_health", description="Index health, stale files, collisions", method="GET", path="/v1/index/health", handler=index_health),
        ToolSpec(name="heal_index", description="Repair quarantined or stale index files", method="POST", path="/v1/index/heal", handler=heal_index),
        ToolSpec(name="search_catalog", description="Search ontologies, overlays, and mappings", method="POST", path="/v1/search", handler=search_catalog),
        ToolSpec(name="validate_text", description="Validate tokens in a string against the catalog", method="POST", path="/v1/validate", handler=validate_text),
        ToolSpec(name="get_concept", description="Get one catalog concept by IRI", method="GET", path="/v1/concepts", handler=get_concept),
        ToolSpec(name="get_ontology", description="Return ontology Turtle excerpt for a domain", method="GET", path="/v1/ontology/{domainId}", handler=get_ontology),
        ToolSpec(name="expand_graph", description="Expand subclass/mapping/alignment neighbors", method="POST", path="/v1/graph/expand", handler=expand_graph),
        ToolSpec(name="list_domains", description="List catalog domains from index.json", method="GET", path="/v1/domains", handler=list_domains),
        ToolSpec(name="list_industries", description="List industries from industries.json", method="GET", path="/v1/industries", handler=list_industries),
        ToolSpec(name="get_mappings_for_concept", description="Non-stub mapping triples for a concept", method="GET", path="/v1/mappings", handler=get_mappings_for_concept),
        ToolSpec(name="get_alignments", description="Core alignment or false-friend flag", method="GET", path="/v1/alignments", handler=get_alignments),
        ToolSpec(name="diagnose_failure", description="Suggest a heal tool after a failure", method="POST", path="/v1/diagnose", handler=diagnose_failure),
        ToolSpec(name="validate_iris", description="Keep only IRIs that exist in the graph", method="POST", path="/v1/iris/validate", handler=validate_iris),
        ToolSpec(
            name="preview_ontology",
            description="Parse Turtle or RDF/XML in memory for a browser session. Does not write to the catalog.",
            method="POST",
            path="/v1/ontologies/preview",
            handler=preview_ontology,
        ),
    ]
