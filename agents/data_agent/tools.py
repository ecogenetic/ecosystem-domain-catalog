#!/usr/bin/env python3.14
"""Data Agent MCP/OpenAPI tool handlers."""

from __future__ import annotations

from typing import Any

from agents.data_agent import complexity as complexity_mod
from agents.data_agent import mapping as mapping_mod
from agents.data_agent import ontology as ontology_mod
from agents.data_agent import query as query_mod
from agents.data_agent import registry
from agents.data_agent.introspect import introspect
from agents.data_agent.store import PII_EXCLUDE
from agents.shared.catalog_index import get_index
from agents.shared.server import ToolSpec


def connect_source(
    uri: str = "",
    database: str = "",
    sourceId: str | None = None,
    source_id: str | None = None,
    kind: str | None = None,
    ddl: str | None = None,
) -> dict[str, Any]:
    try:
        return registry.connect(uri=uri, database=database, source_id=sourceId or source_id, kind=kind, ddl=ddl)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}


def introspect_schema(id: str | None = None, sourceId: str | None = None, sampleSize: int = 20, sample_size: int | None = None) -> dict[str, Any]:
    sid = id or sourceId or ""
    schema = introspect(registry.store(sid), sample_size=sampleSize or sample_size or 20)
    registry.set_schema(sid, schema)
    return schema


def sample_records(id: str | None = None, sourceId: str | None = None, collection: str = "", limit: int = 10) -> dict[str, Any]:
    sid = id or sourceId or ""
    docs = registry.store(sid).find(collection, limit=limit or 10, projection=PII_EXCLUDE)
    return {"ok": True, "documents": docs}


def generate_source_ontology(id: str | None = None, sourceId: str | None = None) -> dict[str, Any]:
    sid = id or sourceId or ""
    schema = registry.get(sid).get("schema") or introspect_schema(id=sid)
    result = ontology_mod.generate_ontology(sid, schema)
    return result


def validate_source_ontology(id: str | None = None, sourceId: str | None = None) -> dict[str, Any]:
    sid = id or sourceId or ""
    result = ontology_mod.validate_source_ontology(sid)
    if not result.get("ok"):
        generate_source_ontology(id=sid)
        result = ontology_mod.validate_source_ontology(sid)
    return result


def map_to_catalog(
    id: str | None = None,
    sourceId: str | None = None,
    preferDomain: str | None = None,
    prefer_domain: str | None = None,
    selections: dict[str, str] | None = None,
) -> dict[str, Any]:
    sid = id or sourceId or ""
    schema = registry.get(sid).get("schema") or introspect_schema(id=sid)
    result = mapping_mod.map_to_catalog(
        sid,
        schema,
        prefer_domain=preferDomain or prefer_domain,
        selections=selections,
    )
    complexity_mod.assess_complexity(sid)
    complexity_mod.export_rerun_suite(sid, include_unsupported=True)
    return result


def mapping_coverage(id: str | None = None, sourceId: str | None = None) -> dict[str, Any]:
    return mapping_mod.mapping_coverage(id or sourceId or "")


def heal_mapping(id: str | None = None, sourceId: str | None = None, collection: str | None = None) -> dict[str, Any]:
    sid = id or sourceId or ""
    schema = registry.get(sid).get("schema") or introspect_schema(id=sid)
    return mapping_mod.heal_mapping(sid, schema, collection=collection)


def compile_query_plan(id: str | None = None, sourceId: str | None = None, query: str = "") -> dict[str, Any]:
    return query_mod.compile_query_plan(id or sourceId or "", query)


def execute_query_plan(id: str | None = None, sourceId: str | None = None, plan: dict[str, Any] | None = None) -> dict[str, Any]:
    sid = id or sourceId or ""
    return query_mod.execute_query_plan(registry.store(sid), sid, plan or {})


def assess_complexity(id: str | None = None, sourceId: str | None = None) -> dict[str, Any]:
    return complexity_mod.assess_complexity(id or sourceId or "")


def export_rerun_suite(id: str | None = None, sourceId: str | None = None, includeUnsupported: bool = True) -> dict[str, Any]:
    return complexity_mod.export_rerun_suite(id or sourceId or "", include_unsupported=includeUnsupported)


def query_mapped_data(
    id: str | None = None,
    sourceId: str | None = None,
    query: str = "",
    useLlm: bool = False,
    use_llm: bool | None = None,
) -> dict[str, Any]:
    sid = id or sourceId or ""
    store = registry.store(sid)
    result = query_mod.query_mapped_data(store, sid, query)
    if result.get("ok") and (useLlm or bool(use_llm)):
        from agents.shared.llm_plan import refine_mapped_query

        result = refine_mapped_query(sid, query, result)
    return result


def diagnose_failure(error: str = "", lastTool: str = "", lastArgs: dict | None = None) -> dict[str, Any]:
    err = (error or "").lower()
    if "mapping_not_ready" in err or "ambiguous" in err:
        return {"ok": True, "cause": "mapping_review_required", "suggestedTool": "map_to_catalog", "suggestedArgs": lastArgs or {}}
    if "relationship" in err:
        return {"ok": True, "cause": "relationship_mapping_gap", "suggestedTool": "map_to_catalog", "suggestedArgs": lastArgs or {}}
    if "operator" in err or "aggregate" in err:
        return {"ok": True, "cause": "unsupported_query_operation", "suggestedTool": None, "suggestedArgs": {}}
    if "unmapped" in err:
        return {"ok": True, "cause": "mapping_gap", "suggestedTool": "heal_mapping", "suggestedArgs": lastArgs or {}}
    if "ontology" in err:
        return {"ok": True, "cause": "ontology_gap", "suggestedTool": "generate_source_ontology", "suggestedArgs": lastArgs or {}}
    return {"ok": True, "cause": "unknown", "suggestedTool": "mapping_coverage", "suggestedArgs": lastArgs or {}}


def validate_iris(iris: list[str] | None = None) -> dict[str, Any]:
    return get_index().validate_iris(iris or [])


def data_tools() -> list[ToolSpec]:
    return [
        ToolSpec(name="connect_source", description="Connect to MongoDB, PostgreSQL, a DDL schema, or a memory store", method="POST", path="/v1/sources/connect", handler=connect_source),
        ToolSpec(name="introspect_schema", description="Introspect collections, fields, lookups enums", method="POST", path="/v1/sources/{id}/introspect", handler=introspect_schema),
        ToolSpec(name="sample_records", description="Sample documents from a collection", method="POST", path="/v1/sources/{id}/sample", handler=sample_records),
        ToolSpec(name="generate_source_ontology", description="Generate internal OWL/SKOS from the schema", method="POST", path="/v1/sources/{id}/generate-ontology", handler=generate_source_ontology),
        ToolSpec(name="validate_source_ontology", description="Require prefLabel and definition on generated classes", method="POST", path="/v1/sources/{id}/validate-ontology", handler=validate_source_ontology),
        ToolSpec(name="map_to_catalog", description="Propose source-to-catalog alignments and require explicit homonym choices", method="POST", path="/v1/sources/{id}/map", handler=map_to_catalog),
        ToolSpec(name="mapping_coverage", description="Coverage and gaps after mapping", method="GET", path="/v1/sources/{id}/coverage", handler=mapping_coverage),
        ToolSpec(name="heal_mapping", description="Repair unmapped collections via SKOS/core", method="POST", path="/v1/sources/{id}/heal-mapping", handler=heal_mapping),
        ToolSpec(name="compile_query_plan", description="Compile NL to a sandboxed query plan", method="POST", path="/v1/sources/{id}/compile", handler=compile_query_plan),
        ToolSpec(name="execute_query_plan", description="Execute a mapped query plan", method="POST", path="/v1/sources/{id}/execute", handler=execute_query_plan),
        ToolSpec(name="assess_complexity", description="Five-level complexity from the mapping graph", method="GET", path="/v1/sources/{id}/complexity", handler=assess_complexity),
        ToolSpec(name="export_rerun_suite", description="Write rerun_suite.json for this source", method="POST", path="/v1/sources/{id}/tests/export", handler=export_rerun_suite),
        ToolSpec(name="query_mapped_data", description="Natural-language query through a complete reviewed mapping", method="POST", path="/v1/sources/{id}/query", handler=query_mapped_data),
        ToolSpec(name="diagnose_failure", description="Suggest a heal tool after a failure", method="POST", path="/v1/diagnose", handler=diagnose_failure),
        ToolSpec(name="validate_iris", description="Keep only IRIs that exist in the catalog graph", method="POST", path="/v1/iris/validate", handler=validate_iris),
    ]
