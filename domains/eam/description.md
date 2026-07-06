# EAM — Enterprise Asset Management

An Enterprise Asset Management system maintains assets, work orders, maintenance plans, and
spare parts so reliability teams reduce downtime through planned maintenance.

## Concepts

- **Asset** — a physical piece of equipment or infrastructure the organization maintains over its life.
- **Location** — a physical site or functional position where an Asset is installed or stored.
- **MaintenancePlan** — a preventive schedule that generates work orders for an Asset at defined intervals.
- **WorkOrder** — an authorized job to inspect, service, or repair an Asset, tracked from schedule to close.
- **SparePart** — a stocked replacement component consumed when executing a WorkOrder.
- **MeterReading** — a recorded measurement (such as hours run or kilometres) captured for an Asset.

## Taxonomy

- Asset is a kind of Equipment.
- SparePart is a kind of InventoryItem.
- MeterReading is a kind of Measurement.

## Relationships

- Asset locatedAtLocation Location (many-to-one)
- MaintenancePlan schedulesWorkOrder WorkOrder (one-to-many)
- WorkOrder performedOnAsset Asset (many-to-one)
- WorkOrder consumesSparePart SparePart (many-to-many)
- MeterReading recordedForAsset Asset (many-to-one)

## Attributes

- Asset: assetTag (string), assetName (string), commissionedOn (date)
- Location: locationName (string), locationCode (string)
- MaintenancePlan: planName (string), intervalDays (integer)
- WorkOrder: workOrderNumber (string), scheduledFor (dateTime), workOrderStatus (string)
- SparePart: partNumber (string), quantityOnHand (integer)
- MeterReading: meterType (string), readingValue (decimal), readAt (dateTime)

## Lifecycle

- WorkOrder: scheduled → in progress → completed → closed

## Roles

- **TechnicianRole** (bearer: person) — executes work orders, consumes spare parts, and records meter readings; permissions: WorkOrder:read, WorkOrder:write, SparePart:read, MeterReading:read, MeterReading:write
- **MaintenancePlannerRole** (bearer: person) — registers assets, defines maintenance plans, and schedules work orders; permissions: Asset:read, Asset:write, MaintenancePlan:read, MaintenancePlan:write, WorkOrder:read, WorkOrder:write

## Primary workflow

Register asset → schedule preventive maintenance → create work order → complete → update meter reading
