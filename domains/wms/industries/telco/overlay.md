# Telco addendum — WMS

## Additional concepts

- **SIMStockBin** — A warehouse bin holding physical SIM cards pending registration or dispatch.
- **DeviceIMEITracking** — Warehouse tracking of handset/router stock by IMEI.
- **DealerReplenishmentPick** — A pick wave replenishing dealer or retail channel stock.

## Additional relationships

- SIMStockBin relatesToContext within the WMS base model (many-to-one).
- DeviceIMEITracking is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **SIM Warehouse Operator** — Picks, packs, and stages SIM and device stock for channels.

## Regulatory notes

- SIM stock movements must preserve ICCID identity for later registration.
- IMEI discrepancies between pick and ship must block dispatch.
