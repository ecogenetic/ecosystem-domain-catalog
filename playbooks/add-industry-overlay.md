# Playbook: Add an industry overlay

Prompt-style procedure. Overlays are **add-only** — see [AGENTS.md](../AGENTS.md) section 8
and [meta-data/industry-overlays.md](../meta-data/industry-overlays.md).

## Inputs

- Domain id and industry id (industry must exist in `industries.json`).
- Additional concepts, relationships, roles, and regulatory notes for that vertical.

## Steps

1. Create `domains/{domainId}/industries/{industryId}/overlay.md` with additive sections only
   (Additional concepts / relationships / roles / Regulatory notes).
2. Create `overlay.ttl` with overlay namespace
   `https://ecosystemcode.com/ontology/{domainId}/{industryId}#`, importing the base domain
   prefix. Add classes/properties/roles/shapes; never redefine base IRIs.
3. Append `{industryId}` to the domain’s `industries` array in `index.json` and bump `version`
   (MINOR). Refresh capability/workflow text if the industry story changes the pitch.
4. Run `./tools/validate-catalog.sh` until exit 0.
5. PR titled `feat(overlay): {domainId}/{industryId} — {short}`.
