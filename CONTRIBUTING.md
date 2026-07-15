# Contributing to ecosystem-domain-catalog

Thank you for helping curate business-domain seed ontologies. This catalog is a
**living library** of domain language (Markdown), OWL/SKOS (Turtle), and SHACL
completeness shapes — used by specialists and by external products.

## Who we want

- **Ontologists / knowledge-graph engineers** — OWL, SKOS, SHACL, IRI discipline
- **Taxonomists / domain experts** — accurate concepts, synonyms, industry notes
- **Practitioners** — overlays and completeness that match real systems

## Before you start

1. Read [meta-data/README.md](meta-data/README.md) (published design rules).
2. Read [AGENTS.md](AGENTS.md) (normative structure enforced by CI).
3. Follow the matching playbook under [playbooks/](playbooks/).
4. Agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Contribution types

| Type | Playbook |
|------|----------|
| New domain | [playbooks/add-domain.md](playbooks/add-domain.md) |
| Extend domain | [playbooks/extend-domain.md](playbooks/extend-domain.md) |
| New industry | [playbooks/add-industry.md](playbooks/add-industry.md) |
| Industry overlay | [playbooks/add-industry-overlay.md](playbooks/add-industry-overlay.md) |

## Hard rules

- Stable IRIs; deprecate, do not delete.
- Overlays are add-only.
- No `TODO` / `TBD` / `PLACEHOLDER` / `FIXME`.
- Every domain has **≥1 industry** overlay listed in `index.json`.
- Any change under `domains/{id}/` updates that domain’s `index.json` entry in the
  **same PR** (SemVer bump + seed fields). See [meta-data/manifest-schema.md](meta-data/manifest-schema.md).
- `./tools/validate-catalog.sh` must exit 0.

## Modeling principles (summary)

Full detail: [meta-data/](meta-data/).

- Prefer clear, non-overlapping concepts with real `skos:altLabel` synonyms.
- Relationships use `Subject verb Object (cardinality)`.
- SHACL is the completeness contract — raising `minCount` on existing concepts is MAJOR.
- Industry/regulatory language belongs in overlays and `industry.md`.

## PR titles

See [meta-data/extension-approaches.md](meta-data/extension-approaches.md). Examples:

- `feat(domain): extend crm — pipeline stages`
- `feat(overlay): erp/banking — GL cost centres`
- `docs: clarify SHACL completeness`

## After merge

Catalog CI validates on every PR. Downstream product builds pull this catalog on their own
schedules — catalog contributors do not need access to sibling application repositories.

## License

Contributions are under the [Apache License 2.0](LICENSE).
Copyright 2026 Ecogenetic LLC.
