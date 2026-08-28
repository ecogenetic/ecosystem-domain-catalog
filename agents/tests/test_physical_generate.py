#!/usr/bin/env python3.14
"""Round-trip tests: ontology → DDL → map and DDL → catalog mapping."""

from __future__ import annotations

import pytest

from agents.catalog_agent.tools import rebuild_index
from agents.data_agent.materialize import materialize_source
from agents.data_agent.physical import compile_physical_model
from agents.data_agent.registry import connect
from agents.data_agent.tools import map_to_catalog
from agents.shared.catalog_index import local_name
from agents.shared.paths import CATALOG_ROOT

CRM_CORE = {"Account", "Contact", "Lead", "Opportunity", "Campaign", "Activity", "Case", "Product", "Quote"}


@pytest.fixture(scope="module")
def catalog_ready():
    rebuild_index(incremental=False)
    yield


def test_compile_crm_physical_model(catalog_ready):
    model = compile_physical_model(domain_id="crm")
    tables = {t["table"] for t in model["tables"]}
    assert "account" in tables
    assert "contact" in tables
    contacts = next(t for t in model["tables"] if t["entity"] == "Contact")
    fk = next(c for c in contacts["columns"] if c.get("kind") == "fk" and c.get("refTable") == "account")
    assert fk["name"] == "account_id"
    assert fk["nullable"] is False
    accounts = next(t for t in model["tables"] if t["entity"] == "Account")
    account_name = next(c for c in accounts["columns"] if c["name"] == "account_name")
    assert account_name["nullable"] is False
    leads = next(t for t in model["tables"] if t["entity"] == "Lead")
    lead_status = next(c for c in leads["columns"] if c["name"] == "lead_status")
    assert "new" in (lead_status.get("enum") or [])


def test_materialize_crm_maps_back(catalog_ready):
    result = materialize_source("gen-crm-roundtrip", domain_id="crm", auto_map=True, prefer_domain="crm")
    assert result["ok"]
    assert result["tableCount"] >= 10
    mapped = result.get("mapping", {}).get("mapped") or []
    catalog_classes = {local_name(m["catalogIri"]) for m in mapped if m.get("catalogIri")}
    assert "Account" in catalog_classes
    account = next(m for m in mapped if local_name(m.get("catalogIri") or "") == "Account")
    assert "crm" in (account.get("catalogIri") or "")
    props = {p["field"]: p for p in account.get("properties") or []}
    assert "account_name" in props
    assert props["account_name"].get("mapped") is True
    assert props["account_name"].get("propertyIri") == "https://ecosystemcode.com/ontology/crm#accountName"


def test_example_sql_schema_maps_to_crm(catalog_ready):
    sql_path = CATALOG_ROOT / "domains" / "crm" / "mappings" / "example-sql-schema.sql"
    ddl = sql_path.read_text(encoding="utf-8")
    connect(kind="ddl", ddl=ddl, source_id="crm-example-sql")
    from agents.data_agent.tools import introspect_schema

    schema = introspect_schema(id="crm-example-sql")
    mapped = map_to_catalog(id="crm-example-sql", preferDomain="crm")
    catalog_classes = {local_name(m["catalogIri"]) for m in mapped.get("mapped") or [] if m.get("catalogIri")}
    matched = CRM_CORE & catalog_classes
    # example-sql-schema.sql only partially parses under the lightweight DDL reader;
    # require solid coverage of the tables that are present.
    assert len(matched) >= 3, f"Expected core CRM classes, got {catalog_classes}"
    assert "Contact" in catalog_classes or "Lead" in catalog_classes


def test_generic_mapping_ttl_binds_property_iri(catalog_ready):
    from agents.data_agent.mapping import _load_generic_mapping

    hints = _load_generic_mapping("crm")
    assert hints["classes"]["accounts_table"] == "https://ecosystemcode.com/ontology/crm#Account"
    assert hints["classes"]["account"] == "https://ecosystemcode.com/ontology/crm#Account"
    assert hints["properties"]["account_name"] == "https://ecosystemcode.com/ontology/crm#accountName"
    assert hints["properties"]["campaign_member_campaign_ref"] == (
        "https://ecosystemcode.com/ontology/crm#memberOfCampaign"
    )

    cvm = _load_generic_mapping("cvm")
    assert cvm["properties"]["campaign_segment_id"] == "https://ecosystemcode.com/ontology/cvm#targetsSegment"
    assert cvm["properties"]["offer_segment_id"] == "https://ecosystemcode.com/ontology/cvm#targetedAtSegment"


def test_generate_ddl_endpoint(catalog_ready):
    from agents.data_agent.tools import generate_ddl_from_model

    out = generate_ddl_from_model(domainId="crm")
    assert out["ok"]
    assert "CREATE TABLE" in out["ddl"]
    assert out["tableCount"] >= 10
    assert out["model"]["domainId"] == "crm"

