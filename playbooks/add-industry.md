# Playbook: Register a new industry

Prompt-style procedure. See [AGENTS.md](../AGENTS.md) section 7 and [meta-data/industry-overlays.md](../meta-data/industry-overlays.md).

## Steps

1. Create `industries/{industryId}/industry.md` (terminology + regulatory notes) and
   `common.ttl` (shared industry concepts; namespace
   `https://ecosystemcode.com/ontology/industry/{industryId}#`).
2. Add the entry to `industries.json`.
3. Run `./tools/validate-catalog.sh`.
4. PR titled `feat(industry): add {industryId}`.
5. Follow [add-industry-overlay.md](add-industry-overlay.md) to attach the industry to at least
   one domain (domains must keep `industries.length ≥ 1`).
