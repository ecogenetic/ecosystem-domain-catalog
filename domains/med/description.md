# MED — Usage Mediation Management

Ingests, validates, normalizes, deduplicates, enriches, and routes high-volume service-usage events.

## Concepts

- **RawUsageEvent** — An unprocessed event emitted by a network or service platform.
- **UsageBatch** — A controlled collection of usage events received and processed together.
- **MediatedUsageRecord** — A validated, normalized, deduplicated, and enriched usage record.
- **ValidationRule** — A rule determining whether a usage event is structurally and semantically valid.
- **EnrichmentRule** — A rule adding reference or subscriber context to usage data.
- **DuplicateRecord** — A usage record identified as a duplicate of an earlier event.
- **RejectedUsageRecord** — A usage record excluded from downstream processing with a recorded reason.
- **UsageRoute** — A rule or destination controlling distribution of mediated usage.

## Taxonomy

- MediatedUsageRecord is a kind of Usage record.
- DuplicateRecord is a kind of Usage exception.
- RejectedUsageRecord is a kind of Usage exception.

## Relationships

- UsageBatch containsRawUsageEvent RawUsageEvent (one-to-many)
- ValidationRule validatesRawUsageEvent RawUsageEvent (many-to-many)
- EnrichmentRule enrichesMediatedUsageRecord MediatedUsageRecord (many-to-many)
- DuplicateRecord duplicatesRawUsageEvent RawUsageEvent (many-to-one)
- RejectedUsageRecord rejectsRawUsageEvent RawUsageEvent (many-to-one)
- UsageRoute routesMediatedUsageRecord MediatedUsageRecord (many-to-many)

## Attributes

- RawUsageEvent: rawUsageEventId (string)
- UsageBatch: usageBatchId (string)
- MediatedUsageRecord: mediatedUsageRecordId (string)
- ValidationRule: validationRuleId (string)
- EnrichmentRule: enrichmentRuleId (string)
- DuplicateRecord: duplicateRecordId (string)
- RejectedUsageRecord: rejectedUsageRecordId (string)
- UsageRoute: usageRouteId (string)

## Lifecycle

- UsageBatch: received → validating → mediated → distributed → rejected

## Roles

- **Mediation Operator** (bearer: person) — monitors usage ingestion, exceptions, and downstream distribution; permissions: UsageBatch:read, UsageBatch:write, RejectedUsageRecord:read, UsageRoute:read, UsageRoute:write.

## Primary workflow

Receive usage batch → validate events → remove duplicates → enrich context → create mediated records → distribute