# Banking

Retail and commercial banking: deposit and lending products, payments, cards, customer
relationship management, treasury, and heavy regulatory oversight. Systems built for banks
must treat identity, consent, auditability, resilience, and policy-versioned decisions as
first-class concerns.

## Terminology
- Customer is often called "client" or "party"; corporate customers are "counterparties".
- Accounts are financial products (current, savings, loan), distinct from CRM Accounts.
- KYC (Know Your Customer) — mandatory identity verification before onboarding.
- AML (Anti-Money Laundering) — transaction monitoring and suspicious-activity reporting.
- Mandate — an authorisation for payments or account operation on behalf of a party.
- Relationship Manager (RM) — the banker who owns a client relationship.
- Maker-checker — dual control requiring distinct maker and checker identities for controlled actions.
- ALM (Asset/Liability Management) — management of liquidity, funding, maturity and interest-rate risk.

## Regulatory notes
- KYC/AML checks must gate customer onboarding workflows; generated flows should include a
  verification step before account activation.
- Every financial mutation needs an immutable audit trail (who, when, what, why).
- Data residency and privacy (GDPR/POPIA) apply to all personal data; consent must be modeled.
- Four-eyes (maker-checker) approval is standard for limits, payments, mandate changes and
  other high-risk actions where policy requires it.
- Product, pricing, compliance, fraud, treasury and servicing decisions should reference the
  immutable policy or product version used at decision time.
- Critical banking services should preserve outage, recovery, customer-impact and change evidence.

## Business value chain

1. Identify and verify parties, beneficial owners and authorised representatives.
2. Assess eligibility, affordability, credit, fraud and financial-crime risk.
3. Define, price, originate and maintain deposits, lending, cards and investment products.
4. Open accounts and services; issue payment instruments and activate customer facilities.
5. Execute, authorise, clear, settle, return and reconcile payments and account movements.
6. Service loans, cards and deposits; manage disputes, hardship, arrears, collections and complaints.
7. Monitor conduct, liquidity, funding, capital, exposure, resilience and regulatory reporting.
8. Grow and retain customer relationships through consent-aware offers and campaigns.

## Cross-domain capability map

| Capability | Typical owning domain |
|---|---|
| Party relationship, onboarding, campaigns and service | CRM |
| Customer value, propensity and next-best action | CVM |
| Product definition and product versions | PIM |
| Customer-specific pricing, concessions and quotes | CPQ |
| Digital origination | ECOM |
| Application/order fulfilment | OMS |
| Regulated process and maker-checker workflow | BPM |
| Documents, disclosures, evidence and records | CMS |
| Golden party/KYC mastering | MDM |
| Accounts, deposits, payments, balances, journals and reconciliation | FIN |
| Cards and payment-instrument lifecycle | CARD |
| Loan servicing and restructures | LNS |
| Credit exposure, arrears and collections | CCM |
| Risk, compliance and controls | GRC |
| Fraud investigation and assurance | RAF |
| Banking service catalog and live service inventory | SIV |
| Partners, agents, correspondents and TPPs | PRM |
| Bank finance and accounting control | FMS / ERP |
| Treasury, liquidity, funding and ALM | TRE |
| Analytics, risk and liquidity reporting | BI |
| Critical-service incidents and regulated change | ITSM |
| Digital service assurance and customer impact | SAM |
| Regulated positions and delegated authority | HCM |
| Mandatory compliance learning and certification | LMS |
| ATM, branch and critical physical assets | EAM |

## Domain integration model

| Canonical detail | Banking specialization | Owning domain | Shared identifiers |
|---|---|---|---|
| Party and customer | Client, counterparty, beneficial owner | CRM / MDM | partyId, customerRelationshipId |
| Product | Deposit, loan, card or investment definition | PIM | productId, productVersionId |
| Offer and quote | Priced, eligibility-checked proposition | CPQ | offerId, quoteId, productVersionId |
| Agreement and account | Product agreement and financial account | CRM / FIN | agreementId, accountId |
| Interaction | Branch, app, contact-centre or adviser contact | CRM | interactionId, channelId |
| Order and process | Application or servicing request | OMS / BPM | orderId, processInstanceId |
| Service | Facility made available under an agreement | SIV | serviceInstanceId, agreementId |
| Deposit/payment | Payment order, authorisation, clearing, settlement, return | FIN | paymentOrderId, accountId, correlationId |
| Card instrument | Physical/virtual card, token, authorisation and dispute | CARD | instrumentId, tokenId, authorizationId, disputeId |
| Loan servicing | Loan account, schedule, accrual and restructure | LNS | loanAccountId, agreementId, scheduleVersion |
| Credit/collections | Credit facility, exposure and collections case | CCM | creditFacilityId, accountId, caseId |
| Transaction | Posting or account movement | FIN | transactionId, accountId |
| Case | Exception, dispute, complaint or collections case | BPM / CCM / CARD | caseId, correlationId |
| Consent | Data-use and channel permission | CRM / GRC | consentId, partyId, purposeCode |
| Decision | Credit, fraud, KYC, AML or eligibility result | RAF / GRC | decisionId, policyVersionId |
| Partner | TPP, correspondent, intermediary or service provider | PRM | partnerId, agreementId |
| Treasury | Funding, liquidity position, limit and treasury deal | TRE | positionId, dealId, limitId, asOfDate |
| Finance | General ledger, Nostro, suspense and period close | FMS / ERP | ledgerId, journalEntryId, fiscalPeriodId |
| Critical service | Major incident, alarm, impact and regulated change | ITSM / SAM | serviceId, incidentId, alarmId, changeId |

### Integration rules
- A party is the legal person or organisation; customer, account holder and beneficiary are roles.
- Product versions are immutable inputs to offers, agreements, orders and decisions.
- A financial product agreement is distinct from the financial account opened under it.
- A payment instrument is not a payment; it is a credential used to initiate payment activity.
- A loan account is a financial account specialization; origination, servicing and collections remain separate bounded contexts.
- Treasury positions are aggregated exposures, not customer financial accounts.
- Each object keeps its own identifier and the correlation identifiers of upstream objects.
- Lifecycle events carry eventId, eventType, occurredAt, sourceDomain, entityId, entityVersion and correlationId.
- Domains exchange references and events instead of copying another domain's authoritative state.
- Banking-specific terminology and states map to canonical concepts through overlays and curated alignments.

## Modeling rules

- Distinguish a legal party, customer relationship, product agreement and financial account.
- Model beneficial ownership, mandates and signatories as dated relationships.
- Preserve immutable posting and approval evidence; corrections are compensating entries.
- Attach KYC, sanctions, AML, fraud, pricing and treasury decisions to the policy/version used at decision time.
- Keep currency and jurisdiction explicit on monetary products, limits and transactions.
- Keep card instrument, payment order and posted financial transaction as separate concepts.
- Keep loan origination, loan servicing and collections as linked but independently owned lifecycles.
- Keep service alarms distinct from managed IT incidents; correlate them through shared identifiers.
