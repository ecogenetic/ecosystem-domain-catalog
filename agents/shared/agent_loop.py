#!/usr/bin/env python3.14
"""Bounded planner loop (Studio pattern) with a self-heal branch."""

from __future__ import annotations

from typing import Any, Callable

from agents.shared.llm import LlmClient, parse_planner_json

ToolFn = Callable[[dict[str, Any]], dict[str, Any]]

MAX_STEPS = 6
MAX_HEALS = 2

PLANNER_SYSTEM = """You are a catalog/data agent planner.
Return ONLY JSON with one of:
{"action":"tool_call","tool":"<name>","arguments":{}}
{"action":"heal","tool":"<heal_*>","arguments":{"error":"..."}}
{"action":"final","response":{}}
Use only the provided tool names. Never invent ontology IRIs.
If candidates were already retrieved, pick among them and return action=final.
"""


class AgentLoop:
    def __init__(self, tools: dict[str, ToolFn], llm: LlmClient | None = None, system: str | None = None) -> None:
        self.tools = tools
        self.llm = llm or LlmClient()
        self.system = system or PLANNER_SYSTEM

    def run(self, user_query: str, seed: dict[str, Any] | None = None) -> dict[str, Any]:
        trace: list[dict[str, Any]] = []
        heals = 0
        context: dict[str, Any] = dict(seed or {})
        context["query"] = user_query

        for _ in range(MAX_STEPS):
            if not self.llm.enabled() or os_disabled():
                break
            decision = self._decide(user_query, context, trace)
            action = decision.get("action")
            if action == "final":
                response = decision.get("response") or {}
                if isinstance(response, dict):
                    response.setdefault("trace", trace)
                    return response
                return {"result": response, "trace": trace}
            tool_name = str(decision.get("tool") or "")
            args = decision.get("arguments") or {}
            if not isinstance(args, dict):
                args = {}
            if tool_name not in self.tools:
                trace.append({"ok": False, "tool": tool_name, "error": "unknown_tool"})
                break
            if action == "heal":
                heals += 1
                if heals > MAX_HEALS:
                    break
            result = self._invoke(tool_name, args)
            trace.append({"tool": tool_name, "args": args, "result": _clip(result)})
            context["last"] = result
            if not result.get("ok", True) and heals < MAX_HEALS:
                diag = self._invoke(
                    "diagnose_failure",
                    {"error": result.get("error", "tool_failed"), "lastTool": tool_name, "lastArgs": args},
                )
                suggested = diag.get("suggestedTool")
                if suggested in self.tools:
                    heals += 1
                    healed = self._invoke(suggested, diag.get("suggestedArgs") or {})
                    trace.append({"tool": suggested, "heal": True, "result": _clip(healed)})
                    context["last"] = healed
        context["trace"] = trace
        return context

    def _decide(self, query: str, context: dict[str, Any], trace: list[dict[str, Any]]) -> dict[str, Any]:
        try:
            raw = self.llm.planner_step(
                self.system + "\nTools: " + ", ".join(sorted(self.tools)),
                f"Query: {query}\nContext: { _clip(context) }\nTrace: { _clip(trace) }",
            )
            if isinstance(raw, dict):
                return raw
            return parse_planner_json(str(raw))
        except Exception:  # noqa: BLE001
            return {"action": "final", "response": context}

    def _invoke(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        try:
            fn = self.tools[name]
            if isinstance(args, dict) and args:
                result = fn(**args)
            else:
                result = fn() if not args else fn(args)
            if not isinstance(result, dict):
                return {"ok": True, "result": result}
            result.setdefault("ok", True)
            return result
        except TypeError:
            try:
                result = self.tools[name](args)
                if not isinstance(result, dict):
                    return {"ok": True, "result": result}
                result.setdefault("ok", True)
                return result
            except Exception as exc:  # noqa: BLE001
                return {"ok": False, "error": str(exc), "tool": name}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc), "tool": name}

    def _call(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        return self._invoke(name, args)


def os_disabled() -> bool:
    import os

    return os.environ.get("ECOSYSTEM_LLM_DISABLE", "") == "1"


def _clip(value: Any, limit: int = 4000) -> Any:
    text = str(value)
    if len(text) <= limit:
        return value
    return text[:limit] + "…"
