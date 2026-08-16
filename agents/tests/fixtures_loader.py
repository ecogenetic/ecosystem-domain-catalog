#!/usr/bin/env python3.14
"""Generic customer/order fixture documents for tests and the in-memory sample."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from agents.data_agent.store import MemoryStore

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SAMPLE_JSON = FIXTURES_DIR / "sample.json"

SAMPLE_DDL = """
CREATE TABLE customer (
  id TEXT PRIMARY KEY,
  status TEXT,
  region TEXT
);
CREATE TABLE "order" (
  id TEXT PRIMARY KEY,
  customer_id TEXT REFERENCES customer(id),
  ordered_at TIMESTAMP,
  status TEXT
);
CREATE TABLE order_line (
  id TEXT PRIMARY KEY,
  order_id TEXT REFERENCES "order"(id),
  quantity INTEGER
);
"""


def sample_fixture() -> dict[str, list[dict[str, Any]]]:
    now = datetime.now(timezone.utc)
    recent = (now - timedelta(days=5)).isoformat()
    old = (now - timedelta(days=80)).isoformat()
    raw = json.loads(SAMPLE_JSON.read_text(encoding="utf-8"))
    return _resolve_dates(raw, recent=recent, old=old)


def _resolve_dates(value: Any, *, recent: str, old: str) -> Any:
    if isinstance(value, str):
        if value == "$recent":
            return recent
        if value == "$old":
            return old
        return value
    if isinstance(value, list):
        return [_resolve_dates(item, recent=recent, old=old) for item in value]
    if isinstance(value, dict):
        return {key: _resolve_dates(item, recent=recent, old=old) for key, item in value.items()}
    return value


def expected_counts() -> dict[int, int]:
    """L1–L5 expected counts against sample_fixture()."""
    return {
        1: 4,  # customers
        2: 2,  # active customers
        3: 2,  # orders last month
        4: 3,  # orders that have customers
        5: 2,  # orders with active customers in the last month
    }


def memory_sample_store() -> MemoryStore:
    return MemoryStore(sample_fixture())
