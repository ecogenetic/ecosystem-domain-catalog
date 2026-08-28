#!/usr/bin/env python3.14
"""Materialize a PhysicalModel as a schema-only DDL source."""

from __future__ import annotations

import json
from typing import Any

from agents.data_agent import registry
from agents.data_agent.emit_mongo import generate_mongo_schema_text
from agents.data_agent.emit_sql import generate_ddl
from agents.data_agent.introspect import introspect
from agents.data_agent.physical import compile_physical_model, save_physical_model
from agents.shared.paths import source_dir


def materialize_source(
    source_id: str,
    domain_id: str | None = None,
    industry: str | None = None,
    turtle: str | None = None,
    auto_map: bool = False,
    prefer_domain: str | None = None,
) -> dict[str, Any]:
    model = compile_physical_model(domain_id=domain_id, industry=industry, turtle=turtle)
    ddl = generate_ddl(model)
    mongo_schema = generate_mongo_schema_text(model)
    dest = source_dir(source_id)
    model_path = save_physical_model(source_id, model)
    ddl_path = dest / "generated.schema.sql"
    ddl_path.write_text(ddl, encoding="utf-8")
    mongo_path = dest / "generated.mongo.schema.json"
    mongo_path.write_text(mongo_schema, encoding="utf-8")
    connect_result = registry.connect(kind="ddl", ddl=ddl, source_id=source_id)
    schema = introspect(registry.store(source_id))
    registry.set_schema(source_id, schema)
    result: dict[str, Any] = {
        "ok": True,
        "sourceId": source_id,
        "modelPath": str(model_path),
        "ddlPath": str(ddl_path),
        "mongoSchemaPath": str(mongo_path),
        "ddl": ddl,
        "tableCount": model.get("tableCount", 0),
        "collections": connect_result.get("collections") or [],
        "schemaOnly": True,
        "domainId": domain_id,
        "industryId": industry,
    }
    if auto_map:
        from agents.data_agent import mapping as mapping_mod

        pref = prefer_domain or domain_id
        mapped = mapping_mod.map_to_catalog(source_id, schema, prefer_domain=pref)
        result["mapping"] = mapped
    return result
