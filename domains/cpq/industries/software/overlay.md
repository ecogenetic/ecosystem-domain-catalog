# Software addendum — CPQ

## Additional concepts

- **EditionBundle** — A bundle of product editions priced together.
- **SeatPriceRule** — A price rule that prices seats or usage for a software edition.

## Additional relationships

- SeatPriceRule pricesEditionBundle EditionBundle (many-to-one)

## Additional roles

- **Software Pricing Approver** — Approves seat and usage prices for a product edition. Bearer: person. Permissions: PriceRule:read, PriceRule:write, Quote:read, Approval:write.

## Regulatory notes

- Approved software quotes should retain the price-rule version and the product edition that was priced.
