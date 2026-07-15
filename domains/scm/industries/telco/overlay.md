# Telco addendum — SCM

## Additional concepts

- **NetworkEquipmentSKU** — A supply-chain SKU for RAN, core, or CPE equipment with vendor part identity.
- **SiteDeliveryOrder** — A delivery order targeting a cell site or POP rather than a warehouse only.
- **SerialisedAssetReceipt** — Receipt of serialised network gear (IMEI/serial) into the supply chain.

## Additional relationships

- NetworkEquipmentSKU relatesToContext within the SCM base model (many-to-one).
- SiteDeliveryOrder is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Network Supply Planner** — Plans equipment supply to sites and tracks serialised receipts.

## Regulatory notes

- Serialised network assets require chain-of-custody from vendor to site.
- Site deliveries must reconcile against approved network build orders.
