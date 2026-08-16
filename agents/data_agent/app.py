#!/usr/bin/env python3.14
"""Data Agent FastAPI + MCP application."""

from __future__ import annotations

from fastapi import FastAPI

from agents.data_agent.tools import data_tools
from agents.shared.server import build_app

app: FastAPI = build_app("Ecosystem Data Agent", "1.0.0", data_tools())
