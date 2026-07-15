# Changelog

All notable catalog-wide changes are recorded here. Per-domain SemVer lives in `index.json`.

## [1.1.0] — 2026-07-15

Public collaboration refresh and domain coverage release. All domain entries in `index.json`
are aligned to **version `1.1.0`**.

### Added

- Public collaboration docs: `LICENSE` (Apache-2.0, Copyright 2026 Ecogenetic LLC),
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `GOVERNANCE.md`, GitHub PR/issue templates
- Published design package under `meta-data/` for external product consumers
- Industry overlay for every domain (≥1 industry per domain)
- Validator rules: SemVer format for `version`; `industries` length ≥ 1

### Changed

- README repositioned for ontology / taxonomy / KG specialists
- AGENTS.md and playbooks updated for manifest SemVer policy and public PR titles
- All domain `index.json` versions set to `1.1.0` for this release
- Removed downstream consumer / server-sync instructions from this repo (sync is owned by
  consuming product build pipelines)
