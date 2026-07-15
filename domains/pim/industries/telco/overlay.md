# Telco addendum — PIM

## Additional concepts

- **RatePlanOffering** — A commercial rate-plan product record in the catalog with allowances and fees.
- **BundleComposition** — How devices, SIMs, and plans are composed into a sellable bundle.
- **ChannelCatalogPublish** — A publish event releasing catalog entries to a sales channel.

## Additional relationships

- RatePlanOffering relatesToContext within the PIM base model (many-to-one).
- BundleComposition is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Catalog Merchandiser** — Maintains rate plans, bundles, and channel publish status.

## Regulatory notes

- Published prices and allowances must match what the billing system will charge.
- Bundle composition changes require a new publish — silent edits to live offers are prohibited.
