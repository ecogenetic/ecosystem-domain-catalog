# TESTS.md — last run report

Recorded 2026-08-19. Rerun the suites with the commands below; this file is a report, not the source of the cases.

## Commands

```bash
cd ecosystem-domain-catalog
PYTHONPATH=. python3.14 -m pytest agents/tests -q -m "not llm"
PYTHONPATH=. python3.14 -m agents.tests rerun --agent all --source sample --no-llm

# optional — skipped unless ECOSYSTEM_LLM_BASE_URL is set
PYTHONPATH=. python3.14 -m pytest agents/tests -q -m llm
PYTHONPATH=. python3.14 -m agents.tests rerun --agent all --source sample --llm
```

Stored cases: `agents/tests/suites/catalog/cases.json`, `agents/tests/suites/data/cases.json`.
LLM planner: only when `ECOSYSTEM_LLM_BASE_URL` is set. `test_llm_suite.py` skips if that variable is empty.

## Pytest — deterministic (`-m "not llm"`)

- Platform: darwin, Python 3.14.7, pytest 9.0.2
- Result: **26 passed** in ~2s
- `test_catalog_suite.py`: 8 passed (index coverage, stub skip, L1–L5 suite, IRI validation, expand, heal)
- `test_complexity.py`: 1 passed (mapping-graph evidence, maxJoinPath ≥ 2)
- `test_data_suite.py`: 7 passed (introspect, map, ontology labels, L1–L5 counts, unmapped reject, complexity=5)
- `test_ddl.py`: 2 passed (CREATE TABLE parse, schema-only connect/map)
- `test_http_apps.py`: 8 passed (catalog search, gateway one-port, MCP JSON Schema, OpenAPI plan paths, source/ontology HTTP routes, preview ontology)

## Pytest — LLM (`test_llm_suite.py`)

- Probe: skipped — `ECOSYSTEM_LLM_BASE_URL` is not set
- Result: **3 skipped**
- Set a live OpenAI-compatible endpoint to run `test_llm_endpoint_reachable`, `test_catalog_suite_with_llm`, and `test_data_suite_with_llm`

## Stored suite rerun (`python3.14 -m agents.tests rerun --source sample --no-llm`)

**10 / 10 passed**, 0 failed.

### Catalog agent

| Level | Id | Query | Status |
|---|---|---|---|
| 1 | catalog-L1-credit-card | ontology for banking credit card | pass — `card/banking#RetailCreditCard` + Turtle |
| 2 | catalog-L2-deal-synonym | deal | pass — `crm:Opportunity` via SKOS altLabel |
| 3 | catalog-L3-customer-phones | my customer buys mobile phones | pass — Customer / Product among CVM, CRM, PIM, ECOM |
| 4 | catalog-L4-account-homonym | Account | pass — distinct `crm:Account` and `fin:Account` |
| 5 | catalog-L5-overlay-expand | banking credit card + expand_graph | pass — overlay class + `subClassOf` edges |

### Data agent (in-memory fixture `sample`)

| Level | Id | Query | Expected count | Status |
|---|---|---|---|---|
| 1 | data-L1-count-customers | how many customers do i have | 4 | pass |
| 2 | data-L2-active-customers | how many active customers | 2 | pass |
| 3 | data-L3-orders-month | how many orders in the last month | 2 | pass |
| 4 | data-L4-orders-have-customers | how many orders have customers | 3 | pass |
| 5 | data-L5-active-recent-orders | campaigns with male customers that interacted last month | 1 | pass |

## Complexity from mapping (`sample`)

```json
{
  "sourceId": "sample",
  "maxLevel": 5,
  "supportedLevels": [1, 2, 3, 4, 5],
  "evidence": {
    "mappedClasses": 5,
    "mappedProperties": 14,
    "enumFields": [
      "Campaign.status",
      "Customer.status",
      "Customer.gender",
      "Customer.region",
      "Interaction.channel",
      "Order.status"
    ],
    "temporalFields": ["Interaction.occurred_at", "Order.ordered_at"],
    "maxJoinPath": 3,
    "joinPaths": [["Campaign", "Interaction", "Customer"]]
  },
  "unsupported": []
}
```

Fixtures include gender, interaction timestamps, and campaign–customer–interaction links. DDL sources are schema-only (`count` 0). Mapping still runs; Ask is disabled until a live store or sample data is connected. Unsupported levels are stored as `{status: "skipped", reason}` in `agents/data/sources/{id}/rerun_suite.json`.

## Example payloads

Catalog L1 top match: `https://ecosystemcode.com/ontology/card/banking#RetailCreditCard` (prefLabel Retail Credit Card, industry banking). Ontology Turtle for the CARD banking overlay is included when `includeOntology` is true.

Data L5 compiled plan: `targetClass=Campaign`, filters `Customer.gender=male` and `Interaction.occurred_at >= (now-31d)`, joins Interaction↔Customer and Interaction↔Campaign.
