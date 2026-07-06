# SCM — Supply Chain Management

A Supply Chain Management system coordinates suppliers, inventory levels, fulfillment orders,
and shipments so supply chain teams resolve stock-outs and delays before they hit customers.

## Concepts

- **Supplier** — an external organisation that provides inventory to replenish the supply chain.
- **Inventory** — stock of goods held at a location and available for allocation to orders.
- **FulfillmentOrder** — an instruction to allocate, pick, and ship inventory to satisfy customer demand.
- **Shipment** — a physical consignment that carries a fulfillment order along a route to its destination.
- **Route** — a planned path from origin to destination used to move shipments.
- **Carrier** — a transport organisation that operates routes and moves shipments.

## Taxonomy

- Supplier is a kind of Organisation.
- Carrier is a kind of Organisation.
- FulfillmentOrder is a kind of DemandOrder.
- Shipment is a kind of Consignment.

## Attributes

- Supplier: supplierName (string), leadTimeDays (integer)
- Inventory: itemCode (string), quantityOnHand (integer), reorderPoint (integer)
- FulfillmentOrder: fulfillmentOrderNumber (string), requestedDate (date), fulfillmentOrderStatus (string)
- Shipment: trackingNumber (string), shippedAt (dateTime)
- Route: originLocation (string), destinationLocation (string), transitTimeDays (integer)
- Carrier: carrierName (string), serviceLevel (string)

## Relationships

- Supplier providesInventory Inventory (one-to-many)
- FulfillmentOrder allocatesInventory Inventory (many-to-many)
- Shipment fulfillsOrder FulfillmentOrder (one-to-one)
- Carrier operatesRoute Route (one-to-many)
- Shipment followsRoute Route (many-to-one)

## Lifecycle

- FulfillmentOrder: allocated → picked → shipped → delivered

## Roles

- **SupplyPlannerRole** (bearer: person) — forecasts demand, plans replenishment, and allocates inventory to fulfillment orders; permissions: Inventory:read, Inventory:write, FulfillmentOrder:read, FulfillmentOrder:write, Supplier:read
- **SupplierRole** (bearer: organisation) — confirms replenishment orders and provides inventory on agreed lead times; permissions: Inventory:read, Supplier:read, Supplier:write

## Primary workflow

Forecast demand → place supplier order → receive inventory → fulfill customer order → ship
