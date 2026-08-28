#!/usr/bin/env python3.14
from __future__ import annotations

from agents.data_agent.complexity import assess_complexity
from agents.data_agent.registry import register
from agents.data_agent.tools import generate_source_ontology, introspect_schema, map_to_catalog
from agents.tests.fixtures_loader import memory_sample_store, sample_mapping_selections


def test_complexity_evidence_from_mapping(catalog_ready):
    store = memory_sample_store()
    register("complexity-source", store)
    introspect_schema(id="complexity-source")
    generate_source_ontology(id="complexity-source")
    map_to_catalog(id="complexity-source", selections=sample_mapping_selections())
    report = assess_complexity("complexity-source")
    evidence = report["evidence"]
    assert evidence["mappedClasses"] >= 3
    assert evidence["enumFields"]
    assert evidence["temporalFields"]
    assert evidence["maxJoinPath"] >= 2
    assert 5 in report["supportedLevels"]
