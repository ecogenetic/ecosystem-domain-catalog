# Industry overlays (add-only)

Industries specialize a base domain without forking it.

## Layout

```text
industries/{industryId}/
  industry.md          # cross-domain terminology + regulatory notes
  common.ttl           # shared industry concepts

domains/{domainId}/industries/{industryId}/
  overlay.md           # additive description sections
  overlay.ttl          # additive OWL + optional SHACL shapes
```

Every domain MUST list at least one industry in `index.json` `industries[]`, and each listed
id MUST have a matching overlay folder (and vice versa). Industry ids MUST exist in
`industries.json`.

## Overlay.md

Contains only additive sections, typically:

- Additional concepts
- Additional relationships
- Additional roles
- Regulatory notes

Do not rewrite base Concepts or delete base relationships.

## Overlay.ttl

MAY:

- add classes (optionally `rdfs:subClassOf` a base class via the domain prefix)
- add object/datatype properties
- add SKOS altLabels
- add SHACL NodeShapes

MUST NOT redefine, rename, remove, or relax base classes, properties, or shapes.

## Starter industries

`banking`, `insurance`, `telco`, `healthcare`, `gambling` (gaming & gambling).
