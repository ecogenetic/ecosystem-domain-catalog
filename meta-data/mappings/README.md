# Data Source Mappings

Mapping assets are colocated with the domain or industry overlay they extend. There is no repository-root `mappings/` directory.

This directory contains **generic mappings from structured data sources** (SQL databases, CSV exports, JSON APIs, legacy ERPs/CRMs) to the canonical domain ontologies in this catalog.

Unlike domain ontologies themselves (which define business meaning), these mappings are **additive alignment triples** that connect external identifiers, tables, and columns to canonical IRIs. They are intentionally product-agnostic to support a wide variety of legacy and modern data systems.

## Structure

- `domains/{domainId}/mappings/` — Domain-specific generic data alignments
- `domains/{domainId}/industries/{industryId}/mappings/` — Industry-specialized mappings beside their overlays
- `meta-data/mappings/` — Mapping conventions and shared source registry
- `mappings/common/index.yaml` — Registry of supported generic source types and prefixes

## Usage

1. **Identify your data source format** (e.g., relational table, CSV dump, JSON payload)
2. **Find the generic mapping file** at `domains/{domainId}/mappings/generic-mapping.ttl`, then load an optional industry specialization from `domains/{domainId}/industries/{industryId}/mappings/generic-mapping.ttl`
3. **Align your columns/fields** to the canonical properties using the provided predicates
4. **Validate** against the domain ontology

## Alignment Types

| Type | Predicate | Purpose |
|------|-----------|---------|
| Class mapping | `owl:equivalentClass` | `legacy:Table ↔ domain:Entity` |
| Property mapping | `rdfs:subPropertyOf` | `legacy:column_name → domain:property` |
| Relationship mapping | `rdfs:subPropertyOf` + domain/range | `legacy:foreign_key → domain:relationship` |

## Customization

These files provide a **baseline template**. Contributors should adjust the `legacy:` prefix and property names to match their specific schema while preserving the alignment to the canonical `domain:` namespace.


## Industry mapping rule

Industry-specialized mappings MUST mirror the domain overlay hierarchy:

```text
domains/{domainId}/industries/{industryId}/overlay.ttl
domains/{domainId}/industries/{industryId}/mappings/generic-mapping.ttl
```

The base mapping is loaded first and the industry mapping is additive. Industry mappings must
reference authoritative operational-domain IRIs instead of duplicating their entities.
