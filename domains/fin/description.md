# FinTech — Financial Technology Platform

A Financial Technology Platform processes transactions, maintains ledgers, and enforces financial
controls so stakeholders trust balances and audit trails in real time.

## Concepts

- **Account** — a balance-holding record for a customer or internal party on the platform.
- **Transaction** — a monetary movement initiated against an account, validated and posted to a ledger.
- **Ledger** — an append-only book of posted transactions from which balances are derived.
- **AuditLog** — an immutable record of every transaction and control decision for audit review.
- **Currency** — the monetary unit in which ledgers and transactions are denominated.
- **Reconciliation** — a control that verifies ledger balances against external or counterpart records.

## Taxonomy

- Transaction is a kind of FinancialEvent.
- AuditLog is a kind of Record.
- Reconciliation is a kind of Control.

## Relationships

- Account holdsTransaction Transaction (one-to-many)
- Transaction postedToLedger Ledger (many-to-one)
- Ledger denominatedInCurrency Currency (many-to-one)
- AuditLog recordsTransaction Transaction (one-to-one)
- Reconciliation balancesLedger Ledger (many-to-one)

## Attributes

- Account: accountNumber (string), accountHolder (string), balance (decimal)
- Transaction: transactionReference (string), amount (decimal), initiatedAt (dateTime), transactionStatus (string)
- Ledger: ledgerName (string), ledgerType (string)
- AuditLog: loggedAt (dateTime), actor (string), eventDetail (string)
- Currency: currencyCode (string), currencyName (string)
- Reconciliation: reconciledAt (dateTime), variance (decimal)

## Lifecycle

- Transaction: initiated → validated → posted → reconciled

## Roles

- **OperationsAnalystRole** (bearer: person) — monitors transaction processing, investigates exceptions, and runs reconciliations; permissions: Transaction:read, Transaction:write, Reconciliation:read, Reconciliation:write, Ledger:read, Account:read
- **AuditorRole** (bearer: person) — reviews audit logs and verifies ledger integrity without altering records; permissions: AuditLog:read, Ledger:read, Transaction:read, Reconciliation:read

## Primary workflow

Initiate transaction → validate limits → post to ledger → reconcile → audit
