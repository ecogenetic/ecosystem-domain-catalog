#!/usr/bin/env python3.14
"""Run the Data Agent (OpenAPI + MCP HTTP, or stdio)."""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(description="Data Agent")
    parser.add_argument("--stdio", action="store_true")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.environ.get("DATA_AGENT_PORT", "8082")))
    parser.add_argument("--seed-demo", action="store_true", help="Load in-memory sample customers/orders before serving")
    args = parser.parse_args()

    if args.seed_demo:
        from agents.data_agent.registry import connect

        print(connect(kind="memory", uri="memory://sample", source_id="sample"))

    if args.stdio:
        from agents.data_agent.tools import data_tools
        from agents.shared.server import stdio_loop

        stdio_loop(data_tools())
        return

    import uvicorn

    uvicorn.run("agents.data_agent.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
