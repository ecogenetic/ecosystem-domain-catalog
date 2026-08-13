# Banking addendum — FIN

## Additional concepts
- **PaymentRailInstruction** — an instruction to move funds over a payment rail.
- **WalletLedgerEntry** — a ledger entry in a customer wallet or payment account.
- **AMLAlert** — an alert raised by transaction monitoring for investigation.
- **Beneficiary** — a party or external payee designated to receive funds.
- **PaymentOrder** — a customer or bank instruction to move funds from one account to a beneficiary.
- **PaymentAuthorisation** — an auditable approval decision for a payment order.
- **ClearingInstruction** — the instruction or message submitted to a clearing mechanism.
- **SettlementRecord** — the record confirming final settlement of a payment obligation.
- **PaymentReturn** — a return or reversal of a previously submitted payment.
- **DepositAccount** — a FinancialAccount specialized for deposit servicing.
- **AccountHold** — a controlled restriction reserving or blocking an amount on a deposit account.
- **InterestAccrual** — interest accrued or credited for a deposit account and period.

## Additional relationships
- PaymentOrder debitsAccount DepositAccount (many-to-one)
- PaymentOrder paysBeneficiary Beneficiary (many-to-one)
- PaymentAuthorisation authorisesPayment PaymentOrder (many-to-one)
- ClearingInstruction clearsPayment PaymentOrder (many-to-one)
- SettlementRecord settlesPayment PaymentOrder (many-to-one)
- PaymentReturn reversesPayment PaymentOrder (many-to-one)
- AccountHold restrictsAccount DepositAccount (many-to-one)
- InterestAccrual accruesForAccount DepositAccount (many-to-one)

## Additional roles
- **Payments Operations Analyst** — monitors rails, investigates AML alerts, and reconciles wallet and settlement records.
- **Deposit Operations Analyst** — manages deposit account holds, interest accruals, payment exceptions, and servicing events.

## Regulatory notes
- KYC/AML and sanctions decisions must gate payments where policy requires it.
- Maker-checker applies to high-risk payments, limit changes, and account restrictions where required.
- Payment corrections should use reversal or compensating records instead of destructive edits.
- Deposit servicing should preserve immutable rate, fee, hold, accrual, and statement history.
