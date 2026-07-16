# BIL — Telecom Billing Management

Manages billing accounts, cycles, bill runs, invoices, usage and recurring lines, adjustments, credits, and taxes.

## Concepts

- **BillingAccount** — An account grouping charges, payment terms, and invoice delivery preferences.
- **BillingProfile** — The invoicing, tax, currency, and delivery configuration for a billing account.
- **BillingCycle** — A recurring period over which charges are collected for billing.
- **BillRun** — A controlled execution that calculates invoices for a billing cycle.
- **Invoice** — A statement of amounts due for supplied products and services.
- **InvoiceLine** — A detailed recurring, one-time, or usage-based amount on an invoice.
- **Adjustment** — A controlled correction increasing or decreasing a billed amount.
- **CreditNote** — A document reducing an amount previously invoiced.
- **TaxCharge** — A tax amount calculated for an invoice or invoice line.

## Taxonomy

- CreditNote is a kind of Billing document.
- Invoice is a kind of Billing document.
- TaxCharge is a kind of Invoice amount.

## Relationships

- BillingAccount usesBillingProfile BillingProfile (one-to-one)
- BillingCycle initiatesBillRun BillRun (one-to-many)
- BillRun producesInvoice Invoice (one-to-many)
- Invoice containsInvoiceLine InvoiceLine (one-to-many)
- Adjustment changesInvoiceLine InvoiceLine (many-to-one)
- CreditNote creditsInvoice Invoice (many-to-one)
- TaxCharge appliesToInvoiceLine InvoiceLine (many-to-one)

## Attributes

- BillingAccount: billingAccountId (string)
- BillingProfile: billingProfileId (string)
- BillingCycle: billingCycleId (string)
- BillRun: billRunId (string)
- Invoice: invoiceId (string)
- InvoiceLine: invoiceLineId (string)
- Adjustment: adjustmentId (string)
- CreditNote: creditNoteId (string)
- TaxCharge: taxChargeId (string)

## Lifecycle

- Invoice: draft → calculated → issued → due → paid → overdue → cancelled

## Roles

- **Billing Operations** (bearer: person) — runs billing cycles and resolves invoice calculation exceptions; permissions: BillingAccount:read, BillRun:read, BillRun:write, Invoice:read, Invoice:write, Adjustment:write.

## Primary workflow

Open billing cycle → execute bill run → calculate invoice lines → apply tax and adjustments → issue invoice → settle