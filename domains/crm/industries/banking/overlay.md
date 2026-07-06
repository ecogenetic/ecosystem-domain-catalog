# Banking addendum — CRM

## Additional concepts

- **ClientParty** — a Contact who is a verified banking client; "client" and "party" are the preferred terms.
- **CorporateClient** — an Account representing a corporate relationship with its own signatories.
- **KYCProfile** — mandatory identity verification record; onboarding is gated on verification.
- **Mandate** — signing authority allowing a person to operate accounts for a corporate client.

## Additional relationships

- ClientParty has exactly one active KYCProfile (1..1).
- Mandate is granted for one CorporateClient (1..1) and held by one ClientParty (1..1).
- Opportunity for a banking product must not close-won until the ClientParty's KYCProfile is verified.

## Additional roles

- **Relationship Manager (RM)** — owns a portfolio of client relationships; reads and writes clients and opportunities, reads KYC profiles.

## Regulatory notes

- KYC/AML verification gates onboarding: generated workflows must include a verification step before account activation or opportunity close.
- Every change to mandates or client limits requires maker-checker (four-eyes) approval.
- All client-data mutations require an immutable audit trail.
