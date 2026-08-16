#!/usr/bin/env python3.14
"""OpenAI-compatible LLM client. Disabled until ECOSYSTEM_LLM_BASE_URL is set."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

DEFAULT_BASE = os.environ.get("ECOSYSTEM_LLM_BASE_URL") or os.environ.get("CHAT_SERVER") or ""
DEFAULT_MODEL = os.environ.get("ECOSYSTEM_LLM_MODEL") or os.environ.get("CHAT_SERVER_MODEL") or ""
DEFAULT_KEY = os.environ.get("ECOSYSTEM_LLM_API_KEY") or os.environ.get("CHAT_SERVER_KEY", "")


class LlmClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = (base_url or DEFAULT_BASE).rstrip("/")
        self.model = model or DEFAULT_MODEL
        self.api_key = api_key if api_key is not None else DEFAULT_KEY
        self.timeout = timeout

    def enabled(self) -> bool:
        return bool(self.base_url) and os.environ.get("ECOSYSTEM_LLM_DISABLE", "") != "1"

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            key = self.api_key.strip()
            if key.lower().startswith("bearer ") or key.lower().startswith("basic "):
                headers["Authorization"] = key
            else:
                headers["Authorization"] = f"Bearer {key}"
        return headers

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": temperature,
        }
        last_error: Exception | None = None
        for path in ("/v1/chat/completions", "/api/chat"):
            url = self.base_url + path
            try:
                body = payload
                if path == "/api/chat":
                    body = {**payload, "model": self.model}
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(url, headers=self._headers(), json=body)
                    resp.raise_for_status()
                    data = resp.json()
                if path == "/v1/chat/completions":
                    choices = data.get("choices") or []
                    if choices:
                        return str((choices[0].get("message") or {}).get("content") or "")
                message = data.get("message") or {}
                if message.get("content"):
                    return str(message["content"])
            except Exception as exc:  # noqa: BLE001 — try fallback endpoint
                last_error = exc
                continue
        raise RuntimeError(f"LLM request failed: {last_error}")

    def planner_step(self, system: str, user: str) -> dict[str, Any]:
        raw = self.chat(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]
        )
        return parse_planner_json(raw)


def parse_planner_json(raw: str) -> dict[str, Any]:
    import re

    text = raw.strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < 0:
        return {"action": "final", "response": {"raw": raw}}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {"action": "final", "response": {"raw": raw}}
