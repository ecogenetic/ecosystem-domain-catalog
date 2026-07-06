# LSM — Lease Management System

A Lease Management System manages lease contracts, leased assets, payment schedules, renewals, and
escalations so real estate and finance teams stay compliant with lease terms and accounting
standards.

## Concepts

- **LeaseContract** — a binding agreement granting a tenant the right to use an asset for a term and rent.
- **LeasedAsset** — the property, equipment, or vehicle whose use is granted under a lease contract.
- **LeasePayment** — a scheduled rent or charge instalment due under a lease contract.
- **RenewalOption** — a contractual right to extend the lease contract beyond its initial term.
- **EscalationSchedule** — the agreed timetable of rent increases applied to lease payments over the term.
- **Tenant** — the organisation or person that leases the asset and owes the payments.

## Taxonomy

- LeaseContract is a kind of Contract.
- LeasedAsset is a kind of Asset.
- LeasePayment is a kind of Payment.

## Relationships

- LeaseContract coversLeasedAsset LeasedAsset (one-to-many)
- Tenant partyToLeaseContract LeaseContract (one-to-many)
- LeasePayment dueUnderLeaseContract LeaseContract (many-to-one)
- EscalationSchedule adjustsLeasePayment LeasePayment (one-to-many)
- RenewalOption extendsLeaseContract LeaseContract (many-to-one)

## Attributes

- LeaseContract: contractNumber (string), commencementDate (date), expiryDate (date), baseRent (decimal), leaseContractStatus (string)
- LeasedAsset: assetName (string), assetType (string), location (string)
- LeasePayment: paymentAmount (decimal), dueDate (date), paid (boolean)
- RenewalOption: noticeDate (date), extensionMonths (integer)
- EscalationSchedule: escalationRate (decimal), frequency (string)
- Tenant: tenantName (string), contactEmail (string)

## Lifecycle

- LeaseContract: draft → active → renewal → terminated

## Roles

- **LeaseAdministratorRole** (bearer: person) — drafts contracts, schedules payments, and tracks renewals and escalations; permissions: LeaseContract:read, LeaseContract:write, LeasePayment:read, LeasePayment:write, RenewalOption:read, RenewalOption:write, EscalationSchedule:read, EscalationSchedule:write
- **TenantRole** (bearer: organisation) — occupies the leased asset, pays scheduled amounts, and exercises renewal options; permissions: LeaseContract:read, LeasePayment:read, RenewalOption:read

## Primary workflow

Create lease contract → link asset → schedule payments → track renewal → amend or terminate
