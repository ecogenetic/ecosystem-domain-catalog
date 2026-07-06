# TMS — Transportation Management System

A Transportation Management System plans carriers, routes, loads, and freight rates for
deliveries so logistics teams reduce cost while meeting delivery commitments.

## Concepts

- **Carrier** — a transport organisation assigned to move planned loads at contracted rates.
- **Route** — a planned path that sequences delivery stops from origin to final destination.
- **LoadPlan** — a consolidation of shipments into a transportable load assigned to a carrier.
- **Shipment** — a consignment of goods planned, tracked, and confirmed through delivery.
- **FreightRate** — the price a carrier charges for moving a load on a lane or service level.
- **DeliveryStop** — a scheduled stop on a route where one or more shipments are delivered.

## Taxonomy

- Carrier is a kind of Organisation.
- Shipment is a kind of Consignment.
- LoadPlan is a kind of TransportPlan.
- DeliveryStop is a kind of RouteEvent.

## Attributes

- Carrier: carrierName (string), scacCode (string)
- Route: routeName (string), totalDistanceKm (decimal)
- LoadPlan: loadNumber (string), plannedDate (date), totalWeightKg (decimal)
- Shipment: shipmentNumber (string), deliveryDeadline (dateTime), shipmentStatus (string)
- FreightRate: ratePerKm (decimal), currency (string), validUntil (date)
- DeliveryStop: stopSequence (integer), scheduledArrival (dateTime), stopAddress (string)

## Relationships

- LoadPlan groupsShipment Shipment (one-to-many)
- Carrier assignedToLoadPlan LoadPlan (one-to-many)
- Route sequencesDeliveryStop DeliveryStop (one-to-many)
- FreightRate pricesCarrier Carrier (many-to-one)
- Shipment followsRoute Route (many-to-one)

## Lifecycle

- Shipment: planned → in transit → delivered → confirmed

## Roles

- **DispatcherRole** (bearer: person) — builds load plans, assigns carriers, and tracks shipments through delivery stops; permissions: LoadPlan:read, LoadPlan:write, Shipment:read, Shipment:write, Route:read, Route:write, Carrier:read
- **CarrierRole** (bearer: organisation) — accepts assigned load plans, executes routes, and confirms deliveries; permissions: LoadPlan:read, Shipment:read, Shipment:write, DeliveryStop:read

## Primary workflow

Create shipment → plan route and load → assign carrier → track stops → confirm delivery
