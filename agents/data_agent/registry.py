#!/usr/bin/env python3.14
"""In-process registry of connected data sources."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from agents.data_agent.store import DdlStore, DocumentStore, MemoryStore, MongoStore, PostgresStore

_SOURCES: dict[str, dict[str, Any]] = {}


def register(source_id: str, store: DocumentStore, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    _SOURCES[source_id] = {"store": store, "meta": meta or {}, "schema": None}
    return {
        "ok": True,
        "sourceId": source_id,
        "kind": getattr(store, "kind", "memory"),
        "schemaOnly": bool(getattr(store, "schema_only", False)),
        "collections": store.list_collections(),
    }


def infer_kind(kind: str | None, uri: str, ddl: str | None) -> str:
    if kind:
        return kind.strip().lower()
    if ddl and str(ddl).strip():
        return "ddl"
    scheme = (urlparse(uri or "").scheme or "").lower()
    if scheme in {"postgres", "postgresql"}:
        return "postgresql"
    if scheme in {"mongodb", "mongodb+srv"}:
        return "mongodb"
    if scheme == "memory":
        return "memory"
    raise ValueError("Provide kind (mongodb, postgresql, ddl, memory), a matching URI, or DDL text")


def connect(
    uri: str = "",
    database: str = "",
    source_id: str | None = None,
    kind: str | None = None,
    ddl: str | None = None,
) -> dict[str, Any]:
    resolved = infer_kind(kind, uri, ddl)
    store: DocumentStore
    if resolved == "ddl":
        if not (ddl or "").strip():
            raise ValueError("ddl text is required")
        sid = source_id or "ddl-source"
        store = DdlStore(ddl or "")
        return register(sid, store, {"kind": "ddl", "schemaOnly": True})
    if resolved == "memory":
        sid = source_id or database or "sample"
        if any(token in (uri or "").lower() for token in ("sample", "fixture", "demo")):
            from agents.tests.fixtures_loader import memory_sample_store

            store = memory_sample_store()
        else:
            store = MemoryStore()
        return register(sid, store, {"kind": "memory", "uri": uri, "database": database})
    if resolved == "postgresql":
        sid = source_id or database or _database_from_uri(uri) or "postgres"
        store = PostgresStore(uri, database)
        return register(sid, store, {"kind": "postgresql", "uri": uri, "database": database})
    if resolved == "mongodb":
        sid = source_id or database or _database_from_uri(uri) or "mongodb"
        store = MongoStore(uri, database or _database_from_uri(uri) or "mydb")
        return register(sid, store, {"kind": "mongodb", "uri": uri, "database": database})
    raise ValueError(f"unsupported source kind {resolved}")


def _database_from_uri(uri: str) -> str:
    path = urlparse(uri or "").path.lstrip("/")
    return path.split("/")[0] if path else ""


def get(source_id: str) -> dict[str, Any]:
    if source_id not in _SOURCES:
        raise KeyError(f"unknown source {source_id}")
    return _SOURCES[source_id]


def set_schema(source_id: str, schema: dict[str, Any]) -> None:
    get(source_id)["schema"] = schema


def store(source_id: str) -> DocumentStore:
    return get(source_id)["store"]
