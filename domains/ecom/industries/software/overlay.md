# Software addendum — ECOM

## Additional concepts

- **DigitalProductOrder** — An order for a software product rather than a shipped good.
- **SoftwareFulfilment** — Fulfilment that provisions access instead of shipping a parcel.

## Additional relationships

- SoftwareFulfilment fulfilsDigitalProductOrder DigitalProductOrder (many-to-one)

## Additional roles

- **Digital Store Administrator** — Oversees digital software orders and provisioning fulfilment. Bearer: person. Permissions: Order:read, Order:write, Fulfilment:read, Fulfilment:write.

## Regulatory notes

- Digital fulfilment should hand the license agreement identifier to licensing rather than copying entitlement state.
