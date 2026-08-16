#!/usr/bin/env python3.14
"""Row store abstraction: memory, MongoDB, PostgreSQL, and DDL schema-only."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _match(doc: dict[str, Any], filt: dict[str, Any] | None) -> bool:
    if not filt:
        return True
    for key, expected in filt.items():
        if key == "$and":
            if not all(_match(doc, part) for part in expected):
                return False
            continue
        if key == "$or":
            if not any(_match(doc, part) for part in expected):
                return False
            continue
        value = _dotted(doc, key)
        if isinstance(expected, dict):
            if "$gte" in expected and not _gte(value, expected["$gte"]):
                return False
            if "$lte" in expected and not _lte(value, expected["$lte"]):
                return False
            if "$gt" in expected and not _gt(value, expected["$gt"]):
                return False
            if "$in" in expected and value not in expected["$in"]:
                return False
            if "$eq" in expected and value != expected["$eq"]:
                return False
            if "$regex" in expected:
                import re

                if not re.search(str(expected["$regex"]), str(value or ""), re.I):
                    return False
        elif value != expected:
            return False
    return True


def _dotted(doc: dict[str, Any], key: str) -> Any:
    cur: Any = doc
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _coerce_dt(value: Any) -> Any:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and "T" in value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    return value


def _gte(a: Any, b: Any) -> bool:
    return _coerce_dt(a) >= _coerce_dt(b)


def _lte(a: Any, b: Any) -> bool:
    return _coerce_dt(a) <= _coerce_dt(b)


def _gt(a: Any, b: Any) -> bool:
    return _coerce_dt(a) > _coerce_dt(b)


class DocumentStore:
    kind = "memory"
    schema_only = False

    def list_collections(self) -> list[str]:
        raise NotImplementedError

    def count(self, collection: str, filt: dict[str, Any] | None = None) -> int:
        raise NotImplementedError

    def find(
        self,
        collection: str,
        filt: dict[str, Any] | None = None,
        limit: int = 50,
        projection: dict[str, int] | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError

    def distinct(self, collection: str, field: str) -> list[Any]:
        raise NotImplementedError

    def insert_many(self, collection: str, docs: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    def column_defs(self) -> dict[str, list[dict[str, Any]]] | None:
        return None


class MemoryStore(DocumentStore):
    kind = "memory"

    def __init__(self, data: dict[str, list[dict[str, Any]]] | None = None) -> None:
        self.data: dict[str, list[dict[str, Any]]] = {k: list(v) for k, v in (data or {}).items()}

    def list_collections(self) -> list[str]:
        return sorted(self.data)

    def count(self, collection: str, filt: dict[str, Any] | None = None) -> int:
        return sum(1 for d in self.data.get(collection, []) if _match(d, filt))

    def find(
        self,
        collection: str,
        filt: dict[str, Any] | None = None,
        limit: int = 50,
        projection: dict[str, int] | None = None,
    ) -> list[dict[str, Any]]:
        out = []
        for d in self.data.get(collection, []):
            if _match(d, filt):
                out.append(_project(d, projection))
            if len(out) >= limit:
                break
        return out

    def distinct(self, collection: str, field: str) -> list[Any]:
        values = []
        for d in self.data.get(collection, []):
            v = _dotted(d, field)
            if v is not None and v not in values:
                values.append(v)
        return values

    def insert_many(self, collection: str, docs: list[dict[str, Any]]) -> None:
        self.data.setdefault(collection, []).extend(docs)


class MongoStore(DocumentStore):
    kind = "mongodb"

    def __init__(self, uri: str, database: str) -> None:
        from pymongo import MongoClient

        self.client = MongoClient(uri)
        self.db = self.client[database]

    def list_collections(self) -> list[str]:
        return sorted(self.db.list_collection_names())

    def count(self, collection: str, filt: dict[str, Any] | None = None) -> int:
        return int(self.db[collection].count_documents(filt or {}))

    def find(
        self,
        collection: str,
        filt: dict[str, Any] | None = None,
        limit: int = 50,
        projection: dict[str, int] | None = None,
    ) -> list[dict[str, Any]]:
        cursor = self.db[collection].find(filt or {}, projection)
        docs = []
        for doc in cursor.limit(limit):
            doc = dict(doc)
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            docs.append(doc)
        return docs

    def distinct(self, collection: str, field: str) -> list[Any]:
        return list(self.db[collection].distinct(field))

    def insert_many(self, collection: str, docs: list[dict[str, Any]]) -> None:
        if docs:
            self.db[collection].insert_many(docs)


class PostgresStore(DocumentStore):
    kind = "postgresql"

    def __init__(self, uri: str, database: str = "") -> None:
        import psycopg
        from psycopg.rows import dict_row

        self.uri = uri
        self.database = database
        self._conn = psycopg.connect(uri, row_factory=dict_row)
        self._conn.autocommit = True

    def list_collections(self) -> list[str]:
        rows = self._conn.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
        ).fetchall()
        return [r["table_name"] for r in rows]

    def count(self, collection: str, filt: dict[str, Any] | None = None) -> int:
        if filt:
            return len(self.find(collection, filt, limit=100000))
        row = self._conn.execute(f"SELECT COUNT(*) AS c FROM {_ident(collection)}").fetchone()
        return int((row or {}).get("c") or 0)

    def find(
        self,
        collection: str,
        filt: dict[str, Any] | None = None,
        limit: int = 50,
        projection: dict[str, int] | None = None,
    ) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            f"SELECT * FROM {_ident(collection)} LIMIT %s", (int(limit),)
        ).fetchall()
        docs = [_normalize_row(dict(r)) for r in rows]
        if filt:
            docs = [d for d in docs if _match(d, filt)]
        return [_project(d, projection) for d in docs]

    def distinct(self, collection: str, field: str) -> list[Any]:
        rows = self._conn.execute(
            f"SELECT DISTINCT {_ident(field)} AS v FROM {_ident(collection)} WHERE {_ident(field)} IS NOT NULL"
        ).fetchall()
        return [r["v"] for r in rows]

    def insert_many(self, collection: str, docs: list[dict[str, Any]]) -> None:
        raise NotImplementedError("PostgreSQL insert is not used by the mapping agent")

    def column_defs(self) -> dict[str, list[dict[str, Any]]] | None:
        cols = self._conn.execute(
            """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """
        ).fetchall()
        fks = self._conn.execute(
            """
            SELECT
              kcu.table_name,
              kcu.column_name,
              ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
            """
        ).fetchall()
        fk_map = {(r["table_name"], r["column_name"]): r["foreign_table_name"] for r in fks}
        out: dict[str, list[dict[str, Any]]] = {}
        for row in cols:
            table = row["table_name"]
            out.setdefault(table, []).append(
                {
                    "name": row["column_name"],
                    "type": row["data_type"],
                    "ref_table": fk_map.get((table, row["column_name"])),
                }
            )
        return out


class DdlStore(DocumentStore):
    kind = "ddl"
    schema_only = True

    def __init__(self, ddl: str) -> None:
        from agents.data_agent.ddl import parse_ddl

        self.ddl = ddl
        self._tables = parse_ddl(ddl)

    def list_collections(self) -> list[str]:
        return sorted(self._tables)

    def count(self, collection: str, filt: dict[str, Any] | None = None) -> int:
        return 0

    def find(
        self,
        collection: str,
        filt: dict[str, Any] | None = None,
        limit: int = 50,
        projection: dict[str, int] | None = None,
    ) -> list[dict[str, Any]]:
        return []

    def distinct(self, collection: str, field: str) -> list[Any]:
        return []

    def insert_many(self, collection: str, docs: list[dict[str, Any]]) -> None:
        return None

    def column_defs(self) -> dict[str, list[dict[str, Any]]] | None:
        return {name: info["columns"] for name, info in self._tables.items()}


def _ident(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def _normalize_row(doc: dict[str, Any]) -> dict[str, Any]:
    out = dict(doc)
    if "id" in out and "_id" not in out:
        out["_id"] = str(out["id"])
    elif "_id" in out:
        out["_id"] = str(out["_id"])
    return out


def _project(doc: dict[str, Any], projection: dict[str, int] | None) -> dict[str, Any]:
    if not projection:
        return dict(doc)
    include = {k for k, v in projection.items() if v}
    if include:
        out = {k: v for k, v in doc.items() if k in include or k == "_id"}
        return out
    exclude = {k for k, v in projection.items() if not v}
    return {k: v for k, v in doc.items() if k not in exclude}


PII_EXCLUDE = {
    "password": 0,
    "passwordHash": 0,
    "hash": 0,
    "token": 0,
    "secret": 0,
    "apiKey": 0,
}
