# Telco addendum — EAM

## Additional concepts

- **CellSiteAsset** — A network asset located at a cell site (antenna, radio, power, shelter).
- **NetworkWorkOrder** — A maintenance or install work order against network assets.
- **AssetLifecycleState** — Lifecycle state of a network asset from deployed to decommissioned.

## Additional relationships

- CellSiteAsset relatesToContext within the EAM base model (many-to-one).
- NetworkWorkOrder is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Network Asset Manager** — Owns cell-site asset registry and work-order prioritisation.

## Regulatory notes

- Decommissioning network assets must update inventory and topology consumers.
- Work orders on live sites require access and safety clearances.
