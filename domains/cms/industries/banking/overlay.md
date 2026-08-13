# Banking addendum — CMS

## Additional concepts
- **RegulatedDocument** — controlled banking content subject to approval, retention, or disclosure rules.
- **KYCArtifact** — identity evidence supporting KYC verification.
- **CustomerStatement** — a periodic account statement.
- **LegalHold** — a preservation instruction preventing disposal.

## Additional relationships
- KYCArtifact kycArtifactForParty Party (many-to-one)
- CustomerStatement statementForAccount FinancialAccount (many-to-one)
- LegalHold legalHoldPreserves RegulatedDocument (one-to-many)

## Additional roles
- **Bank Records Manager** — Governs regulated banking content, retention, legal holds, and approved disclosures. Bearer: person.

## Regulatory notes
- Retention and legal-hold rules must prevent disposal while preserving provenance.
- Statements and disclosures should be reproducible from the product/account version and period used.
