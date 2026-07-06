# ecosystem-domain-catalog

The **living catalog** of business-domain descriptions and seed ontologies consumed by
[EcosystemCode](https://ecosystemcode.com) (ecosystem-server) to enrich UML model generation
and code generation. When a user selects a domain acronym (CRM, ERP, CVM, ...) in the
EcosystemCode Project Wizard, the server uses this catalog's domain description and ontology
to ground and complete what gets generated.

**This catalog is extended over time.** New domains, new concepts within existing domains,
and new industry overlays are added via PR. Once synced into ecosystem-server, new domains
appear automatically in the EcosystemCode wizard.

## What each domain contains

| File | Purpose | Consumed for |
|------|---------|--------------|
| `domains/{id}/description.md` | The domain language: Concepts, Taxonomy, Relationships, Attributes, Lifecycle, Roles, Primary workflow | Prompt enrichment for model + code generation |
| `domains/{id}/ontology.ttl` | OWL classes/properties with SKOS labels, synonyms, definitions (RDF Turtle) | Seed ontology → `ontologyContext` on the project |
| `domains/{id}/shapes.ttl` | SHACL shapes: required properties, cardinalities, allowed lifecycle states | Completeness validation of generated models |

Industry variability is handled by **add-only overlays** under `domains/{id}/industries/{industry}/`
plus shared industry concepts under `industries/{industry}/` — base domains stay industry-neutral.
Starter industries: banking, insurance, telco, healthcare, gambling (gaming & gambling).

## The domain language (template)

Every `description.md` has seven sections — see [AGENTS.md](AGENTS.md) section 3 for the
canonical skeleton and line formats:

1. **Concepts** — each core business object with a one-line definition
2. **Taxonomy** — is-a relationships
3. **Relationships** — `Subject verb Object (cardinality)`
4. **Attributes** — typed attributes per concept
5. **Lifecycle** — state chains for stateful entities
6. **Roles** — who acts, bearer (person/organisation), suggested permissions
7. **Primary workflow** — the main end-to-end flow

## Turtle conventions (worked example)

See [AGENTS.md](AGENTS.md) sections 4–5 for the full templates. In short:

```turtle
@prefix : <https://ecosystemcode.com/ontology/crm#> .

:Account a owl:Class ;
    skos:prefLabel "Account" ;
    skos:altLabel "Customer Account", "Client" ;
    skos:definition "An organisation the business sells to." .

:belongsToAccount a owl:ObjectProperty ;
    rdfs:domain :Contact ; rdfs:range :Account .

:SalesRepRole a owl:Class ;
    rdfs:subClassOf bfo:0000023 ;          # BFO role branch → detected as a role
    skos:prefLabel "Sales Rep" .
```

SHACL shapes (`shapes.ttl`) declare what a *complete* model must contain — required
relationships, attributes, and the allowed lifecycle states.

## Manifests

- `index.json` — one entry per domain: id, acronym, full name, wizard metadata (icon, chips,
  entities) and prompt seeds (capability, benefit, workflow, statefulEntity). Schema in
  [AGENTS.md](AGENTS.md) section 6.
- `industries.json` — the industry registry. Schema in [AGENTS.md](AGENTS.md) section 7.

## Validation

```bash
./tools/validate-catalog.sh
```

Checks every domain folder for the three required files, all seven description sections,
required ontology content (every manifest entity as a class, SKOS labels/definitions,
object properties with domain/range, a role class), SHACL minimums, manifest consistency
in both directions, and rejects placeholder markers. **Must pass before every commit.**

## Sync workflow into ecosystem-server

The server consumes a committed snapshot of this catalog from its classpath
(`src/main/resources/modeling/domains/`). After merging catalog changes:

```bash
cd ../ecosystem-server
./scripts/sync-domain-catalog.sh   # refuses dirty catalog checkout or failing validation
git add src/main/resources/modeling/domains && git commit -m "Sync domain catalog"
```

### Automatic sync (GitHub Actions)

`.github/workflows/sync-to-server.yml` runs on every push to `main`:

1. Validates the catalog (`tools/validate-catalog.sh`) — also runs on PRs as a gate.
2. Runs the server's sync script against a fresh `ecosystem-server` checkout.
3. Opens (or updates) a PR in `ecogenetic/ecosystem-server` on the
   `chore/sync-domain-catalog` branch containing the new snapshot.

**That PR is the reminder** that someone changed the catalog: review the diff under
`src/main/resources/modeling/domains/` and merge to ship it with the next server build.

One-time setup: add a repository secret named `ECOSYSTEM_SERVER_TOKEN` in this repo's
settings — a GitHub PAT with `repo` scope on `ecogenetic/ecosystem-server`.

Local/CI staleness check: `ecosystem-server/scripts/check-domain-catalog-sync.sh`
compares the bundled snapshot's `SYNC-INFO.json` commit with the catalog HEAD (local
checkout, or remote `main` when no checkout exists) and exits non-zero when the
snapshot is stale.

## Extending the catalog

Follow the step-by-step playbooks (agents: read [AGENTS.md](AGENTS.md) first):

- [playbooks/add-domain.md](playbooks/add-domain.md) — add a whole new domain
- [playbooks/extend-domain.md](playbooks/extend-domain.md) — add concepts/relationships to an existing domain
- [playbooks/add-industry.md](playbooks/add-industry.md) — register a new industry
- [playbooks/add-industry-overlay.md](playbooks/add-industry-overlay.md) — specialize a domain for an industry
