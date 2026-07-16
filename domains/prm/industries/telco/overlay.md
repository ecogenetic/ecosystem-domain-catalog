# Telco addendum — PRM

## Additional concepts

- **MVNODealer** — A dealer authorized to register subscribers and sell MVNO products and services.
- **AirtimeDistributor** — A partner distributing prepaid airtime or electronic value across downstream channels.

## Additional relationships

- MVNODealer servesSubscriber Subscriber (many-to-one)

## Additional roles

- **Dealer Operations** — Person role that manages MVNO dealer onboarding, credentials, and channel compliance. Bearer: person. Permissions: Dealer:read, Dealer:write, PartnerCredential:read, PartnerCredential:write, PartnerAgreement:read.

## Regulatory notes

- Identifier, subscriber, usage, and service associations retain effective dates and source-system provenance where required for audit.
- Personally identifiable and communications data are accessed according to applicable privacy, retention, and lawful-process controls.