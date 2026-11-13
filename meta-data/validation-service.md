# Ontology Validation Service

External products and catalog tooling can validate RDF 1.2 / Turtle / OWL 2 / SKOS / SHACL
ontologies through the public **Ontology Validation, Syntax & Recommendation** service hosted
on **ecosystem-server**. No JWT or login is required for the standalone endpoints.

## `ONTOLOGY_VALIDATION_SERVER`

| Environment | Typical value |
|-------------|---------------|
| Local server | `http://localhost:3001` |
| Docker (catalog agents) | `http://host.docker.internal:3001` |
| Hosted | `https://meserver.ecosystem.ai` |

Configure in `agents/.env` / `agents/.env.example` and `agents/docker-compose.yml`.
When unset, clients default to `http://localhost:3001`.

## Unauthenticated REST endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/modeling/ontology/validation/metadata` | Standards, rule catalog, recommendation schema |
| `POST` | `/modeling/ontology/validate` | Validate raw / catalog / inline content |
| `POST` | `/modeling/ontology/recommendations/apply` | Apply selected TTL recommendations |
| `GET` | `/modeling/domains/{domainId}/validate` | Validate a bundled catalog domain |

### Example: validate Turtle

```bash
curl -s -X POST "$ONTOLOGY_VALIDATION_SERVER/modeling/ontology/validate" \
  -H 'Content-Type: application/json' \
  -d '{"inputMode":"raw","format":"ttl","content":"@prefix : <https://ex#> . @prefix owl: <http://www.w3.org/2002/07/owl#> . <https://ex#> a owl:Ontology . :A a owl:Class .","includeRecommendations":true}'
```

### Example: metadata discovery

```bash
curl -s "$ONTOLOGY_VALIDATION_SERVER/modeling/ontology/validation/metadata"
```

## MCP tools (ecosystem-server)

- `get_ontology_validation_metadata`
- `validate_ontology` — accepts `ontology_content`, `shapes_content`, `domain_id`, or `project_id`
- `apply_ontology_recommendations` — stateless or project-scoped patches

## Catalog agent proxy (`ONTOLOGY_VALIDATION_SERVER`)

The catalog agent exposes the same capabilities under `/catalog`:

- `GET /v1/ontologies/validation/metadata`
- `POST /v1/ontologies/validate`
- `POST /v1/ontologies/recommendations/apply`

Shared client: `agents/shared/validation_client.py` (remote first, local pyoxigraph/rdflib fallback).

## Rule IDs

| Prefix | Aspect |
|--------|--------|
| `SYN-*` | RDF 1.2 / Turtle / OWL/XML syntax |
| `OWL-*` | OWL 2 structure (header, domain/range, cycles) |
| `SKOS-*` | prefLabel / definition / altLabel coverage |
| `SHACL-*` | NodeShapes, targetClass, path, minCount, sh:in, sh:or |
| `ROLE-*` | BFO role (`bfo:0000023`) Bearer / Permissions |
| `ALIGN-*` | Core vocabulary alignment suggestions |

## Recommendation schema

Each recommendation includes `id`, `ruleId`, `category`, `severity`, `subject`, `title`,
`rationale`, `actionType` (`add_triples` | `add_shacl_shape` | `confirm_role` |
`add_diagram_element` | `fix_syntax`), `suggestedTtl`, and `autoApplicable`.

## CLI

```bash
./tools/validate-ontology.py --catalog
./tools/validate-ontology.py path/to/custom.ttl --shapes path/to/shapes.ttl --json
./tools/validate-ontology.py --catalog --remote   # uses ONTOLOGY_VALIDATION_SERVER
```

`tools/validate-catalog.sh` invokes `validate-ontology.py --catalog` after structural checks.
