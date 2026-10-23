# Software addendum — OMS

## Additional concepts

- **EntitlementOrder** — An order whose fulfilment grants or changes a software entitlement.
- **LicenseFulfilment** — Fulfilment that completes when the license entitlement is granted.

## Additional relationships

- LicenseFulfilment fulfilsEntitlementOrder EntitlementOrder (many-to-one)

## Additional roles

- **License Order Manager** — Manages orders that grant software entitlements. Bearer: person. Permissions: Order:read, Order:write, Fulfillment:read, Fulfillment:write.

## Regulatory notes

- An entitlement order references the license agreement and does not become the agreement.
