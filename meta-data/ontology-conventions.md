# Ontology conventions (OWL + SKOS)

Seed ontologies are RDF Turtle under `domains/{id}/ontology.ttl`.

## Namespaces

| Scope | Pattern |
|-------|---------|
| Domain | `https://ecosystemcode.com/ontology/{domainId}#` |
| Industry shared | `https://ecosystemcode.com/ontology/industry/{industryId}#` |
| Domain×industry overlay | `https://ecosystemcode.com/ontology/{domainId}/{industryId}#` |

Required prefixes in every domain ontology: `:`, `owl:`, `rdfs:`, `xsd:`, `skos:`, `bfo:`.

## IRI stability

- Once published, a class or property IRI is **never renamed or removed**.
- Retire terms with `owl:deprecated true` and introduce a replacement alongside.
- Overlays MUST NOT redefine base IRIs; they only add.

## Classes and SKOS

Every `owl:Class` MUST carry:

- `skos:prefLabel` — preferred display name
- `skos:definition` — one clear definition
- `skos:altLabel` — strongly encouraged synonyms for retrieval and generation

## Properties

- Object properties: distinct name per relationship; required `rdfs:domain` and `rdfs:range`.
- Datatype properties: typed with `xsd:*`.
- Stateful entities: a `...Status` (or equivalent) string datatype; allowed values live in SHACL `sh:in`.

## Roles (BFO)

Role classes are named `{Something}Role` and subclass `bfo:0000023` (BFO role branch)
so consumers can detect roles and extract permissions from `skos:definition`.

## Minimums (validated)

Per domain ontology: every `index.json` seed entity as a class; ≥4 object properties with
domain/range; ≥1 role under `bfo:0000023`; SKOS prefLabel/definition counts ≥ class count.
