#!/usr/bin/env python3.14
"""Run Catalog + Data agents on one port: python3.14 -m agents"""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ecosystem Agents gateway (Catalog + Data)")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.environ.get("AGENTS_PORT", "8080")))
    parser.add_argument("--rebuild", action="store_true", help="Rebuild catalog index then serve")
    parser.add_argument("--seed-demo", action="store_true", help="Load in-memory sample customers/orders before serving")
    args = parser.parse_args()

    if args.rebuild:
        from agents.catalog_agent.tools import rebuild_index

        print(rebuild_index(incremental=False))

    if args.seed_demo:
        from agents.data_agent.registry import connect

        print(connect(kind="memory", uri="memory://sample", source_id="sample"))

    import uvicorn

    uvicorn.run("agents.gateway:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
