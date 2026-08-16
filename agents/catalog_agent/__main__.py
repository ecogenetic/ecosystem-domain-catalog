#!/usr/bin/env python3.14
"""Run the Catalog Agent (OpenAPI + MCP HTTP, or stdio)."""

from __future__ import annotations

import argparse
import os
import sys

# Allow `python3.14 -m agents.catalog_agent` from the catalog repo root.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(description="Catalog Agent")
    parser.add_argument("--stdio", action="store_true")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.environ.get("CATALOG_AGENT_PORT", "8081")))
    parser.add_argument("--rebuild", action="store_true", help="Rebuild index then exit")
    args = parser.parse_args()

    if args.rebuild:
        from agents.catalog_agent.tools import rebuild_index

        result = rebuild_index(incremental=False)
        print(result)
        return

    if args.stdio:
        from agents.catalog_agent.tools import catalog_tools
        from agents.shared.server import stdio_loop

        stdio_loop(catalog_tools())
        return

    import uvicorn

    uvicorn.run("agents.catalog_agent.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
