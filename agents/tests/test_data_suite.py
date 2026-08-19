#!/usr/bin/env python3.14
from __future__ import annotations

from agents.data_agent.registry import register
from agents.data_agent.tools import (
    assess_complexity,
    compile_query_plan,
    execute_query_plan,
    export_rerun_suite,
    generate_source_ontology,
    introspect_schema,
    map_to_catalog,
    mapping_coverage,
    query_mapped_data,
    validate_source_ontology,
)
from agents.tests.fixtures_loader import expected_counts, memory_sample_store
from agents.tests.runner import load_suite, run_data_case

SOURCE = "sample"


def _setup(catalog_ready):
    store = memory_sample_store()
    register(SOURCE, store, {"kind": "memory"})
    introspect_schema(id=SOURCE)
    generate_source_ontology(id=SOURCE)
    mapped = map_to_catalog(id=SOURCE)
    return mapped


def test_introspect_core_collections(catalog_ready):
    _setup(catalog_ready)
    schema = introspect_schema(id=SOURCE)
    names = {c["name"] for c in schema["collections"]}
    assert "customer" in names
    assert "order" in names
    assert "order_line" in names
    assert "campaign" in names
    assert "interaction" in names
    customer = next(c for c in schema["collections"] if c["name"] == "customer")
    assert "status" in (customer.get("enumsFromLookups") or {})
    assert "gender" in (customer.get("enumsFromLookups") or {})


def test_mapping_customer_order(catalog_ready):
    mapped = _setup(catalog_ready)
    iris = {m["entity"]: m["catalogIri"] for m in mapped["mapped"]}
    assert "Customer" in iris
    assert "Order" in iris
    cov = mapping_coverage(id=SOURCE)
    assert cov["coveragePct"] >= 50


def test_generated_ontology_has_labels(catalog_ready):
    _setup(catalog_ready)
    assert validate_source_ontology(id=SOURCE)["ok"]


def test_data_suite_five_levels(catalog_ready):
    _setup(catalog_ready)
    suite = load_suite("data")
    assert [c["level"] for c in suite["cases"]] == [1, 2, 3, 4, 5]
    failures = []
    for case in suite["cases"]:
        out = run_data_case(case, SOURCE)
        if out["status"] != "pass":
            failures.append(out)
    assert not failures, failures


def test_unmapped_field_rejected(catalog_ready):
    _setup(catalog_ready)
    plan = compile_query_plan(id=SOURCE, query="how many customers do i have")
    plan["filters"] = [{"entity": "Customer", "field": "notARealField", "op": "eq", "value": "x"}]
    plan["ok"] = True
    executed = execute_query_plan(id=SOURCE, plan=plan)
    assert executed.get("ok") is False
    assert executed.get("error") == "unmapped_field"


def test_complexity_reports_five(catalog_ready):
    _setup(catalog_ready)
    report = assess_complexity(id=SOURCE)
    assert report["maxLevel"] == 5
    assert report["supportedLevels"] == [1, 2, 3, 4, 5]
    exported = export_rerun_suite(id=SOURCE, includeUnsupported=True)
    assert len(exported["cases"]) == 5


def test_expected_fixture_counts(catalog_ready):
    _setup(catalog_ready)
    counts = expected_counts()
    suite = load_suite("data")
    for case in suite["cases"]:
        result = query_mapped_data(id=SOURCE, query=case["query"])
        assert result["result"] == counts[case["level"]], (case["id"], result)
