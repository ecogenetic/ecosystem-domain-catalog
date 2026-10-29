#!/usr/bin/env python3.14
"""Tests for ontology → CRUD agent package emission and plan compile."""

from __future__ import annotations

import base64
import importlib.util
import json
import tempfile
import zipfile
from pathlib import Path

import pytest

from agents.catalog_agent.tools import rebuild_index
from agents.data_agent.emit_crud import emit_crud_package
from agents.data_agent.physical import compile_physical_model
from agents.data_agent.tools import generate_crud_agent, generate_ddl_from_model


@pytest.fixture(scope="module")
def catalog_ready():
    rebuild_index(incremental=False)
    yield


SESSION_TURTLE = """
@prefix : <https://example.com/ontology/mine#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:Customer a owl:Class ;
    skos:prefLabel "Customer" ;
    skos:definition "A buyer." .

:SalesRepRole a owl:Class ;
    skos:prefLabel "Sales Rep" ;
    skos:definition "Role bearer." .

:customerName a owl:DatatypeProperty ;
    rdfs:domain :Customer ;
    rdfs:range xsd:string ;
    skos:prefLabel "customer name" .
"""


def test_ddl_header_present(catalog_ready):
    out = generate_ddl_from_model(domainId="crm")
    assert out["ok"]
    assert out["ddl"].startswith("-- Connection: postgresql://")
    assert "CREATE TABLE" in out["ddl"]


def test_emit_postgresql_crm_package(catalog_ready):
    model = compile_physical_model(domain_id="crm")
    pkg = emit_crud_package(model, "postgresql")
    assert pkg["ok"]
    assert pkg["target"] == "postgresql"
    assert pkg["tableCount"] >= 10
    files = pkg["files"]
    assert "schema.sql" in files
    assert "app.py" in files
    assert "requirements.txt" in files
    assert "README.md" in files
    assert "psycopg" in files["requirements.txt"]
    assert "account" in files["app.py"]
    assert "run_request" in files["app.py"]
    assert "describe_model" in files["app.py"]
    assert "compile_crud_plan" in files["app.py"]
    assert "how many" not in files["app.py"].lower()
    assert "when was the last" not in files["app.py"].lower()
    assert files["schema.sql"].startswith("-- Connection:")
    raw = base64.b64decode(pkg["zipBase64"])
    assert raw[:2] == b"PK"


def test_emit_mongodb_package(catalog_ready):
    model = compile_physical_model(domain_id="crm")
    pkg = emit_crud_package(model, "mongodb")
    assert pkg["ok"]
    files = pkg["files"]
    assert "init.js" in files
    assert "mongo.schema.json" in files
    assert "pymongo" in files["requirements.txt"]
    assert "createCollection" in files["init.js"]
    assert files["init.js"].startswith("// Connection:")
    json.loads(files["mongo.schema.json"])


def test_session_turtle_one_class(catalog_ready):
    model = compile_physical_model(turtle=SESSION_TURTLE)
    entities = {t["entity"] for t in model["tables"]}
    assert "Customer" in entities
    assert "SalesRepRole" not in entities
    pkg = emit_crud_package(model, "postgresql")
    assert pkg["ok"]
    assert pkg["tableCount"] == 1
    assert "customer" in pkg["files"]["app.py"]


def test_generate_crud_agent_tool(catalog_ready):
    out = generate_crud_agent(domainId="crm", target="postgresql")
    assert out["ok"]
    assert out["zipBase64"]
    assert out["files"]["app.py"]


def test_invalid_target(catalog_ready):
    model = compile_physical_model(domain_id="crm")
    pkg = emit_crud_package(model, "mysql")
    assert pkg["ok"] is False


def _load_generated_app(app_source: str):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "app.py"
        path.write_text(app_source, encoding="utf-8")
        spec = importlib.util.spec_from_file_location("crud_generated_app", path)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        # Avoid connecting / starting uvicorn on import; only load symbols we need.
        # The module defines MODEL and compile helpers at import time without DB.
        # Skip if fastapi/psycopg missing in test env — still assert source contracts above.
        try:
            spec.loader.exec_module(mod)
        except ModuleNotFoundError as exc:
            pytest.skip(f"generated app deps missing: {exc}")
        return mod


def test_compile_count_plan_against_customer_ontology(catalog_ready):
    model = compile_physical_model(turtle=SESSION_TURTLE)
    pkg = emit_crud_package(model, "postgresql")
    mod = _load_generated_app(pkg["files"]["app.py"])
    compiled = mod.compile_crud_plan(
        {"action": "query", "class": "Customer", "aggregate": [{"fn": "count"}]}
    )
    assert compiled["ok"]
    assert "COUNT(*)" in (compiled.get("sql") or "")
    assert "customer" in (compiled.get("sql") or "")


def test_compile_rejects_unknown_class_on_crm(catalog_ready):
    model = compile_physical_model(domain_id="crm")
    pkg = emit_crud_package(model, "postgresql")
    mod = _load_generated_app(pkg["files"]["app.py"])
    compiled = mod.compile_crud_plan(
        {"action": "query", "class": "Customer", "aggregate": [{"fn": "count"}]}
    )
    assert compiled["ok"] is False
    assert compiled.get("error") == "unknown_class"
    assert "Account" in (compiled.get("classLabels") or [])


def test_compile_insert_update_delete(catalog_ready):
    model = compile_physical_model(turtle=SESSION_TURTLE)
    pkg = emit_crud_package(model, "postgresql")
    mod = _load_generated_app(pkg["files"]["app.py"])
    ins = mod.compile_crud_plan(
        {"action": "insert", "class": "Customer", "set": {"customer_name": "Acme"}}
    )
    assert ins["ok"], ins
    assert "INSERT INTO customer" in (ins.get("sql") or "")
    upd = mod.compile_crud_plan(
        {
            "action": "update",
            "class": "Customer",
            "set": {"customer_name": "Acme Ltd"},
            "where": [{"field": "customer_id", "op": "eq", "value": "a1"}],
        }
    )
    assert upd["ok"], upd
    assert "UPDATE customer" in (upd.get("sql") or "")
    dele = mod.compile_crud_plan(
        {
            "action": "delete",
            "class": "Customer",
            "where": [{"field": "customer_id", "op": "eq", "value": "a1"}],
        }
    )
    assert dele["ok"], dele
    assert "DELETE FROM customer" in (dele.get("sql") or "")


def test_describe_does_not_need_db(catalog_ready):
    model = compile_physical_model(turtle=SESSION_TURTLE)
    pkg = emit_crud_package(model, "mongodb")
    mod = _load_generated_app(pkg["files"]["app.py"])
    out = mod.compile_crud_plan({"action": "describe"})
    assert out["ok"]
    assert out.get("action") == "describe"


def test_missing_required_blocks_insert(catalog_ready):
    model = compile_physical_model(domain_id="crm")
    pkg = emit_crud_package(model, "postgresql")
    mod = _load_generated_app(pkg["files"]["app.py"])
    # Account.account_name is required by SHACL in CRM
    bad = mod.compile_crud_plan({"action": "insert", "class": "Account", "set": {}})
    assert bad["ok"] is False
    assert bad.get("error") == "missing_required"


def test_run_request_requires_llm_url(catalog_ready):
    model = compile_physical_model(turtle=SESSION_TURTLE)
    pkg = emit_crud_package(model, "postgresql")
    mod = _load_generated_app(pkg["files"]["app.py"])
    import os

    os.environ.pop("CRUD_LLM_BASE_URL", None)
    out = mod.run_request(request="anything about the mapped data")
    assert out["ok"] is False
    assert "CRUD_LLM_BASE_URL" in out.get("error", "")


def test_dropped_unknown_property(catalog_ready):
    model = compile_physical_model(turtle=SESSION_TURTLE)
    pkg = emit_crud_package(model, "postgresql")
    mod = _load_generated_app(pkg["files"]["app.py"])
    compiled = mod.compile_crud_plan(
        {
            "action": "query",
            "class": "Customer",
            "select": ["customer_name", "not_a_real_column"],
        }
    )
    assert compiled["ok"]
    assert "not_a_real_column" not in (compiled.get("sql") or "")
    assert "customer_name" in (compiled.get("sql") or "")
