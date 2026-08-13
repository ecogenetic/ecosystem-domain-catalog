# Banking addendum — SIV

## Additional concepts
- **BankingServiceSpecification** — a service specification for an operational banking facility.
- **BankingServiceInstance** — an active operational service made available under an agreement.
- **FacilityServiceMapping** — maps a banking product version to an operational service.

## Additional relationships
- BankingServiceInstance serviceUnderAgreement FinancialProductAgreement (many-to-one)
- BankingServiceInstance serviceForAccount FinancialAccount (many-to-one)

## Additional roles
- **Bank Service Owner** — Owns the operational banking service catalog and live service inventory. Bearer: person.

## Regulatory notes
- Product definitions, agreements, and service instances should remain distinct authoritative objects.
- Activation and suspension events should retain correlation identifiers to the originating order or process case.
