# Software addendum — FMS

## Additional concepts

- **DeferredRevenueJournal** — A journal entry that defers or recognises software subscription revenue.
- **SubscriptionCustomerInvoice** — A customer invoice for a software subscription period.

## Additional relationships

- DeferredRevenueJournal recognisesSubscriptionInvoice SubscriptionCustomerInvoice (many-to-one)

## Additional roles

- **Subscription Accountant** — Posts subscription invoices and deferred revenue. Bearer: person. Permissions: JournalEntry:read, JournalEntry:write, CustomerInvoice:read, CustomerInvoice:write.

## Regulatory notes

- Revenue recognition should keep the invoice, the fiscal period, and the license agreement reference together.
