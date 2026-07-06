# Banking addendum — Financial Management

## Additional concepts

- **NostroAccount** — a correspondent-bank account in another currency, reconciled daily; specializes ChartOfAccount.
- **SuspenseAccount** — temporary holding for unmatched postings with policy age limits; specializes ChartOfAccount.
- **IntradayPosition** — running currency/account balance monitored against liquidity limits during the day.

## Additional relationships

- Every NostroAccount is covered by a daily Reconciliation (1..1 per business day).
- Aged suspense balances are cleared by identified JournalEntries; age is tracked in days.
- IntradayPositions track ChartOfAccounts per currency.

## Additional roles

- **Financial Control Officer** — owns suspense clearance and signs off nostro reconciliations.

## Regulatory notes

- Nostro breaks and aged suspense items above thresholds are reportable control issues; generated flows should escalate on age/threshold breaches.
- Intraday liquidity monitoring is a regulatory expectation; positions need timestamps and currency codes.
- Period close must not complete with unexplained suspense balances.
