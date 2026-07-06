# Playbook: Add an industry overlay to a domain

Prompt-style procedure for specializing an existing domain for an existing industry
(e.g. CRM × telco). Overlays are **add-only** — read AGENTS.md section 8 first.

## Preconditions

- The domain exists under `domains/{domainId}/` and the industry is registered in
  `industries.json` with an `industries/{industryId}/` folder.
- There are real concept-level differences to model. If the industry only changes wording,
  prefer adding `skos:altLabel` synonyms instead of an overlay.

## Steps

1. Create `domains/{domainId}/industries/{industryId}/` with two files:
   - `overlay.md` — additive description sections only (extra **Concepts**, **Relationships**,
     **Roles**, and optional **Regulatory notes**), same line formats as AGENTS.md section 3.
     This text is appended AFTER the base description at generation time — do not repeat
     base content.
   - `overlay.ttl` — namespace `https://ecosystemcode.com/ontology/{domainId}/{industryId}#`.
     May reference base-domain IRIs (`https://ecosystemcode.com/ontology/{domainId}#...`) and
     industry-common IRIs (`https://ecosystemcode.com/ontology/industry/{industryId}#...`) in
     full. Allowed: new classes (optionally `rdfs:subClassOf` base classes), new properties
     over base classes, `skos:altLabel` additions, new SHACL shapes. Forbidden: redefining,
     renaming, removing, or relaxing anything from the base.
2. Add `{industryId}` to the domain's `industries` array in `index.json` and bump the
   entry's `version` (minor bump).
3. Run `./tools/validate-catalog.sh` until it exits 0.
4. PR titled `Overlay: {DOMAIN} × {industry}`. After merge, sync into ecosystem-server
   per the README.

## Example (CRM × telco)

`overlay.ttl` adds `:Subscriber rdfs:subClassOf <https://ecosystemcode.com/ontology/crm#Contact>`,
`:RatePlan`, an `:msisdn` datatype property on `:Subscriber`, and a shape requiring every
Subscriber to have an msisdn. `overlay.md` adds the corresponding Concepts/Relationships lines.
