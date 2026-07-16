# Telco addendum — BIL

## Additional concepts

- **TelcoInvoice** — An invoice containing recurring and usage charges for mobile services.
- **UsageInvoiceLine** — An invoice line derived from rated voice, messaging, or data usage.

## Additional relationships

- TelcoInvoice billsSubscriber Subscriber (many-to-one)

## Additional roles

- **Telco Billing Analyst** — Person role that verifies subscriber bills and usage-derived invoice lines. Bearer: person. Permissions: Invoice:read, Invoice:write, InvoiceLine:read, Adjustment:read, Adjustment:write.

## Regulatory notes

- Identifier, subscriber, usage, and service associations retain effective dates and source-system provenance where required for audit.
- Personally identifiable and communications data are accessed according to applicable privacy, retention, and lawful-process controls.