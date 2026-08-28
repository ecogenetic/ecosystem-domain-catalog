# Catalog and Data Agents

Standalone **Python 3.14** services that sit next to the ecosystem-domain-catalog. They do not edit `domains/`, `index.json`, or other catalog contract files. Generated indexes and source mappings live under `agents/data/` (gitignored).

Two agents, **one HTTP origin** (default port **8080**):

| Path | Purpose |
|---|---|
| `/` | React workbench (after `npm run build` in `agents/frontend`) |
| `/catalog` | Catalog Agent OpenAPI + MCP |
| `/data` | Data Agent OpenAPI + MCP |
| `/docs` | Links to both Swagger UIs |

Standalone processes on 8081/8082 still work for MCP stdio. The workbench talks only to `/catalog` and `/data` on the gateway.

Deterministic graph retrieval is the default. Uploaded ontologies are parsed as **RDF 1.2 Turtle** (Oxigraph) with RDF 1.1 fallback (RDFLib). An optional OpenAI-compatible LLM (`ECOSYSTEM_LLM_BASE_URL`) can re-rank ambiguous language or refine query plans, using only IRIs and fields that already exist in the graph.

## Concept

```text
Domain language (description.md)
        ↓
Canonical OWL/SKOS + SHACL + overlays
        ↓
Catalog knowledge graph (FTS + RDF + NetworkX)
        ↓
Search / validate / expand   ← Catalog Agent
        ↓
Source DB introspection → generated OWL → catalog mapping
        ↓
NL query through mapped collections only   ← Data Agent
```

The catalog graph is a processing pipeline: **extract** file hashes → **transform** Turtle/markdown → **load** SQLite FTS5 + rdflib + NetworkX → **validate** coverage → **heal** quarantined or stale files. Name collisions (`crm:Account` vs `fin:Account`) stay distinct homonyms; joins use `core/alignments.ttl` only. Stub mappings (`legacy:Entity` ↔ `:CoreEntity`) are not indexed.

Catalog-index recovery remains available for stale indexes and invalid IRIs. Data queries are deliberately fail-closed: mapping gaps and homonyms require review, zero-row results remain valid answers, and failed queries are never repaired and silently rerun.

## Requirements

- Python 3.14
- Packages: `fastapi`, `uvicorn`, `httpx`, `pydantic`, `rdflib`, `pyoxigraph`, `networkx`, `pymongo`, `psycopg`, `sqlparse`
- Optional live MongoDB (`mongodb://localhost:27017`) or PostgreSQL (`postgresql://user:pass@localhost:5432/mydb`)

```bash
cd ecosystem-domain-catalog
python3.14 -m pip install -e agents
# or: python3.14 -m pip install fastapi uvicorn httpx pydantic rdflib pyoxigraph networkx pymongo 'psycopg[binary]' sqlparse pytest
```

Copy `agents/.env.example` and export variables as needed.

## Run

From the catalog repository root — **one port**:

```bash
# API + (optional) built UI
PYTHONPATH=. python3.14 -m agents --rebuild --port 8080

# Optional in-memory sample source (customers/orders) — does not write to a live database
PYTHONPATH=. python3.14 -m agents --seed-demo --port 8080

# Workbench with hot reload (proxies /catalog and /data to :8080)
cd agents/frontend && npm install && npm run dev
# open http://127.0.0.1:5175
```

- Workbench: `http://127.0.0.1:5175` (dev) or `http://127.0.0.1:8080` after `npm run build`
- Catalog Swagger: `http://127.0.0.1:8080/catalog/docs`
- Data Swagger: `http://127.0.0.1:8080/data/docs`
- MCP JSON-RPC: `POST /catalog/mcp` and `POST /data/mcp`

The workbench has three spaces: **Ontology** (class lookup and hierarchy), **Your data** (connect → understand → map → ask), and **Advanced** (every tool, JSON playground, MCP, both Swagger UIs).

### Docker

From `agents/` (build context is the catalog repo root):

```bash
docker compose up --build
# open http://127.0.0.1:8080
```

Or from the catalog repository root: `docker compose -f agents/docker-compose.yml up --build`.

The image is Python 3.14, serves the gateway and built workbench on **8080**, and rebuilds the catalog index at image build time. Sample data in the workbench stays in-memory. Set `AGENTS_CORS_ORIGINS` when the UI is hosted on another public origin. To point the Data Agent at a database on the host: `mongodb://host.docker.internal:27017` or `postgresql://user:pass@host.docker.internal:5432/mydb`.

MCP stdio (Cursor / Claude):

```bash
PYTHONPATH=. python3.14 -m agents.catalog_agent --stdio
PYTHONPATH=. python3.14 -m agents.data_agent --stdio
```

### Cursor MCP config

```json
{
  "mcpServers": {
    "catalog-agent": {
      "command": "python3.14",
      "args": ["-m", "agents.catalog_agent", "--stdio"],
      "env": { "PYTHONPATH": "/absolute/path/to/ecosystem-domain-catalog", "ECOSYSTEM_LLM_DISABLE": "1" }
    },
    "data-agent": {
      "command": "python3.14",
      "args": ["-m", "agents.data_agent", "--stdio"],
      "env": { "PYTHONPATH": "/absolute/path/to/ecosystem-domain-catalog" }
    }
  }
}
```

## Catalog Agent — how to use

Rebuild once (or on catalog change):

```bash
curl -X POST http://127.0.0.1:8080/catalog/v1/index/rebuild -d '{"incremental": false}' -H 'Content-Type: application/json'
```

Search:

```bash
curl -X POST http://127.0.0.1:8080/catalog/v1/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"my customer buys mobile phones","includeOntology":true,"useLlm":true}'
```

Directed:

```bash
curl -X POST http://127.0.0.1:8080/catalog/v1/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"ontology for banking credit card","domain":"card","industry":"banking","includeOntology":true}'
```

The payload always includes `validatedTerms`, `matches[]` (IRI, labels, domain, industry, score, reason), `mappings[]`, and `ontology` (IRI + Turtle) when requested or when the query contains “ontology”.

Other tools: `index_health`, `heal_index`, `validate_text`, `get_concept`, `get_ontology`, `expand_graph`, `list_domains`, `list_industries`, `get_mappings_for_concept`, `get_alignments`, `validate_iris`, `diagnose_failure`.

## Data Agent — how to use

Connect MongoDB, PostgreSQL, or a DDL schema, then introspect, generate ontology, propose mappings, resolve every ambiguity, and query. Mapping is graph-first (curated candidates, SKOS, and local names). Optionally pass `preferDomain`; an explicit `selections` object overrides it. After `map_to_catalog`, complexity is scored from the **mapping graph**.

```bash
# MongoDB
curl -X POST http://127.0.0.1:8080/data/v1/sources/connect \
  -d '{"kind":"mongodb","uri":"mongodb://localhost:27017","database":"mydb"}' \
  -H 'Content-Type: application/json'

# PostgreSQL
curl -X POST http://127.0.0.1:8080/data/v1/sources/connect \
  -d '{"kind":"postgresql","uri":"postgresql://user:pass@localhost:5432/mydb"}' \
  -H 'Content-Type: application/json'

# DDL (schema only — mapping works, counts are 0)
curl -X POST http://127.0.0.1:8080/data/v1/sources/connect \
  -d '{"kind":"ddl","sourceId":"uploaded-schema","ddl":"CREATE TABLE customer (id TEXT PRIMARY KEY, status TEXT);"}' \
  -H 'Content-Type: application/json'

# In-memory sample
curl -X POST http://127.0.0.1:8080/data/v1/sources/connect \
  -d '{"kind":"memory","uri":"memory://sample","sourceId":"sample"}' \
  -H 'Content-Type: application/json'

curl -X POST http://127.0.0.1:8080/data/v1/sources/sample/introspect
curl -X POST http://127.0.0.1:8080/data/v1/sources/sample/generate-ontology
# First call proposes mappings and returns readiness, homonyms, and candidate IRIs.
curl -X POST http://127.0.0.1:8080/data/v1/sources/sample/map -H 'Content-Type: application/json' -d '{}'

# Resolve every reported homonym explicitly. Repeat entries for all candidates returned by the first call.
curl -X POST http://127.0.0.1:8080/data/v1/sources/sample/map \
  -H 'Content-Type: application/json' \
  -d '{"selections":{"Campaign":"https://ecosystemcode.com/ontology/cvm#Campaign","Customer":"https://ecosystemcode.com/ontology/cvm#Customer","Interaction":"https://ecosystemcode.com/ontology/cvm#CustomerEvent","Order":"https://ecosystemcode.com/ontology/core#Order","OrderLine":"https://ecosystemcode.com/ontology/core#OrderLine"}}'

curl -X POST http://127.0.0.1:8080/data/v1/sources/sample/query \
  -d '{"query":"how many customers do i have","useLlm":false}' -H 'Content-Type: application/json'
```

Query compilation is sandboxed: only reviewed classes, source fields, operators, aggregates, and join paths are allowed. Ambiguous targets, unmapped fields, disconnected relationships, unsupported operations, and oversized local joins are rejected. Local multi-collection execution is limited to 10,000 rows per involved entity so truncation can never masquerade as a complete answer.

## Five complexity levels

After mapping, `assess_complexity` inspects mapped classes, enums, temporal fields, and join paths:

| Level | Name | Evidence | Example |
|---|---|---|---|
| 1 | Singleton count | ≥1 mapped class | how many customers do i have |
| 2 | Attribute / enum filter | + enum or datatype field | how many active customers |
| 3 | Temporal filter | + date/dateTime field | how many orders in the last month |
| 4 | Binary join | ≥2 classes and a join edge | how many orders have customers |
| 5 | Multi-hop compound | path length ≥2 and enum and time | orders with active customers in the last month |

`export_rerun_suite` writes `agents/data/sources/{id}/complexity.json` and `rerun_suite.json` using this source’s collection names. Unsupported levels are stored as `{status:"skipped", reason}`.

## Tests (stored and rerunnable)

Committed suites (replay without pytest source changes):

- `agents/tests/suites/catalog/cases.json` — five catalog levels
- `agents/tests/suites/data/cases.json` — five data levels against the generic sample
- `agents/tests/fixtures/sample.json` — committed customer/order seed (`$recent` / `$old` resolved at load)

```bash
cd ecosystem-domain-catalog
# graph-only (default for public CI)
PYTHONPATH=. python3.14 -m pytest agents/tests -q -m "not llm"
PYTHONPATH=. python3.14 -m agents.tests rerun --agent all --source sample --no-llm

# optional live LLM planner (requires ECOSYSTEM_LLM_BASE_URL)
PYTHONPATH=. python3.14 -m pytest agents/tests/test_llm_suite.py -q
PYTHONPATH=. python3.14 -m agents.tests rerun --agent all --source sample --llm
```

`TESTS.md` is the last-run report. Rerun does not depend on it.

Search and mapped query stay graph-first. Pass `useLlm: true` to re-rank catalog hits or refine a query plan; invented IRIs are stripped and unmapped fields are rejected. Leave `ECOSYSTEM_LLM_BASE_URL` empty, or set `ECOSYSTEM_LLM_DISABLE=1`, to keep the planner off.

## Layout

```text
agents/
  gateway.py         one-port FastAPI: /catalog + /data + optional SPA
  catalog_agent/     FastAPI + MCP + tools
  data_agent/        introspect, OWL gen, mapping, NL query
  shared/            LLM client, catalog graph, planner loop, dual server
  frontend/          React workbench (Ontology, Your data, Advanced)
  tests/suites/      stored L1–L5 cases
  data/              generated index and per-source artefacts (gitignored)
```
