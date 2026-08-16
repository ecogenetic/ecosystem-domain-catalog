#!/usr/bin/env python3.14
"""Filesystem locations for the catalog repo and generated agent data."""

from __future__ import annotations

import os
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[1]
CATALOG_ROOT = Path(os.environ.get("CATALOG_ROOT") or AGENTS_DIR.parent).resolve()
DATA_DIR = Path(os.environ.get("AGENTS_DATA_DIR") or (AGENTS_DIR / "data")).resolve()
INDEX_DB = DATA_DIR / "catalog_index.db"
GRAPH_PATH = DATA_DIR / "catalog_graph.pkl"
SOURCES_DIR = DATA_DIR / "sources"


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def source_dir(source_id: str) -> Path:
    path = SOURCES_DIR / source_id
    path.mkdir(parents=True, exist_ok=True)
    return path
