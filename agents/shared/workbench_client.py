#!/usr/bin/env python3.14
"""Thin client for Ecosystem Workbench2 public ontology intelligence API.

Configured via:

* ``WORKBENCH_ONTOLOGY_SERVER`` (preferred) or ``ECOSYSTEM_BACKEND_URL``
* ``WORKBENCH_API_KEY`` (``ewb_public_*`` bearer / X-API-Key)

The catalog agents keep local DB connect/sample thin; all ontology intelligence
(mapping, physical compile, browse/resolve, evolution) delegates here when
configured. When the server is unreachable, callers may fall back to local
stubs and stamp ``intelligenceSource: local-fallback``.
"""

from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import urlparse

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None

DEFAULT_SERVER = "http://localhost:8000"


def normalize_workbench_server(raw: str | None = None) -> str:
    value = (
        raw
        if raw is not None
        else (
            os.environ.get("WORKBENCH_ONTOLOGY_SERVER", "").strip()
            or os.environ.get("ECOSYSTEM_BACKEND_URL", "").strip()
        )
    )
    if not value:
        value = DEFAULT_SERVER
    value = re.sub(r"^(https?):(?!/)([^/])", r"\1://\2", value)
    if not value.startswith(("http://", "https://")):
        value = "http://" + value.lstrip("/")
    return value.rstrip("/")


def workbench_server() -> str:
    return normalize_workbench_server()


def workbench_api_key() -> str:
    return (
        os.environ.get("WORKBENCH_API_KEY", "").strip()
        or os.environ.get("ECOSYSTEM_WORKBENCH_API_KEY", "").strip()
    )


def is_configured() -> bool:
    """True when a non-default server or an API key is present."""
    server = workbench_server()
    key = workbench_api_key()
    if key:
        return True
    host = urlparse(server).hostname or ""
    return host not in {"", "localhost", "127.0.0.1"} or bool(
        os.environ.get("WORKBENCH_ONTOLOGY_SERVER", "").strip()
    )


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    key = workbench_api_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"
        headers["X-API-Key"] = key
    return headers


def _public_path(path: str) -> str:
    path = path if path.startswith("/") else f"/{path}"
    if path.startswith("/public/"):
        return path
    if path.startswith("/api/v1/"):
        return path.replace("/api/v1/", "/public/v1/", 1)
    if path.startswith("/ontology"):
        return f"/public/v1{path}"
    return f"/public/v1/ontology{path}"


def _request(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    timeout: float = 60.0,
) -> dict[str, Any]:
    if httpx is None:
        raise RuntimeError("httpx is required for Workbench ontology client")
    url = f"{workbench_server()}{_public_path(path)}"
    resp = httpx.request(
        method.upper(),
        url,
        json=body,
        params=params,
        headers=_headers(),
        timeout=timeout,
    )
    resp.raise_for_status()
    if not resp.content:
        return {"ok": True}
    data = resp.json()
    if isinstance(data, dict):
        data.setdefault("intelligenceSource", "workbench")
        data.setdefault("workbenchServer", workbench_server())
        return data
    return {"ok": True, "data": data, "intelligenceSource": "workbench"}


def get(path: str, *, params: dict[str, Any] | None = None, timeout: float = 30.0) -> dict[str, Any]:
    return _request("GET", path, params=params, timeout=timeout)


def post(
    path: str,
    body: dict[str, Any] | None = None,
    *,
    timeout: float = 60.0,
) -> dict[str, Any]:
    return _request("POST", path, body=body or {}, timeout=timeout)


def health() -> dict[str, Any]:
    try:
        return get("/ontology/health")
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "intelligenceSource": "local-fallback",
            "workbenchServer": workbench_server(),
            "error": str(exc),
        }


def compile_physical(
    ontology_id: str,
    *,
    content: str | None = None,
    shapes_ttl: str | None = None,
    target: str = "postgresql",
) -> dict[str, Any]:
    body: dict[str, Any] = {"target": target}
    if content is not None:
        body["content"] = content
    if shapes_ttl is not None:
        body["shapes_ttl"] = shapes_ttl
    return post(f"/ontology/{ontology_id}/physical/compile", body)


def generate_ddl(ontology_id: str, *, dialect: str = "postgresql", content: str | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"dialect": dialect}
    if content is not None:
        body["content"] = content
    return post(f"/ontology/{ontology_id}/physical/ddl", body)


def browse_semantics(
    ontology_id: str,
    query: str,
    *,
    kind: str = "all",
    limit: int = 6,
    version: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"query": query, "kind": kind, "limit": limit}
    if version:
        body["version"] = version
    return post(f"/ontology/{ontology_id}/browse-semantics", body)


def resolve_semantics(
    ontology_id: str,
    mentions: list[str],
    *,
    context: str = "",
    version: str | None = None,
    mapping_id: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"mentions": mentions, "context": context}
    if version:
        body["version"] = version
    if mapping_id:
        body["mapping_id"] = mapping_id
    return post(f"/ontology/{ontology_id}/resolve-semantics", body)


def from_schema_payload(
    *,
    database: str,
    collection: str,
    sample_documents: list[dict[str, Any]] | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """Forward sampled local rows for remote ontology extraction.

    Prefer ``/ontology/infer`` (documents) or ``/ontology/from-data-source`` when
    the Workbench can reach the same Mongo. Catalog gateways typically POST
    samples via infer.
    """
    body: dict[str, Any] = {
        "database": database,
        "collection": collection,
        "documents": sample_documents or [],
        "persist": True,
    }
    if name:
        body["name"] = name
    return post("/ontology/infer", body, timeout=120.0)


def call_or_fallback(remote_fn, fallback_fn, *args, **kwargs) -> dict[str, Any]:
    """Try Workbench first when configured; otherwise run local fallback."""
    if is_configured() or workbench_api_key():
        try:
            return remote_fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            result = fallback_fn(*args, **kwargs)
            if isinstance(result, dict):
                result = {
                    **result,
                    "intelligenceSource": "local-fallback",
                    "workbenchError": str(exc),
                    "workbenchServer": workbench_server(),
                }
            return result
    result = fallback_fn(*args, **kwargs)
    if isinstance(result, dict):
        result = {**result, "intelligenceSource": "local"}
    return result
