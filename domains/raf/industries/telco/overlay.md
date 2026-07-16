# Telco addendum — RAF

## Additional concepts

- **SIMBoxFraudAlert** — A fraud alert indicating suspected bypass of legitimate mobile interconnect charging.
- **SubscriberInvestigation** — An investigation centered on one or more mobile subscriber identities.

## Additional relationships

- SubscriberInvestigation investigatesSubscriber Subscriber (many-to-one)

## Additional roles

- **Telecom Fraud Investigator** — Person role that investigates suspicious subscriber and network usage patterns. Bearer: person. Permissions: FraudAlert:read, UsageAnomaly:read, Investigation:read, Investigation:write, RecoveryAction:write.

## Regulatory notes

- Identifier, subscriber, usage, and service associations retain effective dates and source-system provenance where required for audit.
- Personally identifiable and communications data are accessed according to applicable privacy, retention, and lawful-process controls.