# SHACL completeness contract

`domains/{id}/shapes.ttl` declares what a **complete** model of the domain must contain.
Products that validate generated UML/class models against the catalog SHOULD treat these
shapes as the completeness baseline.

## Base shapes

- At least one `sh:NodeShape` targeting a core class.
- At least one `sh:minCount 1` constraint overall.
- The domain’s stateful entity status property constrained with `sh:in ( ...states... )`.

Example pattern:

```turtle
:OpportunityShape a sh:NodeShape ;
    sh:targetClass :Opportunity ;
    sh:property [
        sh:path :opportunityStatus ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:in ( "lead" "qualified" "proposal" "won" "lost" ) ;
    ] .
```

## Overlay shapes

Industry overlays may add NodeShapes in `overlay.ttl` (same file as overlay OWL).
They MUST NOT relax or remove base constraints.

## Changing required shapes

Adding `sh:minCount` on **existing** base concepts tightens completeness for all consumers
and is a **MAJOR** SemVer bump on that domain’s `index.json` `version`. Prefer documenting
new optional vocabulary in the ontology without new required shapes unless the domain
owner intentionally raises the bar.

## OWL/SKOS vs SHACL

| Concern | File |
|---------|------|
| Vocabulary (classes, properties, SKOS) | `ontology.ttl` |
| Completeness constraints | `shapes.ttl` (base) / `overlay.ttl` shapes section (industry) |
