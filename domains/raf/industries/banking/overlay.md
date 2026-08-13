# Banking addendum — RAF

## Additional concepts
- **BankingFraudAlert** — a fraud alert against a banking party, account, instrument, or payment.
- **PaymentFraudInvestigation** — an investigation into suspected payment fraud.
- **AccountTakeoverCase** — an investigation into suspected unauthorised account control.
- **FraudLoss** — a confirmed monetary loss attributable to fraud.

## Additional relationships
- PaymentFraudInvestigation investigatesAlert BankingFraudAlert (many-to-one)
- BankingFraudAlert fraudAlertForParty Party (many-to-one)
- FraudLoss lossFromInvestigation PaymentFraudInvestigation (many-to-one)

## Additional roles
- **Bank Fraud Investigator** — Triages fraud alerts, investigates suspicious banking activity, and records outcomes. Bearer: person.

## Regulatory notes
- Fraud decisions should preserve model or rule version, evidence, disposition, and investigator identity.
- Financial-crime and fraud investigations should correlate without collapsing their distinct legal and operational purposes.
