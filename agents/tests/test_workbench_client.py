#!/usr/bin/env python3.14
"""Thin Workbench client tests (no live server required)."""

from __future__ import annotations

import os

from agents.shared import workbench_client


def test_normalize_workbench_server_typo_fix() -> None:
    assert workbench_client.normalize_workbench_server("http:localhost:8000") == "http://localhost:8000"


def test_public_path_rewrites_ontology() -> None:
    assert workbench_client._public_path("/ontology/health") == "/public/v1/ontology/health"
    assert workbench_client._public_path("/public/v1/ontology/x") == "/public/v1/ontology/x"


def test_call_or_fallback_uses_local_when_unconfigured(monkeypatch) -> None:
    monkeypatch.delenv("WORKBENCH_API_KEY", raising=False)
    monkeypatch.delenv("ECOSYSTEM_WORKBENCH_API_KEY", raising=False)
    monkeypatch.setenv("WORKBENCH_ONTOLOGY_SERVER", "")
    monkeypatch.setenv("ECOSYSTEM_BACKEND_URL", "")

    def remote():
        raise AssertionError("should not call remote")

    def local():
        return {"ok": True, "value": 1}

    # Force unconfigured path
    monkeypatch.setattr(workbench_client, "is_configured", lambda: False)
    monkeypatch.setattr(workbench_client, "workbench_api_key", lambda: "")
    result = workbench_client.call_or_fallback(remote, local)
    assert result["ok"] is True
    assert result["intelligenceSource"] == "local"


def test_call_or_fallback_remote_error_stamps_fallback(monkeypatch) -> None:
    monkeypatch.setattr(workbench_client, "is_configured", lambda: True)
    monkeypatch.setattr(workbench_client, "workbench_api_key", lambda: "ewb_public_test")
    monkeypatch.setattr(workbench_client, "workbench_server", lambda: "http://example.invalid")

    def remote():
        raise RuntimeError("down")

    def local():
        return {"ok": True}

    result = workbench_client.call_or_fallback(remote, local)
    assert result["intelligenceSource"] == "local-fallback"
    assert "down" in result["workbenchError"]


def test_env_example_documents_workbench_keys() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(root, ".env.example")
    text = open(env_path, encoding="utf-8").read()
    assert "WORKBENCH_ONTOLOGY_SERVER" in text
    assert "WORKBENCH_API_KEY" in text
