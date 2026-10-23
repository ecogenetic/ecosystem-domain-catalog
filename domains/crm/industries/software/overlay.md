# Software addendum — CRM

## Additional concepts

- **SoftwareAccount** — An organisation account that buys or uses software. Distinct from a financial account and from a cloud account.
- **ProductSubscriptionOpportunity** — An opportunity to sell or expand a software subscription.

## Additional relationships

- ProductSubscriptionOpportunity qualifiesSoftwareAccount SoftwareAccount (many-to-one)

## Additional roles

- **Software Account Executive** — Owns software customer accounts and subscription opportunities. Bearer: person. Permissions: Account:read, Account:write, Opportunity:read, Opportunity:write.

## Regulatory notes

- Subscription opportunities should retain the product edition and customer tenant referenced when the opportunity moves stage.
