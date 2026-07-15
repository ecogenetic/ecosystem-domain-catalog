# Telco addendum — TMS

## Additional concepts

- **FieldTechnicianStop** — A planned stop on a route for installing or maintaining network equipment.
- **SparePartLoad** — Spares loaded onto a technician vehicle for a work order.
- **SiteAccessWindow** — An approved time window for accessing a restricted cell site or facility.

## Additional relationships

- FieldTechnicianStop relatesToContext within the TMS base model (many-to-one).
- SparePartLoad is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Field Logistics Dispatcher** — Plans technician routes, loads, and site access windows.

## Regulatory notes

- Site access windows are safety and landlord constraints — transport plans must respect them.
- Spare part loads remain inventory until consumed on a work order.
