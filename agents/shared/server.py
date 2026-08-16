#!/usr/bin/env python3.14
"""Dual OpenAPI (FastAPI) + MCP JSON-RPC server from a shared tool registry."""

from __future__ import annotations

import inspect
import json
import os
import re
import types
from typing import Any, Callable, Union, get_args, get_origin, get_type_hints

from fastapi import Body, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

LOCAL_ORIGIN_REGEX = r"https?://(localhost|127\.0\.0\.1)(:\d+)?"
PATH_PARAM_RE = re.compile(r"\{([^}]+)\}")


def add_cors(app: FastAPI) -> None:
    extras = [origin.strip().rstrip("/") for origin in os.environ.get("AGENTS_CORS_ORIGINS", "").split(",") if origin.strip()]
    pattern = LOCAL_ORIGIN_REGEX
    if extras:
        escaped = "|".join(re.escape(origin) for origin in extras)
        pattern = rf"({LOCAL_ORIGIN_REGEX})|({escaped})"
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=pattern,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


ToolFn = Callable[..., dict[str, Any]]


class ToolSpec(BaseModel):
    name: str
    description: str
    method: str = "POST"
    path: str
    handler: Any = None

    model_config = {"arbitrary_types_allowed": True}


def annotation_schema(ann: Any) -> dict[str, Any]:
    if ann is inspect.Parameter.empty or ann is Any:
        return {}
    origin = get_origin(ann)
    args = [a for a in get_args(ann) if a is not type(None)]
    if origin in (types.UnionType, Union):
        if len(args) == 1:
            return {**annotation_schema(args[0]), "nullable": True}
        return {}
    if origin is list or ann is list:
        return {"type": "array"}
    if origin is dict or ann is dict:
        return {"type": "object"}
    if ann is bool:
        return {"type": "boolean"}
    if ann is int:
        return {"type": "integer"}
    if ann is float:
        return {"type": "number"}
    if ann is str:
        return {"type": "string"}
    return {}


def input_schema(fn: Callable[..., Any]) -> dict[str, Any]:
    try:
        hints = get_type_hints(fn)
    except Exception:  # noqa: BLE001
        hints = {}
    sig = inspect.signature(fn)
    properties: dict[str, Any] = {}
    required: list[str] = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        properties[name] = annotation_schema(hints.get(name, param.annotation))
        if param.default is inspect.Parameter.empty:
            required.append(name)
    schema: dict[str, Any] = {"type": "object", "properties": properties, "additionalProperties": True}
    if required:
        schema["required"] = required
    return schema


def coerce_value(value: Any, annotation: Any) -> Any:
    if value is None or annotation is inspect.Parameter.empty:
        return value
    origin = get_origin(annotation)
    args = get_args(annotation)
    base = annotation
    if origin in (types.UnionType, Union):
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            base = non_none[0]
    if base is bool:
        if isinstance(value, str):
            return value.lower() in {"1", "true", "yes"}
        return bool(value)
    if base is int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return value
    return value


def build_app(title: str, version: str, tools: list[ToolSpec]) -> FastAPI:
    app = FastAPI(title=title, version=version)
    add_cors(app)
    registry = {t.name: t for t in tools}
    schemas = {t.name: input_schema(t.handler) for t in tools}

    @app.get("/v1/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "service": title}

    @app.get("/mcp/info")
    def mcp_info() -> dict[str, Any]:
        return {
            "name": title,
            "version": version,
            "tools": [t.name for t in tools],
        }

    def make_handler(spec: ToolSpec) -> Callable[..., Any]:
        def _call(payload: dict[str, Any]) -> dict[str, Any]:
            fn = spec.handler
            sig = inspect.signature(fn)
            try:
                hints = get_type_hints(fn)
            except Exception:  # noqa: BLE001
                hints = {}
            kwargs = {}
            for name, param in sig.parameters.items():
                if name in payload:
                    kwargs[name] = coerce_value(payload[name], hints.get(name, param.annotation))
                elif param.default is inspect.Parameter.empty and name not in {"self"}:
                    kwargs[name] = None
            return fn(**kwargs) if kwargs or sig.parameters else fn()

        return _call

    def register_route(spec: ToolSpec, route_path: str, method: str, name: str) -> None:
        runner = make_handler(spec)
        path_params = PATH_PARAM_RE.findall(route_path)
        http_method = method.upper()
        if http_method == "GET" and not path_params:
            sig = inspect.signature(spec.handler)

            async def endpoint(**kwargs: Any) -> JSONResponse:
                return JSONResponse(runner(kwargs))

            params = []
            for pname, param in sig.parameters.items():
                if pname == "self":
                    continue
                default = param.default if param.default is not inspect.Parameter.empty else None
                params.append(
                    inspect.Parameter(
                        pname,
                        inspect.Parameter.KEYWORD_ONLY,
                        default=Query(default),
                        annotation=param.annotation if param.annotation is not inspect.Parameter.empty else Any,
                    )
                )
            endpoint.__signature__ = inspect.Signature(params)  # type: ignore[attr-defined]
            endpoint.__name__ = name
            app.add_api_route(route_path, endpoint, methods=["GET"], name=name, tags=["tools"])
            return

        if http_method == "GET":

            async def get_endpoint(request: Request) -> JSONResponse:
                data = dict(request.query_params)
                data.update(request.path_params)
                return JSONResponse(runner(data))

            get_endpoint.__name__ = name
            app.add_api_route(route_path, get_endpoint, methods=["GET"], name=name, tags=["tools"])
            return

        async def post_endpoint(request: Request, payload: dict[str, Any] | None = Body(default=None)) -> JSONResponse:
            data = dict(payload or {})
            data.update(request.path_params)
            return JSONResponse(runner(data))

        post_endpoint.__name__ = name
        app.add_api_route(route_path, post_endpoint, methods=["POST"], name=name, tags=["tools"])

    for spec in tools:
        register_route(spec, spec.path, spec.method, spec.name)
        alias = f"/v1/tools/{spec.name}"
        if alias != spec.path:
            register_route(spec, alias, "POST", f"{spec.name}_tool")

    def mcp_tool_list() -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": schemas[t.name],
            }
            for t in tools
        ]

    @app.post("/mcp")
    async def mcp_rpc(payload: dict[str, Any] = Body(...)) -> JSONResponse:
        method = payload.get("method")
        req_id = payload.get("id")
        params = payload.get("params") or {}
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": title, "version": version},
            }
        elif method == "tools/list":
            result = {"tools": mcp_tool_list()}
        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments") or {}
            spec = registry.get(name)
            if spec is None:
                return JSONResponse(
                    {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool {name}"}}
                )
            data = make_handler(spec)(arguments)
            result = {
                "content": [{"type": "text", "text": json.dumps(data, default=str)}],
                "isError": not data.get("ok", True),
            }
        elif method == "notifications/initialized":
            return JSONResponse({"jsonrpc": "2.0"})
        else:
            return JSONResponse(
                {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method {method}"}}
            )
        return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": result})

    @app.post("/mcp/tools/list")
    async def tools_list() -> dict[str, Any]:
        return {"tools": mcp_tool_list()}

    @app.post("/mcp/tools/call")
    async def tools_call(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        name = payload.get("name")
        arguments = payload.get("arguments") or {}
        spec = registry.get(name)
        if spec is None:
            return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool {name}"}]}
        data = make_handler(spec)(arguments)
        return {
            "content": [{"type": "text", "text": json.dumps(data, default=str)}],
            "isError": not data.get("ok", True),
        }

    app.state.tools = registry
    return app


def stdio_loop(tools: list[ToolSpec]) -> None:
    """Minimal MCP stdio JSON-RPC loop."""
    import sys

    registry = {t.name: t for t in tools}
    app_name = "catalog-agents"

    def handle(msg: dict[str, Any]) -> dict[str, Any] | None:
        method = msg.get("method")
        req_id = msg.get("id")
        params = msg.get("params") or {}
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": app_name, "version": "1.0.0"},
            }
        elif method == "tools/list":
            result = {
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": input_schema(t.handler),
                    }
                    for t in tools
                ]
            }
        elif method == "tools/call":
            spec = registry.get(params.get("name"))
            if spec is None:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "unknown tool"}}
            fn = spec.handler
            sig = inspect.signature(fn)
            kwargs = {k: v for k, v in (params.get("arguments") or {}).items() if k in sig.parameters}
            data = fn(**kwargs) if kwargs else fn()
            result = {"content": [{"type": "text", "text": json.dumps(data, default=str)}]}
        else:
            if req_id is None:
                return None
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": method}}
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            out = handle(msg)
            if out is not None:
                sys.stdout.write(json.dumps(out) + "\n")
                sys.stdout.flush()
        except Exception as exc:  # noqa: BLE001
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"message": str(exc)}}) + "\n")
            sys.stdout.flush()
