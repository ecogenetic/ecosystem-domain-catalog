# FMS — Financial Management System

A Financial Management System manages the chart of accounts, general ledger, accounts payable and
receivable, sales and purchase subledgers, payments, and period close so finance teams post,
reconcile, and close books with auditable GL-to-subledger traceability.

## Concepts

- **ChartOfAccount** — the structured catalog of account codes that classifies every financial posting.
- **JournalEntry** — a balanced set of debit and credit lines posted to the general ledger.
- **GeneralLedger** — the central book of record aggregating all postings by account and period.
- **VendorInvoice** — a bill received from a supplier, recorded in the purchase ledger for payment.
- **CustomerInvoice** — a bill issued to a customer, recorded in the sales ledger for collection.
- **Payment** — a cash movement that settles a vendor invoice or applies a customer receipt.
- **SalesLedger** — the accounts receivable subledger tracking amounts owed by customers.
- **PurchaseLedger** — the accounts payable subledger tracking amounts owed to suppliers.
- **FiscalPeriod** — a bounded accounting period within which entries are posted and then closed.
- **Reconciliation** — a control that ties subledger and bank balances back to the general ledger.

## Taxonomy

- SalesLedger is a kind of Subledger.
- PurchaseLedger is a kind of Subledger.
- VendorInvoice is a kind of Invoice.
- CustomerInvoice is a kind of Invoice.

## Relationships

- ChartOfAccount structuresGeneralLedger GeneralLedger (one-to-many)
- JournalEntry postedToGeneralLedger GeneralLedger (many-to-one)
- JournalEntry withinFiscalPeriod FiscalPeriod (many-to-one)
- VendorInvoice recordedInPurchaseLedger PurchaseLedger (many-to-one)
- CustomerInvoice recordedInSalesLedger SalesLedger (many-to-one)
- Payment settlesVendorInvoice VendorInvoice (many-to-one)
- Reconciliation tiesLedger GeneralLedger (many-to-one)

## Attributes

- ChartOfAccount: accountCode (string), accountName (string), accountType (string)
- JournalEntry: entryNumber (string), postingDate (date), totalDebit (decimal), totalCredit (decimal), journalEntryStatus (string)
- GeneralLedger: ledgerName (string), currencyCode (string)
- VendorInvoice: invoiceNumber (string), invoiceAmount (decimal), dueDate (date)
- CustomerInvoice: invoiceNumber (string), invoiceAmount (decimal), dueDate (date)
- Payment: paymentAmount (decimal), paymentDate (date), paymentMethod (string)
- SalesLedger: openReceivableBalance (decimal)
- PurchaseLedger: openPayableBalance (decimal)
- FiscalPeriod: periodName (string), startDate (date), endDate (date)
- Reconciliation: reconciledAt (dateTime), variance (decimal)

## Lifecycle

- JournalEntry: draft → posted → reconciled → period closed

## Roles

- **AccountantRole** (bearer: person) — creates and posts journal entries and maintains the chart of accounts; permissions: JournalEntry:read, JournalEntry:write, ChartOfAccount:read, ChartOfAccount:write, GeneralLedger:read
- **APClerkRole** (bearer: person) — records vendor invoices and prepares supplier payments; permissions: VendorInvoice:read, VendorInvoice:write, Payment:read, Payment:write, PurchaseLedger:read
- **ARClerkRole** (bearer: person) — issues customer invoices and applies receipts to the sales ledger; permissions: CustomerInvoice:read, CustomerInvoice:write, Payment:read, Payment:write, SalesLedger:read
- **ControllerRole** (bearer: person) — reviews reconciliations and closes fiscal periods; permissions: Reconciliation:read, Reconciliation:write, FiscalPeriod:read, FiscalPeriod:write, GeneralLedger:read

## Primary workflow

Post to GL → record AP/Purchase Ledger invoice → approve payment → post AR/Sales Ledger receipt → reconcile subledgers → close fiscal period
