#!/usr/bin/env python3.14
"""L1–L5 suites through a configured LLM planner."""

from __future__ import annotations

import os

import pytest

from agents.shared.llm import DEFAULT_BASE, DEFAULT_MODEL
from agents.shared.llm_plan import llm_available
from agents.tests.runner import load_suite, run_catalog_case, run_data_case

SOURCE = "sample-llm"


@pytest.fixture(scope="session")
def live_llm():
    if not (os.environ.get("ECOSYSTEM_LLM_BASE_URL") or os.environ.get("CHAT_SERVER")):
        pytest.skip("ECOSYSTEM_LLM_BASE_URL is not set")
    if os.environ.get("ECOSYSTEM_LLM_DISABLE") == "1":
        pytest.skip("ECOSYSTEM_LLM_DISABLE=1")
    ok, detail = llm_available()
    if not ok:
        pytest.fail(f"LLM at {DEFAULT_BASE or '(unset)'} ({DEFAULT_MODEL}) unavailable: {detail}")
    return detail


@pytest.mark.llm
def test_llm_endpoint_reachable(live_llm):
    assert live_llm


@pytest.mark.llm
def test_catalog_suite_with_llm(catalog_ready, live_llm):
    suite = load_suite("catalog")
    failures = []
    for case in suite["cases"]:
        out = run_catalog_case(case, use_llm=True)
        llm = (out.get("result") or {}).get("llm") or {}
        if not llm.get("used"):
            failures.append({**out, "detail": list(out.get("detail") or []) + [f"llm not used: {llm}"]})
            continue
        if out["status"] != "pass":
            failures.append(out)
    assert not failures, failures


@pytest.mark.llm
def test_data_suite_with_llm(catalog_ready, live_llm):
    from agents.data_agent.registry import register
    from agents.data_agent.tools import generate_source_ontology, introspect_schema, map_to_catalog
    from agents.tests.fixtures_loader import memory_sample_store, sample_mapping_selections

    store = memory_sample_store()
    register(SOURCE, store, {"kind": "memory"})
    introspect_schema(id=SOURCE)
    generate_source_ontology(id=SOURCE)
    map_to_catalog(id=SOURCE, selections=sample_mapping_selections())

    suite = load_suite("data")
    failures = []
    for case in suite["cases"]:
        out = run_data_case(case, SOURCE, use_llm=True)
        llm = (out.get("result") or {}).get("llm") or {}
        if not llm.get("used"):
            failures.append({**out, "detail": list(out.get("detail") or []) + [f"llm not used: {llm}"]})
            continue
        if out["status"] != "pass":
            failures.append(out)
    assert not failures, failures
