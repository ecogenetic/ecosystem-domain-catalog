#!/usr/bin/env python3.14
from __future__ import annotations

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "llm: requires ECOSYSTEM_LLM_BASE_URL")


@pytest.fixture(scope="session")
def catalog_ready():
    from agents.shared.catalog_index import get_index

    idx = get_index()
    count = idx.connect().execute("SELECT COUNT(*) AS c FROM docs").fetchone()["c"]
    health = idx.health()
    if not idx.nx.nodes:
        idx._load_graph()
    has_object_props = any(
        (d or {}).get("edgeKind") == "objectProperty" for _, _, d in idx.nx.edges(data=True)
    )
    opp = "https://ecosystemcode.com/ontology/crm#Opportunity"
    opp_row = idx.connect().execute("SELECT extra FROM docs WHERE iri=?", (opp,)).fetchone()
    import json

    opp_extra = json.loads(opp_row["extra"] or "{}") if opp_row else {}
    has_shapes = bool(opp_extra.get("shapes") or opp_extra.get("lifecycleStates"))
    if count < 50 or health.get("missingDomains") or not has_object_props or not has_shapes:
        idx.rebuild(incremental=False)
    return idx
