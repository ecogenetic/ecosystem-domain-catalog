# Software addendum — ERP

## Additional concepts

- **SubscriptionSalesOrder** — A sales order for a recurring software subscription.
- **SoftwareVendor** — A vendor that supplies software, cloud, or implementation services to the company.

## Additional relationships

- SubscriptionSalesOrder contractedThroughSoftwareVendor SoftwareVendor (many-to-one)

## Additional roles

- **Subscription Finance Clerk** — Records subscription sales orders and their invoices. Bearer: person. Permissions: SalesOrder:read, SalesOrder:write, CustomerInvoice:read.

## Regulatory notes

- Subscription revenue documents should reference the license agreement rather than restate entitlement balances.
