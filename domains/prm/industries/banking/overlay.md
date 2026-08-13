# Banking addendum — PRM

## Additional concepts
- **ThirdPartyProvider** — a regulated third party accessing banking APIs or initiating services.
- **CorrespondentBank** — a bank providing payment, clearing, settlement, or custody services.
- **BankingAgent** — an authorised intermediary providing specified services on behalf of the bank.
- **OpenBankingCredential** — a credential authorising a TPP to access open-banking capabilities.

## Additional relationships
- OpenBankingCredential credentialForProvider ThirdPartyProvider (many-to-one)
- CorrespondentBank correspondentUnderAgreement PartnerAgreement (many-to-one)

## Additional roles
- **Bank Partner Manager** — Onboards and governs TPPs, agents, correspondents, credentials, and partner agreements. Bearer: person.

## Regulatory notes
- Partner onboarding should capture regulatory status, permitted services, jurisdiction, and due-diligence evidence.
- Open-banking credentials should be scoped, time-bounded, revocable, and linked to the governing agreement.
