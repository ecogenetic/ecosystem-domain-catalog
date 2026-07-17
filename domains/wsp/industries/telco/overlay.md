# Telco addendum — WSP

## Additional concepts

- **MVNOWholesaleAgreement** — A wholesale agreement granting an MVNO access to host-network services.
- **HostNetworkSettlement** — A settlement statement issued by or to the host mobile network operator.

## Additional relationships

- HostNetworkSettlement coversSubscriberUsage Subscriber (many-to-one)

## Additional roles

- **Host MNO Commercial Manager** — Person role that governs MVNO host-network contracts, pricing, and settlement escalations. Bearer: person. Permissions: WholesaleAgreement:read, WholesaleAgreement:write, WholesaleRate:read, SettlementStatement:read.

## Regulatory notes

- Identifier, subscriber, usage, and service associations retain effective dates and source-system provenance where required for audit.
- Personally identifiable and communications data are accessed according to applicable privacy, retention, and lawful-process controls.