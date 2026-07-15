# Playbook: Add a new domain

Prompt-style procedure. Follow every step in order; do not skip the validation steps.
All templates referenced here are in [AGENTS.md](../AGENTS.md) — do not improvise formats.
Design rules for external products: [meta-data/](../meta-data/).

## Inputs you need before starting

- Domain id (lowercase, short, e.g. `prm`), acronym (e.g. `PRM`), full name.
- 5–10 core concepts (these become the seed `entities`).
- The primary workflow (4–6 steps) and the stateful entity with its lifecycle states.
- The roles that operate the system (bearer person or organisation, permissions).
- At least one industry id for the first overlay (banking, insurance, telco, healthcare, gambling).
- A lucide-react icon name (for UI consumers).

## Steps

1. Create `domains/{id}/` with exactly three files:
   - `description.md` per AGENTS.md section 3 — all seven sections, non-empty and complete.
     Every concept you list in the manifest `entities` MUST appear as a `**Concept**` bullet.
   - `ontology.ttl` per AGENTS.md section 4 — namespace
     `https://ecosystemcode.com/ontology/{id}#`; every entity as `owl:Class` with
     `skos:prefLabel` + `skos:definition` (+ `skos:altLabel` synonyms); at least 4 object
     properties with `rdfs:domain`/`rdfs:range`; datatype properties for key attributes;
     a `...Status` datatype property for the stateful entity; at least one `{X}Role` class
     under `bfo:0000023`.
   - `shapes.ttl` per AGENTS.md section 5 — a `sh:NodeShape` per core concept; required
     relationships/attributes as `sh:minCount 1`; the stateful entity's `...Status`
     constrained with `sh:in ( ...states... )`.
2. Create at least one industry overlay under `domains/{id}/industries/{industry}/`
   (`overlay.md` + `overlay.ttl`) per [add-industry-overlay.md](add-industry-overlay.md).
3. Add the manifest entry to `index.json` (AGENTS.md section 6 — every field filled,
   `industries: ["{industry}"]` with length ≥ 1, all three `has*` flags true, `version: "1.0.0"`).
4. Run `./tools/validate-catalog.sh`. Fix every reported issue and re-run until it exits 0.
5. Commit on a branch, open a PR. Title: `feat(domain): add {ACRONYM} — {Full Name}`.
6. After merge, maintainers sync into consuming products (e.g. ecosystem-server). Catalog-only
   contributors stop after a green validate PR.

### Maintainer follow-up (optional)

- Sync snapshot: `cd ../ecosystem-server && ./scripts/sync-domain-catalog.sh`
- Static UI seed (if needed): mirror id/entities in the modeling app wizard config
