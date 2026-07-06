# Playbook: Add a new domain

Prompt-style procedure. Follow every step in order; do not skip the validation steps.
All templates referenced here are in [AGENTS.md](../AGENTS.md) — do not improvise formats.

## Inputs you need before starting

- Domain id (lowercase, short, e.g. `prm`), acronym (e.g. `PRM`), full name.
- 5–10 core concepts (these become the wizard seed `entities`).
- The primary workflow (4–6 steps) and the stateful entity with its lifecycle states.
- The roles that operate the system (bearer person or organisation, permissions).
- A lucide-react icon name for the wizard tile.

## Steps

1. Create `domains/{id}/` with exactly three files:
   - `description.md` per AGENTS.md section 3 — all seven sections, non-empty.
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
2. Add the manifest entry to `index.json` (AGENTS.md section 6 — every field filled,
   `industries: []`, all three `has*` flags true, `version: "1.0.0"`).
   Keep the array ordered to match the wizard domain order.
3. Run `./tools/validate-catalog.sh`. Fix every reported issue and re-run until it exits 0.
4. Commit on a branch, open a PR. Title: `Add domain: {ACRONYM} — {Full Name}`.
5. After merge, sync into ecosystem-server:
   `cd ../ecosystem-server && ./scripts/sync-domain-catalog.sh`, commit the snapshot,
   and verify the server test suite passes (`DomainCatalogServiceTest` iterates the
   synced directory automatically).
6. If the domain should appear as a *static* wizard tile (optional — synced domains appear
   dynamically), add it to `WIZARD_DOMAINS` in the ecosystem-modeling repo with matching
   id/acronym/entities.
