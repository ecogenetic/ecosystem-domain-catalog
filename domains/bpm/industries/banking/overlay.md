# Banking addendum — BPM

## Additional concepts
- **BankingCase** — a regulated banking process instance.
- **MakerCheckerApproval** — reuses the shared banking `MakerCheckerApproval` concept for four-eyes control with distinct maker and checker identities.
- **KYCOnboardingCase** — a KYC-gated onboarding case.
- **RegulatorySLA** — an SLA derived from regulatory or policy deadlines.

## Additional relationships
- BankingCase requiresApproval MakerCheckerApproval (one-to-many)
- KYCOnboardingCase onboardsParty Party (many-to-one)
- BankingCase governedByRegulatorySLA RegulatorySLA (many-to-one)

## Additional roles
- **Bank Case Manager** — Coordinates regulated banking cases, exceptions, and escalations. Bearer: person.

## Regulatory notes
- Maker and checker identities must be distinct where four-eyes control is required.
- KYC onboarding should not complete before the applicable compliance decision permits activation.
