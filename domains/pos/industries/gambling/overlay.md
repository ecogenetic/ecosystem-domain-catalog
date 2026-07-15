# Gaming & Gambling addendum — POS

## Additional concepts

- **VenueTill** — A point-of-sale till at a licensed gambling venue.
- **AgeVerificationEvent** — A till event recording age verification before a sale or payout.
- **CashDeskPayout** — A cash payout at the till subject to AML thresholds.

## Additional relationships

- VenueTill relatesToContext within the POS base model (many-to-one).
- AgeVerificationEvent is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Venue Cashier** — Operates venue tills with mandatory age verification and payout limits.

## Regulatory notes

- Age verification is mandatory before wagering or payouts at the till.
- Cash desk payouts above thresholds require AML checks and recording.
