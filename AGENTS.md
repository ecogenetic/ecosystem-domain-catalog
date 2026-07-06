# AGENTS.md — Canonical Structural Contract

This repository is the **ecosystem-domain-catalog**: the source of truth for business-domain
descriptions and seed ontologies consumed by EcosystemCode (ecosystem-server) for model and
code generation. It is a **living catalog** — domains, concepts, and industries are extended
over time via PR.

Any agent or human extending this catalog MUST follow the structures below exactly.
`tools/validate-catalog.sh` enforces this same contract and MUST pass before every commit.
If you change the contract here, change the validator in the same commit — they must not diverge.

---

## 1. Repository tree

```text
ecosystem-domain-catalog/
  README.md                # human authoring guide
  AGENTS.md                # this file — canonical structural contract
  CLAUDE.md                # pointer to AGENTS.md
  index.json               # domain manifest (schema in section 6)
  industries.json          # industry registry (schema in section 7)
  playbooks/               # step-by-step extension procedures
    add-domain.md
    add-industry.md
    add-industry-overlay.md
    extend-domain.md
  tools/
    validate-catalog.sh    # structural validator — run before every commit
  industries/
    {industryId}/
      industry.md          # cross-domain industry context (terminology, regulatory notes)
      common.ttl           # shared industry concepts reused across domain overlays
  domains/
    {domainId}/
      description.md       # domain language (section 3)
      ontology.ttl         # OWL + SKOS Turtle (section 4)
      shapes.ttl           # SHACL shapes (section 5)
      industries/          # OPTIONAL industry overlays
        {industryId}/
          overlay.md       # description addendum appended after the base description
          overlay.ttl      # extends the base ontology — add-only (section 8)
```

Required files per domain: `description.md`, `ontology.ttl`, `shapes.ttl` — no exceptions.
Domain ids are lowercase (e.g. `crm`, `fms`) and MUST match the wizard's `WIZARD_DOMAINS` ids
and an entry in `index.json`.

## 2. Invariants (never break these)

1. **Stable IRIs**: once published, a class or property IRI is never renamed or removed.
   Deprecate with `owl:deprecated true` and add a replacement instead.
2. **Namespace pattern**: `https://ecosystemcode.com/ontology/{domainId}#` for domains,
   `https://ecosystemcode.com/ontology/industry/{industryId}#` for industries.
3. **No placeholders**: `TODO`, `TBD`, `PLACEHOLDER`, `FIXME`, or empty sections fail validation.
4. **Overlays are add-only** (section 8): they never redefine or remove base terms.
5. **Validate before commit**: `./tools/validate-catalog.sh` must exit 0.
6. **Sync after merge**: run `scripts/sync-domain-catalog.sh` in ecosystem-server and commit
   the snapshot there (see README "Sync workflow").

## 3. `description.md` skeleton (all seven sections required, non-empty)

```markdown
# {ACRONYM} — {Full Name}

One-paragraph summary of what this system does and for whom.

## Concepts

- **{Concept}** — one-line definition.
- (one bullet per concept; every seed entity in index.json `entities` MUST appear)

## Taxonomy

- {Concept} is a kind of {SuperConcept}.

## Relationships

- {Subject} {verb} {Object} (one-to-many | many-to-one | one-to-one | many-to-many)

## Attributes

- {Concept}: {attribute} ({type}), {attribute} ({type})

## Lifecycle

- {StatefulConcept}: state1 → state2 → state3 | terminalAlt

## Roles

- **{RoleName}** (bearer: person | organisation) — what they do; permissions: {Entity}:read, {Entity}:write

## Primary workflow

{Step 1} → {Step 2} → {Step 3} → {Step 4}
```

Relationship lines MUST follow `Subject verb Object (cardinality)` so they can be parsed.

## 4. `ontology.ttl` template (OWL + SKOS)

Required prefixes and ontology header:

```turtle
@prefix : <https://ecosystemcode.com/ontology/{domainId}#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix bfo:  <http://purl.obolibrary.org/obo/BFO_> .

<https://ecosystemcode.com/ontology/{domainId}> a owl:Ontology ;
    rdfs:label "{ACRONYM} Domain Ontology" ;
    rdfs:comment "{one-line purpose}" .
```

Class pattern — every class MUST carry `skos:prefLabel` and `skos:definition`
(`skos:altLabel` synonyms strongly encouraged):

```turtle
:Account a owl:Class ;
    skos:prefLabel "Account" ;
    skos:altLabel "Customer Account", "Client" ;
    skos:definition "An organisation the business sells to." .
```

Taxonomy uses `rdfs:subClassOf` between classes.

Object property pattern — every object property MUST have `rdfs:domain` and `rdfs:range`;
use a distinct property name per relationship (no overloading):

```turtle
:belongsToAccount a owl:ObjectProperty ;
    rdfs:label "belongs to account" ;
    rdfs:domain :Contact ;
    rdfs:range  :Account ;
    skos:definition "Associates a contact with the account they work for." .
```

Datatype property pattern:

```turtle
:amount a owl:DatatypeProperty ;
    rdfs:label "amount" ;
    rdfs:domain :Opportunity ;
    rdfs:range  xsd:decimal .
```

Stateful entities get a `...Status` datatype property (`xsd:string`); the allowed states are
constrained in `shapes.ttl`, not in the ontology.

Role pattern — role classes are named `{Something}Role` AND subclassed under the BFO role
branch so the server's `semanticKind=role` detection and rolePolicies extraction work:

```turtle
:SalesRepRole a owl:Class ;
    rdfs:subClassOf bfo:0000023 ;
    skos:prefLabel "Sales Rep" ;
    skos:definition "Person role that owns leads and opportunities. Bearer: person. Permissions: Opportunity:read, Opportunity:write." .
```

Minimum content per domain: every seed entity from `index.json entities[]` as an `owl:Class`;
at least 4 object properties with domain and range; at least one role class.

## 5. `shapes.ttl` template (SHACL)

```turtle
@prefix :    <https://ecosystemcode.com/ontology/{domainId}#> .
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:OpportunityShape a sh:NodeShape ;
    sh:targetClass :Opportunity ;
    sh:property [
        sh:path :belongsToAccount ;
        sh:class :Account ;
        sh:minCount 1 ;
    ] ;
    sh:property [
        sh:path :opportunityStatus ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:in ( "lead" "qualified" "proposal" "won" "lost" ) ;
    ] .
```

Minimum content per domain: at least one `sh:NodeShape` per core concept, at least one
`sh:minCount` constraint overall, and the domain's stateful entity MUST have its
`...Status` property constrained with `sh:in ( ...states... )`.

## 6. `index.json` entry schema (all fields required)

```json
{
  "id": "crm",
  "acronym": "CRM",
  "name": "Customer Relationship Management",
  "description": "Customer Relationship Management",
  "icon": "Users",
  "chips": ["Contact", "Account", "Opportunity"],
  "entities": ["Contact", "Account", "Opportunity", "Pipeline", "Activity", "Lead"],
  "capability": "capture leads, manage accounts and contacts, and progress opportunities through pipeline stages",
  "benefit": "sales teams share one forecastable view of every customer relationship",
  "workflow": "Capture lead → qualify → open opportunity → log activities → close won or lost",
  "statefulEntity": "Opportunity (pipeline stages: lead → qualified → proposal → won/lost)",
  "industries": [],
  "hasDescription": true,
  "hasOntology": true,
  "hasShapes": true,
  "version": "1.0.0"
}
```

`icon` is a lucide-react icon component name. `industries` lists industry ids that have an
overlay folder for this domain. Every `domains/{id}/` folder must have a manifest entry and
vice versa.

## 7. `industries.json` entry schema

```json
{
  "id": "banking",
  "label": "Banking",
  "description": "Retail and commercial banking: accounts, lending, payments, KYC and regulatory compliance."
}
```

Every `industries/{id}/` folder must have a registry entry and vice versa. Each industry
folder requires `industry.md` and `common.ttl` (same class/property patterns as section 4,
namespace `https://ecosystemcode.com/ontology/industry/{industryId}#`).

## 8. Industry overlay contract (add-only)

Overlays specialize a base domain for an industry. They MAY:

- add new classes, optionally `rdfs:subClassOf` a base class (import base terms by full IRI);
- add new object/datatype properties whose domain/range may reference base classes;
- add SKOS `altLabel` synonyms to base classes;
- add new SHACL shapes or property constraints (in `overlay.ttl`, same file).

They MUST NOT redefine, rename, remove, or relax any base class, property, or shape.
`overlay.md` contains only additive description sections (extra Concepts / Relationships /
Roles / regulatory notes) appended after the base description at generation time.

## 9. Workflow for any extension

1. Read the relevant playbook in `playbooks/`.
2. Author files exactly per the templates above.
3. Add/update the manifest entry (`index.json` or `industries.json`).
4. Run `./tools/validate-catalog.sh` — fix everything it reports.
5. Commit via PR. After merge, sync into ecosystem-server per README.
