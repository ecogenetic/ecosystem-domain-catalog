#!/usr/bin/env python3.14
"""Rerun stored per-agent suites: python3.14 -m agents.tests rerun --agent catalog|data."""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="rerun")
    parser.add_argument("--agent", choices=["catalog", "data", "all"], default="all")
    parser.add_argument("--source", default="sample")
    parser.add_argument("--llm", action="store_true", help="Run stored cases through the LLM planner")
    parser.add_argument("--no-llm", action="store_true", help="Force ECOSYSTEM_LLM_DISABLE=1")
    args = parser.parse_args()
    if args.no_llm:
        os.environ["ECOSYSTEM_LLM_DISABLE"] = "1"
    from agents.tests.runner import rerun

    results = rerun(agent=args.agent, source_id=args.source, use_llm=args.llm)
    print(json.dumps(results, indent=2, default=str))
    failed = [c for c in results.get("cases", []) if c.get("status") == "fail"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
