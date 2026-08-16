#!/usr/bin/env python3.14
"""LLM planner wrappers: refine deterministic catalog search and mapped queries."""

from __future__ import annotations

import json
import os
from typing import Any

from agents.shared.agent_loop import AgentLoop, os_disabled
from agents.shared.llm import LlmClient

CATALOG_PLANNER = """You refine catalog search. Deterministic graph search already ran.
Return ONLY JSON:
{"action":"tool_call","tool":"<name>","arguments":{}}
{"action":"final","response":{"selectedIris":["https://..."]}}
Rules:
- selectedIris MUST be copied from the candidate IRIs already in context. Never invent IRIs.
- For homonyms (e.g. Account in CRM vs FIN) keep every distinct matching domain IRI.
- For "credit card" + banking prefer RetailCreditCard overlay IRI if it is a candidate.
- You may call expand_graph, get_ontology, get_concept, validate_iris, search_catalog.
- After at most two tool calls, return action=final.
"""

DATA_PLANNER = """You refine a sandboxed database query plan.
Return ONLY JSON:
{"action":"tool_call","tool":"<name>","arguments":{}}
{"action":"final","response":{"useDeterministic":true}}
{"action":"final","response":{"plan":{...}}}
Rules:
- Prefer the deterministic plan unless a required filter is missing (status, last month).
- Never add fields that are not in the mapping.
- compile_query_plan and execute_query_plan are the only query tools.
- If the deterministic result already answers the question, return useDeterministic true.
"""


def llm_available() -> tuple[bool, str]:
    if os_disabled():
        return False, "ECOSYSTEM_LLM_DISABLE=1"
    client = LlmClient(timeout=45)
    try:
        text = client.chat([{"role": "user", "content": "Reply with the single word pong and nothing else."}])
        if text and text.strip():
            return True, text.strip()[:200]
        return False, "empty LLM response"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def refine_catalog_search(query: str, deterministic: dict[str, Any], **search_kwargs: Any) -> dict[str, Any]:
    from agents.catalog_agent import tools as cat

    if os_disabled() or not LlmClient().enabled():
        deterministic["llm"] = {"used": False, "reason": "disabled"}
        return deterministic
    candidates = [
        {"iri": m.get("iri"), "prefLabel": m.get("prefLabel"), "domainId": m.get("domainId"), "localName": m.get("localName")}
        for m in (deterministic.get("matches") or [])[:15]
    ]
    tools = {
        "search_catalog": lambda **kw: cat.search_catalog(
            query=kw.pop("query", query), **{**search_kwargs, **kw, "useLlm": False}
        ),
        "expand_graph": cat.expand_graph,
        "get_ontology": cat.get_ontology,
        "get_concept": cat.get_concept,
        "validate_iris": cat.validate_iris,
        "diagnose_failure": cat.diagnose_failure,
    }
    loop = AgentLoop(tools, LlmClient(timeout=90), system=CATALOG_PLANNER)
    planned = loop.run(
        query,
        seed={"candidates": candidates, "deterministicMatches": candidates},
    )
    selected = _extract_iris(planned)
    checked = cat.validate_iris(iris=selected)
    valid = [v["iri"] for v in checked.get("valid") or []]
    by_iri = {m.get("iri"): m for m in deterministic.get("matches") or []}
    if valid:
        seen: set[str] = set()
        ordered = []
        for iri in valid:
            if iri in by_iri and iri not in seen:
                ordered.append(by_iri[iri])
                seen.add(iri)
        extra = [cat.get_concept(iri=i) for i in valid if i not in by_iri]
        extra = [e for e in extra if e.get("ok") and e.get("kind") in {"class", "overlay_class", "role"}]
        rest = [m for m in (deterministic.get("matches") or []) if m.get("iri") not in seen]
        deterministic["matches"] = ordered + extra + rest
    deterministic["llm"] = {
        "used": True,
        "selectedIris": valid,
        "trace": planned.get("trace") or [],
        "stripped": checked.get("invalid") or [],
    }
    return deterministic


def refine_mapped_query(source_id: str, query: str, deterministic: dict[str, Any]) -> dict[str, Any]:
    from agents.data_agent import tools as dat
    from agents.data_agent import query as query_mod
    from agents.data_agent import registry

    if os_disabled() or not LlmClient().enabled():
        deterministic["llm"] = {"used": False, "reason": "disabled"}
        return deterministic
    tools = {
        "compile_query_plan": lambda **kw: dat.compile_query_plan(id=source_id, query=kw.get("query", query)),
        "execute_query_plan": lambda **kw: dat.execute_query_plan(id=source_id, plan=kw.get("plan") or deterministic.get("plan")),
        "diagnose_failure": dat.diagnose_failure,
    }
    loop = AgentLoop(tools, LlmClient(timeout=90), system=DATA_PLANNER)
    planned = loop.run(query, seed={"deterministic": _clip_plan(deterministic)})
    response = planned if isinstance(planned, dict) else {}
    inner = response.get("response") if isinstance(response.get("response"), dict) else response
    if inner.get("useDeterministic") or not inner.get("plan"):
        deterministic["llm"] = {"used": True, "keptDeterministic": True, "trace": planned.get("trace") or []}
        return deterministic
    executed = query_mod.execute_query_plan(registry.store(source_id), source_id, inner["plan"])
    executed["plan"] = inner.get("plan") or deterministic.get("plan")
    executed["query"] = query
    executed["llm"] = {"used": True, "keptDeterministic": False, "trace": planned.get("trace") or []}
    if not executed.get("ok"):
        deterministic["llm"] = {"used": True, "fellBack": True, "error": executed.get("error")}
        return deterministic
    return executed


def _extract_iris(planned: dict[str, Any]) -> list[str]:
    blobs = [planned, planned.get("response"), planned.get("last")]
    iris: list[str] = []
    for blob in blobs:
        if not isinstance(blob, dict):
            continue
        for key in ("selectedIris", "iris", "matches"):
            val = blob.get(key)
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, str) and item.startswith("http"):
                        iris.append(item)
                    elif isinstance(item, dict) and str(item.get("iri", "")).startswith("http"):
                        iris.append(str(item["iri"]))
    # also scan trace finals
    for step in planned.get("trace") or []:
        if not isinstance(step, dict):
            continue
        text = json.dumps(step, default=str)
        for token in text.replace('"', " ").replace("'", " ").split():
            if token.startswith("https://ecosystemcode.com/ontology/") and token not in iris:
                iris.append(token.rstrip(",]}"))
    return iris


def _clip_plan(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "result": result.get("result"),
        "plan": result.get("plan"),
        "ok": result.get("ok"),
    }
