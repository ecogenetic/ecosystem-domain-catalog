# Banking

Retail and commercial banking: deposit and lending products, payments, customer relationship
management, and heavy regulatory oversight. Systems built for banks must treat identity,
consent, and auditability as first-class concerns.

## Terminology

- Customer is often called "client" or "party"; corporate customers are "counterparties".
- Accounts are financial products (current, savings, loan), distinct from CRM Accounts.
- KYC (Know Your Customer) — mandatory identity verification before onboarding.
- AML (Anti-Money Laundering) — transaction monitoring and suspicious-activity reporting.
- Mandate — an authorisation for payments or account operation on behalf of a party.
- Relationship Manager (RM) — the banker who owns a client relationship.

## Regulatory notes

- KYC/AML checks must gate customer onboarding workflows; generated flows should include a
  verification step before account activation.
- Every financial mutation needs an immutable audit trail (who, when, what, why).
- Data residency and privacy (GDPR/POPIA) apply to all personal data; consent must be modeled.
- Four-eyes (maker-checker) approval is standard for limits, payments, and mandate changes.
