# LNS — Loan Servicing

Loan Servicing maintains booked loans after origination, including repayment schedules, instalments, interest accruals, collateral references, restructures, settlement quotes, and servicing events.

## Concepts
- **LoanAccount** — the operational servicing record for a booked loan.
- **RepaymentSchedule** — the dated schedule of expected repayments for a loan account.
- **RepaymentInstallment** — one scheduled amount due under a repayment schedule.
- **InterestAccrual** — interest accrued for a period against a loan account.
- **CollateralLink** — a reference linking a loan account to collateral managed or recorded elsewhere.
- **RestructureArrangement** — an approved change to repayment terms for a stressed or modified loan.
- **SettlementQuote** — a time-bounded amount required to settle the loan.
- **LoanServicingEvent** — an immutable record of a material servicing event.

## Taxonomy
- RepaymentInstallment is a kind of scheduled payment obligation.
- RestructureArrangement is a kind of loan modification.

## Relationships
- LoanAccount hasRepaymentSchedule RepaymentSchedule (one-to-many)
- RepaymentSchedule comprisesInstallment RepaymentInstallment (one-to-many)
- InterestAccrual accruesOn LoanAccount (many-to-one)
- CollateralLink securesLoan LoanAccount (many-to-one)
- RestructureArrangement modifiesLoan LoanAccount (many-to-one)
- SettlementQuote settlesLoan LoanAccount (many-to-one)
- LoanServicingEvent recordsEventFor LoanAccount (many-to-one)

## Attributes
- LoanAccount: loanAccountNumber (string), principalBalance (decimal), loanStatus (string)
- RepaymentSchedule: scheduleVersion (string), effectiveDate (date)
- RepaymentInstallment: dueDate (date), principalDue (decimal), interestDue (decimal), installmentStatus (string)
- InterestAccrual: accrualDate (date), accruedAmount (decimal), interestRate (decimal)
- CollateralLink: collateralReference (string), lienPriority (integer)
- RestructureArrangement: restructureReference (string), restructureStatus (string)
- SettlementQuote: quoteReference (string), settlementAmount (decimal), validUntil (date)
- LoanServicingEvent: eventType (string), occurredAt (dateTime)

## Lifecycle
- LoanAccount: booked → active → settled → closed | written_off
- RestructureArrangement: proposed → approved → active → completed | cancelled

## Roles
- **Loan Servicing Officer Role** (bearer: person) — maintains schedules, accruals, settlements, and servicing events; permissions: LoanAccount:read, LoanAccount:write, RepaymentSchedule:read, RepaymentSchedule:write
- **Loan Restructure Approver Role** (bearer: person) — approves restructures within delegated authority; permissions: RestructureArrangement:read, RestructureArrangement:write, LoanAccount:read

## Primary workflow
Book loan account → generate repayment schedule → accrue interest → apply repayments → manage servicing changes → restructure if approved → issue settlement quote → close loan
