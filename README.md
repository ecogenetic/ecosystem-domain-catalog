# ecosystem-domain-catalog

A **living catalog** of business-domain descriptions and seed ontologies: controlled
vocabulary (domain language), OWL/SKOS (RDF Turtle), and SHACL completeness shapes —
with industry overlays for banking, insurance, telco, healthcare, and gambling.

Built for **ontologists, taxonomists, knowledge-graph engineers, and domain experts**.
External products consume the same structure and headings; the published contract lives
in [`meta-data/`](meta-data/).

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## Why contribute

- Improve SKOS synonyms and definitions for existing classes
- Propose industry overlays that encode real regulatory and terminology differences
- Raise SHACL completeness where generated models need mandatory properties
- Add a missing business domain with a full seed ontology

See [CONTRIBUTING.md](CONTRIBUTING.md) and [meta-data/extension-approaches.md](meta-data/extension-approaches.md).

## Standards stack

| Layer | Technology | Location |
|-------|------------|----------|
| Domain language | Markdown (7 sections) | `domains/{id}/description.md` |
| Vocabulary | OWL + SKOS (Turtle) | `domains/{id}/ontology.ttl` |
| Completeness | SHACL | `domains/{id}/shapes.ttl` |
| Industry specialization | Add-only overlays | `domains/{id}/industries/{industry}/` |
| Shared industry concepts | Turtle + Markdown | `industries/{industry}/` |
| Discovery | JSON manifests | `index.json`, `industries.json` |

Design rules for integrators: **[meta-data/](meta-data/)**. Structural contract for agents/CI: **[AGENTS.md](AGENTS.md)**.

## Repository layout

```text
domains/{id}/           description.md · ontology.ttl · shapes.ttl · industries/…
industries/{id}/        industry.md · common.ttl
playbooks/              extension procedures
tools/validate-catalog.sh
meta-data/              published design rules (external products)
index.json · industries.json
```

## Domain language (seven headings)

1. Concepts · 2. Taxonomy · 3. Relationships · 4. Attributes · 5. Lifecycle · 6. Roles · 7. Primary workflow  

Details: [meta-data/domain-language.md](meta-data/domain-language.md).

## Validation

```bash
./tools/validate-catalog.sh
```

Must pass before every commit. Enforces structure, SKOS/SHACL minimums, SemVer format,
and **at least one industry overlay per domain**.

## Playbooks

- [playbooks/add-domain.md](playbooks/add-domain.md)
- [playbooks/extend-domain.md](playbooks/extend-domain.md)
- [playbooks/add-industry.md](playbooks/add-industry.md)
- [playbooks/add-industry-overlay.md](playbooks/add-industry-overlay.md)

## Downstream consumers (secondary)

One consumer is [EcosystemCode](https://ecosystemcode.com): after merge to `main`, maintainers
sync a snapshot into `ecosystem-server` (see CI workflow `sync-to-server.yml`). Catalog
contributors do not need that repo for catalog-only PRs.

```bash
# Maintainer sync (after merge)
cd ../ecosystem-server && ./scripts/sync-domain-catalog.sh
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
