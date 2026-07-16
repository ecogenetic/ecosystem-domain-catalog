# Telco addendum — MED

## Additional concepts

- **ChargingDataRecord** — A mediated voice, messaging, or data record received from a network source.
- **NetworkUsageBatch** — A batch of network-originated usage records for an MVNO.

## Additional relationships

- ChargingDataRecord usageBySubscriber Subscriber (many-to-one)

## Additional roles

- **CDR Operations** — Person role that reconciles MVNO charging-data files and rejected network usage. Bearer: person. Permissions: UsageBatch:read, UsageBatch:write, MediatedUsageRecord:read, RejectedUsageRecord:read.

## Regulatory notes

- Identifier, subscriber, usage, and service associations retain effective dates and source-system provenance where required for audit.
- Personally identifiable and communications data are accessed according to applicable privacy, retention, and lawful-process controls.