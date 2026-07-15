# Manifest schema and SemVer

## `index.json` domain entry

All fields required:

| Field | Meaning |
|-------|---------|
| `id` | Lowercase domain id (folder name under `domains/`) |
| `acronym` | Short display acronym |
| `name` | Full domain name |
| `description` | Short blurb |
| `icon` | Lucide-react icon component name (UI consumers) |
| `chips` | 2–3 headline concept names for UI |
| `entities` | Seed classes for generation; each must appear in description + ontology |
| `capability` | Prompt seed: what the system does |
| `benefit` | Prompt seed: outcome for users |
| `workflow` | Prompt seed: primary flow text |
| `statefulEntity` | Prompt seed: which entity carries lifecycle |
| `industries` | Industry ids with overlays; **length ≥ 1** |
| `hasDescription` / `hasOntology` / `hasShapes` | Asset flags (true for published domains) |
| `version` | Domain SemVer string `MAJOR.MINOR.PATCH` |

## SemVer rules (per domain `version`)

| Change | Bump |
|--------|------|
| First publish of a domain | `1.0.0` |
| Additive concepts, properties, overlays, richer language, new industries in list | **MINOR** |
| Breaking completeness (new required SHACL on existing concepts; remove/rename seed entity) | **MAJOR** |
| Typos / wording-only in description with no structural change | **PATCH** |

**Mandatory:** any change under `domains/{id}/` MUST update that domain’s `index.json` entry
in the same PR, including an appropriate version bump and refreshed
`entities` / `chips` / `capability` / `benefit` / `workflow` / `statefulEntity` / `industries`
when those stories change.

Docs-only repo changes (README, `meta-data/`, CONTRIBUTING) do not bump domain versions.

## `industries.json`

| Field | Meaning |
|-------|---------|
| `id` | Industry id (folder under `industries/`) |
| `label` | Display label |
| `description` | Short industry description |

## Validation

`./tools/validate-catalog.sh` enforces field presence, SemVer format, entities↔ontology↔description,
and industries↔overlay folders. CI runs it on every PR.
