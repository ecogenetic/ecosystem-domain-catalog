# CCM — Credit & Collections Management

A Credit & Collections Management system sets credit limits, monitors exposure, scores risk, and
manages collections cases so finance teams reduce bad debt while keeping good customers trading
within policy.

## Concepts

- **CustomerAccount** — a trading customer whose credit terms and outstanding balances are managed.
- **CreditLimit** — the maximum outstanding balance a customer account is permitted to carry.
- **CreditExposure** — the current outstanding amount measured against a customer's credit limit.
- **CollectionCase** — a managed workstream to recover overdue amounts from a customer account.
- **PaymentPromise** — a customer commitment to pay an agreed amount by an agreed date on a case.
- **RiskScore** — a computed rating of a customer's likelihood of default or late payment.

## Taxonomy

- CustomerAccount is a kind of Account.
- PaymentPromise is a kind of Commitment.
- RiskScore is a kind of Assessment.

## Relationships

- CustomerAccount grantedCreditLimit CreditLimit (one-to-one)
- CreditExposure measuredAgainstCreditLimit CreditLimit (many-to-one)
- CreditExposure exposesCustomerAccount CustomerAccount (many-to-one)
- RiskScore assessesCustomerAccount CustomerAccount (many-to-one)
- CollectionCase openedForCustomerAccount CustomerAccount (many-to-one)
- PaymentPromise madeOnCollectionCase CollectionCase (many-to-one)

## Attributes

- CustomerAccount: accountName (string), paymentTerms (string), onCreditHold (boolean)
- CreditLimit: limitAmount (decimal), effectiveFrom (date), reviewDate (date)
- CreditExposure: exposureAmount (decimal), measuredAt (dateTime)
- CollectionCase: caseNumber (string), overdueAmount (decimal), collectionCaseStatus (string)
- PaymentPromise: promisedAmount (decimal), promisedDate (date), kept (boolean)
- RiskScore: scoreValue (decimal), scoredAt (dateTime), scoreModel (string)

## Lifecycle

- CollectionCase: opened → in progress → resolved → closed

## Roles

- **CreditAnalystRole** (bearer: person) — sets credit limits, reviews risk scores, and monitors exposure; permissions: CreditLimit:read, CreditLimit:write, RiskScore:read, CreditExposure:read, CustomerAccount:read
- **CollectionsAgentRole** (bearer: person) — works collection cases and records payment promises; permissions: CollectionCase:read, CollectionCase:write, PaymentPromise:read, PaymentPromise:write, CustomerAccount:read

## Primary workflow

Onboard account → assign credit limit → monitor exposure → flag breach → open collection case → resolve
