# Governance

## Maintainers

Maintainers of [ecogenetic/ecosystem-domain-catalog](https://github.com/ecogenetic/ecosystem-domain-catalog)
decide merges to `main`, release tagging, and downstream snapshot syncs.

## Decision rules

1. **Stable IRIs** — published class/property IRIs are never renamed or removed without
   deprecation (`owl:deprecated true`) and maintainer approval.
2. **Overlays are add-only** — industry overlays must not redefine base terms.
3. **Every domain has ≥1 industry** — `index.json` `industries` must be non-empty; overlays required.
4. **Manifest sync** — domain content PRs must bump SemVer and refresh seed fields (see `meta-data/manifest-schema.md`).
5. **Validate** — `./tools/validate-catalog.sh` must pass before merge.

## Breaking changes

MAJOR version bumps (required SHACL tightening, seed entity removal) require explicit
maintainer approval in the PR.

## Contribution path

Public specialists contribute via pull requests under [CONTRIBUTING.md](CONTRIBUTING.md).
Agents and automation must follow [AGENTS.md](AGENTS.md).
