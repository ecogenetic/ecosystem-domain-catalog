# Playbook: Extend an existing domain (add concepts / relationships / attributes)

Prompt-style procedure for adding to a domain **without breaking published structure**.
Read [AGENTS.md](../AGENTS.md) section 2 (invariants) before starting.

## Rules

- **Never rename or remove** an existing class, property, or shape (stable IRIs).
  To retire a term: mark it `owl:deprecated true` and add the replacement alongside.
- New concepts/properties follow the exact templates in AGENTS.md sections 4–5.
- Keep `description.md` and `ontology.ttl` in step: every new class gets a Concepts bullet;
  every new object property gets a Relationships line (`Subject verb Object (cardinality)`).

## Steps

1. Add the new `**Concept**` bullets to the domain's `description.md` Concepts section, and
   new lines to Taxonomy / Relationships / Attributes / Roles sections as applicable.
2. Add the matching `owl:Class` (with SKOS labels + definition) and
   `owl:ObjectProperty`/`owl:DatatypeProperty` declarations to `ontology.ttl`.
3. If the new concept is required for a complete model, add or extend a `sh:NodeShape`
   in `shapes.ttl`. Only strengthen shapes for NEW concepts — do not add new constraints
   to existing concepts unless the domain owner agrees (it changes completeness reports
   for existing projects).
4. If the concept should be a wizard seed entity, append it to the domain's `entities`
   in `index.json` and bump the entry's `version` (minor bump, e.g. 1.0.0 → 1.1.0).
5. Run `./tools/validate-catalog.sh` until it exits 0.
6. PR titled `Extend domain: {ACRONYM} — {summary}`. After merge, sync into
   ecosystem-server per the README.
