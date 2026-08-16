#!/usr/bin/env python3.14
"""Catalog Agent FastAPI + MCP application."""

from __future__ import annotations

from fastapi import FastAPI

from agents.catalog_agent.tools import catalog_tools
from agents.shared.server import build_app

app: FastAPI = build_app("Ecosystem Catalog Agent", "1.0.0", catalog_tools())
