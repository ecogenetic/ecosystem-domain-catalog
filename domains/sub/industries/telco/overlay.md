# Telco addendum — SUB

## Additional concepts

- **PrepaidSubscription** — A subscription funded before service consumption.
- **PostpaidSubscription** — A subscription billed after a defined billing period.

## Additional relationships

- PrepaidSubscription representedBySubscriber Subscriber (many-to-one)

## Additional roles

- **Subscriber Operations** — Person role that manages MVNO subscriber activation and lifecycle exceptions. Bearer: person. Permissions: Subscription:read, Subscription:write, ServiceLine:read, ServiceLine:write.

## Regulatory notes

- Identifier, subscriber, usage, and service associations retain effective dates and source-system provenance where required for audit.
- Personally identifiable and communications data are accessed according to applicable privacy, retention, and lawful-process controls.