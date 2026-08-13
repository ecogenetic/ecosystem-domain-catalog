# Banking addendum — CARD

## Additional concepts
- **RetailDebitCard** — a CardInstrument linked to a retail deposit or payment account.
- **RetailCreditCard** — a CardInstrument linked to a regulated revolving credit agreement.
- **StrongCustomerAuthenticationDecision** — an auditable decision recording whether step-up authentication was required and satisfied.

## Additional relationships
- RetailDebitCard operatesAgainst FinancialAccount (many-to-one)
- RetailCreditCard issuedUnder FinancialProductAgreement (many-to-one)
- StrongCustomerAuthenticationDecision appliesToAuthorization CardAuthorization (many-to-one)

## Additional roles
- **Card Fraud Operations Role** — reviews suspicious authorisations and may block instruments pending investigation.

## Regulatory notes
- Card activation, PIN or credential reset, limit changes, and high-risk transactions should preserve maker-checker or strong-authentication evidence where policy requires it.
- PAN-like identifiers should be masked in general operational views and stored only in appropriately controlled systems.
- Dispute and chargeback decisions must preserve evidence and scheme deadlines.
