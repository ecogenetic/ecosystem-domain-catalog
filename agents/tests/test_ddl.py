#!/usr/bin/env python3.14
from __future__ import annotations

from agents.data_agent.ddl import parse_ddl
from agents.data_agent.registry import connect
from agents.data_agent.tools import introspect_schema, map_to_catalog
from agents.tests.fixtures_loader import SAMPLE_DDL, sample_mapping_selections


def test_parse_sample_ddl():
    tables = parse_ddl(SAMPLE_DDL)
    assert "customer" in tables
    assert "order" in tables
    assert "order_line" in tables
    customer_id = next(c for c in tables["order"]["columns"] if c["name"] == "customer_id")
    assert customer_id["ref_table"] == "customer"


def test_ddl_connect_and_map(catalog_ready):
    info = connect(kind="ddl", ddl=SAMPLE_DDL, source_id="sample-ddl")
    assert info["ok"] is True
    assert info["schemaOnly"] is True
    assert "customer" in info["collections"]
    schema = introspect_schema(id="sample-ddl")
    assert schema["schemaOnly"] is True
    customer = next(c for c in schema["collections"] if c["name"] == "customer")
    assert customer["count"] == 0
    mapped = map_to_catalog(id="sample-ddl", selections=sample_mapping_selections())
    entities = {m["entity"] for m in mapped["mapped"]}
    assert "Customer" in entities
    assert "Order" in entities
