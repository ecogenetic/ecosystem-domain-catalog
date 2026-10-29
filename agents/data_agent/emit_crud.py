#!/usr/bin/env python3.14
"""Emit a downloadable Python 3.14 CRUD agent package from a physical model."""

from __future__ import annotations

import base64
import io
import json
import zipfile
from typing import Any

from agents.data_agent.emit_mongo import generate_mongo_schema, generate_mongo_schema_text
from agents.data_agent.emit_sql import generate_ddl

PG_HEADER = """\
-- Connection: postgresql://user:pass@localhost:5432/mydb
-- Create the database, then apply this file:
--   createdb mydb
--   psql "postgresql://user:pass@localhost:5432/mydb" -f schema.sql
-- LLM (required for conversation /run_request):
--   export CRUD_LLM_BASE_URL=https://api.openai.com/v1
--   export CRUD_LLM_API_KEY=sk-...
--   export CRUD_LLM_MODEL=gpt-4o-mini
"""

MONGO_HEADER = """\
// Connection: mongodb://localhost:27017
// Database: mydb
// Create the database and collections (validators are in this file):
//   mongosh "mongodb://localhost:27017/mydb" init.js
// LLM (required for conversation /run_request):
//   export CRUD_LLM_BASE_URL=https://api.openai.com/v1
//   export CRUD_LLM_API_KEY=sk-...
//   export CRUD_LLM_MODEL=gpt-4o-mini
"""


def ddl_with_header(model: dict[str, Any]) -> str:
    body = generate_ddl(model)
    if body.lstrip().startswith("-- Connection:"):
        return body
    return f"{PG_HEADER}\n{body}"


def mongo_init_js(model: dict[str, Any]) -> str:
    schema = generate_mongo_schema(model)
    lines = [MONGO_HEADER.rstrip(), ""]
    for name, coll_schema in (schema.get("collections") or {}).items():
        validator = json.dumps({"$jsonSchema": coll_schema}, indent=2)
        lines.append(f'db.createCollection("{name}", {{ validator: {validator} }});')
        lines.append("")
    return "\n".join(lines)


def emit_crud_package(model: dict[str, Any], target: str) -> dict[str, Any]:
    target = (target or "").strip().lower()
    if target not in {"postgresql", "mongodb"}:
        return {"ok": False, "error": "target must be postgresql or mongodb"}
    tables = model.get("tables") or []
    if not tables:
        return {"ok": False, "error": "physical model has no tables"}

    header = PG_HEADER if target == "postgresql" else MONGO_HEADER
    files: dict[str, str] = {}
    if target == "postgresql":
        files["schema.sql"] = ddl_with_header(model)
        files["requirements.txt"] = "fastapi\nuvicorn\nhttpx\npsycopg[binary]\n"
    else:
        files["init.js"] = mongo_init_js(model)
        files["mongo.schema.json"] = generate_mongo_schema_text(model)
        files["requirements.txt"] = "fastapi\nuvicorn\nhttpx\npymongo\n"
    files["app.py"] = _render_app(model, target)
    files["README.md"] = _render_readme(model, target, header)
    zip_b64 = _zip_base64(files)
    first = tables[0]["table"]
    return {
        "ok": True,
        "target": target,
        "tableCount": model.get("tableCount") or len(tables),
        "header": header,
        "files": files,
        "zipBase64": zip_b64,
        "firstTable": first,
        "model": model,
    }


def _zip_base64(files: dict[str, str]) -> str:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, text in files.items():
            zf.writestr(path, text)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _model_json(model: dict[str, Any]) -> str:
    slim = {
        "tables": model.get("tables") or [],
        "tableCount": model.get("tableCount") or len(model.get("tables") or []),
        "domainId": model.get("domainId"),
        "industry": model.get("industry"),
    }
    return json.dumps(slim, indent=2)


def _render_readme(model: dict[str, Any], target: str, header: str) -> str:
    tables = model.get("tables") or []
    first = tables[0]["table"] if tables else "account"
    pk = next((c["name"] for c in (tables[0].get("columns") or []) if c.get("primaryKey")), f"{first}_id") if tables else "id"
    sample_col = next(
        (c["name"] for c in (tables[0].get("columns") or []) if not c.get("primaryKey")),
        "name",
    ) if tables else "name"
    if target == "postgresql":
        env_block = "export DATABASE_URL=postgresql://user:pass@localhost:5432/mydb"
        init_block = "psql \"$DATABASE_URL\" -f schema.sql\n# or: python3.14 app.py --init"
        mcp_env = '"DATABASE_URL": "postgresql://user:pass@localhost:5432/mydb"'
    else:
        env_block = "export MONGO_URI=mongodb://localhost:27017\nexport MONGO_DB=mydb"
        init_block = 'mongosh "mongodb://localhost:27017/mydb" init.js\n# or: python3.14 app.py --init'
        mcp_env = '"MONGO_URI": "mongodb://localhost:27017", "MONGO_DB": "mydb"'
    return f"""# Ontology CRUD agent ({target})

Generated from an OWL/SHACL physical model. The package contains no sample questions.
Conversation requests go through `run_request` / `POST /requests` and are compiled against
the ontology mapping baked into `app.py`.

## Connection and create commands

```
{header.strip()}
```

## Install and start

```bash
python3.14 -m venv .venv && . .venv/bin/activate
python3.14 -m pip install -r requirements.txt
{env_block}
export CRUD_LLM_BASE_URL=https://api.openai.com/v1
export CRUD_LLM_API_KEY=sk-...
export CRUD_LLM_MODEL=gpt-4o-mini
{init_block}
python3.14 -m uvicorn app:app --port 8090
```

OpenAPI: http://127.0.0.1:8090/docs

## Conversation (query, create, update, delete)

```bash
curl -X POST http://127.0.0.1:8090/requests \\
  -H 'Content-Type: application/json' \\
  -d '{{"request":"your sentence about the data"}}'
```

MCP tool `run_request` takes the same `{{"request":"..."}}` body. Direct row routes remain for a known key.

## Direct HTTP (table `{first}`)

```bash
curl -X POST http://127.0.0.1:8090/{first} -H 'Content-Type: application/json' -d '{{"{pk}":"a1","{sample_col}":"Acme"}}'
curl http://127.0.0.1:8090/{first}/a1
curl http://127.0.0.1:8090/{first}
curl -X POST http://127.0.0.1:8090/{first}/a1 -H 'Content-Type: application/json' -d '{{"{sample_col}":"Acme Ltd"}}'
curl -X POST http://127.0.0.1:8090/{first}/a1/delete
```

## MCP stdio (Cursor)

```json
{{
  "mcpServers": {{
    "crud-agent": {{
      "command": "python3.14",
      "args": ["app.py", "--stdio"],
      "env": {{ {mcp_env}, "CRUD_LLM_BASE_URL": "...", "CRUD_LLM_API_KEY": "...", "CRUD_LLM_MODEL": "..." }}
    }}
  }}
}}
```
"""


def _render_app(model: dict[str, Any], target: str) -> str:
    model_json = _model_json(model)
    is_pg = target == "postgresql"
    header_comment = PG_HEADER if is_pg else MONGO_HEADER
    driver_import = "import psycopg" if is_pg else "from pymongo import MongoClient"
    return f'''#!/usr/bin/env python3.14
"""Ontology CRUD agent — generated package. Do not edit MODEL by hand."""
{chr(10).join("# " + line if line else "#" for line in header_comment.strip().splitlines())}

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
{driver_import}

MODEL: dict[str, Any] = json.loads(r"""{model_json}""")
TARGET = "{target}"

app = FastAPI(title="Ontology CRUD agent", version="1.0.0")


def _tables() -> list[dict[str, Any]]:
    return list(MODEL.get("tables") or [])


def _table_by_name(name: str) -> dict[str, Any] | None:
    for tbl in _tables():
        if tbl.get("table") == name or tbl.get("entity") == name:
            return tbl
    return None


def _table_by_entity(entity: str) -> dict[str, Any] | None:
    low = (entity or "").lower()
    for tbl in _tables():
        if tbl.get("entity") == entity or tbl.get("table") == low or (tbl.get("entity") or "").lower() == low:
            return tbl
    return None


def _pk(tbl: dict[str, Any]) -> str:
    for col in tbl.get("columns") or []:
        if col.get("primaryKey"):
            return col["name"]
    return f"{{tbl['table']}}_id"


def _col_names(tbl: dict[str, Any]) -> set[str]:
    return {{c["name"] for c in tbl.get("columns") or []}}


def _required(tbl: dict[str, Any]) -> list[str]:
    return [c["name"] for c in tbl.get("columns") or [] if not c.get("nullable", True) and not c.get("primaryKey")]


def _enums(tbl: dict[str, Any]) -> dict[str, list[Any]]:
    out: dict[str, list[Any]] = {{}}
    for col in tbl.get("columns") or []:
        if col.get("enum"):
            out[col["name"]] = list(col["enum"])
    return out


def _ontology_listing() -> dict[str, Any]:
    classes = []
    for tbl in _tables():
        cols = []
        for col in tbl.get("columns") or []:
            cols.append(
                {{
                    "name": col["name"],
                    "kind": col.get("kind"),
                    "sqlType": col.get("sqlType"),
                    "bsonType": col.get("bsonType"),
                    "nullable": col.get("nullable", True),
                    "primaryKey": bool(col.get("primaryKey")),
                    "enum": col.get("enum"),
                    "refTable": col.get("refTable"),
                    "refEntity": col.get("refEntity"),
                    "propertyIri": col.get("propertyIri"),
                }}
            )
        classes.append(
            {{
                "entity": tbl.get("entity"),
                "table": tbl.get("table"),
                "classIri": tbl.get("classIri"),
                "columns": cols,
            }}
        )
    return {{"classes": classes, "target": TARGET}}


# --- storage ---

def _pg_conn():
    url = os.environ.get("DATABASE_URL") or "postgresql://user:pass@localhost:5432/mydb"
    return psycopg.connect(url)


def _mongo_db():
    uri = os.environ.get("MONGO_URI") or "mongodb://localhost:27017"
    name = os.environ.get("MONGO_DB") or "mydb"
    return MongoClient(uri)[name]


def init_schema() -> None:
    if TARGET == "postgresql":
        path = os.path.join(os.path.dirname(__file__) or ".", "schema.sql")
        sql = open(path, encoding="utf-8").read()
        statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                for stmt in statements:
                    # skip pure comment blocks
                    body = "\\n".join(line for line in stmt.splitlines() if not line.strip().startswith("--"))
                    if body.strip():
                        cur.execute(body)
            conn.commit()
    else:
        path = os.path.join(os.path.dirname(__file__) or ".", "mongo.schema.json")
        data = json.loads(open(path, encoding="utf-8").read())
        db = _mongo_db()
        for name, schema in (data.get("collections") or {{}}).items():
            if name not in db.list_collection_names():
                db.create_collection(name, validator={{"$jsonSchema": schema}})
            else:
                db.command("collMod", name, validator={{"$jsonSchema": schema}})


def list_rows(table: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    tbl = _table_by_name(table)
    if not tbl:
        raise HTTPException(404, "unknown table")
    allowed = _col_names(tbl)
    filt = {{k: v for k, v in (filters or {{}}).items() if k in allowed}}
    if TARGET == "postgresql":
        where = ""
        vals: list[Any] = []
        if filt:
            parts = []
            for k, v in filt.items():
                parts.append(f"{{k}} = %s")
                vals.append(v)
            where = " WHERE " + " AND ".join(parts)
        cols = ", ".join(sorted(allowed))
        q = f"SELECT {{cols}} FROM {{tbl['table']}}{{where}}"
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(q, vals)
                names = [d.name for d in cur.description]
                return [dict(zip(names, row)) for row in cur.fetchall()]
    db = _mongo_db()
    docs = list(db[tbl["table"]].find(filt or {{}}, {{"_id": 0}}))
    return docs


def get_row(table: str, row_id: str) -> dict[str, Any]:
    tbl = _table_by_name(table)
    if not tbl:
        raise HTTPException(404, "unknown table")
    pk = _pk(tbl)
    if TARGET == "postgresql":
        cols = ", ".join(sorted(_col_names(tbl)))
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT {{cols}} FROM {{tbl['table']}} WHERE {{pk}} = %s", (row_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, "not found")
                names = [d.name for d in cur.description]
                return dict(zip(names, row))
    doc = _mongo_db()[tbl["table"]].find_one({{"_id": row_id}}, {{"_id": 0}})
    if not doc:
        # also try pk field
        doc = _mongo_db()[tbl["table"]].find_one({{pk: row_id}}, {{"_id": 0}})
    if not doc:
        raise HTTPException(404, "not found")
    return doc


def create_row(table: str, body: dict[str, Any]) -> dict[str, Any]:
    tbl = _table_by_name(table)
    if not tbl:
        raise HTTPException(404, "unknown table")
    allowed = _col_names(tbl)
    pk = _pk(tbl)
    data = {{k: v for k, v in body.items() if k in allowed}}
    if pk not in data or not data[pk]:
        data[pk] = str(uuid.uuid4())
    for req in _required(tbl):
        if req not in data or data[req] in (None, ""):
            raise HTTPException(400, f"missing required field: {{req}}")
    for col, vals in _enums(tbl).items():
        if col in data and data[col] not in vals:
            raise HTTPException(400, f"invalid enum for {{col}}")
    if TARGET == "postgresql":
        cols = list(data.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        col_sql = ", ".join(cols)
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {{tbl['table']}} ({{col_sql}}) VALUES ({{placeholders}})",
                    [data[c] for c in cols],
                )
            conn.commit()
        return data
    doc = dict(data)
    doc["_id"] = data[pk]
    _mongo_db()[tbl["table"]].insert_one(doc)
    doc.pop("_id", None)
    return data


def update_row(table: str, row_id: str, body: dict[str, Any]) -> dict[str, Any]:
    tbl = _table_by_name(table)
    if not tbl:
        raise HTTPException(404, "unknown table")
    allowed = _col_names(tbl)
    pk = _pk(tbl)
    data = {{k: v for k, v in body.items() if k in allowed and k != pk}}
    for col, vals in _enums(tbl).items():
        if col in data and data[col] not in vals:
            raise HTTPException(400, f"invalid enum for {{col}}")
    if not data:
        raise HTTPException(400, "no updatable fields")
    if TARGET == "postgresql":
        sets = ", ".join(f"{{k}} = %s" for k in data)
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {{tbl['table']}} SET {{sets}} WHERE {{pk}} = %s",
                    list(data.values()) + [row_id],
                )
                if cur.rowcount == 0:
                    raise HTTPException(404, "not found")
            conn.commit()
        return get_row(table, row_id)
    result = _mongo_db()[tbl["table"]].update_one({{"_id": row_id}}, {{"$set": data}})
    if result.matched_count == 0:
        result = _mongo_db()[tbl["table"]].update_one({{pk: row_id}}, {{"$set": data}})
    if result.matched_count == 0:
        raise HTTPException(404, "not found")
    return get_row(table, row_id)


def delete_row(table: str, row_id: str) -> dict[str, Any]:
    tbl = _table_by_name(table)
    if not tbl:
        raise HTTPException(404, "unknown table")
    pk = _pk(tbl)
    if TARGET == "postgresql":
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {{tbl['table']}} WHERE {{pk}} = %s", (row_id,))
                if cur.rowcount == 0:
                    raise HTTPException(404, "not found")
            conn.commit()
        return {{"ok": True, "deleted": row_id}}
    result = _mongo_db()[tbl["table"]].delete_one({{"_id": row_id}})
    if result.deleted_count == 0:
        result = _mongo_db()[tbl["table"]].delete_one({{pk: row_id}})
    if result.deleted_count == 0:
        raise HTTPException(404, "not found")
    return {{"ok": True, "deleted": row_id}}


# --- plan compile / execute (no question strings in this module) ---

def describe_model() -> dict[str, Any]:
    return {{"ok": True, **_ontology_listing()}}


def _check_plan(plan: dict[str, Any]) -> dict[str, Any]:
    action = plan.get("action")
    if action not in {{"query", "insert", "update", "delete", "describe"}}:
        return {{"ok": False, "error": "invalid_action", "actions": ["query", "insert", "update", "delete", "describe"]}}
    if action == "describe":
        return {{"ok": True, "action": "describe", "plan": plan}}
    cls = plan.get("class") or plan.get("table") or ""
    tbl = _table_by_entity(str(cls))
    if not tbl:
        return {{
            "ok": False,
            "error": "unknown_class",
            "classLabels": [t.get("entity") for t in _tables()],
        }}
    allowed = _col_names(tbl)
    cleaned: dict[str, Any] = {{"action": action, "class": tbl["entity"], "table": tbl["table"]}}
    if plan.get("select"):
        cleaned["select"] = [c for c in plan["select"] if c in allowed]
    where = []
    for w in plan.get("where") or []:
        field = w.get("field")
        op = w.get("op") or "eq"
        if field not in allowed or op not in {{"eq", "gt", "gte", "lt", "lte", "in"}}:
            continue
        enums = _enums(tbl).get(field)
        val = w.get("value")
        if enums is not None and op == "eq" and val not in enums:
            return {{"ok": False, "error": "invalid_enum", "field": field, "allowed": enums}}
        where.append({{"field": field, "op": op, "value": val}})
    if where:
        cleaned["where"] = where
    aggregates = []
    for agg in plan.get("aggregate") or []:
        fn = (agg.get("fn") or "").lower()
        prop = agg.get("property") or agg.get("field")
        if fn == "count":
            aggregates.append({{"fn": "count"}})
        elif fn in {{"min", "max", "sum", "avg"}} and prop in allowed:
            col = next(c for c in tbl["columns"] if c["name"] == prop)
            sql_t = (col.get("sqlType") or "").upper()
            if fn in {{"min", "max"}} and sql_t not in {{"INTEGER", "NUMERIC", "TIMESTAMPTZ", "DATE", "INT", "DECIMAL"}} and col.get("bsonType") not in {{"int", "decimal", "date"}}:
                continue
            aggregates.append({{"fn": fn, "property": prop}})
    if aggregates:
        cleaned["aggregate"] = aggregates
    joins = []
    for j in plan.get("joins") or []:
        field = j.get("field") or j.get("on")
        if field in allowed:
            col = next(c for c in tbl["columns"] if c["name"] == field)
            if col.get("kind") == "fk":
                joins.append({{"field": field, "refTable": col.get("refTable"), "refEntity": col.get("refEntity")}})
    if joins:
        cleaned["joins"] = joins
    if plan.get("orderBy"):
        ob = plan["orderBy"]
        field = ob.get("field") if isinstance(ob, dict) else None
        if field in allowed:
            cleaned["orderBy"] = {{"field": field, "dir": "desc" if str(ob.get("dir", "")).lower() == "desc" else "asc"}}
    if plan.get("limit") is not None:
        try:
            cleaned["limit"] = max(1, min(int(plan["limit"]), 1000))
        except (TypeError, ValueError):
            pass
    if action in {{"insert", "update"}}:
        raw_set = plan.get("set") or {{}}
        cleaned_set = {{k: v for k, v in raw_set.items() if k in allowed}}
        for col, vals in _enums(tbl).items():
            if col in cleaned_set and cleaned_set[col] not in vals:
                return {{"ok": False, "error": "invalid_enum", "field": col, "allowed": vals}}
        if action == "insert":
            for req in _required(tbl):
                if req not in cleaned_set:
                    return {{"ok": False, "error": "missing_required", "field": req}}
        cleaned["set"] = cleaned_set
    return {{"ok": True, "plan": cleaned, "table": tbl}}


def compile_crud_plan(plan: dict[str, Any] | None = None) -> dict[str, Any]:
    checked = _check_plan(plan or {{}})
    if not checked.get("ok"):
        return checked
    if checked.get("action") == "describe" or checked["plan"].get("action") == "describe":
        return {{"ok": True, "action": "describe", "result": describe_model(), "sql": None, "pipeline": None}}
    p = checked["plan"]
    tbl = checked["table"]
    action = p["action"]
    if TARGET == "postgresql":
        sql, params = _compile_sql(p, tbl)
        return {{"ok": True, "plan": p, "sql": sql, "params": params, "pipeline": None, "table": tbl["table"], "class": tbl["entity"]}}
    pipeline, write = _compile_mongo(p, tbl)
    return {{"ok": True, "plan": p, "sql": None, "pipeline": pipeline, "write": write, "table": tbl["table"], "class": tbl["entity"]}}


def _compile_sql(plan: dict[str, Any], tbl: dict[str, Any]) -> tuple[str, list[Any]]:
    table = tbl["table"]
    action = plan["action"]
    params: list[Any] = []
    if action == "query":
        if plan.get("aggregate"):
            parts = []
            for agg in plan["aggregate"]:
                if agg["fn"] == "count":
                    parts.append("COUNT(*) AS n")
                else:
                    parts.append(f"{{agg['fn'].upper()}}({{agg['property']}}) AS {{agg['fn']}}_{{agg['property']}}")
            select = ", ".join(parts)
        else:
            cols = plan.get("select") or sorted(_col_names(tbl))
            select = ", ".join(f"{{table}}.{{c}}" for c in cols)
        joins_sql = ""
        for j in plan.get("joins") or []:
            ref = j.get("refTable")
            if not ref:
                continue
            ref_tbl = _table_by_name(ref)
            ref_pk = _pk(ref_tbl) if ref_tbl else f"{{ref}}_id"
            joins_sql += f" JOIN {{ref}} ON {{table}}.{{j['field']}} = {{ref}}.{{ref_pk}}"
        where_sql, where_params = _sql_where(plan.get("where") or [], table)
        params.extend(where_params)
        order = ""
        if plan.get("orderBy"):
            order = f" ORDER BY {{plan['orderBy']['field']}} {{plan['orderBy']['dir'].upper()}}"
        limit = f" LIMIT {{plan['limit']}}" if plan.get("limit") else ""
        return f"SELECT {{select}} FROM {{table}}{{joins_sql}}{{where_sql}}{{order}}{{limit}}", params
    if action == "insert":
        data = dict(plan.get("set") or {{}})
        pk = _pk(tbl)
        if pk not in data:
            data[pk] = str(uuid.uuid4())
        cols = list(data.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        params.extend(data[c] for c in cols)
        return f"INSERT INTO {{table}} ({{', '.join(cols)}}) VALUES ({{placeholders}}) RETURNING *", params
    if action == "update":
        data = plan.get("set") or {{}}
        sets = ", ".join(f"{{k}} = %s" for k in data)
        params.extend(data.values())
        where_sql, where_params = _sql_where(plan.get("where") or [], table)
        if not where_sql:
            return "", []
        params.extend(where_params)
        return f"UPDATE {{table}} SET {{sets}}{{where_sql}} RETURNING *", params
    where_sql, where_params = _sql_where(plan.get("where") or [], table)
    if not where_sql:
        return "", []
    params.extend(where_params)
    return f"DELETE FROM {{table}}{{where_sql}} RETURNING *", params


def _sql_where(where: list[dict[str, Any]], table: str) -> tuple[str, list[Any]]:
    if not where:
        return "", []
    parts = []
    params: list[Any] = []
    for w in where:
        field = w["field"]
        op = w["op"]
        val = w["value"]
        if op == "eq":
            parts.append(f"{{table}}.{{field}} = %s")
            params.append(val)
        elif op == "gt":
            parts.append(f"{{table}}.{{field}} > %s")
            params.append(val)
        elif op == "gte":
            parts.append(f"{{table}}.{{field}} >= %s")
            params.append(val)
        elif op == "lt":
            parts.append(f"{{table}}.{{field}} < %s")
            params.append(val)
        elif op == "lte":
            parts.append(f"{{table}}.{{field}} <= %s")
            params.append(val)
        elif op == "in":
            vals = list(val) if isinstance(val, list) else [val]
            parts.append(f"{{table}}.{{field}} IN ({{', '.join(['%s'] * len(vals))}})")
            params.extend(vals)
    return " WHERE " + " AND ".join(parts), params


def _compile_mongo(plan: dict[str, Any], tbl: dict[str, Any]) -> tuple[list[dict[str, Any]] | None, dict[str, Any] | None]:
    action = plan["action"]
    if action == "query":
        pipeline: list[dict[str, Any]] = []
        match: dict[str, Any] = {{}}
        for w in plan.get("where") or []:
            field = w["field"]
            op = w["op"]
            val = w["value"]
            if op == "eq":
                match[field] = val
            elif op == "gt":
                match[field] = {{"$gt": val}}
            elif op == "gte":
                match[field] = {{"$gte": val}}
            elif op == "lt":
                match[field] = {{"$lt": val}}
            elif op == "lte":
                match[field] = {{"$lte": val}}
            elif op == "in":
                match[field] = {{"$in": list(val) if isinstance(val, list) else [val]}}
        if match:
            pipeline.append({{"$match": match}})
        for j in plan.get("joins") or []:
            ref = j.get("refTable")
            if ref:
                pipeline.append(
                    {{
                        "$lookup": {{
                            "from": ref,
                            "localField": j["field"],
                            "foreignField": "_id",
                            "as": ref,
                        }}
                    }}
                )
        if plan.get("aggregate"):
            group: dict[str, Any] = {{"_id": None}}
            for agg in plan["aggregate"]:
                if agg["fn"] == "count":
                    group["n"] = {{"$sum": 1}}
                else:
                    group[f"{{agg['fn']}}_{{agg['property']}}"] = {{f"${{agg['fn']}}": f"${{agg['property']}}"}}
            pipeline.append({{"$group": group}})
        if plan.get("orderBy"):
            pipeline.append({{"$sort": {{plan["orderBy"]["field"]: -1 if plan["orderBy"]["dir"] == "desc" else 1}}}})
        if plan.get("limit"):
            pipeline.append({{"$limit": plan["limit"]}})
        return pipeline, None
    if action == "insert":
        data = dict(plan.get("set") or {{}})
        pk = _pk(tbl)
        if pk not in data:
            data[pk] = str(uuid.uuid4())
        data["_id"] = data[pk]
        return None, {{"op": "insert", "document": data}}
    if action == "update":
        filt = _mongo_filter(plan.get("where") or [])
        return None, {{"op": "update", "filter": filt, "set": plan.get("set") or {{}}}}
    filt = _mongo_filter(plan.get("where") or [])
    return None, {{"op": "delete", "filter": filt}}


def _mongo_filter(where: list[dict[str, Any]]) -> dict[str, Any]:
    match: dict[str, Any] = {{}}
    for w in where:
        field = w["field"]
        op = w["op"]
        val = w["value"]
        if op == "eq":
            match[field] = val
        elif op == "gt":
            match[field] = {{"$gt": val}}
        elif op == "gte":
            match[field] = {{"$gte": val}}
        elif op == "lt":
            match[field] = {{"$lt": val}}
        elif op == "lte":
            match[field] = {{"$lte": val}}
        elif op == "in":
            match[field] = {{"$in": list(val) if isinstance(val, list) else [val]}}
    return match


def execute_crud_plan(compiled: dict[str, Any] | None = None) -> dict[str, Any]:
    compiled = compiled or {{}}
    if not compiled.get("ok"):
        return compiled
    if compiled.get("action") == "describe":
        return compiled
    if TARGET == "postgresql":
        sql = compiled.get("sql") or ""
        if not sql:
            return {{"ok": False, "error": "empty_sql"}}
        params = compiled.get("params") or []
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                if cur.description:
                    names = [d.name for d in cur.description]
                    rows = [dict(zip(names, row)) for row in cur.fetchall()]
                else:
                    rows = []
                    rows = [{{"rowcount": cur.rowcount}}]
            conn.commit()
        return {{"ok": True, "plan": compiled.get("plan"), "sql": sql, "result": rows, "class": compiled.get("class"), "table": compiled.get("table")}}
    write = compiled.get("write")
    pipeline = compiled.get("pipeline")
    table = compiled.get("table")
    coll = _mongo_db()[table]
    if write:
        op = write.get("op")
        if op == "insert":
            doc = write["document"]
            coll.insert_one(doc)
            out = dict(doc)
            out.pop("_id", None)
            return {{"ok": True, "plan": compiled.get("plan"), "write": write, "result": out, "class": compiled.get("class"), "table": table}}
        if op == "update":
            filt = write.get("filter") or {{}}
            if not filt:
                return {{"ok": False, "error": "update_requires_where"}}
            result = coll.update_many(filt, {{"$set": write.get("set") or {{}}}})
            return {{"ok": True, "plan": compiled.get("plan"), "write": write, "result": {{"matched": result.matched_count, "modified": result.modified_count}}, "class": compiled.get("class"), "table": table}}
        filt = write.get("filter") or {{}}
        if not filt:
            return {{"ok": False, "error": "delete_requires_where"}}
        result = coll.delete_many(filt)
        return {{"ok": True, "plan": compiled.get("plan"), "write": write, "result": {{"deleted": result.deleted_count}}, "class": compiled.get("class"), "table": table}}
    rows = list(coll.aggregate(pipeline or []))
    for row in rows:
        if "_id" in row and row["_id"] is None:
            row.pop("_id", None)
        elif "_id" in row:
            row["_id"] = str(row["_id"])
    return {{"ok": True, "plan": compiled.get("plan"), "pipeline": pipeline, "result": rows, "class": compiled.get("class"), "table": table}}


# --- LLM agent loop ---

PLANNER_SYSTEM = """You compile a user data request into a JSON plan against the ontology listing.
Return ONLY JSON with one of:
{{"action":"tool_call","tool":"compile_crud_plan","arguments":{{"plan":{{...}}}}}}
{{"action":"tool_call","tool":"execute_crud_plan","arguments":{{"compiled":{{...}}}}}}
{{"action":"final","response":{{...}}}}
Plan fields: action (query|insert|update|delete|describe), class, select, aggregate (fn count|min|max|sum|avg, property), where (field, op eq|gt|gte|lt|lte|in, value), orderBy, limit, joins (field), set.
Use only class and property names from the ontology listing. Never invent SQL or pipeline text.
After compile_crud_plan succeeds, call execute_crud_plan with that compiled object, then return action=final with the execute result.
"""


class LlmClient:
    def __init__(self) -> None:
        self.base_url = (os.environ.get("CRUD_LLM_BASE_URL") or "").rstrip("/")
        self.model = os.environ.get("CRUD_LLM_MODEL") or ""
        self.api_key = os.environ.get("CRUD_LLM_API_KEY") or ""

    def enabled(self) -> bool:
        return bool(self.base_url)

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        headers = {{"Content-Type": "application/json"}}
        if self.api_key:
            key = self.api_key.strip()
            headers["Authorization"] = key if key.lower().startswith(("bearer ", "basic ")) else f"Bearer {{key}}"
        payload = {{"model": self.model, "messages": messages, "stream": False, "temperature": temperature}}
        with httpx.Client(timeout=90.0) as client:
            r = client.post(f"{{self.base_url}}/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
        return data["choices"][0]["message"]["content"]


def _parse_json(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{{")
        end = text.rfind("}}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


def run_request(request: str = "", sentence: str = "") -> dict[str, Any]:
    text = request or sentence or ""
    client = LlmClient()
    if not client.enabled():
        return {{"ok": False, "error": "CRUD_LLM_BASE_URL is required for run_request"}}
    tools = {{
        "compile_crud_plan": lambda **kw: compile_crud_plan(kw.get("plan")),
        "execute_crud_plan": lambda **kw: execute_crud_plan(kw.get("compiled")),
        "describe_model": lambda **kw: describe_model(),
    }}
    ontology = _ontology_listing()
    context: dict[str, Any] = {{"ontology": ontology, "last": None}}
    trace: list[dict[str, Any]] = []
    for _ in range(6):
        raw = client.chat(
            [
                {{"role": "system", "content": PLANNER_SYSTEM + "\\nTools: " + ", ".join(sorted(tools))}},
                {{
                    "role": "user",
                    "content": json.dumps({{"request": text, "ontology": ontology, "context": context.get("last"), "trace": trace[-3:]}}, default=str),
                }},
            ]
        )
        decision = _parse_json(raw)
        action = decision.get("action")
        if action == "final":
            response = decision.get("response") or decision
            if isinstance(response, dict):
                response.setdefault("trace", trace)
                return response
            return {{"ok": True, "result": response, "trace": trace}}
        tool_name = str(decision.get("tool") or "")
        args = decision.get("arguments") or {{}}
        if tool_name not in tools:
            return {{"ok": False, "error": "unknown_tool", "tool": tool_name, "trace": trace}}
        result = tools[tool_name](**args) if args else tools[tool_name]()
        trace.append({{"tool": tool_name, "args": args, "result": result}})
        context["last"] = result
        if tool_name == "execute_crud_plan" and result.get("ok"):
            return {{**result, "trace": trace}}
    return {{"ok": False, "error": "agent_loop_exhausted", "trace": trace, "last": context.get("last")}}


# --- HTTP routes ---

@app.get("/health")
def health() -> dict[str, Any]:
    return {{"ok": True, "target": TARGET, "tableCount": len(_tables())}}


@app.get("/model")
def model_route() -> dict[str, Any]:
    return describe_model()


@app.post("/requests")
async def requests_route(payload: dict[str, Any]) -> dict[str, Any]:
    return run_request(request=str(payload.get("request") or payload.get("sentence") or ""))


for _tbl in _tables():
    _name = _tbl["table"]

    def _make_routes(table_name: str = _name) -> None:
        @app.get(f"/{{table_name}}")
        def list_endpoint(request: Request, table_name: str = table_name) -> list[dict[str, Any]]:
            filters = {{k: v for k, v in request.query_params.items()}}
            return list_rows(table_name, filters)

        @app.get(f"/{{table_name}}/{{{{row_id}}}}")
        def get_endpoint(row_id: str, table_name: str = table_name) -> dict[str, Any]:
            return get_row(table_name, row_id)

        @app.post(f"/{{table_name}}")
        async def create_endpoint(payload: dict[str, Any], table_name: str = table_name) -> dict[str, Any]:
            return create_row(table_name, payload)

        @app.post(f"/{{table_name}}/{{{{row_id}}}}")
        async def update_endpoint(row_id: str, payload: dict[str, Any], table_name: str = table_name) -> dict[str, Any]:
            return update_row(table_name, row_id, payload)

        @app.post(f"/{{table_name}}/{{{{row_id}}}}/delete")
        def delete_endpoint(row_id: str, table_name: str = table_name) -> dict[str, Any]:
            return delete_row(table_name, row_id)

    _make_routes()


# --- MCP HTTP + stdio ---

MCP_TOOLS = [
    {{"name": "describe_model", "description": "Ontology classes, columns, enums", "handler": "describe_model"}},
    {{"name": "run_request", "description": "Compile and execute a natural-language data request", "handler": "run_request"}},
    {{"name": "compile_crud_plan", "description": "Validate a plan and emit SQL or Mongo pipeline", "handler": "compile_crud_plan"}},
    {{"name": "execute_crud_plan", "description": "Execute a compiled plan", "handler": "execute_crud_plan"}},
]


@app.post("/mcp")
async def mcp_rpc(payload: dict[str, Any]) -> JSONResponse:
    method = payload.get("method")
    req_id = payload.get("id")
    if method == "tools/list":
        tools = [{{"name": t["name"], "description": t["description"], "inputSchema": {{"type": "object"}}}} for t in MCP_TOOLS]
        return JSONResponse({{"jsonrpc": "2.0", "id": req_id, "result": {{"tools": tools}}}})
    if method == "tools/call":
        params = payload.get("params") or {{}}
        name = params.get("name")
        args = params.get("arguments") or {{}}
        result = _mcp_call(name, args)
        return JSONResponse({{"jsonrpc": "2.0", "id": req_id, "result": {{"content": [{{"type": "text", "text": json.dumps(result)}}]}}}})
    return JSONResponse({{"jsonrpc": "2.0", "id": req_id, "error": {{"code": -32601, "message": "method not found"}}}})


@app.post("/mcp/tools/list")
def mcp_list() -> dict[str, Any]:
    return {{"tools": [{{"name": t["name"], "description": t["description"]}} for t in MCP_TOOLS]}}


@app.post("/mcp/tools/call")
async def mcp_call_http(payload: dict[str, Any]) -> dict[str, Any]:
    return _mcp_call(payload.get("name"), payload.get("arguments") or {{}})


def _mcp_call(name: str | None, args: dict[str, Any]) -> dict[str, Any]:
    if name == "describe_model":
        return describe_model()
    if name == "run_request":
        return run_request(**{{k: args[k] for k in ("request", "sentence") if k in args}})
    if name == "compile_crud_plan":
        return compile_crud_plan(args.get("plan"))
    if name == "execute_crud_plan":
        return execute_crud_plan(args.get("compiled") or args)
    return {{"ok": False, "error": "unknown_tool", "name": name}}


def stdio_loop() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            print(json.dumps({{"jsonrpc": "2.0", "error": {{"code": -32700, "message": "parse error"}}}}), flush=True)
            continue
        method = payload.get("method")
        req_id = payload.get("id")
        if method == "tools/list":
            tools = [{{"name": t["name"], "description": t["description"], "inputSchema": {{"type": "object"}}}} for t in MCP_TOOLS]
            print(json.dumps({{"jsonrpc": "2.0", "id": req_id, "result": {{"tools": tools}}}}), flush=True)
        elif method == "tools/call":
            params = payload.get("params") or {{}}
            result = _mcp_call(params.get("name"), params.get("arguments") or {{}})
            print(json.dumps({{"jsonrpc": "2.0", "id": req_id, "result": {{"content": [{{"type": "text", "text": json.dumps(result)}}]}}}}), flush=True)
        else:
            print(json.dumps({{"jsonrpc": "2.0", "id": req_id, "error": {{"code": -32601, "message": "method not found"}}}}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdio", action="store_true")
    parser.add_argument("--init", action="store_true")
    args, _unknown = parser.parse_known_args()
    if args.init:
        init_schema()
        print(json.dumps({{"ok": True, "init": TARGET}}))
    if args.stdio:
        stdio_loop()
    elif not args.init:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8090")))
'''
