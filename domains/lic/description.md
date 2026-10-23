# LIC — Licensing and Entitlements

Manages license agreements, entitlements, seat allocations, feature access, usage meters, and license keys for software products.

## Concepts

- **LicenseAgreement** — A contract specialization that grants a customer the right to use a software product edition.
- **Entitlement** — A right, under a license agreement, to a feature, a seat count, or a metered capacity.
- **SeatAllocation** — An assignment of one entitlement seat to a person or tenant.
- **FeatureAccess** — A feature that an entitlement turns on.
- **UsageMeter** — A measure of consumed capacity against an entitlement.
- **LicenseKey** — A credential that identifies a license agreement. Distinct from the agreement itself.

## Taxonomy

- LicenseAgreement is a kind of Contract.
- SeatAllocation is a kind of Entitlement use.
- FeatureAccess is a kind of Entitlement right.

## Relationships

- Entitlement grantedByLicenseAgreement LicenseAgreement (many-to-one)
- SeatAllocation consumesEntitlement Entitlement (many-to-one)
- FeatureAccess enabledByEntitlement Entitlement (many-to-one)
- UsageMeter measuresEntitlement Entitlement (many-to-one)
- LicenseKey identifiesLicenseAgreement LicenseAgreement (many-to-one)

## Attributes

- LicenseAgreement: licenseAgreementId (string), licenseAgreementStatus (string), productEditionCode (string), customerReference (string)
- Entitlement: entitlementId (string), entitlementName (string), quantity (integer)
- SeatAllocation: seatAllocationId (string), assigneeReference (string)
- FeatureAccess: featureAccessId (string), featureCode (string)
- UsageMeter: usageMeterId (string), consumedQuantity (decimal)
- LicenseKey: licenseKeyId (string), keyValue (string)

## Lifecycle

- LicenseAgreement: quoted → active → suspended → expired

## Roles

- **License Administrator** (bearer: person) — issues license agreements, entitlements, and seat allocations; permissions: LicenseAgreement:read, LicenseAgreement:write, Entitlement:read, Entitlement:write, SeatAllocation:read, SeatAllocation:write

## Primary workflow

Quote license → activate agreement → grant entitlement → allocate seats → meter usage → suspend or expire
