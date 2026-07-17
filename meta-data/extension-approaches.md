# Extension approaches

## Choose the right change

| Goal | Approach | Playbook |
|------|----------|----------|
| New business system type | Add a domain | [playbooks/add-domain.md](../playbooks/add-domain.md) |
| Richer base vocabulary | Extend domain (add-only IRIs) | [playbooks/extend-domain.md](../playbooks/extend-domain.md) |
| New vertical | Register industry | [playbooks/add-industry.md](../playbooks/add-industry.md) |
| Specialize a domain for a vertical | Industry overlay | [playbooks/add-industry-overlay.md](../playbooks/add-industry-overlay.md) |
| Share an entity across domains (multi-domain composition) | Core alignment (add-only triples in `core/alignments.ttl`) | [playbooks/add-alignment.md](../playbooks/add-alignment.md) |

## Multi-domain composition

When a consumer combines more than one domain (e.g. CRM + CVM), shared real-world
entities must resolve to **one canonical entity**, never duplicated. The catalog supports
this with two files that are loaded only in multi-domain mode:

- `core/ontology.ttl` — a domain-neutral common-entity vocabulary (Party, Customer,
  Product, Order, Invoice, Payment, ...) with stable IRIs under
  `https://ecosystemcode.com/ontology/core#`.
- `core/alignments.ttl` — curated triples linking domain class IRIs to core classes:
  `owl:equivalentClass` collapses classes into one canonical entity (e.g. `crm:Account`
  and `cvm:Customer` both become **Customer**); `rdfs:subClassOf` keeps a domain class
  distinct but linked to its canonical parent.

Domain ontologies stay byte-for-byte unchanged — alignments are statements about IRIs
defined elsewhere. Homonyms / false friends (e.g. `crm:Account` customer organisation vs
`fin:Account` financial account) get **no** triple and are documented in the
false-friends block. Single-domain generation never loads either file.

## Review bar (specialists)

- Definitions are clear and non-overlapping.
- `skos:altLabel` synonyms are real usage terms, not noise.
- Cardinalities and lifecycles are honest.
- Regulatory notes belong in industry overlays / `industry.md`, not as fake base concepts.
- Overlays never silently redefine base terms.
- `index.json` version bumped and seed fields synced in the same PR.

## PR title conventions

| Type | Title pattern |
|------|----------------|
| New domain | `feat(domain): add {ACRONYM} — {Full Name}` |
| Extend domain | `feat(domain): extend {id} — {short change}` |
| Industry | `feat(industry): add {industryId}` |
| Overlay | `feat(overlay): {domainId}/{industryId} — {short}` |
| Docs / meta-data | `docs: …` |

## After merge

Catalog CI validates. Downstream products refresh their snapshots in **their** build pipelines.
