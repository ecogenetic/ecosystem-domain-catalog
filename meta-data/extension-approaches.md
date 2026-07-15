# Extension approaches

## Choose the right change

| Goal | Approach | Playbook |
|------|----------|----------|
| New business system type | Add a domain | [playbooks/add-domain.md](../playbooks/add-domain.md) |
| Richer base vocabulary | Extend domain (add-only IRIs) | [playbooks/extend-domain.md](../playbooks/extend-domain.md) |
| New vertical | Register industry | [playbooks/add-industry.md](../playbooks/add-industry.md) |
| Specialize a domain for a vertical | Industry overlay | [playbooks/add-industry-overlay.md](../playbooks/add-industry-overlay.md) |

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
