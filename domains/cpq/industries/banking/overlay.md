# Banking addendum — CPQ

## Additional concepts
- **BankingQuote** — a customer-specific priced proposition for a banking product or bundle.
- **RateOffer** — a customer-specific interest or return rate.
- **FeeOffer** — a customer-specific fee arrangement.
- **PricingConcession** — a discretionary reduction or pricing exception.

## Additional relationships
- RateOffer rateOfferForQuote BankingQuote (many-to-one)
- FeeOffer feeOfferForQuote BankingQuote (many-to-one)
- PricingConcession concessionForQuote BankingQuote (many-to-one)

## Additional roles
- **Bank Pricing Approver** — Approves customer-specific pricing exceptions within delegated authority. Bearer: person.

## Regulatory notes
- Pricing exceptions should record delegated authority and approval evidence.
- Quoted terms should reference the immutable product version and eligibility decision used.
