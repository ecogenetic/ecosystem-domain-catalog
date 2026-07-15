## Contribution type
- [ ] New domain
- [ ] Extend domain
- [ ] New industry
- [ ] Industry overlay
- [ ] Docs / meta-data / CI

## Checklist
- [ ] Read `meta-data/` design rules and the matching playbook
- [ ] `./tools/validate-catalog.sh` passes locally
- [ ] Stable IRIs (no renames/removals; overlays add-only)
- [ ] SKOS `prefLabel` + `definition` on new classes; SHACL DoD met if shapes changed
- [ ] **`index.json` updated** for every touched domain: SemVer bump + entities/chips/workflow/industries as needed
- [ ] Domain still has **≥1 industry** in `industries[]` with matching overlay folders

## Summary

<!-- What changed and why -->
