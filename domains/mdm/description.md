# MDM — Master Data Management

A Master Data Management system governs golden records, hierarchies, match rules, and data
stewardship tasks so the organization trusts one authoritative master for each data domain.

## Concepts

- **MasterRecord** — the authoritative golden record consolidated from source records for an entity.
- **DataDomain** — a governed subject area (such as customer, product, or supplier) that master records belong to.
- **MatchRule** — a configured rule that identifies and consolidates duplicate source records into a MasterRecord.
- **Hierarchy** — a governed structure that organizes master records into parent-child relationships.
- **Steward** — the accountable person who reviews, curates, and approves master records.
- **Lineage** — the traceable history linking a MasterRecord back to its contributing source records.

## Taxonomy

- MasterRecord is a kind of GoldenRecord.
- DataDomain is a kind of SubjectArea.
- MatchRule is a kind of GovernanceRule.

## Relationships

- MasterRecord belongsToDataDomain DataDomain (many-to-one)
- MatchRule consolidatesMasterRecord MasterRecord (one-to-many)
- Hierarchy organizesMasterRecord MasterRecord (one-to-many)
- Steward curatesMasterRecord MasterRecord (one-to-many)
- Lineage tracesMasterRecord MasterRecord (many-to-one)

## Attributes

- MasterRecord: recordKey (string), sourceCount (integer), masterRecordStatus (string)
- DataDomain: domainName (string), description (string)
- MatchRule: ruleName (string), matchThreshold (decimal)
- Hierarchy: hierarchyName (string), levelCount (integer)
- Steward: stewardName (string), email (string)
- Lineage: sourceSystem (string), ingestedAt (dateTime)

## Lifecycle

- MasterRecord: ingested → matched → stewarded → published

## Roles

- **DataStewardRole** (bearer: person) — reviews match results, curates golden records, and approves publication; permissions: MasterRecord:read, MasterRecord:write, MatchRule:read, Hierarchy:read, Lineage:read
- **DataOwnerRole** (bearer: person) — owns a data domain, defines match rules and hierarchies, and accepts accountability for data quality; permissions: DataDomain:read, DataDomain:write, MatchRule:read, MatchRule:write, Hierarchy:read, Hierarchy:write

## Primary workflow

Ingest source record → match and merge → steward review → publish golden record
