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
    if count < 50 or health.get("missingDomains"):
        idx.rebuild(incremental=False)
    return idx
