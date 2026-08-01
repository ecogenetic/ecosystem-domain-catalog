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

## Business value chain

1. Identify and verify parties, beneficial owners and authorised representatives.
2. Assess eligibility, affordability, credit, fraud and financial-crime risk.
3. Originate and maintain deposits, lending, cards and investment products.
4. Execute, clear, settle and reconcile payments and account movements.
5. Service customers, manage disputes, arrears, collections and complaints.
6. Monitor conduct, liquidity, capital, exposure and regulatory reporting.

## Cross-domain capability map

| Capability | Typical owning domain |
|---|---|
| Party relationship, onboarding and service | CRM |
| Product and offer configuration | PIM / CPQ |
| Accounts, balances, journals and reporting | FIN |
| Risk, compliance and controls | GRC / RAF |
| Customer value and next-best action | CVM |
| Documents, consent and records | CMS / MDM |
| Collections and workflow | BPM / CCM |

## Domain integration model

| Canonical detail | Banking specialization | Owning domain | Shared identifiers |
|---|---|---|---|
| Party and customer | Client, counterparty, beneficial owner | CRM / MDM | partyId, customerRelationshipId |
| Product | Account, loan, card or investment definition | PIM | productId, productVersionId |
| Offer and quote | Priced, eligibility-checked proposition | CPQ | offerId, quoteId |
| Agreement and account | Product agreement and financial account | CRM / FIN | agreementId, accountId |
| Interaction | Branch, app, contact-centre or adviser contact | CRM | interactionId, channelId |
| Order and process | Application or servicing request | OMS / BPM | orderId, processInstanceId |
| Service | Facility made available under an agreement | SIV | serviceInstanceId |
| Transaction | Posting, payment or account movement | FIN | transactionId, accountId |
| Case | Exception, dispute, complaint or collections case | BPM / CCM | caseId |
| Consent | Data-use and channel permission | CRM / GRC | consentId, partyId, purposeCode |
| Decision | Credit, fraud, KYC, AML or eligibility result | RAF / GRC | decisionId, policyVersionId |
| Partner | Merchant, intermediary or service provider | PRM | partnerId |

### Integration rules

- A party is the legal person or organisation; customer, account holder and beneficiary are roles.
- Product versions are immutable inputs to offers, agreements, orders and decisions.
- Each object keeps its own identifier and the correlation identifiers of upstream objects.
- Lifecycle events carry eventId, eventType, occurredAt, sourceDomain, entityId, entityVersion and correlationId.
- Domains exchange references and events instead of copying another domain's authoritative state.
- Banking-specific terminology and states map to canonical concepts through overlays and mappings.

## Modeling rules

- Distinguish a legal party, customer relationship, product agreement and financial account.
- Model beneficial ownership, mandates and signatories as dated relationships.
- Preserve immutable posting and approval evidence; corrections are compensating entries.
- Attach KYC, sanctions, AML and consent decisions to the policy/version used at decision time.
- Keep currency and jurisdiction explicit on monetary products, limits and transactions.
