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
from agents.tests.fixtures_loader import (
    expected_counts,
    memory_sample_store,
    sample_mapping_selections,
)
from agents.tests.runner import load_suite, run_data_case

SOURCE = "sample"


def _setup(catalog_ready):
    store = memory_sample_store()
    register(SOURCE, store, {"kind": "memory"})
    introspect_schema(id=SOURCE)
    generate_source_ontology(id=SOURCE)
    mapped = map_to_catalog(id=SOURCE, selections=sample_mapping_selections())
    return mapped


def test_ambiguous_mapping_requires_review(catalog_ready):
    store = memory_sample_store()
    register("sample-needs-review", store, {"kind": "memory"})
    introspect_schema(id="sample-needs-review")
    generate_source_ontology(id="sample-needs-review")
    proposed = map_to_catalog(id="sample-needs-review")
    assert proposed["readiness"]["readyForQuery"] is False
    assert proposed["homonyms"]
    customer = next(item for item in proposed["homonyms"] if item["entity"] == "Customer")
    assert all(not iri.endswith("CustomerAccount") for iri in customer["candidates"])
    blocked = query_mapped_data(id="sample-needs-review", query="how many customers do i have")
    assert blocked["ok"] is False
    assert blocked["error"] in {"no_mapping", "mapping_not_ready"}


def test_invalid_catalog_selection_is_not_accepted(catalog_ready):
    store = memory_sample_store()
    source = "sample-invalid-selection"
    register(source, store, {"kind": "memory"})
    introspect_schema(id=source)
    generate_source_ontology(id=source)
    selected = sample_mapping_selections()
    selected["Customer"] = "https://ecosystemcode.com/ontology/cvm#NotAClass"
    result = map_to_catalog(id=source, selections=selected)
    invalid = next(item for item in result["unmapped"] if item["entity"] == "Customer")
    assert invalid["reason"] == "invalid_catalog_selection"
    assert result["readiness"]["readyForQuery"] is False


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


def test_unsupported_operator_rejected(catalog_ready):
    _setup(catalog_ready)
    plan = compile_query_plan(id=SOURCE, query="how many active customers")
    plan["filters"][0]["op"] = "regex"
    executed = execute_query_plan(id=SOURCE, plan=plan)
    assert executed == {"ok": False, "error": "unsupported_operator", "operator": "regex"}


def test_unknown_target_and_ambiguous_target_rejected(catalog_ready):
    _setup(catalog_ready)
    unknown = compile_query_plan(id=SOURCE, query="calculate the total")
    assert unknown["error"] == "no_target_class"
    ambiguous = compile_query_plan(id=SOURCE, query="customers and campaigns")
    assert ambiguous["error"] == "ambiguous_target_class"


def test_disconnected_entities_rejected(catalog_ready):
    from agents.data_agent.store import MemoryStore

    source = "disconnected-source"
    register(
        source,
        MemoryStore({"customer": [{"_id": "c1"}], "campaign": [{"_id": "m1"}]}),
        {"kind": "memory"},
    )
    introspect_schema(id=source)
    generate_source_ontology(id=source)
    map_to_catalog(
        id=source,
        selections={
            "Customer": sample_mapping_selections()["Customer"],
            "Campaign": sample_mapping_selections()["Campaign"],
        },
    )
    result = compile_query_plan(id=source, query="how many campaigns have customers")
    assert result["ok"] is False
    assert result["error"] == "unmapped_relationship"


def test_zero_is_a_valid_answer_and_does_not_heal(catalog_ready):
    from agents.data_agent.store import MemoryStore
    from agents.tests.fixtures_loader import sample_fixture

    source = "zero-result-source"
    data = sample_fixture()
    for customer in data["customer"]:
        customer["status"] = "inactive"
    register(source, MemoryStore(data), {"kind": "memory"})
    introspect_schema(id=source)
    generate_source_ontology(id=source)
    map_to_catalog(id=source, selections=sample_mapping_selections())
    result = query_mapped_data(id=source, query="how many active customers")
    assert result["ok"] is True
    assert result["result"] == 0
    assert "healed" not in result


def test_oversized_local_join_is_rejected(catalog_ready):
    from agents.data_agent.query import execute_query_plan as execute_direct
    from agents.data_agent.store import MemoryStore

    _setup(catalog_ready)
    plan = compile_query_plan(id=SOURCE, query="how many orders have customers")

    class OversizedStore(MemoryStore):
        def count(self, collection, filt=None):
            return 10_001

        def find(self, collection, filt=None, limit=50, projection=None):
            raise AssertionError("oversized joins must fail before rows are loaded")

    result = execute_direct(OversizedStore(), SOURCE, plan)
    assert result["ok"] is False
    assert result["error"] == "incomplete_execution"
    assert result["reason"] == "local_join_row_limit"


def test_postgres_filter_compilation_is_parameterized():
    from agents.data_agent.store import _sql_where

    where, params = _sql_where(
        {"$and": [{"status": "active"}, {"ordered_at": {"$gte": "2026-01-01"}}]}
    )
    assert where == ' WHERE ("status" = %s AND "ordered_at" >= %s)'
    assert params == ("active", "2026-01-01")

    try:
        _sql_where({"name": {"$regex": "unsafe"}})
    except ValueError as exc:
        assert "unsupported filter operator" in str(exc)
    else:
        raise AssertionError("unsupported SQL filters must be rejected")


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
