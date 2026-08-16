#!/usr/bin/env python3.14
"""One-port gateway: Catalog at /catalog, Data at /data, optional SPA at /."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from agents.shared.server import add_cors

FRONTEND_DIST = Path(__file__).resolve().parent / "frontend" / "dist"

DOCS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Ecosystem Agents — API docs</title>
  <style>
    body { font-family: Arial, sans-serif; background: #0d0f12; color: #fff; margin: 2rem; }
    a { color: #00aeef; }
    .card { background: #1a1d24; border: 1px solid #2a2d35; border-radius: 8px; padding: 1.25rem; margin: 1rem 0; max-width: 520px; }
  </style>
</head>
<body>
  <h1>Ecosystem Agents</h1>
  <p>The catalog agent exposes the ontology (classes, labels, relations). The data agent maps sources onto those classes. Open Swagger for the agent you need.</p>
  <div class="card">
    <h2>Catalog Agent — ontology</h2>
    <p><a href="/catalog/docs">Swagger UI</a> · <a href="/catalog/redoc">ReDoc</a> · <a href="/catalog/openapi.json">openapi.json</a></p>
  </div>
  <div class="card">
    <h2>Data Agent</h2>
    <p><a href="/data/docs">Swagger UI</a> · <a href="/data/redoc">ReDoc</a> · <a href="/data/openapi.json">openapi.json</a></p>
  </div>
</body>
</html>
"""


def create_app() -> FastAPI:
    from agents.catalog_agent.app import app as catalog_app
    from agents.data_agent.app import app as data_app

    app = FastAPI(
        title="Ecosystem Agents",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    add_cors(app)
    app.mount("/catalog", catalog_app)
    app.mount("/data", data_app)

    @app.get("/v1/health")
    def health() -> dict:
        return {
            "ok": True,
            "service": "Ecosystem Agents",
            "catalog": "/catalog/v1/health",
            "data": "/data/v1/health",
        }

    @app.get("/docs", response_class=HTMLResponse)
    def docs_index() -> str:
        return DOCS_HTML

    dist = FRONTEND_DIST
    if dist.is_dir() and (dist / "index.html").is_file():
        assets = dist / "assets"
        if assets.is_dir():
            app.mount("/assets", StaticFiles(directory=assets), name="assets")

        @app.get("/")
        def spa_root():
            return FileResponse(dist / "index.html")

        @app.get("/{full_path:path}")
        def spa_fallback(full_path: str):
            reserved = ("catalog", "data", "v1", "docs", "assets")
            if full_path.split("/", 1)[0] in reserved:
                return JSONResponse({"ok": False, "error": "not_found"}, status_code=404)
            candidate = dist / full_path
            if candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(dist / "index.html")
    else:

        @app.get("/")
        def root() -> dict:
            return {
                "ok": True,
                "service": "Ecosystem Agents",
                "catalog": "/catalog/docs",
                "data": "/data/docs",
                "docs": "/docs",
                "ui": "Build agents/frontend (npm run build) to serve the workbench at /",
            }

    return app


app = create_app()
