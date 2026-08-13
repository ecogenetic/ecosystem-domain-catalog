# Banking addendum — LNS

## Additional concepts
- **RetailLoanAccount** — a LoanAccount maintained under a retail lending FinancialProductAgreement.
- **HardshipArrangement** — a regulated restructure arrangement created for a customer experiencing financial difficulty.
- **ArrearsReferral** — an event referring a delinquent loan to Credit & Collections Management.

## Additional relationships
- RetailLoanAccount accountUnderAgreement FinancialProductAgreement (many-to-one)
- HardshipArrangement modifiesRetailLoan RetailLoanAccount (many-to-one)
- ArrearsReferral refersLoan RetailLoanAccount (many-to-one)

## Additional roles
- **Hardship Specialist Role** — assesses hardship requests and records approved customer assistance.

## Regulatory notes
- Loan servicing must preserve the original agreement and immutable schedule versions when terms change.
- Arrears and collections hand-off should reference the same party, agreement, account, and decision identifiers.
- Hardship and restructure decisions should retain policy version, evidence, maker-checker approval, and customer communication history.
