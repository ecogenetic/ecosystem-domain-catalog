# Telco addendum — SAM

## Additional concepts

- **NetworkAlarm** — A service alarm originating from a mobile network or host-MNO feed.
- **SubscriberImpact** — A customer-impact assessment expressed in affected mobile service identities.

## Additional relationships

- SubscriberImpact affectsSubscriber Subscriber (many-to-one)

## Additional roles

- **Network Assurance Analyst** — Person role that correlates host-network alarms with MVNO subscriber impact. Bearer: person. Permissions: ServiceAlarm:read, CustomerImpact:read, CustomerImpact:write, AssuranceCase:read, AssuranceCase:write.

## Regulatory notes

- Identifier, subscriber, usage, and service associations retain effective dates and source-system provenance where required for audit.
- Personally identifiable and communications data are accessed according to applicable privacy, retention, and lawful-process controls.