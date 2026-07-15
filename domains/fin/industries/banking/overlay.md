# Banking addendum — FIN

## Additional concepts

- **PaymentRailInstruction** — An instruction to move funds over a payment rail (instant, RTGS, card).
- **WalletLedgerEntry** — A ledger entry in a customer wallet or payment account.
- **AMLAlert** — An alert raised by transaction monitoring for investigation.

## Additional relationships

- PaymentRailInstruction relatesToContext within the FIN base model (many-to-one).
- WalletLedgerEntry is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Payments Operations Analyst** — Monitors rails, investigates AML alerts, and reconciles wallet ledgers.

## Regulatory notes

- AML alerts must be dispositioned with an audit trail before funds are released where required.
- Wallet ledger entries are double-entry consistent with the payment instruction.
