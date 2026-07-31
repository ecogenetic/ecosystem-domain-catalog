# Data Source Mappings

This directory contains **mappings from structured data sources** (SQL databases, CSV files, APIs, legacy systems) to the canonical domain ontologies in this catalog.

Unlike domain ontologies themselves (which define business meaning), mappings are **additive alignment triples** that connect external identifiers to canonical IRIs.

## Structure

- `mappings/common/` — Shared templates (SHACL, prefixes)
- `mappings/{domainId}/` — Domain‑specific data source mappings
- `mappings/common/index.yaml` — Registry of supported sources and prefixes

## Usage

1. **Identify your data source** (e.g., "Salesforce", "SAP CRM")
2. **Find the mapping file** under `mappings/`
3. **Copy, customize, and contribute**

## Alignment Types

| Type | Predicate | Purpose |
|------|-----------|---------|
| Class mapping | `owl:equivalentClass` | `legacy:Account ↔ crm:Account` |
| Property mapping | `rdfs:subPropertyOf` | `legacy:name → crm:name` |
| Relationship mapping | `rdfs:subPropertyOf` + domain/range | `legacy:accountId → crm:belongsToAccount` |
