# Banking addendum — PIM

## Additional concepts
- **BankingProduct** — a Product representing a deposit, lending, card, payment, or investment offering.
- **ProductVersion** — an immutable version used by offers, agreements, orders, and decisions.
- **ProductDisclosure** — dated product terms or regulatory disclosure content.
- **RateAndFeeSchedule** — effective rates and fees for a product version.

## Additional relationships
- BankingProduct hasProductVersion ProductVersion (one-to-many)
- ProductVersion hasDisclosure ProductDisclosure (one-to-many)
- ProductVersion hasRateAndFeeSchedule RateAndFeeSchedule (one-to-many)

## Additional roles
- **Bank Product Manager** — Owns banking product definitions, immutable versions, disclosures, and publication. Bearer: person.

## Regulatory notes
- Product versions should be immutable once used by an agreement or decision.
- Rates, fees, eligibility, jurisdiction, and disclosures should be traceable to the exact product version.
