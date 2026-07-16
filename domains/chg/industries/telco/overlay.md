# Telco addendum — CHG

## Additional concepts

- **PrepaidBalance** — A real-time balance funded before the subscriber consumes service.
- **RealTimeCharge** — A charge authorized and applied during an active network session.

## Additional relationships

- RealTimeCharge chargedSubscriber Subscriber (many-to-one)

## Additional roles

- **Prepaid Operations** — Person role that monitors online charging, reservations, and subscriber balances. Bearer: person. Permissions: ChargingAccount:read, Balance:read, BalanceReservation:read, Charge:read.

## Regulatory notes

- Identifier, subscriber, usage, and service associations retain effective dates and source-system provenance where required for audit.
- Personally identifiable and communications data are accessed according to applicable privacy, retention, and lawful-process controls.