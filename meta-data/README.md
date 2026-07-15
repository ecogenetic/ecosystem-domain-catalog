# Catalog meta-data (for external products)

This directory publishes the **design rules and approaches** of the ecosystem-domain-catalog
so external products can consume domain language, ontologies, and manifests consistently.

It does **not** duplicate domain content. Domain assets live under `domains/` and `industries/`.
The structural contract enforced by agents and CI is [AGENTS.md](../AGENTS.md); this package
explains the same rules for product integrators and specialists.

## Documents

| File | Audience | Contents |
|------|----------|----------|
| [domain-language.md](domain-language.md) | All consumers | Seven required headings and line formats |
| [ontology-conventions.md](ontology-conventions.md) | Ontology / KG engineers | OWL, SKOS, Turtle namespaces, IRI stability, BFO roles |
| [shacl-completeness.md](shacl-completeness.md) | Model validators | SHACL as completeness contract; base vs overlay shapes |
| [industry-overlays.md](industry-overlays.md) | Domain + industry authors | Add-only overlay contract and required files |
| [manifest-schema.md](manifest-schema.md) | Product / API integrators | `index.json` / `industries.json` fields and SemVer |
| [extension-approaches.md](extension-approaches.md) | Contributors / maintainers | When to extend, overlay, or add a domain |

## How products should consume the catalog

1. Discover domains from `index.json` (id, version, entities, industries, prompt seeds).
2. Load `domains/{id}/description.md` for the domain language (seven sections).
3. Load `domains/{id}/ontology.ttl` (OWL + SKOS) and optionally `shapes.ttl` (SHACL).
4. If an industry is selected, append `domains/{id}/industries/{industry}/overlay.md` and merge `overlay.ttl` additively; also read `industries/{industry}/industry.md` and `common.ttl`.
5. Treat published IRIs as stable. Never rename; deprecate with `owl:deprecated true`.

## Versioning

Each domain entry in `index.json` carries its own SemVer `version`. See [manifest-schema.md](manifest-schema.md).
Catalog releases are also noted in the root [CHANGELOG.md](../CHANGELOG.md).
